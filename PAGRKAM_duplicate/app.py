import file_utils
import db_functions # Contains the logic to talk to the SQLite database
import chatbot # This imports the new file you just created
import streamlit as st
from streamlit_option_menu import option_menu
import time
import random
from datetime import datetime
# app.py - PART A: IMPORTS AND FUNCTIONS (PASTE AT THE TOP)

import os
import io
# Import Streamlit if not already done
# import streamlit as st 
from dotenv import load_dotenv
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment 
# Make sure load_dotenv() is called once at the start of your app
# load_dotenv() 


def speech_to_text(audio_bytes):
    """Converts raw audio bytes to text using Google's Speech Recognition API 
    with noise calibration."""
    if not audio_bytes:
        return None
    
    r = sr.Recognizer()
    
    try:
        # Convert raw audio bytes (from audio_recorder_streamlit, typically WAV) 
        # to a standardized WAV format using pydub for reliable processing.
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        
        # Export as WAV bytes
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        
        # Create AudioData object from the standardized WAV stream
        with sr.AudioFile(wav_io) as source:
            
            # *** 1. NOISE CALIBRATION (CRUCIAL FOR NOISY ENVIRONMENTS) ***
            # This listens for 0.5 seconds of "silence" to determine the ambient noise level
            st.info("Calibrating for background noise (be quiet for a second)...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            
            # 2. Record the actual query
            audio = r.listen(source) 

    except Exception as e:
        # The pydub/audio processing failed.
        st.error(f"Error preparing audio data: {e}. Check if PyAudio and pydub were installed correctly.")
        return None

    try:
        # 3. Call the Google Web Speech API
        st.info("Recognizing speech via Google...")
        text = r.recognize_google(audio, language="en-US")
        return text.strip()
    
    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand audio. Try speaking more clearly.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; check internet connection: {e}")
        return None
# --- PAGE CONFIG ---
st.set_page_config(page_title="PGRKAM Official", layout="wide", initial_sidebar_state="collapsed")

# --- SESSION STATE ---\
if "chat_messages" not in st.session_state: st.session_state.chat_messages = []
if 'user_db' not in st.session_state: st.session_state.user_db = {"admin": "admin123"}
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = "Guest"
if 'otp_sent' not in st.session_state: st.session_state.otp_sent = False
if 'real_otp' not in st.session_state: st.session_state.real_otp = None
if 'mobile_verified' not in st.session_state: st.session_state.mobile_verified = False
if 'verified_mobile_num' not in st.session_state: st.session_state.verified_mobile_num = None
if 'applying_job' not in st.session_state: st.session_state.applying_job = None
if 'app_stage' not in st.session_state: st.session_state.app_stage = None
if 'my_applications' not in st.session_state: st.session_state.my_applications = {}
if 'lang' not in st.session_state: st.session_state.lang = 'en'

# =========================================
# 🌐 COMPLETE TRANSLATION DICTIONARY
# =========================================
TR = {
    'en': {
        'nav_h': 'Home', 'nav_s': 'Search Jobs', 'nav_o': 'Overseas', 'nav_sc': 'Schemes', 'nav_l': 'Login', 'nav_a': 'My Account',
        'hero_t': 'PUNJAB ROZGAR', 'hero_s': 'OFFICIAL STATE EMPLOYMENT PORTAL',
        'st_j': 'Active Jobs', 'st_c': 'Companies', 'st_s': 'Seekers', 'st_t': 'Placed Today',
        'exp': '🚀 Explore Services', 'vid': '📺 Tutorial Gallery',
        's_job': '💼 Find Jobs', 's_ovr': '✈️ Overseas', 's_sch': '📜 Schemes', 's_skl': '🎓 Training',
        's_cou': '🗣️ Counselling', 's_arm': '🎖️ Armed Forces', 's_wom': '👩 Women Wing', 's_pwd': '♿ PWD Support',
        'govt_pvt': 'Govt & Private Listings', 'study_work': 'Foreign Study & Work', 'self_emp': 'Self-Employment Loans', 'free_courses': 'Free Skill Courses',
        'btn_brw': 'Browse →', 'btn_vis': 'Visit Wing →', 'btn_vw': 'View Loans →', 'btn_enr': 'Enroll →',
        'btn_book': 'Book →', 'btn_view': 'View →', 'btn_spl': 'Special →', 'btn_exp': 'Explore →',
        'search_t': '🔍 Search Active Jobs', 'kwd': 'Keywords', 'loc': 'Location', 'typ': 'Type', 'btn_srch': 'SEARCH JOBS',
        'job_apply': 'Apply Now', 'login_req': '⚠️ PLEASE LOGIN TO APPLY',
        'req_t': '📋 Mandatory Requirements', 'req_info': 'Please verify requirements.', 'agree': '✅ I confirm that I meet all requirements.',
        'btn_back': '← BACK', 'btn_proc': 'PROCEED →', 'app_t': '📝 Final Application', 'res_up': 'Upload Resume (PDF)', 'sub_app': '✅ SUBMIT APPLICATION',
        'log_head': '🔐 ACCESS PORTAL', 't_log': 'LOGIN', 't_reg': 'REGISTER', 'sec_log': 'SECURE LOGIN',
        'reg_s1': 'Step 1: Verify Mobile', 'reg_s2': 'Step 2: Complete Profile', 'send_otp': 'SEND OTP', 'ver_otp': 'VERIFY',
        'reg_cred': '##### 🔑 Account Credentials', 'reg_user': 'Choose Username *', 'reg_pass': 'Choose Password *', 
        'reg_pers': '##### 📝 Personal Details', 'reg_type': 'User Type *', 'reg_fn': 'First Name *', 'reg_ln': 'Last Name',
        'reg_gen': 'Gender', 'reg_edu': 'Highest Education *', 'reg_dist': 'District *', 'reg_const': 'Constituency', 'reg_em': 'Email *',
        'reg_vmob': 'Verified Mobile', 'reg_int': 'Interested In *', 'reg_terms': 'Agree to Terms *', 'comp_reg': 'COMPLETE REGISTRATION',
        'welcome': 'Welcome', 'track': '📌 Track My Applications', 'no_apps': 'No active applications.', 'logout': 'LOGOUT',
        'os_t': '✈️ Overseas Employment', 'os_s': '🎓 Student Visa', 'os_w': '💼 Work Visa',
        'os_study_sub': 'Student Visa Counselling Form', 'os_work_sub': 'Skilled Worker Visa Assessment',
        'os_n': 'Full Name *', 'os_dob': 'Date of Birth *', 'os_fam_fin': '##### Family & Financial Details',
        'os_fn': "Father's Name *", 'os_mn': "Mother's Name *", 'os_inc': 'Annual Family Income (₹)',
        'os_ln': 'Any existing loans?', 'os_doc_head': '##### Required Documents',
        'os_cert': 'Upload Highest Qualification Certificate *', 'os_pass': 'Upload Passport (Front & Back) *',
        'btn_submit_study': 'SUBMIT STUDY INQUIRY', 'os_job_prof': 'Current Job Profile', 
        'os_exp': 'Years of Experience', 'os_country': 'Preferred Country',
        'os_cv': 'Upload CV / Resume *', 'btn_submit_work': 'SUBMIT WORK PROFILE',
        'sch_t': '📜 Self-Employment Schemes', 'sch_n': 'PMEGP Loan', 'sch_d': '₹50 Lakh Business Loan', 'sch_c': 'Check Eligibility',
        'ft_c': 'CONTACT US', 'ft_l': 'QUICK LINKS', 'ft_leg': 'LEGAL', 'ft_add': 'Govt of Punjab, India', 'ft_em': 'support@pgrkam.com',
        'ft_ab': 'About Us', 'ft_suc': 'Success Stories', 'ft_gri': 'Grievance', 'ft_rti': 'RTI', 'ft_priv': 'Privacy Policy', 'ft_term': 'Terms & Conditions',
        'app_success': '🎉 Application Submitted Successfully!', 'login_success': 'Login Successful!', 'login_fail': 'Invalid Credentials', 'otp_sent_msg': 'OTP Sent:', 'otp_invalid': 'Invalid OTP', 'reg_success': 'Registered! Login now.', 'err_user_pass': 'Choose Username & Password'
    },
    'hi': {
        'nav_h': 'होम', 'nav_s': 'नौकरी खोजें', 'nav_o': 'विदेशी', 'nav_sc': 'योजनाएं', 'nav_l': 'लॉगिन', 'nav_a': 'मेरा खाता',
        'hero_t': 'पंजाब रोज़गार', 'hero_s': 'आधिकारिक राज्य रोज़गार पोर्टल',
        'st_j': 'सक्रिय नौकरियां', 'st_c': 'कंपनियां', 'st_s': 'नौकरी चाहने वाले', 'st_t': 'आज नियुक्त',
        'exp': '🚀 सेवाओं का अन्वेषण करें', 'vid': '📺 ट्यूटोरियल गैलरी',
        's_job': '💼 नौकरी खोजें', 's_ovr': '✈️ विदेशी विंग', 's_sch': '📜 ऋण योजनाएं', 's_skl': '🎓 कौशल प्रशिक्षण',
        's_cou': '🗣️ परामर्श', 's_arm': '🎖️ सशस्त्र बल', 's_wom': '👩 महिला विंग', 's_pwd': '♿ दिव्यांग सहायता',
        'btn_brw': 'ब्राउज़ करें →', 'btn_vis': 'विंग देखें →', 'btn_vw': 'ऋण देखें →', 'btn_enr': 'नामांकन करें →',
        'btn_book': 'बुक करें →', 'btn_view': 'देखें →', 'btn_spl': 'विशेष →', 'btn_exp': 'अन्वेषण करें →',
        'search_t': '🔍 सक्रिय नौकरियां खोजें', 'kwd': 'कीवर्ड', 'loc': 'स्थान', 'typ': 'प्रकार', 'btn_srch': 'खोजें',
        'job_apply': 'आवेदन करें', 'login_req': '⚠️ लॉगिन करें',
        'req_t': '📋 अनिवार्य आवश्यकताएं', 'req_info': 'कृपया आवश्यकताओं की पुष्टि करें।', 'agree': '✅ मैं पुष्टि करता हूँ कि मैं योग्य हूँ।',
        'btn_back': '← वापस', 'btn_proc': 'आगे बढ़ें →', 'app_t': '📝 अंतिम आवेदन', 'res_up': 'बायोडेटा अपलोड करें (PDF)', 'sub_app': '✅ आवेदन जमा करें',
        'log_head': '🔐 पोर्टल एक्सेस', 't_log': 'लॉगिन', 't_reg': 'रजिस्टर', 'sec_log': 'सुरक्षित लॉगिन',
        'reg_s1': 'चरण 1: मोबाइल सत्यापित करें', 'reg_s2': 'चरण 2: प्रोफ़ाइल पूर्ण करें', 'send_otp': 'ओटीपी भेजें', 'ver_otp': 'सत्यापित करें',
        'reg_cred': '##### 🔑 खाता क्रेडेंशियल', 'reg_user': 'उपयोगकर्ता नाम चुनें *', 'reg_pass': 'पासवर्ड चुनें *', 
        'reg_pers': '##### 📝 व्यक्तिगत विवरण', 'reg_type': 'उपयोगकर्ता प्रकार *', 'reg_fn': 'पहला नाम *', 'reg_ln': 'अंतिम नाम',
        'reg_gen': 'लिंग', 'reg_edu': 'उच्चतम शिक्षा *', 'reg_dist': 'ज़िला *', 'reg_const': 'निर्वाचन क्षेत्र', 'reg_em': 'ईमेल *',
        'reg_vmob': 'सत्यापित मोबाइल', 'reg_int': 'रुचि है *', 'reg_terms': 'शर्तों से सहमत *', 'comp_reg': 'पंजीकरण पूरा करें',
        'welcome': 'स्वागत है', 'track': '📌 मेरे आवेदन ट्रैक करें', 'no_apps': 'कोई सक्रिय आवेदन नहीं।', 'logout': 'लॉग आउट',
        'os_t': '✈️ विदेशी रोजगार', 'os_s': '🎓 छात्र वीज़ा', 'os_w': '💼 कार्य वीज़ा',
        'os_study_sub': 'छात्र वीज़ा परामर्श प्रपत्र', 'os_work_sub': 'कुशल श्रमिक वीज़ा आकलन',
        'os_n': 'पूरा नाम *', 'os_dob': 'जन्म तिथि *', 'os_fam_fin': '##### पारिवारिक और वित्तीय विवरण',
        'os_fn': "पिता का नाम *", 'os_mn': "माता का नाम *", 'os_inc': 'वार्षिक पारिवारिक आय (₹)',
        'os_ln': 'कोई मौजूदा ऋण?', 'os_doc_head': '##### आवश्यक दस्तावेज़',
        'os_cert': 'उच्चतम योग्यता प्रमाणपत्र अपलोड करें *', 'os_pass': 'पासपोर्ट (आगे और पीछे) अपलोड करें *',
        'btn_submit_study': 'अध्ययन पूछताछ जमा करें', 'os_job_prof': 'वर्तमान नौकरी प्रोफ़ाइल', 
        'os_exp': 'वर्षों का अनुभव', 'os_country': 'पसंदीदा देश',
        'os_cv': 'सीवी / रिज्यूमे अपलोड करें *', 'btn_submit_work': 'कार्य प्रोफ़ाइल जमा करें',
        'sch_t': '📜 स्वरोजगार योजनाएं', 'sch_n': 'PMEGP ऋण', 'sch_d': '₹50 लाख ऋण', 'sch_c': 'पात्रता की जांच करें',
        'ft_c': 'संपर्क करें', 'ft_l': 'त्वरित लिंक', 'ft_leg': 'कानूनी', 'ft_add': 'पंजाब सरकार, भारत', 'ft_em': 'support@pgrkam.com',
        'ft_ab': 'हमारे बारे में', 'ft_suc': 'सफलता की कहानियां', 'ft_gri': 'शिकायत निवारण', 'ft_rti': 'आरटीआई', 'ft_priv': 'गोपनीयता नीति', 'ft_term': 'नियम और शर्तें',
        'govt_pvt': 'सरकारी और निजी लिस्टिंग', 'study_work': 'विदेशी अध्ययन और कार्य', 'self_emp': 'स्वरोजगार ऋण', 'free_courses': 'निःशुल्क कौशल पाठ्यक्रम',
        'app_success': '🎉 आवेदन सफलतापूर्वक जमा हो गया!', 'login_success': 'लॉगिन सफल!', 'login_fail': 'अमान्य विवरण', 'otp_sent_msg': 'ओटीपी भेजा गया:', 'otp_invalid': 'अमान्य ओटीपी', 'reg_success': 'पंजीकृत! अब लॉगिन करें।', 'err_user_pass': 'कृपया उपयोगकर्ता नाम और पासवर्ड चुनें'
    },
    'pa': {
        'nav_h': 'ਘਰ', 'nav_s': 'ਨੌਕਰੀ ਖੋਜੋ', 'nav_o': 'ਵਿਦੇਸ਼ੀ', 'nav_sc': 'ਸਕੀਮਾਂ', 'nav_l': 'ਲਾਗਇਨ', 'nav_a': 'ਮੇਰਾ ਖਾਤਾ',
        'hero_t': 'ਪੰਜਾਬ ਰੋਜ਼ਗਾਰ', 'hero_s': 'ਅਧਿਕਾਰਤ ਰਾਜ ਰੋਜ਼ਗਾਰ ਪੋਰਟਲ',
        'st_j': 'ਸਰਗਰਮ ਨੌਕਰੀਆਂ', 'st_c': 'ਕੰਪਨੀਆਂ', 'st_s': 'ਉਮੀਦਵਾਰ', 'st_t': 'ਅੱਜ ਨਿਯੁਕਤ',
        'exp': '🚀 ਸੇਵਾਵਾਂ ਦੀ ਪੜਚੋਲ ਕਰੋ', 'vid': '📺 ਟਿਊਟੋਰਿਅਲ ਗੈਲਰੀ',
        's_job': '💼 ਨੌਕਰੀ ਲੱਭੋ', 's_ovr': '✈️ ਵਿਦੇਸ਼ੀ ਵਿੰਗ', 's_sch': '📜 ਲੋਨ ਸਕੀਮਾਂ', 's_skl': '🎓 ਹੁਨਰ ਸਿਖਲਾਈ',
        's_cou': '🗣️ ਸਲਾਹ', 's_arm': '🎖️ ਫੌਜ ਭਰਤੀ', 's_wom': '👩 ਮਹਿਲਾ ਵਿੰਗ', 's_pwd': '♿ ਦਿਵਯਾਂਗ ਸਹਾਇਤਾ',
        'btn_brw': 'ਬ੍ਰਾਊਜ਼ ਕਰੋ →', 'btn_vis': 'ਵੇਖੋ →', 'btn_vw': 'ਵੇਖੋ →', 'btn_enr': 'ਦਾਖਲਾ ਲਓ →',
        'btn_book': 'ਬੁੱਕ ਕਰੋ →', 'btn_view': 'ਵੇਖੋ →', 'btn_spl': 'ਖਾਸ →', 'btn_exp': 'ਪੜਚੋਲ ਕਰੋ →',
        'search_t': '🔍 ਨੌਕਰੀਆਂ ਖੋਜੋ', 'kwd': 'ਕੀਵਰਡ', 'loc': 'ਸਥਾਨ', 'typ': 'ਕਿਸਮ', 'btn_srch': 'ਖੋਜ ਕਰੋ',
        'job_apply': 'ਹੁਣੇ ਅਪਲਾਈ ਕਰੋ', 'login_req': '⚠️ ਕਿਰਪਾ ਕਰਕੇ ਲਾਗਇਨ ਕਰੋ',
        'req_t': '📋 ਜ਼ਰੂਰੀ ਲੋੜਾਂ', 'req_info': 'ਕਿਰਪਾ ਕਰਕੇ ਲੋੜਾਂ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ।', 'agree': '✅ ਮੈਂ ਪੁਸ਼ਟੀ ਕਰਦਾ ਹਾਂ ਕਿ ਮੈਂ ਯੋਗ ਹਾਂ।',
        'btn_back': '← ਵਾਪਸ', 'btn_proc': 'ਅੱਗੇ ਵਧੋ →', 'app_t': '📝 ਅੰਤਿਮ ਅਰਜ਼ੀ', 'res_up': 'ਰੈਜ਼ਿਊਮੇ ਅਪਲੋਡ ਕਰੋ (PDF)', 'sub_app': '✅ ਅਰਜ਼ੀ ਜਮ੍ਹਾਂ ਕਰੋ',
        'log_head': '🔐 ਪੋਰਟਲ ਐਕਸੈਸ', 't_log': 'ਲਾਗਇਨ', 't_reg': 'ਰਜਿਸਟਰ', 'sec_log': 'ਸੁਰੱਖਿਅਤ ਲਾਗਇਨ',
        'reg_s1': 'ਕਦਮ 1: ਮੋਬਾਈਲ ਪੁਸ਼ਟੀ', 'reg_s2': 'ਕਦਮ 2: ਪ੍ਰੋਫਾਈਲ ਪੂਰਾ ਕਰੋ', 'send_otp': 'ਓਟੀਪੀ ਭੇਜੋ', 'ver_otp': 'ਤਸਦੀਕ ਕਰੋ',
        'reg_cred': '##### 🔑 ਖਾਤਾ ਵੇਰਵੇ', 'reg_user': 'ਯੂਜ਼ਰ ਨਾਂ ਚੁਣੋ *', 'reg_pass': 'ਪਾਸਵਰਡ ਚੁਣੋ *', 
        'reg_pers': '##### 📝 ਨਿੱਜੀ ਵੇਰਵੇ', 'reg_type': 'ਯੂਜ਼ਰ ਕਿਸਮ *', 'reg_fn': 'ਪਹਿਲਾ ਨਾਂ *', 'reg_ln': 'ਆਖਰੀ ਨਾਂ',
        'reg_gen': 'ਲਿੰਗ', 'reg_edu': 'ਉੱਚਤਮ ਸਿੱਖਿਆ *', 'reg_dist': 'ਜ਼ਿਲ੍ਹਾ *', 'reg_const': 'ਹਲਕਾ', 'reg_em': 'ਈਮੇਲ *',
        'reg_vmob': 'ਤਸਦੀਕਸ਼ੁਦਾ ਮੋਬਾਈਲ', 'reg_int': 'ਦਿਲਚਸਪੀ *', 'reg_terms': 'ਸ਼ਰਤਾਂ ਮੰਨੋ *', 'comp_reg': 'ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਪੂਰੀ ਕਰੋ',
        'welcome': 'ਜੀ ਆਇਆਂ ਨੂੰ', 'track': '📌 ਮੇਰੀਆਂ ਅਰਜ਼ੀਆਂ', 'no_apps': 'ਕੋਈ ਅਰਜ਼ੀ ਨਹੀਂ।', 'logout': 'ਲਾਗ ਆਉਟ',
        'os_t': '✈️ ਵਿਦੇਸ਼ੀ ਰੋਜ਼ਗਾਰ', 'os_s': '🎓 ਵਿਦਿਆਰਥੀ ਵੀਜ਼ਾ', 'os_w': '💼 ਕੰਮ ਵੀਜ਼ਾ',
        'os_study_sub': 'ਵਿਦਿਆਰਥੀ ਵੀਜ਼ਾ ਕਾਉਂਸਲਿੰਗ ਫਾਰਮ', 'os_work_sub': 'ਕੁਸ਼ਲ ਵਰਕਰ ਵੀਜ਼ਾ ਮੁਲਾਂਕਣ',
        'os_n': 'ਪੂਰਾ ਨਾਮ *', 'os_dob': 'ਜਨਮ ਮਿਤੀ *', 'os_fam_fin': '##### ਪਰਿਵਾਰਕ ਅਤੇ ਵਿੱਤੀ ਵੇਰਵੇ',
        'os_fn': "ਪਿਤਾ ਦਾ ਨਾਮ *", 'os_mn': "ਮਾਤਾ ਦਾ ਨਾਮ *", 'os_inc': 'ਸਾਲਾਨਾ ਪਰਿਵਾਰਕ ਆਮਦਨ (₹)',
        'os_ln': 'ਕੋਈ ਮੌਜੂਦਾ ਕਰਜ਼ਾ?', 'os_doc_head': '##### ਲੋੜੀਂਦੇ ਦਸਤਾਵੇਜ਼',
        'os_cert': 'ਉੱਚਤਮ ਯੋਗਤਾ ਸਰਟੀਫਿਕੇਟ ਅੱਪਲੋਡ ਕਰੋ *', 'os_pass': 'ਪਾਸਪੋਰਟ (ਅੱਗੇ ਅਤੇ ਪਿੱਛੇ) ਅੱਪਲੋਡ ਕਰੋ *',
        'btn_submit_study': 'ਸਟੱਡੀ ਪੁੱਛਗਿੱਛ ਦਰਜ ਕਰੋ', 'os_job_prof': 'ਮੌਜੂਦਾ ਨੌਕਰੀ ਪ੍ਰੋਫਾਈਲ', 
        'os_exp': 'ਸਾਲਾਂ ਦਾ ਤਜਰਬਾ', 'os_country': 'ਪਸੰਦੀਦਾ ਦੇਸ਼',
        'os_cv': 'ਸੀਵੀ / ਰੈਜ਼ਿਊਮੇ ਅੱਪਲੋਡ ਕਰੋ *', 'btn_submit_work': 'ਵਰਕ ਪ੍ਰੋਫਾਈਲ ਜਮ੍ਹਾਂ ਕਰੋ',
        'sch_t': '📜 ਸਵੈ-ਰੋਜ਼ਗਾਰ ਸਕੀਮਾਂ', 'sch_n': 'PMEGP ਲੋਨ', 'sch_d': '₹50 ਲੱਖ ਲੋਨ', 'sch_c': 'ਯੋਗਤਾ ਦੀ ਜਾਂਚ ਕਰੋ',
        'ft_c': 'ਸੰਪਰਕ ਕਰੋ', 'ft_l': 'ਜ਼ਰੂਰੀ ਲਿੰਕ', 'ft_leg': 'ਕਾਨੂੰਨੀ', 'ft_add': 'ਪੰਜਾਬ ਸਰਕਾਰ, ਭਾਰਤ', 'ft_em': 'support@pgrkam.com',
        'ft_ab': 'ਸਾਡੇ ਬਾਰੇ', 'ft_suc': 'ਸਫਲਤਾ ਦੀਆਂ ਕਹਾਣੀਆਂ', 'ft_gri': 'ਸ਼ਿਕਾਇਤ ਨਿਵਾਰਨ', 'ft_rti': 'ਆਰ.ਟੀ.ਆਈ', 'ft_priv': 'ਪਰਾਈਵੇਸੀ ਨੀਤੀ', 'ft_term': 'ਨਿਯਮ ਅਤੇ ਸ਼ਰਤਾਂ',
        'govt_pvt': 'ਸਰਕਾਰੀ ਅਤੇ ਪ੍ਰਾਈਵੇਟ ਸੂਚੀਆਂ', 'study_work': 'ਵਿਦੇਸ਼ੀ ਅਧਿਐਨ ਅਤੇ ਕੰਮ', 'self_emp': 'ਸਵੈ-ਰੋਜ਼ਗਾਰ ਲੋਨ', 'free_courses': 'ਮੁਫਤ ਹੁਨਰ ਕੋਰਸ',
        'app_success': '🎉 ਅਰਜ਼ੀ ਸਫਲਤਾਪੂਰਵਕ ਜਮ੍ਹਾਂ ਹੋ ਗਈ!', 'login_success': 'ਲਾਗਇਨ ਸਫਲ!', 'login_fail': 'ਗਲਤ ਵੇਰਵੇ', 'otp_sent_msg': 'ਓਟੀਪੀ ਭੇਜਿਆ:', 'otp_invalid': 'ਗਲਤ ਓਟੀਪੀ', 'reg_success': 'ਰਜਿਸਟਰ ਹੋ ਗਿਆ! ਹੁਣ ਲਾਗਇਨ ਕਰੋ।', 'err_user_pass': 'ਕਿਰਪਾ ਕਰਕੇ ਯੂਜ਼ਰ ਨਾਂ ਅਤੇ ਪਾਸਵਰਡ ਚੁਣੋ'
    }
}
def T(key): return TR[st.session_state.lang].get(key, key)
# --- DUMMY JOB DATA ---
JOBS_DB = {
    "j1": {"title": "Senior Clerk (Govt)", "dept": "Water Supply", "loc": "Patiala", "sal": "₹35,000", "reqs": ["Graduate", "Punjabi passed", "120hr Computer Course"]},
    "j2": {"title": "School Teacher", "dept": "Education Dept", "loc": "Ludhiana", "sal": "₹42,000", "reqs": ["B.Ed / ETT", "PSTET qualified", "2 years experience"]},
    "j3": {"title": "Ambulance Driver", "dept": "Health Mission", "loc": "Amritsar", "sal": "₹18,500", "reqs": ["Valid HMV License", "5 years driving experience"]},
    "j4": {"title": "Staff Nurse", "dept": "Civil Hospital", "loc": "Jalandhar", "sal": "₹30,000", "reqs": ["B.Sc Nursing / GNM", "Registered Nurse"]}
}

# --- NAVIGATION HELPER ---
def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- LOGOUT HELPER ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = "Guest"
    st.session_state.page = "Home"
    st.rerun()

# --- GLOBAL CSS (UNCHANGED + NEW FOOTER CSS + VIDEO FLOAT RESTORED) ---
st.markdown("""
<style>
    .stApp { background-color: #FAFAFA !important; color: #333333 !important; }
    p, div, span, li, label { color: #333333 !important; }
    h1, h2, h3, h4 { color: #2C3E50 !important; }
    .mega-title { font-size: 80px; font-weight: 900; text-align: center; color: #2C3E50 !important; margin-bottom: 10px; letter-spacing: -2px; }
    .mega-sub { font-size: 24px; text-align: center; color: #666 !important; margin-bottom: 40px; font-weight: 300; }
    .soft-card { background: #FFFFFF; padding: 25px; border-radius: 15px; border: 1px solid #F0F0F0; box-shadow: 0 5px 15px rgba(0,0,0,0.03); text-align: center; transition: all 0.3s ease; height: 100%; }
    .soft-card:hover { border-color: #3498DB; transform: translateY(-5px); }
    .job-listing { background: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #F0F0F0; border-left: 6px solid #2C3E50; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
    div[data-testid="stButton"] > button { background-color: #FFFFFF !important; color: #2C3E50 !important; border: 2px solid #F0F0F0 !important; border-radius: 8px !important; font-weight: 700 !important; }
    div[data-testid="stButton"] > button:hover { border-color: #2C3E50 !important; background-color: #F8F9FA !important; }
    .social-sidebar { position: fixed; left: 20px; top: 50%; transform: translateY(-50%); background: white; padding: 15px 10px; border-radius: 50px; box-shadow: 0 5px 25px rgba(0,0,0,0.05); border: 1px solid #eee; display: flex; flex-direction: column; gap: 15px; z-index: 99; }
    .social-icon { color: #999 !important; font-size: 22px; text-align: center; text-decoration: none; transition: 0.3s; }
    .social-icon:hover { color: #2C3E50 !important; transform: scale(1.2); }
    .stTextInput input, .stSelectbox div, .stDateInput input, .stNumberInput input { background-color: #FFFFFF !important; border: 1px solid #E0E0E0 !important; color: #333 !important; border-radius: 8px; }
    .app-status-card { background: white; padding: 15px 20px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
    .status-badge-pending { background: #FFF3CD; color: #856404; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    .status-badge-review { background: #D1ECF1; color: #0C5460; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }

    /* NEW FOOTER CSS */
    .footer {
        background-color: #2C3E50; color: white !important; padding: 40px 20px; margin-top: 50px; border-top: 5px solid #F39C12;
    }
    .footer h3 { color: #F39C12 !important; margin-bottom: 20px; }
    .footer p, .footer a { color: #ecf0f1 !important; text-decoration: none; }
    .footer a:hover { color: #F39C12 !important; }

    /* MISSING VIDEO FLOAT CSS RESTORED BELOW */
    .video-float {
        position: fixed; bottom: 30px; right: 30px; background-color: #DC3545 !important;
        color: white !important; padding: 12px 25px; border-radius: 50px; font-weight: bold;
        text-decoration: none; z-index: 999; box-shadow: 0 5px 20px rgba(220, 53, 69, 0.4);
    }
</style>
<div class="social-sidebar"><a href="#" class="social-icon">FB</a><a href="#" class="social-icon">IN</a><a href="#" class="social-icon">YT</a></div>
<a href="#video-gallery" class="video-float">📺</a>
""", unsafe_allow_html=True)

# =========================================
# 🌍 TOP BAR: LANGUAGE & LOGIN STATUS
# =========================================
with st.container():
    c1, c2, c3 = st.columns([3, 5, 2])
    
    # --- LANGUAGE SELECTOR (TOP LEFT) ---
    with c1:
        lang_sel = st.radio("Language", ["English", "हिन्दी", "ਪੰਜਾਬੀ"], horizontal=True, label_visibility="collapsed")
        lang_map = {"English": "en", "हिन्दी": "hi", "ਪੰਜਾਬੀ": "pa"}
        if st.session_state.lang != lang_map[lang_sel]:
            st.session_state.lang = lang_map[lang_sel]
            st.rerun()
            
    # --- LOGIN STATUS (TOP RIGHT) ---
    with c3:
        if st.session_state.logged_in:
            c_a, c_b = st.columns([2, 1])
            c_a.markdown(f"<div style='text-align:right; padding-top:8px; font-weight:600; color:#2C3E50;'>👤 {st.session_state.username} //</div>", unsafe_allow_html=True)
            c_b.button(T('logout'), on_click=logout, key="top_logout")

# =========================================
# 🧭 MAIN NAVIGATION (Multilingual & Fixed)
# =========================================
c1, c2, c3 = st.columns([1, 8, 1])
with c2:
    # 1. Define menu options based on login status (Internal English Names)
    if st.session_state.logged_in:
         internal_pages = ["Home", "Search Jobs", "Overseas", "Schemes", "My Account"]
         trans_keys = ['nav_h', 'nav_s', 'nav_o', 'nav_sc', 'nav_a']
    else:
         internal_pages = ["Home", "Search Jobs", "Overseas", "Schemes", "Login"]
         trans_keys = ['nav_h', 'nav_s', 'nav_o', 'nav_sc', 'nav_l']

    # 2. Create the TRANSLATED list of options for the user to see
    menu_labels = [T(key) for key in trans_keys]

    # 3. Safely find the index of the CURRENT page for correct highlighting
    try:
        current_index = internal_pages.index(st.session_state.page)
    except ValueError:
        current_index = 0 # Default to Home if page not found

    # 4. Render the menu
    selected = option_menu(
        menu_title=None,
        options=menu_labels, # Use translated labels
        icons=["house", "search", "airplane", "file-earmark-text", "person-circle"],
        default_index=current_index, # Use the safe index
        orientation="horizontal",
        styles={"container": {"padding": "5px", "background-color": "#fff", "border-radius": "50px", "border": "1px solid #eee"}, "nav-link": {"font-weight": "600", "color": "#555"}, "nav-link-selected": {"background-color": "#2C3E50", "color": "white"}}
    )

    # 5. Map the clicked translated label back to the internal English name
    pmap = dict(zip(menu_labels, internal_pages))
    
    # 6. Check if the user clicked a new page
    if pmap.get(selected) != st.session_state.page:
        st.session_state.page = pmap.get(selected) # Update page to the INTERNAL name
        st.session_state.applying_job = None
        st.session_state.app_stage = None
        st.rerun()
# =========================================
# PAGE 1: HOME (NOW WITH FOOTER & MULTI-LANGUAGE)
# =========================================
if st.session_state.page == "Home":
    st.write(""); st.write("")
    st.markdown(f'<div class="mega-title">{T("hero_t")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mega-sub">{T("hero_s")}</div>', unsafe_allow_html=True)
    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="soft-card"><h2 style="color:#3498DB !important;">22,848</h2><p>{T("st_j")}</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="soft-card"><h2 style="color:#E67E22 !important;">1,412</h2><p>{T("st_c")}</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="soft-card"><h2 style="color:#27AE60 !important;">2.2M+</h2><p>{T("st_s")}</p></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="soft-card"><h2 style="color:#8E44AD !important;">1.2k</h2><p>{T("st_t")}</p></div>', unsafe_allow_html=True)
    
    st.write(""); st.write(""); st.write("")
    st.subheader(T('exp'))
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="soft-card"><h3>{T("s_job")}</h3><p>{T("govt_pvt")}</p></div>', unsafe_allow_html=True)
        if st.button(T('btn_brw'), key="s1", use_container_width=True): navigate_to("Search Jobs")
    with c2:
        st.markdown(f'<div class="soft-card"><h3>{T("s_ovr")}</h3><p>{T("study_work")}</p></div>', unsafe_allow_html=True)
        if st.button(T('btn_vis'), key="s2", use_container_width=True): navigate_to("Overseas")
    with c3:
        st.markdown(f'<div class="soft-card"><h3>{T("s_sch")}</h3><p>{T("self_emp")}</p></div>', unsafe_allow_html=True)
        if st.button(T('btn_vw'), key="s3", use_container_width=True): navigate_to("Schemes")
    with c4:
        st.markdown(f'<div class="soft-card"><h3>{T("s_skl")}</h3><p>{T("free_courses")}</p></div>', unsafe_allow_html=True)
        if st.button(T('btn_enr'), key="s4", use_container_width=True): st.toast("New batches starting soon!")
    
    st.write("")
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown('<div class="soft-card"><h3>🗣️<br>Counselling</h3><p>Expert Career Guidance</p></div>', unsafe_allow_html=True)
        if st.button(T('btn_book'), key="s5", use_container_width=True): st.toast("Booking system loading...")
    with c6:
        st.markdown('<div class="soft-card"><h3>🎖️<br>Armed Forces</h3><p>Police & Army Recruitment</p></div>', unsafe_allow_html=True)
        if st.button(T('btn_view'), key="s6", use_container_width=True): navigate_to("Search Jobs")
    with c7:
        st.markdown('<div class="soft-card"><h3>👩<br>Women</h3><p>Empowerment Wing</p></div>', unsafe_allow_html=True)
        if st.button(T('btn_spl'), key="s7", use_container_width=True): navigate_to("Search Jobs")
    with c8:
        st.markdown('<div class="soft-card"><h3>♿<br>PWD Services</h3><p>Differently Abled Support</p></div>', unsafe_allow_html=True)
        if st.button(T('btn_exp'), key="s8", use_container_width=True): navigate_to("Schemes")
    
    st.write("---")
    st.subheader(T('vid'))
    v1, v2 = st.columns(2)
    with v1: st.video("https://www.youtube.com/watch?v=B2iAodr0fOo")
    with v2: st.video("https://www.youtube.com/watch?v=Da-iH4489wc")

    # --- FOOTER SECTION (TRANSLATED) ---
    st.markdown(f"""
    <div class="footer">
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: left;">
            <div style="flex: 1; min-width: 250px; margin-bottom: 20px;">
                <h3>{T('ft_c')}</h3>
                <p>{T('ft_add')}</p>
                <p>📧 support@pgrkam.com<br>☎️ Helpline: +91-12345-67890</p>
            </div>
            <div style="flex: 1; min-width: 200px; margin-bottom: 20px;">
                <h3>{T('ft_l')}</h3>
                <p><a href="#">{T('ft_ab')}</a></p>
                <p><a href="#">{T('ft_suc')}</a></p>
                <p><a href="#">{T('ft_gri')}</a></p>
                <p><a href="#">{T('ft_rti')}</a></p>
            </div>
            <div style="flex: 1; min-width: 200px; margin-bottom: 20px;">
                <h3>{T('ft_leg')}</h3>
                <p><a href="#">{T('ft_priv')}</a></p>
                <p><a href="#">{T('ft_term')}</a></p>
                <p><a href="#">Disclaimer</a></p>
            </div>
        </div>
        <hr style="border-color: rgba(255,255,255,0.1);">
        <div style="text-align: center; padding-top: 20px; opacity: 0.8; font-size: 14px;">
            © 2025 Punjab Ghar Ghar Rozgar and Karobar Mission. All Rights Reserved.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================
# PAGE 2: SEARCH JOBS (NOW WITH MULTI-LANGUAGE)
# =========================================
elif st.session_state.page == "Search Jobs":

    # STAGE 1: VIEW JOB LISTINGS
    if st.session_state.app_stage is None:
        st.title(T('search_t'))
        with st.container():
            c1, c2 = st.columns([3, 1])
            c1.text_input(T('kwd'), placeholder="Job title...")
            c2.text_input(T('loc'), placeholder="City...")
            st.button(T('btn_srch'), use_container_width=True)
        st.write("")
        
        for j_id, job in JOBS_DB.items():
            color = "#2C3E50"
            if "School" in job['title']: color = "#E67E22"
            if "Driver" in job['title']: color = "#27AE60"
            if "Nurse" in job['title']: color = "#8E44AD"
            st.markdown(f'<div class="job-listing" style="border-left-color: {color};"><h3>📌 {job["title"]}</h3><p><strong>{job["dept"]}</strong> • {job["loc"]} • {job["sal"]}/mo</p></div>', unsafe_allow_html=True)
            
            # This logic remains identical, just the text changes
            if st.button(T('job_apply'), key=f"btn_{j_id}"):
                if st.session_state.logged_in:
                    st.session_state.applying_job = j_id
                    st.session_state.app_stage = "REQ"
                    st.rerun()
                else:
                    st.error(T('login_req')) # Translated
                    time.sleep(1.5); navigate_to("My Account")

    # STAGE 2: VIEW REQUIREMENTS
    elif st.session_state.app_stage == "REQ":
        job_data = JOBS_DB[st.session_state.applying_job]
        st.title(f"{T('req_t')}: {job_data['title']}") # Translated
        st.info(T('req_info')) # Translated
        with st.container():
            st.markdown("### Mandatory Qualifications:") # Kept English as it's data
            for req in job_data['reqs']: st.markdown(f"- {req}")
            st.write("---")
            agree = st.checkbox(T('agree')) # Translated
            
            c1, c2 = st.columns([1, 4])
            with c1:
                if st.button(T('btn_back')): st.session_state.app_stage = None; st.rerun() # Translated
            with c2:
                if st.button(T('btn_proc'), type="primary", disabled=not agree): st.session_state.app_stage = "FORM"; st.rerun() # Translated

    # STAGE 3: FILL APPLICATION FORM
    elif st.session_state.app_stage == "FORM":
        job_data = JOBS_DB[st.session_state.applying_job]
        st.title(T('app_t'))
        st.write(f"Applying for: **{job_data['title']}** at {job_data['loc']}")
        
        with st.form("final_app_form"):
            st.write("##### 1. Personal Details (Auto-filled)")
            c1, c2 = st.columns(2)
            c1.text_input(T('reg_fn'), value=st.session_state.user_data['first_name'] + " " + st.session_state.user_data['last_name'], disabled=True) 
            c2.text_input("Contact Number", value=st.session_state.user_data['mobile_number'], disabled=True)
            st.write("##### 2. Documents")
            
                        # --- FILE UPLOADER WITH VARIABLE ---
            uploaded_file = st.file_uploader(T('res_up'), type=["pdf", "jpg", "png"])
            st.text_area("Cover Letter (Optional)")
            st.write("---")
            
            if st.form_submit_button(T('sub_app'), use_container_width=True, type="primary"):
                
                if uploaded_file is None:
                    st.error("❌ Resume upload is mandatory.")
                else:
                    # --- SAVE FILE AND GET PATH ---
                    file_path = file_utils.save_uploaded_file(uploaded_file, st.session_state.username, job_data['title'])
                    
                    if file_path:
                        # --- SAVE APPLICATION TO DB (WITH FILE PATH) ---
                        user_id = st.session_state.user_data['id']
                        
                        # Note: We must modify db_functions.save_application to accept file_path
                        # For simplicity here, we assume the DB only saves the link, not the file itself.
                        success, message = db_functions.save_application(
                            user_id,
                            job_data['title'],
                            job_data['dept']
                        )
                        
                        if success:
                            st.balloons()
                            st.success(f"✅ Application Submitted! Resume saved to: {file_path}")
                            time.sleep(2)
                            st.session_state.app_stage = None
                            navigate_to("My Account")
                        else:
                            st.error(f"❌ Error submitting application: {message}")
                    else:
                        st.error("❌ Failed to save the file to the server.")
# PAGE 3: OVERSEAS (UNCHANGED)
# =========================================
# =========================================
# PAGE 3: OVERSEAS (TRANSLATED)
# =========================================
elif st.session_state.page == "Overseas":
    st.title(T('os_t'))
    tab_study, tab_work = st.tabs([T('os_s'), T('os_w')])
    
    with tab_study:
        st.subheader(T('os_study_sub'))
        with st.form("study_form"):
            c1, c2 = st.columns(2)
            c1.text_input(T('os_n'))
            c2.date_input(T('os_dob'))
            
            st.write(T('os_fam_fin'))
            c3, c4 = st.columns(2)
            c3.text_input(T('os_fn'))
            c4.text_input(T('os_mn'))
            
            c5, c6 = st.columns(2)
            c5.number_input(T('os_inc'), min_value=0, step=50000)
            c6.radio(T('os_ln'), ["Yes", "No"], horizontal=True)
            
            st.write(T('os_doc_head'))
            st.file_uploader(T('os_cert'), type=['pdf', 'jpg', 'png'])
            st.file_uploader(T('os_pass'), type=['pdf', 'jpg', 'png'])
            st.write("---")
            
            if st.form_submit_button(T('btn_submit_study'), type="primary", use_container_width=True): 
                st.balloons(); st.success("Inquiry Submitted!")

    with tab_work:
        st.subheader(T('os_work_sub'))
        with st.form("work_form"):
            c1, c2 = st.columns(2)
            c1.text_input(T('os_job_prof'))
            c2.number_input(T('os_exp'), min_value=0)
            
            st.selectbox(T('os_country'), ["Canada", "UK", "Australia", "UAE", "Germany"])
            st.file_uploader(T('os_cv'), type="pdf")
            
            if st.form_submit_button(T('btn_submit_work'), use_container_width=True): 
                st.success("Profile submitted for assessment.")
# =========================================
# PAGE 4: SCHEMES (NOW WITH MULTI-LANGUAGE)
# =========================================
elif st.session_state.page == "Schemes":
    st.title(T('sch_t'))
    # We use the translated key for the expander title
    with st.expander(T('sch_n'), expanded=True):
        # We keep "Prime Minister Employment Generation Programme" in English
        # as it is a proper name, but the details are translated.
        st.write("### Prime Minister Employment Generation Programme")
        st.write(T('sch_d'))
        st.button(T('sch_c'))
# =========================================
# PAGE 5: MY ACCOUNT (TRANSLATED)
# =========================================
# This one line handles both "Login" and "My Account" pages
elif st.session_state.page == "My Account" or st.session_state.page == "Login":
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        if st.session_state.logged_in:
             # --- LOGGED IN VIEW ---
             st.markdown(f'<div class="soft-card"><h2 style="color:#2C3E50 !important;">{T("welcome")}, {st.session_state.username}!</h2></div>', unsafe_allow_html=True)
             st.write("")
             
             # --- NEW SECTION: LIVE TRACK MY APPLICATIONS FROM DB ---
             st.subheader(T('track'))
             
             # Fetch applications from the database
             # This uses the db_functions you created in the previous steps
             user_apps = db_functions.get_applications_by_username(st.session_state.username)
             
             if not user_apps:
                 st.info(T('no_apps'))
                 if st.button(T('nav_s')): navigate_to("Search Jobs")
             else:
                 for app in user_apps:
                     # Status mapping: DB default is 'Submitted'
                     status_cls = "status-badge-review" if app['status'] != "Submitted" else "status-badge-pending"
                     
                     st.markdown(f"""
                     <div class="app-status-card">
                        <div>
                           <h4 style="margin:0; color:#2C3E50 !important;">{app['job_title']}</h4>
                           <p style="margin:0; font-size:14px; color:#666 !important;">{app['department']} • Applied: {app['date_applied'].split()[0]}</p>
                        </div>
                        <div><span class="{status_cls}">{app['status']}</span></div>
                     </div>
                     """, unsafe_allow_html=True)
        else:
            # --- LOGGED OUT VIEW ---
            st.markdown(f'<div class="soft-card"><h3>{T("log_head")}</h3></div>', unsafe_allow_html=True)
            st.write("")
            tab1, tab2 = st.tabs([T('t_log'), T('t_reg')])
            
            # --- LOGIN TAB ---
            # --- TAB 1: EXISTING USER LOGIN (Reads from Database) ---
            with tab1:
                login_user = st.text_input(T('login_user'))
                login_pass = st.text_input(T('login_pass'), type="password")
                if st.button(T('sec_log'), use_container_width=True):
                    
                    # --- CALL DATABASE FUNCTION ---
                    success, user_data = db_functions.verify_login(login_user, login_pass)
                    
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = user_data['username'] # Use username from DB
                        st.session_state.user_data = user_data # Save all user data for future use
                        
                        st.success(T('login_success'))
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(T('login_fail'))
            
            # --- REGISTRATION TAB ---
           # --- TAB 2: NEW REGISTRATION (Writes to Database) ---
            with tab2:
                # 1. MOBILE VERIFICATION STAGE
                if not st.session_state.mobile_verified:
                    st.subheader(T('reg_s1'))
                    mobile_input = st.text_input(T('reg_mob'), max_chars=10)
                    if not st.session_state.otp_sent:
                        if st.button(T('send_otp'), use_container_width=True):
                            if len(mobile_input) == 10: 
                                st.session_state.real_otp = random.randint(1000,9999); st.session_state.otp_sent = True; st.rerun()
                            else: st.error("Invalid Mobile")
                    else:
                        st.info(f"{T('otp_sent_msg')} **{st.session_state.real_otp}**")
                        otp = st.text_input(T('ver_otp'), max_chars=4)
                        if st.button(T('verify'), use_container_width=True):
                            if str(otp) == str(st.session_state.real_otp): 
                                st.success("Verified!"); 
                                st.session_state.mobile_verified = True
                                st.session_state.verified_mobile_num = mobile_input
                                st.session_state.otp_sent = False
                                time.sleep(1); st.rerun()
                            else: st.error(T('otp_invalid'))
                
                # 2. COMPLETE PROFILE STAGE (After verification)
                else:
                    st.subheader(T('reg_s2'))
                    with st.form("reg_full"):
                        st.write(T('reg_cred'))
                        new_u = st.text_input(T('reg_user')); new_p = st.text_input(T('reg_pass'), type="password")
                        st.write("---")
                        st.write(T('reg_pers'))
                        
                        # --- CAPTURE ALL DETAILED FIELDS ---
                        user_type = st.selectbox(T('reg_type'), ["Jobseeker", "Scheme Loans", "Abroad Counseling"])
                        c_a, c_b = st.columns(2); 
                        fname = c_a.text_input(T('reg_fn')); lname = c_b.text_input(T('reg_ln'))
                        gender = st.radio(T('reg_gen'), ["Male", "Female", "Other"], horizontal=True)
                        education = st.selectbox(T('reg_edu'), ["10th", "12th", "Graduate", "Post Graduate", "ITI", "Diploma"])
                        c_c, c_d = st.columns(2); 
                        district = c_c.selectbox(T('reg_dist'), ["Amritsar", "Ludhiana", "Mohali"])
                        constituency = c_d.selectbox(T('reg_const'), ["Const 1", "Const 2"])
                        email = st.text_input(T('reg_em'))
                        interested = st.selectbox(T('reg_int'), ["Private Jobs", "Govt Jobs", "Self Employment"])
                        
                        # Locked Mobile Field
                        st.text_input(T('reg_vmob'), value=st.session_state.verified_mobile_num, disabled=True)
                        
                        terms_agree = st.checkbox(T('reg_terms'))
                        
                        if st.form_submit_button(T('comp_reg'), use_container_width=True):
                            if not terms_agree:
                                st.error("❌ You must agree to the terms.")
                            elif new_u and new_p and fname and education and district:
                                
                                # Package data for DB function
                                reg_data = {
                                    'username': new_u,
                                    'password': new_p,
                                    'mobile': st.session_state.verified_mobile_num,
                                    'email': email,
                                    'user_type': user_type,
                                    'first_name': fname,
                                    'last_name': lname,
                                    'gender': gender,
                                    'education': education,
                                    'district': district
                                }
                                
                                # --- CALL DATABASE FUNCTION ---
                                success, message = db_functions.add_user(reg_data)

                                if success:
                                    st.balloons()
                                    st.success(T('reg_success'))
                                    # Reset state
                                    st.session_state.mobile_verified = False
                                    st.session_state.page = "Login"
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                            else: st.error("Please fill in all mandatory fields.")

# ==========================================================
# 2. CHATBOT UI AND INPUT LOGIC (Place where you want the chat widget to appear)
#    - REQUIRES: T(), st.session_state, chatbot, db_function, and JOBS_DB to be defined elsewhere.
#    - REQUIRES: The speech_to_text function to be defined at the top of app.py.
# ==========================================================

st.markdown("""
<style>
    /* We are using the "video-float" style you already have,
      but changing its color and position to be a chat button.
    */
    .chat-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background-color: #0d6efd !important; /* Blue color */
        color: white !important;
        padding: 15px 15px;
        border-radius: 50%; /* Make it round */
        font-size: 24px;
        font-weight: bold;
        text-decoration: none;
        z-index: 999;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    }
</style>
<a href="#chat-popup-anchor" class="chat-button">💬</a>
<div id="chat-popup-anchor"></div>
""", unsafe_allow_html=True)

# This creates the "popup" chat window
with st.expander(f"🤖 {T('s_cou')}", expanded=True): 
    # ... (Rest of your code remains here) ...
    
    # 1. Display chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # --- VOICE AND TEXT INPUT HANDLING ---

    # A. Voice Input Recorder Component
    st.markdown("---") # Visual separator
    audio_bytes = audio_recorder(
        text="🎙️ **voice**",
        # Changed recording_color to a medium grey for visibility on a light background
        recording_color="#A9A9A9", 
        icon_size="1.5x",
        key="voice_input_chat" # Unique key for Streamlit
    )

    voice_prompt = None
    if audio_bytes:
        # Transcribe the audio
        with st.spinner("Processing Audio..."):
            # This calls the noise-calibrated function defined at the top of app.py
            voice_prompt = speech_to_text(audio_bytes) 
        
        if voice_prompt:
            # Display the transcribed text to the user
            st.info(f"🎤 **You said:** {voice_prompt}")
            
    # B. Text Input Component
    text_prompt = st.chat_input("...or type your question here", key="text_input_chat")

    # C. Determine the final query (Voice takes precedence)
    query = voice_prompt if voice_prompt else text_prompt

    if query:
        # D. Add user message to history and display it
        st.session_state.chat_messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        # E. Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                
                # Get user's application history for context (from your original logic)
                user_apps = st.session_state.my_applications.get(st.session_state.username, [])
                
                # Call the "hybrid brain" from chatbot.py
                response = chatbot.get_hybrid_response(
                    user_query=query, 
                    user_name=st.session_state.username,
                    lang=st.session_state.lang,
                    app_history=user_apps,
                    job_list=JOBS_DB # Your global job list variable
                )
                st.markdown(response)
        
        # F. Add AI response to history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})