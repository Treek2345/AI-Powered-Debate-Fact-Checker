# AI-Powered-Debate-Fact-Checker
AI-Powered Debate Fact-Checker powered by groq + llama 3.1 70b

# AI-Powered Debate Fact-Checker

![Debate Fact-Checker Logo](https://via.placeholder.com/150?text=Debate+Fact-Checker)

## 🎙️ Real-time fact-checking for live debates

The AI-Powered Debate Fact-Checker is a cutting-edge tool designed to enhance the quality and accuracy of public discourse. By leveraging advanced AI and NLP technologies, this application provides real-time fact-checking, sentiment analysis, and topic tracking for live debates.

### 🌟 Key Features

- **Real-time Audio Processing**: Transcribe live debate audio and identify speakers.
- **Automated Claim Extraction**: Identify and isolate fact-checkable claims from transcribed text.
- **AI-Powered Fact-Checking**: Utilize the Groq API for rapid, intelligent fact verification.
- **Interactive Visualizations**: 
  - Timeline of claims and their verification status
  - Network graph of speakers and topics
  - Truth meter for sentiment analysis
- **Efficient Web Search**: Gather relevant information to support fact-checking with caching and rate limiting.
- **Context-Aware Analysis**: Maintain debate context for more accurate fact-checking and topic tracking.
- **Summary Generation**: Produce concise summaries of debate key points and verification results.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Groq API key
- Hugging Face API token (for speaker diarization)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-debate-fact-checker.git
   cd ai-debate-fact-checker
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   HUGGINGFACE_TOKEN=your_huggingface_token_here
   ```

### Usage

Run the Streamlit app:
```
streamlit run main.py
```

Navigate to the provided local URL in your web browser to access the application.

## 📊 How It Works

1. **Audio Upload**: Users upload a debate audio file (WAV format).
2. **Transcription**: The audio is transcribed and processed for speaker diarization.
3. **Claim Extraction**: AI identifies fact-checkable claims from the transcribed text.
4. **Fact-Checking**: Each claim is verified using web searches and AI analysis.
5. **Visualization**: Results are displayed with interactive charts and graphs.
6. **Summary**: A concise summary of the debate and fact-checking results is generated.

## 🛠️ Technologies Used

- Streamlit: Web application framework
- Groq API: AI-powered text generation and analysis
- spaCy: Natural Language Processing
- pyannote.audio: Speaker diarization
- Plotly: Interactive visualizations
- NetworkX: Graph creation for topic/speaker relationships
- Beautiful Soup: Web scraping for fact-checking
- aiohttp: Asynchronous HTTP requests

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Groq for the Groq API
- The open-source & hugging face community for the amazing tools and libraries used in this project

---

Built with ❤️ by [Elena J. Greer]
