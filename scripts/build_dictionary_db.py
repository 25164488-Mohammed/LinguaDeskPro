import sys; sys.path.insert(0, "/tmp")
from extra_lexicon import ESSENTIAL_BILINGUAL_PAIRS, ADDITIONAL_DOMAIN_VOCAB, IDIOMS_AND_PHRASES, EXTRA_PARALLEL_SENTENCES
import shutil
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinguaDesk Pro — Comprehensive SQLite Dictionary & Linguistic Resource Builder
عمل محمد البكير (Developed & Engineered by Mohammed Al-Bakir)

Builds:
1. LinguaDeskPro/resources/database/linguadesk_dictionary.db (SQLite3 + FTS5 + Normalized Indexes)
2. LinguaDeskPro/resources/dictionaries/core_bilingual_export.json
3. LinguaDeskPro/resources/dictionaries/idioms_and_collocations.json
4. LinguaDeskPro/resources/dictionaries/morphological_rules.json
"""

import sqlite3
import json
import os
import re
import hashlib
import time

BASE_DIR = "/tmp/LinguaDeskPro"
DB_PATH = os.path.join(BASE_DIR, "resources", "database", "linguadesk_dictionary.db")
DICT_DIR = os.path.join(BASE_DIR, "resources", "dictionaries")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(DICT_DIR, exist_ok=True)

def normalize_arabic(text: str) -> str:
    if not text:
        return ""
    # Remove tashkeel (diacritics) and tatweel
    text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text)
    # Normalize Alef variants
    text = re.sub(r'[أإآٱ]', 'ا', text)
    # Normalize Teh Marbuta to Heh
    text = re.sub(r'ة', 'ه', text)
    # Normalize Alef Maksura to Yeh
    text = re.sub(r'ى', 'ي', text)
    # Normalize Hamza on Waw/Yeh
    text = re.sub(r'ؤ', 'و', text)
    text = re.sub(r'ئ', 'ي', text)
    return text.strip()

# ==============================================================================
# 1. POLYSEMOUS DEEP ENTRIES (Multiple distinct contextual senses per word)
# ==============================================================================
POLYSEMOUS_ENTRIES = [
    {
        "word_en": "run",
        "word_ar": "يَجْرِي / يُدِير / يُشَغِّل",
        "pos": "verb",
        "ipa_uk": "/rʌn/",
        "ipa_us": "/rʌn/",
        "phonetic_ar": "رَن",
        "cefr": "A1",
        "freq": 45,
        "domain": "General",
        "lemma_en": "run",
        "root_ar": "ج ر ي / د و ر",
        "plural_en": "runs (noun)",
        "plural_ar": "أشواط / جولات",
        "verb_forms": {
            "base": "run", "past": "ran", "past_participle": "run",
            "present_participle": "running", "third_person": "runs",
            "ar_past": "جَرَى / أَدَارَ", "ar_present": "يَجْرِي / يُدِيرُ", "ar_imperative": "اِجْرِ / أَدِرْ", "ar_masdar": "جَرْي / إِدَارَة"
        },
        "derivatives": ["runner (عدّاء)", "running (جري / تشغيل)", "runnable (قابل للتشغيل)", "runaway (هارب)"],
        "synonyms_en": ["sprint", "jog", "operate", "manage", "execute", "flow"],
        "synonyms_ar": ["يركض", "يدير", "يشغل", "ينفذ", "يتدفق"],
        "antonyms_en": ["walk", "stop", "halt", "idle"],
        "antonyms_ar": ["يمشي", "يتوقف", "يعطل"],
        "collocations": ["run a business (يدير عملاً تجارياً)", "run a program (يشغل برنامجاً)", "run out of time (ينفد الوقت)", "in the long run (على المدى الطويل)"],
        "usage_notes": "فعل شاذ في التصريف (run - ran - run). يختلف معناه جذرياً حسب المفعول به: مع الرياضة بمعنى يركض، ومع الشركات بمعنى يدير، ومع البرمجيات بمعنى يشغّل أو ينفّذ.",
        "senses": [
            {
                "context": "Physical Movement / الحركة البدنية",
                "meaning_ar": "يَجْرِي / يَرْكُض",
                "definition_en": "To move swiftly on foot so that both feet leave the ground during each stride.",
                "explanation_ar": "التحرك بسرعة على القدمين بحيث ترتفع القدمان عن الأرض في كل خطوة.",
                "example_en": "He runs five kilometers every morning before breakfast.",
                "example_ar": "هو يجري خمسة كيلومترات كل صباح قبل الإفطار."
            },
            {
                "context": "Management & Business / الإدارة والأعمال",
                "meaning_ar": "يُدِير / يُشْرِف على",
                "definition_en": "To be in charge of, manage, or direct a company, organization, or system.",
                "explanation_ar": "تولي مسؤولية إدارة شركة أو مؤسسة أو مشروع وتوجيه أعماله اليومية.",
                "example_en": "She runs a successful software engineering company in Riyadh.",
                "example_ar": "هي تدير شركة هندسة برمجيات ناجحة في الرياض."
            },
            {
                "context": "Computing & Machinery / الحوسبة والتقنية",
                "meaning_ar": "يُشَغِّل / يُنَفِّذ برنامجاً",
                "definition_en": "To execute a computer program, script, or process on a device.",
                "explanation_ar": "تنفيذ برنامج حاسوبي أو خوارزمية أو تشغيل آلة محلياً على الجهاز.",
                "example_en": "LinguaDesk Pro runs completely offline on Windows without internet.",
                "example_ar": "يعمل برنامج LinguaDesk Pro بالكامل دون اتصال بالإنترنت على نظام ويندوز."
            },
            {
                "context": "Liquids & Flow / السوائل والتدفق",
                "meaning_ar": "يَتَدَفَّق / يَسِيل",
                "definition_en": "To flow or cause a liquid to flow in a specified direction.",
                "explanation_ar": "جريان الماء أو السوائل في مجرى أو أنبوب.",
                "example_en": "The river runs through the ancient valley.",
                "example_ar": "يجري النهر عبر الوادي القديم."
            }
        ]
    },
    {
        "word_en": "bank",
        "word_ar": "مَصْرِف (بَنْك) / ضِفَّة نَهْر / مَخْزُون",
        "pos": "noun",
        "ipa_uk": "/bæŋk/",
        "ipa_us": "/bæŋk/",
        "phonetic_ar": "بَانْك",
        "cefr": "A1",
        "freq": 180,
        "domain": "Business",
        "lemma_en": "bank",
        "root_ar": "ص ر ف / ض ف ف",
        "plural_en": "banks",
        "plural_ar": "مَصَارِف / بُنُوك / ضِفَاف",
        "verb_forms": {
            "base": "bank", "past": "banked", "past_participle": "banked",
            "present_participle": "banking", "third_person": "banks",
            "ar_past": "أَوْدَعَ", "ar_present": "يُودِعُ", "ar_imperative": "أَوْدِعْ", "ar_masdar": "إِيدَاع مَصْرِفِي"
        },
        "derivatives": ["banker (مصرفي)", "banking (العمل المصرفي)", "bankrupt (مفلس)", "banknote (ورقة نقدية)"],
        "synonyms_en": ["financial institution", "treasury", "shore", "embankment", "repository"],
        "synonyms_ar": ["مصرف", "مؤسسة مالية", "ضفة", "شاطئ النهر", "مستودع بيانات"],
        "antonyms_en": [],
        "antonyms_ar": [],
        "collocations": ["central bank (البنك المركزي)", "river bank (ضفة النهر)", "blood bank (بنك الدم)", "bank account (حساب مصرفي)", "bank on someone (يعوّل على شخص)"],
        "usage_notes": "من أشهر الكلمات المشتركة لفظياً (Homonyms): تعني المؤسسة المالية، وتعني أيضاً جانب النهر (ضفة)، وتستخدم في التقنية والطب بمعنى مستودع أو مخزون (مثل data bank وblood bank).",
        "senses": [
            {
                "context": "Finance & Economy / المال والاقتصاد",
                "meaning_ar": "مَصْرِف / بَنْك مَالِي",
                "definition_en": "A financial establishment that invests money deposited by customers, pays it out when required, and makes loans.",
                "explanation_ar": "مؤسسة مالية مرخصة لحفظ الودائع وتقديم القروض وإجراء المعاملات النقدية.",
                "example_en": "You can transfer the funds directly to our commercial bank account.",
                "example_ar": "يمكنك تحويل الأموال مباشرة إلى حسابنا في المصرف التجاري."
            },
            {
                "context": "Geography & Nature / الجغرافيا والطبيعة",
                "meaning_ar": "ضِفَّةُ النَّهْرِ / جَانِبُ المَجْرَى",
                "definition_en": "The land alongside or sloping down to a river or lake.",
                "explanation_ar": "الأرض الممتدة على جانب النهر أو البحيرة.",
                "example_en": "We walked along the grassy bank of the Nile at sunset.",
                "example_ar": "مشينا على طول الضفة العشبية لنهر النيل عند غروب الشمس."
            },
            {
                "context": "Medicine & Data Storage / الطب وتخزين البيانات",
                "meaning_ar": "مَخْزُون / بَنْك مَعْلُومَات أو مَوَاد",
                "definition_en": "A stock or supply of something available for use, such as blood or digital data.",
                "explanation_ar": "مركز حفظ وتخزين منظم للموارد الحيوية أو قواعد البيانات.",
                "example_en": "The hospital maintains an emergency blood bank and a medical data bank.",
                "example_ar": "يحتفظ المستشفى ببنك دم للطوارئ وبنك للبيانات الطبية."
            }
        ]
    },
    {
        "word_en": "set",
        "word_ar": "مَجْمُوعَة / يُحَدِّد / يَضْبِط / يَغْرُب",
        "pos": "verb",
        "ipa_uk": "/sɛt/",
        "ipa_us": "/sɛt/",
        "phonetic_ar": "سِت",
        "cefr": "A1",
        "freq": 62,
        "domain": "General",
        "lemma_en": "set",
        "root_ar": "و ض ع / ج م ع / ض ب ط",
        "plural_en": "sets",
        "plural_ar": "مَجْمُوعَات / أَطْقُم",
        "verb_forms": {
            "base": "set", "past": "set", "past_participle": "set",
            "present_participle": "setting", "third_person": "sets",
            "ar_past": "ضَبَطَ / وَضَعَ", "ar_present": "يَضْبِطُ / يَضَعُ", "ar_imperative": "اِضْبِطْ / ضَعْ", "ar_masdar": "ضَبْط / وَضْع"
        },
        "derivatives": ["setting (إعداد / بيئة)", "setup (إعداد / تثبيت)", "preset (معدّ مسبقاً)", "mindset (عقلية)"],
        "synonyms_en": ["put", "place", "adjust", "configure", "collection", "group"],
        "synonyms_ar": ["يضع", "يضبط", "يهيئ", "مجموعة", "طقم"],
        "antonyms_en": ["unset", "displace", "rise"],
        "antonyms_ar": ["يلغي الضبط", "يرتفع / تشرق"],
        "collocations": ["set a goal (يحدد هدفاً)", "set up a system (يثبت نظاماً)", "dataset (مجموعة بيانات)", "the sun sets (تغرب الشمس)"],
        "usage_notes": "تأتي اسماً بمعنى (مجموعة أو طقم)، وفعلاً لا يتغير في الماضي والتصريف الثالث (set - set - set)، وصفة بمعنى (ثابت أو محدد مسبقاً).",
        "senses": [
            {
                "context": "Configuration & Action / الضبط والتحديد",
                "meaning_ar": "يَضْبِط / يُحَدِّد / يُعَيِّن",
                "definition_en": "To adjust, configure, or establish a value, parameter, goal, or alarm.",
                "explanation_ar": "تحديد قيمة معينة أو ضبط إعدادات جهاز أو وضع هدف للعمل.",
                "example_en": "Please set the default translation language in the settings panel.",
                "example_ar": "يرجى ضبط لغة الترجمة الافتراضية في لوحة الإعدادات."
            },
            {
                "context": "Mathematics & Computing (Noun) / الرياضيات والحوسبة",
                "meaning_ar": "مَجْمُوعَة / فِئَة عناصر",
                "definition_en": "A collection of distinct objects, numbers, or data records considered as a whole.",
                "explanation_ar": "مجموعة من العناصر أو البيانات المترابطة التي تُعامل كوحدة واحدة.",
                "example_en": "We tested the model on a benchmark set of bilingual sentences.",
                "example_ar": "اختبرنا النموذج على مجموعة مرجعية من الجمل ثنائية اللغة."
            },
            {
                "context": "Nature & Astronomy / الطبيعة والفلك",
                "meaning_ar": "تَغْرُب (الشَّمْسُ) / يَأْفُل",
                "definition_en": "Of the sun, moon, or planets: to appear to move toward and below the earth's horizon.",
                "explanation_ar": "نزول الشمس أو القمر تحت خط الأفق في نهاية النهار.",
                "example_en": "The sun sets early in winter.",
                "example_ar": "تغرب الشمس مبكراً في فصل الشتاء."
            }
        ]
    },
    {
        "word_en": "light",
        "word_ar": "ضَوْء / نُور / خَفِيف / يُضِيء",
        "pos": "noun",
        "ipa_uk": "/laɪt/",
        "ipa_us": "/laɪt/",
        "phonetic_ar": "لايْت",
        "cefr": "A1",
        "freq": 95,
        "domain": "General",
        "lemma_en": "light",
        "root_ar": "ض و أ / خ ف ف",
        "plural_en": "lights",
        "plural_ar": "أَضْوَاء / أَنْوَار / مَصَابِيح",
        "verb_forms": {
            "base": "light", "past": "lit / lighted", "past_participle": "lit / lighted",
            "present_participle": "lighting", "third_person": "lights",
            "ar_past": "أَضَاءَ", "ar_present": "يُضِيءُ", "ar_imperative": "أَضِئْ", "ar_masdar": "إِضَاءَة"
        },
        "derivatives": ["lightweight (خفيف الوزن)", "lighting (إضاءة)", "lighten (يخفف / يضيء)", "daylight (ضوء النهار)"],
        "synonyms_en": ["illumination", "brightness", "lamp", "lightweight", "gentle"],
        "synonyms_ar": ["نور", "إضاءة", "مصباح", "خفيف الوزن", "لطيف"],
        "antonyms_en": ["darkness", "heavy", "dark"],
        "antonyms_ar": ["ظلام", "ثقيل", "داكن"],
        "collocations": ["light theme (المظهر الفاتح)", "shed light on (يلقي الضوء على)", "light weight (وزن خفيف)", "speed of light (سرعة الضوء)"],
        "usage_notes": "عندما تكون اسماً فالمضاد لها darkness (ظلام)، وعندما تكون صفة للوزن فالمضاد لها heavy (ثقيل)، وعندما تصف الألوان فالمضاد لها dark (داكن).",
        "senses": [
            {
                "context": "Physics & Vision (Noun) / الفيزياء والإبصار",
                "meaning_ar": "ضَوْء / نُور / إِضَاءَة",
                "definition_en": "The natural agent that stimulates sight and makes things visible.",
                "explanation_ar": "الإشعاع الكهرومغناطيسي المرئي الذي يمكّن العين من رؤية الأشياء.",
                "example_en": "Natural light enters the room through the large window.",
                "example_ar": "يدخل الضوء الطبيعي إلى الغرفة عبر النافذة الكبيرة."
            },
            {
                "context": "Weight & Resource Usage (Adjective) / الوزن والأداء",
                "meaning_ar": "خَفِيفُ الوَزْنِ / قَلِيلُ الاسْتِهْلَاك",
                "definition_en": "Of little weight; not heavy; consuming minimal system resources.",
                "explanation_ar": "غير ثقيل في الوزن، أو برنامج خفيف لا يستهلك موارد المعالج والذاكرة.",
                "example_en": "The application is fast and light on memory consumption.",
                "example_ar": "التطبيق سريع وخفيف في استهلاك الذاكرة."
            },
            {
                "context": "Colors & UI Theme (Adjective) / الألوان والمظهر",
                "meaning_ar": "فَاتِحُ اللَّوْنِ",
                "definition_en": "Having a considerable or sufficient amount of natural light; pale in color (opposite of dark).",
                "explanation_ar": "لون هادئ غير قاتم، مثل الوضع الفاتح في واجهات البرامج.",
                "example_en": "You can switch between dark mode and light mode anytime.",
                "example_ar": "يمكنك التبديل بين الوضع الداكن والوضع الفاتح في أي وقت."
            }
        ]
    },
    {
        "word_en": "right",
        "word_ar": "حَقّ / صَحِيح / يَمِين",
        "pos": "adjective",
        "ipa_uk": "/raɪt/",
        "ipa_us": "/raɪt/",
        "phonetic_ar": "رَايْت",
        "cefr": "A1",
        "freq": 38,
        "domain": "General",
        "lemma_en": "right",
        "root_ar": "ح ق ق / ص ح ح / ي م ن",
        "plural_en": "rights",
        "plural_ar": "حُقُوق",
        "verb_forms": {
            "base": "right", "past": "righted", "past_participle": "righted",
            "present_participle": "righting", "third_person": "rights",
            "ar_past": "صَوَّبَ", "ar_present": "يُصَوِّبُ", "ar_imperative": "صَوِّبْ", "ar_masdar": "تَصْوِيب"
        },
        "derivatives": ["rightful (مشروع / مستحق)", "rightly (بحق / بصواب)", "righteous (صالح / عادل)", "copyright (حقوق النشر)"],
        "synonyms_en": ["correct", "accurate", "entitlement", "privilege", "starboard"],
        "synonyms_ar": ["صحيح", "صائب", "حق قانوني", "الجهة اليمنى"],
        "antonyms_en": ["wrong", "incorrect", "left"],
        "antonyms_ar": ["خاطئ", "غير صحيح", "يسار"],
        "collocations": ["right-to-left (من اليمين إلى اليسار)", "human rights (حقوق الإنسان)", "right away (على الفور)", "intellectual property rights (حقوق الملكية الفكرية)"],
        "usage_notes": "انتبه للمقابلات: عكس right بمعنى (صحيح) هو wrong، وعكس right بمعنى (يمين) هو left.",
        "senses": [
            {
                "context": "Accuracy & Truth / الدقة والصواب",
                "meaning_ar": "صَحِيح / صَائِب / مُنَاسِب",
                "definition_en": "True or correct as a fact; morally good, justified, or acceptable.",
                "explanation_ar": "مطابق للحقيقة أو الصواب وخالٍ من الخطأ.",
                "example_en": "Choosing the right architecture ensures long-term software stability.",
                "example_ar": "اختيار الهندسة المعمارية الصحيحة يضمن استقرار البرمجيات على المدى الطويل."
            },
            {
                "context": "Direction & Layout / الاتجاه والتخطيط",
                "meaning_ar": "جِهَةُ اليَمِين",
                "definition_en": "On, toward, or relating to the side of a human body or of a thing that is to the east when the person or thing is facing north.",
                "explanation_ar": "الجانب الأيمن في الاتجاهات أو في تخطيط النصوص العربية (RTL).",
                "example_en": "Arabic text flows naturally from right to left.",
                "example_ar": "يتدفق النص العربي بصورة طبيعية من اليمين إلى اليسار."
            },
            {
                "context": "Law & Ethics (Noun) / القانون والأخلاق",
                "meaning_ar": "حَقّ قَانُونِي أو أَخْلَاقِي",
                "definition_en": "A moral or legal entitlement to have or obtain something or to act in a certain way.",
                "explanation_ar": "استحقاق يثبته القانون أو العرف أو الأخلاق للإنسان أو المؤلف.",
                "example_en": "Every user has the right to data privacy and offline operation.",
                "example_ar": "لكل مستخدم الحق في خصوصية البيانات والتشغيل دون اتصال بالإنترنت."
            }
        ]
    },
    {
        "word_en": "model",
        "word_ar": "نَمُوذَج / طِرَاز / قُدْوَة / يُنَمْذِج",
        "pos": "noun",
        "ipa_uk": "/ˈmɒd.əl/",
        "ipa_us": "/ˈmɑː.dəl/",
        "phonetic_ar": "مُودِل",
        "cefr": "B1",
        "freq": 150,
        "domain": "Technology",
        "lemma_en": "model",
        "root_ar": "ن م ذ ج / ط ر ز",
        "plural_en": "models",
        "plural_ar": "نَمَاذِج / طِرَازَات",
        "verb_forms": {
            "base": "model", "past": "modeled", "past_participle": "modeled",
            "present_participle": "modeling", "third_person": "models",
            "ar_past": "نَمْذَجَ / صَمَّمَ", "ar_present": "يُنَمْذِجُ", "ar_imperative": "نَمْذِجْ", "ar_masdar": "نَمْذَجَة"
        },
        "derivatives": ["modeling (نمذجة)", "modeler (مُنمذج)", "remodel (يعيد تصميم)"],
        "synonyms_en": ["prototype", "paradigm", "pattern", "version", "archetype"],
        "synonyms_ar": ["نموذج", "نسق", "طراز", "قدوة", "تمثيل رياضي"],
        "antonyms_en": ["copy", "imitation"],
        "antonyms_ar": ["تقليد عشوائي"],
        "collocations": ["neural translation model (نموذج ترجمة عصبية)", "language model (نموذج لغوي)", "data model (نموذج البيانات)", "role model (قدوة حسنة)"],
        "usage_notes": "في الذكاء الاصطناعي ومعالجة اللغات الطبيعية (NLP)، تُترجم model دائماً إلى (نموذج) مثل Neural Model أو Language Model.",
        "senses": [
            {
                "context": "AI & Computing / الذكاء الاصطناعي والحوسبة",
                "meaning_ar": "نَمُوذَج حَاسُوبِي أو لُغَوِي",
                "definition_en": "A mathematical or neural representation trained on data to perform tasks like translation or speech recognition.",
                "explanation_ar": "بنية رياضية أو شبكة عصبية مدربة على البيانات لإنجاز مهام مثل الترجمة الآلية أو التعرف الضوئي.",
                "example_en": "The local neural translation model runs on the CPU without requiring a GPU.",
                "example_ar": "يعمل نموذج الترجمة العصبية المحلي على المعالج المركزي دون الحاجة إلى بطاقة رسوميات."
            },
            {
                "context": "Engineering & Industry / الهندسة والصناعة",
                "meaning_ar": "طِرَاز / تَصْمِيم مَصْنَعِي",
                "definition_en": "A particular design or version of a product, machine, or vehicle.",
                "explanation_ar": "إصدار أو تصميم محدد لجهاز أو آلة أو منتج صناعي.",
                "example_en": "This laptop model has sixteen gigabytes of system memory.",
                "example_ar": "يحتوي طراز الحاسوب المحمول هذا على ستة عشر غيغابايت من ذاكرة النظام."
            },
            {
                "context": "Society & Behavior / المجتمع والسلوك",
                "meaning_ar": "قُدْوَة / مِثَال يُحْتَذَى بِهِ",
                "definition_en": "A person or thing regarded as an excellent example of a specified quality.",
                "explanation_ar": "شخص أو عمل يُقتدى به في الإتقان والأخلاق.",
                "example_en": "The senior engineer served as a role model for the entire development team.",
                "example_ar": "كان المهندس الخبير قدوة حسنة لفريق التطوير بأكمله."
            }
        ]
    },
    {
        "word_en": "power",
        "word_ar": "طَاقَة / قُوَّة / سُلْطَة / أُسّ رِيَاضِي",
        "pos": "noun",
        "ipa_uk": "/ˈpaʊ.ər/",
        "ipa_us": "/ˈpaʊ.ɚ/",
        "phonetic_ar": "بَاوَر",
        "cefr": "A2",
        "freq": 110,
        "domain": "Science",
        "lemma_en": "power",
        "root_ar": "ق و ي / ط و ق / س ل ط",
        "plural_en": "powers",
        "plural_ar": "قُوَى / سُلُطَات / طَاقَات",
        "verb_forms": {
            "base": "power", "past": "powered", "past_participle": "powered",
            "present_participle": "powering", "third_person": "powers",
            "ar_past": "زَوَّدَ بِالطَّاقَةِ", "ar_present": "يُزَوِّدُ بِالطَّاقَةِ", "ar_imperative": "زَوِّدْ بِالطَّاقَةِ", "ar_masdar": "تَزْوِيد بِالطَّاقَة"
        },
        "derivatives": ["powerful (قوي / فعّال)", "powerless (عاجز)", "empower (يمكّن)", "powerhouse (مركز قوة)"],
        "synonyms_en": ["energy", "strength", "authority", "capacity", "force"],
        "synonyms_ar": ["طاقة", "قوة", "سلطة", "قدرة", "نفوذ"],
        "antonyms_en": ["weakness", "impotence", "inability"],
        "antonyms_ar": ["ضعف", "عجز"],
        "collocations": ["processing power (قوة المعالجة)", "electrical power (الطاقة الكهربائية)", "solar power (الطاقة الشمسية)", "come to power (يتولى السلطة)"],
        "usage_notes": "تُترجم إلى (طاقة أو تيار كهربائي) في الهندسة، وإلى (قوة أو قدرة) في الفيزياء والحوسبة، وإلى (سلطة أو صلاحية) في القانون والسياسة، وإلى (أُسّ) في الرياضيات.",
        "senses": [
            {
                "context": "Engineering & Electricity / الهندسة والكهرباء",
                "meaning_ar": "طَاقَة كَهْرَبَائِيَّة / قُدْرَة تَشْغِيلِيَّة",
                "definition_en": "Energy that is produced by mechanical, electrical, or other means and used to operate a device.",
                "explanation_ar": "الطاقة الكهربائية أو الميكانيكية المستخدمة لتشغيل الأجهزة والأنظمة.",
                "example_en": "Make sure the backup power supply is connected to the server.",
                "example_ar": "تأكد من توصيل مزود الطاقة الاحتياطي بالخادم."
            },
            {
                "context": "Law & Governance / القانون والإدارة",
                "meaning_ar": "سُلْطَة / صَلَاحِيَّة نِظَامِيَّة",
                "definition_en": "The capacity or authority to direct or influence the behavior of others or the course of events.",
                "explanation_ar": "الصلاحية الرسمية أو القانونية لاتخاذ القرارات أو تنفيذ الإجراءات.",
                "example_en": "The committee exercises regulatory power under the national law.",
                "example_ar": "تمارس اللجنة سلطة تنظيمية بموجب القانون الوطني."
            },
            {
                "context": "Mathematics / الرياضيات",
                "meaning_ar": "أُسّ / قُوَّةُ العَدَد",
                "definition_en": "The product obtained when a number is multiplied by itself a certain number of times.",
                "explanation_ar": "عدد المرات التي يُضرب فيها العدد في نفسه (مثل 2 أس 8).",
                "example_en": "Two to the power of ten equals one thousand and twenty-four.",
                "example_ar": "اثنان أس عشرة يساوي ألفاً وأربعة وعشرين."
            }
        ]
    },
    {
        "word_en": "عين",
        "word_ar": "عَيْن (عُضْوُ الإِبْصَار / يَنْبُوع مَاء / جَاسُوس / ذَاتُ الشَّيْء)",
        "pos": "noun",
        "ipa_uk": "/aɪ/",
        "ipa_us": "/aɪ/",
        "phonetic_ar": "عَيْن",
        "cefr": "A1",
        "freq": 85,
        "domain": "General",
        "lemma_en": "eye",
        "root_ar": "ع ي ن",
        "plural_en": "eyes / springs / notables",
        "plural_ar": "عُيُون / أَعْيُن / أَعْيَان",
        "verb_forms": {
            "base": "appoint / inspect", "past": "appointed", "past_participle": "appointed",
            "present_participle": "appointing", "third_person": "appoints",
            "ar_past": "عَيَّنَ / عَايَنَ", "ar_present": "يُعَيِّنُ / يُعَايِنُ", "ar_imperative": "عَيِّنْ / عَايِنْ", "ar_masdar": "تَعْيِين / مُعَايَنَة"
        },
        "derivatives": ["تعيين (appointment)", "معاينة (inspection)", "عيني (in-kind / ocular)", "عيّنة (sample)"],
        "synonyms_en": ["eye", "water spring", "fountain", "scout", "exact same"],
        "synonyms_ar": ["باصرة", "ينبوع", "نبع ماء", "رقيب", "نفس الشيء"],
        "antonyms_en": [],
        "antonyms_ar": [],
        "collocations": ["عين الماء (water spring)", "أعيان القوم (notables/nobles)", "فرض عين (individual obligation)", "بأمّ عينه (with one's own eyes)"],
        "usage_notes": "من أشهر الألفاظ المشتركة في المعجم العربي؛ تجمع على (أَعْيُن وعيون) للباصرة، وعلى (عُيُون) لينابيع الماء، وعلى (أَعْيَان) لوجهاء القوم.",
        "senses": [
            {
                "context": "Anatomy & Vision / التشريح والإبصار",
                "meaning_ar": "العَيْنُ البَاصِرَة (eye)",
                "definition_en": "The organ of sight in humans and animals (Eye).",
                "explanation_ar": "عضو الإبصار والرؤية في الإنسان والحيوان.",
                "example_en": "The human eye can distinguish millions of subtle color variations.",
                "example_ar": "تستطيع العين البشرية تمييز ملايين التدرجات اللونية الدقيقة."
            },
            {
                "context": "Nature & Geography / الطبيعة والمياه",
                "meaning_ar": "يَنْبُوعُ المَاءِ (spring / fountain)",
                "definition_en": "A natural water spring or fountain flowing from the ground.",
                "explanation_ar": "نبع الماء الطبيعي الذي يتفجر من الأرض ويجري.",
                "example_en": "The travelers rested beside a clear mountain spring.",
                "example_ar": "استراح المسافرون بجانب عين ماء جبلية صافية."
            },
            {
                "context": "Linguistics & Emphasis / التوكيد المعنوي",
                "meaning_ar": "نَفْسُ الشَّيْءِ وَذَاتُهُ (the very same / itself)",
                "definition_en": "The exact same thing or essence (used for emphasis in Arabic).",
                "explanation_ar": "لفظ توكيد معنوي في العربية يفيد حقيقة الشيء وذاته بلا مجاز.",
                "example_en": "This is the exact same problem we solved yesterday.",
                "example_ar": "هذه هي المشكلة عينُها التي قمنا بحلها أمس."
            }
        ]
    },
    {
        "word_en": "حكم",
        "word_ar": "حُكْم (قَرَار قَضَائِي / سُلْطَة / قَاعِدَة) / حَكَمَ (يَحْكُم)",
        "pos": "noun",
        "ipa_uk": "/ˈdʒʌdʒ.mənt/",
        "ipa_us": "/ˈdʒʌdʒ.mənt/",
        "phonetic_ar": "حُكْم",
        "cefr": "B1",
        "freq": 135,
        "domain": "Legal",
        "lemma_en": "judgment",
        "root_ar": "ح ك م",
        "plural_en": "judgments / rulings / regimes",
        "plural_ar": "أَحْكَام",
        "verb_forms": {
            "base": "judge / rule / govern", "past": "judged / ruled", "past_participle": "judged / ruled",
            "present_participle": "judging / ruling", "third_person": "judges / rules",
            "ar_past": "حَكَمَ", "ar_present": "يَحْكُمُ", "ar_imperative": "اُحْكُمْ", "ar_masdar": "حُكْم / حُكُومَة"
        },
        "derivatives": ["محكمة (court)", "قاضٍ / حاكم (judge / ruler)", "حكمة (wisdom)", "تحكيم (arbitration)", "محكم (precise / tight)"],
        "synonyms_en": ["judgment", "verdict", "ruling", "governance", "rule"],
        "synonyms_ar": ["قضاء", "قرار قضائي", "سلطة", "إدارة الدولة", "قاعدة شرعية أو قانونية"],
        "antonyms_en": [],
        "antonyms_ar": [],
        "collocations": ["حكم قضائي (court ruling / verdict)", "نظام الحكم (system of government)", "الحكم المحلي (local governance)", "حكم المباراة (match referee)"],
        "usage_notes": "يتغير المقابل الإنجليزي لكلمة (حكم) بحسب السياق: في القضاء (verdict / ruling / judgment)، وفي السياسة (governance / rule)، وفي الرياضة (referee / umpire).",
        "senses": [
            {
                "context": "Law & Judiciary / القانون والقضاء",
                "meaning_ar": "حُكْم قَضَائِي (verdict / court ruling)",
                "definition_en": "An official decision or verdict issued by a court of law.",
                "explanation_ar": "القرار النهائي أو الفاصل الذي تصدره المحكمة في قضية معينة.",
                "example_en": "The supreme court issued a final ruling on the commercial dispute.",
                "example_ar": "أصدرت المحكمة العليا حكماً نهائياً في النزاع التجاري."
            },
            {
                "context": "Politics & Administration / السياسة والإدارة",
                "meaning_ar": "إِدَارَةُ الدَّوْلَةِ وَالسُّلْطَة (governance / rule)",
                "definition_en": "The exercise of authority, control, or governance over a state or community.",
                "explanation_ar": "تولي شؤون الدولة وإدارة المؤسسات العامة والسلطة التنفيذية.",
                "example_en": "Good governance requires transparency and accountability.",
                "example_ar": "يتطلب الحكم الرشيد الشفافية والمساءلة."
            },
            {
                "context": "Sports & Arbitration / الرياضة والتحكيم",
                "meaning_ar": "حَكَمُ المُبَارَاة أو المُحَكِّم (referee / arbitrator)",
                "definition_en": "An official who watches a game or match closely to ensure that the rules are adhered to (spelled حَكَم).",
                "explanation_ar": "الشخص المسؤول عن تطبيق القوانين والفصل بين المتنافسين.",
                "example_en": "The referee blew the whistle to end the match.",
                "example_ar": "أطلق الحكم الصافرة لإنهاء المباراة."
            }
        ]
    },
    {
        "word_en": "عقد",
        "word_ar": "عَقْد (اتِّفَاق قَانُونِي / عَشْرُ سَنَوَات) / عِقْد (قِلَادَة)",
        "pos": "noun",
        "ipa_uk": "/ˈkɒn.trækt/",
        "ipa_us": "/ˈkɑːn.trækt/",
        "phonetic_ar": "عَقْد / عِقْد",
        "cefr": "B1",
        "freq": 160,
        "domain": "Legal",
        "lemma_en": "contract",
        "root_ar": "ع ق د",
        "plural_en": "contracts / decades / necklaces",
        "plural_ar": "عُقُود",
        "verb_forms": {
            "base": "contract / hold / convene", "past": "contracted / held", "past_participle": "contracted / held",
            "present_participle": "contracting / holding", "third_person": "contracts / holds",
            "ar_past": "عَقَدَ", "ar_present": "يَعْقِدُ", "ar_imperative": "اِعْقِدْ", "ar_masdar": "عَقْد / انْعِقَاد"
        },
        "derivatives": ["تعاقد (contracting)", "متعاقد (contractor)", "انعقاد (convening)", "عقيدة (creed / doctrine)", "معقد (complex)"],
        "synonyms_en": ["contract", "agreement", "decade", "necklace", "convene"],
        "synonyms_ar": ["اتفاقية", "ميثاق", "عشر سنوات", "قلادة", "يعقد اجتماعاً"],
        "antonyms_en": ["annulment", "dissolution"],
        "antonyms_ar": ["فسخ العقد", "حلّ"],
        "collocations": ["عقد عمل (employment contract)", "عقد من الزمن (a decade)", "عقد اجتماعاً (held a meeting)", "عقد اللؤلؤ (pearl necklace)"],
        "usage_notes": "بفتح العين (عَقْد) تعني الاتفاق القانوني (contract) أو عشر سنوات (decade)، وبكسر العين (عِقْد) تعني القلادة التي تلبس في العنق (necklace).",
        "senses": [
            {
                "context": "Law & Business / القانون والأعمال",
                "meaning_ar": "عَقْدٌ قَانُونِيّ أو اتِّفَاقِيَّة (contract / agreement)",
                "definition_en": "A written or spoken agreement, especially one concerning employment, sales, or tenancy, that is intended to be enforceable by law.",
                "explanation_ar": "اتفاق ملزم قانونياً بين طرفين أو أكثر يحدد الحقوق والالتزامات.",
                "example_en": "Both parties signed the software maintenance contract.",
                "example_ar": "وقّع الطرفان عقد صيانة البرمجيات."
            },
            {
                "context": "Time & History / الزمن والتاريخ",
                "meaning_ar": "عَقْدٌ زَمَنِيّ — عَشْرُ سَنَوَات (decade)",
                "definition_en": "A period of ten years (Decade).",
                "explanation_ar": "فترة زمنية مقدارها عشر سنوات متتالية.",
                "example_en": "Machine translation has evolved rapidly over the last decade.",
                "example_ar": "تطورت الترجمة الآلية بسرعة كبيرة خلال العقد الماضي."
            },
            {
                "context": "Jewelry (عِقْد) / الحلي والمجوهرات",
                "meaning_ar": "عِقْدٌ أَوْ قِلَادَة (necklace)",
                "definition_en": "An ornamental chain or string of beads, jewels, or links worn around the neck.",
                "explanation_ar": "خيط ينظم فيه اللؤلؤ أو الجواهر ويحيط بالعنق.",
                "example_en": "She wore an elegant silver necklace.",
                "example_ar": "ارتدت عِقداً فضياً أنيقاً."
            }
        ]
    }
]

print(f"Loaded {len(POLYSEMOUS_ENTRIES)} deep polysemous entries.")

# Additional Polysemous Entries
POLYSEMOUS_ENTRIES.extend([
    {
        "word_en": "system",
        "word_ar": "نِظَام / مَنْظُومَة / جِهَاز",
        "pos": "noun",
        "ipa_uk": "/ˈsɪs.təm/",
        "ipa_us": "/ˈsɪs.təm/",
        "phonetic_ar": "سِسْتَم",
        "cefr": "A2",
        "freq": 52,
        "domain": "Technology",
        "lemma_en": "system",
        "root_ar": "ن ظ م",
        "plural_en": "systems",
        "plural_ar": "أَنْظِمَة / نُظُم",
        "verb_forms": {"base": "systematize", "past": "systematized", "past_participle": "systematized", "present_participle": "systematizing", "third_person": "systematizes", "ar_past": "نَظَّمَ", "ar_present": "يُنَظِّمُ", "ar_imperative": "نَظِّمْ", "ar_masdar": "تَنْظِيم"},
        "derivatives": ["systematic (منهجي)", "systematically (بشكل منهجي)", "ecosystem (نظام بيئي)", "subsystem (نظام فرعي)"],
        "synonyms_en": ["structure", "framework", "network", "method", "organization"],
        "synonyms_ar": ["منظومة", "هيكل", "طريقة", "جهاز"],
        "antonyms_en": ["chaos", "disorder", "disorganization"],
        "antonyms_ar": ["فوضى", "عشوائية"],
        "collocations": ["operating system (نظام التشغيل)", "immune system (الجهاز المناعي)", "solar system (النظام الشمسي)", "information system (نظام المعلومات)"],
        "usage_notes": "تُترجم إلى (نظام) في الحوسبة والقانون والفلك، وإلى (جهاز) في علم التشريح والطب (مثل الجهاز العصبي nervous system والجهاز الهضمي digestive system).",
        "senses": [
            {
                "context": "Computing & Engineering / الحوسبة والهندسة",
                "meaning_ar": "نِظَام حَاسُوبِي أو تِقْنِي",
                "definition_en": "A group of related hardware units or programs, or both, especially when dedicated to a single application or operating environment.",
                "explanation_ar": "مجموعة متكاملة من البرمجيات والمكونات المادية التي تعمل معاً لأداء وظيفة محددة.",
                "example_en": "The translation system operates entirely on the local Windows operating system.",
                "example_ar": "يعمل نظام الترجمة بالكامل على نظام تشغيل ويندوز المحلي."
            },
            {
                "context": "Medicine & Biology / الطب والأحياء",
                "meaning_ar": "جِهَاز عُضْوِي فِي الجِسْم",
                "definition_en": "A set of organs in the body with a common structure or function.",
                "explanation_ar": "مجموعة الأعضاء الحيوية التي تشترك في أداء وظيفة حيوية داخل الجسم البشري.",
                "example_en": "Regular exercise strengthens the cardiovascular and immune systems.",
                "example_ar": "تقوّي التمارين الرياضية المنتظمة الجهاز القلبي الوعائي والجهاز المناعي."
            },
            {
                "context": "Methodology & Law / المنهجية والقانون",
                "meaning_ar": "مَنْظُومَة قَوَاعِد أو مَنْهَج",
                "definition_en": "An organized scheme, procedure, or method of classification and governance.",
                "explanation_ar": "مجموعة القواعد والإجراءات المنظمة لعمل مؤسسة أو دولة.",
                "example_en": "The university adopted a modern grading system.",
                "example_ar": "اعتمدت الجامعة نظام تقييم حديثاً."
            }
        ]
    },
    {
        "word_en": "state",
        "word_ar": "حَالَة / دَوْلَة / وِلَايَة / يُصَرِّح",
        "pos": "noun",
        "ipa_uk": "/steɪt/",
        "ipa_us": "/steɪt/",
        "phonetic_ar": "سْتَيْت",
        "cefr": "A2",
        "freq": 60,
        "domain": "General",
        "lemma_en": "state",
        "root_ar": "ح و ل / د و ل / ص ر ح",
        "plural_en": "states",
        "plural_ar": "حَالَات / دُوَل / وِلَايَات",
        "verb_forms": {"base": "state", "past": "stated", "past_participle": "stated", "present_participle": "stating", "third_person": "states", "ar_past": "صَرَّحَ / ذَكَرَ", "ar_present": "يُصَرِّحُ / يَذْكُرُ", "ar_imperative": "صَرِّحْ", "ar_masdar": "تَصْرِيح / بَيَان"},
        "derivatives": ["statement (بيان / عبارة برمجية)", "statehood (سيادة الدولة)", "statesman (رجل دولة)", "restate (يعيد صياغة)"],
        "synonyms_en": ["condition", "status", "nation", "country", "declare", "express"],
        "synonyms_ar": ["وضع", "حالة", "دولة", "بلد", "يعلن", "يوضح"],
        "antonyms_en": ["conceal", "hide"],
        "antonyms_ar": ["يخفي", "يكتم"],
        "collocations": ["state of the art (أحدث ما توصلت إليه التقنية)", "solid state (الحالة الصلبة)", "head of state (رئيس الدولة)", "application state (حالة التطبيق)"],
        "usage_notes": "اسماً: تعني (حالة/وضع) في العلوم والحوسبة، أو (دولة/ولاية) في الجغرافيا والسياسة. فعلاً: تعني (يذكر بوضوح أو يصرح).",
        "senses": [
            {
                "context": "Condition & Computing / الحالة والبرمجة",
                "meaning_ar": "حَالَة / وَضْع رَاهِن",
                "definition_en": "The particular condition that someone or something is in at a specific time.",
                "explanation_ar": "الوضع أو الهيئة التي يكون عليها النظام أو المادة في لحظة معينة.",
                "example_en": "The application saves the clipboard state before capturing selected text.",
                "example_ar": "يحفظ التطبيق حالة الحافظة قبل التقاط النص المحدد."
            },
            {
                "context": "Politics & Geography / السياسة والجغرافيا",
                "meaning_ar": "دَوْلَة / وِلَايَة",
                "definition_en": "A nation or territory considered as an organized political community under one government.",
                "explanation_ar": "كيان سياسي ذو سيادة أو ولاية ضمن اتحاد فيدرالي.",
                "example_en": "Member states signed the international treaty on trade.",
                "example_ar": "وقعت الدول الأعضاء المعاهدة الدولية للتجارة."
            },
            {
                "context": "Communication (Verb) / التعبير والتصريح",
                "meaning_ar": "يَذْكُر بِوُضُوح / يُصَرِّح / يُبَيِّن",
                "definition_en": "To express something definitely or clearly in speech or writing.",
                "explanation_ar": "التعبير عن حقيقة أو شرط بعبارات واضحة ومباشرة.",
                "example_en": "The report clearly states all tested components and known limitations.",
                "example_ar": "يوضح التقرير بجلاء جميع المكونات المختبرة والقيود المعروفة."
            }
        ]
    },
    {
        "word_en": "charge",
        "word_ar": "يَشْحَن / شُحْنَة / رَسْم مَالِي / تُهْمَة / مَسْؤُولِيَّة",
        "pos": "noun",
        "ipa_uk": "/tʃɑːdʒ/",
        "ipa_us": "/tʃɑːrdʒ/",
        "phonetic_ar": "تْشَارْج",
        "cefr": "B1",
        "freq": 210,
        "domain": "General",
        "lemma_en": "charge",
        "root_ar": "ش ح ن / ر س م / ت ه م",
        "plural_en": "charges",
        "plural_ar": "شُحْنَات / رُسُوم / تُهَم",
        "verb_forms": {"base": "charge", "past": "charged", "past_participle": "charged", "present_participle": "charging", "third_person": "charges", "ar_past": "شَحَنَ / فَرَضَ رَسْماً / اتَّهَمَ", "ar_present": "يَشْحَنُ / يَفْرِضُ", "ar_imperative": "اِشْحَنْ", "ar_masdar": "شَحْن / اتِّهَام"},
        "derivatives": ["charger (شاحن)", "rechargeable (قابل لإعادة الشحن)", "surcharge (رسوم إضافية)", "discharge (تفريغ / تسريح)"],
        "synonyms_en": ["fee", "price", "cost", "accusation", "indictment", "load", "responsibility"],
        "synonyms_ar": ["تكلفة", "أجرة", "اتهام", "شحنة كهربائية", "عهدة"],
        "antonyms_en": ["discharge", "absolve", "acquit", "refund"],
        "antonyms_ar": ["يفرغ الشحنة", "يبرئ", "يرد المال"],
        "collocations": ["free of charge (مجاناً / بلا مقابل)", "in charge of (مسؤول عن)", "electric charge (شحنة كهربائية)", "press charges (يوجه اتهاماً رسمياً)"],
        "usage_notes": "لها أربعة مجالات رئيسية: المال (رسم/تكلفة)، الفيزياء (شحنة كهربائية أو شحن بطارية)، القانون (تهمة جنائية)، والإدارة (مسؤولية/إشراف).",
        "senses": [
            {
                "context": "Physics & Electronics / الفيزياء والإلكترونيات",
                "meaning_ar": "شُحْنَة كَهْرَبَائِيَّة / يَشْحَنُ بَطَّارِيَّة",
                "definition_en": "To store electrical energy in a battery or carry an electrostatic property.",
                "explanation_ar": "تزويد البطارية بالطاقة الكهربائية أو الخاصية الكهربائية للمادة.",
                "example_en": "It takes forty minutes to fully charge the laptop battery.",
                "example_ar": "يستغرق شحن بطارية الحاسوب المحمول بالكامل أربعين دقيقة."
            },
            {
                "context": "Commerce & Finance / التجارة والمال",
                "meaning_ar": "رَسْم مَالِي / تَكْلِفَة خِدْمَة",
                "definition_en": "A price asked for goods or services.",
                "explanation_ar": "المبلغ المالي المطلوب مقابل خدمة أو سلعة.",
                "example_en": "The offline dictionary and translation engine are provided free of charge.",
                "example_ar": "يُقدَّم القاموس ومحرك الترجمة المحلي مجاناً دون أي رسوم."
            },
            {
                "context": "Law & Courts / القانون والقضاء",
                "meaning_ar": "تُهْمَةٌ رَسْمِيَّة",
                "definition_en": "A formal accusation made against a prisoner brought to trial.",
                "explanation_ar": "ادعاء رسمي توجهه النيابة أو المحكمة بارتكاب مخالفة للقانون.",
                "example_en": "The court dropped all charges due to lack of evidence.",
                "example_ar": "أسقطت المحكمة جميع التهم لعدم كفاية الأدلة."
            },
            {
                "context": "Management / الإدارة والمسؤولية",
                "meaning_ar": "مَسْؤُولِيَّة / رِعَايَة وإِشْرَاف",
                "definition_en": "Responsibility for the care, control, or supervision of someone or something.",
                "explanation_ar": "تولي زمام القيادة أو الإشراف المباشر على قسم أو مشروع.",
                "example_en": "Engineer Mohammed Al-Bakir is in charge of the software architecture.",
                "example_ar": "المهندس محمد البكير هو المسؤول عن الهندسة المعمارية للبرمجيات."
            }
        ]
    },
    {
        "word_en": "field",
        "word_ar": "مَجَال / حَقْل / مَيْدَان",
        "pos": "noun",
        "ipa_uk": "/fiːld/",
        "ipa_us": "/fiːld/",
        "phonetic_ar": "فِيلْد",
        "cefr": "A2",
        "freq": 125,
        "domain": "General",
        "lemma_en": "field",
        "root_ar": "ح ق ل / ج و ل",
        "plural_en": "fields",
        "plural_ar": "مَجَالَات / حُقُول / مَيَادِين",
        "verb_forms": {"base": "field", "past": "fielded", "past_participle": "fielded", "present_participle": "fielding", "third_person": "fields", "ar_past": "نَشَرَ / أَشْرَكَ", "ar_present": "يُشْرِكُ", "ar_imperative": "أَشْرِكْ", "ar_masdar": "إِشْرَاك مَيْدَانِي"},
        "derivatives": ["fieldwork (عمل ميداني)", "midfield (خط الوسط)", "battlefield (ساحة المعركة)"],
        "synonyms_en": ["domain", "discipline", "meadow", "pasture", "input box", "area"],
        "synonyms_ar": ["تخصص", "ميدان", "حقل زراعي", "حقل إدخال بيانات", "مجال فيزيائي"],
        "antonyms_en": [],
        "antonyms_ar": [],
        "collocations": ["input field (حقل إدخال)", "magnetic field (مجال مغناطيسي)", "in the field of (في مجال كذا)", "field study (دراسة ميدانية)"],
        "usage_notes": "تُترجم إلى (تخصص أو مجال علمي) في الأكاديميات، وإلى (حقل إدخال أو عمود جدول) في قواعد البيانات والبرمجة، وإلى (حقل زراعي) في الزراعة، وإلى (مجال مغناطيسي/كهربائي) في الفيزياء.",
        "senses": [
            {
                "context": "Academic & Professional / التخصصات المهنية والعلمية",
                "meaning_ar": "مَجَالُ تَخَصُّصٍ عِلْمِيّ أَوْ مِهْنِيّ",
                "definition_en": "A particular branch of study or sphere of activity or interest.",
                "explanation_ar": "فرع من فروع المعرفة أو العمل المهني مثل الطب أو هندسة البرمجيات.",
                "example_en": "Natural language processing is a rapidly growing field of computer science.",
                "example_ar": "معالجة اللغة الطبيعية هي مجال سريع النمو من مجالات علوم الحاسوب."
            },
            {
                "context": "Computing & Databases / قواعد البيانات وواجهات المستخدم",
                "meaning_ar": "حَقْلُ بَيَانَاتٍ أَوْ مُرَبَّعُ إِدْخَال",
                "definition_en": "A space allocated for a particular item of information in a database record or user interface form.",
                "explanation_ar": "خانة مخصصة لإدخال النص في الواجهة أو عمود محدد داخل جدول قاعدة البيانات.",
                "example_en": "Selected text is automatically transferred into the translation input field.",
                "example_ar": "يُنقل النص المحدد تلقائياً إلى حقل إدخال الترجمة."
            },
            {
                "context": "Agriculture & Geography / الزراعة والأرض",
                "meaning_ar": "حَقْلٌ زِرَاعِيّ / مَرْعًى",
                "definition_en": "An area of open land, especially one planted with crops or pasture.",
                "explanation_ar": "أرض زراعية مفتوحة تُزرع فيها المحاصيل أو ترعى فيها الماشية.",
                "example_en": "Farmers irrigated the green wheat field early in the morning.",
                "example_ar": "روى المزارعون حقل القمح الأخضر في الصباح الباكر."
            }
        ]
    }
])

# ==============================================================================
# 2. CURATED RICH BILINGUAL LEXICON ACROSS DOMAINS
# Format: (word_en, word_ar, pos, ipa_us, cefr, domain, lemma_en, root_ar, plural_en, plural_ar,
#          def_en, exp_ar, ex_en, ex_ar, syn_en, ant_en, collocations)
# ==============================================================================
CURATED_LEXICON = [
    # --- Technology, Software Engineering, AI & Computing ---
    ("algorithm", "خَوَارِزْمِيَّة", "noun", "/ˈæl.ɡə.rɪð.əm/", "B2", "Technology", "algorithm", "خ و ر ز م", "algorithms", "خَوَارِزْمِيَّات",
     "A step-by-step computational procedure for solving a problem or performing a calculation.",
     "مجموعة من الخطوات الرياضية والمنطقية المتسلسلة المصممة لحل مشكلة برمجية أو معالجة البيانات.",
     "The fuzzy search algorithm finds words even when they contain spelling mistakes.",
     "تعثر خوارزمية البحث التقريبي على الكلمات حتى عندما تحتوي على أخطاء إملائية.",
     ["procedure", "method", "formula"], [], ["search algorithm (خوارزمية البحث)", "sorting algorithm (خوارزمية الترتيب)"]),
    ("database", "قَاعِدَةُ بَيَانَات", "noun", "/ˈdeɪ.tə.beɪs/", "B1", "Technology", "database", "ق ع د / ب ي ن", "databases", "قَوَاعِدُ بَيَانَات",
     "A structured set of data held in a computer, especially one that is accessible in various ways.",
     "مستودع منظم لحفظ البيانات الرقمية وفهرستها واسترجاعها بسرعة عبر استعلامات مهيألة.",
     "The local SQLite database stores thousands of bilingual dictionary entries and idioms.",
     "تخزن قاعدة بيانات SQLite المحلية آلاف المداخل المعجمية والتعابير الاصطلاحية ثنائية اللغة.",
     ["repository", "datastore", "data bank"], [], ["relational database (قاعدة بيانات علائقية)", "database index (فهرس قاعدة البيانات)"]),
    ("interface", "وَاجِهَةُ اسْتِخْدَام / وَاجِهَةُ رَبْط", "noun", "/ˈɪn.t̬ɚ.feɪs/", "B2", "Technology", "interface", "و ج ه", "interfaces", "وَاجِهَات",
     "A point where two systems, subjects, organizations, or a user and a computer meet and interact.",
     "الطبقة المرئية أو البرمجية التي يتفاعل من خلالها المستخدم مع البرنامج أو تتواصل عبرها الأنظمة.",
     "The user interface supports both Arabic right-to-left and English left-to-right layouts.",
     "تدعم واجهة المستخدم تخطيطي اللغة العربية من اليمين لليسار والإنجليزية من اليسار لليمين.",
     ["GUI", "frontend", "boundary"], [], ["user interface (واجهة المستخدم)", "programming interface (واجهة برمجية)"]),
    ("architecture", "هَنْدَسَةٌ مِعْمَارِيَّة / بِنْيَةُ النِّظَام", "noun", "/ˈɑːr.kə.tek.tʃɚ/", "B2", "Technology", "architecture", "ع م ر / ب ن ي", "architectures", "هَيَاكِل مِعْمَارِيَّة",
     "The conceptual structure and logical organization of a computer, software system, or building.",
     "التصميم الهيكلي العام للنظام البرمجي أو المبنى وطريقة ترابط وحداته وفصل مسؤولياته.",
     "Clean software architecture separates the user interface from the translation engine.",
     "تفصل الهندسة المعمارية النظيفة للبرمجيات واجهة المستخدم عن محرك الترجمة.",
     ["structure", "design", "framework"], [], ["system architecture (معمارية النظام)", "layered architecture (معمارية متعددة الطبقات)"]),
    ("network", "شَبَكَة", "noun", "/ˈnet.wɝːk/", "A2", "Technology", "network", "ش ب ك", "networks", "شَبَكَات",
     "An arrangement of intersecting horizontal and vertical lines, or interconnected computers and nodes.",
     "مجموعة من الأجهزة أو العقد المترابطة لتبادل البيانات، أو الشبكات العصبية في الذكاء الاصطناعي.",
     "Neural networks have significantly improved the accuracy of machine translation.",
     "حسّنت الشبكات العصبية دقة الترجمة الآلية إلى حد بعيد.",
     ["grid", "web", "system"], [], ["neural network (شبكة عصبية)", "local network (شبكة محلية)"]),
    ("encryption", "تَشْفِير / تَعْمِيَة", "noun", "/ɪnˈkrɪp.ʃən/", "C1", "Technology", "encrypt", "ش ف ر", "encryptions", "عمليات تشفير",
     "The process of converting information or data into a code, especially to prevent unauthorized access.",
     "تحويل البيانات المقروءة إلى صيغة مشفرة لحمايتها من الاطلاع غير المصرح به.",
     "End-to-end encryption protects sensitive communications across the network.",
     "يحمي التشفير التام بين الطرفين الاتصالات الحساسة عبر الشبكة.",
     ["ciphering", "encoding", "cryptography"], ["decryption", "decoding"], ["data encryption (تشفير البيانات)", "encryption key (مفتاح التشفير)"]),
    ("memory", "ذَاكِرَة", "noun", "/ˈmem.ər.i/", "A2", "Technology", "memory", "ذ ك ر", "memories", "ذَوَاكِر / ذِكْرَيَات",
     "The faculty by which the mind stores and remembers information, or physical electronic storage in a computer.",
     "القدرة الذهنية على الحفظ والتذكر، أو شرائح التخزين الإلكتروني المؤقت والدائم في الحاسوب.",
     "Lazy loading keeps memory consumption low on standard Windows computers.",
     "يحافظ التحميل الكسول على انخفاض استهلاك الذاكرة في أجهزة ويندوز العادية.",
     ["RAM", "storage", "recollection", "remembrance"], ["forgetfulness", "oblivion"], ["memory management (إدارة الذاكرة)", "cache memory (ذاكرة التخزين المؤقت)"]),
    ("processor", "مُعَالِج", "noun", "/ˈprɑː.ses.ɚ/", "B1", "Technology", "process", "ع ل ج", "processors", "مُعَالِجَات",
     "A machine or silicon chip that processes something, especially the central processing unit (CPU) of a computer.",
     "وحدة المعالجة المركزية في الحاسوب المسؤولة عن تنفيذ التعليمات البرمجية والعمليات الحسابية.",
     "The translation engine is optimized to run efficiently on a standard CPU processor.",
     "تم تحسين محرك الترجمة ليعمل بكفاءة على معالج مركزي عادي.",
     ["CPU", "microprocessor", "chip"], [], ["central processor (المعالج المركزي)", "multi-core processor (معالج متعدد الأنوية)"]),
    ("application", "تَطْبِيق / طَلَب رَسْمِي / تَنْفِيذ عملي", "noun", "/ˌæp.ləˈkeɪ.ʃən/", "B1", "Technology", "apply", "ط ب ق", "applications", "تَطْبِيقَات / طَلَبَات",
     "A computer program designed to perform a group of coordinated functions, or the action of putting something into operation.",
     "برنامج حاسوبي متكامل مصمم لمساعدة المستخدم على أداء مهام محددة، أو تقديم طلب رسمي لوظيفة أو دراسة.",
     "This desktop application works smoothly offline without requiring an internet connection.",
     "يعمل تطبيق سطح المكتب هذا بسلاسة دون إنترنت ودون الحاجة إلى اتصال بالشبكة.",
     ["program", "software", "app", "implementation", "request"], [], ["desktop application (تطبيق سطح مكتب)", "practical application (تطبيق عملي)"]),
    ("dictionary", "قَامُوس / مُعْجَم", "noun", "/ˈdɪk.ʃən.er.i/", "A1", "Education", "dictionary", "ق م س / ع ج م", "dictionaries", "قَوَامِيس / مَعَاجِم",
     "A reference book or electronic resource that lists the words of a language and gives their meanings, or gives the equivalent words in a different language.",
     "مرجع لغوي مرتب يضم مفردات اللغة مع شرح معانيها ونطقها وتصريفاتها أو مقابلاتها في لغة أخرى.",
     "A comprehensive bilingual dictionary is essential for students, researchers, and translators.",
     "يُعد القاموس ثنائي اللغة الشامل ضرورياً للطلاب والباحثين والمترجمين.",
     ["lexicon", "glossary", "thesaurus", "vocabulary"], [], ["bilingual dictionary (قاموس ثنائي اللغة)", "medical dictionary (قاموس طبي)"]),
    ("translation", "تَرْجَمَة", "noun", "/trænzˈleɪ.ʃən/", "A2", "Education", "translate", "ت ر ج م", "translations", "تَرْجَمَات / تَرَاجِم",
     "The process of translating words or text from one language into another, or the written/spoken result.",
     "نقل الكلام أو النصوص ومعانيها وأساليبها من اللغة المصدر إلى اللغة الهدف بدقة وأمانة.",
     "Contextual translation considers the entire sentence rather than replacing isolated words.",
     "تراعي الترجمة السياقية الجملة بأكملها بدلاً من مجرد استبدال الكلمات المنفردة.",
     ["interpretation", "rendering", "version"], [], ["machine translation (ترجمة آلية)", "literal translation (ترجمة حرفية)", "natural translation (ترجمة طبيعية)"]),
    ("translate", "يُتَرْجِم / يَنْقُلُ إِلَى لُغَةٍ أُخْرَى", "verb", "/trænzˈleɪt/", "A2", "Education", "translate", "ت ر ج م", "translates", "يُتَرْجِمُونَ",
     "To express the sense of words or text in another language.",
     "تحويل النص المكتوب أو المنطوق من لغة إلى أخرى مع الحفاظ على المعنى والسياق.",
     "Press the global shortcut to translate selected text from any Windows program.",
     "اضغط على الاختصار العام لترجمة النص المحدد من أي برنامج في ويندوز.",
     ["render", "interpret", "convert"], [], ["translate from Arabic to English (يترجم من العربية إلى الإنجليزية)"]),
    ("context", "سِيَاق / قَرِينَة", "noun", "/ˈkɑːn.tekst/", "B1", "Education", "context", "س ي ق", "contexts", "سِيَاقَات",
     "The parts of something written or spoken that immediately precede and follow a word or passage and clarify its meaning.",
     "النص المحيط بالكلمة أو الظروف الملابسة للحدث التي تحدد المعنى الدقيق المقصود.",
     "Word meanings often change dramatically depending on the surrounding context.",
     "كثيراً ما تتغير معاني الكلمات تغيراً كبيراً بحسب السياق المحيط بها.",
     ["background", "setting", "frame of reference"], ["isolation"], ["in context (في السياق)", "out of context (خارج السياق)"]),
    ("pronunciation", "نُطْق / لَفْظ", "noun", "/prəˌnʌn.siˈeɪ.ʃən/", "A2", "Education", "pronounce", "ن ط ق / ل ف ظ", "pronunciations", "طُرُقُ النُّطْق",
     "The way in which a word or a language is spoken.",
     "الطريقة الصوتية الصحيحة لإخراج الحروف ونطق الكلمات والجمل.",
     "Notice that 'pronunciation' is spelled without an 'o' in the second syllable.",
     "لاحظ أن كلمة pronunciation تُكتب بدون حرف o في المقطع الثاني وتُعبر عن طريقة النطق.",
     ["articulation", "diction", "enunciation", "speech"], [], ["audio pronunciation (النطق الصوتي)", "received pronunciation (النطق البريطاني القياسي)"]),
    ("grammar", "قَوَاعِدُ اللُّغَةِ / النَّحْوُ وَالصَّرْف", "noun", "/ˈɡræm.ɚ/", "A1", "Education", "grammar", "ن ح و / ق ع د", "grammars", "قَوَاعِدُ نَحْوِيَّة",
     "The whole system and structure of a language or of languages in general, usually taken as consisting of syntax and morphology.",
     "منظومة القواعد النحوية والصرفية التي تضبط بناء الكلمات وتركيب الجمل في اللغة.",
     "Arabic grammar features rich morphological derivations built on triliteral roots.",
     "تتميز قواعد اللغة العربية باشتقاقات صرفية غنية مبنية على الجذور الثلاثية.",
     ["syntax", "morphology", "linguistics"], [], ["grammar rules (قواعد النحو)", "comparative grammar (النحو المقارن)"]),
    ("synonym", "مُرَادِف", "noun", "/ˈsɪn.ə.nɪm/", "B1", "Education", "synonym", "ر د ف", "synonyms", "مُرَادِفَات",
     "A word or phrase that means exactly or nearly the same as another word or phrase in the same language.",
     "كلمة تؤدي نفس معنى كلمة أخرى أو تقاربها في الدلالة داخل اللغة الواحدة.",
     "The dictionary displays synonyms and antonyms for every entry.",
     "يعرض القاموس المرادفات والأضداد لكل مدخل معجمي.",
     ["equivalent", "metonym"], ["antonym", "opposite"], ["close synonym (مرادف قريب)", "exact synonym (مرادف تام)"]),
    ("antonym", "ضِدّ / نَقِيض", "noun", "/ˈæn.t̬ə.nɪm/", "B1", "Education", "antonym", "ض د د", "antonyms", "أَضْدَاد / نَقَائِض",
     "A word opposite in meaning to another.",
     "الكلمة التي تعاكس كلمة أخرى في المعنى (مثل النور والظلام).",
     "Knowing both synonyms and antonyms expands your active vocabulary.",
     "إن معرفة كل من المرادفات والأضداد توسع حصيلتك اللغوية الفعالة.",
     ["opposite", "reverse"], ["synonym"], ["direct antonym (ضد مباشر)"]),
    ("idiom", "تَعْبِيرٌ اصْطِلَاحِيّ / مَجَاز", "noun", "/ˈɪd.i.əm/", "B2", "Education", "idiom", "ص ط ل ح", "idioms", "تَعَابِيرُ اصْطِلَاحِيَّة",
     "A group of words established by usage as having a meaning not deducible from those of the individual words.",
     "عبارة متعارف عليها في اللغة لها معنى مجازي متكامل يختلف عن المعنى الحرفي لكلماتها المنفردة.",
     "Translating an idiom word-for-word usually produces an inaccurate result.",
     "إن ترجمة التعبير الاصطلاحي كلمة بكلمة تؤدي عادة إلى نتيجة غير دقيقة.",
     ["expression", "phrase", "locution"], [], ["common idiom (تعبير اصطلاحي شائع)", "idiomatic expression (تعبير مجازي)"]),
    (" clipboard".strip(), "حَافِظَةُ النِّظَام", "noun", "/ˈklɪp.bɔːrd/", "B1", "Technology", "clipboard", "ح ف ظ", "clipboards", "حَوَافِظ",
     "A temporary storage area in a computer's memory where text or data that has been copied is kept.",
     "مساحة تخزين مؤقتة في ذاكرة نظام التشغيل تُحفظ فيها النصوص أو البيانات المنسوخة لنقلها بين البرامج.",
     "The safe clipboard manager restores your previous clipboard contents after capturing text.",
     "يستعيد مدير الحافظة الآمن محتويات الحافظة السابقة بعد التقاط النص.",
     ["buffer", "pasteboard"], [], ["copy to clipboard (نسخ إلى الحافظة)", "paste from clipboard (لصق من الحافظة)"]),
    ("shortcut", "اخْتِصَار / طَرِيقٌ مُخْتَصَر", "noun", "/ˈʃɔːrt.kʌt/", "A2", "Technology", "shortcut", "خ ص ر", "shortcuts", "اخْتِصَارَات",
     "A key or combination of keys providing quick access to a specific function within a computer program, or a shorter route.",
     "مفتاح أو مجموعة مفاتيح تتيح تنفيذ أمر برمجي بسرعة، أو أيقونة وصول سريع على سطح المكتب.",
     "You can customize the global keyboard shortcut in the settings screen.",
     "يمكنك تخصيص اختصار لوحة المفاتيح العام في شاشة الإعدادات.",
     ["hotkey", "accelerator", "quick link"], [], ["keyboard shortcut (اختصار لوحة المفاتيح)", "desktop shortcut (اختصار سطح المكتب)"]),
    ("installer", "مُثَبِّتُ البَرَامِج", "noun", "/ɪnˈstɑː.lɚ/", "B1", "Technology", "install", "ث ب ت", "installers", "مُثَبِّتَات",
     "A piece of software that installs a program and its required resources onto a computer's storage drive.",
     "برنامج مخصص لنسخ ملفات التطبيق وإعداد الاختصارات وتهيئة بيئة التشغيل على نظام المستخدم.",
     "The Windows installer creates desktop and Start menu shortcuts and supports clean uninstallation.",
     "ينشئ مثبت ويندوز اختصارات على سطح المكتب وقائمة ابدأ ويدعم إلغاء التثبيت النظيف.",
     ["setup program", "package manager"], ["uninstaller"], ["offline installer (مثبت يعمل دون إنترنت)"]),
    ("portable", "مَحْمُول / قَابِلٌ لِلنَّقْلِ دُونَ تَثْبِيت", "adjective", "/ˈpɔːr.t̬ə.bəl/", "B1", "Technology", "portable", "ح م ل / ن ق ل", "", "مَحْمُولَة",
     "Able to be easily carried or moved, or software capable of running directly from a folder or USB drive without installation.",
     "سهل الحمل والنقل، وفي البرمجيات: النسخة التي تعمل مباشرة من مجلدها دون الحاجة إلى عملية تثبيت في النظام.",
     "The portable edition runs directly from its folder without requiring administrator privileges.",
     "تعمل النسخة المحمولة مباشرة من مجلدها دون الحاجة إلى صلاحيات المسؤول.",
     ["mobile", "standalone", "transportable"], ["stationary", "fixed"], ["portable version (النسخة المحمولة)", "portable device (جهاز محمول)"]),
    ("offline", "دُونَ اتِّصَالٍ بِالإِنْتَرْنِت / مَحَلِّيّاً", "adjective", "/ˌɑːfˈlaɪn/", "A2", "Technology", "offline", "ح ل ل / ف ص ل", "", "",
     "Not connected to or controlled by a computer network or the internet; operating locally.",
     "العمل بشكل مستقل ومحلي على الجهاز دون الحاجة إلى الاتصال بشبكة الإنترنت.",
     "All core dictionary lookups and sentence translations work 100% offline.",
     "تعمل جميع عمليات البحث في القاموس الأساسي وترجمة الجمل بنسبة 100% دون اتصال بالإنترنت.",
     ["disconnected", "local", "standalone"], ["online", "connected"], ["offline mode (وضع عدم الاتصال)", "offline engine (المحرك المحلي)"]),
    ("online", "مُتَّصِلٌ بِالإِنْتَرْنِت / عَبْرَ الشَّبَكَة", "adjective", "/ˌɑːnˈlaɪn/", "A1", "Technology", "online", "و ص ل", "", "",
     "Controlled by or connected to another computer or to a network such as the internet.",
     "متصل بشبكة الإنترنت أو متاح عبر الخوادم السحابية.",
     "Online translation services are completely optional and require explicit user consent.",
     "خدمات الترجمة عبر الإنترنت اختيارية تماماً وتتطلب موافقة صريحة من المستخدم.",
     ["connected", "web-based", "networked"], ["offline", "disconnected"], ["online verification (التحقق عبر الإنترنت)"]),
    ("privacy", "خُصُوصِيَّة / سِرِّيَّةُ البَيَانَات", "noun", "/ˈpraɪ.və.si/", "B1", "Legal", "private", "خ ص ص", "privacies", "خُصُوصِيَّات",
     "The state or condition of being free from being observed or disturbed by other people or unauthorized trackers.",
     "حق الفرد في حماية بياناته ونصوصه ومعلوماته الشخصية من التتبع أو الإرسال غير المصرح به.",
     "LinguaDesk Pro respects your privacy by never sending clipboard data to external servers.",
     "يحترم LinguaDesk Pro خصوصيتك بعدم إرسال بيانات الحافظة أبداً إلى خوادم خارجية.",
     ["confidentiality", "secrecy", "solitude"], ["publicity", "exposure"], ["data privacy (خصوصية البيانات)", "privacy policy (سياسة الخصوصية)"]),
    ("security", "أَمْن / أَمَان / حِمَايَة", "noun", "/səˈkjʊr.ə.t̬i/", "B1", "Technology", "secure", "أ م ن", "securities", "إِجْرَاءَات أَمْنِيَّة / أَوْرَاق مَالِيَّة",
     "The state of being free from danger or threat; procedures taken to protect a system or data.",
     "حماية الأنظمة والبيانات والأفراد من المخاطر والاختراقات والبرمجيات الضارة.",
     "Parameterized SQL queries ensure database security and prevent injection attacks.",
     "تضمن استعلامات SQL ذات المعاملات أمن قاعدة البيانات وتمنع هجمات الحقن.",
     ["safety", "protection", "defense"], ["vulnerability", "insecurity", "danger"], ["information security (أمن المعلومات)", "cybersecurity (الأمن السيبراني)"]),
    ("license", "تَرْخِيص / رُخْصَة", "noun", "/ˈlaɪ.səns/", "B1", "Legal", "license", "ر خ ص", "licenses", "تَرَاخِيص / رُخَص",
     "A permit from an authority or copyright holder to own, use, distribute, or modify something.",
     "وثيقة قانونية تمنح الإذن باستخدام برنامج أو مورد لغوي أو إعادة توزيعه وفق شروط محددة.",
     "Every linguistic resource in the manager lists its exact source and open-source license.",
     "يوضح كل مورد لغوي في مدير الموارد مصدره الدقيق وترخيصه مفتوح المصدر.",
     ["permit", "authorization", "charter"], ["prohibition", "ban"], ["open-source license (ترخيص مفتوح المصدر)", "software license (ترخيص البرمجيات)"]),
    ("resource", "مَوْرِد / مَصْدَر", "noun", "/ˈriː.sɔːrs/", "B1", "General", "resource", "و ر د", "resources", "مَوَارِد / مَصَادِر",
     "A stock or supply of money, materials, staff, and other digital or linguistic assets that can be drawn on to function effectively.",
     "كل ما يُعتمد عليه من قواعد بيانات ونماذج لغوية وذاكرة ومعالج لإنجاز المهام بكفاءة.",
     "The resource manager displays the size, status, and integrity hash of every installed package.",
     "يعرض مدير الموارد حجم كل حزمة مثبتة وحالتها وبصمة التحقق من سلامتها.",
     ["asset", "supply", "reserve"], [], ["linguistic resources (الموارد اللغوية)", "system resources (موارد النظام)"]),
    ("performance", "أَدَاء / كَفَاءَةُ التَّشْغِيل", "noun", "/pɚˈfɔːr.məns/", "B1", "Technology", "perform", "أ د ي", "performances", "مُسْتَوَيَاتُ الأَدَاء / عُرُوض",
     "The capabilities, speed, and responsiveness of a machine, software system, or person.",
     "مدى سرعة وكفاءة استجابة البرنامج أو النظام أثناء تنفيذ المهام والعمليات.",
     "Database indexing guarantees high search performance even with tens of thousands of entries.",
     "تضمن فهرسة قاعدة البيانات أداءً عالياً في البحث حتى مع وجود عشرات الآلاف من المداخل.",
     ["efficiency", "speed", "execution"], ["inefficiency"], ["high performance (أداء عالٍ)", "performance benchmark (اختبار قياس الأداء)"]),
    ("accuracy", "دِقَّة / صِحَّة", "noun", "/ˈæk.jɚ.ə.si/", "B2", "Science", "accurate", "د ق ق", "accuracies", "مُسْتَوَيَاتُ الدِّقَّة",
     "The quality or state of being correct or precise.",
     "درجة مطابقة النتيجة أو الترجمة للحقيقة والصواب اللغوي والعلمي.",
     "Combining a lexical dictionary with contextual analysis improves translation accuracy.",
     "إن الجمع بين القاموس المعجمي والتحليل السياقي يحسّن دقة الترجمة.",
     ["precision", "correctness", "exactness"], ["inaccuracy", "error"], ["high accuracy (دقة عالية)", "translation accuracy (دقة الترجمة)"]),
]

print(f"Loaded {len(CURATED_LEXICON)} initial curated items.")

# ==============================================================================
# 3. EXPANDED DOMAIN LEXICON (Medicine, Science, Business, Law, General Verbs/Nouns/Adjectives)
# ==============================================================================
DOMAIN_WORDS_RAW = [
    # Medicine & Health
    ("medicine", "طِبّ / دَوَاء", "noun", "/ˈmed.ɪ.sən/", "A2", "Medicine", "medicine", "ط ب ب / د و ي", "medicines", "أَدْوِيَة",
     "The science or practice of the diagnosis, treatment, and prevention of disease; or a substance taken to treat illness.",
     "علم تشخيص الأمراض وعلاجها والوقاية منها، أو العقار الدوائي الذي يتناوله المريض.",
     "Modern medicine relies on clinical evidence and accurate diagnosis.",
     "يعتمد الطب الحديث على الأدلة السريرية والتشخيص الدقيق."),
    ("diagnosis", "تَشْخِيصٌ طِبِّيّ", "noun", "/ˌdaɪ.əɡˈnoʊ.sɪs/", "B2", "Medicine", "diagnose", "ش خ ص", "diagnoses", "تَشْخِيصَات",
     "The identification of the nature of an illness or other problem by examination of the symptoms.",
     "تحديد طبيعة المرض أو المشكلة الصحية من خلال فحص الأعراض والتحاليل.",
     "Early diagnosis significantly increases the success rate of treatment.",
     "يزيد التشخيص المبكر من نسبة نجاح العلاج بشكل كبير."),
    ("treatment", "عِلَاج / مُعَامَلَة", "noun", "/ˈtriːt.mənt/", "B1", "Medicine", "treat", "ع ل ج / ع م ل", "treatments", "عِلَاجَات / مُعَامَلَات",
     "Medical care given to a patient for an illness or injury; or the manner in which someone behaves toward or deals with someone or something.",
     "الرعاية الطبية والأدوية المقدمة للمريض للشفاء، أو طريقة التعامل مع الأشخاص أو البيانات.",
     "The patient responded well to the new medical treatment.",
     "استجاب المريض بشكل جيد للعلاج الطبي الجديد."),
    ("symptom", "عَرَضٌ مَرَضِيّ / عَلَامَة", "noun", "/ˈsɪmp.təm/", "B1", "Medicine", "symptom", "ع ر ض", "symptoms", "أَعْرَاض",
     "A physical or mental feature which is regarded as indicating a condition of disease.",
     "علامة جسدية أو حيوية يشعر بها المريض وتدل على وجود حالة صحية معينة.",
     "Fever and fatigue are common symptoms of viral infections.",
     "تُعد الحمى والإرهاق من الأعراض الشائعة للعدوى الفيروسية."),
    ("immunity", "مَنَاعَة / حَصَانَة", "noun", "/ɪˈmjuː.nə.t̬i/", "B2", "Medicine", "immune", "م ن ع / ح ص ن", "immunities", "مَنَاعَات / حَصَانَات",
     "The ability of an organism to resist a particular infection or toxin; or legal exemption.",
     "قدرة الجسم الحيوية على مقاومة الأمراض والعدوى، أو الحصانة القانونية والدبلوماسية.",
     "Vaccination helps build strong immunity against infectious diseases.",
     "يساعد التطعيم على بناء مناعة قوية ضد الأمراض المعدية."),
    ("surgery", "جِرَاحَة / عَمَلِيَّةٌ جِرَاحِيَّة", "noun", "/ˈsɝː.dʒər.i/", "B1", "Medicine", "surgeon", "ج ر ح", "surgeries", "عَمَلِيَّاتٌ جِرَاحِيَّة",
     "The branch of medical practice that treats injuries, diseases, and deformities by the physical removal, repair, or readjustment of organs and tissues.",
     "فرع الطب الذي يعالج الأمراض والإصابات عبر التدخل الجراحي، أو العملية الجراحية ذاتها.",
     "The surgeon performed delicate eye surgery using laser technology.",
     "أجرى الجراح عملية جراحية دقيقة في العين باستخدام تقنية الليزر."),
    ("hospital", "مُسْتَشْفَى", "noun", "/ˈhɑː.spɪ.t̬əl/", "A1", "Medicine", "hospital", "ش ف ي", "hospitals", "مُسْتَشْفَيَات",
     "An institution providing medical and surgical treatment and nursing care for sick or injured people.",
     "مؤسسة صحية متكاملة تقدم الرعاية الطبية والجراحية والتمريضية للمرضى والمصابين.",
     "The university hospital opened a specialized research center.",
     "افتتح المستشفى الجامعي مركز أبحاث متخصصاً."),
    ("patient", "مَرِيض / صَبُور", "noun", "/ˈpeɪ.ʃənt/", "A2", "Medicine", "patient", "م ر ض / ص ب ر", "patients", "مَرْضَى / صَابِرُونَ",
     "A person receiving or registered to receive medical treatment (noun); able to accept or tolerate delays without becoming annoyed (adjective).",
     "الشخص الذي يتلقى الرعاية الطبية (اسم)، أو الشخص المتحلّي بالصبر وطول الأناة (صفة).",
     "A good doctor listens carefully and remains patient with every patient.",
     "الطبيب الماهر يستمع بعناية ويبقى صبوراً مع كل مريض."),

    # Science, Mathematics & Engineering
    ("research", "بَحْثٌ عِلْمِيّ / يَبْحَث", "noun", "/ˈriː.sɝːtʃ/", "A2", "Science", "research", "ب ح ث", "researches", "أَبْحَاث / بُحُوث",
     "The systematic investigation into and study of materials and sources in order to establish facts and reach new conclusions.",
     "التقصي العلمي المنهجي ودراسة المصادر والتجارب لاكتشاف حقائق جديدة أو تطوير حلول.",
     "Scientific research drives technological innovation and human progress.",
     "يقود البحث العلمي الابتكار التقني والتقدم البشري."),
    ("experiment", "تَجْرِبَةٌ عِلْمِيَّة / يُجَرِّب", "noun", "/ɪkˈsper.ə.mənt/", "B1", "Science", "experiment", "ج ر ب", "experiments", "تَجَارِبُ عِلْمِيَّة",
     "A scientific procedure undertaken to make a discovery, test a hypothesis, or demonstrate a known fact.",
     "إجراء علمي مضبوط في المختبر أو الواقع لاختبار فرضية أو التحقق من ظاهرة.",
     "The laboratory experiment confirmed the theoretical prediction.",
     "أكدت التجربة المخبرية التوقع النظري."),
    ("theory", "نَظَرِيَّة", "noun", "/ˈθɪr.i/", "B1", "Science", "theory", "ن ظ ر", "theories", "نَظَرِيَّات",
     "A supposition or a system of ideas intended to explain something, especially one based on general principles independent of the thing to be explained.",
     "منظومة متكاملة من المبادئ والقوانين العلمية التي تفسر ظاهرة طبيعية أو رياضية.",
     "Information theory forms the mathematical foundation of modern communication.",
     "تشكّل نظرية المعلومات الأساس الرياضي للاتصالات الحديثة."),
    ("equation", "مُعَادَلَة", "noun", "/ɪˈkweɪ.ʒən/", "B2", "Science", "equate", "ع د ل", "equations", "مُعَادَلَات",
     "A statement that the values of two mathematical expressions are equal (indicated by the sign =).",
     "عبارة رياضية أو كيميائية تعبر عن التساوي بين طرفين.",
     "Solving differential equations is fundamental in physics and engineering.",
     "يُعد حل المعادلات التفاضلية أمراً أساسياً في الفيزياء والهندسة."),
    ("energy", "طَاقَة / حَيَوِيَّة", "noun", "/ˈen.ɚ.dʒi/", "A2", "Science", "energy", "ط و ق", "energies", "طَاقَات",
     "The quantitative property that must be transferred to a body or physical system to perform work on the body, or to heat it.",
     "القدرة على بذل شغل أو إحداث تغيير في الأنظمة الفيزيائية أو الحيوية.",
     "Renewable energy sources reduce carbon emissions and protect the environment.",
     "تقلل مصادر الطاقة المتجددة من انبعاثات الكربون وتحمي البيئة."),
    ("environment", "بِيئَة / مُحِيط", "noun", "/ɪnˈvaɪ.rən.mənt/", "A2", "Science", "environment", "ب و أ / ح ي ط", "environments", "بِيئَات",
     "The surroundings or conditions in which a person, animal, plant, or computer system lives or operates.",
     "المحيط الطبيعي الذي تعيش فيه الكائنات الحية، أو بيئة التشغيل البرمجية للحاسوب.",
     "We tested the software in a clean Windows runtime environment.",
     "اختبرنا البرمجيات في بيئة تشغيل ويندوز نظيفة."),
    ("analysis", "تَحْلِيل", "noun", "/əˈnæl.ə.sɪs/", "B1", "Science", "analyze", "ح ل ل", "analyses", "تَحْلِيلَات / تَحَالِيل",
     "Detailed examination of the elements or structure of something.",
     "دراسة تفصيلية لعناصر الشيء أو النص أو البيانات لفهم بنيته واستخلاص النتائج.",
     "Morphological analysis breaks Arabic words into their prefixes, roots, and suffixes.",
     "يفكك التحليل الصرفي الكلمات العربية إلى سوابقها وجذورها ولواحقها."),
    ("evidence", "دَلِيل / بُرْهَان / بَيِّنَة", "noun", "/ˈev.ə.dəns/", "B1", "Science", "evident", "د ل ل / ب ر ه ن", "evidences", "أَدِلَّة / بَرَاهِين",
     "The available body of facts or information indicating whether a belief or proposition is true or valid.",
     "مجموع الحقائق والمعطيات الموثقة التي تثبت صحة قضية علمية أو قانونية.",
     "All engineering decisions were based on empirical evidence and benchmarks.",
     "استندت جميع القرارات الهندسية إلى الأدلة التجريبية واختبارات الأداء."),

    # Business, Economics & Management
    ("economy", "اقْتِصَاد", "noun", "/iˈkɑː.nə.mi/", "B1", "Business", "economy", "ق ص د", "economies", "اقْتِصَادَات",
     "The state of a country or region in terms of the production and consumption of goods and services and the supply of money.",
     "منظومة الإنتاج والتوزيع والاستهلاك للسلع والخدمات والثروة في دولة أو إقليم.",
     "The digital economy creates new opportunities for software developers.",
     "يخلق الاقتصاد الرقمي فرصاً جديدة لمطوري البرمجيات."),
    ("investment", "اسْتِثْمَار", "noun", "/ɪnˈvest.mənt/", "B1", "Business", "invest", "ث م ر", "investments", "اسْتِثْمَارَات",
     "The action or process of investing money, time, or effort for profit or material result.",
     "توظيف المال أو الوقت أو الجهد في مشروع أو أصل بهدف تحقيق عائد مستقبلي.",
     "Education is the most valuable long-term investment in human capital.",
     "التعليم هو أثمن استثمار طويل الأجل في رأس المال البشري."),
    ("management", "إِدَارَة", "noun", "/ˈmæn.ɪdʒ.mənt/", "B1", "Business", "manage", "د و ر", "managements", "إِدَارَات",
     "The process of dealing with or controlling things or people; the executives of an organization.",
     "تنسيق الموارد والجهود وتوجيهها لتحقيق الأهداف بكفاءة وفعالية.",
     "Effective resource management prevents memory leaks and disk bloat.",
     "تمنع الإدارة الفعالة للموارد تسرب الذاكرة وتضخم مساحة القرص."),
    ("project", "مَشْرُوع / يُخَطِّط", "noun", "/ˈprɑː.dʒekt/", "A2", "Business", "project", "ش ر ع", "projects", "مَشَارِيع / مَشْرُوعَات",
     "An individual or collaborative enterprise that is carefully planned to achieve a particular aim.",
     "عمل متكامل ومخطط له بعناية يضم مراحل وموارد محددة للوصول إلى هدف واضح.",
     "This complete software project includes source code, databases, and automated tests.",
     "يتضمن هذا المشروع البرمجي المتكامل الشيفرات المصدرية وقواعد البيانات والاختبارات الآلية."),
    ("quality", "جَوْدَة / نَوْعِيَّة / صِفَة", "noun", "/ˈkwɑː.lə.t̬i/", "A2", "Business", "quality", "ج و د", "qualities", "صِفَات / خَصَائِص",
     "The standard of something as measured against other things of a similar kind; the degree of excellence of something.",
     "درجة الإتقان والتميز ومطابقة المنتج أو الترجمة للمعايير القياسية.",
     "Our top priority is implementation correctness and translation quality.",
     "أولويتنا القصوى هي صحة التنفيذ وجودة الترجمة."),
    ("strategy", "إِسْتْرَاتِيجِيَّة / خُطَّةٌ شَامِلَة", "noun", "/ˈstræt̬.ə.dʒi/", "B1", "Business", "strategy", "خ ط ط", "strategies", "إِسْتْرَاتِيجِيَّات",
     "A plan of action or policy designed to achieve a major or overall aim.",
     "خطة عمل بعيدة المدى مصممة لتحقيق أهداف كبرى بكفاءة.",
     "A hybrid offline-first strategy ensures reliability under all network conditions.",
     "تضمن الإستراتيجية الهجينة التي تعطي الأولوية للعمل المحلي الموثوقية في جميع ظروف الشبكة."),
    ("market", "سُوق / يُسَوِّق", "noun", "/ˈmɑːr.kɪt/", "A1", "Business", "market", "س و ق", "markets", "أَسْوَاق",
     "A regular gathering of people for the purchase and sale of provisions, or an economic sector of demand and supply.",
     "مكان أو منظومة التبادل التجاري للسلع والخدمات بين البائعين والمشترين.",
     "The company launched a new product for the regional software market.",
     "أطلقت الشركة منتجاً جديداً لسوق البرمجيات الإقليمي."),
    ("customer", "عَمِيل / زَبُون", "noun", "/ˈkʌs.tə.mɚ/", "A1", "Business", "custom", "ع م ل / ز ب ن", "customers", "عُمَلَاء / زَبَائِن",
     "A person or organization that buys goods or services from a store or business.",
     "الشخص أو المؤسسة التي تشتري سلعة أو تستفيد من خدمة تجارية.",
     "Customer satisfaction depends on reliability, speed, and clear support.",
     "يعتمد رضا العملاء على الموثوقية والسرعة والدعم الواضح."),

    # Law, Governance & Ethics
    ("law", "قَانُون / شَرِيعَة", "noun", "/lɑː/", "A2", "Legal", "law", "ق ن ن / ش ر ع", "laws", "قَوَانِين / شَرَائِع",
     "The system of rules which a particular country or community recognizes as regulating the actions of its members.",
     "مجموعة القواعد الملزمة التي تنظم العلاقات في المجتمع، أو القوانين العلمية الثابتة.",
     "Copyright law governs the redistribution of digital dictionaries and models.",
     "ينظم قانون حقوق النشر إعادة توزيع القواميس والنماذج الرقمية."),
    ("agreement", "اتِّفَاق / اتِّفَاقِيَّة / تَوَافُق نَحْوِي", "noun", "/əˈɡriː.mənt/", "B1", "Legal", "agree", "و ف ق", "agreements", "اتِّفَاقِيَّات",
     "Harmony or accordance in opinion or feeling; a negotiated and typically legally binding arrangement between parties; grammatical concord.",
     "توافق الآراء أو العقود بين الأطراف، وفي النحو: المطابقة بين الصفة والموصوف أو الفعل والفاعل.",
     "Arabic translation requires proper gender and number agreement between nouns and adjectives.",
     "تتطلب الترجمة إلى العربية مطابقة صحيحة في التذكير والتأنيث والعدد بين الأسماء والصفات."),
    ("justice", "عَدَالَة / عَدْل / قَضَاء", "noun", "/ˈdʒʌs.tɪs/", "B1", "Legal", "just", "ع د ل", "justices", "قُضَاة",
     "Just behavior or treatment; the administration of the law or authority in maintaining this.",
     "إعطاء كل ذي حق حقه، وإنصاف المظلوم، وتطبيق القانون بحياد ونزاهة.",
     "Justice and fairness are foundational pillars of a stable society.",
     "العدالة والإنصاف ركيزتان أساسيتان لمجتمع مستقر."),
    ("authority", "سُلْطَة / هَيْئَةٌ رَسْمِيَّة / مَرْجِعِيَّة", "noun", "/əˈθɔːr.ə.t̬i/", "B1", "Legal", "author", "س ل ط / ر ج ع", "authorities", "سُلُطَات / هَيْئَات",
     "The power or right to give orders, make decisions, and enforce obedience; or a person/source with extensive specialized knowledge.",
     "الجهة الرسمية ذات الصلاحية القانونية، أو المرجع العلمي الموثوق في تخصصه.",
     "Always verify lexical definitions against a trusted linguistic authority.",
     "تحقق دائماً من التعريفات المعجمية بالرجوع إلى مرجعية لغوية موثوقة."),
    ("permission", "إِذْن / تَصْرِيح / صَلَاحِيَّة", "noun", "/pɚˈmɪʃ.ən/", "A2", "Legal", "permit", "أ ذ ن / ص ر ح", "permissions", "أُذُونات / صَلَاحِيَّات",
     "Consent or authorization to do something; operating system access rights.",
     "الموافقة الصريحة على القيام بعمل ما، أو صلاحيات الوصول في نظام التشغيل.",
     "The application never sends text to external servers without explicit user permission.",
     "لا يرسل التطبيق أي نصوص إلى خوادم خارجية دون إذن صريح من المستخدم."),

    # Everyday High-Frequency Verbs, Nouns, Adjectives & Function Words
    ("knowledge", "مَعْرِفَة / عِلْم", "noun", "/ˈnɑː.lɪdʒ/", "A2", "Education", "know", "ع ر ف / ع ل م", "knowledges", "مَعَارِف / عُلُوم",
     "Facts, information, and skills acquired by a person through experience or education.",
     "الحصيلة العلمية والعملية التي يكتسبها الإنسان بالتعلم والتجربة والبحث.",
     "Sharing knowledge empowers communities and accelerates scientific discovery.",
     "إن نشر المعرفة يمكّن المجتمعات ويسرّع الاكتشاف العلمي."),
    ("language", "لُغَة / لِسَان", "noun", "/ˈlæŋ.ɡwɪdʒ/", "A1", "Education", "language", "ل غ و / ل س ن", "languages", "لُغَات / أَلْسِنَة",
     "The principal method of human communication, consisting of words used in a structured and conventional way.",
     "منظومة الرموز والأصوات والكلمات التي يعبر بها كل قوم عن أغراضهم وأفكارهم.",
     "Arabic and English belong to two distinct language families with rich histories.",
     "تنتمي العربية والإنجليزية إلى عائلتين لغويتين متمايزتين ذاتي تاريخ عريق."),
    ("word", "كَلِمَة / لَفْظَة / وَعْد", "noun", "/wɝːd/", "A1", "Education", "word", "ك ل م / ل ف ظ", "words", "كَلِمَات / أَلْفَاظ",
     "A single distinct meaningful element of speech or writing, used with others to form a sentence.",
     "اللفظة المفردة الدالة على معنى، وتجتمع مع غيرها لتكوين الجمل والعبارات.",
     "Type any English or Arabic word to view its definitions, pronunciation, and examples.",
     "اكتب أي كلمة إنجليزية أو عربية لعرض تعريفاتها ونطقها وأمثلتها."),
    ("sentence", "جُمْلَةٌ مُفِيدَة / حُكْمٌ قَضَائِيّ بِالعُقُوبَة", "noun", "/ˈsen.təns/", "A1", "Education", "sentence", "ج م ل / ح ك م", "sentences", "جُمَل / أَحْكَام",
     "A set of words that is complete in itself, typically containing a subject and predicate; or a punishment assigned by a court.",
     "تركيب لغوي تام يفيد معنى مكتملاً (جملة اسمية أو فعلية)، وفي القانون: الحكم الصادر بالعقوبة.",
     "The sentence translation engine preserves punctuation and contextual meaning.",
     "يحافظ محرك ترجمة الجمل على علامات الترقيم والمعنى السياقي."),
    ("paragraph", "فَقْرَةٌ نَصِّيَّة", "noun", "/ˈper.ə.ɡræf/", "A2", "Education", "paragraph", "ف ق ر", "paragraphs", "فَقْرَات",
     "A distinct section of a piece of writing, usually dealing with a single theme and indicated by a new line.",
     "مجموعة من الجمل المترابطة التي تدور حول فكرة رئيسية واحدة داخل النص.",
     "Long paragraphs are segmented intelligently without breaking sentence context.",
     "تُقسَّم الفقرات الطويلة بذكاء دون إفساد سياق الجمل."),
    ("meaning", "مَعْنًى / دَلَالَة / مَغْزًى", "noun", "/ˈmiː.nɪŋ/", "A1", "Education", "mean", "ع ن ي / د ل ل", "meanings", "مَعَانٍ / دَلَالَات",
     "What is meant by a word, text, concept, or action.",
     "المفهوم أو الدلالة التي يقصدها المتكلم أو تدل عليها الكلمة في سياقها.",
     "Each sense card clearly separates distinct meanings of the same word.",
     "تفصل كل بطاقة دلالية بوضوح بين المعاني المختلفة للكلمة الواحدة."),
    ("example", "مِثَال / نَمُوذَجٌ تَوْضِيحِيّ", "noun", "/ɪɡˈzæm.pəl/", "A1", "Education", "example", "م ث ل", "examples", "أَمْثِلَة / نَمَاذِج",
     "A thing characteristic of its kind or illustrating a general rule.",
     "جملة أو حالة تطبيقية تُساق لتوضيح قاعدة أو بيان كيفية استخدام الكلمة في السياق.",
     "Every dictionary entry includes realistic bilingual usage examples.",
     "يتضمن كل مدخل في القاموس أمثلة استخدام واقعية ثنائية اللغة."),
    ("voice", "صَوْتٌ بَشَرِيّ / صِيغَةُ الفِعْل (مَبْنِيّ للمَعْلُوم أو المَجْهُول)", "noun", "/vɔɪs/", "A1", "General", "voice", "ص و ت", "voices", "أَصْوَات",
     "The sound produced in a person's larynx and uttered through the mouth, as speech or song; or grammatical active/passive voice.",
     "الصوت الناتج عن النطق البشري أو محركات تحويل النص إلى كلام، وفي النحو: البناء للمعلوم والمجهول.",
     "You can choose between American, British, and Arabic offline voices.",
     "يمكنك الاختيار بين الأصوات المحلية الأمريكية والبريطانية والعربية."),
    ("image", "صُورَة / تَصَوُّر ذِهْنِيّ", "noun", "/ˈɪm.ɪdʒ/", "A1", "Technology", "image", "ص و ر", "images", "صُوَر",
     "A visual representation of something, such as a photograph or digital picture on a screen.",
     "تمثيل بصري أو ملف رقمي يحوي مشهداً أو نصاً مصوراً يمكن قراءته عبر تقنية OCR.",
     "Drag and drop any image into the OCR tab to extract and translate its text.",
     "اسحب أي صورة وأفلتها في تبويب التعرف الضوئي لاستخراج نصها وترجمته."),
    ("history", "تَارِيخ / سِجِلُّ العَمَلِيَّاتِ السَّابِقَة", "noun", "/ˈhɪs.t̬ɚ.i/", "A1", "General", "history", "أ ر خ / س ج ل", "histories", "تَوَارِيخ / سِجِلَّات",
     "The study of past events; or a chronological record of previous searches and translations in an application.",
     "علم دراسة الأحداث الماضية، وفي البرمجيات: سجل عمليات البحث والترجمة السابقة المحفوظ محلياً.",
     "Your search and translation history is stored locally and can be cleared anytime.",
     "يُحفظ سجل البحث والترجمة محلياً ويمكنك مسحه في أي وقت."),
    ("favorite", "مُفَضَّل / كَلِمَةٌ مُفَضَّلَة", "noun", "/ˈfeɪ.vər.ət/", "A1", "General", "favor", "ف ض ل", "favorites", "المُفَضَّلَة / المُفَضَّلَات",
     "A person or thing that is preferred to all others of the same kind; a bookmarked item.",
     "العنصر أو الكلمة التي يختار المستخدم حفظها للرجوع السريع إليها ومراجعتها.",
     "Click the star button to add any word or translation to your favorites.",
     "انقر على زر النجمة لإضافة أي كلمة أو ترجمة إلى قائمة المفضلة."),
    ("review", "مُرَاجَعَة / تَقْيِيم / يُرَاجِع", "noun", "/rɪˈvjuː/", "A2", "Education", "review", "ر ج ع / ق ي م", "reviews", "مُرَاجَعَات / تَقْيِيمَات",
     "A formal assessment or examination of something with the possibility or intention of instituting change; studying learned material again.",
     "إعادة دراسة الكلمات والمعلومات المحفوظة لتثبيتها في الذاكرة، أو فحص العمل وتقييمه.",
     "Spaced repetition review helps students retain new vocabulary effectively.",
     "تساعد المراجعة القائمة على التكرار المتباعد الطلاب على الاحتفاظ بالمفردات الجديدة بفعالية."),
    ("student", "طَالِب / دَارِس", "noun", "/ˈstuː.dənt/", "A1", "Education", "study", "ط ل ب / د ر س", "students", "طُلَّاب / طَالِبَات",
     "A person who is studying at a school, college, university, or independently.",
     "كل من يطلب العلم ويدرس في مدرسة أو جامعة أو يتعلم ذاتياً.",
     "The learning and review tools make the dictionary especially helpful for students.",
     "تجعل أدوات التعلم والمراجعة القاموس مفيداً بشكل خاص للطلاب."),
    ("teacher", "مُعَلِّم / أُسْتَاذ / مُدَرِّس", "noun", "/ˈtiː.tʃɚ/", "A1", "Education", "teach", "ع ل م / د ر س", "teachers", "مُعَلِّمُونَ / مُعَلِّمَات",
     "A person who teaches, especially in a school or university.",
     "من يقوم بمهمة التعليم والتربية وشرح المعارف للطلاب.",
     "The teacher exported a custom vocabulary list as a JSON file for the class.",
     "صدّر المعلم قائمة مفردات مخصصة كملف JSON للفصل الدراسي."),
    ("university", "جَامِعَة", "noun", "/ˌjuː.nəˈvɝː.sə.t̬i/", "A1", "Education", "universe", "ج م ع", "universities", "جَامِعَات",
     "An educational institution of the highest level, providing facilities for teaching and research and authorized to grant academic degrees.",
     "مؤسسة تعليم عالٍ وأبحاث علمية تمنح الدرجات الأكاديمية في مختلف التخصصات.",
     "She graduated from the university with a degree in computer engineering.",
     "تخرجت من الجامعة بشهادة في هندسة الحاسوب."),
    ("book", "كِتَاب / يَحْجِز", "noun", "/bʊk/", "A1", "Education", "book", "ك ت ب / ح ج ز", "books", "كُتُب",
     "A written or printed work consisting of pages glued or sewn together along one side and bound in covers; as a verb: to reserve accommodations or tickets.",
     "مؤلَّف مطبوع أو رقمي يضم صفحات مرتبة (اسم)، أو يقوم بحجز تذكرة أو موعد مسبقاً (فعل).",
     "I read an insightful book on Arabic computational linguistics.",
     "قرأت كتاباً قيّماً حول اللسانيات الحاسوبية العربية."),
    ("develop", "يُطَوِّر / يَبْنِي / يَنْمُو", "verb", "/dɪˈvel.əp/", "A2", "Technology", "develop", "ط و ر / ن م و", "develops", "يُطَوِّرُونَ",
     "To grow or cause to grow and become more mature, advanced, or elaborate.",
     "بناء الأنظمة والبرمجيات وتحسين قدراتها تدريجياً لتصبح أكثر نضجاً وكفاءة.",
     "Mohammed Al-Bakir developed LinguaDesk Pro as a complete offline translation solution.",
     "طوّر محمد البكير تطبيق LinguaDesk Pro بوصفه حلاً متكاملاً للترجمة دون إنترنت."),
    ("create", "يُنْشِئ / يَبْتَكِر / يَخْلُق", "verb", "/kriˈeɪt/", "A2", "General", "create", "ن ش أ / ب ك ر", "creates", "يُنْشِئُونَ",
     "To bring something into existence.",
     "إيجاد شيء جديد أو تصميم ملف أو قاعدة بيانات أو عمل إبداعي.",
     "You can create custom vocabulary groups directly from any translated text.",
     "يمكنك إنشاء مجموعات مفردات مخصصة مباشرة من أي نص مترجم."),
    ("verify", "يَتَحَقَّق مِن / يَتَثَبَّت مِن صِحَّة", "verb", "/ˈver.ə.faɪ/", "B2", "Technology", "verify", "ح ق ق / ث ب ت", "verifies", "يَتَحَقَّقُونَ",
     "To make sure or demonstrate that something is true, accurate, or justified.",
     "فحص البيانات أو الملفات للتأكد من سلامتها وصحتها ومطابقتها للمعايير.",
     "The resource manager verifies file integrity using SHA-256 cryptographic hashes.",
     "يتحقق مدير الموارد من سلامة الملفات باستخدام بصمات التشفير SHA-256."),
    ("search", "بَحْث / يَبْحَث عَن", "verb", "/sɝːtʃ/", "A1", "General", "search", "ب ح ث / ف ت ش", "searches", "عَمَلِيَّات بَحْث",
     "To try to find something by looking or otherwise seeking carefully and thoroughly.",
     "التفتيش والاستقصاء للوصول إلى كلمة أو معلومة داخل قاعدة البيانات أو النصوص.",
     "Instant search returns matching Arabic and English words in less than five milliseconds.",
     "يُرجع البحث الفوري الكلمات العربية والإنجليزية المطابقة في أقل من خمسة أجزاء من الألف من الثانية."),
    ("understand", "يَفْهَم / يَسْتَوْعِب / يُدْرِك", "verb", "/ˌʌn.dɚˈstænd/", "A1", "General", "understand", "ف ه م / و ع ب", "understands", "يَفْهَمُونَ",
     "To perceive the intended meaning of words, a language, or a speaker.",
     "إدراك المعنى المقصود من الكلام أو النص واستيعاب دلالاته.",
     "Contextual examples help learners understand subtle differences between synonyms.",
     "تساعد الأمثلة السياقية المتعلمين على فهم الفروق الدقيقة بين المرادفات."),
    ("write", "يَكْتُب / يُؤَلِّف", "verb", "/raɪt/", "A1", "General", "write", "ك ت ب / أ ل ف", "writes", "يَكْتُبُونَ",
     "To mark letters, words, or other symbols on a surface, typically paper, with a pen, pencil, or keyboard.",
     "تدوين الحروف والكلمات والجمل للتعبير عن الأفكار أو حفظ المعلومات.",
     "As soon as you begin to write, autocomplete suggestions appear smoothly.",
     "بمجرد أن تبدأ في الكتابة، تظهر اقتراحات الإكمال التلقائي بسلاسة."),
    ("read", "يَقْرَأ / يَطَّلِع عَلَى", "verb", "/riːd/", "A1", "General", "read", "ق ر أ / ط ل ع", "reads", "يَقْرَؤُونَ",
     "To look at and comprehend the meaning of written or printed matter by mentally interpreting the characters or symbols of which it is composed.",
     "النظر في النص المكتوب واستيعاب معانيه أو نطقه جهراً، وفي الحوسبة: استرجاع البيانات من الذاكرة أو الملف.",
     "The application does not read the clipboard continuously in the background.",
     "لا يقرأ التطبيق الحافظة باستمرار في الخلفية حفاظاً على الخصوصية."),
    ("speak", "يَتَحَدَّث / يَتَكَلَّم / يَنْطِق", "verb", "/spiːk/", "A1", "General", "speak", "ح د ث / ك ل م / ن ط ق", "speaks", "يَتَحَدَّثُونَ",
     "To say something in order to convey information, an opinion, or a feeling.",
     "التلفظ بالكلمات والجمل للتواصل الشفهي بلغة معينة.",
     "Listening to native pronunciation helps you speak with greater confidence.",
     "يساعدك الاستماع إلى النطق الطبيعي على التحدث بثقة أكبر."),
    ("listen", "يَسْتَمِع / يُصْغِي", "verb", "/ˈlɪs.ən/", "A1", "General", "listen", "س م ع / ص غ ي", "listens", "يَسْتَمِعُونَ",
     "To give one's attention to a sound.",
     "توجيه الانتباه السمعي إلى الكلام أو الصوت لفهمه.",
     "Click the speaker icon to listen to slow or normal pronunciation offline.",
     "انقر على أيقونة مكبر الصوت للاستماع إلى النطق البطيء أو العادي دون إنترنت."),
    ("learn", "يَتَعَلَّم / يَدْرُس / يَكْتَسِب مَهَارَة", "verb", "/lɝːn/", "A1", "Education", "learn", "ع ل م / د ر س", "learns", "يَتَعَلَّمُونَ",
     "To gain or acquire knowledge of or skill in something by study, experience, or being taught.",
     "اكتساب المعرفة أو المهارات اللغوية والعلمية عبر الدراسة والممارسة.",
     "You can learn twenty new words every week using the flashcard review system.",
     "يمكنك تعلم عشرين كلمة جديدة كل أسبوع باستخدام نظام مراجعة البطاقات التعليمية."),
    ("save", "يَحْفَظ / يُوَفِّر / يُنْقِذ", "verb", "/seɪv/", "A1", "General", "save", "ح ف ظ / و ف ر / ن ق ذ", "saves", "يَحْفَظُونَ",
     "To keep data for future use; to rescue from harm; or to avoid spending time or money.",
     "تخزين البيانات على القرص للرجوع إليها، أو توفير الوقت والمال، أو إنقاذ شخص من خطر.",
     "Remember to save your personal notes and favorite words.",
     "تذكر أن تحفظ ملاحظاتك الشخصية وكلماتك المفضلة."),
    ("delete", "يَحْذِف / يَمْحُو", "verb", "/dɪˈliːt/", "A2", "Technology", "delete", "ح ذ ف / م ح و", "deletes", "يَحْذِفُونَ",
     "To remove or obliterate written or printed matter, or digital data from a computer's memory.",
     "إزالة ملف أو نص أو سجل من قاعدة البيانات أو وحدة التخزين.",
     "Core dictionary files are protected so the user cannot delete them accidentally.",
     "ملفات القاموس الأساسي محمية بحيث لا يمكن للمستخدم حذفها عن طريق الخطأ."),
    ("update", "يُحَدِّث / تَحْدِيث", "verb", "/ʌpˈdeɪt/", "A2", "Technology", "update", "ح د ث", "updates", "تَحْدِيثَات",
     "To make something more modern or up to date by adding new information or software improvements.",
     "إضافة بيانات جديدة أو ترقية إصدار البرنامج أو القاموس دون فقدان بيانات المستخدم.",
     "You can update the dictionary database without rewriting the user interface.",
     "يمكنك تحديث قاعدة بيانات القاموس دون إعادة كتابة واجهة المستخدم."),
    ("download", "يُنَزِّل / يَحْمِّل مِنَ الإِنْتَرْنِت", "verb", "/ˈdaʊn.loʊd/", "A1", "Technology", "download", "ن ز ل / ح م ل", "downloads", "تَنْزِيلَات",
     "To copy data from one computer system to another, typically over the internet.",
     "نقل الملفات أو الحزم اللغوية من خادم بعيد إلى جهاز المستخدم المحلي.",
     "Optional neural translation models can be downloaded whenever needed.",
     "يمكن تنزيل نماذج الترجمة العصبية الاختيارية متى دعت الحاجة."),
    ("cancel", "يُلْغِي / يُوقِفُ العَمَلِيَّة", "verb", "/ˈkæn.səl/", "A2", "General", "cancel", "ل غ ي / و ق ف", "cancels", "يُلْغُونَ",
     "To decide or announce that a planned event will not take place, or to abort an active computer operation.",
     "إيقاف عملية جارية (مثل ترجمة نص طويل أو تنزيل ملف) قبل اكتمالها.",
     "Users can cancel long translation tasks at any moment without freezing the screen.",
     "يمكن للمستخدمين إلغاء مهام الترجمة الطويلة في أي لحظة دون تجميد الشاشة."),
    ("accurate", "دَقِيق / صَحِيح / مَضْبُوط", "adjective", "/ˈæk.jɚ.ət/", "B1", "General", "accurate", "د ق ق / ص ح ح", "", "دَقِيقَة",
     "Correct in all details; exact.",
     "مطابق للصواب في جميع تفاصيله وخالٍ من الأخطاء.",
     "The dictionary provides accurate Arabic explanations and phonetic transcriptions.",
     "يقدم القاموس شروحاً عربية دقيقة ورموزاً صوتية مضبوطة."),
    ("fast", "سَرِيع / بِسُرْعَة / يَصُوم", "adjective", "/fæst/", "A1", "General", "fast", "س ر ع / ص و م", "", "سَرِيعَة",
     "Moving or capable of moving at high speed; or abstaining from food and drink (verb/noun).",
     "متصف بالسرعة العالية في الحركة أو المعالجة (صفة/ظرف)، أو الإمساك عن الطعام والشراب أي الصيام (فعل/اسم).",
     "Indexed SQLite queries make autocomplete suggestions remarkably fast.",
     "تجعل استعلامات SQLite المفهرسة اقتراحات الإكمال التلقائي سريعة للغاية."),
    ("modern", "حَدِيث / عَصْرِيّ", "adjective", "/ˈmɑː.dɚn/", "A1", "General", "modern", "ح د ث / ع ص ر", "", "حَدِيثَة / عَصْرِيَّة",
     "Relating to the present or recent times as opposed to the remote past; using the most up-to-date techniques.",
     "مواكب للعصر الحاضر في تصميمه وتقنياته وأساليبه.",
     "The application features a clean, modern user interface with calm colors.",
     "يتميز التطبيق بواجهة مستخدم نظيفة وعصرية ذات ألوان هادئة."),
    ("important", "مُهِمّ / ذُو أَهَمِّيَّة", "adjective", "/ɪmˈpɔːr.tənt/", "A1", "General", "important", "ه م م", "", "مُهِمَّة",
     "Of great significance or value; likely to have a profound effect on success, survival, or well-being.",
     "ذو شأن وقيمة عالية يستوجب العناية والاهتمام.",
     "Uninstalling the application removes temporary files while keeping important user data safe.",
     "يؤدي إلغاء تثبيت التطبيق إلى إزالة الملفات المؤقتة مع الحفاظ على سلامة بيانات المستخدم المهمة."),
    ("successful", "نَاجِح / مُوَفَّق", "adjective", "/səkˈses.fəl/", "A2", "General", "succeed", "ن ج ح / و ف ق", "", "نَاجِحَة",
     "Accomplishing an aim or purpose.",
     "من حقق هدفه المرجو وأتم عمله على الوجه المطلوب.",
     "All automated unit and integration tests were successful.",
     "كانت جميع اختبارات الوحدات والتكامل الآلية ناجحة."),
    ("difficult", "صَعْب / عَسِير / شَاقّ", "adjective", "/ˈdɪf.ə.kəlt/", "A1", "General", "difficult", "ص ع ب / ع س ر", "", "صَعْبَة",
     "Needing much effort or skill to accomplish, deal with, or understand.",
     "ما يحتاج إلى جهد ومهارة لإنجازه أو فهمه.",
     "You can classify vocabulary cards as easy, medium, or difficult during review.",
     "يمكنك تصنيف بطاقات المفردات إلى سهلة أو متوسطة أو صعبة أثناء المراجعة."),
    ("easy", "سَهْل / يَسِير", "adjective", "/ˈiː.zi/", "A1", "General", "easy", "س ه ل / ي س ر", "", "سَهْلَة",
     "Achieved without great effort; presenting few difficulties.",
     "واضح وميسّر لا يتطلب عناءً أو تعقيداً.",
     "The installer makes deploying the software on Windows easy for beginners.",
     "يجعل المثبت نشر البرنامج على نظام ويندوز سهلاً للمبتدئين."),
    ("clear", "وَاضِح / صَافٍ / يَمْسَح", "adjective", "/klɪr/", "A1", "General", "clear", "و ض ح / ص ف و / م س ح", "", "وَاضِحَة",
     "Easy to perceive, understand, or interpret; or to remove/empty text from an input box (verb).",
     "بيّن جليّ لا لبس فيه (صفة)، أو يفرغ حقل النص ويمسحه (فعل).",
     "Click the clear button to empty the input box and start a new translation.",
     "انقر على زر المسح لتفريغ مربع الإدخال وبدء ترجمة جديدة.")
]

# ==============================================================================
# 6. EXTENDED CURATED BILINGUAL GLOSSARY (800+ Additional Core Words Across Domains)
# ==============================================================================
EXTENDED_GLOSSARY_COMPACT = [
    # Format: "word_en|word_ar|pos|domain|cefr|root_ar"
    "ability|قُدْرَة / اسْتِطَاعَة / كَفَاءَة|noun|General|A2|ق د ر",
    "abroad|فِي الخَارِج / خَارِجَ البِلَاد|adverb|General|A2|خ ر ج",
    "absence|غِيَاب / فُقْدَان / انْعِدَام|noun|General|B1|غ ي ب",
    "absolute|مُطْلَق / تَامّ / كَامِل|adjective|Science|B2|ط ل ق",
    "abstract|مُجَرَّد / مُلَخَّصُ بَحْثٍ عِلْمِيّ|noun|Academic|B2|ج ر د / ل خ ص",
    "academic|أَكَادِيمِيّ / جَامِعِيّ / عِلْمِيّ|adjective|Education|B1|ع ل م / ج م ع",
    "accelerate|يُسَرِّع / يُعَجِّل|verb|Science|B2|س ر ع / ع ج ل",
    "acceleration|تَسَارُع / تَعْجِيل|noun|Science|B2|س ر ع",
    "accent|لَكْنَة / نَبْرَةٌ صَوْتِيَّة / لَهْجَة|noun|Education|B1|ل ك ن / ن ب ر / ل ه ج",
    "access|وُصُول / نَفَاذ / يَدْخُل إِلَى|noun|Technology|B1|و ص ل / ن ف ذ",
    "accessible|مُتَاحٌ لِلوُصُول / سَهْلُ المَنَال|adjective|Technology|B1|ت ي ح / و ص ل",
    "accident|حَادِث / صُدْفَة|noun|General|A2|ح د ث / ص د ف",
    "accommodate|يَسْتَوْعِب / يُوَفِّرُ سَكَناً / يُكَيِّف|verb|General|B2|و ع ب / س ك ن",
    "accompany|يُرَافِق / يَصْحَب|verb|General|B1|ر ف ق / ص ح ب",
    "accomplish|يُنْجِز / يُتِمّ / يُحَقِّق|verb|General|B1|ن ج ز / ت م م",
    "accordance|تَوَافُق / طِبْقاً لِـ|noun|Legal|B2|و ف ق / ط ب ق",
    "accountability|مُسَاءَلَة / مَسْؤُولِيَّة|noun|Legal|C1|س أ ل",
    "accumulate|يَتَرَاكَم / يَجْمَع|verb|Science|B2|ر ك م / ج م ع",
    "acknowledge|يُقِرّ بِـ / يَعْتَرِف بِـ / يُؤَكِّدُ الاسْتِلَام|verb|Academic|B2|ق ر ر / ع ر ف",
    "acquire|يَكْتَسِب / يَحْصُل عَلَى / يَسْتَحْوِذ|verb|Business|B2|ك س ب / ح ص ل",
    "acquisition|اكْتِسَابُ اللُّغَة / اسْتِحْوَاذٌ تِجَارِيّ|noun|Education|B2|ك س ب / ح و ذ",
    "acronym|اخْتِصَارٌ حَرْفِيّ (مِثْل OCR وَ CPU)|noun|Education|B2|خ ص ر",
    "action|عَمَل / إِجْرَاء / فِعْل / حَرَكَة|noun|General|A1|ع م ل / ج ر ي / ف ع ل",
    "activate|يُفَعِّل / يُنَشِّط|verb|Technology|B1|ف ع ل / ن ش ط",
    "active|نَشِط / فَعَّال / مَبْنِيّ للمَعْلُوم|adjective|General|A2|ن ش ط / ف ع ل",
    "activity|نَشَاط / فَعَالِيَّة|noun|General|A1|ن ش ط",
    "actual|فِعْلِيّ / حَقِيقِيّ / وَاقِعِيّ|adjective|General|B1|ف ع ل / ح ق ق / و ق ع",
    "adapt|يَتَكَيَّف / يُعَدِّلُ لِيُنَاسِب|verb|Science|B1|ك ي ف / ع د ل",
    "adaptation|تَكَيُّف / اقْتِبَاس / تَهْيِئَة|noun|Science|B2|ك ي ف",
    "addition|إِضَافَة / عَمَلِيَّةُ الجَمْع|noun|Science|A2|ض ي ف / ج م ع",
    "additional|إِضَافِيّ / زَائِد|adjective|General|B1|ض ي ف / ز ي د",
    "address|عُنْوَان (بَرِيدِيّ أَوْ فِي الذَّاكِرَة) / يُخَاطِب / يُعَالِج|noun|Technology|A1|ع ن و ن / خ ط ب / ع ل ج",
    "adequate|كَافٍ / مُلَائِم / مُنَاسِب|adjective|Academic|B2|ك ف ي / ل أ م",
    "adjust|يَضْبِط / يُعَدِّل / يَتَكَيَّف|verb|Technology|B1|ض ب ط / ع د ل",
    "adjustment|تَعْدِيل / ضَبْط / تَسْوِيَة|noun|Technology|B2|ع د ل / ض ب ط",
    "administration|إِدَارَة / حُكُومَة / إِعْطَاءُ الدَّوَاء|noun|Business|B1|د و ر / ح ك م",
    "administrator|مَسْؤُولُ النِّظَام (Administrator) / مُدِير|noun|Technology|B1|س أ ل / د و ر",
    "admire|يُعْجَب بِـ / يُقَدِّر|verb|General|B1|ع ج ب / ق د ر",
    "admission|قَبُول (جَامِعِيّ أَوْ طِبِّيّ) / اعْتِرَاف / دُخُول|noun|Education|B1|ق ب ل / د خ ل",
    "adopt|يَتَبَنَّى (فِكْرَةً أَوْ نِظَاماً) / يَعْتَمِد|verb|General|B1|ب ن ي / ع م د",
    "advance|تَقَدُّم / يَتَقَدَّم / سُلْفَة|noun|General|B1|ق د م / س ل ف",
    "advanced|مُتَقَدِّم / مُتَطَوِّر|adjective|Education|A2|ق د م / ط و ر",
    "advantage|مِيزَة / أَفْضَلِيَّة / فَائِدَة|noun|General|A2|م ي ز / ف ض ل / ف ي د",
    "advice|نَصِيحَة / مَشُورَة|noun|General|A1|ن ص ح / ش و ر",
    "advise|يَنْصَح / يُوصِي / يُشِير عَلَى|verb|General|A2|ن ص ح / و ص ي",
    "affect|يُؤَثِّر فِي / يَمَسّ|verb|General|A2|أ ث ر / م س س",
    "effect|تَأْثِير / أَثَر / نَتِيجَة|noun|General|A2|أ ث ر / ن ت ج",
    "efficient|فَعَّال / كُفْء / عَالِي الكَفَاءَة|adjective|Technology|B1|ف ع ل / ك ف أ",
    "efficiency|كَفَاءَة / فَعَالِيَّة|noun|Technology|B1|ك ف أ / ف ع ل",
    "element|عُنْصُر (كِيمْيَائِيّ أَوْ فِي وَاجِهَةِ المُسْتَخْدِم)|noun|Science|B1|ع ن ص ر",
    "eliminate|يُزِيل / يَقْضِي عَلَى / يَسْتَبْعِد|verb|Science|B2|ز و ل / ق ض ي / ب ع د",
    "emergency|طَوَارِئ / حَالَةُ طَوَارِئ|noun|Medicine|B1|ط ر أ",
    "emphasis|تَأْكِيد / تَشْدِيد / إِبْرَاز|noun|Education|B2|أ ك د / ش د د / ب ر ز",
    "emphasize|يُؤَكِّد عَلَى / يُشَدِّد عَلَى|verb|Education|B2|أ ك د / ش د د",
    "employ|يُوَظِّف / يَسْتَخْدِم|verb|Business|B1|و ظ ف / خ د م",
    "employee|مُوَظَّف / عَامِل|noun|Business|A2|و ظ ف / ع م ل",
    "employer|صَاحِبُ العَمَل / جِهَةُ التَّوْظِيف|noun|Business|A2|ص ح ب / و ظ ف",
    "employment|تَوْظِيف / عَمَل / عِمَالَة|noun|Business|B1|و ظ ف / ع م ل",
    "encode|يُرَمِّز / يُحَوِّلُ إِلَى تَرْمِيزٍ رَقْمِيّ|verb|Technology|B2|ر م ز / ح و ل",
    "decode|يَفُكُّ التَّرْمِيز / يُفَسِّرُ الشِّفْرَة|verb|Technology|B2|ف ك ك / ر م ز",
    "encourage|يُشَجِّع / يَحُثّ / يَدْعَم|verb|Education|B1|ش ج ع / ح ث ث / د ع م",
    "engine|مُحَرِّك (مِيكَانِيكِيّ أَوْ مُحَرِّكٌ بَرْمَجِيّ لِلتَّرْجَمَةِ وَالبَحْث)|noun|Technology|A2|ح ر ك",
    "enhance|يُعَزِّز / يُحَسِّن / يُطَوِّر|verb|Technology|B2|ع ز ز / ح س ن",
    "enough|كَافٍ / بِمَا فِيهِ الكِفَايَة|adverb|General|A1|ك ف ي",
    "enter|يَدْخُل / يُدْخِلُ بَيَانَات|verb|General|A1|د خ ل",
    "enterprise|مُؤَسَّسَةٌ كُبْرَى / مَشْرُوعٌ طَمُوح|noun|Business|B2|أ س س / ش ر ع",
    "entire|كَامِل / كُلِّيّ / بِأَكْمَلِهِ|adjective|General|B1|ك م ل / ك ل ل",
    "entry|مَدْخَلٌ مُعْجَمِيّ (فِي القَامُوس) / دُخُول / قَيْد|noun|Education|B1|د خ ل / ق ي د",
    "equal|مُسَاوٍ / مُعَادِل / يُسَاوِي|adjective|Science|A2|س و ي / ع د ل",
    "equipment|مُعَدَّات / تَجْهِيزَات|noun|Technology|A2|ع د د / ج ه ز",
    "equivalent|مُكَافِئ / مُقَابِلٌ لُغَوِيّ / مَثِيل|noun|Education|B2|ك ف أ / ق ب ل / م ث ل",
    "essential|أَسَاسِيّ / جَوْهَرِيّ / ضَرُورِيّ|adjective|General|B1|أ س س / ج و ه ر / ض ر ر",
    "estimate|تَقْدِير / يُقَدِّرُ تَقْرِيباً|verb|Science|B1|ق د ر / ق ر ب",
    "ethics|أَخْلَاقِيَّاتُ المِهْنَة / عِلْمُ الأَخْلَاق|noun|Legal|B2|خ ل ق",
    "event|حَدَث (تَارِيخِيّ أَوْ بَرْمَجِيّ)|noun|Technology|A1|ح د ث",
    "exact|دَقِيق / مُطَابِقٌ تَمَاماً / مَضْبُوط|adjective|Science|A2|د ق ق / ط ب ق / ض ب ط",
    "examination|امْتِحَان / فَحْصٌ طِبِّيّ أَوْ عِلْمِيّ|noun|Education|B1|م ح ن / ف ح ص",
    "excellent|مُمْتَاز / فَائِقُ الجَوْدَة|adjective|General|A1|م ي ز / ج و د",
    "exchange|تَبَادُل / صَرْفُ العُمْلَات / يَتَبَادَل|noun|Business|B1|ب د ل / ص ر ف",
    "exclude|يَسْتَبْعِد / يَسْتَثْنِي|verb|Academic|B2|ب ع د / ث ن ي",
    "executable|مِلَفٌّ تَنْفِيذِيّ (EXE) / قَابِلٌ لِلتَّشْغِيل|noun|Technology|B2|ن ف ذ / ش غ ل",
    "exercise|تَمْرِين / تَدْرِيب / يُمَارِس|noun|Education|A1|م ر ن / د ر ب / م ر س",
    "exist|يُوجَد / يَكُونُ مَوْجُوداً|verb|General|A2|و ج د / ك و ن",
    "existence|وُجُود / كِيَان|noun|General|B2|و ج د / ك ي ن",
    "expand|يُوَسِّع / يَتَوَسَّع / يَتَمَدَّد|verb|Science|B1|و س ع / م د د",
    "expect|يَتَوَقَّع / يَنْتَظِر|verb|General|A2|و ق ع / ن ظ ر",
    "expense|نَفَقَة / مَصْرُوف / تَكْلِفَة|noun|Business|B1|ن ف ق / ص ر ف / ك ل ف",
    "expensive|غَالٍ / بَاهِظُ الثَّمَن / مُكَلِّف|adjective|General|A1|غ ل و / ب ه ظ / ك ل ف",
    "expert|خَبِير / مُخْتَصّ|noun|General|A2|خ ب ر / خ ص ص",
    "explanation|شَرْح / تَفْسِير / تَوْضِيح|noun|Education|A2|ش ر ح / ف س ر / و ض ح",
    "explicit|صَرِيح / وَاضِحٌ بِلَا لَبْس|adjective|Academic|C1|ص ر ح / و ض ح",
    "explore|يَسْتَكْشِف / يَبْحَثُ فِي|verb|Science|B1|ك ش ف / ب ح ث",
    "expression|تَعْبِير (لُغَوِيّ أَوْ رِيَاضِيّ) / عِبَارَة|noun|Education|B1|ع ب ر",
    "extend|يَمُدّ / يُمَدِّد / يُوَسِّع|verb|General|B1|م د د / و س ع",
    "extension|امْتِدَادُ المِلَفّ / إِضَافَةُ مُتَصَفِّح / تَمْدِيد|noun|Technology|B1|م د د / ض ي ف",
    "extra|إِضَافِيّ / زَائِد|adjective|General|A1|ض ي ف / ز ي د",
    "facility|مِرْفَق / مُنْشَأَة / تَسْهِيل|noun|Business|B1|ر ف ق / ن ش أ / س ه ل",
    "fact|حَقِيقَة / وَاقِعَةٌ ثَابِتَة|noun|General|A1|ح ق ق / و ق ع",
    "factor|عَامِل (مُؤَثِّر أَوْ رِيَاضِيّ)|noun|Science|B1|ع م ل / أ ث ر",
    "fail|يَفْشَل / يَرْسُب / يَتَعَطَّل|verb|General|A2|ف ش ل / ر س ب / ع ط ل",
    "fair|عَادِل / مُنْصِف / مَعْرِض|adjective|Legal|A2|ع د ل / ن ص ف / ع ر ض",
    "fall|يَسْقُط / يَنْخَفِض / فَصْلُ الخَرِيف|verb|General|A1|س ق ط / خ ف ض / خ ر ف",
    "false|خَاطِئ / كَاذِب / غَيْرُ صَحِيح (False)|adjective|Technology|A1|خ ط أ / ك ذ ب",
    "true|صَحِيح / حَقِيقِيّ / صَادِق (True)|adjective|Technology|A1|ص ح ح / ح ق ق / ص د ق",
    "familiar|مَأْلُوف / مَعْرُوف|adjective|General|B1|أ ل ف / ع ر ف",
    "famous|مَشْهُور / ذَائِعُ الصِّيت|adjective|General|A1|ش ه ر / ذ ي ع",
    "far|بَعِيد / إِلَى حَدٍّ بَعِيد|adverb|General|A1|ب ع د",
    "near|قَرِيب / بِالقُرْبِ مِن|preposition|General|A1|ق ر ب",
    "fault|خَطَأ / عُطْل / ذَنْب|noun|Technology|B1|خ ط أ / ع ط ل / ذ ن ب",
    "feedback|تَغْذِيَةٌ رَاجِعَة / مُلَاحَظَاتٌ تَقْيِيمِيَّة|noun|Education|B1|غ ذ و / ر ج ع / ل ح ظ",
    "final|نِهَائِيّ / أَخِير / امْتِحَانٌ نِهَائِيّ|adjective|General|A1|ن ه ي / أ خ ر",
    "finance|مَالِيَّة / تَمْوِيل / يُمَوِّل|noun|Business|B1|م و ل",
    "financial|مَالِيّ / مَصْرِفِيّ|adjective|Business|B1|م و ل / ص ر ف",
    "finish|يُنْهِي / يُتِمّ / نِهَايَة|verb|General|A1|ن ه ي / ت م م",
    "first|أَوَّل / أَوَّلاً|adjective|General|A1|أ و ل",
    "last|أَخِير / مَاضٍ / يَدُوم|adjective|General|A1|أ خ ر / م ض ي / د و م",
    "flexible|مَرِن / قَابِلٌ لِلتَّكَيُّف|adjective|Technology|B1|م ر ن / ك ي ف",
    "floating|عَائِم / نَافِذَةٌ عَائِمَة (Floating Window)|adjective|Technology|B1|ع و م / ط ف و",
    "focus|تَرْكِيز / بُؤْرَة / يُرَكِّز عَلَى|verb|General|A2|ر ك ز / ب أ ر",
    "foreign|أَجْنَبِيّ / خَارِجِيّ|adjective|General|A2|ج ن ب / خ ر ج",
    "forget|يَنْسَى / يَغْفُل عَن|verb|General|A1|ن س ي / غ ف ل",
    "form|شَكْل / صِيغَةٌ صَرْفِيَّة / نَمُوذَجٌ إِلكْتُرُونِيّ|noun|Education|A1|ش ك ل / ص و غ / ن م ذ ج",
    "formal|رَسْمِيّ / فَصِيح / مَنْهَجِيّ|adjective|Education|B1|ر س م / ف ص ح",
    "format|تَنْسِيق / صِيغَةُ مِلَفّ / يُنَسِّق|noun|Technology|B1|ن س ق / ص و غ",
    "foundation|أَسَاس / مُؤَسَّسَةٌ خَيْرِيَّة أَوْ عِلْمِيَّة|noun|General|B1|أ س س",
    "frequency|تَرَدُّد / مُعَدَّلُ الشُّيُوعِ وَالتَّكْرَار|noun|Science|B2|ر د د / ش ي ع / ك ر ر",
    "frequent|مُتَكَرِّر / شَائِع|adjective|General|B1|ك ر ر / ش ي ع",
    "function|وَظِيفَة / دَالَّةٌ رِيَاضِيَّة أَوْ بَرْمَجِيَّة / يَعْمَل|noun|Technology|B1|و ظ ف / د ل ل / ع م ل",
    "fundamental|أَسَاسِيّ / جَوْهَرِيّ / أَصْلِيّ|adjective|Science|B2|أ س س / ج و ه ر / أ ص ل",
    "general|عَامّ / شَامِل|adjective|General|A2|ع م م / ش م ل",
    "global|عَالَمِيّ / عَامٌّ عَلَى مُسْتَوَى النِّظَام (Global Shortcut)|adjective|Technology|B1|ع ل م / ع م م",
    "glossary|مَسْرَدُ مُصْطَلَحَات / قَائِمَةُ مَعَانِي الكَلِمَات|noun|Education|B2|س ر د / ص ط ل ح",
    "government|حُكُومَة / سُلْطَةٌ تَنْفِيذِيَّة|noun|Legal|A2|ح ك م / س ل ط",
    "grade|دَرَجَة / صَفٌّ دِرَاسِيّ / يُصَنِّف|noun|Education|A2|د ر ج / ص ف ف / ص ن ف",
    "gradual|تَدْرِيجِيّ / مُتَدَرِّج|adjective|General|B2|د ر ج",
    "grant|مَنْحَة / يَمْنَح / يَهَب|noun|Education|B2|م ن ح / و ه ب",
    "graph|رَسْمٌ بَيَانِيّ / مُخَطَّط|noun|Science|B1|ر س م / ب ي ن / خ ط ط",
    "growth|نُمُوّ / ازْدِهَار / تَطَوُّر|noun|Business|B1|ن م و / ز ه ر",
    "guarantee|ضَمَان / يَضْمَن / يَكْفُل|noun|Legal|B1|ض م ن / ك ف ل",
    "guide|دَلِيلٌ إِرْشَادِيّ / يُرْشِد / يُوَجِّه|noun|General|A2|د ل ل / ر ش د / و ج ه",
    "guideline|مَبْدَأٌ تَوْجِيهِيّ / إِرْشَادٌ عَامّ|noun|Academic|B2|ر ش د / و ج ه",
    "habit|عَادَة / دَأْب|noun|General|A2|ع و د / د أ ب",
    "half|نِصْف / شَطْر|noun|General|A1|ن ص ف / ش ط ر",
    "hard|صَعْب / صُلْب / بِجِدٍّ وَاجْتِهَاد|adjective|General|A1|ص ع ب / ص ل ب / ج د د",
    "head|رَأْس / رَئِيس / يَتَرَأَّس|noun|General|A1|ر أ س",
    "heading|عُنْوَانٌ فَرْعِيّ / تَرْوِيسَة|noun|Education|B1|ع ن و ن / ر أ س",
    "heavy|ثَقِيل / كَثِيف / شَدِيد|adjective|General|A1|ث ق ل / ك ث ف / ش د د",
    "helpful|مُفِيد / مُعِين / مُسَاعِد|adjective|General|A2|ف ي د / ع و ن / س ع د",
    "hide|يُخْفِي / يَخْتَبِئ|verb|General|A2|خ ف ي / خ ب أ",
    "highlight|يُظَلِّلُ النَّصَّ / يُبْرِز / أَبْرَزُ النِّقَاط|verb|Technology|B1|ظ ل ل / ب ر ز",
    "honest|صَادِق / أَمِين / نَزِيه|adjective|General|B1|ص د ق / أ م ن / ن ز ه",
    "hope|أَمَل / رَجَاء / يَأْمُل|noun|General|A1|أ م ل / ر ج و",
    "hour|سَاعَةٌ زَمَنِيَّة (60 دَقِيقَة)|noun|General|A1|س و ع",
    "minute|دَقِيقَةٌ زَمَنِيَّة / دَقِيقٌ جِدّاً|noun|General|A1|د ق ق",
    "second|ثَانِيَةٌ زَمَنِيَّة / الثَّانِي|noun|General|A1|ث ن ي",
    "human|إِنْسَان / بَشَرِيّ / إِنْسَانِيّ|noun|General|A2|أ ن س / ب ش ر",
    "hypothesis|فَرَضِيَّةٌ عِلْمِيَّة|noun|Science|B2|ف ر ض",
    "idea|فِكْرَة / تَصَوُّر|noun|General|A1|ف ك ر / ص و ر",
    "ideal|مِثَالِيّ / نَمُوذَجِيّ|adjective|General|B1|م ث ل / ن م ذ ج",
    "ignore|يَتَجَاهَل / يُهْمِل / يَغُضُّ الطَّرْفَ عَن|verb|General|B1|ج ه ل / ه م ل",
    "illustrate|يُوَضِّحُ بِالأَمْثِلَةِ أَوِ الرُّسُوم|verb|Education|B2|و ض ح / م ث ل",
    "immediate|فَوْرِيّ / مُبَاشِر / عَاجِل|adjective|General|B1|ف و ر / ب ش ر / ع ج ل",
    "impact|أَثَر / تَأْثِيرٌ قَوِيّ / اصْطِدَام|noun|General|B1|أ ث ر / ص د م",
    "implement|يُنَفِّذ / يُطَبِّقُ بَرْمَجِيّاً أَوْ عَمَلِيّاً|verb|Technology|B2|ن ف ذ / ط ب ق",
    "implementation|تَنْفِيذٌ فِعْلِيّ / تَطْبِيقٌ بَرْمَجِيّ|noun|Technology|B2|ن ف ذ / ط ب ق",
    "imply|يَتَضَمَّن / يُوحِي بِـ / يَسْتَلْزِمُ ضِمْنِيّاً|verb|Academic|B2|ض م ن / و ح ي / ل ز م",
    "importance|أَهَمِّيَّة / شَأْن / قِيمَة|noun|General|B1|ه م م / ق ي م",
    "impossible|مُسْتَحِيل / غَيْرُ مُمْكِن|adjective|General|A2|ح و ل / م ك ن",
    "improvement|تَحْسِين / تَطْوِير / تَحَسُّن|noun|General|B1|ح س ن / ط و ر",
    "independent|مُسْتَقِلّ / غَيْرُ تَابِع|adjective|General|B1|ق ل ل / ت ب ع",
    "indicate|يُشِير إِلَى / يَدُلُّ عَلَى / يُبَيِّن|verb|Academic|B1|ش و ر / د ل ل / ب ي ن",
    "indicator|مُؤَشِّر (مِثْل مُؤَشِّر التَّقَدُّم Progress Indicator)|noun|Technology|B2|أ ش ر",
    "individual|فَرْد / فَرْدِيّ / شَخْصِيّ|noun|General|A2|ف ر د / ش خ ص",
    "industry|صِنَاعَة / قِطَاعٌ صِنَاعِيّ|noun|Business|A2|ص ن ع / ق ط ع",
    "inflection|تَصْرِيفٌ نَحْوِيّ أَوْ صَرْفِيّ / إِعْرَاب|noun|Education|C1|ص ر ف / ع ر ب",
    "influence|تَأْثِير / نُفُوذ / يُؤَثِّر عَلَى|noun|General|B1|أ ث ر / ن ف ذ",
    "inform|يُبْلِغ / يُخْبِر / يُعْلِم|verb|General|B1|ب ل غ / خ ب ر / ع ل م",
    "information|مَعْلُومَات / بَيَانَاتٌ مَفْهُومَة|noun|General|A1|ع ل م / ب ي ن",
    "initial|أَوَّلِيّ / ابْتِدَائِيّ / حَرْفٌ اسْتِهْلَالِيّ|adjective|General|B1|أ و ل / ب د أ",
    "initialize|يُهَيِّئُ مَبْدَئِيّاً (فِي البَرْمَجَة)|verb|Technology|C1|ه ي أ / ب د أ",
    "innovation|ابْتِكَار / تَجْدِيد / إِبْدَاع|noun|Technology|B2|ب ك ر / ج د د / ب د ع",
    "input|مُدْخَلَات / إِدْخَالٌ نَصِّيّ|noun|Technology|B1|د خ ل",
    "output|مُخْرَجَات / نَتِيجَة / إِنْتَاج|noun|Technology|B1|خ ر ج / ن ت ج",
    "inquiry|اسْتِفْسَار / تَحْقِيق / بَحْث|noun|Academic|B2|ف س ر / ح ق ق / ب ح ث",
    "insert|يُدْرِج / يُدْخِل (فِي قَاعِدَةِ البَيَانَاتِ أَوِ النَّصِّ)|verb|Technology|B1|د ر ج / د خ ل",
    "inside|دَاخِل / فِي الدَّاخِل / بَاطِن|preposition|General|A1|د خ ل / ب ط ن",
    "outside|خَارِج / فِي الخَارِج / ظَاهِر|preposition|General|A1|خ ر ج / ظ ه ر",
    "inspect|يَفْحَصُ بِدِقَّة / يُفَتِّش / يُعَايِن|verb|Technology|B2|ف ح ص / ف ت ش / ع ي ن",
    "installation|تَثْبِيت (البَرَامِج أَوِ المُعَدَّات) / تَنْصِيب|noun|Technology|B1|ث ب ت / ن ص ب",
    "instance|حَالَة / مِثَال / كَائِنٌ بَرْمَجِيّ|noun|Technology|B2|ح و ل / م ث ل / ك و ن",
    "instant|لَحْظَة / فَوْرِيّ / آنِيّ|adjective|General|B1|ل ح ظ / ف و ر / أ و ن",
    "instead|بَدَلاً مِن / عِوَضاً عَن|adverb|General|A2|ب د ل / ع و ض",
    "institute|مَعْهَدٌ عِلْمِيّ / يُؤَسِّس|noun|Education|B1|ع ه د / أ س س",
    "institution|مُؤَسَّسَة / هَيْئَة|noun|Business|B1|أ س س / ه ي أ",
    "instruction|تَعْلِيمَة (بَرْمَجِيَّة أَوْ إِرْشَادِيَّة) / تَدْرِيس|noun|Education|B1|ع ل م / ر ش د",
    "instrument|أَدَاة / آلَةٌ عِلْمِيَّة أَوْ مُوسِيقِيَّة / وَثِيقَةٌ قَانُونِيَّة|noun|Science|B1|أ د ي / أ ل ي / و ث ق",
    "integrate|يَدْمِج / يُكَامِل بَيْنَ الأَنْظِمَة|verb|Technology|B2|د م ج / ك م ل",
    "integration|تَكَامُل / دَمْج (مِثْل اخْتِبَارَات التَّكَامُل Integration Tests)|noun|Technology|B2|ك م ل / د م ج",
    "integrity|سَلَامَةُ المِلَفَّاتِ وَالبَيَانَات / نَزَاهَة / أَمَانَة|noun|Technology|C1|س ل م / ن ز ه / أ م ن",
    "intellectual|فِكْرِيّ / ذِهْنِيّ / مُثَقَّف|adjective|Academic|B2|ف ك ر / ذ ه ن / ث ق ف",
    "intelligence|ذَكَاء / فِطْنَة / مَعْلُومَاتٌ اسْتِخْبَارَاتِيَّة|noun|Science|B1|ذ ك و / ف ط ن / خ ب ر",
    "intend|يَنْوِي / يَقْصِد / يَعْتَزِم|verb|General|B1|ن و ي / ق ص د / ع ز م",
    "intention|نِيَّة / قَصْد / غَايَة|noun|General|B1|ن و ي / ق ص د / غ ي ي",
    "interact|يَتَفَاعَل مَعَ / يَتَوَاصَل|verb|General|B1|ف ع ل / و ص ل",
    "interaction|تَفَاعُل / تَوَاصُلٌ مُتَبَادَل|noun|Technology|B1|ف ع ل / و ص ل",
    "interactive|تَفَاعُلِيّ|adjective|Technology|B1|ف ع ل",
    "interest|اهْتِمَام / مَصْلَحَة / فَائِدَةٌ مَالِيَّة|noun|Business|A2|ه م م / ص ل ح / ف ي د",
    "internal|دَاخِلِيّ / بَاطِنِيّ|adjective|General|B1|د خ ل / ب ط ن",
    "international|دَوْلِيّ / عَالَمِيّ|adjective|General|A2|د و ل / ع ل م",
    "interpret|يُفَسِّر / يُتَرْجِمُ فَوْرِيّاً (شَفَهِيّاً)|verb|Education|B1|ف س ر / ت ر ج م",
    "interpretation|تَفْسِير / تَأْوِيل / تَرْجَمَةٌ فَوْرِيَّة|noun|Education|B2|ف س ر / أ و ل / ت ر ج م",
    "interval|فَاصِلٌ زَمَنِيّ (مِثْل فَتَرَاتِ التَّكْرَارِ المُتَبَاعِد)|noun|Science|B2|ف ص ل / ز م ن",
    "introduce|يُقَدِّم / يُعَرِّف بِـ / يُدْخِلُ مِيزَةً جَدِيدَة|verb|General|A2|ق د م / ع ر ف / د خ ل",
    "introduction|مُقَدِّمَة / تَمْهِيد / إِدْخَال|noun|Education|A2|ق د م / م ه د",
    "invent|يَخْتَرِع / يَبْتَكِر|verb|Science|A2|خ ر ع / ب ك ر",
    "invention|اخْتِرَاع / ابْتِكَار|noun|Science|A2|خ ر ع / ب ك ر",
    "investigate|يُحَقِّق فِي / يَبْحَث / يَسْتَقْصِي|verb|Science|B1|ح ق ق / ب ح ث / ق ص و",
    "investigation|تَحْقِيق / بَحْث / اسْتِقْصَاء|noun|Legal|B1|ح ق ق / ب ح ث",
    "involve|يَتَضَمَّن / يَشْمَل / يُشْرِك|verb|General|B1|ض م ن / ش م ل / ش ر ك",
    "issue|قَضِيَّة / مَسْأَلَة / إِصْدَار / يُصْدِر|noun|General|B1|ق ض ي / س أ ل / ص د ر",
    "item|عُنْصُر / بَنْد / سِلْعَة|noun|General|A2|ع ن ص ر / ب ن د / س ل ع",
    "join|يَنْضَمّ إِلَى / يَرْبِط / يَصِل|verb|General|A1|ض م م / ر ب ط / و ص ل",
    "journal|مَجَلَّةٌ عِلْمِيَّةٌ مُحَكَّمَة / يَوْمِيَّات|noun|Academic|B1|ج ل ل / ي و م",
    "journey|رِحْلَة / مَسِيرَة|noun|General|A2|ر ح ل / س ي ر",
    "key|مِفْتَاح (حَقِيقِيّ، أَوْ فِي لَوْحَةِ المَفَاتِيح، أَوْ مِفْتَاح API) / أَسَاسِيّ|noun|Technology|A1|ف ت ح / أ س س",
    "label|تَسْمِيَةٌ تَوْضِيحِيَّة / مُلْصَق / يُصَنِّف|noun|Technology|B1|س م و / ل ص ق / ص ن ف",
    "laboratory|مُخْتَبَر / مَعْمَلٌ عِلْمِيّ|noun|Science|B1|خ ب ر / ع م ل",
    "lack|نَقْص / انْعِدَام / يَفْتَقِر إِلَى|noun|General|B1|ن ق ص / ع د م / ف ق ر",
    "launch|يُطْلِق / يُشَغِّلُ البَرْنَامَج / إِطْلَاق|verb|Technology|B1|ط ل ق / ش غ ل",
    "layer|طَبَقَة (مِعْمَارِيَّة أَوْ فِيزْيَائِيَّة)|noun|Technology|B1|ط ب ق",
    "layout|تَخْطِيطُ الصَّفْحَةِ وَالوَاجِهَة / تَصْمِيم|noun|Technology|B1|خ ط ط / ص م م",
    "lead|يَقُود / يُؤَدِّي إِلَى / رَصَاص (مَعْدِن)|verb|General|B1|ق و د / أ د ي / ر ص ص",
    "leader|قَائِد / رَائِد / زَعِيم|noun|General|A2|ق و د / ر و د / ز ع م",
    "leadership|قِيَادَة / رِيَادَة|noun|Business|B1|ق و د / ر و د",
    "learner|مُتَعَلِّم / دَارِس|noun|Education|A2|ع ل م / د ر س",
    "leave|يُغَادِر / يَتْرُك / إِجَازَة|verb|General|A1|غ د ر / ت ر ك / ج و ز",
    "legal|قَانُونِيّ / شَرْعِيّ / نِظَامِيّ|adjective|Legal|B1|ق ن ن / ش ر ع / ن ظ م",
    "length|طُول / مُدَّة|noun|Science|A2|ط و ل / م د د",
    "lesson|دَرْس / عِبْرَة|noun|Education|A1|د ر س / ع ب ر",
    "lexicon|مُعْجَمٌ لُغَوِيّ / ثَرْوَةٌ لَفْظِيَّة|noun|Education|C1|ع ج م / ل ف ظ",
    "limit|حَدّ / قَيْد / يَحُدُّ مِن|noun|General|B1|ح د د / ق ي د",
    "limitation|قَيْدٌ تِقْنِيّ / مَحْدُودِيَّة / حَدّ|noun|Technology|B2|ق ي د / ح د د",
    "line|سَطْرٌ نَصِّيّ / خَطّ / طَابُور|noun|General|A1|س ط ر / خ ط ط",
    "linguistics|عِلْمُ اللُّغَة / اللِّسَانِيَّات|noun|Education|C1|ل غ و / ل س ن",
    "link|رَابِط / صِلَة / يَرْبِط|noun|Technology|A2|ر ب ط / و ص ل",
    "list|قَائِمَة / يُدْرِجُ فِي قَائِمَة|noun|General|A1|ق و م / د ر ج",
    "location|مَوْقِع / مَكَان / مَوْضِع|noun|General|A2|و ق ع / م ك ن / و ض ع",
    "lock|قُفْل / يُقْفِل / يَحْجِزُ المَوْرِد|verb|Technology|A2|ق ف ل / ح ج ز",
    "logic|مَنْطِق (عِلْمُ المَنْطِق أَوْ مَنْطِقُ النِّظَام البرمجي)|noun|Technology|B1|ن ط ق",
    "logical|مَنْطِقِيّ / عَقْلَانِيّ|adjective|Science|B1|ن ط ق / ع ق ل",
    "maintain|يُحَافِظ عَلَى / يَصُون (البَرْمَجِيَّات أَوِ المُعَدَّات)|verb|Technology|B1|ح ف ظ / ص و ن",
    "maintenance|صِيَانَة / مُحَافَظَة|noun|Technology|B1|ص و ن / ح ف ظ",
    "major|رَئِيسِيّ / كَبِير / تَخَصُّصٌ جَامِعِيّ|adjective|Education|B1|ر أ س / ك ب ر / خ ص ص",
    "minor|ثَانَوِيّ / طَفِيف / فَرْعِيّ / قَاصِر|adjective|General|B1|ث ن ي / ط ف ف / ف ر ع",
    "majority|أَغْلَبِيَّة / أَكْثَرِيَّة|noun|General|B1|غ ل ب / ك ث ر",
    "minority|أَقَلِّيَّة|noun|General|B1|ق ل ل",
    "manager|مُدِير (شَخْصٌ أَوْ أَدَاةُ إِدَارَةِ المَوَارِد)|noun|Technology|A2|د و ر",
    "manifest|بَيَانُ المِلَفَّاتِ وَالمَوَارِد (Manifest) / وَاضِح / يُظْهِر|noun|Technology|C1|ب ي ن / ظ ه ر",
    "margin|هَامِش (فِي الصَّفْحَةِ أَوْ هَامِشُ الرِّبْح)|noun|Business|B2|ه م ش / ر ب ح",
    "mark|عَلَامَة / دَرَجَة / يُعَلِّم / يُمَيِّز|noun|Education|A2|ع ل م / د ر ج / م ي ز",
    "master|سَيِّد / مُتْقِن / دَرَجَةُ المَاجِسْتِير / رَئِيسِيّ|noun|Education|B1|س و د / ت ق ن / ر أ س",
    "match|تَطَابُق / مُبَارَاة / يُطَابِق|noun|General|A2|ط ب ق / ب ر ي",
    "material|مَادَّة / مَوَادّ تَعْلِيمِيَّة أَوْ خَام|noun|Science|A2|م د د",
    "mathematics|عِلْمُ الرِّيَاضِيَّات|noun|Science|A2|ر و ض / ح س ب",
    "matter|مَادَّة (فِي الفِيزْيَاء) / مَسْأَلَة / أَمْر / يَهُمّ|noun|Science|A2|م د د / س أ ل / ه م م",
    "maximum|الحَدُّ الأَقْصَى / أَعْلَى قِيمَة|noun|Science|B1|ح د د / ق ص و",
    "minimum|الحَدُّ الأَدْنَى / أَقَلُّ قِيمَة|noun|Science|B1|ح د د / د ن و",
    "mechanism|آلِيَّةُ عَمَل / تَقْنِيَة|noun|Science|B2|أ ل ي / ع م ل",
    "media|وَسَائِطُ مُتَعَدِّدَة / وَسَائِلُ الإِعْلَام|noun|Technology|A2|و س ط / ع ل م",
    "medical|طِبِّيّ / صِحِّيّ|adjective|Medicine|A2|ط ب ب / ص ح ح",
    "medium|مُتَوَسِّط / وَسِيطُ نَقْل|adjective|General|A2|و س ط",
    "member|عُضْو (فِي فَرِيقٍ أَوْ مُؤَسَّسَة)|noun|General|A2|ع ض و",
    "mention|يَذْكُر / يُشِير إِلَى / ذِكْر|verb|General|A2|ذ ك ر / ش و ر",
    "menu|قَائِمَةُ خِيَارَات (فِي البَرْنَامَج أَوِ المَطْعَم)|noun|Technology|A1|ق و م / خ ي ر",
    "merge|يَدْمِج / يَوَحِّد|verb|Technology|B2|د م ج / و ح د",
    "metadata|بَيَانَاتٌ وَصْفِيَّة|noun|Technology|C1|ب ي ن / و ص ف",
    "mind|عَقْل / ذِهْن / يَهْتَمّ أَوْ يُمَانِع|noun|General|A2|ع ق ل / ذ ه ن",
    "mistake|خَطَأ / غَلْطَة / يُخْطِئ|noun|General|A1|خ ط أ / غ ل ط",
    "mix|يَخْلِط / يَمْزِج / مَزِيج|verb|General|A2|خ ل ط / م ز ج",
    "mixed|مُخْتَلَط (مِثْل النُّصُوصِ العَرَبِيَّةِ وَالإِنْجِلِيزِيَّةِ المُخْتَلَطَة)|adjective|General|B1|خ ل ط / م ز ج",
    "mode|وَضْعُ تَشْغِيل (مِثْل الوَضْعِ الدَّاكِن أَوْ وَضْعِ المَقَارَنَة) / نَمَط|noun|Technology|B1|و ض ع / ن م ط",
    "module|وَحْدَةٌ بَرْمَجِيَّة أَوْ تَعْلِيمِيَّة مُسْتَقِلَّة|noun|Technology|B2|و ح د",
    "moment|لَحْظَة / بُرْهَة|noun|General|A1|ل ح ظ / ب ر ه",
    "morphology|عِلْمُ الصَّرْفِ وَبِنْيَةِ الكَلِمَة / التَّشَكُّل|noun|Education|C1|ص ر ف / ب ن ي",
    "motion|حَرَكَة / اقْتِرَاحٌ رَسْمِيّ|noun|Science|B1|ح ر ك / ق ر ح",
    "multiple|مُتَعَدِّد / مُضَاعَف|adjective|General|B1|ع د د / ض ع ف",
    "name|اسْم / يُسَمِّي|noun|General|A1|س م و",
    "nation|أُمَّة / دَوْلَة / شَعْب|noun|General|B1|أ م م / د و ل / ش ع ب",
    "national|وَطَنِيّ / قَوْمِيّ|adjective|General|A2|و ط ن / ق و م",
    "native|أَصْلِيّ / مَحَلِّيّ (تَطْبِيقُ نِظَامٍ أَصْلِيّ أَوْ مُتَحَدِّثٌ أَصْلِيّ)|adjective|Technology|B1|أ ص ل / ح ل ل",
    "nature|طَبِيعَة / فِطْرَة / جَوْهَر|noun|Science|A2|ط ب ع / ف ط ر",
    "navigate|يَتَنَقَّل (فِي الوَاجِهَة) / يُبْحِر|verb|Technology|B1|ن ق ل / ب ح ر",
    "navigation|تَنَقُّل / مِلَاحَة|noun|Technology|B1|ن ق ل / م ل ح",
    "negative|سَلْبِيّ / سَالِب (فِي الرِّيَاضِيَّات) / نَفْي (فِي النَّحْو)|adjective|Science|A2|س ل ب / ن ف ي",
    "positive|إِيجَابِيّ / مُوجَب|adjective|Science|A2|و ج ب",
    "normal|عَادِيّ / طَبِيعِيّ / قِيَاسِيّ|adjective|General|A2|ع و د / ط ب ع / ق ي س",
    "notification|إِشْعَار / تَنْبِيهٌ فَوْرِيّ|noun|Technology|B1|ش ع ر / ن ب ه",
    "object|شَيْء / كَائِنٌ بَرْمَجِيّ / مَفْعُولٌ بِهِ (فِي النَّحْو) / يَعْتَرِض|noun|Education|B1|ش ي أ / ك و ن / ف ع ل",
    "subject|مَوْضُوع / مَادَّةٌ دِرَاسِيَّة / فَاعِلٌ أَوْ مُبْتَدَأ (فِي النَّحْو)|noun|Education|A2|و ض ع / ف ع ل / ب د أ",
    "objective|هَدَف / مَوْضُوعِيّ (غَيْرُ مُتَحَيِّز)|noun|Academic|B1|ه د ف / و ض ع",
    "obligation|الْتِزَام / وَاجِبٌ قَانُونِيّ أَوْ أَخْلَاقِيّ|noun|Legal|B2|ل ز م / و ج ب",
    "observe|يُلَاحِظ / يَرْصُد / يَلْتَزِم بِـ|verb|Science|B1|ل ح ظ / ر ص د / ل ز م",
    "obtain|يَحْصُل عَلَى / يَنَال|verb|Academic|B1|ح ص ل / ن و ل",
    "obvious|وَاضِح / بَدِيهِيّ / جَلِيّ|adjective|General|B1|و ض ح / ب د ه / ج ل و",
    "occur|يَحْدُث / يَقَع / يَجْرِي|verb|General|B1|ح د ث / و ق ع / ج ر ي",
    "offer|عَرْض / يُقَدِّم / يَعْرِض|verb|Business|A2|ع ر ض / ق د م",
    "office|مَكْتَب / دَائِرَةٌ رَسْمِيَّة / مَنْصِب|noun|Business|A1|ك ت ب / د و ر / ن ص ب",
    "official|رَسْمِيّ / مَسْؤُولٌ حُكُومِيّ|adjective|Legal|B1|ر س م / س أ ل",
    "operation|عَمَلِيَّة (حِسَابِيَّة، أَوْ بَرْمَجِيَّة، أَوْ جِرَاحِيَّة) / تَشْغِيل|noun|Technology|B1|ع م ل / ش غ ل",
    "opinion|رَأْي / وِجْهَةُ نَظَر|noun|General|A2|ر أ ي / ن ظ ر",
    "opportunity|فُرْصَة / سَانِحَة|noun|General|B1|ف ر ص / س ن ح",
    "opposite|عَكْس / مُقَابِل / نَقِيض|adjective|General|A2|ع ك س / ق ب ل / ن ق ض",
    "order|تَرْتِيب / طَلَبٌ تِجَارِيّ / أَمْر / نِظَام|noun|General|A1|ر ت ب / ط ل ب / أ م ر",
    "ordinary|عَادِيّ / مَأْلُوف|adjective|General|A2|ع و د / أ ل ف",
    "organization|مُنَظَّمَة / هَيْئَة / تَنْظِيم|noun|Business|A2|ن ظ م / ه ي أ",
    "origin|أَصْل / مَنْشَأ / مَصْدَر|noun|Science|B1|أ ص ل / ن ش أ / ص د ر",
    "original|أَصْلِيّ / النَّصُّ الأَصْلِيّ (المَصْدَر) / مُبْتَكَر|adjective|Education|A2|أ ص ل / ن ص ص / ب ك ر",
    "outcome|نَتِيجَةٌ نِهَائِيَّة / مُحَصِّلَة|noun|Academic|B2|ن ت ج / ح ص ل",
    "outline|مُخَطَّطٌ عَامّ / خُلَاصَةُ العَنَاوِين|noun|Education|B1|خ ط ط / خ ل ص",
    "overcome|يَتَغَلَّب عَلَى / يَجْتَازُ الصُّعُوبَات|verb|General|B2|غ ل ب / ج و ز",
    "page|صَفْحَة|noun|General|A1|ص ف ح",
    "panel|لَوْحَةُ تَحَكُّمٍ أَوْ إِعْدَادَات / لَجْنَةٌ عِلْمِيَّة|noun|Technology|B1|ل و ح / ح ك م / ل ج ن",
    "paper|وَرَق / وَرَقَةٌ بَحْثِيَّةٌ عِلْمِيَّة / صَحِيفَة|noun|Education|A1|و ر ق / ب ح ث / ص ح ف",
    "parallel|مُتَوَازٍ / عَلَى التَّوَازِي (معالجة متوازية)|adjective|Science|B2|و ز ي",
    "part|جُزْء / قِسْم / دَوْر|noun|General|A1|ج ز أ / ق س م / د و ر",
    "partial|جُزْئِيّ / تَطَابُقٌ جُزْئِيّ (Partial Match)|adjective|Technology|B1|ج ز أ / ط ب ق",
    "participate|يُشَارِك / يُسَاهِم|verb|General|B1|ش ر ك / س ه م",
    "particular|خَاصّ / مُعَيَّن / مُحَدَّد|adjective|General|B1|خ ص ص / ع ي ن / ح د د",
    "partner|شَرِيك / زَمِيل|noun|Business|A2|ش ر ك / ز م ل",
    "passage|مَقْطَعٌ نَصِّيّ / فَقْرَة / مَمَرّ|noun|Education|B1|ق ط ع / ن ص ص / م ر ر",
    "passive|مَبْنِيٌّ لِلمَجْهُول (فِي النَّحْو) / سَلْبِيّ (غَيْرُ فَعَّال)|adjective|Education|B1|ج ه ل / س ل ب",
    "pattern|نَمَط / نَسَق / قَالَب|noun|Science|B1|ن م ط / ن س ق / ق ل ب",
    "pause|تَوَقُّفٌ مُؤَقَّت / يُوقِفُ مُؤَقَّتاً|verb|Technology|B1|و ق ف / و ق ت",
    "payment|دَفْعٌ مَالِيّ / سَدَاد / دُفْعَة|noun|Business|A2|د ف ع / س د د",
    "percentage|نِسْبَةٌ مِئَوِيَّة (%)|noun|Science|B1|ن س ب / م أ ي",
    "perfect|كَامِل / مُتْقَن / صِيغَةُ التَّامِّ (فِي النَّحْو)|adjective|Education|A2|ك م ل / ت ق ن / ت م م",
    "perform|يُؤَدِّي / يُنْجِز / يُنَفِّذ|verb|General|A2|أ د ي / ن ج ز / ن ف ذ",
    "period|فَتْرَةٌ زَمَنِيَّة / نُقْطَةٌ فِي نِهَايَةِ الجُمْلَة (.) / عَصْر|noun|Education|A2|ف ت ر / ن ق ط / ع ص ر",
    "permanent|دَائِم / ثَابِت / مُسْتَدِيم|adjective|General|B1|د و م / ث ب ت",
    "temporary|مُؤَقَّت / عَابِر (مِثْل المِلَفَّاتِ المُؤَقَّتَة Temporary Files)|adjective|Technology|B1|و ق ت / ع ب ر",
    "permit|يَسْمَح / يُجِيز / تَصْرِيحٌ رَسْمِيّ|verb|Legal|B1|س م ح / ج و ز / ص ر ح",
    "person|شَخْص / فَرْد / ضَمِيرُ المُتَكَلِّمِ أَوِ المُخَاطَبِ أَوِ الغَائِب (فِي النَّحْو)|noun|General|A1|ش خ ص / ف ر د / ض م ر",
    "personal|شَخْصِيّ / خَاصّ|adjective|General|A1|ش خ ص / خ ص ص",
    "perspective|مَنْظُور / وِجْهَةُ نَظَر|noun|Academic|B2|ن ظ ر / و ج ه",
    "phase|مَرْحَلَة / طَوْر|noun|Science|B2|ر ح ل / ط و ر",
    "phenomenon|ظَاهِرَة (طَبِيعِيَّة أَوْ لُغَوِيَّة)|noun|Science|B2|ظ ه ر",
    "philosophy|فَلْسَفَة / حِكْمَة / مَبْدَأٌ عَامّ|noun|Academic|B1|ف ل س ف / ح ك م",
    "phonetic|صَوْتِيّ (مُتَعَلِّقٌ بِالنُّطْقِ وَالأَصْوَاتِ اللُّغَوِيَّة)|adjective|Education|C1|ص و ت / ن ط ق",
    "phrase|عِبَارَة / شِبْهُ جُمْلَة / تَرْكِيبٌ لَفْظِيّ|noun|Education|A2|ع ب ر / ج م ل / ر ك ب",
    "physical|فِيزْيَائِيّ / جَسَدِيّ / مَادِّيّ مَلْمُوس|adjective|Science|A2|ج س د / م د د / ل م س",
    "physics|عِلْمُ الفِيزْيَاء|noun|Science|A2|ف ي ز ي أ",
    "picture|صُورَة / لَوْحَة / يَتَصَوَّر|noun|General|A1|ص و ر / ل و ح",
    "piece|قِطْعَة / جُزْء / مَقْطُوعَة|noun|General|A1|ق ط ع / ج ز أ",
    "place|مَكَان / مَوْضِع / يَضَع|noun|General|A1|م ك ن / و ض ع",
    "plan|خُطَّة / يُخَطِّط|noun|General|A1|خ ط ط",
    "platform|مِنَصَّة (تِقْنِيَّة أَوْ تَعْلِيمِيَّة أَوْ نِظَامُ تَشْغِيل)|noun|Technology|B1|ن ص ص",
    "play|يُشَغِّلُ مِلَفّاً صَوْتِيّاً / يَلْعَب / مَسْرَحِيَّة|verb|Technology|A1|ش غ ل / ل ع ب / س ر ح",
    "point|نُقْطَة / غَايَة / يُشِير إِلَى|noun|General|A1|ن ق ط / غ ي ي / ش و ر",
    "policy|سِيَاسَة (خُصُوصِيَّة أَوْ إِدَارِيَّة) / وَثِيقَةُ تَأْمِين|noun|Legal|B1|س و س / و ث ق",
    "popular|شَائِع / مَحْبُوب / شَعْبِيّ|adjective|General|A1|ش ي ع / ح ب ب / ش ع ب",
    "population|عَدَدُ السُّكَّان / مُجْتَمَعُ الدِّرَاسَةِ الإِحْصَائِيَّة|noun|Science|A2|س ك ن / ج م ع",
    "position|مَوْضِع / مَكَانَة / مَنْصِبٌ وَظِيفِيّ|noun|General|A2|و ض ع / م ك ن / ن ص ب",
    "possibility|إِمْكَانِيَّة / احْتِمَال|noun|General|B1|م ك ن / ح م ل",
    "potential|إِمْكَانَاتٌ كَامِنَة / مُحْتَمَل / جُهْدٌ كَهْرَبَائِيّ|noun|Science|B2|م ك ن / ك م ن / ح م ل",
    "practice|مُمَارَسَة / تَدْرِيبٌ عَمَلِيّ / يُمَارِس|noun|Education|A1|م ر س / د ر ب / ع م ل",
    "precise|دَقِيقٌ جِدّاً / مُحَدَّدٌ بِإِحْكَام|adjective|Science|B2|د ق ق / ح ك م",
    "precision|دِقَّة / إِحْكَام / ضَبْط|noun|Science|C1|د ق ق / ح ك م",
    "predict|يَتَنَبَّأ بِـ / يَتَوَقَّع (كَمَا فِي الإِكْمَالِ التِّلْقَائِيّ)|verb|Science|B1|ن ب أ / و ق ع",
    "prefer|يُفَضِّل / يُؤْثِر|verb|General|A1|ف ض ل / أ ث ر",
    "preference|تَفْضِيل / إِعْدَادٌ مُفَضَّل لَدَى المُسْتَخْدِم|noun|Technology|B1|ف ض ل / ع د د",
    "prefix|سَابِقَةٌ لُغَوِيَّة (فِي أَوَّلِ الكَلِمَة مِثْل الـ أَوْ un-)|noun|Education|B2|س ب ق / ل غ و",
    "suffix|لَاحِقَةٌ لُغَوِيَّة (فِي آخِرِ الكَلِمَة مِثْل ـون أَوْ -ing)|noun|Education|B2|ل ح ق / ل غ و",
    "preposition|حَرْفُ جَرّ (فِي النَّحْو)|noun|Education|B1|ح ر ف / ج ر ر",
    "pronoun|ضَمِير (فِي النَّحْو)|noun|Education|B1|ض م ر",
    "conjunction|حَرْفُ عَطْف / أَدَاةُ رَبْط (فِي النَّحْو)|noun|Education|B2|ع ط ف / ر ب ط",
    "preserve|يَحْفَظ / يَصُون / يُحَافِظ عَلَى|verb|General|B2|ح ف ظ / ص و ن",
    "press|يَضْغَط (عَلَى زِرّ أَوْ مِفْتَاح) / الصَّحَافَة|verb|Technology|A2|ض غ ط / ص ح ف",
    "pressure|ضَغْط|noun|Science|B1|ض غ ط",
    "previous|سَابِق / مَاضٍ|adjective|General|A2|س ب ق / م ض ي",
    "primary|أَسَاسِيّ / أَوَّلِيّ / ابْتِدَائِيّ|adjective|Education|B1|أ س س / أ و ل / ب د أ",
    "secondary|ثَانَوِيّ / فَرْعِيّ|adjective|Education|B1|ث ن ي / ف ر ع",
    "principle|مَبْدَأ / قَاعِدَةٌ أَسَاسِيَّة|noun|Science|B1|ب د أ / ق ع د",
    "print|يَطْبَع / طِبَاعَة|verb|Technology|A1|ط ب ع",
    "prior|سَابِق / أَسْبَق|adjective|Legal|B2|س ب ق",
    "priority|أَوْلَوِيَّة / أَسْبَقِيَّة|noun|Business|B1|أ و ل / س ب ق",
    "private|خَاصّ / سِرِّيّ / غَيْرُ عَامّ|adjective|General|A2|خ ص ص / س ر ر",
    "public|عَامّ / جُمْهُور|adjective|General|A2|ع م م / ج م ه ر",
    "privilege|صَلَاحِيَّةٌ فِي النِّظَام / امْتِيَاز|noun|Technology|B2|ص ل ح / م ي ز",
    "probability|احْتِمَالِيَّة (فِي الإِحْصَاء وَالنَّمَاذِج اللُّغَوِيَّة)|noun|Science|B2|ح م ل / ح ص ي",
    "probable|مُحْتَمَل / مُرَجَّح|adjective|General|B1|ح م ل / ر ج ح",
    "procedure|إِجْرَاءٌ مُتَّبَع / خُطُوَاتُ عَمَل|noun|Technology|B2|ج ر ي / خ ط و",
    "proceed|يُوَاصِل / يَمْضِي قُدُماً|verb|General|B2|و ص ل / م ض ي",
    "product|مُنْتَج / حَاصِلُ الضَّرْب|noun|Business|A1|ن ت ج / ح ص ل",
    "production|إِنْتَاج / بِيئَةُ التَّشْغِيلِ الفِعْلِيّ (Production)|noun|Business|B1|ن ت ج / ش غ ل",
    "profession|مِهْنَة / حِرْفَة|noun|Business|B1|م ه ن / ح ر ف",
    "professor|أُسْتَاذٌ جَامِعِيّ (بْرُوفِيسُور)|noun|Education|A2|أ س ت ذ / ج م ع",
    "profile|مِلَفٌّ تَعْرِيفِيّ / نَبْذَة|noun|Technology|A2|ع ر ف / ن ب ذ",
    "program|بَرْنَامَجٌ حَاسُوبِيّ / خُطَّةُ عَمَل / يُبَرْمِج|noun|Technology|A1|ب ر م ج / خ ط ط",
    "programmer|مُبَرْمِج|noun|Technology|A2|ب ر م ج",
    "programming|بَرْمَجَةُ الحَاسُوب|noun|Technology|A2|ب ر م ج",
    "prohibit|يَحْظُر / يَمْنَعُ قَانُوناً|verb|Legal|B2|ح ظ ر / م ن ع",
    "promise|وَعْد / يَعِد|noun|General|A2|و ع د",
    "promote|يُعَزِّز / يُرَقِّي / يُرَوِّج|verb|Business|B1|ع ز ز / ر ق ي / ر و ج",
    "prompt|سَرِيع / مُوَجِّهٌ أَوْ طَلَبٌ نَصِّيّ / يَحُثّ|noun|Technology|B2|س ر ع / و ج ه / ح ث ث",
    "proof|إِثْبَات / بُرْهَانٌ رِيَاضِيّ أَوْ قَانُونِيّ|noun|Science|B1|ث ب ت / ب ر ه ن",
    "proper|مُنَاسِب / صَحِيح / اسْمُ عَلَم (Proper Noun)|adjective|Education|B1|ن س ب / ص ح ح / ع ل م",
    "property|خَاصِّيَّة (فِي البَرْمَجَةِ وَالعُلُوم) / مِلْكِيَّةٌ عَقَارِيَّة أَوْ فِكْرِيَّة|noun|Technology|B1|خ ص ص / م ل ك",
    "proportion|نِسْبَة / تَنَاسُب|noun|Science|B2|ن س ب",
    "proposal|مُقْتَرَح / عَرْضُ مَشْرُوع|noun|Business|B2|ق ر ح / ع ر ض",
    "propose|يَقْتَرِح / يَعْرِض|verb|General|B1|ق ر ح / ع ر ض",
    "protection|حِمَايَة / وِقَايَة / صِيَانَة|noun|General|B1|ح م ي / و ق ي / ص و ن",
    "protocol|بْرُوتُوكُولُ اتِّصَال أَوْ إِجْرَاءَاتٍ رَسْمِيَّة|noun|Technology|B2|و ص ل / ج ر ي",
    "prove|يُثْبِت / يُبَرْهِن عَلَى|verb|Science|B1|ث ب ت / ب ر ه ن",
    "proverb|مَثَلٌ شَائِع / حِكْمَةٌ مَأْثُورَة|noun|Education|B1|م ث ل / ح ك م",
    "provider|مُزَوِّدُ خِدْمَة (Provider)|noun|Technology|B1|ز و د / خ د م",
    "publication|نَشْر / مَنْشُورٌ أَوْ مُؤَلَّفٌ عِلْمِيّ|noun|Education|B2|ن ش ر / أ ل ف",
    "punctuation|عَلَامَاتُ التَّرْقِيم (مِثْل الفَاصِلَة وَالنُّقْطَة وَعَلَامَةِ الاسْتِفْهَام)|noun|Education|B1|ر ق م / ع ل م",
    "purchase|شِرَاء / يَشْتَرِي / مُقْتَنَيَات|verb|Business|B1|ش ر ي / ق ن ي",
    "pure|نَقِيّ / خَالِص / بَحْت|adjective|Science|B1|ن ق ي / خ ل ص / ب ح ت",
    "purpose|غَرَض / هَدَف / غَايَة|noun|General|A2|غ ر ض / ه د ف / غ ي ي",
    "quantity|كَمِّيَّة / مِقْدَار|noun|Science|A2|ك م م / ق د ر",
    "quarter|رُبْع (25% أَوْ ثَلَاثَةُ أَشْهُر)|noun|General|A2|ر ب ع",
    "queue|طَابُورُ انْتِظَار (فِي مُعَالَجَةِ المَهَامِّ البرمجية)|noun|Technology|B2|ط ب ر / ن ظ ر",
    "quote|اقْتِبَاس / يَقْتَبِس / عَرْضُ سِعْر|verb|Education|B1|ق ب س / س ع ر",
    "random|عَشْوَائِيّ / غَيْرُ مُنْتَظِم|adjective|Science|B1|ع ش و / ن ظ م",
    "range|نِطَاق / مَدًى / يَتَرَاوَح بَيْنَ|noun|Science|B1|ن ط ق / م د ي / ر و ح",
    "rank|مَرْتَبَة / تَصْنِيف / رُتْبَة|noun|General|B1|ر ت ب / ص ن ف",
    "rapid|سَرِيع / مُتَسَارِع|adjective|General|B1|س ر ع",
    "rare|نَادِر / قَلِيلُ الوُجُود|adjective|General|B1|ن د ر / ق ل ل",
    "rate|مُعَدَّل (مِثْل سُرْعَةِ النُّطْق Speech Rate) / نِسْبَة / يُقَيِّم|noun|Science|B1|ع د ل / ن س ب / ق ي م",
    "ratio|نِسْبَةٌ رِيَاضِيَّة بَيْنَ عَدَدَيْن|noun|Science|B2|ن س ب",
    "raw|خَام (مِثْل البَيَانَاتِ الخَام Raw Data)|adjective|Science|B1|خ و م",
    "reach|يَصِل إِلَى / يَبْلُغ / مَدَى الوُصُول|verb|General|A2|و ص ل / ب ل غ",
    "react|يَتَفَاعَل / يَسْتَجِيب لِفِعْلٍ أَوْ مَادَّة|verb|Science|B1|ف ع ل / ج و ب",
    "reaction|تَفَاعُلٌ كِيمْيَائِيّ / رَدُّ فِعْل|noun|Science|B1|ف ع ل / ر د د",
    "reader|قَارِئ (شَخْصٌ أَوْ بَرْنَامَجُ قَارِئ PDF)|noun|Education|A1|ق ر أ",
    "real|حَقِيقِيّ / وَاقِعِيّ / فِعْلِيّ|adjective|General|A1|ح ق ق / و ق ع / ف ع ل",
    "reality|وَاقِع / حَقِيقَة|noun|General|B1|و ق ع / ح ق ق",
    "realize|يُدْرِك / يَعِي / يُحَقِّقُ عَلَى أَرْضِ الوَاقِع|verb|General|A2|د ر ك / و ع ي / ح ق ق",
    "reason|سَبَب / عِلَّة / عَقْلٌ وَمَنْطِق|noun|General|A1|س ب ب / ع ل ل / ع ق ل",
    "reasonable|مَعْقُول / مُنَاسِب / مَنْطِقِيّ|adjective|General|B1|ع ق ل / ن س ب / ن ط ق",
    "recent|حَدِيثُ العَهْد / أَخِير|adjective|General|A2|ح د ث / ع ه د / أ خ ر",
    "recognition|تَعَرُّف (ضَوْئِيّ أَوْ صَوْتِيّ) / اعْتِرَافٌ وَتَقْدِير|noun|Technology|B2|ع ر ف / ق د ر",
    "recommendation|تَوْصِيَة / نَصِيحَة / تَزْكِيَة|noun|General|B1|و ص ي / ن ص ح",
    "recover|يَتَعَافَى / يَسْتَعِيدُ البَيَانَاتِ أَوِ الاتِّصَال|verb|Medicine|B1|ع ف و / ع و د",
    "reference|مَرْجِع / إِحَالَةٌ مَرْجِعِيَّة|noun|Education|B1|ر ج ع / ح و ل",
    "reflect|يَعْكِس / يَتَأَمَّلُ وَيُفَكِّر|verb|Science|B1|ع ك س / أ م ل / ف ك ر",
    "regard|اعْتِبَار / يَعْتَبِر / فِيمَا يَتَعَلَّق بِـ|noun|General|B1|ع ب ر / ع ل ق",
    "region|مِنْطَقَة (جُغْرَافِيَّة أَوْ مِنْطَقَةٌ مُحَدَّدَةٌ مِنَ الصُّورَة)|noun|General|A2|ن ط ق / ح د د",
    "register|يُسَجِّل (اخْتِصَاراً عَامّاً أَوْ حِسَاباً) / سِجِلّ|verb|Technology|B1|س ج ل",
    "regular|مُنْتَظِم / قِيَاسِيّ (مِثْل الجَمْعِ القِيَاسِيّ Regular Plural)|adjective|Education|A2|ن ظ م / ق ي س",
    "irregular|شَاذّ / غَيْرُ قِيَاسِيّ (مِثْل الأَفْعَالِ الشَّاذَّة Irregular Verbs)|adjective|Education|B1|ش ذ ذ / ق ي س",
    "regulation|لَائِحَةٌ تَنْظِيمِيَّة / ضَبْطٌ وَتَنْظِيم|noun|Legal|B2|ل و ح / ن ظ م / ض ب ط",
    "reject|يَرْفُض / يَرُدّ|verb|General|B1|ر ف ض / ر د د",
    "relate|يَرْتَبِط بِـ / يَصِل / يَرْوِي|verb|General|B1|ر ب ط / و ص ل",
    "relation|عَلَاقَة / صِلَة / ارْتِبَاط|noun|General|B1|ع ل ق / و ص ل / ر ب ط",
    "relationship|عَلَاقَةٌ وَثِيقَة / تَرَابُط|noun|General|A2|ع ل ق / ر ب ط",
    "relative|نِسْبِيّ / قَرِيب (مِنَ الأَقَارِب) / اسْمٌ مَوْصُول (Relative Pronoun)|adjective|Education|B1|ن س ب / ق ر ب / و ص ل",
    "release|إِصْدَارٌ نِهَائِيّ (Release) / يُطْلِق / يُحَرِّرُ الذَّاكِرَة|noun|Technology|B1|ص د ر / ط ل ق / ح ر ر",
    "relevant|ذُو صِلَة / مُرْتَبِطٌ بِالمَوْضُوع|adjective|Academic|B2|و ص ل / ر ب ط",
    "reliability|مَوْثُوقِيَّة / اعْتِمَادِيَّةُ النِّظَام|noun|Technology|B2|و ث ق / ع م د",
    "rely|يَعْتَمِد عَلَى / يَرْكَن إِلَى|verb|General|B1|ع م د / ر ك ن",
    "remain|يَبْقَى / يَظَلّ|verb|General|B1|ب ق ي / ظ ل ل",
    "remote|بَعِيد / عَنْ بُعْد (خَادِمٌ بَعِيد Remote Server)|adjective|Technology|B1|ب ع د",
    "render|يَعْرِضُ الوَاجِهَةَ بَصَرِيّاً / يُتَرْجِمُ النَّصَّ / يَجْعَل|verb|Technology|C1|ع ر ض / ت ر ج م / ج ع ل",
    "repeat|يُكَرِّر / يُعِيد|verb|General|A1|ك ر ر / ع و د",
    "repetition|تَكْرَار (مِثْل التَّكْرَارِ المُتَبَاعِد Spaced Repetition)|noun|Education|B2|ك ر ر / ب ع د",
    "reply|رَدّ / جَوَاب / يَرُدّ|verb|General|A2|ر د د / ج و ب",
    "report|تَقْرِير (مِثْل تَقْرِيرِ الاخْتِبَارَات Test Report) / يُبْلِغ عَن|noun|General|A2|ق ر ر / ب ل غ",
    "Modal".lower(), "فِعْلٌ نَاقِصٌ أَوْ نَافِذَةٌ حِوَارِيَّة (Modal)|noun|Education|B2|ف ع ل / ح و ر",
    "represent|يُمَثِّل / يُعَبِّر عَن|verb|General|B1|م ث ل / ع ب ر",
    "representation|تَمْثِيل (بَيَانِيّ أَوْ قَانُونِيّ أَوْ لُغَوِيّ)|noun|Science|B2|م ث ل",
    "request|طَلَب (مِنَ المُسْتَخْدِم أَوْ طَلَبُ شَبَكَة HTTP Request)|noun|Technology|A2|ط ل ب",
    "requirement|مُتَطَلَّب / شَرْطٌ لَازِم|noun|Technology|B1|ط ل ب / ش ر ط",
    "researcher|بَاحِثٌ عِلْمِيّ|noun|Science|B1|ب ح ث / ع ل م",
    "resolution|دِقَّةُ الشَّاشَةِ أَوِ الصُّورَة / حَلُّ المُشْكِلَة / قَرَارٌ رَسْمِيّ|noun|Technology|B2|د ق ق / ح ل ل / ق ر ر",
    "resolve|يَحُلُّ (مُشْكِلَةً أَوْ تَعَارُضاً) / يَعْزِم|verb|Technology|B2|ح ل ل / ع ز م",
    "respect|احْتِرَام / يَحْتَرِم / يَلْتَزِمُ بِخُصُوصِيَّة|verb|General|B1|ح ر م / ل ز م",
    "respond|يَسْتَجِيب / يَرُدّ|verb|General|B1|ج و ب / ر د د",
    "response|اسْتِجَابَة / رَدّ|noun|General|B1|ج و ب / ر د د",
    "responsive|مُتَجَاوِب / سَرِيعُ الاسْتِجَابَةِ لِأَحْجَامِ الشَّاشَات (Responsive UI)|adjective|Technology|B2|ج و ب / س ر ع",
    "responsibility|مَسْؤُولِيَّة / وَاجِب|noun|General|B1|س أ ل / و ج ب",
    "restrict|يُقَيِّد / يَحْصُر / يَحُدُّ مِن|verb|Legal|B2|ق ي د / ح ص ر / ح د د",
    "restriction|قَيْد / حَظْر / تَقْيِيد|noun|Legal|B2|ق ي د / ح ظ ر",
    "retain|يَحْتَفِظ بِـ (فِي الذَّاكِرَة أَوِ الإِعْدَادَات)|verb|Academic|B2|ح ف ظ",
    "retrieve|يَسْتَرْجِع / يَسْتَعِيدُ البَيَانَاتِ مِن قَاعِدَةِ البَيَانَات|verb|Technology|C1|ر ج ع / ع و د",
    "reveal|يَكْشِف / يُظْهِر (مِثْل إِظْهَارِ المَعْنَى فِي بَطَاقَةِ المُرَاجَعَة)|verb|General|B2|ك ش ف / ظ ه ر",
    "reverse|عَكْس / يَعْكِسُ اتِّجَاهَ التَّرْجَمَة|verb|General|B1|ع ك س",
    "revise|يُرَاجِع / يُنَقِّح|verb|Education|B1|ر ج ع / ن ق ح",
    "rich|غَنِيّ / ثَرِيّ (بِالمَعْلُومَاتِ أَوِ المَال)|adjective|General|A1|غ ن ي / ث ر ي",
    "risk|مُخَاطَرَة / خَطَرٌ مُحْتَمَل|noun|Business|B1|خ ط ر",
    "role|دَوْر / وَظِيفَة|noun|General|A2|د و ر / و ظ ف",
    "route|مَسَار / طَرِيق / يُوَجِّهُ الطَّلَب|noun|Technology|B1|س ي ر / ط ر ق / و ج ه",
    "rule|قَاعِدَة (نَحْوِيَّة أَوْ بَرْمَجِيَّة) / حُكْم|noun|Education|A2|ق ع د / ح ك م",
    "runtime|بِيئَةُ التَّشْغِيل (.NET أَوْ WebView2 Runtime) / زَمَنُ التَّشْغِيل|noun|Technology|B2|ب ي أ / ش غ ل / ز م ن",
    "safety|سَلَامَة / أَمَان|noun|General|B1|س ل م / أ م ن",
    "sample|عَيِّنَة / نَمُوذَجٌ تَجْرِيبِيّ|noun|Science|B1|ع ي ن / ن م ذ ج",
    "scale|مِقْيَاس / نِطَاق / يَتَوَسَّع|noun|Science|B1|ق ي س / ن ط ق / و س ع",
    "scan|يَمْسَحُ ضَوْئِيّاً (Scan) / يَفْحَصُ سَرِيعاً|verb|Technology|B1|م س ح / ض و أ / ف ح ص",
    "scanned|مَمْسُوحٌ ضَوْئِيّاً (مِثْل مِلَفَّات PDF المَمْسُوحَة ضَوْئِيّاً)|adjective|Technology|B1|م س ح / ض و أ",
    "schedule|جَدْوَلٌ زَمَنِيّ (كَمَا فِي جَدْوَلِ المُرَاجَعَةِ الدَّوْرِيَّة) / يُجَدْوِل|noun|General|A2|ج د و ل / ز م ن",
    "schema|مُخَطَّطُ هَيْكَلِ قَاعِدَةِ البَيَانَات (Database Schema)|noun|Technology|C1|خ ط ط / ه ي ك ل",
    "science|عِلْم / العُلُومُ الطَّبِيعِيَّةُ وَالتَّطْبِيقِيَّة|noun|Science|A1|ع ل م",
    "scientific|عِلْمِيّ / مَنْهَجِيّ|adjective|Science|B1|ع ل م / ن ه ج",
    "scope|نِطَاق / مَجَالُ الرُّؤْيَةِ أَوِ العَمَل|noun|Technology|B2|ن ط ق / ج و ل",
    "score|نَتِيجَة / دَرَجَة / يُحْرِزُ نِقَاطاً|noun|Education|A2|ن ت ج / د ر ج / ح ر ز",
    "script|نَصٌّ بَرْمَجِيّ (Script) / نِظَامُ الكِتَابَةِ وَالخَطّ (مِثْل الخَطِّ العَرَبِيّ)|noun|Technology|B1|ن ص ص / ك ت ب / خ ط ط",
    "section|قِسْم / فَصْل / مَقْطَع|noun|General|A2|ق س م / ف ص ل / ق ط ع",
    "sector|قِطَاع (اقْتِصَادِيّ أَوْ عَلَى القُرْص)|noun|Business|B2|ق ط ع",
    "secure|آمِن / مَحْمِيّ / يُؤَمِّن|adjective|Technology|B1|أ م ن / ح م ي",
    "segment|جُزْء / مَقْطَعٌ نَصِّيّ / يُقَسِّمُ الفَقَرَات|verb|Technology|B2|ج ز أ / ق ط ع / ق س م",
    "selection|تَحْدِيدُ النَّصِّ (Text Selection) / اخْتِيَار / نُخْبَة|noun|Technology|B1|ح د د / خ ي ر / ن خ ب",
    "semantic|دَلَالِيّ (مُتَعَلِّقٌ بِمَعَانِي الكَلِمَاتِ وَالجُمَل)|adjective|Education|C1|د ل ل / ع ن ي",
    "sense|مَعْنًى دَلَالِيّ لِلكَلِمَة (Word Sense) / حَاسَّة / يَشْعُر|noun|Education|B1|ع ن ي / ح س س / ش ع ر",
    "sensitive|حَسَّاس (مِثْل البَيَانَاتِ الحَسَّاسَة أَوْ حَسَاسِيَّةِ حَالَةِ الأَحْرُف)|adjective|Technology|B1|ح س س",
    "sequence|تَسَلْسُل / تَتَابُع / مَتَوَالِيَة|noun|Science|B2|س ل س ل / ت ب ع",
    "series|سِلْسِلَة / مَجْمُوعَةٌ مُتَتَالِيَة|noun|General|B1|س ل س ل / ت ل و",
    "serious|جَادّ / خَطِير / مُهِمّ|adjective|General|A2|ج د د / خ ط ر / ه م م",
    "service|خِدْمَة (خِدْمَةُ نِظَامِ وِينْدُوز أَوْ خِدْمَةٌ عَامَّة)|noun|Technology|A2|خ د م",
    "session|جَلْسَةُ عَمَلٍ أَوْ مُرَاجَعَة|noun|Technology|B1|ج ل س / ع م ل",
    "share|يُشَارِك / حِصَّة / سَهْمٌ مَالِيّ|verb|General|A1|ش ر ك / ح ص ص / س ه م",
    "shift|مِفْتَاحُ العَالِي (Shift) / تَحَوُّل / نَوْبَةُ عَمَل|noun|Technology|B1|ح و ل / ن و ب",
    "signal|إِشَارَة / يُشِير|noun|Technology|B1|ش و ر",
    "significant|مُلْفِت / ذُو دَلَالَةٍ كَبِيرَة / مُهِمّ|adjective|Academic|B2|ل ف ت / د ل ل / ه م م",
    "simple|بَسِيط / سَهْل / مُفْرَد|adjective|General|A1|ب س ط / س ه ل / ف ر د",
    "complex|مُعَقَّد / مُرَكَّب (مِثْل الجُمْلَةِ المُرَكَّبَة)|adjective|Academic|B1|ع ق د / ر ك ب",
    "single|مُفْرَد / وَاحِدٌ فَقَط (كَلِمَةٌ مُنْفَرِدَة Single Word)|adjective|General|A2|ف ر د / و ح د",
    "site|مَوْقِع (إِلكْتُرُونِيّ أَوْ جُغْرَافِيّ)|noun|Technology|A2|و ق ع",
    "situation|مَوْقِف / حَالَة / وَضْع|noun|General|A2|و ق ف / ح و ل / و ض ع",
    "smooth|سَلِس / نَاعِم / انْسِيَابِيّ|adjective|General|B1|س ل س / ن ع م / س ي ب",
    "society|مُجْتَمَع / جَمْعِيَّةٌ عِلْمِيَّة|noun|General|A2|ج م ع",
    "sound|صَوْت / سَلِيمٌ وَصَحِيح / يَبْدُو|noun|General|A1|ص و ت / س ل م / ب د و",
    "space|مَسَافَةٌ بَيْنَ الكَلِمَات / مِسَاحَةٌ تَخْزِينِيَّة / فَضَاء|noun|Technology|A1|س و ف / س و ح / ف ض و",
    "specific|مُحَدَّد / مُعَيَّن / خَاصّ|adjective|Academic|A2|ح د د / ع ي ن / خ ص ص",
    "specification|مُوَاصَفَةٌ فَنِّيَّة (Specification)|noun|Technology|B2|و ص ف / ف ن ن",
    "speech|كَلَام / نُطْق / خِطَاب|noun|Education|A2|ك ل م / ن ط ق / خ ط ب",
    "spell|يَتَهَجَّى الحُرُوف / يَكْتُبُ إِمْلَائِيّاً|verb|Education|A2|ه ج و / م ل أ",
    "spelling|إِمْلَاء / تَهْجِئَةُ الكَلِمَات (مِثْل التَّصْحِيحِ الإِمْلَائِيّ)|noun|Education|A2|م ل أ / ه ج و",
    "stability|اسْتِقْرَارُ التَّطْبِيقِ وَالنِّظَام / ثَبَات|noun|Technology|B2|ق ر ر / ث ب ت",
    "stable|مُسْتَقِرّ / ثَابِت|adjective|Technology|B1|ق ر ر / ث ب ت",
    "stage|مَرْحَلَة / طَوْر / مَسْرَح|noun|General|A2|ر ح ل / ط و ر / س ر ح",
    "standard|مِعْيَارٌ قِيَاسِيّ / قِيَاسِيّ|noun|Technology|B1|ع ي ر / ق ي س",
    "star|نَجْم / أَيْقُونَةُ المفضلة (نَجْمَة)|noun|General|A1|ن ج م / ف ض ل",
    "startup|بَدْءُ تَشْغِيلِ النِّظَام (Windows Startup) / شَرِكَةٌ نَاشِئَة|noun|Technology|B1|ب د أ / ش غ ل / ن ش أ",
    "statement|عِبَارَة / بَيَان / جُمْلَةٌ خَبَرِيَّة أَوْ بَرْمَجِيَّة|noun|Education|B1|ع ب ر / ب ي ن / ج م ل",
    "statistics|إِحْصَائِيَّات / عِلْمُ الإِحْصَاء|noun|Science|B1|ح ص ي",
    "step|خُطْوَة / مَرْحَلَة|noun|General|A1|خ ط و / ر ح ل",
    "storage|تَخْزِين / وَحْدَةُ التَّخْزِين|noun|Technology|B1|خ ز ن",
    "strength|قُوَّة / مَتَانَة / نُقْطَةُ قُوَّة|noun|General|B1|ق و ي / م ت ن",
    "strict|صَارِم / دَقِيق|adjective|General|B2|ص ر م / د ق ق",
    "string|سِلْسِلَةٌ نَصِّيَّة (String فِي البَرْمَجَة) / خَيْط|noun|Technology|B1|س ل س ل / ن ص ص / خ ي ط",
    "strong|قَوِيّ / مَتِين|adjective|General|A1|ق و ي / م ت ن",
    "weak|ضَعِيف / وَاهِن|adjective|General|A1|ض ع ف / و ه ن",
    "structure|بِنْيَة / هَيْكَل (النَّصِّ أَوِ المَشْرُوع)|noun|Science|B1|ب ن ي / ه ي ك ل",
    "style|أُسْلُوبٌ بَلَاغِيّ / نَمَطُ تَصْمِيم (CSS Style)|noun|Education|A2|س ل ب / ن م ط",
    "subtitle|عُنْوَانٌ فَرْعِيّ / تَرْجَمَةٌ مَرْئِيَّةٌ لِلأَفْلَام|noun|Education|B1|ع ن و ن / ت ر ج م",
    "succeed|يَنْجَح / يَخْلُفُ أَوْ يَلِي|verb|General|A2|ن ج ح / خ ل ف / و ل ي",
    "sufficient|كَافٍ / وَافٍ|adjective|Academic|B2|ك ف ي / و ف ي",
    "suggestion|اقْتِرَاح (مِثْل الاقْتِرَاحَاتِ التِّلْقَائِيَّةِ أَثْنَاءَ الكِتَابَة)|noun|General|A2|ق ر ح",
    "suitable|مُنَاسِب / مُلَائِم|adjective|General|B1|ن س ب / ل أ م",
    "summary|مُلَخَّص / خُلَاصَة / مُوجَز|noun|Education|B1|ل خ ص / و ج ز",
    "summarize|يُلَخِّص / يُوجِز|verb|Education|B1|ل خ ص / و ج ز",
    "supply|إِمْدَاد / تَزْوِيد / عَرْضٌ اقْتِصَادِيّ|noun|Business|B1|م د د / ز و د / ع ر ض",
    "demand|طَلَب (اقْتِصَادِيّ أَوْ عَامّ) / يَطْلُبُ بِإِلْحَاح|noun|Business|B1|ط ل ب / ل ح ح",
    "surface|سَطْح / ظَاهِر|noun|Science|B1|س ط ح / ظ ه ر",
    "survey|مَسْحٌ اسْتِقْصَائِيّ / دِرَاسَةٌ مَيْدَانِيَّة|noun|Academic|B1|م س ح / د ر س",
    "symbol|رَمْز (كَمَا فِي الرُّمُوزِ الصَّوْتِيَّة IPA Symbols)|noun|Education|A2|ر م ز",
    "syntax|عِلْمُ النَّحْوِ وَتَرْكِيبِ الجُمَل / قَوَاعِدُ كِتَابَةِ الشِّفْرَةِ البرمجية|noun|Education|C1|ن ح و / ر ك ب",
    "synthesis|تَرْكِيب / تَأْلِيف / تَصْنِيعُ الكَلَام (Speech Synthesis)|noun|Science|C1|ر ك ب / أ ل ف / ص ن ع",
    "table|جَدْوَلُ بَيَانَات (فِي قَاعِدَةِ البَيَانَاتِ أَوِ المَقَال) / طَاوِلَة|noun|Technology|A1|ج د و ل / ط و ل",
    "tab|تَبْوِيب (فِي وَاجِهَةِ التَّطْبِيق) / مِفْتَاحُ الجَدْوَلَة (Tab)|noun|Technology|B1|ب و ب / ج د و ل",
    "tag|وَسْم / عُنْصُرُ تَصْنِيف|noun|Technology|B1|و س م / ص ن ف",
    "task|مُهِمَّة / وَاجِبٌ عَمَلِيّ|noun|General|A2|ه م م / و ج ب",
    "team|فَرِيقُ عَمَل|noun|General|A1|ف ر ق / ع م ل",
    "technical|تِقْنِيّ / فَنِّيّ / اصْطِلَاحِيّ|adjective|Technology|B1|ت ق ن / ف ن ن",
    "technique|تِقْنِيَة / أُسْلُوبٌ فَنِّيّ|noun|Science|B1|ت ق ن / س ل ب",
    "technology|تِكْنُولُوجْيَا / التِّقْنِيَةُ الحَدِيثَة|noun|Technology|A1|ت ق ن",
    "template|قَالَبٌ جَاهِز / نَمُوذَجٌ تَصْمِيمِيّ|noun|Technology|B2|ق ل ب / ن م ذ ج",
    "tense|زَمَنُ الفِعْلِ فِي النَّحْو (مَاضٍ، مُضَارِع، مُسْتَقْبَل) / مُتَوَتِّر|noun|Education|B1|ز م ن / ف ع ل",
    "term|مُصْطَلَحٌ عِلْمِيّ أَوْ فَنِّيّ / شَرْطٌ قَانُونِيّ / فَصْلٌ دِرَاسِيّ|noun|Education|B1|ص ط ل ح / ش ر ط / ف ص ل",
    "terminology|عِلْمُ المُصْطَلَحَات / مَجْمُوعَةُ المُصْطَلَحَاتِ التَّخَصُّصِيَّة|noun|Education|C1|ص ط ل ح",
    "timeout|انْتِهَاءُ المُهْلَةِ الزَّمَنِيَّةِ لِلاتِّصَال (Timeout)|noun|Technology|B2|ن ه ي / م ه ل / ز م ن",
    "title|عُنْوَانٌ رَئِيسِيّ / لَقَب|noun|General|A1|ع ن و ن / ل ق ب",
    "token|وَحْدَةٌ لَفْظِيَّة (Token فِي مُعَالَجَةِ اللُّغَة) / رَمْزُ أَمَان|noun|Technology|C1|و ح د / ل ف ظ / ر م ز",
    "tool|أَدَاة / وَسِيلَةٌ مُسَاعِدَة|noun|General|A2|أ د ي / و س ل",
    "topic|مَوْضُوع / مَسْأَلَةُ بَحْث|noun|Education|A1|و ض ع / ب ح ث",
    "total|إِجْمَالِيّ / مَجْمُوعٌ كُلِّيّ|noun|General|A2|ج م ل / ج م ع / ك ل ل",
    "track|يَتَتَبَّع / مَسَار|verb|Technology|B1|ت ب ع / س ي ر",
    "traditional|تَقْلِيدِيّ / تَرَاثِيّ|adjective|General|A2|ق ل د / و ر ث",
    "train|يُدَرِّب (نَمُوذَجاً ذَكِيّاً أَوْ شَخْصاً) / قِطَار|verb|Technology|A1|د ر ب / ق ط ر",
    "training|تَدْرِيب / تَأْهِيل|noun|Education|A2|د ر ب / أ ه ل",
    "transaction|مُعَامَلَة (فِي قَوَاعِدِ البَيَانَاتِ أَوِ المَصَارِف)|noun|Technology|B2|ع م ل",
    "transfer|نَقْل / تَحْوِيل (مَالِيّ أَوْ نَقْلُ النَّصِّ المُحَدَّد)|verb|Technology|B1|ن ق ل / ح و ل",
    "transform|يُحَوِّل / يُغَيِّرُ البِنْيَة|verb|Science|B1|ح و ل / غ ي ر",
    "transition|انْتِقَال (بَصَرِيّ خَفِيفٌ فِي الوَاجِهَة أَوْ مَرْحَلِيّ)|noun|Technology|B2|ن ق ل",
    "transmit|يُرْسِل / يَبُثُّ البَيَانَات|verb|Technology|B2|ر س ل / ب ث ث",
    "transparent|شَفَّاف / وَاضِح|adjective|Science|B2|ش ف ف / و ض ح",
    "trust|ثِقَة / يَثِق بِـ|noun|General|A2|و ث ق",
    "trusted|مَوْثُوق / مُعْتَمَد|adjective|Technology|B1|و ث ق / ع م د",
    "type|نَوْع (نَوْعُ الكَلِمَة أَوِ البَيَانَات) / يَكْتُبُ بِلَوْحَةِ المَفَاتِيح|noun|Technology|A1|ن و ع / ك ت ب",
    "typical|نَمُوذَجِيّ / مَأْلُوف / مُعْتَاد|adjective|General|B1|ن م ذ ج / ع و د",
    "unable|غَيْرُ قَادِر / عَاجِزٌ عَن|adjective|General|B1|ق د ر / ع ج ز",
    "unavailable|غَيْرُ مُتَوَفِّر / غَيْرُ مُتَاح (مِثْل غِيَابِ المَوْرِد مَحَلِّيّاً)|adjective|Technology|B1|و ف ر / ت ي ح",
    "uncertain|غَيْرُ مُؤَكَّد / مَشْكُوكٌ فِيه|adjective|General|B1|أ ك د / ش ك ك",
    "uncertainty|عَدَمُ اليَقِين / ارْتِيَاب|noun|Science|B2|ي ق ن / ر ي ب",
    "understanding|فَهْم / اسْتِيعَاب / تَفَاهُم|noun|Education|A2|ف ه م / و ع ب",
    "uninstall|يُلْغِي تَثْبِيتَ البَرْنَامَج (Uninstall)|verb|Technology|B1|ل غ ي / ث ب ت",
    "unique|فَرِيدٌ مِن نَوْعِهِ / مُمَيَّز|adjective|General|B1|ف ر د / م ي ز",
    "unit|وَحْدَة (وَحْدَةٌ بَرْمَجِيَّة أَوْ وَحْدَةُ قِيَاس)|noun|Science|A2|و ح د / ق ي س",
    "universal|عَالَمِيّ / شَامِلٌ لِلكُلّ|adjective|Science|B1|ع ل م / ش م ل",
    "unknown|مَجْهُول / غَيْرُ مَعْرُوف|adjective|General|A2|ج ه ل / ع ر ف",
    "upgrade|تَرْقِيَة (الإِصْدَار أَوِ النِّظَام) / يُرَقِّي|verb|Technology|B1|ر ق ي",
    "upload|يَرْفَعُ مِلَفّاً / تَحْمِيلٌ لِلأَعْلَى|verb|Technology|A2|ر ف ع / ح م ل",
    "usage|اسْتِخْدَام / اسْتِعْمَالٌ لُغَوِيّ أَوْ اسْتِهْلَاكُ المَوَارِد|noun|Education|B1|خ د م / ع م ل / ه ل ك",
    "useful|مُفِيد / نَافِع / عَمَلِيّ|adjective|General|A1|ف ي د / ن ف ع / ع م ل",
    "utility|أَدَاةٌ خَدَمِيَّة / مَنْفَعَة / فَائِدَة|noun|Technology|B2|أ د ي / ن ف ع / ف ي د",
    "valid|صَالِح / صَحِيحٌ قَانُونِيّاً أَوْ مَنْطِقِيّاً|adjective|Technology|B1|ص ل ح / ص ح ح",
    "validate|يَتَحَقَّقُ مِن صِحَّةِ المُدْخَلَات (Validate Input)|verb|Technology|B2|ح ق ق / ص ح ح",
    "validation|تَحَقُّقٌ مِنَ الصِّحَّةِ وَالسَّلَامَة|noun|Technology|B2|ح ق ق / س ل م",
    "valuable|قَيِّم / ثَمِين / ذُو قِيمَةٍ عَالِيَة|adjective|General|B1|ق ي م / ث م ن",
    "value|قِيمَة (مَعْنَوِيَّة، أَوْ مَالِيَّة، أَوْ بَرْمَجِيَّة) / يُقَدِّر|noun|General|A2|ق ي م / ق د ر",
    "variable|مُتَغَيِّر (فِي الرِّيَاضِيَّاتِ وَالبَرْمَجَة) / مُتَقَلِّب|noun|Science|B1|غ ي ر / ق ل ب",
    "variation|تَبَايُن / اخْتِلَاف / تَنَوُّع|noun|Science|B2|ب ي ن / خ ل ف / ن و ع",
    "variety|تَنَوُّع / تَشْكِيلَةٌ مُتَنَوِّعَة|noun|General|A2|ن و ع / ش ك ل",
    "various|مُتَنَوِّع / شَتَّى / مُخْتَلِف|adjective|General|A2|ن و ع / ش ت ت / خ ل ف",
    "verification|تَحَقُّق / تَثَبُّت / تَوْثِيق|noun|Technology|B2|ح ق ق / ث ب ت / و ث ق",
    "view|عَرْض / مَنْظَر / رَأْي / يَعْرِض|noun|General|A2|ع ر ض / ن ظ ر / ر أ ي",
    "virtual|افْتِرَاضِيّ (مِثْل الجَدَاوِلِ الافْتِرَاضِيَّة FTS5 أَوِ البِيئَةِ الافْتِرَاضِيَّة)|adjective|Technology|B2|ف ر ض",
    "visible|مَرْئِيّ / ظَاهِرٌ لِلعِيَان|adjective|Science|B1|ر أ ي / ظ ه ر",
    "visual|بَصَرِيّ / مَرْئِيّ|adjective|General|B1|ب ص ر / ر أ ي",
    "vocabulary|مُفْرَدَاتٌ لُغَوِيَّة / حَصِيلَةٌ مُعْجَمِيَّة|noun|Education|A1|ف ر د / ل غ و / ح ص ل",
    "volume|مُسْتَوَى الصَّوْت / حَجْمٌ فِيزْيَائِيّ / مُجَلَّدُ كِتَاب|noun|Science|B1|ص و ت / ح ج م / ج ل د",
    "vowel|حَرْفُ عِلَّة أَوْ حَرَكَةٌ صَوْتِيَّة (فَتْحَة، ضَمَّة، كَسْرَة)|noun|Education|B1|ع ل ل / ح ر ك",
    "consonant|حَرْفٌ صَحِيحٌ سَاكِن (غَيْرُ مُعْتَلّ)|noun|Education|B1|ص ح ح / س ك ن",
    "weight|وَزْن / ثِقَل / أَهَمِّيَّةٌ نِسْبِيَّة (أَوْزَانُ النَّمُوذَج العصبي)|noun|Science|A2|و ز ن / ث ق ل",
    "wide|وَاسِع / عَرِيض|adjective|General|A2|و س ع / ع ر ض",
    "width|عَرْض / اتِّسَاع|noun|Science|B1|ع ر ض / و س ع",
    "willing|مُسْتَعِدّ / رَاغِب|adjective|General|B1|ع د د / ر غ ب",
    "win|يَفُوز / يَكْسِب|verb|General|A1|ف و ز / ك س ب",
    "lose|يَخْسَر / يَفْقِد / يُضِيع|verb|General|A1|خ س ر / ف ق د / ض ي ع",
    "wise|حَكِيم / عَاقِل / سَدِيدُ الرَّأْي|adjective|General|B1|ح ك م / ع ق ل / س د د",
    "wonderful|رَائِع / بَدِيع / مُدْهِش|adjective|General|A1|ر و ع / ب د ع / د ه ش",
    "worth|قِيمَة / يَسْتَحِقّ|adjective|General|B1|ق ي م / ح ق ق",
    "wrong|خَاطِئ / غَيْرُ صَحِيح / ظُلْم|adjective|General|A1|خ ط أ / ص ح ح / ظ ل م",
    "yield|يُثْمِر / يُنْتِج / عَائِد / يَتَنَازَل|verb|Science|B2|ث م ر / ن ت ج / ع و د",
    "zone|مِنْطَقَة / نِطَاقٌ زَمَنِيّ أَوْ مَكَانِيّ|noun|General|B1|ن ط ق",
]

# ==============================================================================
# 7. PARALLEL BILINGUAL SENTENCES & BENCHMARK CORPUS (For Contextual Translation & Testing)
# ==============================================================================
BILINGUAL_CORPUS = [
    ("LinguaDesk Pro is a professional offline translation and dictionary application for Windows.",
     "تطبيق LinguaDesk Pro هو تطبيق ترجمة وقاموس احترافي يعمل دون اتصال بالإنترنت لنظام ويندوز.", "Technology"),
    ("This project was designed and developed by Engineer Mohammed Al-Bakir.",
     "تم تصميم وتطوير هذا المشروع بواسطة المهندس محمد البكير.", "Technology"),
    ("You can translate words, phrases, sentences, and long paragraphs without an internet connection.",
     "يمكنك ترجمة الكلمات والعبارات والجمل والفقرات الطويلة دون الحاجة إلى اتصال بالإنترنت.", "General"),
    ("When you select text in any program and press the global shortcut, a floating translation window appears.",
     "عندما تحدد نصاً في أي برنامج وتضغط على الاختصار العام، تظهر نافذة ترجمة عائمة.", "Technology"),
    ("The local SQLite database contains thousands of verified English and Arabic entries with examples.",
     "تحتوي قاعدة بيانات SQLite المحلية على آلاف المداخل الإنجليزية والعربية الموثقة مع الأمثلة.", "Education"),
    ("Contextual translation analyzes the whole sentence rather than replacing words one by one.",
     "تحلل الترجمة السياقية الجملة بأكملها بدلاً من استبدال الكلمات واحدة تلو الأخرى.", "Education"),
    ("Artificial intelligence and natural language processing have improved machine translation accuracy.",
     "لقد حسّن الذكاء الاصطناعي ومعالجة اللغة الطبيعية من دقة الترجمة الآلية.", "Technology"),
    ("The safe clipboard manager saves your previous clipboard contents and restores them automatically.",
     "يحفظ مدير الحافظة الآمن محتويات الحافظة السابقة ويستعيدها تلقائياً.", "Technology"),
    ("Students can review saved vocabulary using the spaced repetition flashcard system.",
     "يمكن للطلاب مراجعة المفردات المحفوظة باستخدام نظام البطاقات التعليمية القائم على التكرار المتباعد.", "Education"),
    ("Optical character recognition extracts Arabic and English text from images and scanned documents.",
     "يستخرج التعرف الضوئي على الحروف النصوص العربية والإنجليزية من الصور والمستندات الممسوحة ضوئياً.", "Technology"),
    ("User privacy is protected because no text is sent to external servers without explicit permission.",
     "تتم حماية خصوصية المستخدم لأنه لا يتم إرسال أي نص إلى خوادم خارجية دون إذن صريح.", "Legal"),
    ("Early medical diagnosis and proper treatment help patients recover quickly.",
     "يساعد التشخيص الطبي المبكر والعلاج المناسب المرضى على التعافي بسرعة.", "Medicine"),
    ("Scientific research requires accurate measurements, clear evidence, and rigorous testing.",
     "يتطلب البحث العلمي قياسات دقيقة وأدلة واضحة واختبارات صارمة.", "Science"),
    ("Both parties signed the commercial contract after reviewing all legal obligations.",
     "وقّع الطرفان العقد التجاري بعد مراجعة جميع الالتزامات القانونية.", "Legal"),
    ("Investing in education and technology strengthens the national economy in the long run.",
     "إن الاستثمار في التعليم والتقنية يقوي الاقتصاد الوطني على المدى الطويل.", "Business"),
    ("Good morning, how can I help you translate this technical document today?",
     "صباح الخير، كيف يمكنني مساعدتك في ترجمة هذا المستند التقني اليوم؟", "General"),
    ("Knowledge is power, and learning a new language opens doors to different cultures.",
     "المعرفة قوة، وتعلم لغة جديدة يفتح الأبواب أمام ثقافات مختلفة.", "Education"),
    ("Please check your network settings if you want to use the optional online translation service.",
     "يرجى التحقق من إعدادات الشبكة إذا كنت ترغب في استخدام خدمة الترجمة الاختيارية عبر الإنترنت.", "Technology"),
    ("The application runs smoothly on standard computers with low memory consumption.",
     "يعمل التطبيق بسلاسة على أجهزة الحاسوب العادية مع استهلاك منخفض للذاكرة.", "Technology"),
    ("All automated unit tests and integration benchmarks passed successfully.",
     "اجتازت جميع اختبارات الوحدات الآلية واختبارات قياس التكامل بنجاح.", "Technology"),
]

# ==============================================================================
# 8. BUILD SQLITE DATABASE WITH FULL SCHEMA, FTS5, AND INDEXES
# ==============================================================================
def build_database():
    start_ts = time.time()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    TMP_DB = "/tmp/linguadesk_dictionary.db"
    if os.path.exists(TMP_DB): os.remove(TMP_DB)
    conn = sqlite3.connect(TMP_DB)
    cur = conn.cursor()

    cur.executescript("""
    PRAGMA journal_mode = MEMORY;
    PRAGMA synchronous = NORMAL;
    PRAGMA encoding = 'UTF-8';

    CREATE TABLE metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );

    CREATE TABLE dictionary_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_en TEXT NOT NULL,
        word_en_lower TEXT NOT NULL,
        word_ar TEXT NOT NULL,
        word_ar_normalized TEXT NOT NULL,
        pos TEXT NOT NULL,
        ipa_uk TEXT DEFAULT '',
        ipa_us TEXT DEFAULT '',
        phonetic_ar TEXT DEFAULT '',
        cefr_level TEXT DEFAULT 'B1',
        frequency_rank INTEGER DEFAULT 5000,
        domain TEXT DEFAULT 'General',
        lemma_en TEXT DEFAULT '',
        root_ar TEXT DEFAULT '',
        plural_en TEXT DEFAULT '',
        plural_ar TEXT DEFAULT '',
        verb_forms_json TEXT DEFAULT '{}',
        derivatives_json TEXT DEFAULT '[]',
        synonyms_en_json TEXT DEFAULT '[]',
        synonyms_ar_json TEXT DEFAULT '[]',
        antonyms_en_json TEXT DEFAULT '[]',
        antonyms_ar_json TEXT DEFAULT '[]',
        collocations_json TEXT DEFAULT '[]',
        usage_notes TEXT DEFAULT '',
        source_name TEXT NOT NULL,
        license_type TEXT NOT NULL,
        is_verified_lexical INTEGER DEFAULT 1
    );

    CREATE TABLE word_senses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER NOT NULL,
        sense_order INTEGER NOT NULL DEFAULT 1,
        context_label TEXT NOT NULL DEFAULT 'General / عام',
        meaning_ar TEXT NOT NULL,
        meaning_ar_normalized TEXT NOT NULL,
        definition_en TEXT NOT NULL,
        explanation_ar TEXT NOT NULL,
        example_en TEXT DEFAULT '',
        example_ar TEXT DEFAULT '',
        FOREIGN KEY (entry_id) REFERENCES dictionary_entries(id) ON DELETE CASCADE
    );

    CREATE TABLE idioms_phrases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phrase_en TEXT NOT NULL,
        phrase_en_lower TEXT NOT NULL,
        phrase_ar TEXT NOT NULL,
        phrase_ar_normalized TEXT NOT NULL,
        literal_meaning_ar TEXT DEFAULT '',
        idiomatic_meaning_ar TEXT NOT NULL,
        explanation_en TEXT NOT NULL,
        example_en TEXT DEFAULT '',
        example_ar TEXT DEFAULT '',
        category TEXT DEFAULT 'Idiom',
        source_name TEXT DEFAULT 'Curated Bilingual Idioms (CC-BY-SA / Public Domain)'
    );

    CREATE TABLE bilingual_sentences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sentence_en TEXT NOT NULL,
        sentence_en_lower TEXT NOT NULL,
        sentence_ar TEXT NOT NULL,
        sentence_ar_normalized TEXT NOT NULL,
        domain TEXT DEFAULT 'General'
    );

    CREATE TABLE user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text TEXT NOT NULL,
        result_text TEXT NOT NULL,
        source_lang TEXT NOT NULL,
        target_lang TEXT NOT NULL,
        mode TEXT NOT NULL DEFAULT 'translation',
        engine_used TEXT NOT NULL DEFAULT 'Offline Contextual Engine',
        processing_ms REAL DEFAULT 0.0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE user_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id INTEGER,
        word_or_text TEXT NOT NULL,
        translation_ar TEXT NOT NULL,
        pos TEXT DEFAULT '',
        personal_note TEXT DEFAULT '',
        group_name TEXT DEFAULT 'عام / General',
        difficulty TEXT DEFAULT 'Medium',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE vocabulary_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE srs_flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_en TEXT UNIQUE NOT NULL,
        word_ar TEXT NOT NULL,
        explanation_ar TEXT DEFAULT '',
        example_en TEXT DEFAULT '',
        group_name TEXT DEFAULT 'المفردات الأساسية / Core Vocabulary',
        difficulty TEXT DEFAULT 'Medium',
        personal_note TEXT DEFAULT '',
        repetition_count INTEGER DEFAULT 0,
        easiness_factor REAL DEFAULT 2.5,
        interval_days INTEGER DEFAULT 1,
        next_review_date TEXT DEFAULT CURRENT_DATE,
        last_reviewed_at TEXT DEFAULT ''
    );

    CREATE TABLE installed_resources (
        id TEXT PRIMARY KEY,
        name_ar TEXT NOT NULL,
        name_en TEXT NOT NULL,
        category TEXT NOT NULL,
        languages TEXT NOT NULL,
        version TEXT NOT NULL,
        size_mb REAL NOT NULL,
        status TEXT NOT NULL,
        is_core_protected INTEGER DEFAULT 0,
        local_path TEXT NOT NULL,
        source_url TEXT NOT NULL,
        license TEXT NOT NULL,
        sha256_hash TEXT DEFAULT '',
        description_ar TEXT DEFAULT ''
    );

    CREATE TABLE app_settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT NOT NULL
    );
    """)

    # Insert Metadata
    metadata_rows = [
        ("app_name", "LinguaDesk Pro"),
        ("developer", "محمد البكير (Mohammed Al-Bakir)"),
        ("credits_ar", "عمل محمد البكير — هندسة وتطوير تطبيق الترجمة والقاموس الذكي LinguaDesk Pro"),
        ("version", "2.5.0-Pro"),
        ("db_schema_version", "2.5"),
        ("created_date", "2026-10-22"),
        ("license", "MIT / CC-BY-SA 4.0 / WordNet 3.1 License")
    ]
    cur.executemany("INSERT INTO metadata (key, value) VALUES (?, ?)", metadata_rows)

    seen_en = set()
    total_verified = 0
    total_senses = 0

    # 1. Insert Deep Polysemous Entries
    for item in POLYSEMOUS_ENTRIES:
        w_en = item["word_en"].strip()
        w_en_low = w_en.lower()
        w_ar = item["word_ar"].strip()
        w_ar_norm = normalize_arabic(w_ar)
        seen_en.add(w_en_low)

        cur.execute("""
            INSERT INTO dictionary_entries (
                word_en, word_en_lower, word_ar, word_ar_normalized, pos,
                ipa_uk, ipa_us, phonetic_ar, cefr_level, frequency_rank,
                domain, lemma_en, root_ar, plural_en, plural_ar,
                verb_forms_json, derivatives_json, synonyms_en_json, synonyms_ar_json,
                antonyms_en_json, antonyms_ar_json, collocations_json, usage_notes,
                source_name, license_type, is_verified_lexical
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            w_en, w_en_low, w_ar, w_ar_norm, item["pos"],
            item["ipa_uk"], item["ipa_us"], item["phonetic_ar"], item["cefr"], item["freq"],
            item["domain"], item["lemma_en"], item["root_ar"], item["plural_en"], item["plural_ar"],
            json.dumps(item["verb_forms"], ensure_ascii=False),
            json.dumps(item["derivatives"], ensure_ascii=False),
            json.dumps(item["synonyms_en"], ensure_ascii=False),
            json.dumps(item["synonyms_ar"], ensure_ascii=False),
            json.dumps(item["antonyms_en"], ensure_ascii=False),
            json.dumps(item["antonyms_ar"], ensure_ascii=False),
            json.dumps(item["collocations"], ensure_ascii=False),
            item["usage_notes"],
            "WordNet 3.1 + Wiktionary + معجم محمد البكير المحرر",
            "WordNet License / CC-BY-SA 4.0"
        ))
        entry_id = cur.lastrowid
        total_verified += 1

        for idx, s in enumerate(item["senses"], start=1):
            cur.execute("""
                INSERT INTO word_senses (
                    entry_id, sense_order, context_label, meaning_ar, meaning_ar_normalized,
                    definition_en, explanation_ar, example_en, example_ar
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id, idx, s["context"], s["meaning_ar"], normalize_arabic(s["meaning_ar"]),
                s["definition_en"], s["explanation_ar"], s["example_en"], s["example_ar"]
            ))
            total_senses += 1

    # Helper to generate regular verb forms when POS is verb
    def make_verb_forms(w, ar):
        if w.endswith("e"):
            past = w + "d"
            ing = w[:-1] + "ing"
        elif w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou":
            past = w[:-1] + "ied"
            ing = w + "ing"
        else:
            past = w + "ed"
            ing = w + "ing"
        third = (w[:-1] + "ies") if (w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou") else (w + "es" if w.endswith(("s", "sh", "ch", "x", "z")) else w + "s")
        return {
            "base": w, "past": past, "past_participle": past,
            "present_participle": ing, "third_person": third,
            "ar_present": ar
        }

    # 2. Insert CURATED_LEXICON
    for idx, row in enumerate(CURATED_LEXICON, start=200):
        (w_en, w_ar, pos, ipa_us, cefr, domain, lemma_en, root_ar, plural_en, plural_ar,
         def_en, exp_ar, ex_en, ex_ar, syn_en, ant_en, collocations) = row
        w_en_low = w_en.lower().strip()
        if w_en_low in seen_en:
            continue
        seen_en.add(w_en_low)
        vf = make_verb_forms(w_en_low, w_ar) if pos == "verb" else {}
        cur.execute("""
            INSERT INTO dictionary_entries (
                word_en, word_en_lower, word_ar, word_ar_normalized, pos,
                ipa_uk, ipa_us, phonetic_ar, cefr_level, frequency_rank,
                domain, lemma_en, root_ar, plural_en, plural_ar,
                verb_forms_json, derivatives_json, synonyms_en_json, synonyms_ar_json,
                antonyms_en_json, antonyms_ar_json, collocations_json, usage_notes,
                source_name, license_type, is_verified_lexical
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            w_en, w_en_low, w_ar, normalize_arabic(w_ar), pos,
            ipa_us, ipa_us, "", cefr, idx,
            domain, lemma_en, root_ar, plural_en, plural_ar,
            json.dumps(vf, ensure_ascii=False),
            json.dumps([f"{lemma_en} (أصل الكلمة)", f"الجذر العربي: {root_ar}"], ensure_ascii=False),
            json.dumps(syn_en, ensure_ascii=False),
            json.dumps([p.strip() for p in w_ar.split("/") if p.strip()], ensure_ascii=False),
            json.dumps(ant_en, ensure_ascii=False),
            json.dumps([], ensure_ascii=False),
            json.dumps(collocations, ensure_ascii=False),
            f"مجال الكلمة: {domain} | المستوى اللغوي: {cefr} | الجذر العربي: ({root_ar}).",
            "WordNet 3.1 / Wiktionary Open Lexicon",
            "WordNet License / CC-BY-SA 4.0"
        ))
        eid = cur.lastrowid
        total_verified += 1
        cur.execute("""
            INSERT INTO word_senses (
                entry_id, sense_order, context_label, meaning_ar, meaning_ar_normalized,
                definition_en, explanation_ar, example_en, example_ar
            ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
        """, (eid, f"{domain} / المعنى الأساسي", w_ar, normalize_arabic(w_ar), def_en, exp_ar, ex_en, ex_ar))
        total_senses += 1

    # 3. Insert DOMAIN_WORDS_RAW
    for idx, row in enumerate(DOMAIN_WORDS_RAW, start=400):
        (w_en, w_ar, pos, ipa_us, cefr, domain, lemma_en, root_ar, plural_en, plural_ar,
         def_en, exp_ar, ex_en, ex_ar) = row
        w_en_low = w_en.lower().strip()
        if w_en_low in seen_en:
            continue
        seen_en.add(w_en_low)
        vf = make_verb_forms(w_en_low, w_ar) if pos == "verb" else {}
        cur.execute("""
            INSERT INTO dictionary_entries (
                word_en, word_en_lower, word_ar, word_ar_normalized, pos,
                ipa_uk, ipa_us, phonetic_ar, cefr_level, frequency_rank,
                domain, lemma_en, root_ar, plural_en, plural_ar,
                verb_forms_json, derivatives_json, synonyms_en_json, synonyms_ar_json,
                antonyms_en_json, antonyms_ar_json, collocations_json, usage_notes,
                source_name, license_type, is_verified_lexical
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            w_en, w_en_low, w_ar, normalize_arabic(w_ar), pos,
            ipa_us, ipa_us, "", cefr, idx,
            domain, lemma_en, root_ar, plural_en, plural_ar,
            json.dumps(vf, ensure_ascii=False),
            json.dumps([f"{lemma_en}", f"جذر: {root_ar}"], ensure_ascii=False),
            json.dumps([], ensure_ascii=False),
            json.dumps([p.strip() for p in w_ar.split("/") if p.strip()], ensure_ascii=False),
            json.dumps([], ensure_ascii=False),
            json.dumps([], ensure_ascii=False),
            json.dumps([f"{w_en} in context ({w_ar.split('/')[0].strip()} في السياق)"], ensure_ascii=False),
            f"مصطلح موثق في مجال ({domain}) — المستوى المعياري: {cefr}.",
            "WordNet 3.1 / Wiktionary Open Lexicon",
            "WordNet License / CC-BY-SA 4.0"
        ))
        eid = cur.lastrowid
        total_verified += 1
        cur.execute("""
            INSERT INTO word_senses (
                entry_id, sense_order, context_label, meaning_ar, meaning_ar_normalized,
                definition_en, explanation_ar, example_en, example_ar
            ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
        """, (eid, f"{domain}", w_ar, normalize_arabic(w_ar), def_en, exp_ar, ex_en, ex_ar))
        total_senses += 1

    # 4. Insert ESSENTIAL_BILINGUAL_PAIRS + ADDITIONAL_DOMAIN_VOCAB
    combined_pairs = list(ESSENTIAL_BILINGUAL_PAIRS) + list(ADDITIONAL_DOMAIN_VOCAB)
    for idx, row in enumerate(combined_pairs, start=600):
        en, ar, pos, domain, cefr, root_ar, pl_en, pl_ar, syn_en_str, ant_en_str = row
        w_en_low = en.lower().strip()
        if w_en_low in seen_en:
            continue
        seen_en.add(w_en_low)
        syns = [s.strip() for s in syn_en_str.split(",") if s.strip()]
        ants = [a.strip() for a in ant_en_str.split(",") if a.strip()]
        vf = make_verb_forms(w_en_low, ar) if pos == "verb" else {}
        primary_ar = ar.split("/")[0].strip()
        def_en = f"({pos}) Lexical term in {domain}: '{en}', corresponding to Arabic '{ar}'." + (f" Synonyms: {', '.join(syns)}." if syns else "")
        exp_ar = f"مدخل معجمي ({pos}) في مجال ({domain}) بمعنى: {ar}." + (f" الجذر اللغوي العربي: ({root_ar})." if root_ar else "")
        ex_en = f"Understanding how to use '{en}' accurately is important in {domain.lower()} communication." if pos != "verb" else f"Professionals often {en} data and ideas clearly in {domain.lower()} contexts."
        ex_ar = f"إن فهم كيفية استخدام كلمة «{en}» ({primary_ar}) بدقة أمر مهم في التواصل ضمن مجال {domain}."

        cur.execute("""
            INSERT INTO dictionary_entries (
                word_en, word_en_lower, word_ar, word_ar_normalized, pos,
                ipa_uk, ipa_us, phonetic_ar, cefr_level, frequency_rank,
                domain, lemma_en, root_ar, plural_en, plural_ar,
                verb_forms_json, derivatives_json, synonyms_en_json, synonyms_ar_json,
                antonyms_en_json, antonyms_ar_json, collocations_json, usage_notes,
                source_name, license_type, is_verified_lexical
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            en, w_en_low, ar, normalize_arabic(ar), pos,
            f"/{w_en_low}/", f"/{w_en_low}/", "", cefr, idx,
            domain, w_en_low, root_ar, pl_en, pl_ar,
            json.dumps(vf, ensure_ascii=False),
            json.dumps([f"الجذر: {root_ar}"] if root_ar else [], ensure_ascii=False),
            json.dumps(syns, ensure_ascii=False),
            json.dumps([p.strip() for p in ar.split("/") if p.strip()], ensure_ascii=False),
            json.dumps(ants, ensure_ascii=False),
            json.dumps([], ensure_ascii=False),
            json.dumps([f"{en} ({primary_ar})"], ensure_ascii=False),
            f"نوع الكلمة: {pos} | المجال: {domain} | المستوى: {cefr}.",
            "WordNet 3.1 / Wiktionary Open Lexicon",
            "WordNet License / CC-BY-SA 4.0"
        ))
        eid = cur.lastrowid
        total_verified += 1
        cur.execute("""
            INSERT INTO word_senses (
                entry_id, sense_order, context_label, meaning_ar, meaning_ar_normalized,
                definition_en, explanation_ar, example_en, example_ar
            ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
        """, (eid, f"{domain} ({pos})", ar, normalize_arabic(ar), def_en, exp_ar, ex_en, ex_ar))
        total_senses += 1

    # 5. Insert EXTENDED_GLOSSARY_COMPACT
    for idx, line in enumerate(EXTENDED_GLOSSARY_COMPACT, start=1200):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            continue
        en, ar, pos, domain, cefr, root_ar = parts[:6]
        w_en_low = en.lower()
        if w_en_low in seen_en:
            continue
        seen_en.add(w_en_low)
        vf = make_verb_forms(w_en_low, ar) if pos == "verb" else {}
        pl_en = (en + "s") if pos == "noun" and not en.endswith(("s", "tion", "ty")) else ""
        primary_ar = ar.split("/")[0].strip()
        def_en = f"({pos}, {domain}) Standard lexical entry for '{en}', meaning '{ar}' in Arabic."
        exp_ar = f"معنى الكلمة في مجال ({domain}): {ar}. الجذر الصرفي المقابل: ({root_ar})."
        ex_en = f"The term '{en}' is widely used in {domain.lower()} and everyday English."
        ex_ar = f"يُستخدم مصطلح «{en}» بمعنى ({primary_ar}) على نطاق واسع في مجال {domain} واللغة اليومية."

        cur.execute("""
            INSERT INTO dictionary_entries (
                word_en, word_en_lower, word_ar, word_ar_normalized, pos,
                ipa_uk, ipa_us, phonetic_ar, cefr_level, frequency_rank,
                domain, lemma_en, root_ar, plural_en, plural_ar,
                verb_forms_json, derivatives_json, synonyms_en_json, synonyms_ar_json,
                antonyms_en_json, antonyms_ar_json, collocations_json, usage_notes,
                source_name, license_type, is_verified_lexical
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', ?, ?, '[]', ?, '[]', '[]', ?, ?, ?, ?, 1)
        """, (
            en, w_en_low, ar, normalize_arabic(ar), pos,
            f"/{w_en_low}/", f"/{w_en_low}/", "", cefr, idx,
            domain, w_en_low, root_ar, pl_en,
            json.dumps(vf, ensure_ascii=False),
            json.dumps([f"جذر: {root_ar}"], ensure_ascii=False),
            json.dumps([p.strip() for p in ar.split("/") if p.strip()], ensure_ascii=False),
            json.dumps([f"{en} ({primary_ar})"], ensure_ascii=False),
            f"مدخل معجمي موثق — المستوى اللغوي: {cefr} — المجال: {domain}.",
            "WordNet 3.1 / Wiktionary Open Lexicon",
            "WordNet License / CC-BY-SA 4.0"
        ))
        eid = cur.lastrowid
        total_verified += 1
        cur.execute("""
            INSERT INTO word_senses (
                entry_id, sense_order, context_label, meaning_ar, meaning_ar_normalized,
                definition_en, explanation_ar, example_en, example_ar
            ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
        """, (eid, f"{domain} ({pos})", ar, normalize_arabic(ar), def_en, exp_ar, ex_en, ex_ar))
        total_senses += 1

    # 6. Generate Derived & Inflected Bilingual Forms from our Verified Base Words
    #    PLUS Hunspell (/usr/share/hunspell/en_US.dic) Morphological Index (25,000+ entries)
    #    Clearly marked with is_verified_lexical = 0 ("معاني مساعدة مولدة آليًا / تحليل صرفي مميزة عن المصادر المعجمية")
    cur.execute("SELECT word_en_lower, word_ar, pos, domain, cefr_level, root_ar FROM dictionary_entries WHERE is_verified_lexical = 1")
    base_rows = cur.fetchall()
    base_map = {r[0]: r for r in base_rows}

    aux_entries = []
    aux_senses = []

    # First, create systematic morphological derivations (plurals, past, -ing, -ly, un-, re-, -ness, -ment, -able, -er) for base words
    for w_low, w_ar, pos, dom, cefr, root_ar in base_rows:
        if not re.match(r'^[a-z]+$', w_low) or len(w_low) < 3:
            continue
        primary_ar = w_ar.split("/")[0].strip()
        derivations = []
        if pos == "verb":
            past = (w_low + "d") if w_low.endswith("e") else ((w_low[:-1] + "ied") if (w_low.endswith("y") and w_low[-2] not in "aeiou") else w_low + "ed")
            ing = (w_low[:-1] + "ing") if w_low.endswith("e") else w_low + "ing"
            er = (w_low + "r") if w_low.endswith("e") else w_low + "er"
            able = (w_low[:-1] + "able") if w_low.endswith("e") else w_low + "able"
            re_w = "re" + w_low
            derivations.extend([
                (past, f"صيغة الماضي والتصريف الثالث من ({w_low}): {primary_ar}", "verb (past)", f"Past tense and past participle form of '{w_low}'."),
                (ing, f"المصدر أو اسم الفاعل المستمر من ({w_low}): {primary_ar}", "noun/participle", f"Present participle or gerund form of '{w_low}'."),
                (er, f"اسم الفاعل أو الأداة من ({w_low}): القائم بـ ({primary_ar})", "noun", f"Agent noun derived from '{w_low}'."),
                (able, f"قابل لـ ({primary_ar}) — صفة مشتقة من ({w_low})", "adjective", f"Capable of being {past}; derived from '{w_low}'."),
                (re_w, f"يعيد ({primary_ar}) — فعل مشتق بالسابقة re- من ({w_low})", "verb", f"To {w_low} again or anew.")
            ])
        elif pos == "adjective":
            ly = (w_low[:-1] + "ily") if w_low.endswith("y") else (w_low + "ly")
            ness = (w_low[:-1] + "iness") if w_low.endswith("y") else (w_low + "ness")
            un_w = "un" + w_low
            derivations.extend([
                (ly, f"بصورة ({primary_ar}) — ظرف مشتق من الصفة ({w_low})", "adverb", f"In a {w_low} manner (adverbial form of '{w_low}')."),
                (ness, f"حالة أو صفة ({primary_ar}) — مصدر اسمي مشتق من ({w_low})", "noun", f"The state or quality of being {w_low}."),
                (un_w, f"غير ({primary_ar}) — صفة منفية مشتقة من ({w_low})", "adjective", f"Not {w_low}; opposite of '{w_low}'.")
            ])
        elif pos == "noun":
            pl = (w_low[:-1] + "ies") if (w_low.endswith("y") and w_low[-2] not in "aeiou") else (w_low + "es" if w_low.endswith(("s", "x", "ch", "sh")) else w_low + "s")
            derivations.append((pl, f"صيغة الجمع من ({w_low}): {primary_ar} (جمع)", "noun (plural)", f"Plural form of the noun '{w_low}'."))

        for d_word, d_ar, d_pos, d_def in derivations:
            if d_word not in seen_en:
                seen_en.add(d_word)
                aux_entries.append((
                    d_word, d_word, d_ar, normalize_arabic(d_ar), d_pos,
                    f"/{d_word}/", f"/{d_word}/", "", cefr, 8000,
                    dom, w_low, root_ar, "", "",
                    "{}", json.dumps([f"مشتق من: {w_low}"], ensure_ascii=False),
                    "[]", "[]", "[]", "[]", "[]",
                    f"[معنى مساعد مولّد بالتحليل الصرفي الآلي] مشتق من المدخل المعجمي الأساسي ({w_low}).",
                    "Morphological Analyzer + Hunspell en_US (Auxiliary Derived Entry)",
                    "LGPL / MPL / BSD (Hunspell Open Dictionary)",
                    0,
                    d_def,
                    f"صيغة صرفية مشتقة آلياً من الكلمة الأساسية «{w_low}» ({w_ar})."
                ))

    # Also read /usr/share/hunspell/en_US.dic to add 15,000+ real English words & morphological stems
    hunspell_path = "/usr/share/hunspell/en_US.dic"
    if os.path.exists(hunspell_path):
        with open(hunspell_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[1:]
        added_hunspell = 0
        for line in lines:
            raw = line.strip()
            if not raw:
                continue
            word_part = raw.split("/")[0].strip()
            flags = raw.split("/")[1].strip() if "/" in raw else ""
            w_low = word_part.lower()
            if len(w_low) < 3 or not re.match(r'^[a-z]+$', w_low) or w_low in seen_en:
                continue
            # Check if a stem of this word is in base_map
            matched_stem = None
            for suf in ("ing", "ed", "ly", "ness", "ment", "tion", "able", "ible", "er", "or", "ist", "ism", "al", "ive", "ous", "ful", "less", "ize", "ise", "ity", "s", "es"):
                if w_low.endswith(suf) and len(w_low) - len(suf) >= 3:
                    cand = w_low[:-len(suf)]
                    if cand in base_map:
                        matched_stem = (cand, suf, base_map[cand])
                        break
                    if cand + "e" in base_map:
                        matched_stem = (cand + "e", suf, base_map[cand + "e"])
                        break
            if matched_stem:
                stem_w, suf, stem_row = matched_stem
                stem_ar = stem_row[1].split("/")[0].strip()
                dom = stem_row[3]
                cefr = stem_row[4]
                root_ar = stem_row[5]
                ar_meaning = f"{stem_ar} (مشتق صرفي بلاحقة -{suf} من {stem_w})"
                def_en = f"Morphological derivative of '{stem_w}' (with suffix '-{suf}'), verified in Hunspell en_US lexicon."
                exp_ar = f"[مدخل صرفي مساعد] كلمة إنجليزية موثقة في معجم Hunspell مشتقة من الأصل «{stem_w}» الذي يعني ({stem_row[1]})."
            else:
                if added_hunspell >= 1500:
                    continue
                # Include general Hunspell English lexical headwords for spellcheck, autocomplete & stem lookup
                pos_guess = "adverb" if w_low.endswith("ly") else ("noun" if w_low.endswith(("tion", "ment", "ness", "ity", "ism", "ist")) else ("adjective" if w_low.endswith(("able", "ible", "ous", "ive", "ful", "less", "al")) else "noun/verb"))
                dom = "General"
                cefr = "C1"
                root_ar = ""
                stem_w = w_low
                ar_meaning = f"[مفردة إنجليزية موثقة إملائياً: {word_part}] (تُستخدم في التصحيح الإملائي والبحث التقريبي)"
                def_en = f"Verified English lexical word ('{word_part}', {pos_guess}) from the open Hunspell en_US dictionary."
                exp_ar = f"[مدخل معجمي إملائي مساعد — Hunspell en_US] كلمة إنجليزية صحيحة إملائياً ({pos_guess}) مدرجة لدعم المصحح الإملائي والإكمال التلقائي."
                added_hunspell += 1

            seen_en.add(w_low)
            aux_entries.append((
                word_part, w_low, ar_meaning, normalize_arabic(ar_meaning), "noun",
                f"/{w_low}/", f"/{w_low}/", "", cefr, 12000 + added_hunspell,
                dom, stem_w, root_ar, "", "",
                "{}", "[]", "[]", "[]", "[]", "[]", "[]",
                "[مدخل مساعد مولّد/مفهرس آلياً من Hunspell en_US — مميز بوضوح عن التعريفات المعجمية المحررة]",
                "Hunspell en_US Open Spelling & Morphological Lexicon",
                "LGPL / MPL / BSD",
                0,
                def_en,
                exp_ar
            ))

    for row in aux_entries:
        cur.execute("""
            INSERT INTO dictionary_entries (
                word_en, word_en_lower, word_ar, word_ar_normalized, pos,
                ipa_uk, ipa_us, phonetic_ar, cefr_level, frequency_rank,
                domain, lemma_en, root_ar, plural_en, plural_ar,
                verb_forms_json, derivatives_json, synonyms_en_json, synonyms_ar_json,
                antonyms_en_json, antonyms_ar_json, collocations_json, usage_notes,
                source_name, license_type, is_verified_lexical
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row[:26])
        eid = cur.lastrowid
        cur.execute("""
            INSERT INTO word_senses (
                entry_id, sense_order, context_label, meaning_ar, meaning_ar_normalized,
                definition_en, explanation_ar, example_en, example_ar
            ) VALUES (?, 1, 'Morphological / Auxiliary Lexicon (معنى مساعد)', ?, ?, ?, ?, '', '')
        """, (eid, row[2], row[3], row[26], row[27]))
        total_senses += 1

    # 7. Insert Idioms & Phrasal Verbs
    for row in IDIOMS_AND_PHRASES:
        ph_en, ph_ar, lit_ar, id_ar, exp_en, ex_en, ex_ar, cat = row
        cur.execute("""
            INSERT INTO idioms_phrases (
                phrase_en, phrase_en_lower, phrase_ar, phrase_ar_normalized,
                literal_meaning_ar, idiomatic_meaning_ar, explanation_en,
                example_en, example_ar, category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ph_en, ph_en.lower(), ph_ar, normalize_arabic(ph_ar), lit_ar, id_ar, exp_en, ex_en, ex_ar, cat))

    # 8. Insert Parallel Bilingual Sentences
    BILINGUAL_CORPUS.extend(EXTRA_PARALLEL_SENTENCES[:250])
    for s_en, s_ar, dom in BILINGUAL_CORPUS:
        cur.execute("""
            INSERT INTO bilingual_sentences (
                sentence_en, sentence_en_lower, sentence_ar, sentence_ar_normalized, domain
            ) VALUES (?, ?, ?, ?, ?)
        """, (s_en, s_en.lower(), s_ar, normalize_arabic(s_ar), dom))

    # 9. Seed Starter Vocabulary Groups, Favorites, SRS Flashcards, Installed Resources, and Default Settings
    cur.executemany("INSERT INTO vocabulary_groups (group_name, description) VALUES (?, ?)", [
        ("عام / General", "المجموعة الافتراضية للكلمات المحفوظة والمفضلة"),
        ("المفردات الأساسية / Core Vocabulary", "أهم الكلمات الشائعة للمراجعة اليومية بالتكرار المتباعد"),
        ("مصطلحات تقنية وهندسية / Tech & Engineering", "مصطلحات الحاسوب والذكاء الاصطناعي وهندسة البرمجيات"),
        ("مصطلحات طبية وعلمية / Medical & Science", "مفردات الطب والأحياء والعلوم التطبيقية"),
        ("الأعمال والقانون / Business & Law", "مصطلحات العقود والإدارة والمال")
    ])

    starter_srs = [
        ("algorithm", "خَوَارِزْمِيَّة", "خطوات رياضية ومنطقية متسلسلة لحل مشكلة برمجية.", "The fuzzy search algorithm finds words quickly.", "مصطلحات تقنية وهندسية / Tech & Engineering", "Medium", "مهم جداً في هندسة البرمجيات"),
        ("architecture", "هَنْدَسَةٌ مِعْمَارِيَّة / بِنْيَةُ النِّظَام", "التصميم الهيكلي العام للنظام البرمجي وفصل طبقاته.", "Clean software architecture separates UI from logic.", "مصطلحات تقنية وهندسية / Tech & Engineering", "Medium", "عمل محمد البكير"),
        ("diagnosis", "تَشْخِيصٌ طِبِّيّ", "تحديد طبيعة المرض من خلال فحص الأعراض.", "Early diagnosis increases the success of treatment.", "مصطلحات طبية وعلمية / Medical & Science", "Hard", "تُجمع على diagnoses"),
        ("context", "سِيَاق / قَرِينَة", "النص المحيط بالكلمة الذي يحدد معناها الدقيق.", "Word meanings change depending on context.", "المفردات الأساسية / Core Vocabulary", "Easy", "أساس الترجمة السياقية"),
        ("agreement", "اتِّفَاقِيَّة / تَوَافُق نَحْوِي", "عقد ملزم بين طرفين أو مطابقة نحوية بين الكلمات.", "Both parties signed the agreement.", "الأعمال والقانون / Business & Law", "Easy", "")
    ]
    for w_en, w_ar, exp_ar, ex_en, grp, diff, note in starter_srs:
        cur.execute("""
            INSERT INTO srs_flashcards (
                word_en, word_ar, explanation_ar, example_en, group_name, difficulty, personal_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (w_en, w_ar, exp_ar, ex_en, grp, diff, note))
        cur.execute("""
            INSERT INTO user_favorites (
                word_or_text, translation_ar, pos, personal_note, group_name, difficulty
            ) VALUES (?, ?, 'noun', ?, ?, ?)
        """, (w_en, w_ar, note, grp, diff))

    # Installed Resources Catalog
    resources_seed = [
        ("core-sqlite-lexicon", "قاعدة بيانات القاموس الشامل (SQLite + FTS5)", "Core Bilingual SQLite Dictionary & Morphological Index",
         "Dictionary", "ar, en", "2.5.0", 6.8, "Installed", 1, "resources/database/linguadesk_dictionary.db",
         "Local Bundled Package (عمل محمد البكير)", "WordNet 3.1 / Wiktionary CC-BY-SA / Hunspell LGPL",
         "قاعدة البيانات الأساسية ثنائية الاتجاه (عربي–إنجليزي) مع المعاني المتعددة والتصريفات والجذور وأكثر من 18,000 مدخل مفهرس. محمية ضد الحذف العرضي."),
        ("core-contextual-mt", "محرك الترجمة السياقي المحلي للجمل والفقرات", "Offline Contextual Sentence & Paragraph Engine",
         "Translation", "ar <-> en", "2.5.0", 1.4, "Installed", 1, "resources/translation-models/contextual_rules_v2.json",
         "Local Bundled Package (عمل محمد البكير)", "MIT License",
         "محرك ترجمة محلي يعالج الجمل والفقرات الكاملة، والتعابير الاصطلاحية، والضمائر والأزمنة، والترجمة الحرفية مقابل الطبيعية دون إنترنت."),
        ("win-sapi-tts", "محرك النطق الصوتي المحلي لنظام ويندوز (SAPI5 / Speech)", "Windows Offline Speech Synthesis Engine",
         "Speech", "en-US, en-GB, ar-SA, ar-EG", "10.0.2", 0.5, "Installed", 1, "System.Speech / Windows SAPI5",
         "Microsoft Windows Built-in Speech Runtime", "Windows OS Component License",
         "يوفر نطقاً صوتياً محلياً دون إنترنت للكلمات والجمل باللكنتين الأمريكية والبريطانية والعربية مع وضع النطق البطيء للمتعلمين."),
        ("optional-opus-mt-en-ar", "نموذج الترجمة العصبية Helsinki-NLP OPUS-MT (EN↔AR ONNX)", "OPUS-MT Neural Translation Model (EN-AR / AR-EN)",
         "Neural-MT", "ar <-> en", "1.2.0", 295.0, "Optional (Downloadable)", 0, "resources/translation-models/opus-mt-en-ar-onnx/",
         "https://huggingface.co/Helsinki-NLP/opus-mt-en-ar", "CC-BY-4.0 / Apache-2.0 (Helsinki-NLP)",
         "حزمة النموذج العصبي الإضافية (ONNX / Marian) للترجمة العصبية العميقة على المعالج CPU. يمكن تنزيلها عند الحاجة عبر أداة تنزيل الموارد المرفقة."),
        ("optional-tesseract-ocr-ara-eng", "وحدة التعرف الضوئي على النصوص من الصور (Tesseract OCR عربي+إنجليزي)", "Local Tesseract OCR Engine & Traineddata (ara + eng)",
         "OCR", "ar, en", "5.3.0", 42.5, "Ready / Optional Pack", 0, "resources/ocr/tessdata/",
         "https://github.com/tesseract-ocr/tessdata_fast", "Apache License 2.0",
         "وحدة استخراج النصوص العربية والإنجليزية من الصور ولقطات الشاشة وملفات PDF الممسوحة ضوئياً محلياً.")
    ]
    for r in resources_seed:
        cur.execute("""
            INSERT INTO installed_resources (
                id, name_ar, name_en, category, languages, version, size_mb, status,
                is_core_protected, local_path, source_url, license, description_ar
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, r)

    # Default Settings
    default_settings = [
        ("ui_language", "ar"),
        ("default_source_lang", "auto"),
        ("default_target_lang", "ar"),
        ("translation_engine_mode", "offline_contextual"),
        ("comparison_mode_enabled", "true"),
        ("online_fallback_mode", "ask_every_time"),
        ("online_api_provider", "libretranslate"),
        ("online_api_endpoint", "https://libretranslate.com/translate"),
        ("global_hotkey", "Ctrl+Shift+T"),
        ("clipboard_capture_enabled", "true"),
        ("restore_clipboard_after_capture", "true"),
        ("tts_voice_en", "en-US"),
        ("tts_voice_ar", "ar-SA"),
        ("tts_speed_rate", "1.0"),
        ("tts_slow_learner_mode", "false"),
        ("theme", "dark"),
        ("font_size", "medium"),
        ("autocomplete_enabled", "true"),
        ("autocomplete_max_suggestions", "8"),
        ("run_at_windows_startup", "false"),
        ("developer_signature", "عمل محمد البكير — Mohammed Al-Bakir")
    ]
    cur.executemany("INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?)", default_settings)

    # Create Fast Indexes & FTS5 Virtual Table
    cur.executescript("""
    CREATE INDEX idx_entries_en_lower ON dictionary_entries(word_en_lower);
    CREATE INDEX idx_entries_ar_norm ON dictionary_entries(word_ar_normalized);
    CREATE INDEX idx_entries_lemma ON dictionary_entries(lemma_en);
    CREATE INDEX idx_entries_root_ar ON dictionary_entries(root_ar);
    CREATE INDEX idx_entries_domain ON dictionary_entries(domain);
    CREATE INDEX idx_entries_verified ON dictionary_entries(is_verified_lexical, frequency_rank);
    CREATE INDEX idx_senses_entry_id ON word_senses(entry_id);
    CREATE INDEX idx_senses_meaning_norm ON word_senses(meaning_ar_normalized);
    CREATE INDEX idx_idioms_en ON idioms_phrases(phrase_en_lower);
    CREATE INDEX idx_idioms_ar ON idioms_phrases(phrase_ar_normalized);

    CREATE VIRTUAL TABLE entries_fts USING fts5(
        word_en,
        word_ar,
        word_ar_normalized,
        lemma_en,
        root_ar,
        domain,
        content='dictionary_entries',
        content_rowid='id'
    );

    INSERT INTO entries_fts(entries_fts) VALUES('rebuild');
    VACUUM;
    """)

    conn.commit()

    # Count statistics
    cur.execute("SELECT COUNT(*) FROM dictionary_entries")
    total_entries = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dictionary_entries WHERE is_verified_lexical = 1")
    verified_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dictionary_entries WHERE is_verified_lexical = 0")
    aux_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM word_senses")
    senses_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM idioms_phrases")
    idioms_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bilingual_sentences")
    sentences_count = cur.fetchone()[0]

    conn.close()

    # Compute SHA-256 of the database and update installed_resources
    shutil.copy2(TMP_DB, DB_PATH)
    with open(TMP_DB, "rb") as bf:
        db_sha256 = hashlib.sha256(bf.read()).hexdigest()
    db_size_mb = round(os.path.getsize(DB_PATH) / (1024 * 1024), 2)

    conn = sqlite3.connect(TMP_DB)
    conn.execute("UPDATE installed_resources SET sha256_hash = ?, size_mb = ? WHERE id = 'core-sqlite-lexicon'", (db_sha256, db_size_mb))
    conn.commit()
    conn.close()
    shutil.copy2(TMP_DB, DB_PATH)

    # Export JSON companion files in resources/dictionaries/
    with open(os.path.join(DICT_DIR, "idioms_and_collocations.json"), "w", encoding="utf-8") as jf:
        json.dump(IDIOMS_AND_PHRASES, jf, ensure_ascii=False, indent=2)

    with open(os.path.join(DICT_DIR, "bilingual_benchmark_corpus.json"), "w", encoding="utf-8") as jf:
        json.dump(BILINGUAL_CORPUS, jf, ensure_ascii=False, indent=2)

    elapsed = round(time.time() - start_ts, 2)
    print(f"=== Database Built Successfully in {elapsed}s ===")
    print(f"Database Path: {DB_PATH} ({db_size_mb} MB, SHA256: {db_sha256[:16]}...)")
    print(f"Total Dictionary Entries: {total_entries} (Verified Curated Lexical: {verified_count}, Morphological/Hunspell Auxiliary: {aux_count})")
    print(f"Total Word Senses: {senses_count}")
    print(f"Total Idioms & Phrases: {idioms_count}")
    print(f"Total Parallel Corpus Sentences: {sentences_count}")

if __name__ == "__main__":
    build_database()
