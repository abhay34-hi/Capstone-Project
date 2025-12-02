AI Smart Chatbot for PGRKAM

This project is an AI-powered employment assistance chatbot designed for the Punjab Ghar Ghar Rozgar and Karobar Mission (PGRKAM). It helps job seekers search jobs, apply online, track applications, and interact with a multilingual chatbot powered by modern AI..

🔥 Features

AI chatbot using Google Gemini API

Zero-shot NLU with mDeBERTa for intent detection

Supports English, Hindi, Punjabi

User Registration & Login

Job search and application submission

Resume upload (PDF/DOCX)

Application tracking dashboard

Voice-to-text input support

SQLite database for storing users & applications

🧩 Tech Stack

Python 3

Streamlit

Gemini API

Transformers (mDeBERTa zero-shot classifier)

SQLite

SpeechRecognition + pydub

📂 Project Structure
app.py               # Main application
chatbot.py           # AI hybrid response engine
nlu_model.py         # Zero-shot intent classifier
db_setup.py          # Creates database tables
db_functions.py      # User login, registration, application storage
file_utils.py        # Resume upload handling
evaluate_bert.py     # Accuracy + confusion matrix testing
pgrkam_portal.db     # SQLite database
uploads/             # Uploaded resumes
screenshots/         # UI images (optional)

⚙️ How to Run
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Create database
python db_setup.py

3️⃣ Add your Gemini API key

In chatbot.py:

GEMINI_API_KEY = "YOUR_API_KEY"

4️⃣ Run the Streamlit app
streamlit run app.py


📜 License

Open for academic and personal use.
