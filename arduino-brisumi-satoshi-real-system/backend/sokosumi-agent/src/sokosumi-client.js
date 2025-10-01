const axios = require('axios');

class SokosumiClient {
  constructor(apiKey, apiUrl = 'https://app.sokosumi.com/api') {
    this.apiKey = apiKey;
    this.apiUrl = apiUrl;
    this.emotionalAgentId = 'cmd7lmdt50ln39d1217yxlps8'; // HybridAI Emotional Sensing Agent
  }

  /**
   * Get the input schema for the emotional sensing agent
   */
  async getInputSchema() {
    try {
      const response = await axios.get(
        `${this.apiUrl}/v1/agents/${this.emotionalAgentId}/input-schema`,
        {
          headers: {
            'x-api-key': this.apiKey
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching input schema:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Create a job for emotional analysis
   * @param {string|string[]} statements - Text statement(s) to analyze
   * @param {string} jobName - Optional job name
   * @param {number} maxCredits - Maximum credits to spend
   */
  async createEmotionalAnalysisJob(statements, jobName = null, maxCredits = 10) {
    try {
      // Ensure statements is an array
      const inputStatements = Array.isArray(statements) ? statements : [statements];

      const payload = {
        maxAcceptedCredits: maxCredits,
        name: jobName || `Emotion Analysis - ${new Date().toISOString()}`,
        inputData: {
          statements: inputStatements
        }
      };

      console.log('Creating Sokosumi job with payload:', JSON.stringify(payload, null, 2));

      const response = await axios.post(
        `${this.apiUrl}/v1/agents/${this.emotionalAgentId}/jobs`,
        payload,
        {
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': this.apiKey
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error creating emotional analysis job:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Get job status and results
   * @param {string} jobId - The job ID to check
   */
  async getJobStatus(jobId) {
    try {
      const response = await axios.get(
        `${this.apiUrl}/v1/jobs/${jobId}`,
        {
          headers: {
            'x-api-key': this.apiKey
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching job status:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Wait for job completion and return results
   * @param {string} jobId - The job ID to wait for
   * @param {number} maxWaitTime - Maximum wait time in milliseconds (default: 5 minutes)
   * @param {number} pollInterval - Polling interval in milliseconds (default: 5 seconds)
   */
  async waitForJobCompletion(jobId, maxWaitTime = 300000, pollInterval = 5000) {
    const startTime = Date.now();

    while (Date.now() - startTime < maxWaitTime) {
      const jobStatus = await this.getJobStatus(jobId);

      console.log(`Job ${jobId} status: ${jobStatus.data.status}`);

      if (jobStatus.data.status === 'completed' || jobStatus.data.agentJobStatus === 'completed') {
        return jobStatus;
      }

      if (jobStatus.data.status === 'failed' || jobStatus.data.agentJobStatus === 'failed') {
        throw new Error(`Job failed: ${JSON.stringify(jobStatus.data)}`);
      }

      // Wait before polling again
      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error(`Job ${jobId} did not complete within ${maxWaitTime}ms`);
  }
}

module.exports = SokosumiClient;
