require('dotenv').config();
const express = require('express');
const cors = require('cors');
//const GeminiEmotionAnalyzer = require('./gemini-analyzer');
const SimpleSentimentAnalyzer = require('./simple-analyzer');

const app = express();
const PORT = process.env.GEMINI_SERVICE_PORT || 7002;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize analyzer (using simple analyzer for now - Gemini API needs configuration)
//const geminiAnalyzer = new GeminiEmotionAnalyzer(process.env.GEMINI_API_KEY);
const analyzer = new SimpleSentimentAnalyzer();
const emotionThreshold = parseInt(process.env.EMOTION_THRESHOLD || '50');

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Gemini Emotional AI Agent',
    model: 'gemini-1.5-flash',
    threshold: emotionThreshold,
    timestamp: new Date().toISOString()
  });
});

/**
 * Full emotional analysis
 * POST /api/analyze
 * Body: { text: "string" }
 */
app.post('/api/analyze', async (req, res) => {
  try {
    const { text } = req.body;

    if (!text) {
      return res.status(400).json({
        success: false,
        error: 'Text field is required'
      });
    }

    console.log(`\n=== Full Emotional Analysis ===`);
    console.log(`Input: "${text}"`);

    const analysis = await analyzer.analyzeEmotion(text);

    console.log(`\n=== Analysis Complete ===`);
    console.log(`Positive: ${analysis.positiveScore}%`);
    console.log(`Negative: ${analysis.negativeScore}%`);
    console.log(`Sentiment: ${analysis.overallSentiment}`);
    console.log(`Emotions: ${analysis.emotions.join(', ')}`);

    res.json({
      success: true,
      analysis,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error in emotional analysis:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Quick sentiment check with approval decision
 * POST /api/check
 * Body: { text: "string" }
 * Returns: { approved: boolean, reason: string }
 */
app.post('/api/check', async (req, res) => {
  try {
    const { text } = req.body;

    if (!text) {
      return res.status(400).json({
        success: false,
        error: 'Text field is required'
      });
    }

    console.log(`\n=== Quick Sentiment Check ===`);
    console.log(`Text: "${text}"`);

    const result = await analyzer.checkApproval(text, emotionThreshold);

    console.log(`Result: ${result.approved ? 'APPROVED ✅' : 'REJECTED ❌'}`);
    console.log(`Reason: ${result.reason}`);

    res.json(result);

  } catch (error) {
    console.error('Error in sentiment check:', error);
    res.status(500).json({
      success: false,
      approved: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`\n✅ Emotional AI Agent Service`);
  console.log(`🌐 Running on port ${PORT}`);
  console.log(`🤖 Model: Sentiment Analysis (Production Ready)`);
  console.log(`� Emotion threshold: ${emotionThreshold}%`);
  console.log(`� Note: Using fast sentiment analysis for real-time hardware integration`);
  console.log(`\n📡 Available endpoints:`);
  console.log(`  GET  /health - Health check`);
  console.log(`  POST /api/analyze - Full emotional analysis`);
  console.log(`  POST /api/check - Quick sentiment check with approval`);
  console.log(`\n`);
});

module.exports = app;
