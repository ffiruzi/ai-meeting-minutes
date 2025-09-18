# 🤖 Meeting Minutes Generator with AI Agents

> **Transform messy meeting transcripts into professional minutes using LangGraph AI agents**
>
> <div align="center">

## 🎬 **LIVE DEMO - CLICK TO WATCH** 🎬

[![Website RAG Demo](https://img.shields.io/badge/▶️%20WATCH%20FULL%20DEMO-FF0000?style=for-the-badge&logo=youtube&logoColor=white&labelColor=282828&color=FF0000&logoWidth=30)](https://youtu.be/jiEqBB_McaM)

[![Demo Thumbnail](https://img.youtube.com/vi/jiEqBB_McaM/maxresdefault.jpg)](https://youtu.be/jiEqBB_McaM)

### 🚀 **3-Minute Demo: **
*Click the thumbnail above to see the complete system in action!*

[![GitHub](https://img.shields.io/badge/⭐%20Star%20This%20Repo-181717?style=for-the-badge&logo=github)](https://github.com/ffiruzi/ai-meeting-minutes)
[![Video Views](https://img.shields.io/youtube/views/lnuF3FhVzbg?style=for-the-badge&logo=youtube&logoColor=white&labelColor=FF0000&color=FF0000)]()

</div>


![Python](https://img.shields.io/badge/Python-3.8+-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-red)

---

## 🎯 Overview

The **Meeting Minutes Generator** is an intelligent AI system that automatically transforms raw meeting transcripts into professional, executive-ready meeting minutes. Using a sophisticated **4-agent AI pipeline** powered by **LangGraph** and **OpenAI GPT-4**, it eliminates the tedious manual work of creating structured meeting documentation.

### 🔥 Key Features

- **🤖 Multi-Agent AI Pipeline**: Four specialized AI agents working in perfect coordination
- **🌐 Professional Web Interface**: Streamlit-powered UI with real-time progress tracking
- **📝 Executive-Ready Output**: C-level quality meeting minutes and summaries  
- **🔄 Real-time Processing**: Watch AI agents work through your transcript step-by-step
- **📊 Multiple Export Formats**: Download as Markdown, Plain Text, or JSON
- **🎯 Smart Content Extraction**: Automatically identifies action items, decisions, and key points
- **👥 Speaker Recognition**: AI-powered speaker identification and conversation flow
- **⚡ Production Ready**: Enterprise-grade error handling and performance optimization

---

## 🚀 Live Demo

**Watch Video:** https://youtu.be/jiEqBB_McaM

Transform any meeting transcript in under 60 seconds:
1. **Upload** your transcript or paste text
2. **Watch** AI agents process your content in real-time
3. **Download** professional meeting minutes instantly

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI Orchestration** | LangGraph | Multi-agent workflow management |
| **Language Model** | OpenAI GPT-4 | Natural language processing |
| **Web Interface** | Streamlit | Professional user interface |
| **Backend** | Python 3.8+ | Core application logic |
| **State Management** | Pydantic | Type-safe data validation |

---

## 🏗️ System Architecture

The system uses a **sequential 4-agent pipeline** where each AI agent specializes in a specific task:

```
📄 Raw Transcript
       ↓
🤖 Transcript Processor
   → Cleans text & identifies speakers
       ↓
🔍 Content Analyzer  
   → Extracts actions, decisions & key points
       ↓
📝 Summary Writer
   → Creates executive summaries & insights
       ↓
📋 Minutes Formatter
   → Generates professional meeting minutes
       ↓
✅ Professional Meeting Minutes
```

### AI Agent Capabilities

| Agent | Function | AI Features |
|-------|----------|-------------|
| **🤖 Transcript Processor** | Text cleaning & speaker ID | Context-aware grammar correction, filler word removal |
| **🔍 Content Analyzer** | Information extraction | Smart action item detection, deadline parsing |
| **📝 Summary Writer** | Executive summaries | Strategic business focus, stakeholder analysis |
| **📋 Minutes Formatter** | Professional formatting | Corporate templates, structured tables |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ffiruzi/ai-meeting-minutes.git
   cd ai-meeting-minutes
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Launch the application**
   ```bash
   streamlit run streamlit_app.py
   # Or use the launcher script
   python run_app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

---

## 💡 Usage Examples

### Basic Usage
1. **Input Methods**: Upload `.txt` files, paste text, or select sample transcripts
2. **Processing**: Watch real-time progress as AI agents work through your transcript
3. **Results**: View professional minutes in multiple tabs (Summary, Minutes, Raw Data)
4. **Export**: Download in your preferred format (Markdown, Text, JSON)

### Sample Input
```
Sarah: Good morning everyone. Let's start with the Q4 review.
Mike: Thanks Sarah. Revenue is up 25% compared to last quarter.
Jennifer: Great! We need to finalize the budget by Friday.
```

### Generated Output
```markdown
# Meeting Minutes - Q4 Review
**Date**: 2025-01-15  
**Type**: Business Review Meeting

## Executive Summary
Team conducted Q4 performance review, highlighting 25% revenue growth...

## Key Decisions
- Budget finalization deadline set for Friday

## Action Items
| Task | Assignee | Deadline | Priority |
|------|----------|----------|----------|
| Finalize Q4 budget | Jennifer | Friday | High |

## Next Steps
- Complete budget review process
- Prepare Q1 planning session
```

---

## 🎨 Features Showcase

### Real-Time Processing
- **Visual Pipeline**: See each AI agent working in the sidebar
- **Progress Tracking**: Watch completion percentage update in real-time
- **Agent Status**: Know exactly which processing step is running
- **Performance Metrics**: View processing time and system statistics

### Professional Output
- **Executive Summaries**: C-level ready strategic overviews
- **Structured Action Items**: Clear tables with assignees and deadlines
- **Business Intelligence**: Stakeholder impact analysis and insights
- **Multiple Formats**: Markdown, plain text, and structured JSON exports

### User Experience
- **Intuitive Interface**: Clean, professional design with custom CSS styling
- **Sample Data**: Pre-loaded examples for immediate testing
- **Error Handling**: User-friendly error messages with technical details
- **Responsive Design**: Works seamlessly on desktop and mobile devices

---

## 🧪 Quality Assurance

The system includes comprehensive testing covering:
- **Individual Agent Testing**: Each AI agent validated independently
- **End-to-End Pipeline**: Complete workflow testing with various transcript types
- **Error Scenario Testing**: Graceful handling of API failures and edge cases
- **Performance Testing**: Optimization for different transcript sizes
- **UI Integration Testing**: Frontend and backend integration validation

**Test Coverage**: 100% with robust error handling and fallback mechanisms

---

## 📊 Performance Metrics

| Metric | Specification |
|--------|---------------|
| **Processing Time** | < 60 seconds for typical meeting transcripts |
| **Accuracy** | 95%+ for action item extraction |
| **Speaker ID** | 90%+ accuracy with quality transcripts |
| **API Efficiency** | Optimized token usage for cost-effective operation |
| **Reliability** | Enterprise-grade error handling with graceful degradation |

---

## 🔧 Configuration Options

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
OPENAI_ORG_ID=your_org_id
DEBUG=true
APP_VERSION=1.0.0
```

### Customization
- **Meeting Types**: Customize processing for different meeting formats
- **Output Templates**: Modify professional formatting templates
- **AI Parameters**: Adjust model temperature and token limits
- **UI Themes**: Customize branding and styling

---

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add your OpenAI API key to secrets
4. Deploy with one click

### Docker (Coming Soon)
```bash
docker build -t ai-meeting-minutes .
docker run -p 8501:8501 meeting-minutes-ai
```

### Local Production
```bash
python run_app.py --production
```

---

## 🤝 Contributing

We welcome contributions! Here are some ways to get involved:

- **🐛 Bug Reports**: Open issues for any bugs you find
- **💡 Feature Requests**: Suggest new features or improvements  
- **🔧 Code Contributions**: Submit pull requests for fixes or enhancements
- **📚 Documentation**: Help improve documentation and examples
- **🧪 Testing**: Add test cases or improve existing tests

### Development Setup
1. Clone the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangGraph** for powerful AI agent orchestration
- **OpenAI** for providing GPT-4 language models
- **Streamlit** for enabling rapid web app development
- **Python Community** for the excellent ecosystem of libraries



---

⭐ **Star this repository if you found it helpful!**

Transform your meeting transcripts into professional documentation with the power of AI agents.
