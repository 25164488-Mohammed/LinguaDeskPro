using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace LinguaDeskPro.OCR
{
    /// <summary>
    /// Local OCR Wrapper for Tesseract OCR (Arabic + English) & Scanned PDFs.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public class LocalOcrService
    {
        private readonly string _tesseractExecutable;

        public LocalOcrService(string tesseractExecutable = "tesseract")
        {
            _tesseractExecutable = tesseractExecutable;
        }

        public async Task<(bool Success, string ExtractedText, string ErrorAr)> ExtractTextFromImageAsync(
            string imagePath,
            string languages = "eng+ara",
            CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(imagePath) || !File.Exists(imagePath))
                return (false, string.Empty, "ملف الصورة المحدد غير موجود.");

            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = _tesseractExecutable,
                    Arguments = $""{imagePath}" stdout -l {languages}",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var proc = Process.Start(psi);
                if (proc == null)
                    return (false, string.Empty, "تعذر تشغيل محرك التعرف الضوئي المحلي Tesseract.");

                string output = await proc.StandardOutput.ReadToEndAsync(cancellationToken);
                string err = await proc.StandardError.ReadToEndAsync(cancellationToken);
                await proc.WaitForExitAsync(cancellationToken);

                if (proc.ExitCode != 0 && string.IsNullOrWhiteSpace(output))
                    return (false, string.Empty, $"خطأ أثناء قراءة النص من الصورة: {err}");

                return (true, output.Trim(), string.Empty);
            }
            catch (Exception ex)
            {
                return (false, string.Empty, $"وحدة OCR المحلية غير مثبتة أو تعذر تشغيلها: {ex.Message}");
            }
        }
    }
}
