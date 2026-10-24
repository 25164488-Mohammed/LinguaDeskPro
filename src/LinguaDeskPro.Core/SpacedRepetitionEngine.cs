using System;

namespace LinguaDeskPro.Core
{
    /// <summary>
    /// SuperMemo SM-2 Spaced Repetition Scheduler for student vocabulary review.
    /// عمل محمد البكير — Mohammed Al-Bakir
    /// </summary>
    public static class SpacedRepetitionEngine
    {
        /// <summary>
        /// Updates an SRS flashcard based on recall quality (0..5: 5=Easy, 3=Medium, 1=Hard/Forgot).
        /// </summary>
        public static void ApplyReview(SrsFlashcardDto card, int qualityGrade)
        {
            qualityGrade = Math.Clamp(qualityGrade, 0, 5);
            if (qualityGrade >= 3)
            {
                if (card.RepetitionCount == 0)
                    card.IntervalDays = 1;
                else if (card.RepetitionCount == 1)
                    card.IntervalDays = 4;
                else
                    card.IntervalDays = (int)Math.Round(card.IntervalDays * card.EasinessFactor);

                card.RepetitionCount++;
            }
            else
            {
                card.RepetitionCount = 0;
                card.IntervalDays = 1;
            }

            double ef = card.EasinessFactor + (0.1 - (5 - qualityGrade) * (0.08 + (5 - qualityGrade) * 0.02));
            card.EasinessFactor = Math.Max(1.3, Math.Round(ef, 2));
            card.Difficulty = qualityGrade >= 4 ? "Easy" : (qualityGrade >= 3 ? "Medium" : "Hard");
            card.NextReviewDate = DateTime.UtcNow.AddDays(card.IntervalDays).ToString("yyyy-MM-dd");
        }
    }
}
