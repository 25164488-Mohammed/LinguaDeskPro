using System;
using System.Collections.Generic;
using System.Linq;

namespace LinguaDeskPro.Core
{
    /// <summary>
    /// Damerau-Levenshtein Edit Distance for spelling correction and fuzzy word search.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public static class FuzzyMatcher
    {
        public static int ComputeEditDistance(string s, string t)
        {
            if (string.IsNullOrEmpty(s)) return t?.Length ?? 0;
            if (string.IsNullOrEmpty(t)) return s.Length;

            int n = s.Length;
            int m = t.Length;
            int[,] d = new int[n + 1, m + 1];

            for (int i = 0; i <= n; i++) d[i, 0] = i;
            for (int j = 0; j <= m; j++) d[0, j] = j;

            for (int i = 1; i <= n; i++)
            {
                for (int j = 1; j <= m; j++)
                {
                    int cost = (s[i - 1] == t[j - 1]) ? 0 : 1;
                    d[i, j] = Math.Min(
                        Math.Min(d[i - 1, j] + 1, d[i, j - 1] + 1),
                        d[i - 1, j - 1] + cost);

                    // Transposition of adjacent characters (e.g. "teh" -> "the")
                    if (i > 1 && j > 1 && s[i - 1] == t[j - 2] && s[i - 2] == t[j - 1])
                    {
                        d[i, j] = Math.Min(d[i, j], d[i - 2, j - 2] + cost);
                    }
                }
            }
            return d[n, m];
        }

        public static List<string> FindClosestMatches(string query, IEnumerable<string> candidates, int maxDistance = 2, int limit = 6)
        {
            string q = query.Trim().ToLowerInvariant();
            if (string.IsNullOrEmpty(q)) return new List<string>();

            return candidates
                .Where(c => Math.Abs(c.Length - q.Length) <= maxDistance)
                .Select(c => new { Word = c, Dist = ComputeEditDistance(q, c.ToLowerInvariant()) })
                .Where(x => x.Dist > 0 && x.Dist <= maxDistance)
                .OrderBy(x => x.Dist)
                .ThenBy(x => Math.Abs(x.Word.Length - q.Length))
                .Select(x => x.Word)
                .Distinct()
                .Take(limit)
                .ToList();
        }
    }
}
