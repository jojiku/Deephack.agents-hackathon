# chatbot.py

import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from sites.htmlTemplates import css, bot_template, user_template 
from langchain_community.embeddings.gigachat import GigaChatEmbeddings 
from langchain.chat_models.gigachat import GigaChat
import re
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder

auth = "OWYzYzU1MzEtNGZhZi00ZDQxLWI2ODMtM2QxY2EyYTY5ZWEzOjhmOGNjMTAwLWUwOGUtNDgzZC1iZWFhLTcyMGE5YjY2YzAwZg=="

def chatbot():
    load_dotenv() 

    st.write(css, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = MessagesPlaceholder(variable_name="chat_history")
    if "conversation" not in st.session_state:
        st.session_state.conversation = ConversationalRetrievalChain.llm_chain()


    with st.sidebar:
        st.subheader("Загруженные статьи")
        pdf_docs = st.file_uploader(
            "Загрузите PDF статей и нажмите 'Обработать'", accept_multiple_files=True)
        if st.button("Обработать"):
            with st.spinner("Processing"):
             
                raw_text = get_pdf_text(pdf_docs)

              
                text_chunks = get_text_chunks(raw_text)

              
                vectorstore = get_vectorstore(text_chunks)

               
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)
    st.header("Научный куратор :books:")
    user_question = st.chat_input("Отвечу на любые возникшие вопросы по научным статьям:", key="user_input")
    if user_question:
            handle_userinput(user_question)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text 

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_system_prompt_from_file():
    with open('docs/prompt.txt', 'r', encoding='utf-8') as f:
        system_prompt = f.read().strip()
    return system_prompt

def get_vectorstore(text_chunks):
    embeddings = GigaChatEmbeddings(credentials=auth, 
                                    verify_ssl_certs=False,
                                    scope='GIGACHAT_API_CORP')
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = GigaChat(credentials=auth,
            model='GigaChat-Pro',
            verify_ssl_certs=False, 
            scope='GIGACHAT_API_CORP',
            profanity_check=False)
     
    memory = ConversationBufferMemory(memory_key='chat_history', max_len=7, return_messages=True)
    prompt_template = get_system_prompt_from_file()

    PROMPT = PromptTemplate.from_template(
            template=prompt_template
        )
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        condense_question_prompt=PROMPT
    ) 
    return conversation_chain

@st.cache_data(show_spinner=True)
def handle_userinput(user_question):
    # response = st.session_state.conversation({'question': user_question})
    # st.session_state.chat_history = response['chat_history']

    # if st.session_state.conversation is None:
    #     st.warning("Please process the articles first before starting the conversation.")
    #     return

    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if message.type == 'ai':
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)