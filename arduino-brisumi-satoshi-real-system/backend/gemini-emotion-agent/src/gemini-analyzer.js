const { GoogleGenerativeAI } = require('@google/generative-ai');

class GeminiEmotionAnalyzer {
  constructor(apiKey) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    // Try gemini-pro or fallback to available model
    try {
      this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' });
    } catch (error) {
      console.log('Trying alternative model...');
      this.model = this.genAI.getGenerativeModel({ model: 'models/gemini-pro' });
    }
  }

  /**
   * Analyze emotional content using Gemini AI
   * @param {string} text - Text to analyze
   * @returns {Promise<Object>} Analysis result with emotional scores
   */
  async analyzeEmotion(text) {
    try {
      const prompt = `Analyze the emotional sentiment of the following text and provide scores:

Text: "${text}"

Provide a JSON response with:
1. positiveScore (0-100): How positive/happy/excited the text is
2. negativeScore (0-100): How negative/sad/frustrated the text is
3. emotions: List of detected emotions (joy, sadness, anger, fear, surprise, etc.)
4. overallSentiment: "positive", "negative", or "neutral"
5. confidence (0-100): Confidence in the analysis

Return ONLY valid JSON, no additional text.`;

      console.log('Sending request to Gemini AI...');
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const responseText = response.text();

      console.log('Gemini AI raw response:', responseText);

      // Extract JSON from response (Gemini sometimes adds markdown)
      let jsonText = responseText;
      if (responseText.includes('```json')) {
        jsonText = responseText.split('```json')[1].split('```')[0].trim();
      } else if (responseText.includes('```')) {
        jsonText = responseText.split('```')[1].split('```')[0].trim();
      }

      const analysis = JSON.parse(jsonText);

      return {
        success: true,
        positiveScore: parseFloat(analysis.positiveScore) || 0,
        negativeScore: parseFloat(analysis.negativeScore) || 0,
        emotions: analysis.emotions || [],
        overallSentiment: analysis.overallSentiment || 'neutral',
        confidence: parseFloat(analysis.confidence) || 0,
        rawAnalysis: analysis
      };

    } catch (error) {
      console.error('Error analyzing emotion with Gemini:', error);
      throw error;
    }
  }

  /**
   * Determine if transaction should be approved based on emotional analysis
   * @param {string} text - Text to analyze
   * @param {number} threshold - Positive emotion threshold (default 50%)
   * @returns {Promise<Object>} Approval decision with reasoning
   */
  async checkApproval(text, threshold = 50) {
    try {
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
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('Error in approval check:', error);
      return {
        success: false,
        approved: false,
        error: error.message,
        reason: `Error analyzing emotion: ${error.message}`
      };
    }
  }
}

module.exports = GeminiEmotionAnalyzer;
