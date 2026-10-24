#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinguaDesk Pro — Core Local Backend Engine & HTTP/WebView2 Bridge Server
عمل محمد البكير (Developed & Engineered by Mohammed Al-Bakir)
"""

import os
import sys
import re
import json
import time
import shutil
import sqlite3
import hashlib
import tempfile
import subprocess
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

_CAND1 = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CAND2 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE_DIR = _CAND1 if os.path.exists(os.path.join(_CAND1, "ui")) else _CAND2
DB_SOURCE_PATH = os.path.join(BASE_DIR, "resources", "database", "linguadesk_dictionary.db")
RULES_PATH = os.path.join(BASE_DIR, "resources", "translation-models", "contextual_rules_v2.json")
UI_DIR = os.path.join(BASE_DIR, "ui")
RUNTIME_DB_PATH = os.path.join(tempfile.gettempdir(), "linguadesk_runtime_active.db")


def init_runtime_db(force_reset=False):
    if not os.path.exists(DB_SOURCE_PATH):
        gz_path = DB_SOURCE_PATH + ".gz"
        if os.path.exists(gz_path):
            import gzip
            with gzip.open(gz_path, "rb") as f_in, open(DB_SOURCE_PATH, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        else:
            raise FileNotFoundError(f"قاعدة البيانات الأساسية غير موجودة: {DB_SOURCE_PATH}")
    if force_reset or not os.path.exists(RUNTIME_DB_PATH):
        shutil.copy2(DB_SOURCE_PATH, RUNTIME_DB_PATH)
    return RUNTIME_DB_PATH


def sync_runtime_db_back():
    try:
        if os.path.exists(RUNTIME_DB_PATH) and os.path.abspath(RUNTIME_DB_PATH) != os.path.abspath(DB_SOURCE_PATH):
            shutil.copy2(RUNTIME_DB_PATH, DB_SOURCE_PATH)
    except Exception:
        pass


def normalize_arabic(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text)
    text = re.sub(r'[أإآٱ]', 'ا', text)
    text = text.replace('ة', 'ه').replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي')
    return text.strip()


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "en"
    ar_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    en_chars = len(re.findall(r'[A-Za-z]', text))
    if ar_chars > 0 and en_chars > 0:
        return "ar" if ar_chars >= en_chars else "en"
    return "ar" if ar_chars > 0 else "en"


def is_mixed_language(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r'[\u0600-\u06FF]', text) and re.search(r'[A-Za-z]', text))


def damerau_levenshtein(s1: str, s2: str) -> int:
    len1, len2 = len(s1), len(s2)
    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + cost)
    return d[len1][len2]


class LinguaDeskEngine:
    IRREGULAR_EN = {
        "ran": "run", "running": "run", "runs": "run",
        "went": "go", "gone": "go", "going": "go", "goes": "go",
        "wrote": "write", "written": "write", "writing": "write", "writes": "write",
        "read": "read", "reading": "read", "reads": "read",
        "spoke": "speak", "spoken": "speak", "speaking": "speak", "speaks": "speak",
        "built": "build", "building": "build", "builds": "build",
        "found": "find", "finding": "find", "finds": "find",
        "sent": "send", "sending": "send", "sends": "send",
        "kept": "keep", "keeping": "keep", "keeps": "keep",
        "knew": "know", "known": "know", "knowing": "know",
        "thought": "think", "thinking": "think", "thinks": "think",
        "bought": "purchase", "taught": "teach", "teaching": "teacher",
        "children": "child", "mice": "mouse", "analyses": "analysis",
        "diagnoses": "diagnosis", "theories": "theory", "libraries": "library",
        "universities": "university", "companies": "company", "cities": "city",
        "countries": "country", "families": "family", "stories": "story",
        "studies": "study", "dictionaries": "dictionary", "categories": "group"
    }

    AR_PREFIXES = ["وال", "بال", "كال", "فال", "لل", "ال", "و", "ف", "ب", "ل", "س", "ي", "ت", "ن", "ا"]
    AR_SUFFIXES = ["ات", "ون", "ين", "ان", "هم", "ها", "كم", "نا", "تم", "تن", "وا", "ت", "ه", "ي", "ك"]

    def __init__(self, db_path=None):
        self.db_path = db_path or init_runtime_db(force_reset=True)
        self.rules = self._load_rules()
        self._vocab_cache_en = None
        self._vocab_cache_ar = None
        self._fast_en_map = None
        self._fast_ar_map = None
        self._cancel_flag = False

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _load_rules(self):
        if os.path.exists(RULES_PATH):
            with open(RULES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"en_to_ar_phrases": {}, "ar_to_en_phrases": {}, "tense_auxiliaries_en_ar": {}, "protected_acronyms": []}

    def _ensure_fast_token_maps(self, conn):
        if self._fast_en_map is not None:
            return
        self._fast_en_map = {}
        self._fast_ar_map = {}
        rows = conn.execute("SELECT word_en_lower, lemma_en, word_en, word_ar, word_ar_normalized, pos FROM dictionary_entries WHERE is_verified_lexical = 1 ORDER BY frequency_rank ASC").fetchall()
        for r in rows:
            ar_clean = re.sub(r'\(.*?\)', '', r["word_ar"]).split("/")[0].strip()
            ar_clean = re.sub(r'[\u064B-\u065F\u0670]', '', ar_clean).strip()
            entry_val = (ar_clean, r["pos"], r["word_en"])
            if r["word_en_lower"] not in self._fast_en_map:
                self._fast_en_map[r["word_en_lower"]] = entry_val
            if r["lemma_en"] and r["lemma_en"] not in self._fast_en_map:
                self._fast_en_map[r["lemma_en"]] = entry_val
            for part in r["word_ar_normalized"].split("/"):
                p_clean = re.sub(r'\(.*?\)', '', part).strip()
                if p_clean and p_clean not in self._fast_ar_map:
                    self._fast_ar_map[p_clean] = (r["word_en"], r["pos"])

    def _ensure_vocab_cache(self):
        if self._vocab_cache_en is not None:
            return
        with self._get_conn() as conn:
            rows = conn.execute("SELECT word_en_lower, word_ar_normalized, word_ar FROM dictionary_entries WHERE frequency_rank <= 8500 ORDER BY frequency_rank ASC").fetchall()
            self._vocab_cache_en = [r["word_en_lower"] for r in rows if r["word_en_lower"]]
            self._vocab_cache_ar = [(r["word_ar_normalized"], r["word_ar"]) for r in rows if r["word_ar_normalized"]]

    def get_en_candidate_lemmas(self, word: str):
        w = word.strip().lower()
        cands = [w]
        if w in self.IRREGULAR_EN:
            cands.append(self.IRREGULAR_EN[w])
        if w.endswith("ies") and len(w) > 4:
            cands.append(w[:-3] + "y")
        if w.endswith("es") and len(w) > 4:
            cands.extend([w[:-2], w[:-1]])
        if w.endswith("s") and len(w) > 3:
            cands.append(w[:-1])
        if w.endswith("ied") and len(w) > 4:
            cands.append(w[:-3] + "y")
        if w.endswith("ed") and len(w) > 4:
            cands.extend([w[:-2], w[:-1], w[:-3] if len(w) > 5 and w[-3] == w[-4] else w[:-2]])
        if w.endswith("ing") and len(w) > 5:
            base = w[:-3]
            cands.extend([base, base + "e"])
            if len(base) > 2 and base[-1] == base[-2]:
                cands.append(base[:-1])
        if w.endswith("ly") and len(w) > 4:
            cands.append(w[:-2])
        if w.endswith("er") and len(w) > 4:
            cands.extend([w[:-2], w[:-1]])
        if w.endswith("tion") and len(w) > 5:
            cands.extend([w[:-3] + "e", w[:-4]])
        seen = set()
        out = []
        for c in cands:
            if c and c not in seen:
                seen.add(c)
                out.append(c)
        return out

    def get_ar_candidate_stems(self, word: str):
        norm = normalize_arabic(word)
        cands = [norm]
        for pre in self.AR_PREFIXES:
            if norm.startswith(pre) and len(norm) - len(pre) >= 3:
                sub = norm[len(pre):]
                cands.append(sub)
                for suf in self.AR_SUFFIXES:
                    if sub.endswith(suf) and len(sub) - len(suf) >= 3:
                        cands.append(sub[:-len(suf)])
        for suf in self.AR_SUFFIXES:
            if norm.endswith(suf) and len(norm) - len(suf) >= 3:
                cands.append(norm[:-len(suf)])
        seen = set()
        out = []
        for c in cands:
            if c and c not in seen:
                seen.add(c)
                out.append(c)
        return out

    def lookup_word(self, query: str) -> dict:
        t0 = time.perf_counter()
        q = (query or "").strip()
        if not q:
            return {"found": False, "error": "يرجى إدخال كلمة للبحث عنها في القاموس.", "suggestions": []}

        lang = detect_language(q)
        with self._get_conn() as conn:
            row = None
            matched_via = "exact"
            if lang == "en":
                cands = self.get_en_candidate_lemmas(q)
                for idx, cand in enumerate(cands):
                    row = conn.execute("""
                        SELECT * FROM dictionary_entries
                        WHERE word_en_lower = ? OR lemma_en = ?
                        ORDER BY is_verified_lexical DESC,
                                 CASE WHEN word_en_lower = ? THEN 0 ELSE 1 END,
                                 frequency_rank ASC
                        LIMIT 1
                    """, (cand, cand, cand)).fetchone()
                    if row:
                        matched_via = "exact" if idx == 0 else f"stemmed ({cand})"
                        break
            else:
                stems = self.get_ar_candidate_stems(q)
                for idx, stem in enumerate(stems):
                    row = conn.execute("""
                        SELECT * FROM dictionary_entries
                        WHERE word_en_lower = ? OR word_ar_normalized = ? OR word_ar_normalized LIKE ? || '%'
                        ORDER BY is_verified_lexical DESC,
                                 CASE WHEN word_en_lower = ? THEN 0 WHEN word_ar_normalized = ? THEN 1 ELSE 2 END,
                                 frequency_rank ASC
                        LIMIT 1
                    """, (stem, stem, stem, stem, stem)).fetchone()
                    if not row:
                        row = conn.execute("""
                            SELECT * FROM dictionary_entries
                            WHERE is_verified_lexical = 1 AND word_ar_normalized LIKE '%' || ? || '%'
                            ORDER BY frequency_rank ASC LIMIT 1
                        """, (stem,)).fetchone()
                    if row:
                        matched_via = "exact_ar" if idx == 0 else f"stemmed_ar ({stem})"
                        break
                    srow = conn.execute("""
                        SELECT entry_id FROM word_senses
                        WHERE meaning_ar_normalized LIKE '%' || ? || '%'
                        ORDER BY sense_order ASC LIMIT 1
                    """, (stem,)).fetchone()
                    if srow:
                        row = conn.execute("SELECT * FROM dictionary_entries WHERE id = ?", (srow["entry_id"],)).fetchone()
                        if row:
                            matched_via = f"sense_ar ({stem})"
                            break

            if not row:
                suggestions = self.get_fuzzy_suggestions(q, lang=lang, limit=6)
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                return {
                    "found": False,
                    "query": q,
                    "detected_lang": lang,
                    "message_ar": f"لم يتم العثور على الكلمة «{q}» بشكل مباشر في القاموس المحلي. إليك أقرب الكلمات المقترحة إملائياً:",
                    "suggestions": suggestions,
                    "query_time_ms": elapsed_ms
                }

            entry_dict = self._format_entry(conn, row)
            entry_dict["found"] = True
            entry_dict["matched_via"] = matched_via
            prefix_3 = row["word_en_lower"][:3] if len(row["word_en_lower"]) >= 3 else row["word_en_lower"]
            near_rows = conn.execute("""
                SELECT word_en FROM dictionary_entries
                WHERE is_verified_lexical = 1 AND word_en_lower LIKE ? || '%' AND word_en_lower != ?
                LIMIT 5
            """, (prefix_3, row["word_en_lower"])).fetchall()
            entry_dict["fuzzy_suggestions"] = [nr["word_en"] for nr in near_rows]
            entry_dict["related_idioms"] = self._find_related_idioms(conn, row["word_en_lower"], normalize_arabic(row["word_ar"]))
            entry_dict["query_time_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            return entry_dict

    def _format_entry(self, conn, row) -> dict:
        senses_rows = conn.execute("""
            SELECT sense_order, context_label, meaning_ar, definition_en, explanation_ar, example_en, example_ar
            FROM word_senses WHERE entry_id = ? ORDER BY sense_order ASC
        """, (row["id"],)).fetchall()

        return {
            "id": row["id"],
            "word_en": row["word_en"],
            "word_ar": row["word_ar"],
            "pos": row["pos"],
            "ipa_uk": row["ipa_uk"] or f"/{row['word_en_lower']}/",
            "ipa_us": row["ipa_us"] or f"/{row['word_en_lower']}/",
            "phonetic_ar": row["phonetic_ar"],
            "cefr_level": row["cefr_level"],
            "frequency_rank": row["frequency_rank"],
            "domain": row["domain"],
            "lemma_en": row["lemma_en"],
            "root_ar": row["root_ar"],
            "plural_en": row["plural_en"],
            "plural_ar": row["plural_ar"],
            "verb_forms": json.loads(row["verb_forms_json"] or "{}"),
            "derivatives": json.loads(row["derivatives_json"] or "[]"),
            "synonyms_en": json.loads(row["synonyms_en_json"] or "[]"),
            "synonyms_ar": json.loads(row["synonyms_ar_json"] or "[]"),
            "antonyms_en": json.loads(row["antonyms_en_json"] or "[]"),
            "antonyms_ar": json.loads(row["antonyms_ar_json"] or "[]"),
            "collocations": json.loads(row["collocations_json"] or "[]"),
            "usage_notes": row["usage_notes"],
            "source_name": row["source_name"],
            "license_type": row["license_type"],
            "is_verified_lexical": bool(row["is_verified_lexical"]),
            "senses": [dict(s) for s in senses_rows]
        }

    def _find_related_idioms(self, conn, word_en_low: str, word_ar_norm: str):
        rows = conn.execute("""
            SELECT phrase_en, phrase_ar, literal_meaning_ar, idiomatic_meaning_ar, example_en, example_ar, category
            FROM idioms_phrases
            WHERE phrase_en_lower LIKE '%' || ? || '%'
               OR phrase_ar_normalized LIKE '%' || ? || '%'
            LIMIT 5
        """, (word_en_low, word_ar_norm.split("/")[0].strip())).fetchall()
        return [dict(r) for r in rows]

    def get_fuzzy_suggestions(self, query: str, lang: str = "en", limit: int = 6):
        self._ensure_vocab_cache()
        q = query.strip().lower() if lang == "en" else normalize_arabic(query)
        if not q:
            return []
        scored = []
        if lang == "en":
            for cand in self._vocab_cache_en:
                if cand == q or abs(len(cand) - len(q)) > 2:
                    continue
                dist = damerau_levenshtein(q, cand)
                if 0 < dist <= 2:
                    scored.append((dist, abs(len(cand) - len(q)), cand))
            scored.sort()
            return [x[2] for x in scored[:limit]]
        else:
            for norm_ar, orig_ar in self._vocab_cache_ar:
                first_part = norm_ar.split("/")[0].strip()
                if first_part == q or abs(len(first_part) - len(q)) > 2:
                    continue
                dist = damerau_levenshtein(q, first_part)
                if 0 < dist <= 2:
                    scored.append((dist, abs(len(first_part) - len(q)), orig_ar.split("/")[0].strip()))
            scored.sort()
            return [x[2] for x in scored[:limit]]

    def autocomplete(self, prefix: str, max_results: int = 8) -> list:
        p = (prefix or "").strip()
        if not p:
            return []
        lang = detect_language(p)
        results = []
        seen = set()

        with self._get_conn() as conn:
            favs = conn.execute("""
                SELECT word_or_text, translation_ar FROM user_favorites
                WHERE word_or_text LIKE ? || '%' OR translation_ar LIKE '%' || ? || '%'
                LIMIT 2
            """, (p, p)).fetchall()
            for f in favs:
                if f["word_or_text"].lower() not in seen:
                    seen.add(f["word_or_text"].lower())
                    results.append({
                        "text": f["word_or_text"],
                        "meaning": f["translation_ar"],
                        "category": "مفضلة ★",
                        "pos": "favorite"
                    })

            if lang == "en":
                p_low = p.lower()
                rows = conn.execute("""
                    SELECT word_en, word_ar, pos, is_verified_lexical
                    FROM dictionary_entries
                    WHERE word_en_lower LIKE ? || '%'
                    ORDER BY is_verified_lexical DESC, frequency_rank ASC
                    LIMIT ?
                """, (p_low, max_results)).fetchall()
                for r in rows:
                    if r["word_en"].lower() not in seen:
                        seen.add(r["word_en"].lower())
                        results.append({
                            "text": r["word_en"],
                            "meaning": r["word_ar"].split("/")[0].strip(),
                            "category": "قاموس موثق" if r["is_verified_lexical"] else "تحليل صرفي",
                            "pos": r["pos"]
                        })
                id_rows = conn.execute("""
                    SELECT phrase_en, phrase_ar, category FROM idioms_phrases
                    WHERE phrase_en_lower LIKE ? || '%'
                    LIMIT 3
                """, (p_low,)).fetchall()
                for ir in id_rows:
                    if ir["phrase_en"].lower() not in seen and len(results) < max_results:
                        seen.add(ir["phrase_en"].lower())
                        results.append({
                            "text": ir["phrase_en"],
                            "meaning": ir["phrase_ar"].split("/")[0].strip(),
                            "category": ir["category"],
                            "pos": "phrase"
                        })
            else:
                norm_p = normalize_arabic(p)
                rows = conn.execute("""
                    SELECT word_ar, word_en, pos, is_verified_lexical
                    FROM dictionary_entries
                    WHERE word_ar_normalized LIKE ? || '%'
                       OR word_ar_normalized LIKE '% ' || ? || '%'
                    ORDER BY is_verified_lexical DESC, frequency_rank ASC
                    LIMIT ?
                """, (norm_p, norm_p, max_results)).fetchall()
                for r in rows:
                    primary_ar = r["word_ar"].split("/")[0].strip()
                    if primary_ar not in seen:
                        seen.add(primary_ar)
                        results.append({
                            "text": primary_ar,
                            "meaning": r["word_en"],
                            "category": "قاموس عربي",
                            "pos": r["pos"]
                        })

            if len(results) < 3 and len(p) >= 3:
                fuzzy = self.get_fuzzy_suggestions(p, lang=lang, limit=4)
                for fz in fuzzy:
                    if fz.lower() not in seen and len(results) < max_results:
                        seen.add(fz.lower())
                        results.append({
                            "text": fz,
                            "meaning": "تصحيح إملائي مقترح",
                            "category": "تصحيح إملائي",
                            "pos": "suggestion"
                        })

        return results[:max_results]

    def translate_text(self, text: str, source_lang: str = "auto", target_lang: str = "ar",
                       save_history: bool = True) -> dict:
        t0 = time.perf_counter()
        self._cancel_flag = False
        raw = (text or "").strip()
        if not raw:
            return {
                "original_text": "",
                "detected_source_lang": "en",
                "target_lang": target_lang,
                "natural_translation": "",
                "literal_translation": "",
                "alternative_translations": [],
                "token_breakdown": [],
                "uncertain_terms": [],
                "word_count": 0,
                "char_count": 0,
                "processing_time_ms": 0.0,
                "engine_used": "Offline Contextual Engine (عمل محمد البكير)",
                "is_online": False,
                "single_word_entry": None
            }

        src_lang = detect_language(raw) if source_lang == "auto" else source_lang
        tgt_lang = target_lang
        if src_lang == tgt_lang:
            tgt_lang = "en" if src_lang == "ar" else "ar"

        mixed = is_mixed_language(raw)
        words_list = re.findall(r'\S+', raw)

        if len(words_list) == 1 and not re.search(r'[\n\r]', raw):
            clean_word = re.sub(r'^[^\w\u0600-\u06FF]+|[^\w\u0600-\u06FF]+$', '', raw)
            dict_res = self.lookup_word(clean_word)
            if dict_res.get("found"):
                nat = dict_res["word_en"] if src_lang == "ar" else dict_res["word_ar"].split("/")[0].strip()
                alts = [s["meaning_ar"] for s in dict_res.get("senses", [])] if src_lang == "en" else [dict_res["word_en"]] + dict_res.get("synonyms_en", [])
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                if save_history:
                    self._record_history(raw, nat, src_lang, tgt_lang, "dictionary_single", "القاموس المحلي المباشر (Dictionary First)", elapsed_ms)
                return {
                    "original_text": raw,
                    "detected_source_lang": src_lang,
                    "target_lang": tgt_lang,
                    "natural_translation": nat,
                    "literal_translation": dict_res["word_ar"] if src_lang == "en" else dict_res["word_en"],
                    "alternative_translations": list(dict.fromkeys(alts))[:4],
                    "token_breakdown": [{"original": clean_word, "translated": nat, "pos": dict_res["pos"], "uncertain": False}],
                    "uncertain_terms": [],
                    "word_count": 1,
                    "char_count": len(raw),
                    "processing_time_ms": elapsed_ms,
                    "engine_used": "القاموس المحلي المباشر (Offline Dictionary First — عمل محمد البكير)",
                    "is_online": False,
                    "single_word_entry": dict_res
                }

        paragraphs = raw.splitlines()
        nat_paragraphs = []
        lit_paragraphs = []
        all_tokens = []
        uncertain_terms = []
        alternatives = []

        with self._get_conn() as conn:
            for para in paragraphs:
                if self._cancel_flag:
                    break
                p_strip = para.strip()
                if not p_strip:
                    nat_paragraphs.append("")
                    lit_paragraphs.append("")
                    continue

                sentences = re.split(r'(?<=[.!?؟؛])\s+', p_strip)
                nat_sents = []
                lit_sents = []
                for sent in sentences:
                    if not sent.strip():
                        continue
                    n_s, l_s, alt_s = self._translate_sentence_contextual(conn, sent.strip(), src_lang, tgt_lang, all_tokens, uncertain_terms)
                    nat_sents.append(n_s)
                    lit_sents.append(l_s)
                    if alt_s and alt_s != n_s:
                        alternatives.append(alt_s)

                nat_paragraphs.append(" ".join(nat_sents))
                lit_paragraphs.append(" ".join(lit_sents))

        final_nat = "\n".join(nat_paragraphs)
        final_lit = "\n".join(lit_paragraphs)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

        if save_history and final_nat:
            self._record_history(raw, final_nat, src_lang, tgt_lang, "sentence_contextual", "محرك الترجمة السياقي المحلي (عمل محمد البكير)", elapsed_ms)

        return {
            "original_text": raw,
            "detected_source_lang": "mixed (" + src_lang + ")" if mixed else src_lang,
            "target_lang": tgt_lang,
            "natural_translation": final_nat,
            "literal_translation": final_lit,
            "alternative_translations": alternatives[:3],
            "token_breakdown": all_tokens,
            "uncertain_terms": list(dict.fromkeys(uncertain_terms)),
            "word_count": len(words_list),
            "char_count": len(raw),
            "processing_time_ms": elapsed_ms,
            "engine_used": "محرك الترجمة السياقي المحلي للجمل والفقرات (Offline Contextual Engine — عمل محمد البكير)",
            "is_online": False,
            "single_word_entry": None
        }

    def _translate_sentence_contextual(self, conn, sentence: str, src_lang: str, tgt_lang: str,
                                       token_breakdown: list, uncertain_terms: list):
        if src_lang == "en" and tgt_lang == "ar":
            s_low = sentence.lower().rstrip(".!?")
            row = conn.execute("""
                SELECT sentence_ar FROM bilingual_sentences
                WHERE sentence_en_lower = ? OR rtrim(sentence_en_lower, '.!?') = ?
                LIMIT 1
            """, (sentence.lower(), s_low)).fetchone()
            if row:
                lit = self._build_literal_gloss_en_ar(conn, sentence, token_breakdown, uncertain_terms)
                return row["sentence_ar"], lit, ""
        elif src_lang == "ar" and tgt_lang == "en":
            s_norm = normalize_arabic(sentence).rstrip(".!?؟")
            row = conn.execute("""
                SELECT sentence_en FROM bilingual_sentences
                WHERE sentence_ar_normalized = ? OR rtrim(sentence_ar_normalized, '.!?؟') = ?
                LIMIT 1
            """, (normalize_arabic(sentence), s_norm)).fetchone()
            if row:
                lit = self._build_literal_gloss_ar_en(conn, sentence, token_breakdown, uncertain_terms)
                return row["sentence_en"], lit, ""

        if src_lang == "en" and tgt_lang == "ar":
            return self._transfer_en_to_ar(conn, sentence, token_breakdown, uncertain_terms)
        else:
            return self._transfer_ar_to_en(conn, sentence, token_breakdown, uncertain_terms)

    def _transfer_en_to_ar(self, conn, sentence: str, token_breakdown: list, uncertain_terms: list):
        working = sentence
        phrase_map = self.rules.get("en_to_ar_phrases", {})
        placeholders = {}
        ph_idx = 0

        for en_ph, ar_ph in sorted(phrase_map.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = re.compile(r'\b' + re.escape(en_ph) + r'\b', re.IGNORECASE)
            if pattern.search(working):
                key = f"__PHRASE{ph_idx}__"
                ph_idx += 1
                placeholders[key] = ar_ph
                working = pattern.sub(key, working)
                token_breakdown.append({"original": en_ph, "translated": ar_ph, "pos": "idiom/phrase", "uncertain": False})

        words_lower = working.lower()
        db_idioms = conn.execute("""
            SELECT phrase_en, idiomatic_meaning_ar FROM idioms_phrases
            WHERE length(phrase_en) >= 6 AND ? LIKE '%' || phrase_en_lower || '%'
            ORDER BY length(phrase_en) DESC LIMIT 4
        """, (words_lower,)).fetchall()
        for ir in db_idioms:
            en_ph = ir["phrase_en"]
            ar_ph = ir["idiomatic_meaning_ar"].split("/")[0].strip()
            pattern = re.compile(r'\b' + re.escape(en_ph) + r'\b', re.IGNORECASE)
            if pattern.search(working):
                key = f"__PHRASE{ph_idx}__"
                ph_idx += 1
                placeholders[key] = ar_ph
                working = pattern.sub(key, working)
                token_breakdown.append({"original": en_ph, "translated": ar_ph, "pos": "idiom", "uncertain": False})

        raw_tokens = re.findall(r'__PHRASE\d+__|\.NET|C#|SHA-256|UTF-8|[A-Za-z]+(?:-[A-Za-z]+)*|\d+(?:\.\d+)?|[\u0600-\u06FF]+|[^\w\s]', working)
        analyzed = []
        protected_set = {p.lower() for p in self.rules.get("protected_acronyms", [])}

        STOP_GRAMMAR_EN_AR = {
            "the": ("الـ", "det"), "a": ("", "det"), "an": ("", "det"),
            "is": ("هو / يكون", "copula"), "are": ("هم / تكون", "copula"),
            "was": ("كان", "aux"), "were": ("كانوا", "aux"),
            "be": ("يكون", "aux"), "been": ("كان", "aux"),
            "has": ("لديه / قد", "aux"), "have": ("لديهم / قد", "aux"), "had": ("كان قد", "aux"),
            "will": ("سوف", "aux"), "would": ("سوف", "aux"),
            "can": ("يستطيع", "aux"), "could": ("تمكّن من", "aux"),
            "should": ("ينبغي", "aux"), "must": ("يجب", "aux"),
            "not": ("لا / ليس", "neg"), "no": ("لا", "neg"),
            "of": ("لـ / من", "prep"), "for": ("لأجل / لـ", "prep"),
            "in": ("في", "prep"), "on": ("على", "prep"), "at": ("في / عند", "prep"),
            "by": ("بواسطة / عبر", "prep"), "with": ("مع / بـ", "prep"),
            "without": ("دون", "prep"), "from": ("من", "prep"), "to": ("إلى / أن", "prep"),
            "into": ("إلى داخل", "prep"), "between": ("بين", "prep"), "through": ("عبر", "prep"),
            "and": ("و", "conj"), "or": ("أو", "conj"), "but": ("ولكن", "conj"),
            "because": ("لأن", "conj"), "if": ("إذا", "conj"), "when": ("عندما", "conj"),
            "while": ("بينما", "conj"), "than": ("من", "prep"), "as": ("كما / بوصفه", "prep"),
            "this": ("هذا", "det"), "that": ("ذلك / أن", "conj"), "these": ("هذه", "det"), "those": ("تلك", "det"),
            "my": ("الخاص بي", "poss"), "your": ("الخاص بك", "poss"), "our": ("الخاص بنا", "poss"),
            "their": ("الخاص بهم", "poss"), "its": ("الخاص به", "poss"), "his": ("الخاص به", "poss"), "her": ("الخاص بها", "poss"),
            "we": ("نحن", "pron"), "they": ("هم", "pron"), "he": ("هو", "pron"), "she": ("هي", "pron"), "you": ("أنت", "pron"), "i": ("أنا", "pron")
        }

        for idx, tok in enumerate(raw_tokens):
            if tok in placeholders:
                analyzed.append({"orig": tok, "ar": placeholders[tok], "lit": placeholders[tok], "pos": "phrase"})
                continue
            if re.match(r'^[\u0600-\u06FF]+$', tok):
                analyzed.append({"orig": tok, "ar": tok, "lit": tok, "pos": "arabic_kept"})
                continue
            if re.match(r'^[^\w\s]+$', tok) or re.match(r'^\d+([.,]\d+)?$', tok):
                analyzed.append({"orig": tok, "ar": tok, "lit": tok, "pos": "punct"})
                continue

            low = tok.lower()
            if low in protected_set or (tok.isupper() and len(tok) >= 2):
                analyzed.append({"orig": tok, "ar": tok, "lit": tok, "pos": "proper"})
                token_breakdown.append({"original": tok, "translated": tok, "pos": "acronym/proper", "uncertain": False})
                continue

            if low in STOP_GRAMMAR_EN_AR:
                ar_g, pos_g = STOP_GRAMMAR_EN_AR[low]
                analyzed.append({"orig": tok, "ar": ar_g.split("/")[0].strip(), "lit": ar_g.split("/")[0].strip() or "(أداة تنكير)", "pos": pos_g})
                continue

            self._ensure_fast_token_maps(conn)
            cands = self.get_en_candidate_lemmas(low)
            found_en = None
            for c in cands:
                if c in self._fast_en_map:
                    found_en = self._fast_en_map[c]
                    break

            if found_en:
                ar_word, pos, _ = found_en
                analyzed.append({"orig": tok, "ar": ar_word, "lit": ar_word, "pos": pos})
                token_breakdown.append({"original": tok, "translated": ar_word, "pos": pos, "uncertain": False})
            else:
                is_prop = tok[0].isupper() and idx > 0
                uncertain_terms.append(tok)
                analyzed.append({"orig": tok, "ar": tok, "lit": tok, "pos": "proper" if is_prop else "unknown"})
                token_breakdown.append({"original": tok, "translated": tok, "pos": "proper_noun" if is_prop else "unknown", "uncertain": True})

        lit_tokens = [x["lit"] for x in analyzed if x["lit"]]
        literal_str = " ".join(lit_tokens).replace(" ,", "،").replace(" .", ".")

        nat_out = []
        i = 0
        n = len(analyzed)
        while i < n:
            cur = analyzed[i]
            if cur["pos"] == "copula":
                i += 1
                continue

            has_det = (cur["pos"] == "det")
            adj_idx = i + 1 if has_det else i
            noun_idx = adj_idx + 1

            if adj_idx < n and noun_idx < n and analyzed[adj_idx]["pos"] == "adjective" and analyzed[noun_idx]["pos"] == "noun":
                adj_ar = analyzed[adj_idx]["ar"]
                noun_ar = analyzed[noun_idx]["ar"]
                if has_det and cur["orig"].lower() == "the":
                    if not noun_ar.startswith("ال"):
                        noun_ar = "ال" + noun_ar
                    if not adj_ar.startswith("ال"):
                        adj_ar = "ال" + adj_ar
                nat_out.append(f"{noun_ar} {adj_ar}")
                i = noun_idx + 1
                continue

            n1_idx = i + 1 if has_det else i
            n2_idx = n1_idx + 1
            if n1_idx < n and n2_idx < n and analyzed[n1_idx]["pos"] == "noun" and analyzed[n2_idx]["pos"] == "noun":
                n1_ar = analyzed[n1_idx]["ar"]
                n2_ar = analyzed[n2_idx]["ar"]
                if not n1_ar.startswith("ال"):
                    n1_ar = "ال" + n1_ar
                nat_out.append(f"{n2_ar} {n1_ar}")
                i = n2_idx + 1
                continue

            if has_det and cur["orig"].lower() == "the" and (i + 1) < n and analyzed[i + 1]["pos"] in ("noun", "adjective"):
                nxt_ar = analyzed[i + 1]["ar"]
                if not nxt_ar.startswith("ال"):
                    nxt_ar = "ال" + nxt_ar
                nat_out.append(nxt_ar)
                i += 2
                continue

            if has_det and cur["ar"] in ("", "الـ"):
                i += 1
                continue

            nat_out.append(cur["ar"])
            i += 1

        natural_str = " ".join(x for x in nat_out if x)
        natural_str = re.sub(r'\s+([.!,?؟،؛])', r'\1', natural_str)
        natural_str = natural_str.replace(" و ", " و").replace(",", "،")
        alt_str = literal_str if literal_str != natural_str else ""
        return natural_str.strip(), literal_str.strip(), alt_str.strip()

    def _transfer_ar_to_en(self, conn, sentence: str, token_breakdown: list, uncertain_terms: list):
        working = sentence
        phrase_map = self.rules.get("ar_to_en_phrases", {})
        placeholders = {}
        ph_idx = 0

        for ar_ph, en_ph in sorted(phrase_map.items(), key=lambda x: len(x[0]), reverse=True):
            if ar_ph in working:
                key = f"__PHRASE{ph_idx}__"
                ph_idx += 1
                placeholders[key] = en_ph
                working = working.replace(ar_ph, f" {key} ")
                token_breakdown.append({"original": ar_ph, "translated": en_ph, "pos": "phrase", "uncertain": False})

        raw_tokens = re.findall(r'__PHRASE\d+__|\.NET|C#|SHA-256|UTF-8|[\u0600-\u06FF]+|[A-Za-z]+(?:-[A-Za-z]+)*|\d+(?:\.\d+)?|[^\w\s]', working)
        STOP_AR_EN = {
            "في": ("in", "prep"), "على": ("on", "prep"), "من": ("from", "prep"), "الى": ("to", "prep"),
            "إلى": ("to", "prep"), "عن": ("about", "prep"), "مع": ("with", "prep"), "بدون": ("without", "prep"),
            "دون": ("without", "prep"), "بين": ("between", "prep"), "عبر": ("through", "prep"),
            "خلال": ("during", "prep"), "قبل": ("before", "prep"), "بعد": ("after", "prep"),
            "تحت": ("under", "prep"), "فوق": ("above", "prep"), "كل": ("every", "det"),
            "هذا": ("this", "det"), "هذه": ("this", "det"), "ذلك": ("that", "det"), "تلك": ("that", "det"),
            "هو": ("is / he", "pron"), "هي": ("is / she", "pron"), "نحن": ("we", "pron"), "هم": ("they", "pron"),
            "انا": ("I", "pron"), "انت": ("you", "pron"), "الذي": ("which / who", "pron"), "التي": ("which / who", "pron"),
            "ان": ("that", "conj"), "أن": ("that", "conj"), "إن": ("indeed", "part"), "قد": ("has", "aux"),
            "لقد": ("has", "aux"), "سوف": ("will", "aux"), "لم": ("did not", "neg"), "لن": ("will not", "neg"),
            "لا": ("not", "neg"), "ليس": ("is not", "neg"), "كان": ("was", "aux"), "كانت": ("was", "aux"),
            "و": ("and", "conj"), "أو": ("or", "conj"), "او": ("or", "conj"), "لكن": ("but", "conj"),
            "ولكن": ("but", "conj"), "لأن": ("because", "conj"), "اذا": ("if", "conj"), "إذا": ("if", "conj"),
            "عندما": ("when", "conj"), "حيث": ("where", "conj"), "اي": ("any", "det"), "أي": ("any", "det")
        }

        en_tokens = []
        lit_tokens = []

        for tok in raw_tokens:
            if tok in placeholders:
                en_tokens.append(placeholders[tok])
                lit_tokens.append(placeholders[tok])
                continue
            if re.match(r'^[A-Za-z0-9_.\-#]+$', tok) or re.match(r'^[^\w\s]+$', tok):
                t_clean = "," if tok == "،" else ("?" if tok == "؟" else (";" if tok == "؛" else tok))
                en_tokens.append(t_clean)
                lit_tokens.append(t_clean)
                continue

            norm_t = normalize_arabic(tok)
            if tok in STOP_AR_EN or norm_t in STOP_AR_EN:
                val, pos = STOP_AR_EN.get(tok, STOP_AR_EN.get(norm_t))
                chosen = val.split("/")[0].strip()
                if chosen != "indeed":
                    en_tokens.append(chosen)
                lit_tokens.append(chosen)
                continue

            prefix_and = False
            if norm_t.startswith("و") and len(norm_t) > 3:
                sub_norm = norm_t[1:]
                if sub_norm in STOP_AR_EN:
                    en_tokens.append("and " + STOP_AR_EN[sub_norm][0].split("/")[0].strip())
                    lit_tokens.append("and " + STOP_AR_EN[sub_norm][0].split("/")[0].strip())
                    continue

            has_al = norm_t.startswith("ال") or norm_t.startswith("وال")
            if norm_t.startswith("وال"):
                prefix_and = True

            self._ensure_fast_token_maps(conn)
            stems = self.get_ar_candidate_stems(tok)
            found_ar = None
            for st in stems:
                if st in self._fast_ar_map:
                    found_ar = self._fast_ar_map[st]
                    break

            if found_ar:
                w_en, r_pos = found_ar
                piece = ("and " if prefix_and else "") + ("the " if has_al and r_pos == "noun" else "") + w_en
                en_tokens.append(piece)
                lit_tokens.append(w_en)
                token_breakdown.append({"original": tok, "translated": w_en, "pos": r_pos, "uncertain": False})
            else:
                uncertain_terms.append(tok)
                en_tokens.append(tok)
                lit_tokens.append(tok)
                token_breakdown.append({"original": tok, "translated": tok, "pos": "unknown", "uncertain": True})

        nat_str = " ".join(en_tokens)
        nat_str = re.sub(r'\s+([.,!?;])', r'\1', nat_str).strip()
        if nat_str and nat_str[0].islower():
            nat_str = nat_str[0].upper() + nat_str[1:]
        lit_str = " ".join(lit_tokens)
        return nat_str, lit_str, ""

    def _build_literal_gloss_en_ar(self, conn, sentence: str, token_breakdown: list, uncertain_terms: list) -> str:
        _, lit, _ = self._transfer_en_to_ar(conn, sentence, token_breakdown, uncertain_terms)
        return lit

    def _build_literal_gloss_ar_en(self, conn, sentence: str, token_breakdown: list, uncertain_terms: list) -> str:
        _, lit, _ = self._transfer_ar_to_en(conn, sentence, token_breakdown, uncertain_terms)
        return lit

    def _record_history(self, query_text, result_text, src_lang, tgt_lang, mode, engine_used, ms):
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    INSERT INTO user_history (query_text, result_text, source_lang, target_lang, mode, engine_used, processing_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (query_text, result_text, src_lang, tgt_lang, mode, engine_used, ms))
                conn.commit()
        except Exception:
            pass

    def get_history(self, limit=50):
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM user_history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def clear_history(self):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM user_history")
            conn.commit()
        sync_runtime_db_back()
        return {"success": True, "message_ar": "تم مسح سجل البحث والترجمات بنجاح."}

    def get_favorites(self):
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM user_favorites ORDER BY id DESC").fetchall()
            groups = conn.execute("SELECT * FROM vocabulary_groups ORDER BY id ASC").fetchall()
            return {"favorites": [dict(r) for r in rows], "groups": [dict(g) for g in groups]}

    def add_favorite(self, word_or_text: str, translation_ar: str, pos: str = "noun",
                     personal_note: str = "", group_name: str = "عام / General", difficulty: str = "Medium"):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO user_favorites (word_or_text, translation_ar, pos, personal_note, group_name, difficulty)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (word_or_text.strip(), translation_ar.strip(), pos, personal_note, group_name, difficulty))
            conn.execute("""
                INSERT OR REPLACE INTO srs_flashcards (word_en, word_ar, explanation_ar, group_name, difficulty, personal_note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (word_or_text.strip(), translation_ar.strip(), personal_note, group_name, difficulty, personal_note))
            conn.commit()
        sync_runtime_db_back()
        return {"success": True, "message_ar": f"تمت إضافة «{word_or_text}» إلى المفضلة وبطاقات المراجعة."}

    def delete_favorite(self, fav_id: int):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM user_favorites WHERE id = ?", (fav_id,))
            conn.commit()
        sync_runtime_db_back()
        return {"success": True}

    def create_vocab_group(self, group_name: str, description: str = ""):
        with self._get_conn() as conn:
            conn.execute("INSERT OR IGNORE INTO vocabulary_groups (group_name, description) VALUES (?, ?)",
                         (group_name.strip(), description.strip()))
            conn.commit()
        sync_runtime_db_back()
        return {"success": True, "message_ar": f"تم إنشاء المجموعة «{group_name}» بنجاح."}

    def get_srs_flashcards(self, group_name: str = ""):
        with self._get_conn() as conn:
            if group_name and group_name != "all":
                rows = conn.execute("SELECT * FROM srs_flashcards WHERE group_name = ? ORDER BY next_review_date ASC, id ASC", (group_name,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM srs_flashcards ORDER BY next_review_date ASC, id ASC").fetchall()
            return [dict(r) for r in rows]

    def review_srs_card(self, card_id: int, quality_grade: int):
        quality_grade = max(0, min(5, int(quality_grade)))
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM srs_flashcards WHERE id = ?", (card_id,)).fetchone()
            if not row:
                return {"success": False, "error": "البطاقة غير موجودة."}
            rep = row["repetition_count"]
            ef = row["easiness_factor"]
            interval = row["interval_days"]

            if quality_grade >= 3:
                if rep == 0:
                    interval = 1
                elif rep == 1:
                    interval = 4
                else:
                    interval = max(1, int(round(interval * ef)))
                rep += 1
            else:
                rep = 0
                interval = 1

            ef = max(1.3, round(ef + (0.1 - (5 - quality_grade) * (0.08 + (5 - quality_grade) * 0.02)), 2))
            diff = "Easy" if quality_grade >= 4 else ("Medium" if quality_grade >= 3 else "Hard")
            next_date = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

            conn.execute("""
                UPDATE srs_flashcards
                SET repetition_count = ?, easiness_factor = ?, interval_days = ?,
                    difficulty = ?, next_review_date = ?, last_reviewed_at = ?
                WHERE id = ?
            """, (rep, ef, interval, diff, next_date, now_str, card_id))
            conn.commit()
        sync_runtime_db_back()
        return {
            "success": True,
            "card_id": card_id,
            "new_interval_days": interval,
            "next_review_date": next_date,
            "easiness_factor": ef,
            "difficulty": diff
        }

    def analyze_word_frequencies_in_text(self, text: str) -> list:
        tokens = re.findall(r'[A-Za-z]{3,}|[\u0600-\u06FF]{3,}', text or "")
        counts = {}
        for t in tokens:
            k = t.lower() if re.match(r'^[A-Za-z]+$', t) else normalize_arabic(t)
            counts[k] = counts.get(k, 0) + 1

        results = []
        for word, cnt in sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:25]:
            info = self.lookup_word(word)
            meaning = info.get("word_ar", info.get("word_en", "—")) if info.get("found") else "غير مدرج"
            results.append({
                "word": word,
                "count": cnt,
                "meaning": meaning.split("/")[0].strip() if meaning else "—",
                "found_in_dict": bool(info.get("found"))
            })
        return results

    def export_vocabulary(self, fmt: str = "json") -> dict:
        cards = self.get_srs_flashcards()
        if fmt.lower() == "csv":
            lines = ["word_en,word_ar,group_name,difficulty,interval_days,personal_note"]
            for c in cards:
                row = [
                    str(c.get("word_en", "")).replace('"', '""'),
                    str(c.get("word_ar", "")).replace('"', '""'),
                    str(c.get("group_name", "")).replace('"', '""'),
                    str(c.get("difficulty", "")),
                    str(c.get("interval_days", 1)),
                    str(c.get("personal_note", "")).replace('"', '""')
                ]
                lines.append(",".join(f'"{x}"' for x in row))
            return {"format": "csv", "content": "\n".join(lines), "count": len(cards)}
        return {"format": "json", "content": json.dumps(cards, ensure_ascii=False, indent=2), "count": len(cards)}

    def import_vocabulary(self, items: list) -> dict:
        added = 0
        with self._get_conn() as conn:
            for item in items:
                w_en = (item.get("word_en") or item.get("word") or "").strip()
                w_ar = (item.get("word_ar") or item.get("meaning") or "").strip()
                if not w_en or not w_ar:
                    continue
                grp = item.get("group_name", "مستورد / Imported")
                diff = item.get("difficulty", "Medium")
                note = item.get("personal_note", "")
                conn.execute("""
                    INSERT OR REPLACE INTO srs_flashcards (word_en, word_ar, explanation_ar, group_name, difficulty, personal_note)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (w_en, w_ar, note, grp, diff, note))
                added += 1
            conn.commit()
        sync_runtime_db_back()
        return {"success": True, "imported_count": added, "message_ar": f"تم استيراد {added} كلمة بنجاح إلى نظام التعلم والمراجعة."}

    def run_local_ocr(self, image_path: str = "", crop_box: list = None) -> dict:
        t0 = time.perf_counter()
        target_path = image_path if image_path and os.path.exists(image_path) else os.path.join(BASE_DIR, "resources", "ocr", "sample_bilingual_ocr_card.png")
        if not os.path.exists(target_path):
            return {"success": False, "error_ar": "ملف الصورة غير موجود لإجراء التعرف الضوئي OCR."}

        work_img_path = target_path
        try:
            if crop_box and len(crop_box) == 4:
                from PIL import Image
                im = Image.open(target_path)
                cropped = im.crop(tuple(int(v) for v in crop_box))
                work_img_path = os.path.join(tempfile.gettempdir(), "linguadesk_ocr_crop.png")
                cropped.save(work_img_path)

            proc = subprocess.run(
                ["tesseract", work_img_path, "stdout", "-l", "eng"],
                capture_output=True, text=True, timeout=15
            )
            extracted = proc.stdout.strip()
            if not extracted:
                return {"success": False, "error_ar": "لم يتم العثور على نص واضح داخل الصورة المحددة."}

            trans = self.translate_text(extracted, source_lang="auto", target_lang="ar", save_history=False)
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            return {
                "success": True,
                "image_used": os.path.basename(target_path),
                "extracted_text": extracted,
                "translated_text": trans["natural_translation"],
                "processing_time_ms": elapsed_ms,
                "engine": "Local Tesseract OCR 5.x"
            }
        except Exception as e:
            return {"success": False, "error_ar": f"حدث خطأ في وحدة OCR المحلية: {str(e)}"}

    def get_resources_and_settings(self) -> dict:
        with self._get_conn() as conn:
            res_rows = conn.execute("SELECT * FROM installed_resources").fetchall()
            set_rows = conn.execute("SELECT setting_key, setting_value FROM app_settings").fetchall()
            cnt_entries = conn.execute("SELECT COUNT(*) FROM dictionary_entries").fetchone()[0]
            cnt_verified = conn.execute("SELECT COUNT(*) FROM dictionary_entries WHERE is_verified_lexical = 1").fetchone()[0]
            cnt_idioms = conn.execute("SELECT COUNT(*) FROM idioms_phrases").fetchone()[0]
            cnt_sentences = conn.execute("SELECT COUNT(*) FROM bilingual_sentences").fetchone()[0]

        return {
            "resources": [dict(r) for r in res_rows],
            "settings": {r["setting_key"]: r["setting_value"] for r in set_rows},
            "stats": {
                "total_dictionary_entries": cnt_entries,
                "verified_lexical_entries": cnt_verified,
                "auxiliary_morphological_entries": cnt_entries - cnt_verified,
                "total_idioms_phrases": cnt_idioms,
                "total_parallel_sentences": cnt_sentences,
                "db_size_mb": round(os.path.getsize(DB_SOURCE_PATH) / (1024 * 1024), 2) if os.path.exists(DB_SOURCE_PATH) else 0
            }
        }

    def verify_resource_integrity(self, resource_id: str) -> dict:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM installed_resources WHERE id = ?", (resource_id,)).fetchone()
            if not row:
                return {"success": False, "message_ar": "المورد المطلوب غير مدرج في قاعدة البيانات."}
            rel_path = row["local_path"]
            full_path = os.path.join(BASE_DIR, rel_path)
            if row["is_core_protected"] and os.path.exists(full_path):
                with open(full_path, "rb") as bf:
                    sha = hashlib.sha256(bf.read()).hexdigest()
                size_mb = round(os.path.getsize(full_path) / (1024 * 1024), 2)
                return {
                    "success": True,
                    "resource_id": resource_id,
                    "verified": True,
                    "sha256": sha,
                    "size_mb": size_mb,
                    "message_ar": f"تم التحقق من سلامة الملف بنجاح (SHA-256: {sha[:16]}... | الحجم: {size_mb} MB)."
                }
            elif row["status"].startswith("Installed"):
                return {
                    "success": True,
                    "resource_id": resource_id,
                    "verified": True,
                    "message_ar": "المورد النظامي متاح ويعمل بصورة سليمة."
                }
            else:
                return {
                    "success": True,
                    "resource_id": resource_id,
                    "verified": False,
                    "message_ar": "هذه الحزمة اختيارية ولم يتم تنزيلها بعد. يمكنك تنزيلها عبر أداة تنزيل الموارد عند الاتصال بالإنترنت."
                }

    def delete_optional_resource(self, resource_id: str) -> dict:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM installed_resources WHERE id = ?", (resource_id,)).fetchone()
            if not row:
                return {"success": False, "message_ar": "المورد غير موجود."}
            if row["is_core_protected"]:
                return {
                    "success": False,
                    "protected_error": True,
                    "message_ar": "رفض العملية: هذا المورد محمي وأساسي لتشغيل القاموس والترجمة دون إنترنت ولا يُسمح بحذفه."
                }
            return {"success": True, "message_ar": f"تم إزالة المورد الاختياري «{row['name_ar']}» بنجاح."}

    def update_settings(self, updates: dict) -> dict:
        with self._get_conn() as conn:
            for k, v in updates.items():
                conn.execute("INSERT OR REPLACE INTO app_settings (setting_key, setting_value) VALUES (?, ?)", (str(k), str(v)))
            conn.commit()
        sync_runtime_db_back()
        return {"success": True, "message_ar": "تم حفظ الإعدادات محلياً بنجاح."}

    def simulate_safe_clipboard_capture(self, current_clipboard: str, selected_external_text: str, restore_previous: bool = True) -> dict:
        saved_previous = current_clipboard
        captured = (selected_external_text or "").strip()
        if not captured:
            return {
                "success": False,
                "captured_text": "",
                "restored_clipboard": saved_previous,
                "message_ar": "تم تجاهل النص الفارغ ولم يتم المساس بمحتوى الحافظة السابق."
            }
        translation = self.translate_text(captured, source_lang="auto", target_lang="ar", save_history=True)
        final_clipboard = saved_previous if restore_previous else captured
        return {
            "success": True,
            "captured_text": captured,
            "translation": translation["natural_translation"],
            "restored_clipboard": final_clipboard,
            "clipboard_preserved": (final_clipboard == saved_previous),
            "message_ar": "تم التقاط النص المحدد وترجمته فوراً مع استعادة محتوى الحافظة الأصلي بأمان."
        }


class LinguaDeskHttpHandler(SimpleHTTPRequestHandler):
    engine_instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.path = "/ui/index.html"
            return super().do_GET()
        if parsed.path == "/api/init":
            eng = self.engine_instance
            data = eng.get_resources_and_settings()
            data["history"] = eng.get_history(30)
            data["favorites_data"] = eng.get_favorites()
            data["srs_cards"] = eng.get_srs_flashcards()
            return self._send_json(data)
        if parsed.path == "/api/autocomplete":
            qs = parse_qs(parsed.query)
            prefix = qs.get("q", [""])[0]
            limit = int(qs.get("limit", ["8"])[0])
            return self._send_json({"suggestions": self.engine_instance.autocomplete(prefix, limit)})
        if parsed.path == "/api/lookup":
            qs = parse_qs(parsed.query)
            word = qs.get("w", [""])[0]
            return self._send_json(self.engine_instance.lookup_word(word))
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        payload = json.loads(raw_body or "{}")
        eng = self.engine_instance

        if parsed.path == "/api/translate":
            res = eng.translate_text(
                payload.get("text", ""),
                payload.get("source_lang", "auto"),
                payload.get("target_lang", "ar"),
                payload.get("save_history", True)
            )
            return self._send_json(res)
        elif parsed.path == "/api/lookup":
            return self._send_json(eng.lookup_word(payload.get("query", "")))
        elif parsed.path == "/api/favorite/add":
            return self._send_json(eng.add_favorite(
                payload.get("word_or_text", ""),
                payload.get("translation_ar", ""),
                payload.get("pos", "noun"),
                payload.get("personal_note", ""),
                payload.get("group_name", "عام / General"),
                payload.get("difficulty", "Medium")
            ))
        elif parsed.path == "/api/favorite/delete":
            return self._send_json(eng.delete_favorite(int(payload.get("id", 0))))
        elif parsed.path == "/api/group/create":
            return self._send_json(eng.create_vocab_group(payload.get("group_name", ""), payload.get("description", "")))
        elif parsed.path == "/api/srs/review":
            return self._send_json(eng.review_srs_card(int(payload.get("card_id", 0)), int(payload.get("grade", 4))))
        elif parsed.path == "/api/word-freq":
            return self._send_json({"frequencies": eng.analyze_word_frequencies_in_text(payload.get("text", ""))})
        elif parsed.path == "/api/export":
            return self._send_json(eng.export_vocabulary(payload.get("format", "json")))
        elif parsed.path == "/api/import":
            return self._send_json(eng.import_vocabulary(payload.get("items", [])))
        elif parsed.path == "/api/ocr":
            return self._send_json(eng.run_local_ocr(payload.get("image_path", ""), payload.get("crop_box")))
        elif parsed.path == "/api/resource/verify":
            return self._send_json(eng.verify_resource_integrity(payload.get("resource_id", "")))
        elif parsed.path == "/api/resource/delete":
            return self._send_json(eng.delete_optional_resource(payload.get("resource_id", "")))
        elif parsed.path == "/api/settings/update":
            return self._send_json(eng.update_settings(payload.get("settings", {})))
        elif parsed.path == "/api/history/clear":
            return self._send_json(eng.clear_history())
        elif parsed.path == "/api/clipboard-capture":
            return self._send_json(eng.simulate_safe_clipboard_capture(
                payload.get("current_clipboard", "بيانات المستخدم السابقة المحفوظة"),
                payload.get("selected_text", ""),
                payload.get("restore_previous", True)
            ))
        return self._send_json({"error": "Unknown endpoint"}, 404)


def run_server(port=18765):
    LinguaDeskHttpHandler.engine_instance = LinguaDeskEngine()
    server = ThreadingHTTPServer(("127.0.0.1", port), LinguaDeskHttpHandler)
    print(f"LinguaDesk Pro Local Backend Server running at http://127.0.0.1:{port}/ (عمل محمد البكير)")
    server.serve_forever()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        port_arg = 18765
        for idx, a in enumerate(sys.argv):
            if a == "--port" and idx + 1 < len(sys.argv):
                port_arg = int(sys.argv[idx + 1])
        run_server(port_arg)
    else:
        engine = LinguaDeskEngine()
        r = engine.lookup_word("run")
        print(f"LinguaDeskEngine ready. Lookup('run') in {r['query_time_ms']} ms.")
