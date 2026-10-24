# LinguaDesk Pro (v7.0)

**Bilingual English–Arabic / Arabic–English Desktop Dictionary, Contextual Translation Tool & Visual OCR Utility for Windows 10/11**

[العربية — قراءة التوثيق باللغة العربية (README\_AR.md)](https://www.google.com/search?q=README_AR.md) | [Build Guide (BUILD.md)](BUILD.md) | [Licenses (LICENSES.md)](https://www.google.com/search?q=LICENSES.md) | [Test Report (docs/TEST\_REPORT.md)](https://www.google.com/search?q=docs/TEST_REPORT.md)

**Author & Maintainer:** Mohammed Albukeer (محمد البكير) — [mohammedalbukeer@gmail.com](mailto:mohammedalbukeer@gmail.com)  
**Repository:** [github.com/25164488-Mohammed/LinguaDeskPro](https://github.com/25164488-Mohammed/LinguaDeskPro)  
**Latest Release:** [v7.0-latest on GitHub Releases](https://github.com/25164488-Mohammed/LinguaDeskPro/releases/tag/v7.0-latest)

## What is LinguaDesk Pro?

**LinguaDesk Pro** is a Windows desktop translation and lexical reference application designed for bidirectional **English ↔ Arabic** workflows. It combines a large local bilingual dictionary, rule-based offline sentence translation, optional online neural translation when connected to the internet, a global floating mini-translator window, and a side-by-side visual OCR workspace inside a self-extracting Windows executable.

## What Problem Does It Solve?

1. **Offline & Hybrid Continuity:** Standard web translators stop working when internet access is unavailable, while traditional offline dictionaries only look up isolated single words. LinguaDesk Pro provides full offline lexical lookup and rule-based sentence/paragraph translation locally, and automatically queries online neural translation endpoints when internet connectivity is available.
2. **Arabic Morphological Normalization:** Searching for Arabic words in many dictionaries fails if diacritics (*Tashkeel*), Hamza forms (`أ / إ / آ / ا`), or attached prefixes (`الـ`, `وبـ`, `فـ`) do not match the stored entry. LinguaDesk Pro normalizes Arabic input automatically so users can search with or without diacritics.
3. **In-Place Workflow Integration:** Instead of switching back and forth between windows, users can highlight text in standard desktop applications and press a global keyboard shortcut to translate it in a compact, always-on-top floating window synchronized with the main application.

## How It Differs from Traditional Dictionaries

* **Multi-Layer Translation Architecture:** Clearly separates verified lexical lookup (roots, polysemous word senses, idioms, and domain terminology), offline rule-based contextual sentence synthesis, and online neural machine translation.
* **Two-Way Real-Time Synchronization:** Translations performed in the native Windows Forms floating overlay (`FloatingOverlayForm`) and words learned in the main workspace synchronize automatically over the local loopback bridge (`http://127.0.0.1:18955/api/sync`).
* **Self-Learning Local Store:** Online translations and user-edited term pairs can be saved directly to the local dictionary so they remain available offline in future sessions.
* **Visual OCR Comparison:** Displays the original image on the right and the translated overlay on the left with selectable text boxes and PNG export.

## Core Features & Offline vs. Online Capabilities

For technical transparency, the table below distinguishes between features that operate **100% offline** and features that use **online services** when an internet connection is available:

| Feature / Subsystem | Offline Operation (No Internet) | Online Operation (When Connected) |
| :--- | :--- | :--- |
| **Bilingual Dictionary Lookup** | **Yes:** Searches `147,674` in-memory lexical entries (`6,911` roots, `139,000` derived/inflected forms, `1,300` idioms/collocations, `463` reference sentences) in `ui/js/full_lexicon_db.js` and `129,394` indexed SQLite/FTS5 rows in `resources/database/linguadesk_dictionary.db.gz` | Uses the same local dictionary; no internet required |
| **Sentence & Paragraph Translation** | **Yes (Rule-Based Contextual Engine):** Matches stored bilingual sentences, idioms, technical collocations, and proper names first, then applies morphological analysis and syntactic reordering (`SVO ↔ VSO`, article attachment) via `ui/js/bridge.js` and `OfflineLexiconEngine` | **Yes (Online Neural Translation):** Automatically queries live neural translation endpoints (Google GTX / MyMemory fallback) and caches learned translations locally |
| **Floating Mini-Translator Overlay** | **Yes:** Loads the local lexicon into C# memory (`OfflineLexiconEngine`) for offline translation and allows toggling *"Offline Mode Only"* | Queries online translation with automatic fallback to the local lexicon if offline |
| **Optical Character Recognition (OCR)** | **Yes:** Uses Windows 10/11 native WinRT OCR (`Windows.Media.Ocr` via `scripts/windows_ocr/win_ocr.ps1`), bundled `Tesseract.js v5.1.1` (`ara` + `eng` traineddata included during release build), and the fallback canvas recognizer (`ui/js/local_ocr_engine.js`) | Optional *"Scan & Translate Online"* button queries the `OCR.space` cloud OCR API with automatic local fallback |
| **Audio Pronunciation (TTS)** | **English:** Uses local `Windows SAPI5` voices (`en-US`, `en-GB`). **Arabic:** Uses local SAPI5 voice only if an Arabic TTS voice is installed in Windows | Streams natural Arabic and English TTS audio via the local `/api/tts-audio` proxy |
| **Spaced Repetition (SRS) & History** | **Yes:** Flashcard review (`SM-2` scheduling), favorites, custom groups, history, and `JSON`/`CSV` import/export are stored locally | Works locally without internet |

## System Requirements

* **Operating System:** Windows 10 (64-bit, version 1809 or newer recommended) or Windows 11 (64-bit).
* **Architecture:** `x64` (`win-x64`).
* **Browser Runtime for Main UI Window:** Microsoft Edge (pre-installed on Windows 10/11) or Google Chrome. The native C# host (`LinguaDeskPro.exe`) launches the main UI in a standalone `--app` window served from `http://127.0.0.1:18955/index.html` while hosting the floating overlay natively in Windows Forms.
* **Windows OCR Language Packs (for Native Local OCR):** Windows English and Arabic OCR capabilities (`Language.OCR~~~en-US~0.0.1.0` and `Language.OCR~~~ar-SA~0.0.1.0`) for `Windows.Media.Ocr`, with `Tesseract.js` (`ara+eng`) included as a built-in local fallback in the packaged release.
* **Disk Space:** Approximately `250 MB` of free disk space for the installed application and extracted local dictionary/OCR resources under `%LOCALAPPDATA%\LinguaDeskPro`.

## Download & Installation

All official binaries are published on the [**GitHub Releases page (`v7.0-latest`)**](https://github.com/25164488-Mohammed/LinguaDeskPro/releases/tag/v7.0-latest).

| Release File | Type | Recommended Use |
| :--- | :--- | :--- |
| [**`LinguaDeskPro_Setup_v7.0_AllInOne.exe`**](https://github.com/25164488-Mohammed/LinguaDeskPro/releases/tag/v7.0-latest) | **Windows Setup Installer (Inno Setup)** | **Recommended for most users:** Installs the application under `%LOCALAPPDATA%\LinguaDeskPro`, creates a single `LinguaDesk Pro` shortcut on the Desktop and Start Menu, and registers an uninstaller |
| [**`LinguaDeskPro_v7.0_SingleFile_Portable.exe`**](https://github.com/25164488-Mohammed/LinguaDeskPro/releases/tag/v7.0-latest) | **Self-Contained Single-File Executable** | **Portable / Direct Run:** Runs directly without a setup wizard and self-extracts its embedded payload (`EmbeddedPayload.zip`) to `%LOCALAPPDATA%\LinguaDeskPro\v7_0` on first launch |

### Installation Steps
1. Go to [**Releases (`v7.0-latest`)**](https://github.com/25164488-Mohammed/LinguaDeskPro/releases/tag/v7.0-latest) and download **`LinguaDeskPro_Setup_v7.0_AllInOne.exe`**.
2. Run the installer, follow the setup prompt, and click **Finish** to launch **LinguaDesk Pro**.
3. If Windows SmartScreen displays a prompt (because the binary is built via GitHub Actions without a paid commercial EV code-signing certificate), click **More info** → **Run anyway**.

## How to Use Core Features

1. **Main Translation & Dictionary Lookup:**
   * Open **LinguaDesk Pro** from the Desktop shortcut.
   * Type or paste any English or Arabic word, phrase, sentence, or paragraph into the source box.
   * View the contextual translation, literal translation, token-by-token morphological breakdown, and dictionary sense cards below.
   * To teach the application a new term or custom translation, edit the target text box and click **«💾 حفظ في القاموس المحلي» (Save to Local Dictionary)**.
2. **Floating Mini-Translator (External Applications):**
   * Highlight text in a browser, PDF viewer, or text editor and press **`Ctrl + Shift + T`**, **`Ctrl + Q`**, or **`Alt + Q`**.
   * The floating overlay window will appear on top of the active application, translate the selected text, and synchronize the result with the main window.
   * You can also enable *"Auto-translate on Copy (`Ctrl+C`)"* or *"Offline Mode Only"* directly inside the floating window.
3. **Visual OCR Studio (Image Translation):**
   * Switch to the **OCR (المسح الضوئي للصور)** tab in the main window.
   * Select the image language (**Auto**, **Arabic**, or **English**), then click **«📂 اختيار صورة من الجهاز»** (or press **`Ctrl + V`** to paste a screenshot from the clipboard).
   * Use **«📴 مسح وترجمة محلياً (بدون إنترنت)»** for offline recognition or **«🌐 مسح وترجمة عبر الإنترنت»** for cloud OCR.
   * Click **«🗑️ حذف الصورة السابقة وبدء صورة جديدة»** to clear the canvas and scan another image, or **«💾 حفظ الصورة المترجمة (PNG)»** to export the translated image.

## Supported Keyboard Shortcuts

| Shortcut | Scope | Action |
| :--- | :--- | :--- |
| **`Ctrl + Shift + T`** | Global (System-wide on Windows) | Captures selected text from the active window and translates it in the floating overlay |
| **`Ctrl + Q`** | Global (System-wide on Windows) | Alternative global shortcut to summon the floating overlay and translate selected text |
| **`Alt + Q`** | Global (System-wide on Windows) | Secondary alternative global shortcut for the floating overlay |
| **`Ctrl + C`** | Global (When Clipboard Watcher is enabled) | Automatically translates newly copied text (up to 1,500 characters) in the floating overlay |
| **`Ctrl + V`** | Inside Main App (OCR Studio) | Pastes an image from the clipboard directly into the OCR scanner |
| **`Ctrl + Enter`** | Inside Main App (Translation Editor) | Triggers immediate translation of the source input box |
| **`Escape`** | Inside Main App | Closes the in-app quick floating preview dialog |

## Building from Source

You can build the single-file executable either automatically via **GitHub Actions** (`.github/workflows/build-single-exe.yml`) or locally on Windows using `BUILD_SINGLE_EXE_LOCALLY.bat` or the `.NET 8.0 SDK`. See [**BUILD.md**](BUILD.md) for complete build instructions and architecture details.

## Known Limitations & Technical Notes

To ensure accurate expectations, please note the following current technical boundaries:

1. **Offline Rule-Based Translation vs. Online Neural Translation:**
   * Offline sentence translation uses a rule-based morphological and syntactic engine (`OfflineContextualTranslator` / `ui/js/bridge.js`) backed by the local lexicon (`147,674` entries). While effective for single words, idioms, technical terminology, and structured sentences, complex literary or highly idiomatic paragraphs achieve higher fluency when connected to the internet (where the online neural engine is used and cached locally).
   * The file `resources/translation-models/opus-mt-en-ar-onnx/opus_mt_ar_en_quantized.onnx` (`~65 KB`) is a lightweight auxiliary rule/matrix metadata artifact, not a full standalone ONNX transformer model.
2. **Global Hotkey Text Capture in Elevated Windows:**
   * The global shortcuts (`Ctrl+Shift+T`, `Ctrl+Q`, `Alt+Q`) capture selected text by simulating `Ctrl+C` via Win32 `keybd_event`. Due to Windows User Interface Privilege Isolation (UIPI), if the target application is running as **Administrator**, `LinguaDeskPro.exe` must also be run with matching privileges to simulate keystrokes into that window, or you can press `Ctrl+C` manually with the clipboard watcher enabled.
3. **Arabic Offline Speech Synthesis (TTS):**
   * Most default Windows 10/11 installations do not include a pre-installed Arabic SAPI5 voice. When offline, Arabic TTS will only speak if a Windows Arabic voice pack (such as *Microsoft Naayf* or *Microsoft Hoda*) is installed in Windows Settings; otherwise, natural Arabic speech requires an internet connection.
4. **Source Repository OCR Stub vs. Release Build:**
   * To keep the Git repository lightweight, `resources/ocr/tessdata/ara.traineddata` in the raw source tree is a compact placeholder (`32 KB`), whereas `.github/workflows/build-single-exe.yml` downloads the full official `ara.traineddata` and `eng.traineddata` from `tesseract-ocr/tessdata_fast` plus `Tesseract.js v5.1.1` when building the release executables. If building locally from raw source without running the download step, local OCR relies primarily on Windows 10/11 native `Windows.Media.Ocr`.

## Reporting Issues & Contact

If you encounter a bug, installation issue, or translation error:
* Open a new issue on the [GitHub Issues page](https://www.google.com/search?q=https://github.com/25164488-Mohammed/LinguaDeskPro/issues) and include your Windows version (`Windows 10` or `Windows 11`), whether you used `LinguaDeskPro_Setup_v7.0_AllInOne.exe` or `LinguaDeskPro_v7.0_SingleFile_Portable.exe`, and steps to reproduce.
* Or contact the developer directly via email: **Mohammed Albukeer (محمد البكير)** at [mohammedalbukeer@gmail.com](mailto:mohammedalbukeer@gmail.com).

## License

The **LinguaDesk Pro** application source code is licensed under the **MIT License**. Bundled lexical datasets and open-source components (`WordNet 3.1`, `Wiktionary CC-BY-SA 4.0`, `Hunspell / SCOWL`, `SQLite`, and `Tesseract OCR`) are distributed under their respective open-source licenses. See [LICENSES.md](https://www.google.com/search?q=LICENSES.md) and [THIRD\_PARTY\_NOTICES.md](https://www.google.com/search?q=THIRD_PARTY_NOTICES.md) for full details.
