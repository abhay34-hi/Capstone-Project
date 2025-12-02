import streamlit as st
import sys

# We import the required third-party libraries inside the try-block 
# to catch 'Module Not Found' errors gracefully without crashing the app.

@st.cache_resource(show_spinner=False)
def load_bert_classifier():
    """
    Loads a zero-shot classification pipeline using a multilingual model (mDeBERTa).
    This simulates the NLU layer's high-accuracy Intent Classification (the BERT function).
    """
    try:
        # Import 'pipeline' from 'transformers' inside the function
        from transformers import pipeline
        
        # Define the possible user intents based on the application's logic
        intent_labels = [
            "greeting", 
            "find_jobs", 
            "check_status", 
            "career_advice" # Maps to 'generic' in the chatbot logic
        ]
        
        # Load the multilingual model
        with st.spinner("⏳ Loading BERT NLU Model... This may take a minute on first run."):
            classifier = pipeline(
                "zero-shot-classification", 
                model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli", # Multilingual model for English/Hindi/Punjabi
                device=-1 # Use -1 for CPU (recommended for prototypes)
            )
        
        st.success("✅ NLU/BERT Model Loaded Successfully (Hybrid Mode Active)")
        return classifier, intent_labels
        
    except ImportError:
        # Catches the case where 'transformers' or 'torch' is not installed
        st.error(
            "❌ **ERROR: NLU Libraries Missing** "
            "The required libraries 'transformers' or 'torch' are not installed. "
            "Please close the app and run the following command in your terminal: "
            "**`pip install transformers torch`**"
        )
        return None, None
        
    except Exception as e:
        # Catches network errors, model file corruption, etc.
        st.error(
            f"❌ **ERROR: Failed to load BERT NLU model** "
            f"A network or file error occurred during model loading. Check your internet connection. Details: {e}"
        )
        return None, None

def classify_intent_with_bert(user_query, classifier, intent_labels):
    """
    Performs Intent Classification.
    """
    if classifier is None:
        return "generic"
        
    try:
        # The model finds the probability of the query matching each label
        result = classifier(user_query, intent_labels, multi_label=False)
        
        # Return the label with the highest score
        predicted_intent = result['labels'][0]
        
        # Map 'career_advice' intent to 'generic' for the existing chatbot logic flow
        if predicted_intent == "career_advice":
            return "generic"
            
        return predicted_intent
    
    except Exception as e:
        print(f"NLU Classification Error: {e}", file=sys.stderr)
        return "generic"
        
# Load the model once when the application starts
BERT_MODEL, BERT_LABELS = load_bert_classifier()