using System;
using System.Collections.Generic;

namespace LinguaDeskPro.Core
{
    /// <summary>
    /// Core domain models for LinguaDesk Pro — عمل محمد البكير (Developed by Mohammed Al-Bakir)
    /// </summary>
    public static class AppIdentity
    {
        public const string AppName = "LinguaDesk Pro";
        public const string DeveloperNameAr = "عمل محمد البكير";
        public const string DeveloperNameEn = "Developed & Engineered by Mohammed Al-Bakir";
        public const string Version = "2.5.0-Pro";
    }

    public class WordSenseDto
    {
        public int SenseOrder { get; set; }
        public string ContextLabel { get; set; } = string.Empty;
        public string MeaningAr { get; set; } = string.Empty;
        public string DefinitionEn { get; set; } = string.Empty;
        public string ExplanationAr { get; set; } = string.Empty;
        public string ExampleEn { get; set; } = string.Empty;
        public string ExampleAr { get; set; } = string.Empty;
    }

    public class DictionaryEntryDto
    {
        public int Id { get; set; }
        public string WordEn { get; set; } = string.Empty;
        public string WordAr { get; set; } = string.Empty;
        public string Pos { get; set; } = string.Empty;
        public string IpaUk { get; set; } = string.Empty;
        public string IpaUs { get; set; } = string.Empty;
        public string PhoneticAr { get; set; } = string.Empty;
        public string CefrLevel { get; set; } = "B1";
        public int FrequencyRank { get; set; }
        public string Domain { get; set; } = "General";
        public string LemmaEn { get; set; } = string.Empty;
        public string RootAr { get; set; } = string.Empty;
        public string PluralEn { get; set; } = string.Empty;
        public string PluralAr { get; set; } = string.Empty;
        public Dictionary<string, string> VerbForms { get; set; } = new();
        public List<string> Derivatives { get; set; } = new();
        public List<string> SynonymsEn { get; set; } = new();
        public List<string> SynonymsAr { get; set; } = new();
        public List<string> AntonymsEn { get; set; } = new();
        public List<string> AntonymsAr { get; set; } = new();
        public List<string> Collocations { get; set; } = new();
        public string UsageNotes { get; set; } = string.Empty;
        public string SourceName { get; set; } = string.Empty;
        public string LicenseType { get; set; } = string.Empty;
        public bool IsVerifiedLexical { get; set; } = true;
        public List<WordSenseDto> Senses { get; set; } = new();
        public List<string> FuzzySuggestions { get; set; } = new();
        public double QueryTimeMs { get; set; }
    }

    public class TranslationRequestDto
    {
        public string SourceText { get; set; } = string.Empty;
        public string SourceLang { get; set; } = "auto";
        public string TargetLang { get; set; } = "ar";
        public bool IncludeLiteralComparison { get; set; } = true;
        public bool AllowOnlineFallback { get; set; } = false;
        public bool UserApprovedOnlineSend { get; set; } = false;
    }

    public class TokenAnalysisItem
    {
        public string OriginalToken { get; set; } = string.Empty;
        public string TranslatedToken { get; set; } = string.Empty;
        public string Pos { get; set; } = string.Empty;
        public bool IsNamedEntityOrAcronym { get; set; }
        public bool IsUncertain { get; set; }
    }

    public class TranslationResultDto
    {
        public string OriginalText { get; set; } = string.Empty;
        public string DetectedSourceLang { get; set; } = "en";
        public string TargetLang { get; set; } = "ar";
        public string NaturalTranslation { get; set; } = string.Empty;
        public string LiteralTranslation { get; set; } = string.Empty;
        public List<string> AlternativeTranslations { get; set; } = new();
        public List<TokenAnalysisItem> TokenBreakdown { get; set; } = new();
        public List<string> UncertainOrProperTerms { get; set; } = new();
        public string EngineUsed { get; set; } = "Offline Contextual Engine (عمل محمد البكير)";
        public bool IsOnlineResult { get; set; }
        public int WordCount { get; set; }
        public int CharCount { get; set; }
        public double ProcessingTimeMs { get; set; }
        public DictionaryEntryDto? SingleWordEntry { get; set; }
    }

    public class AutocompleteSuggestionDto
    {
        public string Text { get; set; } = string.Empty;
        public string MeaningPreview { get; set; } = string.Empty;
        public string Category { get; set; } = "Dictionary"; // Dictionary, FuzzySpelling, Idiom, History, Favorite
        public string Pos { get; set; } = string.Empty;
    }

    public class SrsFlashcardDto
    {
        public int Id { get; set; }
        public string WordEn { get; set; } = string.Empty;
        public string WordAr { get; set; } = string.Empty;
        public string ExplanationAr { get; set; } = string.Empty;
        public string ExampleEn { get; set; } = string.Empty;
        public string GroupName { get; set; } = string.Empty;
        public string Difficulty { get; set; } = "Medium";
        public string PersonalNote { get; set; } = string.Empty;
        public int RepetitionCount { get; set; }
        public double EasinessFactor { get; set; } = 2.5;
        public int IntervalDays { get; set; } = 1;
        public string NextReviewDate { get; set; } = string.Empty;
    }
}
