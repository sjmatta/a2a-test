# Distributed A2A Research Platform

A comprehensive demonstration of **true Application-to-Application (A2A)** communication using distributed microservices for intelligent research and web search workflows. Each service runs as a separate HTTP server with secure inter-service authentication.

## 🚀 Quick Start

```bash
# Start all distributed services
make start

# Run interactive research session
uv run python distributed_main.py

# Or search directly from command line
uv run python distributed_main.py "artificial intelligence advances 2024"
```

## 🎯 System Architecture

This platform demonstrates **true distributed A2A** with separate HTTP servers, not simulated A2A in a single process.

```
┌─────────────────────────────────────────────────────────────────┐
│                    A2A Research Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Client    │◄──►│  Registry   │◄──►│   Services  │         │
│  │ (Rich UI)   │    │   :8000     │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────────────────────────────────────────────────────┤
│  │              Distributed Service Mesh                      │
│  │                                                             │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  │   Search    │  │ Knowledge   │  │ Aggregation │        │
│  │  │ Server      │  │ Server      │  │   Server    │        │
│  │  │   :8001     │  │   :8002     │  │    :8003    │        │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │
│  │         │                │                │               │
│  │         ▼                ▼                ▼               │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  │ DuckDuckGo  │  │ LM Studio   │  │ LM Studio   │        │
│  │  │ Web Search  │  │ (Analysis)  │  │ (Reports)   │        │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │
│  └─────────────────────────────────────────────────────────────┤
└─────────────────────────────────────────────────────────────────┘
```

## 🤖 Intelligent Agent Services

### 🔍 Web Search Agent
**Port: 8001** | **Endpoint: `/search`**

```
┌─────────────────────────────────────────────────────────┐
│                   🔍 Web Search Agent                   │
├─────────────────────────────────────────────────────────┤
│ Capabilities:                                           │
│ • Real-time DuckDuckGo web search                      │
│ • LLM-powered follow-up query generation               │
│ • Multi-round comprehensive research                   │
│ • Web content extraction and parsing                   │
│ • Intelligent query expansion                          │
│                                                         │
│ Technology Stack:                                       │
│ • DuckDuckGo Search API                                │
│ • BeautifulSoup web scraping                           │
│ • FastAPI HTTP server                                  │
│ • LM Studio for query enhancement                      │
│                                                         │
│ Input: SearchRequest                                    │
│ Output: Structured search results with relevance       │
└─────────────────────────────────────────────────────────┘
```

**Communication Pattern:**
```
Client ──► Search Agent ──► DuckDuckGo ──► Web Scraping
   ▲           │                              │
   │           ▼                              │
   └─── LM Studio ◄─── Query Enhancement ◄───┘
```

### 🧠 Knowledge Extraction Agent
**Port: 8002** | **Endpoint: `/extract`**

```
┌─────────────────────────────────────────────────────────┐
│                🧠 Knowledge Extraction Agent            │
├─────────────────────────────────────────────────────────┤
│ Capabilities:                                           │
│ • Deep LLM-powered content analysis                    │
│ • Multi-category insight extraction                    │
│ • Source credibility assessment                        │
│ • Entity recognition and classification                │
│ • Confidence scoring for insights                      │
│                                                         │
│ Insight Categories:                                     │
│ • Overview, Methodology, Domain                        │
│ • Findings, Institutions, Significance                 │
│ • Context, Timeline, Relationships                     │
│                                                         │
│ Technology Stack:                                       │
│ • Local LM Studio (Mistral/Gemma/Llama models)        │
│ • Comprehensive prompt engineering                      │
│ • JSON-structured analysis output                      │
│                                                         │
│ Input: Search results                                   │
│ Output: 15-25 categorized insights per source          │
└─────────────────────────────────────────────────────────┘
```

**Communication Pattern:**
```
Search Results ──► Knowledge Agent ──► LM Studio
      │                  │                │
      │                  ▼                ▼
      └─── Credibility ◄─── Analysis ◄─── AI Model
```

### 📊 Research Aggregation Agent
**Port: 8003** | **Endpoint: `/report`**

```
┌─────────────────────────────────────────────────────────┐
│              📊 Research Aggregation Agent              │
├─────────────────────────────────────────────────────────┤
│ Capabilities:                                           │
│ • Research session management                           │
│ • Multi-source data synthesis                          │
│ • Comprehensive report generation                      │
│ • LLM-powered executive summaries                      │
│ • Statistical analysis and metrics                     │
│                                                         │
│ Report Sections:                                        │
│ • Executive Summary                                     │
│ • Key Findings & Detailed Analysis                     │
│ • Significance Assessment                               │
│ • Research Gaps & Recommendations                      │
│ • Methodology Notes & Conclusion                       │
│                                                         │
│ Technology Stack:                                       │
│ • Session-based workflow management                     │
│ • LM Studio for comprehensive reporting                │
│ • Source quality assessment                            │
│ • Rich statistical analysis                            │
│                                                         │
│ Input: Aggregated research data                         │
│ Output: Academic-quality research reports              │
└─────────────────────────────────────────────────────────┘
```

**Communication Pattern:**
```
Research Data ──► Aggregation Agent ──► LM Studio
      │               │                    │
      ▼               ▼                    ▼
Session Storage ── Report Builder ── AI Analysis
```

### 🌐 Service Registry
**Port: 8000** | **Endpoint: `/services`**

```
┌─────────────────────────────────────────────────────────┐
│                🌐 Service Registry                      │
├─────────────────────────────────────────────────────────┤
│ Capabilities:                                           │
│ • Automatic service discovery                           │
│ • Health monitoring and status tracking                │
│ • Load balancing and failover                          │
│ • Service metadata management                          │
│                                                         │
│ Features:                                               │
│ • Real-time health checks                              │
│ • Service registration/deregistration                  │
│ • Client service discovery                             │
│ • Fault tolerance                                      │
└─────────────────────────────────────────────────────────┘
```

## 🔄 A2A Communication Flow

### Research Query Processing
```
1. Client Request
   │
   ▼
2. Service Discovery ──► Registry (:8000)
   │
   ▼
3. Web Search ──► Search Agent (:8001) ──► DuckDuckGo + LLM
   │
   ▼
4. Knowledge Extraction ──► Knowledge Agent (:8002) ──► LM Studio
   │
   ▼
5. Research Aggregation ──► Aggregation Agent (:8003) ──► LM Studio
   │
   ▼
6. Comprehensive Report ──► Rich UI Display
```

### Multi-Round Research Process
```
Initial Query ──► Primary Search ──► Follow-up Queries
      │               │                     │
      ▼               ▼                     ▼
   LLM Analysis ── Web Scraping ── Content Extraction
      │               │                     │
      ▼               ▼                     ▼
   Insights ──── Credibility ──── Comprehensive Report
```

## 🔐 Security Architecture

### HMAC-Based Authentication
```
Service A ──► Create Signature ──► HTTP Request ──► Service B
   │              │                     │              │
   │              ▼                     ▼              ▼
Shared Key ── HMAC-SHA256 ─── Headers ─── Verify ── Process
```

**Authentication Headers:**
- `X-Service-Name`: Requesting service identifier
- `X-Timestamp`: Request timestamp (prevents replay attacks)
- `X-Signature`: HMAC-SHA256 signature

### Security Features
- ✅ Service-to-service authentication
- ✅ Request timestamp validation (5-minute window)
- ✅ Replay attack prevention
- ✅ Message integrity verification
- ✅ No real secrets in repository (demo values only)

## 🚀 Getting Started

### Prerequisites
- **Python 3.12+** with UV package manager
- **LM Studio** running locally with an LLM model (Mistral, Gemma, Llama, etc.)
- **Make** for easy service management

### Installation
```bash
# Clone repository
git clone git@github.com:sjmatta/a2a-test.git
cd a2a-test

# Install dependencies
uv sync
```

### Running the Platform
```bash
# Start all services (registry + 3 agents)
make start

# Run interactive research session
uv run python distributed_main.py

# Command-line search
uv run python distributed_main.py "quantum computing breakthroughs"

# Stop all services
make stop
```

### Service Management
```bash
# Start individual services
make start-registry    # Service registry (:8000)
make start-search      # Search agent (:8001)  
make start-knowledge   # Knowledge agent (:8002)
make start-aggregation # Aggregation agent (:8003)

# Check service status
make status

# View service logs
make logs
```

## 🔬 Research Capabilities

### Comprehensive Multi-Round Search
- **Primary Query**: Initial web search with DuckDuckGo
- **Follow-up Queries**: LLM-generated related searches
- **Content Extraction**: Full web page content analysis
- **Deduplication**: Smart removal of duplicate sources

### Advanced Knowledge Extraction
- **10 Insight Categories**: Overview, methodology, findings, etc.
- **15-25 Insights per Source**: Comprehensive analysis
- **Confidence Scoring**: AI-powered relevance assessment
- **Source Credibility**: Academic vs. commercial source analysis

### Academic-Quality Reports
- **Executive Summary**: 2-3 paragraph overview
- **Detailed Analysis**: 4-5 paragraph deep dive
- **Key Findings**: Structured bullet points
- **Research Gaps**: Areas for future investigation
- **Recommendations**: Actionable next steps

## 🛠 Technical Implementation

### Distributed Architecture
```python
# Each service runs independently
FastAPI Server (:8001) ← Search Agent
FastAPI Server (:8002) ← Knowledge Agent  
FastAPI Server (:8003) ← Aggregation Agent
FastAPI Server (:8000) ← Service Registry
```

### LLM Integration
- **Local LM Studio**: No cloud dependencies
- **Model Flexibility**: Supports Mistral, Gemma, Llama, Phi, DeepSeek
- **Prompt Engineering**: Optimized for research tasks
- **JSON Output**: Structured AI responses

### Rich Terminal UI
- **Interactive Mode**: Menu-driven research sessions
- **Progress Indicators**: Real-time operation status
- **Colored Output**: Categorized information display
- **Tables & Panels**: Professional report formatting

## 📁 Project Structure

```
a2a-research-platform/
├── Makefile                    # Service management commands
├── pyproject.toml             # UV project configuration
├── distributed_main.py        # Main client interface
├── scripts/                   # Service management scripts
│   ├── start_services.sh      
│   ├── stop_services.sh       
│   └── register_services.sh   
└── src/a2a_research/
    ├── distributed_client.py  # Main client orchestrator
    ├── models.py              # Data models
    └── servers/               # Distributed service implementations
        ├── registry.py        # Service discovery
        ├── search_server.py   # Web search agent
        ├── knowledge_server.py # Knowledge extraction agent
        ├── aggregation_server.py # Research aggregation agent
        └── auth.py            # Security & authentication
```

## 🌟 Key Features

- ✅ **True Distributed A2A**: Separate HTTP servers, not simulated
- ✅ **Real Web Search**: Live DuckDuckGo integration
- ✅ **Local LLM Processing**: No cloud dependencies
- ✅ **Comprehensive Research**: Multi-round intelligent search
- ✅ **Rich Terminal UI**: Professional research interface
- ✅ **Secure Communication**: HMAC-based service authentication
- ✅ **Service Discovery**: Automatic agent registration and health monitoring
- ✅ **Academic Quality**: Research-grade reports and analysis

## 🔮 Future Enhancements

### Advanced Research Features
- **Citation Analysis**: Academic paper citation networks
- **Multi-language Support**: International research sources
- **Data Visualization**: Charts and graphs in reports
- **Research Collaboration**: Multi-user sessions

### Technical Improvements
- **Container Deployment**: Docker/Kubernetes support
- **Monitoring**: Metrics and observability
- **Caching**: Intelligent result caching
- **Scaling**: Horizontal service scaling

### Integration Capabilities
- **Academic Databases**: PubMed, arXiv, Google Scholar
- **Reference Management**: Zotero, Mendeley integration
- **Export Formats**: LaTeX, Word, PDF generation
- **API Gateway**: External system integration

---

**Built with ❤️ using Python, FastAPI, LM Studio, and UV package manager**

*This platform demonstrates production-ready A2A communication patterns for intelligent research workflows.*