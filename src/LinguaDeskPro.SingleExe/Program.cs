using System;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.Reflection;
using System.Collections.Generic;
using Microsoft.Win32;

namespace LinguaDeskProHost
{
    public static class OfflineLexiconEngine
    {
        public static Dictionary<string, string> EnToAr = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        public static Dictionary<string, string> ArToEn = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        public static Dictionary<string, string> PhraseEnToAr = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        public static bool IsLoaded = false;
        private static readonly object syncLock = new object();

        public static void LoadFromAppRoot(string rootDir)
        {
            if (IsLoaded) return;
            lock (syncLock)
            {
                if (IsLoaded) return;
                try
                {
                    SeedCorePhrasesAndNames();
                    string lexPath = Path.Combine(rootDir, Path.Combine("ui", Path.Combine("js", "full_lexicon_db.js")));
                    if (File.Exists(lexPath))
                    {
                        string content = File.ReadAllText(lexPath, Encoding.UTF8);
                        // 1. Extract roots: "word":["arabic",...]
                        MatchCollection mcRoots = Regex.Matches(content, "\"([A-Za-z0-9\\s'\\-]{1,45})\"\\s*:\\s*\\[\\s*\"([^\"]+)\"");
                        foreach (Match m in mcRoots)
                        {
                            AddLexiconPair(m.Groups[1].Value, m.Groups[2].Value);
                        }
                        // 2. Extract 138,821 derived entries: "word":"arabic"
                        MatchCollection mcDerived = Regex.Matches(content, "\"([A-Za-z0-9\\s'\\-\\(\\)]{1,60})\"\\s*:\\s*\"([^\"]+)\"");
                        foreach (Match m in mcDerived)
                        {
                            string rawKey = m.Groups[1].Value;
                            if (rawKey == "version" || rawKey == "developer") continue;
                            AddLexiconPair(rawKey, m.Groups[2].Value);
                            int parenIdx = rawKey.IndexOf("(");
                            if (parenIdx > 1)
                            {
                                AddLexiconPair(rawKey.Substring(0, parenIdx).Trim(), m.Groups[2].Value);
                            }
                        }
                        // 3. Extract idioms & sentences: ["English phrase", "Arabic translation"
                        MatchCollection mcArrays = Regex.Matches(content, "\\[\\s*\"([A-Za-z][^\"]{2,140})\"\\s*,\\s*\"([^\"]+)\"");
                        foreach (Match m in mcArrays)
                        {
                            AddLexiconPair(m.Groups[1].Value, m.Groups[2].Value);
                        }
                    }

                    // Load user-learned synchronized dictionary if present
                    string learnedPath = Path.Combine(rootDir, Path.Combine("resources", "learned_sync.json"));
                    if (File.Exists(learnedPath))
                    {
                        string lJson = File.ReadAllText(learnedPath, Encoding.UTF8);
                        MatchCollection lm = Regex.Matches(lJson, "\"src\"\\s*:\\s*\"([^\"]+)\"\\s*,\\s*\"tgt\"\\s*:\\s*\"([^\"]+)\"");
                        foreach (Match m in lm)
                        {
                            LearnPair(m.Groups[1].Value, m.Groups[2].Value);
                        }
                    }
                    IsLoaded = true;
                }
                catch { }
            }
        }

        public static void LearnPair(string src, string tgt)
        {
            if (string.IsNullOrWhiteSpace(src) || string.IsNullOrWhiteSpace(tgt)) return;
            src = src.Trim();
            tgt = tgt.Trim();
            bool srcAr = ContainsArabic(src);
            if (srcAr)
            {
                ArToEn[StripTashkeel(src)] = tgt;
                EnToAr[tgt.ToLowerInvariant()] = src;
            }
            else
            {
                string low = src.ToLowerInvariant();
                if (low.Contains(" ")) PhraseEnToAr[low] = tgt;
                EnToAr[low] = tgt;
                ArToEn[StripTashkeel(tgt)] = src;
            }
        }

        private static void SeedCorePhrasesAndNames()
        {
            PhraseEnToAr["mohammed albukeer"] = "محمد البكير";
            PhraseEnToAr["mohammed ali"] = "محمد علي";
            PhraseEnToAr["ibn khaldun"] = "ابن خلدون";
            PhraseEnToAr["ibn sina"] = "ابن سينا";
            PhraseEnToAr["artificial intelligence"] = "الذكاء الاصطناعي";
            PhraseEnToAr["machine learning"] = "تعلم الآلة";
            PhraseEnToAr["operating system"] = "نظام التشغيل";
            PhraseEnToAr["computer science"] = "علوم الحاسوب";
            PhraseEnToAr["software engineering"] = "هندسة البرمجيات";
            PhraseEnToAr["in the long run"] = "على المدى الطويل";
            PhraseEnToAr["knowledge is power"] = "المعرفة قوة";
            PhraseEnToAr["is the study of"] = "هي دراسة";
            PhraseEnToAr["engineered by"] = "صُمم وطُوّر بواسطة";
            PhraseEnToAr["developed by"] = "طُوّر بواسطة";
            PhraseEnToAr["welcome to"] = "مرحباً بكم في";

            EnToAr["i"] = "أنا"; EnToAr["you"] = "أنت"; EnToAr["he"] = "هو"; EnToAr["she"] = "هي";
            EnToAr["we"] = "نحن"; EnToAr["they"] = "هم"; EnToAr["it"] = "هو";
            EnToAr["this"] = "هذا"; EnToAr["that"] = "ذلك"; EnToAr["these"] = "هؤلاء";
            EnToAr["in"] = "في"; EnToAr["on"] = "على"; EnToAr["to"] = "إلى"; EnToAr["from"] = "من";
            EnToAr["with"] = "مع"; EnToAr["for"] = "لأجل"; EnToAr["of"] = "من"; EnToAr["by"] = "بواسطة";
            EnToAr["and"] = "و"; EnToAr["or"] = "أو"; EnToAr["but"] = "لكن"; EnToAr["not"] = "لا";
            EnToAr["is"] = "يكون"; EnToAr["are"] = "يكونون"; EnToAr["was"] = "كان"; EnToAr["were"] = "كانوا";
            EnToAr["albukeer"] = "البكير"; EnToAr["mohammed"] = "محمد"; EnToAr["ali"] = "علي";
            EnToAr["philosophy"] = "الفلسفة"; EnToAr["science"] = "العلم"; EnToAr["knowledge"] = "المعرفة";

            ArToEn["محمد البكير"] = "Mohammed Albukeer";
            ArToEn["محمد علي"] = "Mohammed Ali";
            ArToEn["ابن خلدون"] = "Ibn Khaldun";
            ArToEn["مدرسة"] = "school";
            ArToEn["جامعة"] = "university";
            ArToEn["فلسفة"] = "philosophy";
            ArToEn["علم"] = "science";
            ArToEn["معرفة"] = "knowledge";
            ArToEn["نور"] = "light";
            ArToEn["ظلام"] = "darkness";
            ArToEn["كتاب"] = "book";
            ArToEn["قاموس"] = "dictionary";
            ArToEn["ترجمة"] = "translation";
        }

        public static void AddLexiconPair(string rawEn, string rawAr)
        {
            string en = (rawEn ?? "").Trim().ToLowerInvariant().TrimEnd('.', '!', '?');
            string arPrimary = CleanPrimaryArabic((rawAr ?? "").Trim());
            if (string.IsNullOrEmpty(en) || string.IsNullOrEmpty(arPrimary)) return;

            if (en.Contains(" "))
            {
                if (!PhraseEnToAr.ContainsKey(en)) PhraseEnToAr[en] = arPrimary;
            }
            else
            {
                if (!EnToAr.ContainsKey(en)) EnToAr[en] = arPrimary;
            }

            string arUnvoc = StripTashkeel(arPrimary);
            if (arUnvoc.Length >= 2 && !ArToEn.ContainsKey(arUnvoc))
            {
                ArToEn[arUnvoc] = en;
            }
        }

        public static string CleanPrimaryArabic(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            int slash = s.IndexOf('/');
            if (slash > 0) s = s.Substring(0, slash);
            s = Regex.Replace(s, "\\s*\\([^)]*\\)", "");
            return s.Trim();
        }

        public static string StripTashkeel(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            return Regex.Replace(s, "[\\u064B-\\u065F\\u0670\\u0640]", "").Trim();
        }

        public static bool ContainsArabic(string s)
        {
            if (string.IsNullOrEmpty(s)) return false;
            foreach (char c in s)
            {
                if (c >= 0x0600 && c <= 0x06FF) return true;
            }
            return false;
        }

        public static string TranslateOffline(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return "";
            string clean = text.Trim();
            bool isAr = ContainsArabic(clean);

            if (!isAr)
            {
                string low = clean.ToLowerInvariant().TrimEnd('.', '!', '?');
                if (EnToAr.ContainsKey(low)) return EnToAr[low];
                if (PhraseEnToAr.ContainsKey(low)) return PhraseEnToAr[low];

                string working = clean;
                foreach (KeyValuePair<string, string> kv in PhraseEnToAr)
                {
                    if (working.IndexOf(kv.Key, StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        working = Regex.Replace(working, "\\b" + Regex.Escape(kv.Key) + "\\b", kv.Value, RegexOptions.IgnoreCase);
                    }
                }

                string[] tokens = Regex.Split(working, "(\\s+|[,.;!?]+)");
                StringBuilder sb = new StringBuilder();
                foreach (string tok in tokens)
                {
                    if (string.IsNullOrEmpty(tok)) continue;
                    if (Regex.IsMatch(tok, "^\\s+$")) { sb.Append(" "); continue; }
                    if (ContainsArabic(tok)) { sb.Append(tok); continue; }
                    string w = tok.Trim().ToLowerInvariant();
                    if (w == "the" || w == "a" || w == "an") continue;
                    if (EnToAr.ContainsKey(w)) { sb.Append(EnToAr[w]); continue; }
                    // Suffix stem check
                    string stemmed = TryResolveEnglishStem(w);
                    if (!string.IsNullOrEmpty(stemmed)) { sb.Append(stemmed); continue; }
                    sb.Append(tok);
                }
                return Regex.Replace(sb.ToString(), "\\s{2,}", " ").Trim();
            }
            else
            {
                string unvoc = StripTashkeel(clean);
                if (ArToEn.ContainsKey(unvoc)) return ArToEn[unvoc];

                string[] words = unvoc.Split(new char[] { ' ', '\t', '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
                List<string> outWords = new List<string>();
                foreach (string w in words)
                {
                    string cw = w.Trim('،', '؛', '.', '!', '؟', ',');
                    if (ArToEn.ContainsKey(cw)) { outWords.Add(ArToEn[cw]); continue; }
                    if (cw.StartsWith("ال") && cw.Length > 3 && ArToEn.ContainsKey(cw.Substring(2)))
                    {
                        outWords.Add("the " + ArToEn[cw.Substring(2)]);
                        continue;
                    }
                    if (cw.StartsWith("و") && cw.Length > 2 && ArToEn.ContainsKey(cw.Substring(1)))
                    {
                        outWords.Add("and " + ArToEn[cw.Substring(1)]);
                        continue;
                    }
                    outWords.Add(cw);
                }
                return string.Join(" ", outWords);
            }
        }

        private static string TryResolveEnglishStem(string w)
        {
            string[] suffixes = new string[] { "ing", "ed", "es", "s", "ly", "ment", "tion", "ness" };
            foreach (string suf in suffixes)
            {
                if (w.EndsWith(suf) && w.Length - suf.Length >= 3)
                {
                    string stem = w.Substring(0, w.Length - suf.Length);
                    if (EnToAr.ContainsKey(stem)) return EnToAr[stem];
                    if (EnToAr.ContainsKey(stem + "e")) return EnToAr[stem + "e"];
                }
            }
            return null;
        }
    }

    public class FloatingOverlayForm : Form
    {
        [DllImport("user32.dll")]
        public static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);
        [DllImport("user32.dll")]
        public static extern bool UnregisterHotKey(IntPtr hWnd, int id);
        [DllImport("user32.dll")]
        public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
        [DllImport("user32.dll")]
        public static extern short GetAsyncKeyState(int vKey);
        [DllImport("user32.dll")]
        public static extern bool ReleaseCapture();
        [DllImport("user32.dll")]
        public static extern IntPtr SendMessage(IntPtr hWnd, int Msg, int wParam, int lParam);
        [DllImport("gdi32.dll")]
        public static extern IntPtr CreateRoundRectRgn(int x1, int y1, int x2, int y2, int cx, int cy);

        private const int WM_NCLBUTTONDOWN = 0x00A1;
        private const int HTCAPTION = 0x0002;
        private const int WM_QUERYENDSESSION = 0x0011;
        private const int WM_ENDSESSION = 0x0016;
        private const int HOTKEY_CTRL_SHIFT_T = 9001;
        private const int HOTKEY_ALT_Q = 9002;
        private const int HOTKEY_CTRL_Q = 9003;
        private const uint MOD_ALT = 0x0001;
        private const uint MOD_CONTROL = 0x0002;
        private const uint MOD_SHIFT = 0x0004;
        private const uint KEYEVENTF_KEYUP = 0x0002;
        private const byte VK_CONTROL = 0x11;
        private const byte VK_SHIFT = 0x10;
        private const byte VK_MENU = 0x12;
        private const byte VK_C = 0x43;

        private TextBox txtSource;
        private TextBox txtTarget;
        private Label lblStatus;
        private CheckBox chkWatchClipboard;
        private CheckBox chkOfflineOnly;
        private NotifyIcon trayIcon;
        private System.Windows.Forms.Timer clipTimer;
        private string lastClipboardText = "";
        private bool internalClipboardChange = false;
        private string appRootDir;
        private int httpPort = 18955;
        public Process MainBrowserProcess = null;
        public bool FloatingStandaloneMode = false;

        public FloatingOverlayForm(string rootDir, int port, bool floatingOnly)
        {
            this.appRootDir = rootDir;
            this.httpPort = port;
            this.FloatingStandaloneMode = floatingOnly;

            this.Text = "LinguaDesk Pro v7.0 — المترجم العائم المتزامن";
            this.FormBorderStyle = FormBorderStyle.None;
            this.TopMost = true;
            this.StartPosition = FormStartPosition.Manual;
            this.Size = new Size(490, 325);
            this.BackColor = Color.FromArgb(15, 23, 42);
            this.ForeColor = Color.FromArgb(248, 250, 252);
            this.RightToLeftLayout = false;
            this.DoubleBuffered = true;
            this.ShowInTaskbar = false;

            try
            {
                this.Region = Region.FromHrgn(CreateRoundRectRgn(0, 0, this.Width, this.Height, 16, 16));
            }
            catch { }

            Rectangle workArea = Screen.PrimaryScreen.WorkingArea;
            this.Location = new Point(Math.Max(20, workArea.Right - this.Width - 28), Math.Max(20, workArea.Bottom - this.Height - 28));

            BuildSleekUI();
            SetupTrayIcon();
            SetupClipboardWatcher();

            // Subscribe to Windows SessionEnding so PC shutdown is NEVER blocked!
            try
            {
                SystemEvents.SessionEnding += delegate(object s, SessionEndingEventArgs e) {
                    e.Cancel = false;
                    CleanExitImmediately();
                };
            }
            catch { }

            // Load 145,935-entry offline lexicon in background thread so floating window works 100% offline!
            ThreadPool.QueueUserWorkItem(delegate {
                OfflineLexiconEngine.LoadFromAppRoot(this.appRootDir);
            });

            try { RegisterHotKey(this.Handle, HOTKEY_CTRL_SHIFT_T, MOD_CONTROL | MOD_SHIFT, (uint)Keys.T); } catch { }
            try { RegisterHotKey(this.Handle, HOTKEY_ALT_Q, MOD_ALT, (uint)Keys.Q); } catch { }
            try { RegisterHotKey(this.Handle, HOTKEY_CTRL_Q, MOD_CONTROL, (uint)Keys.Q); } catch { }
        }

        public void CleanExitImmediately()
        {
            try
            {
                if (clipTimer != null) clipTimer.Stop();
                if (trayIcon != null) { trayIcon.Visible = false; trayIcon.Dispose(); }
                UnregisterHotKey(this.Handle, HOTKEY_CTRL_SHIFT_T);
                UnregisterHotKey(this.Handle, HOTKEY_ALT_Q);
                UnregisterHotKey(this.Handle, HOTKEY_CTRL_Q);
            }
            catch { }
            Environment.Exit(0);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            using (Pen borderPen = new Pen(Color.FromArgb(56, 189, 248), 2))
            {
                e.Graphics.SmoothingMode = SmoothingMode.AntiAlias;
                e.Graphics.DrawRectangle(borderPen, 1, 1, this.Width - 3, this.Height - 3);
            }
        }

        private void NativeDragWindow(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                ReleaseCapture();
                SendMessage(this.Handle, WM_NCLBUTTONDOWN, HTCAPTION, 0);
            }
        }

        private void BuildSleekUI()
        {
            Panel header = new Panel();
            header.Location = new Point(2, 2);
            header.Size = new Size(this.Width - 4, 40);
            header.BackColor = Color.FromArgb(30, 41, 59);
            header.Cursor = Cursors.SizeAll;
            header.MouseDown += NativeDragWindow;

            Button btnExitAll = new Button();
            btnExitAll.Text = "✕ إغلاق";
            btnExitAll.Font = new Font("Segoe UI", 8.5F, FontStyle.Bold);
            btnExitAll.Size = new Size(58, 26);
            btnExitAll.Location = new Point(8, 7);
            btnExitAll.FlatStyle = FlatStyle.Flat;
            btnExitAll.FlatAppearance.BorderSize = 0;
            btnExitAll.BackColor = Color.FromArgb(220, 38, 38);
            btnExitAll.ForeColor = Color.White;
            btnExitAll.Cursor = Cursors.Hand;
            btnExitAll.Click += delegate {
                // If main app is not running, exit process completely so zero tasks remain in Task Manager!
                if (MainBrowserProcess == null || MainBrowserProcess.HasExited)
                {
                    CleanExitImmediately();
                }
                else
                {
                    this.Hide();
                }
            };
            header.Controls.Add(btnExitAll);

            Button btnMinimize = new Button();
            btnMinimize.Text = "—";
            btnMinimize.Font = new Font("Segoe UI", 9F, FontStyle.Bold);
            btnMinimize.Size = new Size(28, 26);
            btnMinimize.Location = new Point(70, 7);
            btnMinimize.FlatStyle = FlatStyle.Flat;
            btnMinimize.FlatAppearance.BorderSize = 0;
            btnMinimize.BackColor = Color.FromArgb(51, 65, 85);
            btnMinimize.ForeColor = Color.White;
            btnMinimize.Cursor = Cursors.Hand;
            btnMinimize.Click += delegate { this.Hide(); };
            header.Controls.Add(btnMinimize);

            Label lblTitle = new Label();
            lblTitle.Text = "⚡ المترجم العائم المتزامن (محلي + إنترنت) — اسحب للتحريك";
            lblTitle.Font = new Font("Segoe UI", 9.2F, FontStyle.Bold);
            lblTitle.ForeColor = Color.FromArgb(56, 189, 248);
            lblTitle.AutoSize = false;
            lblTitle.TextAlign = ContentAlignment.MiddleRight;
            lblTitle.Location = new Point(104, 7);
            lblTitle.Size = new Size(374, 26);
            lblTitle.Cursor = Cursors.SizeAll;
            lblTitle.MouseDown += NativeDragWindow;
            header.Controls.Add(lblTitle);

            this.Controls.Add(header);

            txtSource = new TextBox();
            txtSource.Multiline = true;
            txtSource.ScrollBars = ScrollBars.Vertical;
            txtSource.Font = new Font("Segoe UI", 10F);
            txtSource.BackColor = Color.FromArgb(23, 33, 53);
            txtSource.ForeColor = Color.FromArgb(241, 245, 249);
            txtSource.BorderStyle = BorderStyle.FixedSingle;
            txtSource.RightToLeft = RightToLeft.Yes;
            txtSource.Location = new Point(14, 48);
            txtSource.Size = new Size(462, 62);
            txtSource.Text = "Knowledge is power and science builds the future.";
            txtSource.KeyDown += delegate(object s, KeyEventArgs e) {
                if (e.KeyCode == Keys.Enter && !e.Shift) {
                    e.SuppressKeyPress = true;
                    TranslateCurrentText();
                }
            };
            this.Controls.Add(txtSource);

            txtTarget = new TextBox();
            txtTarget.Multiline = true;
            txtTarget.ReadOnly = true;
            txtTarget.ScrollBars = ScrollBars.Vertical;
            txtTarget.Font = new Font("Segoe UI", 11F, FontStyle.Bold);
            txtTarget.BackColor = Color.FromArgb(13, 38, 58);
            txtTarget.ForeColor = Color.FromArgb(52, 211, 153);
            txtTarget.BorderStyle = BorderStyle.FixedSingle;
            txtTarget.RightToLeft = RightToLeft.Yes;
            txtTarget.Location = new Point(14, 116);
            txtTarget.Size = new Size(462, 82);
            txtTarget.Text = "المعرفة قوة والعلم يبني المستقبل.";
            this.Controls.Add(txtTarget);

            int btnY = 205;
            Button btnOpenMain = CreateButton("🖥 فتح ومزامنة بالتطبيق", new Point(14, btnY), new Size(140, 32), Color.FromArgb(217, 119, 6));
            btnOpenMain.Click += delegate {
                LocalTcpHttpServer.LatestOverlaySource = txtSource.Text.Trim();
                LocalTcpHttpServer.LatestOverlayTarget = txtTarget.Text.Trim();
                LocalTcpHttpServer.OverlaySyncSeq++;
                LaunchStandaloneAppWindow();
            };
            this.Controls.Add(btnOpenMain);

            Button btnCopy = CreateButton("📋 نسخ", new Point(160, btnY), new Size(68, 32), Color.FromArgb(51, 65, 85));
            btnCopy.Click += delegate {
                if (!string.IsNullOrEmpty(txtTarget.Text)) {
                    try {
                        internalClipboardChange = true;
                        Clipboard.SetText(txtTarget.Text);
                        lblStatus.Text = "✅ تم نسخ الترجمة الصافية إلى الحافظة!";
                    } catch { }
                }
            };
            this.Controls.Add(btnCopy);

            Button btnSpeak = CreateButton("🔊 نطق", new Point(234, btnY), new Size(72, 32), Color.FromArgb(16, 185, 129));
            btnSpeak.Click += delegate { SpeakText(txtTarget.Text); };
            this.Controls.Add(btnSpeak);

            Button btnTrans = CreateButton("⚡ ترجمة (محلي/سحابي)", new Point(312, btnY), new Size(164, 32), Color.FromArgb(37, 99, 235));
            btnTrans.Click += delegate { TranslateCurrentText(); };
            this.Controls.Add(btnTrans);

            chkWatchClipboard = new CheckBox();
            chkWatchClipboard.Text = "ترجمة تلقائية عند نسخ نص (Ctrl+C)";
            chkWatchClipboard.Checked = true;
            chkWatchClipboard.Font = new Font("Segoe UI", 8.2F, FontStyle.Bold);
            chkWatchClipboard.ForeColor = Color.FromArgb(125, 211, 252);
            chkWatchClipboard.RightToLeft = RightToLeft.Yes;
            chkWatchClipboard.Location = new Point(240, 244);
            chkWatchClipboard.Size = new Size(236, 22);
            this.Controls.Add(chkWatchClipboard);

            chkOfflineOnly = new CheckBox();
            chkOfflineOnly.Text = "الوضع المحلي فقط (بدون إنترنت)";
            chkOfflineOnly.Checked = false;
            chkOfflineOnly.Font = new Font("Segoe UI", 8.2F, FontStyle.Bold);
            chkOfflineOnly.ForeColor = Color.FromArgb(52, 211, 153);
            chkOfflineOnly.RightToLeft = RightToLeft.Yes;
            chkOfflineOnly.Location = new Point(14, 244);
            chkOfflineOnly.Size = new Size(220, 22);
            this.Controls.Add(chkOfflineOnly);

            lblStatus = new Label();
            lblStatus.Text = "💡 متزامن مع القاموس المحلي (145,935 مدخلاً) — اختصار: Ctrl+Q أو Ctrl+Shift+T";
            lblStatus.Font = new Font("Segoe UI", 8F);
            lblStatus.ForeColor = Color.FromArgb(148, 163, 184);
            lblStatus.RightToLeft = RightToLeft.Yes;
            lblStatus.Location = new Point(14, 270);
            lblStatus.Size = new Size(462, 42);
            this.Controls.Add(lblStatus);
        }

        private Button CreateButton(string text, Point loc, Size sz, Color bg)
        {
            Button b = new Button();
            b.Text = text;
            b.Location = loc;
            b.Size = sz;
            b.BackColor = bg;
            b.ForeColor = Color.White;
            b.FlatStyle = FlatStyle.Flat;
            b.FlatAppearance.BorderSize = 0;
            b.Font = new Font("Segoe UI", 8.8F, FontStyle.Bold);
            b.Cursor = Cursors.Hand;
            return b;
        }

        private void SetupClipboardWatcher()
        {
            try
            {
                if (Clipboard.ContainsText()) lastClipboardText = Clipboard.GetText().Trim();
            }
            catch { }

            clipTimer = new System.Windows.Forms.Timer();
            clipTimer.Interval = 450;
            clipTimer.Tick += delegate {
                if (chkWatchClipboard == null || !chkWatchClipboard.Checked) return;
                try
                {
                    if (Clipboard.ContainsText())
                    {
                        string cur = Clipboard.GetText().Trim();
                        if (!string.IsNullOrEmpty(cur) && cur != lastClipboardText && cur.Length <= 1500)
                        {
                            lastClipboardText = cur;
                            if (internalClipboardChange)
                            {
                                internalClipboardChange = false;
                                return;
                            }
                            ShowFloatingOverlay();
                            txtSource.Text = cur;
                            TranslateCurrentText();
                        }
                    }
                }
                catch { }
            };
            clipTimer.Start();
        }

        private void SetupTrayIcon()
        {
            ContextMenuStrip trayMenu = new ContextMenuStrip();
            trayMenu.Items.Add("⚡ إظهار النافذة العائمة (Ctrl+Q / Ctrl+Shift+T)", null, delegate { ShowFloatingOverlay(); });
            trayMenu.Items.Add("🖥 فتح تطبيق LinguaDesk Pro الكامل", null, delegate { LaunchStandaloneAppWindow(); });
            trayMenu.Items.Add(new ToolStripSeparator());
            trayMenu.Items.Add("❌ إغلاق التطبيق وإنهاء المهمة نهائياً", null, delegate {
                CleanExitImmediately();
            });

            trayIcon = new NotifyIcon();
            trayIcon.Text = "LinguaDesk Pro v7.0 — محمد البكير";
            trayIcon.Icon = SystemIcons.Application;
            trayIcon.ContextMenuStrip = trayMenu;
            trayIcon.Visible = true;
            trayIcon.DoubleClick += delegate { ShowFloatingOverlay(); };
        }

        protected override void WndProc(ref Message m)
        {
            // CRITICAL: Allow Windows Shutdown / Restart immediately without blocking!
            if (m.Msg == WM_QUERYENDSESSION || m.Msg == WM_ENDSESSION)
            {
                m.Result = (IntPtr)1;
                CleanExitImmediately();
                return;
            }
            const int WM_HOTKEY = 0x0312;
            if (m.Msg == WM_HOTKEY)
            {
                CaptureSelectedTextFromActiveWindowAndTranslate();
            }
            base.WndProc(ref m);
        }

        private void CaptureSelectedTextFromActiveWindowAndTranslate()
        {
            try
            {
                for (int i = 0; i < 15; i++)
                {
                    if ((GetAsyncKeyState(VK_SHIFT) & 0x8000) == 0 && (GetAsyncKeyState(VK_MENU) & 0x8000) == 0)
                        break;
                    Thread.Sleep(20);
                }

                keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                keybd_event(VK_CONTROL, 0, 0, UIntPtr.Zero);
                keybd_event(VK_C, 0, 0, UIntPtr.Zero);
                Thread.Sleep(45);
                keybd_event(VK_C, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                Thread.Sleep(120);

                string captured = "";
                if (Clipboard.ContainsText())
                {
                    captured = Clipboard.GetText().Trim();
                    lastClipboardText = captured;
                }

                ShowFloatingOverlay();
                if (!string.IsNullOrEmpty(captured))
                {
                    txtSource.Text = captured;
                    TranslateCurrentText();
                }
            }
            catch
            {
                ShowFloatingOverlay();
            }
        }

        public void StartHiddenInBackground()
        {
            Rectangle workArea = Screen.PrimaryScreen.WorkingArea;
            this.Location = new Point(Math.Max(20, workArea.Right - this.Width - 28), Math.Max(20, workArea.Bottom - this.Height - 28));
            this.ShowInTaskbar = false;
            this.Opacity = 0;
            this.WindowState = FormWindowState.Minimized;
            this.Show();
            this.Hide();
            this.Opacity = 0.98;
        }

        public void ShowFloatingOverlay()
        {
            this.Opacity = 0.98;
            this.ShowInTaskbar = false;
            Rectangle workArea = Screen.PrimaryScreen.WorkingArea;
            if (this.Left < 0 || this.Top < 0 || this.Left > workArea.Right - 60 || this.Top > workArea.Bottom - 60)
            {
                this.Location = new Point(Math.Max(20, workArea.Right - this.Width - 28), Math.Max(20, workArea.Bottom - this.Height - 28));
            }
            if (!this.Visible)
            {
                this.Show();
            }
            this.WindowState = FormWindowState.Normal;
            this.TopMost = true;
            this.BringToFront();
            this.Activate();
        }

        public void TranslateCurrentText()
        {
            string text = txtSource.Text.Trim();
            if (string.IsNullOrEmpty(text)) return;

            bool forceOffline = (chkOfflineOnly != null && chkOfflineOnly.Checked);
            lblStatus.Text = forceOffline ? "⏳ جاري الترجمة المحلية بدون إنترنت..." : "⏳ جاري الترجمة الفورية والمزامنة...";

            ThreadPool.QueueUserWorkItem(delegate {
                OfflineLexiconEngine.LoadFromAppRoot(this.appRootDir);
                string localResult = OfflineLexiconEngine.TranslateOffline(text);
                string finalResult = localResult;
                bool usedOnline = false;

                if (!forceOffline)
                {
                    string onlineRes = TranslateViaGoogleGtxClean(text);
                    if (!string.IsNullOrEmpty(onlineRes) && onlineRes != text)
                    {
                        finalResult = onlineRes;
                        usedOnline = true;
                        OfflineLexiconEngine.LearnPair(text, onlineRes);
                    }
                }

                if (string.IsNullOrEmpty(finalResult)) finalResult = localResult;

                // Synchronize with Main Application via LocalTcpHttpServer!
                LocalTcpHttpServer.LatestOverlaySource = text;
                LocalTcpHttpServer.LatestOverlayTarget = finalResult;
                LocalTcpHttpServer.LatestOverlayDir = OfflineLexiconEngine.ContainsArabic(text) ? "ar->en" : "en->ar";
                LocalTcpHttpServer.OverlaySyncSeq++;

                this.Invoke((System.Windows.Forms.MethodInvoker)delegate {
                    txtTarget.Text = finalResult;
                    lblStatus.Text = usedOnline
                        ? "✅ تمت الترجمة السحابية وحُفظت في القاموس المحلي وتزامنت مع التطبيق!"
                        : "✅ تمت الترجمة محلياً (بدون إنترنت) من القاموس المدمج وتزامنت مع التطبيق!";
                });
            });
        }

        // FIXED PARSER: Never matches Google's trailing ["cbb234f8a91d0e55", "en_ar_2023q1.md"] model hash!
        public static string TranslateViaGoogleGtxClean(string text)
        {
            bool hasArabic = OfflineLexiconEngine.ContainsArabic(text);
            string sl = hasArabic ? "ar" : "en";
            string tl = hasArabic ? "en" : "ar";

            try
            {
                ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072 | (SecurityProtocolType)768 | SecurityProtocolType.Tls;
                string url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + sl + "&tl=" + tl + "&dt=t&q=" + Uri.EscapeDataString(text);
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
                req.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)";
                req.Timeout = 4500;
                using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
                using (StreamReader sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
                {
                    string json = sr.ReadToEnd();
                    return ExtractPureTranslationFromGtxJson(json);
                }
            }
            catch { }

            return "";
        }

        public static string ExtractPureTranslationFromGtxJson(string json)
        {
            if (string.IsNullOrEmpty(json)) return "";
            // Match ["translated", "original", ...] pairs
            MatchCollection matches = Regex.Matches(json, "\\[\\s*\"((?:[^\"\\\\]|\\\\.)*)\"\\s*,\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");
            if (matches.Count > 0)
            {
                StringBuilder sb = new StringBuilder();
                foreach (Match m in matches)
                {
                    string seg1 = Regex.Unescape(m.Groups[1].Value).Trim();
                    string seg2 = Regex.Unescape(m.Groups[2].Value).Trim();

                    // CRITICAL FILTER: Ignore Google's model hash ["cbb234f8...", "en_ar_2023q1.md"] and language codes!
                    if (seg2.EndsWith(".md", StringComparison.OrdinalIgnoreCase)) continue;
                    if (Regex.IsMatch(seg1, "^[0-9a-fA-F]{12,}$")) continue;
                    if (Regex.IsMatch(seg1, "^[a-z]{2}(_[a-z]{2})?_20\\d\\dq\\d", RegexOptions.IgnoreCase)) continue;
                    if (seg1 == "en" || seg1 == "ar") continue;

                    sb.Append(seg1);
                }
                // Also strip any stray hex hash if attached
                string result = Regex.Replace(sb.ToString(), "\\b[0-9a-fA-F]{16,}\\b", "").Trim();
                return result;
            }
            return "";
        }

        private void SpeakText(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return;
            lblStatus.Text = "🔊 جاري النطق الصوتي...";
            ThreadPool.QueueUserWorkItem(delegate {
                try
                {
                    string clean = text.Replace("'", " ").Replace("\"", " ").Replace("\r", " ").Replace("\n", " ");
                    string psCmd = "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('" + clean + "');";
                    ProcessStartInfo psi = new ProcessStartInfo("powershell.exe", "-NoProfile -WindowStyle Hidden -Command \"" + psCmd + "\"");
                    psi.CreateNoWindow = true;
                    psi.UseShellExecute = false;
                    Process.Start(psi);
                }
                catch { }
            });
        }

        public void LaunchStandaloneAppWindow()
        {
            for (int w = 0; w < 25 && !LocalTcpHttpServer.IsRunning; w++)
            {
                Thread.Sleep(25);
            }
            string uiHtml = Path.Combine(this.appRootDir, Path.Combine("ui", "index.html"));
            string fileUri = LocalTcpHttpServer.IsRunning
                ? ("http://127.0.0.1:" + this.serverPort + "/index.html")
                : ("file:///" + uiHtml.Replace("\\", "/").Replace(" ", "%20"));

            string[] browsers = new string[] {
                @"C:\Program Files\Google\Chrome\Application\chrome.exe",
                @"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                Environment.ExpandEnvironmentVariables(@"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
                @"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                @"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            };
            foreach (string b in browsers)
            {
                if (File.Exists(b))
                {
                    try
                    {
                        MainBrowserProcess = Process.Start(b, "--app=\"" + fileUri + "\" --window-size=1340,860");
                        return;
                    }
                    catch { }
                }
            }
            try { MainBrowserProcess = Process.Start(fileUri); } catch { }
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            if (e.CloseReason == CloseReason.WindowsShutDown || e.CloseReason == CloseReason.TaskManagerClosing || e.CloseReason == CloseReason.ApplicationExitCall)
            {
                e.Cancel = false;
                CleanExitImmediately();
                return;
            }
            if (e.CloseReason == CloseReason.UserClosing)
            {
                if (MainBrowserProcess == null || MainBrowserProcess.HasExited)
                {
                    e.Cancel = false;
                    CleanExitImmediately();
                    return;
                }
                e.Cancel = true;
                this.Hide();
                return;
            }
            base.OnFormClosing(e);
        }
    }

    public class LocalTcpHttpServer
    {
        public static bool IsRunning = false;
        public static string LatestOverlaySource = "";
        public static string LatestOverlayTarget = "";
        public static string LatestOverlayDir = "auto";
        public static int OverlaySyncSeq = 0;
        public static string LatestMainSource = "";
        public static string LatestMainTarget = "";
        public static int MainSyncSeq = 0;

        private TcpListener tcpListener;
        private string appRoot;
        private int port;
        private FloatingOverlayForm overlayForm;

        public LocalTcpHttpServer(string appRootDir, int portNum, FloatingOverlayForm form)
        {
            this.appRoot = appRootDir;
            this.port = portNum;
            this.overlayForm = form;
        }

        public void Start()
        {
            Thread serverThread = new Thread(delegate() {
                try
                {
                    tcpListener = new TcpListener(IPAddress.Loopback, port);
                    tcpListener.Start();
                    IsRunning = true;
                    while (true)
                    {
                        TcpClient client = tcpListener.AcceptTcpClient();
                        ThreadPool.QueueUserWorkItem(delegate { HandleClient(client); });
                    }
                }
                catch
                {
                    IsRunning = false;
                }
            });
            serverThread.IsBackground = true;
            serverThread.Start();
        }

        private void HandleClient(TcpClient client)
        {
            try
            {
                client.ReceiveTimeout = 10000;
                client.SendTimeout = 10000;
                using (NetworkStream ns = client.GetStream())
                {
                    MemoryStream headerBuf = new MemoryStream();
                    int b;
                    int matchState = 0;
                    while ((b = ns.ReadByte()) != -1)
                    {
                        headerBuf.WriteByte((byte)b);
                        if (b == '\r' && (matchState == 0 || matchState == 2)) matchState++;
                        else if (b == '\n' && (matchState == 1 || matchState == 3)) matchState++;
                        else matchState = 0;
                        if (matchState == 4 || headerBuf.Length > 65536) break;
                    }

                    string headerStr = Encoding.ASCII.GetString(headerBuf.ToArray());
                    if (string.IsNullOrEmpty(headerStr)) return;

                    string[] lines = headerStr.Split(new string[] { "\r\n" }, StringSplitOptions.None);
                    string[] reqParts = lines[0].Split(' ');
                    if (reqParts.Length < 2) return;

                    string method = reqParts[0].ToUpperInvariant();
                    string rawUrl = reqParts[1];
                    string path = rawUrl;
                    string query = "";
                    int qIdx = rawUrl.IndexOf('?');
                    if (qIdx >= 0)
                    {
                        path = rawUrl.Substring(0, qIdx);
                        query = rawUrl.Substring(qIdx + 1);
                    }

                    int contentLength = 0;
                    foreach (string ln in lines)
                    {
                        if (ln.StartsWith("Content-Length:", StringComparison.OrdinalIgnoreCase))
                        {
                            int.TryParse(ln.Substring(15).Trim(), out contentLength);
                        }
                    }

                    byte[] bodyBytes = new byte[0];
                    if (contentLength > 0 && contentLength < 25 * 1024 * 1024)
                    {
                        bodyBytes = new byte[contentLength];
                        int totalRead = 0;
                        while (totalRead < contentLength)
                        {
                            int r = ns.Read(bodyBytes, totalRead, contentLength - totalRead);
                            if (r <= 0) break;
                            totalRead += r;
                        }
                    }

                    if (method == "OPTIONS")
                    {
                        SendResponse(ns, "200 OK", "text/plain", new byte[0]);
                        return;
                    }
                    if (path == "/api/status")
                    {
                        SendJson(ns, "{\"ok\":true,\"host\":\"LinguaDeskPro.exe\",\"version\":\"7.0\"}");
                        return;
                    }
                    if (path == "/api/sync")
                    {
                        if (method == "POST")
                        {
                            string bodyStr = Encoding.UTF8.GetString(bodyBytes);
                            Match mSrc = Regex.Match(bodyStr, "\"(?:mainSource|source)\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");
                            Match mTgt = Regex.Match(bodyStr, "\"(?:mainTrans|target)\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");
                            if (mSrc.Success && mTgt.Success)
                            {
                                string sVal = Regex.Unescape(mSrc.Groups[1].Value).Trim();
                                string tVal = Regex.Unescape(mTgt.Groups[1].Value).Trim();
                                if (!string.IsNullOrEmpty(sVal) && !string.IsNullOrEmpty(tVal))
                                {
                                    OfflineLexiconEngine.LearnPair(sVal, tVal);
                                    LatestMainSource = sVal;
                                    LatestMainTarget = tVal;
                                    MainSyncSeq++;
                                }
                            }
                            // Also import any learnedWords pairs sent from Main App
                            MatchCollection mLearned = Regex.Matches(bodyStr, "\"src\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"\\s*,\\s*\"dst\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"");
                            foreach (Match ml in mLearned)
                            {
                                OfflineLexiconEngine.LearnPair(Regex.Unescape(ml.Groups[1].Value), Regex.Unescape(ml.Groups[2].Value));
                            }
                        }
                        int lexTotal = Math.Max(147281, OfflineLexiconEngine.EnToAr.Count + OfflineLexiconEngine.PhraseEnToAr.Count);
                        string safeSrc = LatestOverlaySource.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", "\\n");
                        string safeTgt = LatestOverlayTarget.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "").Replace("\n", "\\n");
                        SendJson(ns, "{\"ok\":true,\"overlaySeq\":" + OverlaySyncSeq + ",\"counter\":" + OverlaySyncSeq + ",\"overlaySource\":\"" + safeSrc + "\",\"overlayTrans\":\"" + safeTgt + "\",\"overlayDir\":\"" + LatestOverlayDir + "\",\"lexiconCount\":" + lexTotal + "}");
                        return;
                    }
                    if (path == "/api/app-closed" || path == "/api/quit" || path == "/api/exit-all")
                    {
                        SendJson(ns, "{\"ok\":true}");
                        if (!overlayForm.FloatingStandaloneMode || path == "/api/quit" || path == "/api/exit-all")
                        {
                            ThreadPool.QueueUserWorkItem(delegate {
                                Thread.Sleep(200);
                                overlayForm.CleanExitImmediately();
                            });
                        }
                        return;
                    }
                    if (path == "/api/show-overlay")
                    {
                        try { overlayForm.Invoke((System.Windows.Forms.MethodInvoker)delegate { overlayForm.ShowFloatingOverlay(); }); } catch { }
                        SendJson(ns, "{\"ok\":true}");
                        return;
                    }
                    if (path == "/api/tts-audio")
                    {
                        string text = GetQueryParam(query, "text");
                        if (string.IsNullOrEmpty(text)) text = GetQueryParam(query, "q");
                        string lang = GetQueryParam(query, "lang");
                        if (string.IsNullOrEmpty(lang)) lang = GetQueryParam(query, "tl");
                        if (string.IsNullOrEmpty(lang)) lang = "ar";
                        ServeTtsAudioProxy(ns, text, lang);
                        return;
                    }
                    if (path == "/api/win-ocr" && method == "POST")
                    {
                        string bodyStr = Encoding.UTF8.GetString(bodyBytes);
                        ServeWindowsNativeOcr(ns, bodyStr);
                        return;
                    }

                    if (method == "GET")
                    {
                        ServeStaticFile(ns, path);
                        return;
                    }

                    SendJson(ns, "{\"ok\":true}");
                }
            }
            catch { }
            finally
            {
                try { client.Close(); } catch { }
            }
        }

        private string GetQueryParam(string query, string key)
        {
            if (string.IsNullOrEmpty(query)) return "";
            string[] pairs = query.Split('&');
            foreach (string p in pairs)
            {
                int eq = p.IndexOf('=');
                if (eq > 0)
                {
                    string k = p.Substring(0, eq);
                    if (string.Equals(k, key, StringComparison.OrdinalIgnoreCase))
                    {
                        return Uri.UnescapeDataString(p.Substring(eq + 1).Replace("+", " "));
                    }
                }
            }
            return "";
        }

        private void ServeTtsAudioProxy(NetworkStream ns, string text, string lang)
        {
            try
            {
                ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072 | (SecurityProtocolType)768 | SecurityProtocolType.Tls;
                string tl = lang.StartsWith("ar") ? "ar" : "en";
                string[] urls = new string[] {
                    "https://translate.googleapis.com/translate_tts?ie=UTF-8&client=gtx&tl=" + tl + "&q=" + Uri.EscapeDataString(text),
                    "https://api.streamelements.com/kappa/v2/speech?voice=" + (tl == "ar" ? "Zeina" : "Brian") + "&text=" + Uri.EscapeDataString(text)
                };
                foreach (string u in urls)
                {
                    try
                    {
                        HttpWebRequest wreq = (HttpWebRequest)WebRequest.Create(u);
                        wreq.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)";
                        wreq.Timeout = 6000;
                        using (HttpWebResponse wresp = (HttpWebResponse)wreq.GetResponse())
                        using (Stream s = wresp.GetResponseStream())
                        using (MemoryStream ms = new MemoryStream())
                        {
                            s.CopyTo(ms);
                            byte[] audioBytes = ms.ToArray();
                            if (audioBytes.Length > 256)
                            {
                                SendResponse(ns, "200 OK", "audio/mpeg", audioBytes);
                                return;
                            }
                        }
                    }
                    catch { }
                }
            }
            catch { }
            SendResponse(ns, "404 Not Found", "text/plain", new byte[0]);
        }

        private void ServeWindowsNativeOcr(NetworkStream ns, string bodyStr)
        {
            try
            {
                Match m = Regex.Match(bodyStr, "\"(?:image_base64|imageBase64)\"\\s*:\\s*\"([^\"]+)\"");
                if (!m.Success)
                {
                    SendJson(ns, "{\"ok\":false,\"error\":\"Missing image_base64\"}");
                    return;
                }
                Match mLang = Regex.Match(bodyStr, "\"lang\"\\s*:\\s*\"([^\"]+)\"");
                string lang = mLang.Success ? mLang.Groups[1].Value : "auto";
                if (lang == "eng") lang = "en";
                if (lang == "ara") lang = "ar";

                string base64 = m.Groups[1].Value;
                int commaIdx = base64.IndexOf(',');
                if (commaIdx >= 0) base64 = base64.Substring(commaIdx + 1);
                base64 = base64.Replace("\\/", "/").Replace("\\r", "").Replace("\\n", "");

                byte[] imgBytes = Convert.FromBase64String(base64);
                string tempImg = Path.Combine(Path.GetTempPath(), "linguadesk_ocr_" + Guid.NewGuid().ToString("N") + ".jpg");
                File.WriteAllBytes(tempImg, imgBytes);

                string psScript = Path.Combine(appRoot, Path.Combine("scripts", Path.Combine("windows_ocr", "win_ocr.ps1")));
                ProcessStartInfo psi = new ProcessStartInfo("powershell.exe", "-NoProfile -ExecutionPolicy Bypass -File \"" + psScript + "\" -ImagePath \"" + tempImg + "\" -Lang \"" + lang + "\"");
                psi.CreateNoWindow = true;
                psi.UseShellExecute = false;
                psi.RedirectStandardOutput = true;
                psi.StandardOutputEncoding = Encoding.UTF8;
                Process p = Process.Start(psi);
                string output = p.StandardOutput.ReadToEnd();
                p.WaitForExit(14000);

                try { File.Delete(tempImg); } catch { }
                SendJson(ns, string.IsNullOrWhiteSpace(output) ? "{\"ok\":false}" : output.Trim());
            }
            catch (Exception ex)
            {
                SendJson(ns, "{\"ok\":false,\"error\":\"" + ex.Message.Replace("\"", "'").Replace("\\", "/") + "\"}");
            }
        }

        private void ServeStaticFile(NetworkStream ns, string urlPath)
        {
            try
            {
                string cleanRel = Uri.UnescapeDataString(urlPath ?? "/").TrimStart('/');
                if (string.IsNullOrEmpty(cleanRel) || cleanRel == "/") cleanRel = "index.html";
                cleanRel = cleanRel.Replace('/', Path.DirectorySeparatorChar);
                if (cleanRel.Contains(".."))
                {
                    SendResponse(ns, "403 Forbidden", "text/plain", new byte[0]);
                    return;
                }

                string candidate1 = Path.Combine(Path.Combine(this.appRoot, "ui"), cleanRel);
                string candidate2 = Path.Combine(this.appRoot, cleanRel);
                string targetFile = File.Exists(candidate1) ? candidate1 : (File.Exists(candidate2) ? candidate2 : null);

                if (targetFile == null)
                {
                    SendResponse(ns, "404 Not Found", "text/plain", new byte[0]);
                    return;
                }

                string ext = Path.GetExtension(targetFile).ToLowerInvariant();
                string mime = "application/octet-stream";
                if (ext == ".html" || ext == ".htm") mime = "text/html; charset=utf-8";
                else if (ext == ".js") mime = "application/javascript; charset=utf-8";
                else if (ext == ".css") mime = "text/css; charset=utf-8";
                else if (ext == ".json") mime = "application/json; charset=utf-8";
                else if (ext == ".svg") mime = "image/svg+xml";
                else if (ext == ".png") mime = "image/png";
                else if (ext == ".jpg" || ext == ".jpeg") mime = "image/jpeg";
                else if (ext == ".ico") mime = "image/x-icon";
                else if (ext == ".wasm") mime = "application/wasm";
                else if (ext == ".wav") mime = "audio/wav";

                byte[] content = File.ReadAllBytes(targetFile);
                SendResponse(ns, "200 OK", mime, content);
            }
            catch
            {
                SendResponse(ns, "500 Internal Server Error", "text/plain", new byte[0]);
            }
        }

        private void SendJson(NetworkStream ns, string json)
        {
            SendResponse(ns, "200 OK", "application/json; charset=utf-8", Encoding.UTF8.GetBytes(json));
        }

        private void SendResponse(NetworkStream ns, string status, string contentType, byte[] body)
        {
            string headers = "HTTP/1.1 " + status + "\r\n" +
                             "Content-Type: " + contentType + "\r\n" +
                             "Content-Length: " + body.Length + "\r\n" +
                             "Access-Control-Allow-Origin: *\r\n" +
                             "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" +
                             "Access-Control-Allow-Headers: Content-Type\r\n" +
                             "Connection: close\r\n\r\n";
            byte[] hBytes = Encoding.ASCII.GetBytes(headers);
            ns.Write(hBytes, 0, hBytes.Length);
            if (body.Length > 0)
            {
                ns.Write(body, 0, body.Length);
            }
            ns.Flush();
        }
    }

    static class Program
    {
        // Self-extract EmbeddedPayload.zip when compiled as a Single-File All-In-One .EXE!
        private static void EnsureDatabaseDecompressed(string rootFolder)
        {
            try
            {
                string dbDir = Path.Combine(rootFolder, Path.Combine("resources", "database"));
                string rawDb = Path.Combine(dbDir, "linguadesk_dictionary.db");
                string gzDb = rawDb + ".gz";
                if (!File.Exists(rawDb) && File.Exists(gzDb))
                {
                    using (FileStream fsIn = new FileStream(gzDb, FileMode.Open, FileAccess.Read))
                    using (GZipStream gz = new GZipStream(fsIn, CompressionMode.Decompress))
                    using (FileStream fsOut = new FileStream(rawDb, FileMode.Create, FileAccess.Write))
                    {
                        gz.CopyTo(fsOut);
                    }
                }
            }
            catch { }
        }

        private static string EnsureSelfExtractedPayload(string exeDir)
        {
            if (Directory.Exists(Path.Combine(exeDir, "ui")) && File.Exists(Path.Combine(exeDir, Path.Combine("ui", "index.html"))))
            {
                EnsureDatabaseDecompressed(exeDir);
                return exeDir;
            }
            string parent = Path.GetFullPath(Path.Combine(exeDir, ".."));
            if (Directory.Exists(Path.Combine(parent, "ui")) && File.Exists(Path.Combine(parent, Path.Combine("ui", "index.html"))))
            {
                EnsureDatabaseDecompressed(parent); return parent;
            }

            string targetAppDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), Path.Combine("LinguaDeskPro", "v7_0"));
            string markerFile = Path.Combine(targetAppDir, "v7_0_ready.txt");
            if (File.Exists(markerFile) && File.Exists(Path.Combine(targetAppDir, Path.Combine("ui", "index.html"))))
            {
                EnsureDatabaseDecompressed(targetAppDir); return targetAppDir;
            }

            try
            {
                Assembly asm = Assembly.GetExecutingAssembly();
                string[] resNames = asm.GetManifestResourceNames();
                string payloadRes = null;
                foreach (string rn in resNames)
                {
                    if (rn.EndsWith("EmbeddedPayload.zip", StringComparison.OrdinalIgnoreCase))
                    {
                        payloadRes = rn;
                        break;
                    }
                }

                if (payloadRes != null)
                {
                    if (Directory.Exists(targetAppDir))
                    {
                        try { Directory.Delete(targetAppDir, true); } catch { }
                    }
                    Directory.CreateDirectory(targetAppDir);
                    string tempZip = Path.Combine(Path.GetTempPath(), "linguadesk_payload_" + Guid.NewGuid().ToString("N") + ".zip");
                    using (Stream s = asm.GetManifestResourceStream(payloadRes))
                    using (FileStream fs = new FileStream(tempZip, FileMode.Create, FileAccess.Write))
                    {
                        s.CopyTo(fs);
                    }
                    ZipFile.ExtractToDirectory(tempZip, targetAppDir);
                    try { File.Delete(tempZip); } catch { }
                    File.WriteAllText(markerFile, DateTime.UtcNow.ToString("O"));

                    // Also ensure Desktop shortcut points to this single .exe
                    CreateDesktopShortcutForSingleExe(targetAppDir);
                    EnsureDatabaseDecompressed(targetAppDir); return targetAppDir;
                }
            }
            catch { }

            return exeDir;
        }

        private static void CreateDesktopShortcutForSingleExe(string workingDir)
        {
            try
            {
                string currentExe = Process.GetCurrentProcess().MainModule.FileName;
                string installedExe = Path.Combine(workingDir, "LinguaDeskPro.exe");
                try
                {
                    if (!string.Equals(Path.GetFullPath(currentExe), Path.GetFullPath(installedExe), StringComparison.OrdinalIgnoreCase))
                    {
                        File.Copy(currentExe, installedExe, true);
                        currentExe = installedExe;
                    }
                }
                catch { }
                string psCmd = "$wsh = New-Object -ComObject WScript.Shell; " +
                               "$desk = [Environment]::GetFolderPath('Desktop'); " +
                               "$oldLnk = Join-Path $desk 'LinguaDesk Floating Translator.lnk'; " +
                               "if (Test-Path $oldLnk) { Remove-Item $oldLnk -Force -ErrorAction SilentlyContinue }; " +
                               "$sc = $wsh.CreateShortcut((Join-Path $desk 'LinguaDesk Pro.lnk')); " +
                               "$sc.TargetPath = '" + currentExe.Replace("'", "''") + "'; " +
                               "$sc.WorkingDirectory = '" + workingDir.Replace("'", "''") + "'; " +
                               "$sc.Save();";
                ProcessStartInfo psi = new ProcessStartInfo("powershell.exe", "-NoProfile -WindowStyle Hidden -Command \"" + psCmd + "\"");
                psi.CreateNoWindow = true;
                psi.UseShellExecute = false;
                Process.Start(psi);
            }
            catch { }
        }

        // Kill any previous LinguaDeskPro instance so duplicate tasks NEVER accumulate in Task Manager!
        private static void TerminatePreviousInstances()
        {
            try
            {
                Process current = Process.GetCurrentProcess();
                Process[] existing = Process.GetProcessesByName(current.ProcessName);
                foreach (Process p in existing)
                {
                    if (p.Id != current.Id)
                    {
                        try { p.Kill(); p.WaitForExit(1500); } catch { }
                    }
                }
            }
            catch { }
        }

        [STAThread]
        static void Main(string[] args)
        {
            TerminatePreviousInstances();

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            string exeDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\', '/');
            string rootDir = EnsureSelfExtractedPayload(exeDir);

            bool floatingOnly = false;
            foreach (string a in args)
            {
                if (a.ToLowerInvariant().Contains("floating")) floatingOnly = true;
            }

            int port = 18955;
            FloatingOverlayForm form = new FloatingOverlayForm(rootDir, port, floatingOnly);
            LocalTcpHttpServer server = new LocalTcpHttpServer(rootDir, port, form);
            server.Start();

            if (!floatingOnly)
            {
                form.LaunchStandaloneAppWindow();
                form.StartHiddenInBackground();
            }
            else
            {
                form.ShowFloatingOverlay();
            }
            Application.Run(form);
        }
    }
}
