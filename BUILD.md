# دليل البناء والتجميع على نظام Windows (BUILD.md)
**LinguaDesk Pro — عمل محمد البكير (Mohammed Al-Bakir)**

## 1. هيكل الحل البرمجي (`LinguaDeskPro.sln`)
يتكون الحل البرمجي لبيئة `.NET 8.0` من 7 مشاريع مفصولة المسؤوليات داخل مجلد `src/`:
1. `LinguaDeskPro.Core`: النماذج الأساسية، مطبّع النصوص العربية (`ArabicNormalizer`)، خوارزمية البحث التقريبي (`FuzzyMatcher`)، محرك التكرار المتباعد (`SpacedRepetitionEngine`)، ومدير التحقق من سلامة الموارد (`SHA-256`).
2. `LinguaDeskPro.Dictionary`: مستودع قاعدة بيانات SQLite (`SqliteDictionaryRepository`) والمحلل الصرفي (`MorphologicalAnalyzer`).
3. `LinguaDeskPro.Translation`: محرك الترجمة السياقي المحلي (`OfflineContextualTranslator`) ومزود الترجمة الخارجي الاختياري المحمي بموافقة المستخدم (`OnlineTranslationProvider`).
4. `LinguaDeskPro.Speech`: خدمة النطق الصوتي المحلي لنظام ويندوز عبر `System.Speech.Synthesis`.
5. `LinguaDeskPro.OCR`: خدمة التعرف الضوئي المحلي على النصوص عبر `Tesseract OCR`.
6. `LinguaDeskPro.Integrations`: خدمة اختصار لوحة المفاتيح العام عبر Win32 (`RegisterHotKey`)، ومدير الحافظة الآمن (`SafeClipboardManager`)، والنافذة العائمة (`FloatingMiniTranslatorForm`).
7. `LinguaDeskPro.Desktop`: تطبيق سطح المكتب الرئيسي لنظام Windows المستضيف لواجهة `WebView2` المعزولة أمنياً، بالإضافة إلى المحرك المحلي `linguadesk_backend.py`.

## 2. خطوات البناء على Windows
### الخيار الأول: البناء الآلي الكامل عبر PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File installer\Build-Windows-Release.ps1
```

### الخيار الثاني: البناء اليدوي عبر .NET 8 CLI
```powershell
dotnet restore LinguaDeskPro.sln
dotnet publish src\LinguaDeskPro.Desktop\LinguaDeskPro.Desktop.csproj -c Release -r win-x64 --self-contained true -o ReadyToInstall\LinguaDeskPro_Portable
```

### الخيار الثالث: توليد المثبت عبر Inno Setup
افتح الملف `installer\LinguaDeskPro_Setup.iss` بواسطة برنامج **Inno Setup 6** واضغط `Compile` (أو نفّذ `ISCC.exe installer\LinguaDeskPro_Setup.iss`) لتوليد ملف المثبت `ReadyToInstall\Installer_Build\LinguaDeskPro_Setup_v2.5.0.exe`.

### الخيار الرابع: إعادة بناء قاعدة بيانات SQLite من الصفر
```bash
python3 scripts/build_dictionary_db.py
```
