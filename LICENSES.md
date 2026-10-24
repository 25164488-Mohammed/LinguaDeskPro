# التراخيص ومصادر البيانات (https://www.google.com/search?q=LICENSES.md)
**LinguaDesk Pro v7.0 — عمل المهندس محمد البكير (Mohammed Albukeer — mohammedalbukeer@gmail.com)**  
[README (English)](README.md) | [README\_AR (العربية)](https://www.google.com/search?q=README_AR.md)

## 1. ترخيص شيفرة المشروع (Application Source Code License)
جميع ملفات الشيفرة المصدرية وهندسة النظام والواجهة ومحرك الترجمة السياقي القواعدي المحلي من **عمل المهندس محمد البكير (Mohammed Albukeer)** ومرخصة بموجب ترخيص **MIT License**:

```text
MIT License

Copyright (c) 2026 Mohammed Albukeer (محمد البكير - mohammedalbukeer@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 2. تراخيص البيانات المعجمية والمكونات مفتوحة المصدر المضمنة

| المورد اللغوي / البرمجي | الوظيفة في التطبيق | المصدر | الترخيص | قابلية إعادة التوزيع |
| :--- | :--- | :--- | :--- | :--- |
| **Core Curated Bilingual Lexicon** | المداخل المعجمية المحررة ثنائية الاتجاه والأمثلة والشروح (`full_lexicon_db.js` + `linguadesk_dictionary.db.gz`) | Princeton WordNet 3.1 + Wiktionary Extracts + تحرير محمد البكير | WordNet License / CC-BY-SA 4.0 | مسموح مع نسبة المصدر |
| **Hunspell en_US Morphological Index** | الجذور الإنجليزية والمشتقات الصرفية والتصحيح الإملائي | SCOWL / Hunspell `en_US` | LGPL / MPL / BSD | مسموح بالكامل |
| **SQLite 3 Engine & FTS5** | محرك قواعد البيانات المحلي والفهرسة النصية السريعة | SQLite Consortium | Public Domain | ملكية عامة |
| **Tesseract OCR & Traineddata (`ara` + `eng`)** | نماذج ومكتبة استخراج النصوص العربية والإنجليزية من الصور (`Tesseract.js v5.1.1` + `tessdata_fast`) | Google / Tesseract OCR / Naptha (`tesseract.js`) | Apache License 2.0 | مسموح بالكامل |
| **Contextual Rules & Lexical Matrix** | قواعد إعادة الترتيب النحوي والصرفي المحلية (`contextual_rules_v2.json`) | تطوير محمد البكير (Mohammed Albukeer) | MIT License | مسموح بالكامل |
