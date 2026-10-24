using System;
using System.Text.RegularExpressions;

namespace LinguaDeskPro.Core
{
    /// <summary>
    /// Normalizes Arabic and English text for fast, diacritic-insensitive dictionary & FTS lookup.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public static class ArabicNormalizer
    {
        private static readonly Regex TashkeelRegex = new(@"[ً-ٰٟـ]", RegexOptions.Compiled);
        private static readonly Regex AlefRegex = new(@"[أإآٱ]", RegexOptions.Compiled);
        private static readonly Regex ArabicCharRegex = new(@"[؀-ۿ]", RegexOptions.Compiled);
        private static readonly Regex LatinCharRegex = new(@"[A-Za-z]", RegexOptions.Compiled);

        public static string NormalizeArabic(string input)
        {
            if (string.IsNullOrWhiteSpace(input))
                return string.Empty;

            string s = TashkeelRegex.Replace(input, "");
            s = AlefRegex.Replace(s, "ا");
            s = s.Replace('ة', 'ه')
                 .Replace('ى', 'ي')
                 .Replace('ؤ', 'و')
                 .Replace('ئ', 'ي');
            return s.Trim();
        }

        public static string DetectLanguage(string text)
        {
            if (string.IsNullOrWhiteSpace(text))
                return "en";

            int arCount = ArabicCharRegex.Matches(text).Count;
            int enCount = LatinCharRegex.Matches(text).Count;

            if (arCount > 0 && enCount > 0)
                return arCount >= enCount ? "ar" : "en";
            return arCount > 0 ? "ar" : "en";
        }

        public static bool IsMixedLanguage(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return false;
            return ArabicCharRegex.IsMatch(text) && LatinCharRegex.IsMatch(text);
        }
    }
}
