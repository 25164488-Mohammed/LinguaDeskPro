using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text.Json;
using Microsoft.Data.Sqlite;
using LinguaDeskPro.Core;

namespace LinguaDeskPro.Dictionary
{
    /// <summary>
    /// High-performance SQLite Dictionary Repository using parameterized SQL and indexed FTS5 lookups.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public class SqliteDictionaryRepository
    {
        private readonly string _connectionString;

        public SqliteDictionaryRepository(string databasePath)
        {
            _connectionString = new SqliteConnectionStringBuilder
            {
                DataSource = databasePath,
                Mode = SqliteOpenMode.ReadWriteCreate,
                Cache = SqliteCacheMode.Shared
            }.ToString();
        }

        public DictionaryEntryDto? LookupWord(string rawQuery)
        {
            if (string.IsNullOrWhiteSpace(rawQuery)) return null;
            var sw = Stopwatch.StartNew();
            string lang = ArabicNormalizer.DetectLanguage(rawQuery);

            using var conn = new SqliteConnection(_connectionString);
            conn.Open();

            DictionaryEntryDto? entry = lang == "ar"
                ? LookupArabicInternal(conn, rawQuery)
                : LookupEnglishInternal(conn, rawQuery);

            if (entry != null)
            {
                LoadSenses(conn, entry);
                sw.Stop();
                entry.QueryTimeMs = Math.Round(sw.Elapsed.TotalMilliseconds, 2);
            }
            return entry;
        }

        private DictionaryEntryDto? LookupEnglishInternal(SqliteConnection conn, string query)
        {
            foreach (var cand in MorphologicalAnalyzer.GetEnglishCandidateLemmas(query))
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = @"
                    SELECT id, word_en, word_ar, pos, ipa_uk, ipa_us, phonetic_ar, cefr_level,
                           frequency_rank, domain, lemma_en, root_ar, plural_en, plural_ar,
                           verb_forms_json, derivatives_json, synonyms_en_json, synonyms_ar_json,
                           antonyms_en_json, antonyms_ar_json, collocations_json, usage_notes,
                           source_name, license_type, is_verified_lexical
                    FROM dictionary_entries
                    WHERE word_en_lower = $w OR lemma_en = $w
                    ORDER BY is_verified_lexical DESC, frequency_rank ASC
                    LIMIT 1;";
                cmd.Parameters.AddWithValue("$w", cand);
                using var reader = cmd.ExecuteReader();
                if (reader.Read())
                    return MapEntry(reader);
            }
            return null;
        }

        private DictionaryEntryDto? LookupArabicInternal(SqliteConnection conn, string query)
        {
            foreach (var stem in MorphologicalAnalyzer.GetArabicCandidateStems(query))
            {
                using var cmd = conn.CreateCommand();
                cmd.CommandText = @"
                    SELECT id, word_en, word_ar, pos, ipa_uk, ipa_us, phonetic_ar, cefr_level,
                           frequency_rank, domain, lemma_en, root_ar, plural_en, plural_ar,
                           verb_forms_json, derivatives_json, synonyms_en_json, synonyms_ar_json,
                           antonyms_en_json, antonyms_ar_json, collocations_json, usage_notes,
                           source_name, license_type, is_verified_lexical
                    FROM dictionary_entries
                    WHERE word_ar_normalized = $q OR word_ar_normalized LIKE '%' || $q || '%'
                    ORDER BY is_verified_lexical DESC,
                             CASE WHEN word_ar_normalized = $q THEN 0 ELSE 1 END,
                             frequency_rank ASC
                    LIMIT 1;";
                cmd.Parameters.AddWithValue("$q", stem);
                using var reader = cmd.ExecuteReader();
                if (reader.Read())
                    return MapEntry(reader);
            }
            return null;
        }

        private void LoadSenses(SqliteConnection conn, DictionaryEntryDto entry)
        {
            using var cmd = conn.CreateCommand();
            cmd.CommandText = @"
                SELECT sense_order, context_label, meaning_ar, definition_en, explanation_ar, example_en, example_ar
                FROM word_senses
                WHERE entry_id = $id
                ORDER BY sense_order ASC;";
            cmd.Parameters.AddWithValue("$id", entry.Id);
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                entry.Senses.Add(new WordSenseDto
                {
                    SenseOrder = reader.GetInt32(0),
                    ContextLabel = reader.GetString(1),
                    MeaningAr = reader.GetString(2),
                    DefinitionEn = reader.GetString(3),
                    ExplanationAr = reader.GetString(4),
                    ExampleEn = reader.GetString(5),
                    ExampleAr = reader.GetString(6)
                });
            }
        }

        private DictionaryEntryDto MapEntry(SqliteDataReader r)
        {
            return new DictionaryEntryDto
            {
                Id = r.GetInt32(0),
                WordEn = r.GetString(1),
                WordAr = r.GetString(2),
                Pos = r.GetString(3),
                IpaUk = r.GetString(4),
                IpaUs = r.GetString(5),
                PhoneticAr = r.GetString(6),
                CefrLevel = r.GetString(7),
                FrequencyRank = r.GetInt32(8),
                Domain = r.GetString(9),
                LemmaEn = r.GetString(10),
                RootAr = r.GetString(11),
                PluralEn = r.GetString(12),
                PluralAr = r.GetString(13),
                VerbForms = JsonSerializer.Deserialize<Dictionary<string, string>>(r.GetString(14)) ?? new(),
                Derivatives = JsonSerializer.Deserialize<List<string>>(r.GetString(15)) ?? new(),
                SynonymsEn = JsonSerializer.Deserialize<List<string>>(r.GetString(16)) ?? new(),
                SynonymsAr = JsonSerializer.Deserialize<List<string>>(r.GetString(17)) ?? new(),
                AntonymsEn = JsonSerializer.Deserialize<List<string>>(r.GetString(18)) ?? new(),
                AntonymsAr = JsonSerializer.Deserialize<List<string>>(r.GetString(19)) ?? new(),
                Collocations = JsonSerializer.Deserialize<List<string>>(r.GetString(20)) ?? new(),
                UsageNotes = r.GetString(21),
                SourceName = r.GetString(22),
                LicenseType = r.GetString(23),
                IsVerifiedLexical = r.GetInt32(24) == 1
            };
        }

        public List<AutocompleteSuggestionDto> GetAutocompleteSuggestions(string prefix, int maxResults = 8)
        {
            var results = new List<AutocompleteSuggestionDto>();
            if (string.IsNullOrWhiteSpace(prefix)) return results;

            using var conn = new SqliteConnection(_connectionString);
            conn.Open();

            string lang = ArabicNormalizer.DetectLanguage(prefix);
            using var cmd = conn.CreateCommand();
            if (lang == "ar")
            {
                string norm = ArabicNormalizer.NormalizeArabic(prefix);
                cmd.CommandText = @"
                    SELECT word_ar, word_en, pos, is_verified_lexical
                    FROM dictionary_entries
                    WHERE word_ar_normalized LIKE $p || '%' OR word_ar_normalized LIKE '% ' || $p || '%'
                    ORDER BY is_verified_lexical DESC, frequency_rank ASC
                    LIMIT $lim;";
                cmd.Parameters.AddWithValue("$p", norm);
            }
            else
            {
                cmd.CommandText = @"
                    SELECT word_en, word_ar, pos, is_verified_lexical
                    FROM dictionary_entries
                    WHERE word_en_lower LIKE $p || '%'
                    ORDER BY is_verified_lexical DESC, frequency_rank ASC
                    LIMIT $lim;";
                cmd.Parameters.AddWithValue("$p", prefix.Trim().ToLowerInvariant());
            }
            cmd.Parameters.AddWithValue("$lim", maxResults);

            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                results.Add(new AutocompleteSuggestionDto
                {
                    Text = reader.GetString(0),
                    MeaningPreview = reader.GetString(1),
                    Pos = reader.GetString(2),
                    Category = reader.GetInt32(3) == 1 ? "Dictionary" : "Morphological"
                });
            }
            return results;
        }
    }
}
