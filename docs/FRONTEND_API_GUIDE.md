# NextFitAI Frontend Integration Guide

## 🚀 Quick Start

**Base URL**: `https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod`

**Complete Workflow**:
1. Submit resume analysis → `POST /analyze`
2. Poll for results → `GET /results/{analysis_id}`
3. Monitor system health → `GET /health`

## 📋 API Reference

### 1. Submit Analysis
**Endpoint**: `POST /analyze`

**Request**:
```javascript
const submitAnalysis = async (resumeText, jobDescription) => {
  const analysisId = crypto.randomUUID(); // Generate unique ID
  
  const response = await fetch('https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      analysis_id: analysisId,
      resume_text: resumeText,
      job_description: jobDescription
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
};
```

**Response**:
```json
{
  "status": "submitted",
  "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
  "estimated_completion": "2025-06-30T10:46:10.063857"
}
```

### 2. Get Analysis Results
**Endpoint**: `GET /results/{analysis_id}`

**Request**:
```javascript
const getAnalysisResults = async (analysisId) => {
  const response = await fetch(`https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/results/${analysisId}`);
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Analysis not found');
    }
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
};
```

**Response (Completed)**:
```json
{
  "status": "completed",
  "results": {
    "match_score": 85,
    "missing_skills": ["Python", "AWS", "Docker"],
    "recommendations": [
      "Add quantified achievements (e.g., 'Increased efficiency by 25%')",
      "Include relevant keywords from the job description"
    ],
    "confidence_score": 92,
    "analysis_timestamp": "2025-06-29T10:35:00Z"
  }
}
```

**Response (Processing)**:
```json
{
  "status": "processing",
  "message": "Analysis is currently being processed"
}
```

### 3. Health Check
**Endpoint**: `GET /health`

**Request**:
```javascript
const checkSystemHealth = async () => {
  const response = await fetch('https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/health');
  return await response.json();
};
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-29T10:00:00Z",
  "checks": {
    "dynamodb": {"status": "healthy", "message": "Connected successfully"},
    "s3": {"status": "healthy", "message": "Bucket accessible"},
    "environment": {"status": "healthy", "message": "All required variables present"}
  }
}
```

## 🔧 TypeScript Definitions

```typescript
// Request Types
interface AnalysisRequest {
  analysis_id: string;
  resume_text: string;
  job_description: string;
}

// Response Types
interface SubmitAnalysisResponse {
  status: 'submitted';
  analysis_id: string;
  estimated_completion: string;
}

interface AnalysisResults {
  match_score: number;
  missing_skills: string[];
  recommendations: string[];
  confidence_score: number;
  analysis_timestamp: string;
}

interface CompletedAnalysisResponse {
  status: 'completed';
  results: AnalysisResults;
}

interface ProcessingAnalysisResponse {
  status: 'processing';
  message: string;
}

interface FailedAnalysisResponse {
  status: 'failed';
  error: string;
  timestamp: string;
}

type AnalysisResponse = CompletedAnalysisResponse | ProcessingAnalysisResponse | FailedAnalysisResponse;

interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  message: string;
}

interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  checks: {
    dynamodb: HealthCheck;
    s3: HealthCheck;
    environment: HealthCheck;
  };
}

interface ErrorResponse {
  error: string;
}
```

## ⚛️ React Integration Examples

### Custom Hook for Resume Analysis

```typescript
import { useState, useCallback } from 'react';

interface UseResumeAnalysisReturn {
  submitAnalysis: (resumeText: string, jobDescription: string) => Promise<void>;
  pollForResults: (analysisId: string) => Promise<void>;
  isLoading: boolean;
  isPolling: boolean;
  results: AnalysisResults | null;
  error: string | null;
  analysisId: string | null;
  status: 'idle' | 'submitting' | 'polling' | 'completed' | 'failed';
}

export const useResumeAnalysis = (): UseResumeAnalysisReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'submitting' | 'polling' | 'completed' | 'failed'>('idle');

  const submitAnalysis = useCallback(async (resumeText: string, jobDescription: string) => {
    setIsLoading(true);
    setError(null);
    setStatus('submitting');
    
    try {
      const newAnalysisId = crypto.randomUUID();
      
      const response = await fetch('https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_id: newAnalysisId,
          resume_text: resumeText,
          job_description: jobDescription
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to submit analysis: ${response.status}`);
      }

      const data: SubmitAnalysisResponse = await response.json();
      setAnalysisId(data.analysis_id);
      
      // Automatically start polling
      await pollForResults(data.analysis_id);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      setStatus('failed');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const pollForResults = useCallback(async (id: string) => {
    setIsPolling(true);
    setStatus('polling');
    
    const maxAttempts = 30; // 1 minute with 2-second intervals
    let attempts = 0;

    const poll = async (): Promise<void> => {
      try {
        const response = await fetch(`https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/results/${id}`);
        
        if (!response.ok) {
          throw new Error(`Failed to get results: ${response.status}`);
        }

        const data: AnalysisResponse = await response.json();

        if (data.status === 'completed') {
          setResults(data.results);
          setStatus('completed');
          setIsPolling(false);
          return;
        }

        if (data.status === 'failed') {
          setError(data.error);
          setStatus('failed');
          setIsPolling(false);
          return;
        }

        // Still processing, continue polling
        attempts++;
        if (attempts >= maxAttempts) {
          throw new Error('Analysis timeout - please try again');
        }

        setTimeout(poll, 2000); // Poll every 2 seconds
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        setStatus('failed');
        setIsPolling(false);
      }
    };

    await poll();
  }, []);

  return {
    submitAnalysis,
    pollForResults,
    isLoading,
    isPolling,
    results,
    error,
    analysisId,
    status
  };
};
```

### Complete Resume Analyzer Component

```tsx
import React, { useState } from 'react';
import { useResumeAnalysis } from './hooks/useResumeAnalysis';

export const ResumeAnalyzer: React.FC = () => {
  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  
  const {
    submitAnalysis,
    isLoading,
    isPolling,
    results,
    error,
    status
  } = useResumeAnalysis();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!resumeText.trim() || !jobDescription.trim()) {
      alert('Please fill in both resume and job description');
      return;
    }

    await submitAnalysis(resumeText, jobDescription);
  };

  const getStatusMessage = () => {
    switch (status) {
      case 'submitting':
        return 'Submitting your analysis...';
      case 'polling':
        return 'Analyzing your resume... This may take up to 30 seconds.';
      case 'completed':
        return 'Analysis completed!';
      case 'failed':
        return 'Analysis failed. Please try again.';
      default:
        return '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">NextFitAI Resume Analyzer</h1>
      
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-6 mb-8">
        <div>
          <label htmlFor="resume" className="block text-sm font-medium mb-2">
            Resume Text
          </label>
          <textarea
            id="resume"
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume content here..."
            className="w-full h-40 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || isPolling}
          />
        </div>
        
        <div>
          <label htmlFor="jobDescription" className="block text-sm font-medium mb-2">
            Job Description
          </label>
          <textarea
            id="jobDescription"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here..."
            className="w-full h-40 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || isPolling}
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading || isPolling}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading || isPolling ? 'Analyzing...' : 'Analyze Resume'}
        </button>
      </form>

      {/* Status Message */}
      {status !== 'idle' && (
        <div className={`p-4 rounded-md mb-6 ${
          status === 'failed' ? 'bg-red-100 text-red-700' : 
          status === 'completed' ? 'bg-green-100 text-green-700' : 
          'bg-blue-100 text-blue-700'
        }`}>
          <div className="flex items-center">
            {(isLoading || isPolling) && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
            )}
            {getStatusMessage()}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-6">Analysis Results</h2>
          
          {/* Match Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-lg font-medium">Match Score</span>
              <span className="text-2xl font-bold text-blue-600">{results.match_score}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${results.match_score}%` }}
              ></div>
            </div>
          </div>

          {/* Confidence Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-lg font-medium">Confidence Score</span>
              <span className="text-xl font-semibold text-green-600">{results.confidence_score}%</span>
            </div>
          </div>

          {/* Missing Skills */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Missing Skills</h3>
            <div className="flex flex-wrap gap-2">
              {results.missing_skills.map((skill, index) => (
                <span 
                  key={index}
                  className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Recommendations</h3>
            <ul className="space-y-2">
              {results.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  <span className="text-gray-700">{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Timestamp */}
          <div className="mt-6 pt-4 border-t border-gray-200 text-sm text-gray-500">
            Analysis completed: {new Date(results.analysis_timestamp).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
};
```

## 🔄 Advanced Patterns

### Retry Logic with Exponential Backoff

```typescript
const fetchWithRetry = async (
  url: string, 
  options: RequestInit, 
  maxRetries: number = 3
): Promise<Response> => {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      
      // Don't retry on client errors (4xx)
      if (response.status >= 400 && response.status < 500) {
        return response;
      }
      
      // Retry on server errors (5xx) or network issues
      if (response.ok || attempt === maxRetries) {
        return response;
      }
      
      throw new Error(`HTTP ${response.status}`);
      
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');
      
      if (attempt < maxRetries) {
        // Exponential backoff: 1s, 2s, 4s
        const delay = Math.pow(2, attempt) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError!;
};
```

### Caching Strategy

```typescript
class AnalysisCache {
  private cache = new Map<string, { data: AnalysisResponse; timestamp: number }>();
  private readonly TTL = 5 * 60 * 1000; // 5 minutes

  get(analysisId: string): AnalysisResponse | null {
    const cached = this.cache.get(analysisId);
    
    if (!cached) return null;
    
    // Check if cache is expired
    if (Date.now() - cached.timestamp > this.TTL) {
      this.cache.delete(analysisId);
      return null;
    }
    
    return cached.data;
  }

  set(analysisId: string, data: AnalysisResponse): void {
    this.cache.set(analysisId, {
      data,
      timestamp: Date.now()
    });
  }

  clear(): void {
    this.cache.clear();
  }
}

const analysisCache = new AnalysisCache();

const getCachedAnalysisResults = async (analysisId: string): Promise<AnalysisResponse> => {
  // Check cache first
  const cached = analysisCache.get(analysisId);
  if (cached) {
    return cached;
  }

  // Fetch from API
  const response = await fetch(`https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/results/${analysisId}`);
  const data = await response.json();

  // Cache the result
  analysisCache.set(analysisId, data);
  
  return data;
};
```

## 🧪 Testing & Development

### Mock API Responses for Development

```typescript
// mockApi.ts
export const mockApiResponses = {
  submitAnalysis: (): SubmitAnalysisResponse => ({
    status: 'submitted',
    analysis_id: 'mock-analysis-id-123',
    estimated_completion: new Date(Date.now() + 30000).toISOString()
  }),

  getResults: (status: 'processing' | 'completed' | 'failed' = 'completed'): AnalysisResponse => {
    switch (status) {
      case 'processing':
        return {
          status: 'processing',
          message: 'Analysis is currently being processed'
        };
      
      case 'failed':
        return {
          status: 'failed',
          error: 'Mock analysis failed',
          timestamp: new Date().toISOString()
        };
      
      default:
        return {
          status: 'completed',
          results: {
            match_score: 85,
            missing_skills: ['Python', 'AWS', 'Docker'],
            recommendations: [
              'Add quantified achievements (e.g., "Increased efficiency by 25%")',
              'Include relevant keywords from the job description',
              'Highlight specific technical skills and experience'
            ],
            confidence_score: 92,
            analysis_timestamp: new Date().toISOString()
          }
        };
    }
  },

  healthCheck: (): HealthResponse => ({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    checks: {
      dynamodb: { status: 'healthy', message: 'Connected successfully' },
      s3: { status: 'healthy', message: 'Bucket accessible' },
      environment: { status: 'healthy', message: 'All required variables present' }
    }
  })
};

// Development API client
export const createApiClient = (useMock: boolean = false) => {
  if (useMock) {
    return {
      submitAnalysis: async () => {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay
        return mockApiResponses.submitAnalysis();
      },
      
      getResults: async (analysisId: string) => {
        await new Promise(resolve => setTimeout(resolve, 500));
        return mockApiResponses.getResults('completed');
      },
      
      checkHealth: async () => {
        await new Promise(resolve => setTimeout(resolve, 200));
        return mockApiResponses.healthCheck();
      }
    };
  }

  // Real API client
  return {
    submitAnalysis: async (resumeText: string, jobDescription: string) => {
      const response = await fetch('https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_id: crypto.randomUUID(),
          resume_text: resumeText,
          job_description: jobDescription
        })
      });
      return await response.json();
    },
    
    getResults: async (analysisId: string) => {
      const response = await fetch(`https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/results/${analysisId}`);
      return await response.json();
    },
    
    checkHealth: async () => {
      const response = await fetch('https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/health');
      return await response.json();
    }
  };
};
```

### Jest Test Examples

```typescript
// __tests__/useResumeAnalysis.test.ts
import { renderHook, act } from '@testing-library/react';
import { useResumeAnalysis } from '../hooks/useResumeAnalysis';

// Mock fetch
global.fetch = jest.fn();

describe('useResumeAnalysis', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should submit analysis successfully', async () => {
    const mockResponse = {
      status: 'submitted',
      analysis_id: 'test-id',
      estimated_completion: '2025-06-30T10:00:00Z'
    };

    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    const { result } = renderHook(() => useResumeAnalysis());

    await act(async () => {
      await result.current.submitAnalysis('resume text', 'job description');
    });

    expect(result.current.analysisId).toBe('test-id');
    expect(result.current.error).toBeNull();
  });

  it('should handle submission errors', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 400
    });

    const { result } = renderHook(() => useResumeAnalysis());

    await act(async () => {
      await result.current.submitAnalysis('', '');
    });

    expect(result.current.error).toContain('Failed to submit analysis');
    expect(result.current.status).toBe('failed');
  });
});
```

## 🛠️ Environment Configuration

### Environment Variables

```typescript
// config/environment.ts
export const config = {
  apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod',
  isDevelopment: process.env.NODE_ENV === 'development',
  useMockApi: process.env.REACT_APP_USE_MOCK_API === 'true',
  
  // Polling configuration
  polling: {
    maxAttempts: parseInt(process.env.REACT_APP_POLLING_MAX_ATTEMPTS || '30'),
    intervalMs: parseInt(process.env.REACT_APP_POLLING_INTERVAL_MS || '2000')
  },
  
  // Retry configuration
  retry: {
    maxAttempts: parseInt(process.env.REACT_APP_RETRY_MAX_ATTEMPTS || '3'),
    baseDelayMs: parseInt(process.env.REACT_APP_RETRY_BASE_DELAY_MS || '1000')
  }
};
```

### .env.example

```bash
# API Configuration
REACT_APP_API_BASE_URL=https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_USE_MOCK_API=false

# Polling Configuration
REACT_APP_POLLING_MAX_ATTEMPTS=30
REACT_APP_POLLING_INTERVAL_MS=2000

# Retry Configuration
REACT_APP_RETRY_MAX_ATTEMPTS=3
REACT_APP_RETRY_BASE_DELAY_MS=1000
```

## 📱 Mobile Considerations

### React Native Example

```typescript
// For React Native, use the same API calls but with different UI components
import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';

export const ResumeAnalyzerMobile = () => {
  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const { submitAnalysis, isLoading, results, error } = useResumeAnalysis();

  const handleSubmit = async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      Alert.alert('Error', 'Please fill in both resume and job description');
      return;
    }

    try {
      await submitAnalysis(resumeText, jobDescription);
    } catch (err) {
      Alert.alert('Error', 'Failed to submit analysis');
    }
  };

  return (
    <ScrollView style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>
        Resume Analyzer
      </Text>
      
      <TextInput
        multiline
        numberOfLines={6}
        value={resumeText}
        onChangeText={setResumeText}
        placeholder="Paste your resume here..."
        style={{
          borderWidth: 1,
          borderColor: '#ccc',
          padding: 12,
          marginBottom: 16,
          textAlignVertical: 'top'
        }}
      />
      
      <TextInput
        multiline
        numberOfLines={6}
        value={jobDescription}
        onChangeText={setJobDescription}
        placeholder="Paste job description here..."
        style={{
          borderWidth: 1,
          borderColor: '#ccc',
          padding: 12,
          marginBottom: 16,
          textAlignVertical: 'top'
        }}
      />
      
      <TouchableOpacity
        onPress={handleSubmit}
        disabled={isLoading}
        style={{
          backgroundColor: isLoading ? '#ccc' : '#007AFF',
          padding: 16,
          borderRadius: 8,
          alignItems: 'center'
        }}
      >
        <Text style={{ color: 'white', fontSize: 16, fontWeight: 'bold' }}>
          {isLoading ? 'Analyzing...' : 'Analyze Resume'}
        </Text>
      </TouchableOpacity>
      
      {results && (
        <View style={{ marginTop: 20, padding: 16, backgroundColor: '#f5f5f5', borderRadius: 8 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 10 }}>
            Results
          </Text>
          <Text>Match Score: {results.match_score}%</Text>
          <Text>Confidence: {results.confidence_score}%</Text>
          {/* Add more result display components */}
        </View>
      )}
    </ScrollView>
  );
};
```

## 🎯 Best Practices

### 1. Error Handling
- Always handle network errors gracefully
- Provide meaningful error messages to users
- Implement retry logic for transient failures
- Log errors for debugging (but don't expose sensitive data)

### 2. User Experience
- Show loading states during API calls
- Implement progress indicators for long-running operations
- Cache results to avoid unnecessary API calls
- Provide offline fallbacks when possible

### 3. Performance
- Use debouncing for search/input fields
- Implement proper caching strategies
- Minimize API calls with intelligent polling
- Use React.memo and useMemo for expensive operations

### 4. Security
- Never expose API keys in frontend code
- Validate all user inputs before sending to API
- Implement proper CORS handling
- Use HTTPS for all API communications

### 5. Accessibility
- Provide proper ARIA labels for screen readers
- Ensure keyboard navigation works properly
- Use semantic HTML elements
- Provide alternative text for visual elements

## 🔗 Additional Resources

- **API Testing**: Use the test files in `tests/` directory
- **Monitoring**: Check `utilities/monitor_analysis_status.py` for CLI monitoring
- **Documentation**: See individual function docs in `src/*/README.md`
- **Architecture**: Review `design_docs/` for system architecture

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors**
   - The API includes proper CORS headers
   - Ensure you're making requests from allowed origins

2. **404 Errors on Results**
   - Verify the analysis_id is correct
   - Check that the analysis was successfully submitted

3. **Timeout Issues**
   - Increase polling timeout for complex analyses
   - Implement proper retry logic

4. **Network Errors**
   - Check internet connectivity
   - Verify API endpoint URL is correct
   - Implement offline handling

### Debug Steps

1. Check browser network tab for actual HTTP requests/responses
2. Verify API endpoint URLs are correct
3. Test with curl or Postman first
4. Check CloudWatch logs for server-side errors
5. Use the health endpoint to verify system status

---

**Need Help?** Check the comprehensive documentation in each function's README file or test the API using the provided test scripts.
