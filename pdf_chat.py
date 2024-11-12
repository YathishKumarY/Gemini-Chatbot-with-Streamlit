from dotenv import load_dotenv
from PIL import Image
import os
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import PyPDF2

st.set_page_config(page_title="Pdf Chat", page_icon="🗂️", layout="centered")

# Load environment variables
load_dotenv()   
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")

AI_AVATAR_ICON = '✨'

def convert_messages(messages):
    return [{"role": m["role"], "parts": m["parts"]} for m in messages]

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_txt(uploaded_file):
    return uploaded_file.getvalue().decode("utf-8")

def input_files_setup(uploaded_files):
    """Process and set up the uploaded files for the model."""
    files_parts = []

    for uploaded_file in uploaded_files:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
                
        elif uploaded_file.type == "text/plain":
            text = extract_text_from_txt(uploaded_file)
        
        else:
            text = None
            
        files_parts.append({
            "mime_type": uploaded_file.type,
            "data": text
        })

    return files_parts

# Streamlit UI header
st.header("Gemini Pdf Chat")

# # Allow user to upload multiple files (images or documents)
uploaded_files = st.file_uploader("Choose file", type=["pdf", "txt"], accept_multiple_files=True)

# st.markdown(input_files_setup(uploaded_files))

# If image files are uploaded, display them
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.type.startswith("application/pdf"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                # st.write(page.extract_text())
        elif uploaded_file.type.startswith("text/plain"):
            text = uploaded_file.getvalue().decode("utf-8")
            # st.write(text)

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if(message["role"] == "user"):
        with st.chat_message(message["role"], avatar="user"):
            st.markdown(message["parts"])
    else:
        with st.chat_message(message["role"], avatar=AI_AVATAR_ICON):
            st.markdown(message["parts"])

# Static prompt for the Gemini model
prompt = """
You are an expert in understanding various file types and answering questions related to them.
"""

if input_prompt := st.chat_input("Input your question or prompt"):
    if not uploaded_files:
        st.error("Please upload at least one file")
    else:
        files_data = input_files_setup(uploaded_files)

        combined_data = [{"data": file["data"]} for file in files_data]

        st.write(files_data)
        # st.write(files_data[0]["data"])

        st.session_state.messages.append({"role": "user", "parts": input_prompt})
        with st.chat_message("user"):
            st.markdown(input_prompt)

        with st.chat_message("model", avatar=AI_AVATAR_ICON):
            message_placeholder = st.empty()
            full_response = ""
            converted_messages = convert_messages(st.session_state.messages)

        # Set up file data for all uploaded files

        for chunk in model.generate_content([input_prompt] + [combined_data] + [prompt]).text:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
        
        # Generate the response from the model
        st.session_state.messages.append({"role": "model", "parts": full_response})

        # st.write(st.session_state.messages)
        
