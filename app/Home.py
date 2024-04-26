# home.py

import streamlit as st
from streamlit_option_menu import option_menu
from sites.Corpus import corpus
from sites.Analytics import analytics
import sites.ChatBot as chatbot 

def main():
    st.set_page_config(page_title="Научный куратор :books:")

    if "active_page" not in st.session_state:
        st.session_state.active_page = "Ассистент"

    with st.sidebar:
        st.session_state.active_page = option_menu("GigaResearch", ['Ассистент', 'Статьи'], 
            icons=['archive', 'chat-left-text', 'bar-chart'], menu_icon="infinity", default_index=0)

    
    if st.session_state.active_page == "Ассистент":
        st.session_state.runpage = "Ассистент"
        chatbot.chatbot()  # Вызов функции main из chatbot.py
    elif st.session_state.active_page == "Статьи":
        corpus()

if __name__ == '__main__':
    main()
