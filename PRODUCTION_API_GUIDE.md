# Production API Usage Guide

## 📡 Switching from Local to Production

### Local Development
```javascript
const API_URL = "http://localhost:8000"
```

### Production
```javascript
const API_URL = "https://your-eb-url.elasticbeanstalk.com"
```

---

## 🔧 Frontend Configuration

### Option 1: Environment Variables (Recommended)

#### **For Vite/Vue**
Create `.env.production` in your frontend:
```bash
VITE_API_URL=https://pinnacle-sso-production.us-east-1.elasticbeanstalk.com
```

Usage in code:
```javascript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

// Make API calls
const response = await fetch(`${API_URL}/api/v1/public/onboard-client`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
```

#### **For React**
Create `.env.production`:
```bash
REACT_APP_API_URL=https://pinnacle-sso-production.us-east-1.elasticbeanstalk.com
```

Usage in code:
```javascript
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"
```

#### **For Next.js**
Create `.env.production`:
```bash
NEXT_PUBLIC_API_URL=https://pinnacle-sso-production.us-east-1.elasticbeanstalk.com
```

Usage in code:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
```

### Option 2: AWS Amplify Environment Variables

1. Go to: [AWS Amplify Console](https://console.aws.amazon.com/amplify)
2. Select your app
3. Click **Environment variables** (left sidebar)
4. Add new variable:
   - Key: `VITE_API_URL` (or `REACT_APP_API_URL`)
   - Value: `https://your-eb-url.elasticbeanstalk.com`
5. Click **Save**
6. Redeploy your app

---

## 🌐 API Endpoints Reference

### Base URLs
| Environment | Base URL |
|-------------|----------|
| Local | `http://localhost:8000` |
| Production | `https://your-eb-url.elasticbeanstalk.com` |

### Available Endpoints

#### 1. **Health Check**
```bash
GET /health
```

**Local:**
```bash
curl http://localhost:8000/health
```

**Production:**
```bash
curl https://your-eb-url.elasticbeanstalk.com/health
```

---

#### 2. **Onboard Client (Create Proposal)**
```bash
POST /api/v1/public/onboard-client
```

**Local:**
```bash
curl -X POST "http://localhost:8000/api/v1/public/onboard-client" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

**Production:**
```bash
curl -X POST "https://your-eb-url.elasticbeanstalk.com/api/v1/public/onboard-client" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

**JavaScript Example:**
```javascript
const API_URL = import.meta.env.VITE_API_URL

async function onboardClient(payload) {
  const response = await fetch(`${API_URL}/api/v1/public/onboard-client`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

// Usage
const result = await onboardClient({
  client_name: "JOHN",
  client_email: "michael.chen@globaltech.com",
  // ... rest of payload
})
```

---

#### 3. **Get Proposal by Job Number**
```bash
GET /api/v1/proposals/{job_number}
```

**Production:**
```bash
curl "https://your-eb-url.elasticbeanstalk.com/api/v1/proposals/302946"
```

**JavaScript:**
```javascript
async function getProposal(jobNumber) {
  const response = await fetch(`${API_URL}/api/v1/proposals/${jobNumber}`)
  return await response.json()
}
```

---

#### 4. **Ask AI Question (RAG)**
```bash
POST /api/v1/proposals/{proposal_id}/questions/ask-ai
```

**Production:**
```bash
curl -X POST "https://your-eb-url.elasticbeanstalk.com/api/v1/proposals/cd8849f5-c572-48fa-ad37-d10b298056db/questions/ask-ai" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the total cost?",
    "use_rag": true
  }'
```

**JavaScript:**
```javascript
async function askAI(proposalId, question) {
  const response = await fetch(
    `${API_URL}/api/v1/proposals/${proposalId}/questions/ask-ai`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question: question,
        use_rag: true
      })
    }
  )
  return await response.json()
}

// Usage
const answer = await askAI(
  'cd8849f5-c572-48fa-ad37-d10b298056db',
  'What is the total cost?'
)
console.log(answer.answer)
```

---

#### 5. **Submit Question**
```bash
POST /api/v1/proposals/{proposal_id}/questions
```

**Production:**
```bash
curl -X POST "https://your-eb-url.elasticbeanstalk.com/api/v1/proposals/cd8849f5-c572-48fa-ad37-d10b298056db/questions" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Can I get a discount?",
    "asked_by_name": "John Doe",
    "asked_by_email": "john@example.com"
  }'
```

---

## 🔐 Authentication (If Required)

If your endpoints require authentication, add Bearer token:

```javascript
const token = "your-jwt-token"

const response = await fetch(`${API_URL}/api/v1/proposals/302946`, {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
})
```

---

## 🚀 Complete Frontend Integration Example

### Create API Service File

**`src/services/api.js`** (or `api.ts` for TypeScript)

```javascript
// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// API Service Class
class APIService {
  constructor(baseURL = API_URL) {
    this.baseURL = baseURL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error)
      throw error
    }
  }

  // Health check
  async health() {
    return this.request('/health')
  }

  // Onboard client
  async onboardClient(payload) {
    return this.request('/api/v1/public/onboard-client', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  // Get proposal
  async getProposal(jobNumber) {
    return this.request(`/api/v1/proposals/${jobNumber}`)
  }

  // Ask AI
  async askAI(proposalId, question, useRag = true) {
    return this.request(
      `/api/v1/proposals/${proposalId}/questions/ask-ai`,
      {
        method: 'POST',
        body: JSON.stringify({ question, use_rag: useRag }),
      }
    )
  }

  // Submit question
  async submitQuestion(proposalId, questionData) {
    return this.request(`/api/v1/proposals/${proposalId}/questions`, {
      method: 'POST',
      body: JSON.stringify(questionData),
    })
  }

  // Get questions for proposal
  async getQuestions(proposalId) {
    return this.request(`/api/v1/proposals/${proposalId}/questions`)
  }
}

// Export singleton instance
export const api = new APIService()

// For default export
export default api
```

### Usage in Components

**Vue Component Example:**
```vue
<script setup>
import { ref } from 'vue'
import api from '@/services/api'

const proposal = ref(null)
const loading = ref(false)
const error = ref(null)

async function loadProposal(jobNumber) {
  loading.value = true
  error.value = null

  try {
    proposal.value = await api.getProposal(jobNumber)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function askQuestion(question) {
  try {
    const answer = await api.askAI(proposal.value.id, question)
    console.log('AI Answer:', answer.answer)
    return answer
  } catch (err) {
    console.error('Error asking question:', err)
  }
}
</script>

<template>
  <div>
    <button @click="loadProposal('302946')">
      Load Proposal
    </button>

    <div v-if="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="proposal">
      <h1>{{ proposal.client_name }}</h1>
      <p>Job #{{ proposal.job_number }}</p>
      <p>Total: ${{ proposal.total_cost }}</p>
    </div>
  </div>
</template>
```

**React Component Example:**
```jsx
import { useState, useEffect } from 'react'
import api from './services/api'

function ProposalView({ jobNumber }) {
  const [proposal, setProposal] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadProposal() {
      try {
        const data = await api.getProposal(jobNumber)
        setProposal(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadProposal()
  }, [jobNumber])

  async function askQuestion(question) {
    try {
      const answer = await api.askAI(proposal.id, question)
      console.log('AI Answer:', answer.answer)
      return answer
    } catch (err) {
      console.error('Error:', err)
    }
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div className="error">{error}</div>
  if (!proposal) return null

  return (
    <div>
      <h1>{proposal.client_name}</h1>
      <p>Job #{proposal.job_number}</p>
      <p>Total: ${proposal.total_cost}</p>

      <button onClick={() => askQuestion('What is included?')}>
        Ask AI
      </button>
    </div>
  )
}
```

---

## 🌍 CORS Configuration

Your backend is already configured to allow your Amplify frontend:

```python
# In app/config.py
ALLOWED_ORIGINS = "https://main.dnfe4l5bsjojn.amplifyapp.com,https://*.dnfe4l5bsjojn.amplifyapp.com"
```

This means:
✅ `https://main.dnfe4l5bsjojn.amplifyapp.com` can call your API
✅ Any branch deploy (e.g., `dev.dnfe4l5bsjojn.amplifyapp.com`) can call your API
✅ `localhost:3000`, `localhost:8080`, `localhost:5173` for development

---

## 🔧 Testing Production API

### **1. Test from Command Line**

```bash
# Health check
curl https://your-eb-url.elasticbeanstalk.com/health

# Onboard client (save your payload to payload.json)
curl -X POST "https://your-eb-url.elasticbeanstalk.com/api/v1/public/onboard-client" \
  -H "Content-Type: application/json" \
  -d @payload.json \
  | jq .

# Get proposal
curl "https://your-eb-url.elasticbeanstalk.com/api/v1/proposals/302946" | jq .

# Ask AI
curl -X POST "https://your-eb-url.elasticbeanstalk.com/api/v1/proposals/cd8849f5-c572-48fa-ad37-d10b298056db/questions/ask-ai" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total cost?", "use_rag": true}' \
  | jq .
```

### **2. Test from Browser Console**

Visit `https://main.dnfe4l5bsjojn.amplifyapp.com` and open browser console:

```javascript
// Test API connection
const API_URL = 'https://your-eb-url.elasticbeanstalk.com'

// Health check
fetch(`${API_URL}/health`)
  .then(r => r.json())
  .then(console.log)

// Get proposal
fetch(`${API_URL}/api/v1/proposals/302946`)
  .then(r => r.json())
  .then(console.log)

// Ask AI
fetch(`${API_URL}/api/v1/proposals/cd8849f5-c572-48fa-ad37-d10b298056db/questions/ask-ai`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What is included in the audio package?',
    use_rag: true
  })
})
  .then(r => r.json())
  .then(data => console.log(data.answer))
```

---

## 📊 Deployment Checklist

- [ ] Deploy backend to AWS EB: `./deploy_to_aws.sh`
- [ ] Get production URL from deployment output
- [ ] Test health endpoint: `curl https://your-url/health`
- [ ] Test onboard-client endpoint with your payload
- [ ] Update Amplify environment variable: `VITE_API_URL`
- [ ] Redeploy Amplify frontend
- [ ] Test from frontend application
- [ ] Enable HTTPS (if using custom domain)
- [ ] Set up monitoring and alarms

---

## 🐛 Troubleshooting

### CORS Error
```
Access to fetch at 'https://...' from origin 'https://main.dnfe4l5bsjojn.amplifyapp.com' has been blocked by CORS policy
```

**Solution:** Verify ALLOWED_ORIGINS in backend:
```bash
eb printenv | grep ALLOWED_ORIGINS
```

### 502 Bad Gateway
**Solution:** Check backend logs:
```bash
eb logs
```

### Connection Timeout
**Solution:** Verify backend is running:
```bash
eb health
```

### Invalid API Response
**Solution:** Check if using correct URL:
- ❌ `http://your-url` (no http, use https)
- ✅ `https://your-url.elasticbeanstalk.com`

---

## 📚 Next Steps

1. ✅ Deploy backend: `./deploy_to_aws.sh`
2. ✅ Test all endpoints in production
3. ✅ Update Amplify with production API URL
4. ✅ Integrate API service in frontend code
5. ✅ Test RAG functionality from frontend
6. ✅ Set up custom domain (optional)
7. ✅ Enable monitoring and logging

---

**Your URLs:**
- Frontend: `https://main.dnfe4l5bsjojn.amplifyapp.com`
- Backend (after deployment): `https://pinnacle-sso-production.elasticbeanstalk.com`

**Quick Test:**
```bash
curl https://your-eb-url.elasticbeanstalk.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```
