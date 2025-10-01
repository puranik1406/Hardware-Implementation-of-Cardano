require('dotenv').config();
const express = require('express');
const cors = require('cors');
const SokosumiClient = require('./sokosumi-client');
const EmotionAnalyzer = require('./emotion-analyzer');

const app = express();
const PORT = process.env.SOKOSUMI_SERVICE_PORT || 7001;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Sokosumi client
const sokosumiClient = new SokosumiClient(
  process.env.SOKOSUMI_API_KEY,
  process.env.SOKOSUMI_API_URL
);

// Initialize Emotion Analyzer
const emotionAnalyzer = new EmotionAnalyzer(
  parseInt(process.env.SOKOSUMI_EMOTION_THRESHOLD || '50')
);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Sokosumi Emotional AI Agent',
    timestamp: new Date().toISOString()
  });
});

// Get agent input schema
app.get('/api/schema', async (req, res) => {
  try {
    const schema = await sokosumiClient.getInputSchema();
    res.json({
      success: true,
      data: schema
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Analyze emotion from text input
 * POST /api/analyze
 * Body: { text: "string" } or { statements: ["string1", "string2"] }
 */
app.post('/api/analyze', async (req, res) => {
  try {
    const { text, statements } = req.body;

    if (!text && !statements) {
      return res.status(400).json({
        success: false,
        error: 'Either "text" or "statements" field is required'
      });
    }

    // Convert to statements array
    const inputStatements = statements || [text];

    console.log(`\n=== Starting Emotional Analysis ===`);
    console.log(`Input: ${JSON.stringify(inputStatements)}`);

    // Create Sokosumi job
    const jobCreation = await sokosumiClient.createEmotionalAnalysisJob(
      inputStatements,
      `Arduino Emotion Check - ${Date.now()}`
    );

    console.log(`Job created: ${jobCreation.data.id}`);

    // Wait for job completion
    const jobResult = await sokosumiClient.waitForJobCompletion(
      jobCreation.data.id,
      300000, // 5 minutes max wait
      5000    // Check every 5 seconds
    );

    console.log(`Job completed: ${jobResult.data.status}`);

    // Analyze emotional content
    const analysis = emotionAnalyzer.analyze(jobResult);

    console.log(`\n=== Emotional Analysis Result ===`);
    console.log(`Positive Score: ${analysis.sentiment.positiveScore}%`);
    console.log(`Negative Score: ${analysis.sentiment.negativeScore}%`);
    console.log(`Approved: ${analysis.sentiment.approved}`);
    console.log(`Reason: ${analysis.sentiment.reason}`);

    res.json({
      success: true,
      jobId: jobCreation.data.id,
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
 * Check job status
 * GET /api/job/:jobId
 */
app.get('/api/job/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params;
    const jobStatus = await sokosumiClient.getJobStatus(jobId);

    res.json({
      success: true,
      data: jobStatus
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Quick sentiment check - simplified endpoint
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

    // Create and analyze
    const jobCreation = await sokosumiClient.createEmotionalAnalysisJob([text]);
    const jobResult = await sokosumiClient.waitForJobCompletion(jobCreation.data.id);
    const analysis = emotionAnalyzer.analyze(jobResult);

    console.log(`Result: ${analysis.sentiment.approved ? 'APPROVED' : 'REJECTED'}`);

    res.json({
      success: true,
      approved: analysis.sentiment.approved,
      reason: analysis.sentiment.reason,
      scores: {
        positive: analysis.sentiment.positiveScore,
        negative: analysis.sentiment.negativeScore
      },
      timestamp: new Date().toISOString()
    });

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
  console.log(`\n✅ Sokosumi Emotional AI Agent Service`);
  console.log(`🌐 Running on port ${PORT}`);
  console.log(`🔑 API Key configured: ${process.env.SOKOSUMI_API_KEY ? 'Yes' : 'No'}`);
  console.log(`📊 Emotion threshold: ${process.env.SOKOSUMI_EMOTION_THRESHOLD || '50'}%`);
  console.log(`\n📡 Available endpoints:`);
  console.log(`  GET  /health - Health check`);
  console.log(`  GET  /api/schema - Get agent schema`);
  console.log(`  POST /api/analyze - Full emotional analysis`);
  console.log(`  POST /api/check - Quick sentiment check`);
  console.log(`  GET  /api/job/:jobId - Get job status`);
  console.log(`\n`);
});

module.exports = app;
