import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DIARIZATION_MODEL = "pyannote/speaker-diarization"
SPACY_MODEL = "en_core_web_sm"
LLM_MODEL = "llama-3.1-70b-versatile"

# Utility functions
def format_web_results(web_results):
    """Format web search results for display"""
    return "\n".join([f"- {result['title']}: {result['snippet']}" for result in web_results])

def sentiment_to_percentage(sentiment):
    """Convert sentiment score to percentage for visualization"""
    return (sentiment + 1) / 2 * 100

def get_verification_counts(fact_checks):
    """Count the number of each verification type"""
    verified_count = sum(1 for _, result, _ in fact_checks if result.get("Verification") == "VERIFIED")
    partially_verified_count = sum(1 for _, result, _ in fact_checks if result.get("Verification") == "PARTIALLY VERIFIED")
    not_verified_count = sum(1 for _, result, _ in fact_checks if result.get("Verification") == "NOT VERIFIED")
    return verified_count, partially_verified_count, not_verified_count

# Error messages
TRANSCRIPTION_ERROR = "Error transcribing audio: {}"
CLAIM_EXTRACTION_ERROR = "Error extracting claims: {}"
FACT_CHECKING_ERROR = "Error during fact-checking: {}"
JSON_PARSING_ERROR = "An error occurred while parsing the fact-check result: {}"
UNEXPECTED_ERROR = "An unexpected error occurred: {}"