# 🚀 LinguaDesk Pro v7.0 Ultimate — Single-File EXE Edition
**تصميم وتطوير المهندس: محمد البكير (Mohammed Albukeer)**  
**للتواصل المباشر:** `mohammedalbukeer@gmail.com`

---

## ✨ الجديد في الإصدار السابع الشامل (v7.0 Single-File All-In-One Edition)

1. **ملف تنفيذي واحد فقط (`LinguaDeskPro.exe`) عبر GitHub Actions (`.github/workflows/build-single-exe.yml`)**:
   - بمجرد رفع هذه الملفات إلى مستودع GitHub، يكتشف GitHub تلقائياً ملف سير العمل `.github/workflows/build-single-exe.yml` ويقوم بتحميل ملفات المسح الضوئي (`ara.traineddata` + `eng.traineddata` + `Tesseract.js v5.1.1`) ودمجها مع قاعدة البيانات (145,935 مدخلاً) والواجهة في **ملف تنفيذي واحد فقط (`LinguaDeskPro_v7.0_SingleFile_Portable.exe`)** وملف تثبيت واحد شامل (`LinguaDeskPro_Setup_v7.0_AllInOne.exe`).
   - كما يمكنك بناء الملف التنفيذي الوحيد فوراً على جهازك بضغطة مزدوجة على `BUILD_SINGLE_EXE_LOCALLY.bat`.

2. **إصلاح جذري لظهور الحروف الإنجليزية والأرقام بجانب الترجمة في النافذة العائمة الصغيرة**:
   - تم استبدال المحلل القديم بمحلل `ExtractPureTranslationFromGtxJson` الذي يفلتر بصمات النماذج السداسية عشرية (`cbb234f8a91d0e55` و `en_ar_2023q1.md`) بنسبة 100% فلا يظهر أي حرف أو رقم غريب بجانب الترجمة.

3. **ترجمة بدون إنترنت + مزامنة لحظية بين النافذة العائمة والتطبيق الرئيسي**:
   - النافذة العائمة (`Ctrl+Shift+T` / `Alt+Q`) تحمل الآن القاموس المحلي الكامل (`145,935` كلمة ومصطلح وجملة + الأسماء المركبة + الكلمات المتعلمة) داخل الذاكرة (`OfflineLexiconEngine`) لتعمل **بدون إنترنت نهائياً** وبنفس دقة التطبيق الرئيسي.
   - مزامنة ثنائية الاتجاه عبر `/api/sync`: أي نص تترجمه في النافذة العائمة ينتقل فوراً إلى التطبيق الرئيسي وسجل الترجمات، وأي كلمة تتعلمها في التطبيق الرئيسي تنتقل فوراً إلى النافذة العائمة.

4. **إصلاح جذري لتراكم المهمات في الخلفية وعدم إعاقة إيقاف تشغيل الكمبيوتر (Shutdown)**:
   - عند تشغيل التطبيق، يقوم `TerminatePreviousInstances()` بإنهاء أي مهمة سابقة تلقائياً بحيث لا توجد سوى مهمة واحدة فقط في مدير المهام (Task Manager).
   - عند إغلاق نافذة التطبيق الرئيسي، يرسل التطبيق إشارة `/api/app-closed` فينهي المهمة الخلفية تلقائياً ولا تبقى عالقة في الخلفية.
   - يعترض التطبيق رسائل إيقاف تشغيل ويندوز (`WM_QUERYENDSESSION` و `WM_ENDSESSION` و `SystemEvents.SessionEnding`) ويغلق نفسه فوراً خلال أجزاء من الثانية حتى ينطفئ الكمبيوتر بسلاسة تامة.

5. **مكتبات محدثة بالكامل لأحدث إصدار أمني (Zero Vulnerabilities)**:
   - يعتمد مشروع `LinguaDeskPro.SingleExe` على `.NET 8.0` المحدث بالكامل دون أي حزم خارجية قديمة أو مصابة بثغرات (`0 Known Vulnerabilities`)، مع تفعيل الفحص الأمني التلقائي `dotnet list package --vulnerable` و `Dependabot` اليومي.

---

## 🛠️ طريقة الرفع إلى GitHub والحصول على الملف التنفيذي الوحيد (`EXE`)

1. ارفع جميع ملفات ومجلدات هذه الحزمة (بما فيها مجلد `.github/workflows/build-single-exe.yml`) إلى مستودعك في **GitHub**.
2. انتقل إلى تبويب **Actions** في مستودع GitHub — ستجد سير العمل **Build LinguaDesk Pro v7.0 Single-File EXE (All-In-One)** يعمل تلقائياً.
3. بعد انتهاء البناء (خلال دقيقتين تقريباً)، انزل إلى قسم **Artifacts** وحمّل:
   - `LinguaDeskPro_v7.0_SingleFile_Portable.exe` (ملف `.exe` واحد فقط يعمل ويتثبت مباشرة وبداخله كل شيء).
   - `LinguaDeskPro_Setup_v7.0_AllInOne.exe` (معالج التثبيت الرسمي الموحد بملف واحد فقط).
