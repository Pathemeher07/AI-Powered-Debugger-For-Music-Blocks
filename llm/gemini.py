import google.generativeai as genai
from google.api_core import retry
import time
import os
from dotenv import load_dotenv

load_dotenv()

api_key = None
try:
    import streamlit as st
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in either Streamlit secrets or environment variables")

genai.configure(api_key=api_key)

CANDIDATE_MODELS = ["models/gemini-3.8-flash", "models/gemini-flash-latest", "models/gemini-2.5-flash", "gemini-1.5-flash"]
MODEL_NAME = "models/gemini-3.8-flash"
MAX_RETRIES = 3
TIMEOUT = 30

@retry.Retry(
    initial=1.0,
    maximum=10.0,
    multiplier=2.0,
    deadline=TIMEOUT,
    predicate=retry.if_exception_type(Exception),
)
def ask_gemini(prompt: str) -> str:
    """Send prompt to Gemini and return the response text."""
    last_err = None
    for model_name in CANDIDATE_MODELS:
        try:
            model = genai.GenerativeModel(model_name)

            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000,
                },
                safety_settings={
                    "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                    "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
                },
            )

            if hasattr(response, "text") and response.text:
                return response.text

            try:
                return response.candidates[0].content.parts[0].text
            except Exception:
                raise ValueError("Gemini response format is unexpected.")

        except Exception as e:
            last_err = e
            # If model is not found, try next candidate model
            err_str = str(e).lower()
            if "not found" in err_str or "no longer available" in err_str:
                continue
            raise e

    if last_err:
        raise last_err
    raise RuntimeError("No suitable Gemini model found.")

def safe_ask_gemini(prompt: str) -> str | None:
    """Wrapper to retry Gemini call up to MAX_RETRIES."""
    for attempt in range(MAX_RETRIES):
        try:
            return ask_gemini(prompt)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                st.error(f"Gemini failed after {MAX_RETRIES} attempts: {e}")
                return None
            time.sleep(1 * (attempt + 1))
            return None
    return None

if __name__ == "__main__":
    st.title("Gemini API Test")
    prompt = st.text_input("Enter prompt", "Explain Music Blocks in 2 lines.")

    if st.button("Ask Gemini"):
        with st.spinner("Thinking..."):
            reply = safe_ask_gemini(prompt)
            if reply:
                st.success("Gemini replied:")
                st.write(reply)
