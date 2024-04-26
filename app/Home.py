import streamlit as st
from streamlit_option_menu import option_menu
from sites.Corpus import corpus
from sites.ChatBot import chatbot 


st.set_page_config(page_title="Научный куратор :books:")

if "active_page" not in st.session_state:
    st.session_state.active_page = "ChatBot"

 

with st.sidebar:
    st.session_state.active_page = option_menu("GigaResearch", ["Статьи", 'Ассистент'], 
        icons=['archive', 'chat-left-text', 'bar-chart'], menu_icon="books", default_index=0)

        

if st.session_state.active_page == "Статьи":
    corpus()
elif st.session_state.active_page == "Ассистент":
    chatbot()
 
