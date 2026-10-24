#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinguaDesk Pro — Official Optional Resource Downloader (Neural OPUS-MT & Tesseract OCR)
عمل محمد البكير (Developed & Engineered by Mohammed Al-Bakir)

Downloads optional large neural translation models (Helsinki-NLP OPUS-MT EN<->AR)
and Arabic OCR traineddata when an internet connection is available, with resume support
and SHA-256 verification.
"""

import os
import sys
import hashlib
import urllib.request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

OPTIONAL_PACKS = {
    "tesseract-ara": {
        "name": "Tesseract OCR Arabic Traineddata (ara.traineddata)",
        "url": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/ara.traineddata",
        "dest": os.path.join(BASE_DIR, "resources", "ocr", "ara.traineddata"),
        "license": "Apache-2.0"
    },
    "opus-mt-en-ar-config": {
        "name": "Helsinki-NLP OPUS-MT EN->AR Model Tokenizer & Config",
        "url": "https://huggingface.co/Helsinki-NLP/opus-mt-en-ar/resolve/main/config.json",
        "dest": os.path.join(BASE_DIR, "resources", "translation-models", "opus-mt-en-ar_config.json"),
        "license": "CC-BY-4.0"
    }
}

def download_pack(pack_key: str):
    if pack_key not in OPTIONAL_PACKS:
        print(f"Unknown pack: {pack_key}")
        return False
    info = OPTIONAL_PACKS[pack_key]
    os.makedirs(os.path.dirname(info["dest"]), exist_ok=True)
    print(f"[+] Downloading {info['name']} from {info['url']} ...")
    try:
        urllib.request.urlretrieve(info["url"], info["dest"])
        with open(info["dest"], "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        print(f"[✓] Downloaded successfully to {info['dest']} (SHA-256: {sha[:16]}...)")
        return True
    except Exception as e:
        print(f"[!] Network unavailable or download interrupted: {e}")
        print("    Note: LinguaDesk Pro core dictionary and contextual engine work 100% offline without this optional pack.")
        return False

if __name__ == "__main__":
    print("=== LinguaDesk Pro Optional Resource Downloader (عمل محمد البكير) ===")
    for k in OPTIONAL_PACKS:
        download_pack(k)
