# دليل البناء والتجميع والتوزيع (BUILD.md)
**LinguaDesk Pro v7.0 — عمل المهندس محمد البكير (Mohammed Albukeer)**  
[README (English)](README.md) | [README\_AR (العربية)](https://www.google.com/search?q=README_AR.md)

## 1. البنية المعمارية ومشاريع الحل البرمجي (`src/`)

يضم المجلد `src/` المشاريع التالية المبنية لمنصة `.NET 8.0` و `.NET Framework 4.x`:

1. **`src/LinguaDeskPro.SingleExe`** *(المشروع التنفيذي الموحد للإصدار v7.0)*:
   * يضم الملف الموحد `Program.cs` وملف المشروع `LinguaDeskPro.SingleExe.csproj`.
   * يحتوي على محرك القاموس المحلي المدمج في الذاكرة (`OfflineLexiconEngine`)، والنافذة العائمة الأصلية (`FloatingOverlayForm`)، وخادم المزامنة والملفات المحلي (`LocalTcpHttpServer` على المنفذ `127.0.0.1:18955`)، ونظام الاستخراج الذاتي لحزمة الموارد المدمجة (`EmbeddedPayload.zip`) وفك ضغط قاعدة البيانات (`EnsureDatabaseDecompressed`).
2. **`src/LinguaDeskPro.Core`**: النماذج الأساسية، مطبّع النصوص العربية (`ArabicNormalizer`)، خوارزمية البحث التقريبي (`FuzzyMatcher`)، ومحرك التكرار المتباعد (`SpacedRepetitionEngine`).
3. **`src/LinguaDeskPro.Dictionary`**: مستودع قاعدة بيانات SQLite (`SqliteDictionaryRepository`) والمحلل الصرفي (`MorphologicalAnalyzer`).
4. **`src/LinguaDeskPro.Translation`**: محرك الترجمة السياقي القواعدي المحلي (`OfflineContextualTranslator`) ومزود الترجمة السحابي (`OnlineTranslationProvider`).
5. **`src/LinguaDeskPro.Speech`**: خدمة النطق الصوتي المحلي لنظام ويندوز عبر `System.Speech.Synthesis`.
6. **`src/LinguaDeskPro.OCR`**: وحدة التعرف الضوئي على النصوص وجسر `Windows.Media.Ocr` (`scripts/windows_ocr/win_ocr.ps1`).
7. **`src/LinguaDeskPro.Integrations`**: خدمة اختصارات لوحة المفاتيح العامة عبر Win32 (`RegisterHotKey`) ومدير الحافظة الآمن.
8. **`src/LinguaDeskPro.Desktop`**: نسخة سطح المكتب الموازية للمضيف الأصلي (`LinguaDeskPro_DesktopHost.cs`).

## 2. طرق بناء المشروع وإنتاج الملف التنفيذي الموحد

### الطريقة الأولى: البناء التلقائي الكامل عبر GitHub Actions (موصى بها)
يعمل ملف سير العمل [.github/workflows/build-single-exe.yml](https://www.google.com/search?q=.github/workflows/build-single-exe.yml) تلقائياً عند كل عملية `git push` أو عبر التشغيل اليدوي (`workflow_dispatch`) على بيئة `windows-latest`، وينفذ الخطوات التالية:
1. استعادة الاعتمادات والتحقق الأمني عبر `dotnet list package --vulnerable`.
2. تنزيل ملفات التعرف الضوئي الكاملة (`ara.traineddata` و `eng.traineddata`) من `tesseract-ocr/tessdata_fast` ومكتبة `Tesseract.js v5.1.1`، وفك ضغط قاعدة البيانات `resources/database/linguadesk_dictionary.db.gz`.
3. ضغط مجلدات `ui/` و `resources/` و `scripts/` داخل الأرشيف `src/LinguaDeskPro.SingleExe/EmbeddedPayload.zip`.
4. نشر الملف التنفيذي الموحد المستقل (`LinguaDeskPro_v7.0_SingleFile_Portable.exe`) عبر `dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true`.
5. تجميع معالج التثبيت الرسمي (`LinguaDeskPro_Setup_v7.0_AllInOne.exe`) عبر **Inno Setup (`iscc`)** ونشر الملفين مباشرة في قسم [**GitHub Releases (`v7.0-latest`)**](https://github.com/25164488-Mohammed/LinguaDeskPro/releases/tag/v7.0-latest).

### الطريقة الثانية: البناء المحلي الفوري على نظام Windows (بدون أدوات خارجية)
لبناء الملف التنفيذي الموحد `LinguaDeskPro_SingleFile.exe` محلياً على أي جهاز يعمل بنظام Windows 10/11 باستخدام مترجم `.NET Framework` المدمج في ويندوز (`csc.exe`):
```bat
BUILD_SINGLE_EXE_LOCALLY.bat
```
يقوم هذا السكربت بضغط الموارد داخل `EmbeddedPayload.zip` وترجمة `src/LinguaDeskPro.SingleExe/Program.cs` مع تضمين الأرشيف كمورد داخلي (`/resource:EmbeddedPayload.zip`).

### الطريقة الثالثة: البناء اليدوي عبر `.NET 8.0 SDK`
إذا كانت حزمة `.NET 8.0 SDK` مثبتة على جهازك:
```powershell
dotnet publish src/LinguaDeskPro.SingleExe/LinguaDeskPro.SingleExe.csproj `
  -c Release `
  -r win-x64 `
  --self-contained true `
  -p:PublishSingleFile=true `
  -p:IncludeNativeLibrariesForSelfExtract=true `
  -p:EnableCompressionInSingleFile=true `
  -o publish/single-exe
```

## 3. تشغيل الاختبارات الآلية وفحص قاعدة البيانات

لتشغيل حزمة الاختبارات القياسية المكونة من 27 اختباراً (تتطلب Python 3):
```bash
python3 tests/run_all_tests.py
```
يقوم السكربت بفك ضغط `resources/database/linguadesk_dictionary.db.gz` تلقائياً عند الحاجة، واختبار البحث المعجمي، والتطبيع العربي، والترجمة السياقية، والـ OCR، ونظام المراجعة `SRS`، ثم يحفظ النتائج الفعلية في `tests/test_results.json`.
