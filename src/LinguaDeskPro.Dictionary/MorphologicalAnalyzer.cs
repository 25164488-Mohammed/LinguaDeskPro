using System;
using System.Collections.Generic;
using LinguaDeskPro.Core;

namespace LinguaDeskPro.Dictionary
{
    /// <summary>
    /// Bilingual Morphological Analyzer & Light Stemmer for English inflections and Arabic clitics/roots.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public static class MorphologicalAnalyzer
    {
        private static readonly Dictionary<string, string> IrregularEnglishMap = new(StringComparer.OrdinalIgnoreCase)
        {
            ["ran"] = "run", ["running"] = "run", ["runs"] = "run",
            ["went"] = "go", ["gone"] = "go", ["going"] = "go", ["goes"] = "go",
            ["wrote"] = "write", ["written"] = "write", ["writing"] = "write",
            ["read"] = "read", ["reading"] = "read",
            ["spoke"] = "speak", ["spoken"] = "speak", ["speaking"] = "speak",
            ["built"] = "build", ["building"] = "build", ["builds"] = "build",
            ["found"] = "find", ["finding"] = "find",
            ["sent"] = "send", ["sending"] = "send",
            ["kept"] = "keep", ["keeping"] = "keep",
            ["knew"] = "know", ["known"] = "know",
            ["thought"] = "think", ["thinking"] = "think",
            ["Children".ToLower()] = "child", ["mice"] = "mouse", ["analyses"] = "analysis",
            ["diagnoses"] = "diagnosis", ["criteria"] = "criterion", ["phenomena"] = "phenomenon"
        };

        private static readonly string[] ArabicPrefixes = { "وال", "بال", "كال", "فال", "لل", "ال", "و", "ف", "ب", "ل", "س" };
        private static readonly string[] ArabicSuffixes = { "ات", "ون", "ين", "ان", "هم", "ها", "كم", "نا", "ت", "ه", "ي", "ك" };

        public static List<string> GetEnglishCandidateLemmas(string word)
        {
            var list = new List<string>();
            if (string.IsNullOrWhiteSpace(word)) return list;

            string w = word.Trim().ToLowerInvariant();
            list.Add(w);

            if (IrregularEnglishMap.TryGetValue(w, out var irr))
                list.Add(irr);

            if (w.EndsWith("ies") && w.Length > 4) list.Add(w[..^3] + "y");
            if (w.EndsWith("es") && w.Length > 4) { list.Add(w[..^2]); list.Add(w[..^1]); }
            if (w.EndsWith("s") && w.Length > 3) list.Add(w[..^1]);
            if (w.EndsWith("ied") && w.Length > 4) list.Add(w[..^3] + "y");
            if (w.EndsWith("ed") && w.Length > 4) { list.Add(w[..^2]); list.Add(w[..^1]); }
            if (w.EndsWith("ing") && w.Length > 5) { list.Add(w[..^3]); list.Add(w[..^3] + "e"); }
            if (w.EndsWith("ly") && w.Length > 4) list.Add(w[..^2]);

            return list;
        }

        public static List<string> GetArabicCandidateStems(string word)
        {
            var list = new List<string>();
            if (string.IsNullOrWhiteSpace(word)) return list;

            string norm = ArabicNormalizer.NormalizeArabic(word);
            list.Add(norm);

            foreach (var pre in ArabicPrefixes)
            {
                if (norm.StartsWith(pre) && norm.Length - pre.Length >= 3)
                {
                    string withoutPre = norm[pre.Length..];
                    list.Add(withoutPre);
                    foreach (var suf in ArabicSuffixes)
                    {
                        if (withoutPre.EndsWith(suf) && withoutPre.Length - suf.Length >= 3)
                            list.Add(withoutPre[..^suf.Length]);
                    }
                }
            }

            foreach (var suf in ArabicSuffixes)
            {
                if (norm.EndsWith(suf) && norm.Length - suf.Length >= 3)
                    list.Add(norm[..^suf.Length]);
            }

            return list;
        }
    }
}
