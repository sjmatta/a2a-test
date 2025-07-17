# Google A2A Demo - Research & Search Implementation

A demonstration of Application-to-Application (A2A) communication patterns for deep research and search workflows, implemented locally without cloud dependencies.

## Features

- **Secure A2A Authentication**: HMAC-based message signing for service-to-service communication
- **Research Microservices**: Document indexing, knowledge extraction, and research aggregation services
- **Advanced Search Capabilities**: Semantic search, keyword indexing, and citation analysis
- **Knowledge Discovery**: Automated insight extraction, trend analysis, and research gap identification
- **Local Execution**: No cloud dependencies - runs entirely on your local machine

## What is A2A Communication in Research?

Application-to-Application (A2A) communication in research contexts enables automated collaboration between specialized research services:

- **Document Indexing**: Automated ingestion and indexing of research papers
- **Knowledge Extraction**: AI-powered insight extraction from academic content
- **Citation Analysis**: Network analysis of research connections and influence
- **Trend Detection**: Pattern recognition across research domains
- **Report Generation**: Automated synthesis of research findings

## Project Structure

```
google-a2a-demo/
├── main.py           # Entry point for research demo
├── research_demo.py  # Research-focused A2A implementation
├── a2a_demo.py       # Original e-commerce demo (preserved)
├── auth.py           # Authentication utilities (for cloud extensions)
├── pyproject.toml    # UV project configuration
└── README.md         # This file
```

## Usage

1. **Run the research demo**:
   ```bash
   uv run main.py
   ```

2. **Run the original e-commerce demo**:
   ```bash
   uv run python a2a_demo.py
   ```

3. **Run research demo directly**:
   ```bash
   uv run python research_demo.py
   ```

## Research Demo Flow

The demo simulates a comprehensive research workflow:

1. **Research Session Initialization**: Start a focused research session on a specific topic
2. **Deep Document Search**: Perform semantic search across indexed research papers
3. **Knowledge Extraction**: Extract insights, methodologies, and key findings
4. **Trend Analysis**: Identify patterns and trends across multiple documents
5. **Citation Network Analysis**: Map citation relationships and influence patterns
6. **Research Gap Identification**: Discover potential areas for future research
7. **Comprehensive Report Generation**: Synthesize all findings into actionable reports

Each step demonstrates secure A2A communication with authenticated message passing.

## Research Services

### DocumentIndexService
- **Document Ingestion**: Index research papers with metadata
- **Advanced Search**: Keyword, author, and semantic search capabilities
- **Citation Tracking**: Maintain citation graphs and relationships
- **Retrieval**: Fast document lookup and content access

### KnowledgeExtractionService
- **Insight Extraction**: Extract key findings and methodologies
- **Entity Recognition**: Identify research domains, metrics, and approaches
- **Trend Analysis**: Detect emerging patterns across research areas
- **Gap Analysis**: Identify underexplored research directions

### ResearchAggregationService
- **Session Management**: Coordinate multi-step research workflows
- **Result Synthesis**: Combine findings from multiple sources
- **Report Generation**: Create comprehensive research summaries
- **Timeline Analysis**: Track research evolution over time

## Sample Research Data

The demo includes pre-loaded research documents covering:

- **Machine Learning in Climate Science**: Deep learning for weather prediction
- **Quantum Computing & Cryptography**: Post-quantum security implications
- **Neural Networks**: Weather forecasting applications
- **Cryptographic Standards**: Emerging post-quantum algorithms

## Security Features

- **HMAC-SHA256 Message Signing**: Ensure message authenticity
- **Service Identity Verification**: Validate sender credentials
- **Timestamp Tracking**: Prevent replay attacks
- **Research Data Integrity**: Protect academic content from tampering

## Extending for New Research Domains

To add support for new research areas:

1. **Extend Document Schemas**: Add domain-specific metadata fields
2. **Custom Extractors**: Create specialized knowledge extraction patterns
3. **Domain Vocabularies**: Add field-specific terminology and concepts
4. **Analysis Pipelines**: Implement domain-specific analysis workflows

Example:
```python
class BioinformaticsAnalysisService(A2AService):
    def __init__(self, shared_secret: str):
        super().__init__("bioinformatics-analysis", shared_secret)
        self.protein_patterns = {...}
        self.register_handler('analyze_sequences', self.handle_sequence_analysis)
    
    async def handle_sequence_analysis(self, message: A2AMessage):
        # Bioinformatics-specific analysis
        pass
```

## Production Research Platform Considerations

For building a production research platform:

- **Distributed Computing**: Scale analysis across compute clusters
- **Version Control**: Track research data and analysis versions
- **Collaboration Tools**: Multi-researcher session management
- **Data Privacy**: Ensure compliance with research data regulations
- **Integration APIs**: Connect with academic databases and repositories
- **Reproducibility**: Maintain analysis provenance and repeatability

## Dependencies

- Python 3.12+
- No external runtime dependencies for core research functionality
- Google Cloud SDK packages included for potential cloud-based research extensions
- Built-in support for academic metadata formats and citation standards