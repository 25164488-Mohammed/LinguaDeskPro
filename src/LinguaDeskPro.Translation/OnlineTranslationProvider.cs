using System;
using System.Net.Http;
using System.Net.NetworkInformation;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace LinguaDeskPro.Translation
{
    /// <summary>
    /// Optional Online Translation Provider over HTTPS with strict user consent, timeout, and no infinite retries.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public class OnlineTranslationProvider
    {
        private readonly HttpClient _httpClient;

        public OnlineTranslationProvider()
        {
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(8)
            };
        }

        public static bool IsNetworkLikelyAvailable()
        {
            return NetworkInterface.GetIsNetworkAvailable();
        }

        public async Task<(bool Success, string TranslatedText, string ProviderName, string ErrorMessage)> TranslateOnlineAsync(
            string text,
            string sourceLang,
            string targetLang,
            string endpointUrl,
            string? apiKey,
            bool userExplicitlyApproved,
            CancellationToken cancellationToken = default)
        {
            if (!userExplicitlyApproved)
            {
                return (false, string.Empty, "Blocked (Privacy Guard)",
                    "تم حظر الاتصال الخارجي: يتطلب التطبيق موافقة المستخدم الصريحة قبل إرسال أي نص عبر الإنترنت.");
            }

            if (string.IsNullOrWhiteSpace(endpointUrl) || !endpointUrl.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
            {
                return (false, string.Empty, "HTTPS Security Guard",
                    "يجب أن يستخدم مزود الترجمة الخارجي بروتوكول HTTPS الآمن.");
            }

            try
            {
                var payload = new
                {
                    q = text,
                    source = sourceLang == "auto" ? "en" : sourceLang,
                    target = targetLang,
                    format = "text",
                    api_key = apiKey ?? string.Empty
                };

                using var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");
                using var response = await _httpClient.PostAsync(endpointUrl, content, cancellationToken);

                if (!response.IsSuccessStatusCode)
                {
                    return (false, string.Empty, endpointUrl,
                        $"فشلت خدمة الترجمة الخارجية (رمز الحالة: {(int)response.StatusCode}). يظل المحرك المحلي والقاموس يعملان بالكامل.");
                }

                string json = await response.Content.ReadAsStringAsync(cancellationToken);
                using var doc = JsonDocument.Parse(json);
                if (doc.RootElement.TryGetProperty("translatedText", out var transProp))
                {
                    return (true, transProp.GetString() ?? string.Empty, "Online API (Verified HTTPS)", string.Empty);
                }

                return (false, string.Empty, endpointUrl, "استجابة غير متوقعة من الخادم الخارجي.");
            }
            catch (TaskCanceledException)
            {
                return (false, string.Empty, endpointUrl, "انتهت مهلة الاتصال بالإنترنت (Timeout) دون استجابة. تم الاكتفاء بالنتائج المحلية.");
            }
            catch (Exception ex)
            {
                return (false, string.Empty, endpointUrl, $"تعذر الوصول إلى خدمة الترجمة الخارجية: {ex.Message}");
            }
        }
    }
}
