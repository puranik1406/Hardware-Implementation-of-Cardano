/**
 * Emotional Analyzer
 * Analyzes emotional content and determines if transaction should proceed
 */

class EmotionAnalyzer {
  constructor(positiveThreshold = 50) {
    this.positiveThreshold = positiveThreshold; // Percentage threshold for positive emotions
  }

  /**
   * Parse Sokosumi emotional analysis output
   * @param {object} jobResult - The completed job result from Sokosumi
   * @returns {object} Parsed emotional data
   */
  parseEmotionalData(jobResult) {
    try {
      // Extract output from job result
      const output = jobResult.data.output;
      
      if (!output) {
        throw new Error('No output data in job result');
      }

      // Parse the output if it's a string
      const parsedOutput = typeof output === 'string' ? JSON.parse(output) : output;

      return {
        raw: parsedOutput,
        statements: parsedOutput.statements || [],
        summary: parsedOutput.summary || {}
      };
    } catch (error) {
      console.error('Error parsing emotional data:', error);
      throw error;
    }
  }

  /**
   * Calculate overall emotional sentiment
   * @param {object} emotionalData - Parsed emotional data
   * @returns {object} Sentiment scores and decision
   */
  calculateSentiment(emotionalData) {
    const { statements } = emotionalData;

    if (!statements || statements.length === 0) {
      return {
        positiveScore: 0,
        negativeScore: 0,
        approved: false,
        reason: 'No statements to analyze'
      };
    }

    let totalPositive = 0;
    let totalNegative = 0;
    let statementCount = 0;

    // Analyze each statement
    statements.forEach(statement => {
      const signals = statement.signals || {};
      
      // Positive indicators
      const businessOpportunity = signals.businessOpportunity || signals.Business_Opportunity || 0;
      
      // Negative indicators
      const churnRisk = signals.churnRisk || signals.Churn_Risk || 0;
      const emotionalUrgency = signals.emotionalUrgency || signals.Emotional_Urgency || 0;
      const serviceComplexity = signals.serviceComplexity || signals.Service_Complexity || 0;

      // Calculate positive and negative scores for this statement
      const positiveScore = businessOpportunity;
      const negativeScore = (churnRisk + emotionalUrgency + serviceComplexity) / 3;

      totalPositive += positiveScore;
      totalNegative += negativeScore;
      statementCount++;

      console.log(`Statement "${statement.text?.substring(0, 50)}...":`, {
        positive: positiveScore,
        negative: negativeScore
      });
    });

    // Calculate averages
    const avgPositive = totalPositive / statementCount;
    const avgNegative = totalNegative / statementCount;

    // Determine if transaction should be approved
    const approved = avgPositive > avgNegative && avgPositive >= this.positiveThreshold;

    return {
      positiveScore: avgPositive.toFixed(2),
      negativeScore: avgNegative.toFixed(2),
      approved,
      reason: approved 
        ? `Positive emotion (${avgPositive.toFixed(2)}%) exceeds negative (${avgNegative.toFixed(2)}%)`
        : `Insufficient positive emotion. Positive: ${avgPositive.toFixed(2)}%, Negative: ${avgNegative.toFixed(2)}%`,
      details: {
        totalStatements: statementCount,
        threshold: this.positiveThreshold
      }
    };
  }

  /**
   * Analyze text and determine if transaction should proceed
   * @param {object} jobResult - Completed Sokosumi job result
   * @returns {object} Analysis result with approval decision
   */
  analyze(jobResult) {
    try {
      const emotionalData = this.parseEmotionalData(jobResult);
      const sentiment = this.calculateSentiment(emotionalData);

      return {
        success: true,
        emotionalData,
        sentiment,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error analyzing emotions:', error);
      return {
        success: false,
        error: error.message,
        sentiment: {
          approved: false,
          reason: `Analysis error: ${error.message}`
        }
      };
    }
  }
}

module.exports = EmotionAnalyzer;
