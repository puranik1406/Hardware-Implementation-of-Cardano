/**
 * Simple Sentiment Analyzer (Mock Implementation)
 * This demonstrates the concept while Gemini API configuration is verified
 */

class SimpleSentimentAnalyzer {
  constructor() {
    // Positive words
    this.positiveWords = [
      'happy', 'excited', 'great', 'amazing', 'wonderful', 'excellent', 'fantastic',
      'love', 'enjoy', 'pleased', 'delighted', 'thrilled', 'joyful', 'awesome',
      'perfect', 'brilliant', 'outstanding', 'superb', 'good', 'nice', 'beautiful'
    ];

    // Negative words
    this.negativeWords = [
      'sad', 'angry', 'frustrated', 'terrible', 'horrible', 'awful', 'bad',
      'hate', 'dislike', 'annoyed', 'upset', 'disappointed', 'worried', 'scared',
      'poor', 'worst', 'fail', 'problem', 'issue', 'wrong', 'difficult'
    ];
  }

  /**
   * Analyze emotional content
   * @param {string} text - Text to analyze
   * @returns {Promise<Object>} Analysis result
   */
  async analyzeEmotion(text) {
    const lowerText = text.toLowerCase();
    const words = lowerText.split(/\s+/);

    let positiveCount = 0;
    let negativeCount = 0;
    const detectedEmotions = [];

    // Count positive words
    this.positiveWords.forEach(word => {
      if (lowerText.includes(word)) {
        positiveCount++;
        if (!detectedEmotions.includes('joy')) detectedEmotions.push('joy');
      }
    });

    // Count negative words
    this.negativeWords.forEach(word => {
      if (lowerText.includes(word)) {
        negativeCount++;
        if (word.includes('sad')) detectedEmotions.push('sadness');
        if (word.includes('angry') || word.includes('frustrat')) detectedEmotions.push('anger');
        if (word.includes('scared') || word.includes('worried')) detectedEmotions.push('fear');
      }
    });

    // Calculate scores
    const totalEmotionalWords = positiveCount + negativeCount;
    const positiveScore = totalEmotionalWords > 0 
      ? (positiveCount / totalEmotionalWords) * 100 
      : 50;
    const negativeScore = totalEmotionalWords > 0 
      ? (negativeCount / totalEmotionalWords) * 100 
      : 50;

    // Determine sentiment
    let overallSentiment = 'neutral';
    if (positiveScore > negativeScore + 10) overallSentiment = 'positive';
    else if (negativeScore > positiveScore + 10) overallSentiment = 'negative';

    if (detectedEmotions.length === 0) {
      detectedEmotions.push(overallSentiment === 'positive' ? 'contentment' : 'neutral');
    }

    return {
      success: true,
      positiveScore,
      negativeScore,
      emotions: detectedEmotions,
      overallSentiment,
      confidence: totalEmotionalWords > 0 ? Math.min(totalEmotionalWords * 20, 100) : 50,
      rawAnalysis: {
        positiveWords: positiveCount,
        negativeWords: negativeCount,
        totalWords: words.length
      }
    };
  }

  /**
   * Check if transaction should be approved
   * @param {string} text - Text to analyze
   * @param {number} threshold - Approval threshold
   * @returns {Promise<Object>} Approval decision
   */
  async checkApproval(text, threshold = 50) {
    const analysis = await this.analyzeEmotion(text);

    const approved = analysis.positiveScore > analysis.negativeScore && 
                    analysis.positiveScore >= threshold;

    return {
      success: true,
      approved,
      positiveScore: analysis.positiveScore.toFixed(2),
      negativeScore: analysis.negativeScore.toFixed(2),
      overallSentiment: analysis.overallSentiment,
      emotions: analysis.emotions,
      confidence: analysis.confidence,
      reason: approved 
        ? `Positive emotion (${analysis.positiveScore.toFixed(2)}%) exceeds negative (${analysis.negativeScore.toFixed(2)}%) - Transaction approved!`
        : `Insufficient positive emotion. Positive: ${analysis.positiveScore.toFixed(2)}%, Negative: ${analysis.negativeScore.toFixed(2)}% - Transaction rejected.`,
      threshold,
      timestamp: new Date().toISOString(),
      note: "Using simplified sentiment analysis for demonstration"
    };
  }
}

module.exports = SimpleSentimentAnalyzer;
