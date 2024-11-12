import time
import joblib
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config("Gemini LLM ChatBot", page_icon="favicon.ico", layout="wide", initial_sidebar_state="auto")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
st.session_state.model = genai.GenerativeModel('gemini-1.5-flash')

new_chat_id = f'{time.time()}'

st.header("Gemini LLM ChatBot")

AI_AVATAR_ICON = '✨'

try:
    os.mkdir('data/')
except:
    pass

try:
    past_chats: dict = joblib.load('data/past_chats_list')
except:
    past_chats = {}

with st.sidebar:
    st.markdown('# Chat History')
    if st.session_state.get('chat_id') is None:
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=[new_chat_id] + list(past_chats.keys()),
            format_func=lambda x: past_chats.get(x, 'New Chat'),
            placeholder='_',
        )
    else:
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=[new_chat_id, st.session_state.chat_id] + list(past_chats.keys()),
            index=1,
            format_func=lambda x: past_chats.get(x, 'New Chat' if x != st.session_state.chat_id else st.session_state.chat_title),
            placeholder='_',
        )

    st.session_state.chat_title = f'ChatSession-{st.session_state.chat_id}'


try:
    st.session_state.messages = joblib.load(
        f'data/{st.session_state.chat_id}-st_messages'
    )
    st.session_state.gemini_history = joblib.load(
        f'data/{st.session_state.chat_id}-gemini_messages'
    )

except:
    st.session_state.messages = []
    st.session_state.gemini_history = []

st.session_state.chat = st.session_state.model.start_chat(
    history=st.session_state.gemini_history,
)

for message in st.session_state.messages:
    if(message["role"] == "user"):
        with st.chat_message(message["role"], avatar="user"):
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"], avatar=AI_AVATAR_ICON):
            st.markdown(message["content"])

if prompt := st.chat_input('Message Gemini'):

    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'data/past_chats_list')

    with st.chat_message('user'):
        st.markdown(prompt)

    st.session_state.messages.append(
        dict(
            role='user',
            content=prompt,
        )
    )

    response = st.session_state.chat.send_message(
        prompt,
        stream=True,
    )

    with st.chat_message(
        name="model",
        avatar=AI_AVATAR_ICON,
    ):
        message_placeholder = st.empty()
        full_response = ''
        assistant_response = response

        for chunk in response:
            for ch in chunk.text.split(' '):
                full_response += ch + ' '
                time.sleep(0.025)
                message_placeholder.write(full_response + '▌')

        message_placeholder.write(full_response)

    st.session_state.messages.append(
        dict(
            role="model",
            content=st.session_state.chat.history[-1].parts[0].text,
            avatar=AI_AVATAR_ICON,
        )
    )
    st.session_state.gemini_history = st.session_state.chat.history

    joblib.dump(
        st.session_state.messages,
        f'data/{st.session_state.chat_id}-st_messages',
    )
    
    joblib.dump(
        st.session_state.gemini_history,
        f'data/{st.session_state.chat_id}-gemini_messages',
    )