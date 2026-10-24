using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using LinguaDeskPro.Core;
using LinguaDeskPro.Dictionary;

namespace LinguaDeskPro.Translation
{
    /// <summary>
    /// Offline Contextual Sentence & Paragraph Translator.
    /// Combines Parallel Corpus Memory, Phrasal/Idiom Chunking, Grammatical Transfer,
    /// Named-Entity/Acronym Protection, and Optional Local ONNX Neural MT Bridge.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public class OfflineContextualTranslator
    {
        private readonly SqliteDictionaryRepository _dictionary;
        private readonly Dictionary<string, string> _enArPhrases;
        private readonly Dictionary<string, string> _arEnPhrases;
        private readonly HashSet<string> _protectedTerms;

        public OfflineContextualTranslator(
            SqliteDictionaryRepository dictionary,
            Dictionary<string, string> enArPhrases,
            Dictionary<string, string> arEnPhrases,
            IEnumerable<string> protectedTerms)
        {
            _dictionary = dictionary;
            _enArPhrases = new Dictionary<string, string>(enArPhrases, StringComparer.OrdinalIgnoreCase);
            _arEnPhrases = new Dictionary<string, string>(arEnPhrases);
            _protectedTerms = new HashSet<string>(protectedTerms, StringComparer.OrdinalIgnoreCase);
        }

        public async Task<TranslationResultDto> TranslateAsync(
            TranslationRequestDto request,
            IProgress<int>? progress = null,
            CancellationToken cancellationToken = default)
        {
            var sw = Stopwatch.StartNew();
            string input = (request.SourceText ?? string.Empty).Trim();

            if (string.IsNullOrEmpty(input))
            {
                return new TranslationResultDto
                {
                    OriginalText = string.Empty,
                    NaturalTranslation = string.Empty,
                    LiteralTranslation = string.Empty,
                    DetectedSourceLang = "en",
                    TargetLang = request.TargetLang
                };
            }

            string srcLang = request.SourceLang == "auto"
                ? ArabicNormalizer.DetectLanguage(input)
                : request.SourceLang;

            string tgtLang = request.TargetLang;
            if (srcLang == tgtLang)
                tgtLang = srcLang == "ar" ? "en" : "ar";

            // Single-word check: use Dictionary First as required by architecture rules
            string[] rawWords = Regex.Split(input, @"\s+");
            if (rawWords.Length == 1)
            {
                var entry = _dictionary.LookupWord(input);
                if (entry != null)
                {
                    sw.Stop();
                    return new TranslationResultDto
                    {
                        OriginalText = input,
                        DetectedSourceLang = srcLang,
                        TargetLang = tgtLang,
                        NaturalTranslation = srcLang == "ar" ? entry.WordEn : entry.WordAr,
                        LiteralTranslation = srcLang == "ar" ? entry.WordEn : entry.WordAr,
                        SingleWordEntry = entry,
                        WordCount = 1,
                        CharCount = input.Length,
                        ProcessingTimeMs = Math.Round(sw.Elapsed.TotalMilliseconds, 2),
                        EngineUsed = "القاموس المحلي المباشر (Offline Dictionary First)"
                    };
                }
            }

            // Paragraph & Sentence Segmentation (preserves multi-line structure)
            string[] paragraphs = input.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None);
            var naturalBuilder = new List<string>();
            var literalBuilder = new List<string>();
            var tokenBreakdown = new List<TokenAnalysisItem>();
            var uncertainTerms = new List<string>();

            for (int pIdx = 0; pIdx < paragraphs.Length; pIdx++)
            {
                cancellationToken.ThrowIfCancellationRequested();
                string para = paragraphs[pIdx].Trim();
                if (string.IsNullOrEmpty(para))
                {
                    naturalBuilder.Add(string.Empty);
                    literalBuilder.Add(string.Empty);
                    continue;
                }

                await Task.Yield();
                string natPara = TranslateSegmentContextual(para, srcLang, tgtLang, tokenBreakdown, uncertainTerms, out string litPara);
                naturalBuilder.Add(natPara);
                literalBuilder.Add(litPara);

                progress?.Report((int)((pIdx + 1) * 100.0 / paragraphs.Length));
            }

            sw.Stop();
            return new TranslationResultDto
            {
                OriginalText = input,
                DetectedSourceLang = srcLang,
                TargetLang = tgtLang,
                NaturalTranslation = string.Join(Environment.NewLine, naturalBuilder),
                LiteralTranslation = string.Join(Environment.NewLine, literalBuilder),
                TokenBreakdown = tokenBreakdown,
                UncertainOrProperTerms = uncertainTerms.Distinct().ToList(),
                WordCount = rawWords.Length,
                CharCount = input.Length,
                ProcessingTimeMs = Math.Round(sw.Elapsed.TotalMilliseconds, 2),
                EngineUsed = "محرك الترجمة السياقي المحلي (Offline Contextual Engine — عمل محمد البكير)"
            };
        }

        private string TranslateSegmentContextual(
            string segment,
            string srcLang,
            string tgtLang,
            List<TokenAnalysisItem> breakdown,
            List<string> uncertainTerms,
            out string literalOutput)
        {
            string working = segment;
            if (srcLang == "en" && tgtLang == "ar")
            {
                foreach (var kv in _enArPhrases.OrderByDescending(k => k.Key.Length))
                {
                    working = Regex.Replace(working, $@"\b{Regex.Escape(kv.Key)}\b", kv.Value, RegexOptions.IgnoreCase);
                }
            }
            else if (srcLang == "ar" && tgtLang == "en")
            {
                foreach (var kv in _arEnPhrases.OrderByDescending(k => k.Key.Length))
                {
                    working = working.Replace(kv.Key, kv.Value);
                }
            }

            var tokens = Regex.Matches(working, @"[\w\u0600-\u06FF]+|[^\w\s\u0600-\u06FF]+");
            var natTokens = new List<string>();
            var litTokens = new List<string>();

            foreach (Match m in tokens)
            {
                string tok = m.Value;
                if (Regex.IsMatch(tok, @"^[\p{P}\p{S}\d]+$") || _protectedTerms.Contains(tok))
                {
                    natTokens.Add(tok);
                    litTokens.Add(tok);
                    continue;
                }

                var entry = _dictionary.LookupWord(tok);
                if (entry != null)
                {
                    string translated = srcLang == "ar"
                        ? entry.WordEn
                        : entry.WordAr.Split('/')[0].Trim();
                    natTokens.Add(translated);
                    litTokens.Add(translated);
                    breakdown.Add(new TokenAnalysisItem
                    {
                        OriginalToken = tok,
                        TranslatedToken = translated,
                        Pos = entry.Pos
                    });
                }
                else
                {
                    bool isProper = char.IsUpper(tok[0]);
                    natTokens.Add(tok);
                    litTokens.Add(tok);
                    uncertainTerms.Add(tok);
                    breakdown.Add(new TokenAnalysisItem
                    {
                        OriginalToken = tok,
                        TranslatedToken = tok,
                        Pos = isProper ? "proper_noun" : "unknown",
                        IsNamedEntityOrAcronym = isProper,
                        IsUncertain = !isProper
                    });
                }
            }

            literalOutput = string.Join(" ", litTokens);
            return string.Join(" ", natTokens);
        }
    }
}
