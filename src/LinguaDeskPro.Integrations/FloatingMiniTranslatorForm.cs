using System;
using System.Drawing;
using System.Windows.Forms;

namespace LinguaDeskPro.Integrations
{
    /// <summary>
    /// Lightweight Floating Mini-Translator Window that pops up on Global Shortcut (Ctrl+Shift+T).
    /// Supports Pin-on-Top, Copy Result, and Open in Main LinguaDesk Pro Window.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public class FloatingMiniTranslatorForm : Form
    {
        private readonly Label _titleLabel;
        private readonly TextBox _sourceBox;
        private readonly TextBox _resultBox;
        private readonly Button _copyBtn;
        private readonly Button _pinBtn;
        private readonly Button _openMainBtn;
        private bool _isPinned = true;

        public event Action<string>? OpenInMainWindowRequested;

        public FloatingMiniTranslatorForm()
        {
            Text = "LinguaDesk Pro — الترجمة السريعة (عمل محمد البكير)";
            FormBorderStyle = FormBorderStyle.FixedToolWindow;
            StartPosition = FormStartPosition.Manual;
            Size = new Size(440, 290);
            TopMost = true;
            BackColor = Color.FromArgb(15, 23, 42);
            ForeColor = Color.FromArgb(241, 245, 249);
            RightToLeft = RightToLeft.Yes;
            RightToLeftLayout = true;

            _titleLabel = new Label
            {
                Text = "⚡ نافذة الترجمة السريعة العائمة — LinguaDesk Pro",
                Dock = DockStyle.Top,
                Height = 32,
                TextAlign = ContentAlignment.MiddleLeft,
                Padding = new Padding(8, 0, 8, 0),
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold),
                ForeColor = Color.FromArgb(96, 165, 250)
            };

            _sourceBox = new TextBox
            {
                Multiline = true,
                ReadOnly = true,
                Height = 65,
                Dock = DockStyle.Top,
                BackColor = Color.FromArgb(30, 41, 59),
                ForeColor = Color.FromArgb(226, 232, 240),
                BorderStyle = BorderStyle.FixedSingle,
                Font = new Font("Segoe UI", 9.5f)
            };

            _resultBox = new TextBox
            {
                Multiline = true,
                ReadOnly = true,
                Height = 105,
                Dock = DockStyle.Top,
                BackColor = Color.FromArgb(15, 23, 42),
                ForeColor = Color.FromArgb(52, 211, 153),
                BorderStyle = BorderStyle.FixedSingle,
                Font = new Font("Segoe UI", 10.5f, FontStyle.Bold)
            };

            var bottomPanel = new FlowLayoutPanel
            {
                Dock = DockStyle.Bottom,
                Height = 44,
                Padding = new Padding(6),
                FlowDirection = FlowDirection.RightToLeft
            };

            _copyBtn = new Button { Text = "نسخ الترجمة", Width = 105, Height = 30, FlatStyle = FlatStyle.Flat };
            _pinBtn = new Button { Text = "📌 مثبت فوق النوافذ", Width = 130, Height = 30, FlatStyle = FlatStyle.Flat };
            _openMainBtn = new Button { Text = "فتح بالتطبيق الرئيسي", Width = 145, Height = 30, FlatStyle = FlatStyle.Flat };

            _copyBtn.Click += (_, _) =>
            {
                if (!string.IsNullOrEmpty(_resultBox.Text))
                    Clipboard.SetText(_resultBox.Text);
            };

            _pinBtn.Click += (_, _) =>
            {
                _isPinned = !_isPinned;
                TopMost = _isPinned;
                _pinBtn.Text = _isPinned ? "📌 مثبت فوق النوافذ" : "غير مثبت";
            };

            _openMainBtn.Click += (_, _) =>
            {
                OpenInMainWindowRequested?.Invoke(_sourceBox.Text);
                Hide();
            };

            bottomPanel.Controls.AddRange(new Control[] { _copyBtn, _pinBtn, _openMainBtn });
            Controls.Add(_resultBox);
            Controls.Add(_sourceBox);
            Controls.Add(_titleLabel);
            Controls.Add(bottomPanel);
        }

        public void ShowPopupNearCursor(string sourceText, string translatedText)
        {
            _sourceBox.Text = sourceText;
            _resultBox.Text = translatedText;

            Point cursor = Cursor.Position;
            Location = new Point(Math.Max(10, cursor.X - Width / 2), Math.Max(10, cursor.Y + 20));
            Show();
            BringToFront();
        }
    }
}
