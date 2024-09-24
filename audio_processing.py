from nltk.tokenize import sent_tokenize
import time
from textblob import TextBlob
from utils import UNEXPECTED_ERROR

def identify_speaker(diarization, time_position):
    try:
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if turn.start <= time_position < turn.end:
                return speaker
        return "Unknown"
    except Exception as e:
        print(UNEXPECTED_ERROR.format(str(e)))
        return "Unknown"

def process_audio(audio_file, diarization_pipeline):
    try:
        diarization = diarization_pipeline(audio_file)
        # Additional audio processing logic can be added here
        return diarization
    except Exception as e:
        print(UNEXPECTED_ERROR.format(str(e)))
        return None

def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except Exception as e:
        print(UNEXPECTED_ERROR.format(str(e)))
        return 0  # Neutral sentiment as fallback