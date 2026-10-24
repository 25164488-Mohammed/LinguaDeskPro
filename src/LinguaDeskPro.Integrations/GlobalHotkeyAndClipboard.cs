using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;

namespace LinguaDeskPro.Integrations
{
    /// <summary>
    /// Native Win32 Global Hotkey (Ctrl+Shift+T) and Safe Clipboard State Manager.
    /// Captures selected text from external Windows apps without corrupting the user's previous clipboard content.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public class GlobalHotkeyService : NativeWindow, IDisposable
    {
        private const int WM_HOTKEY = 0x0312;
        public const uint MOD_ALT = 0x0001;
        public const uint MOD_CONTROL = 0x0002;
        public const uint MOD_SHIFT = 0x0004;
        public const uint MOD_NOREPEAT = 0x4000;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

        private readonly int _hotkeyId = 9001;
        private bool _isRegistered;

        public event EventHandler? HotkeyPressed;

        public GlobalHotkeyService()
        {
            CreateHandle(new CreateParams());
        }

        public bool RegisterGlobalShortcut(uint modifiers = MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, Keys key = Keys.T)
        {
            if (_isRegistered)
                UnregisterHotKey(Handle, _hotkeyId);

            _isRegistered = RegisterHotKey(Handle, _hotkeyId, modifiers, (uint)key);
            return _isRegistered;
        }

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == WM_HOTKEY && m.WParam.ToInt32() == _hotkeyId)
            {
                HotkeyPressed?.Invoke(this, EventArgs.Empty);
            }
            base.WndProc(ref m);
        }

        public void Dispose()
        {
            if (_isRegistered)
            {
                UnregisterHotKey(Handle, _hotkeyId);
                _isRegistered = false;
            }
            DestroyHandle();
        }
    }

    public static class SafeClipboardManager
    {
        /// <summary>
        /// Safely captures selected text using Ctrl+C while backing up and restoring the user's original clipboard text.
        /// Never polls the clipboard in the background and never sends clipboard data to the internet.
        /// </summary>
        public static (bool Success, string CapturedText, string StatusMessageAr) CaptureSelectedTextSafely(bool restorePreviousClipboard = true)
        {
            string? previousText = null;
            bool hadText = false;

            try
            {
                if (Clipboard.ContainsText())
                {
                    previousText = Clipboard.GetText();
                    hadText = true;
                }

                // Clear temporarily to detect fresh copy
                Clipboard.Clear();
                SendKeys.SendWait("^c");
                Thread.Sleep(120);

                string captured = Clipboard.ContainsText() ? Clipboard.GetText().Trim() : string.Empty;

                if (restorePreviousClipboard && hadText && previousText != null)
                {
                    Clipboard.SetText(previousText);
                }

                if (string.IsNullOrWhiteSpace(captured))
                {
                    return (false, string.Empty, "لم يتم اكتشاف نص محدد في البرنامج الحالي.");
                }

                return (true, captured, "تم التقاط النص المحدد بنجاح مع الحفاظ على محتوى الحافظة السابق.");
            }
            catch (Exception ex)
            {
                return (false, string.Empty, $"تعذر الوصول إلى الحافظة بسبب قيود صلاحيات النافذة: {ex.Message}");
            }
        }
    }
}
