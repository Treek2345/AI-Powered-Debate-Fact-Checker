import streamlit as st
import speech_recognition as sr
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv
import os
import traceback
from web_search import EfficientWebSearch
from fact_checking import fact_check_with_groq, parse_fact_check_result
import plotly.graph_objs as go
import spacy
from pyannote.audio import Pipeline
from utils import GROQ_API_KEY, SPACY_MODEL, sentiment_to_percentage, get_verification_counts
from audio_processing import process_audio, analyze_sentiment, identify_speaker
from context_builder import EnhancedContextBuilder

# Load environment variables
load_dotenv()

# Initialize components
groq_client = AsyncGroq(api_key=GROQ_API_KEY)
r = sr.Recognizer()
web_searcher = EfficientWebSearch()

# Initialize NLP models
nlp = spacy.load(SPACY_MODEL)
auth_token = os.getenv("HUGGINGFACE_TOKEN")
diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=auth_token)

# Initialize context builder
context_builder = EnhancedContextBuilder()

# Streamlit page configuration
st.set_page_config(page_title="AI-Powered Debate Fact-Checker", page_icon="🎙️", layout="wide")
st.title("AI-Powered Debate Fact-Checker")

# Initialize session state variables
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'claims' not in st.session_state:
    st.session_state.claims = []
if 'fact_checks' not in st.session_state:
    st.session_state.fact_checks = []

async def transcribe_audio(audio_file):
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
        text = r.recognize_google(audio_data)
        return text
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return ""

async def extract_claims(text):
    prompt = f"""
    Given the following transcribed text, extract all clear and concise claims that can be fact-checked.
    Each claim should be a single sentence and should be something that can be verified.
    Do not include any additional commentary or notes about the claims.
    Format the output as a simple numbered list, with each claim on a new line.

    Transcribed text:
    {text}
    """
    
    try:
        response = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI assistant that extracts clear, concise, and fact-checkable claims from text."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.1,
            max_tokens=500,
            top_p=1,
        )
        claims = response.choices[0].message.content.split("\n")
        return [claim.strip().lstrip("0123456789. ") for claim in claims if claim.strip()]
    except Exception as e:
        st.error(f"Error extracting claims: {str(e)}")
        return []

async def categorize_claim(claim):
    doc = nlp(claim)
    categories = [ent.label_ for ent in doc.ents]
    return list(set(categories))

async def fact_check_claim(claim, web_results, context):
    categories = await categorize_claim(claim)
    sentiment = analyze_sentiment(claim)
    
    result = await fact_check_with_groq(groq_client, claim, context, web_results, categories, sentiment, None)
    parsed_result = parse_fact_check_result(result)
    
    parsed_result['Categories'] = categories
    parsed_result['Sentiment'] = sentiment
    return parsed_result

async def process_claims(claims, context, audio_file):
    fact_checks = []
    
    try:
        # Process audio for diarization
        diarization_result = process_audio(audio_file, diarization_pipeline)
        
        for i, claim in enumerate(claims):
            st.write(f"Processing claim {i+1}/{len(claims)}: {claim}")
            web_results = await web_searcher.search(claim)
            context = context_builder.get_relevant_context(claim)
            result = await fact_check_claim(claim, web_results, context)
            
            # Assign speaker based on diarization
            speaker = identify_speaker(diarization_result, i * 10)  # Assuming 10 seconds per claim, adjust as needed
            
            context_builder.add_statement(claim, speaker)
            fact_checks.append((claim, result, speaker))
    except Exception as e:
        st.error(f"Error processing claims: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
    return fact_checks

async def main():
    st.header("1. Upload Audio")
    uploaded_file = st.file_uploader("Choose a WAV file", type="wav")

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        if st.button("Transcribe and Analyze"):
            with st.spinner("Transcribing and analyzing..."):
                st.session_state.transcribed_text = await transcribe_audio(uploaded_file)
                st.session_state.claims = await extract_claims(st.session_state.transcribed_text)
                st.session_state.fact_checks = await process_claims(st.session_state.claims, st.session_state.transcribed_text, uploaded_file)
            st.success("Analysis complete!")

    st.header("2. Transcribed Text and Claims")
    st.text_area("Transcribed Text", st.session_state.transcribed_text, height=200)
    st.write("Extracted claims:", st.session_state.claims)

    st.header("3. Fact-Check Results")
    for i, (claim, result, speaker) in enumerate(st.session_state.fact_checks):
        with st.expander(f"Claim {i+1}: {claim}", expanded=True):
            verification = result.get("Verification", "N/A")
            confidence = result.get("Confidence", "N/A")
            explanation = result.get("Explanation", "N/A")
            bias = result.get("Bias", "N/A")
            sources = result.get("Sources", "N/A")
            categories = result.get("Categories", [])
            sentiment = result.get("Sentiment", 0)

            st.write(f"**Speaker:** {speaker}")
            st.write(f"**Verification:** {verification}")
            st.write(f"**Confidence:** {confidence}")
            st.write(f"**Explanation:** {explanation}")
            st.write(f"**Potential Bias:** {bias}")
            st.write(f"**Sources:** {sources}")
            st.write(f"**Categories:** {', '.join(categories)}")
            
            # Truth meter visualization
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = sentiment_to_percentage(sentiment),
                title = {'text': "Truth Meter"},
                gauge = {'axis': {'range': [0, 100]},
                         'bar': {'color': "darkblue"},
                         'steps' : [
                             {'range': [0, 33], 'color': "lightgray"},
                             {'range': [33, 66], 'color': "gray"},
                             {'range': [66, 100], 'color': "darkgray"}],
                         'threshold': {
                             'line': {'color': "red", 'width': 4},
                             'thickness': 0.75,
                             'value': 50}}))
            st.plotly_chart(fig)

    # Overall statistics
    st.header("4. Overall Statistics")
    verified_count, partially_verified_count, not_verified_count = get_verification_counts(st.session_state.fact_checks)
    
    fig = go.Figure(data=[go.Pie(labels=['Verified', 'Partially Verified', 'Not Verified'], 
                                 values=[verified_count, partially_verified_count, not_verified_count])])
    st.plotly_chart(fig)

    # Display current topics
    st.header("5. Current Topics")
    current_topics = context_builder.get_current_topics()
    st.write("Current topics:", ", ".join(current_topics))

if __name__ == "__main__":
    asyncio.run(main())