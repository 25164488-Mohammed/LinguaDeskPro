using System;
using System.Collections.Generic;
using System.Speech.Synthesis;

namespace LinguaDeskPro.Speech
{
    /// <summary>
    /// Native Windows Offline Speech Synthesis (SAPI5 / System.Speech) with UK/US/Arabic voice inspection and Slow Learner Mode.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public class OfflineSpeechService : IDisposable
    {
        private readonly SpeechSynthesizer _synthesizer;

        public OfflineSpeechService()
        {
            _synthesizer = new SpeechSynthesizer();
            _synthesizer.SetOutputToDefaultAudioDevice();
        }

        public List<object> GetInstalledLocalVoices()
        {
            var voices = new List<object>();
            foreach (var v in _synthesizer.GetInstalledVoices())
            {
                if (!v.Enabled) continue;
                var info = v.VoiceInfo;
                voices.Add(new
                {
                    Name = info.Name,
                    Culture = info.Culture.Name,
                    Gender = info.Gender.ToString(),
                    Description = info.Description
                });
            }
            return voices;
        }

        public (bool Success, string MessageAr) SpeakAsync(string text, string preferredCulture = "en-US", bool slowLearnerMode = false, int rate = 0)
        {
            if (string.IsNullOrWhiteSpace(text))
                return (false, "النص فارغ؛ لا يوجد محتوى للنطق.");

            try
            {
                _synthesizer.SpeakAsyncCancelAll();
                _synthesizer.Rate = slowLearnerMode ? -4 : Math.Clamp(rate, -10, 10);

                foreach (var v in _synthesizer.GetInstalledVoices())
                {
                    if (v.Enabled && v.VoiceInfo.Culture.Name.StartsWith(preferredCulture, StringComparison.OrdinalIgnoreCase))
                    {
                        _synthesizer.SelectVoice(v.VoiceInfo.Name);
                        break;
                    }
                }

                _synthesizer.SpeakAsync(text);
                return (true, "جاري تشغيل النطق الصوتي المحلي.");
            }
            catch (Exception ex)
            {
                return (false, $"تعذر تشغيل الصوت المحلي على هذا الجهاز: {ex.Message}");
            }
        }

        public void Stop()
        {
            _synthesizer.SpeakAsyncCancelAll();
        }

        public void Dispose()
        {
            _synthesizer.Dispose();
        }
    }
}
