import streamlit as st
from lib.scrape.doaj import ScrapeDoaj
import os
from .ChatBot import chatbot 
def corpus():

    if "sd" not in st.session_state:
        st.session_state.sd = ScrapeDoaj()

    if "num_displayed" not in st.session_state:
        st.session_state.num_displayed = 5  

    if "papers" not in st.session_state:
        st.session_state.papers = []   
 
    

   
    st.header("Поиск релевантных статей")
    query = st.text_input("Найти статьи по теме:") 
    offset = st.slider('Сколько статей искать?', 0, 2000, 100, 50)

    
    def create_card(authors, publication_date, title, uri):
        card = f"""
        **Title:** {title}<br>
        **Authors:** {", ".join([author["name"] for author in authors])} <br>
        **Publication Date:** {publication_date} <br>
        **Link:** [Read More]({uri})
        """
        return card

    
    def display_papers():
        print("Papers to display: ", st.session_state.num_displayed)
        for i in range(st.session_state.num_displayed):
            paper = st.session_state.papers[i]
            st.markdown(create_card(paper["bibjson"]["author"], paper["bibjson"]["year"], paper["bibjson"]["title"], paper["bibjson"]["link"][0]["url"]), unsafe_allow_html=True)

    if st.button("Поиск", disabled=False if query else True) or query:
        st.session_state.num_displayed = 5
        st.session_state.papers = []
        with st.spinner('Исследую интернет...'):
            st.session_state.papers, papers_amount = st.session_state.sd.scrape(query)
        st.success(f'Было найдено {papers_amount} статей.')
        
    if len(st.session_state.papers):
        display_papers()
        def increase_papers():    
            st.session_state["num_displayed"] += 5
        col1, col2 = st.columns(2)
        with col1:
            st.button("Show more", on_click=increase_papers, use_container_width=True)
        with col2:
            scrape_btn = st.button("Chat", type="primary", use_container_width=True)
        if scrape_btn:
            with st.spinner('Загружаю статьи...'):
                st.session_state.sd.scrape(query)
            st.session_state.active_page = "ChatBot"   
            st.experimental_rerun()

    
