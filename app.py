import streamlit as st

pages = {
    "Chat": [
        st.Page("chat.py", title="Text Chat", url_path="chat"),
        st.Page("image_chat.py", title="Image Chat", url_path="image_chat"),
        st.Page("pdf_chat.py", title="PDF Chat", url_path="pdf_chat"),
    ]
}

pg = st.navigation(pages)
pg.run()
