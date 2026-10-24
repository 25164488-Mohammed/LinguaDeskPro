using System;
using System.IO;
using System.Security.Cryptography;

namespace LinguaDeskPro.Core
{
    /// <summary>
    /// Verifies local resource integrity (SHA-256) and prevents accidental deletion of protected core files.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public class ResourceManagerService
    {
        public static string ComputeFileSha256(string filePath)
        {
            if (!File.Exists(filePath))
                throw new FileNotFoundException("ملف المورد اللغوي غير موجود في المسار المحدد.", filePath);

            using var sha = SHA256.Create();
            using var stream = File.OpenRead(filePath);
            byte[] hash = sha.ComputeHash(stream);
            return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
        }

        public static bool CanDeleteResource(bool isCoreProtected, out string reasonAr)
        {
            if (isCoreProtected)
            {
                reasonAr = "لا يمكن حذف هذا المورد لأنه من المكونات الأساسية الضرورية لعمل القاموس والترجمة دون إنترنت.";
                return false;
            }
            reasonAr = "يمكن حذف المورد الاختياري بأمان.";
            return true;
        }
    }
}
