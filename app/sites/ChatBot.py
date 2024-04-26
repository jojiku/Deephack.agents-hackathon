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
from langchain_community.document_loaders import JSONLoader

import streamlit as st
from lib.chat_with_data import ChatWithData, VectorDBParams, ChatParams
import random, json, os
from langchain.document_loaders import DirectoryLoader, TextLoader, JSONLoader
from langchain.text_splitter import SpacyTextSplitter, NLTKTextSplitter
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.query_constructor.base import AttributeInfo
from dotenv import load_dotenv  

auth = "OWYzYzU1MzEtNGZhZi00ZDQxLWI2ODMtM2QxY2EyYTY5ZWEzOjhmOGNjMTAwLWUwOGUtNDgzZC1iZWFhLTcyMGE5YjY2YzAwZg=="
load_dotenv()

def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["journal"] = record["journal"]["title"]
    metadata["publisher"] = record["journal"]["publisher"]
    if "keywords" in record:
        metadata["keywords"] = "; ".join(record["keywords"])
    metadata["year"] = int(record["year"]) if isinstance(record["year"], int) else 0
    metadata["author"] = "; ".join([author["name"] for author in record["author"]])
    metadata["url"] = record["link"][0]["url"]
    metadata["title"] = record["title"]
    return metadata

metadata_field_info = [
    AttributeInfo(
        name="journal",
        type="string",
        description="Name of the journal the paper was published in.",
    ),
    AttributeInfo(
        name="publisher",
        type="string",
        description="Name of the publisher of the journal the paper was published in. Queries may not \
            include the exact name of the publisher, but should be similar.",
    ),
    AttributeInfo(
        name="keywords",
        type="string",
        description="List of keywords associated with the paper.",
    ),
    AttributeInfo(
        name="year",
        type="int",
        description="Year the paper was published.",
    ),
    AttributeInfo(
        name="author",
        type="string",
        description="List of authors of the paper.",
    ),
    AttributeInfo(
        name="url",
        type="string",
        description="URL of the paper.",
    ),
    AttributeInfo(
        name="title",
        type="string",
        description="Title of the paper.",
    ),
]

 


llm = GigaChat(credentials=auth,
                model='GigaChat-Plus-preview',
                verify_ssl_certs=False,
                scope='GIGACHAT_API_CORP',
                profanity_check=False)

def metadata_func(doc):
        return {
            "title": doc.get("title", ""),
            "authors": doc.get("authors", []),
        }

def chatbot():
    with open("doaj/a.json", "r") as f:
        data = json.load(f)

        if "vector_db_kwargs" not in st.session_state:
            docs = [item["bibjson"] for item in data]

            abstracts = [doc["abstract"] for doc in docs]

          
            def metadata_func(doc):
                return {
                    "title": doc.get("title", ""),
                    "authors": doc.get("authors", []),
                }

           
            metadata = [metadata_func(doc) for doc in docs[:100]]

      
            st.session_state.vector_db_kwargs = {
                "docs": abstracts, 
                "metadata_field_info": metadata, 
            
    
            "splitter": NLTKTextSplitter(
                chunk_size=1000, 
                chunk_overlap=100, 
                add_start_index=True
            ),
            "llm": llm,
            "document_content_description": "Abstract of a research paper.",
            "metadata_field_info": metadata_field_info,
       
            "embedding": GigaChatEmbeddings(credentials=auth,
                                            verify_ssl_certs=False, scope="GIGACHAT_API_CORP"
            ),
           
            "persist_directory": "./vectordb/metadata",
           
            "vector_db": Chroma,
          
            "retriever_kwargs": {
                "search_type": "mmr",
                "search_kwargs": {
                    "fetch_k": 5,
                    "k": 2
                }
            }
        }
    if "chat_params_kwargs" not in st.session_state:
        st.session_state.chat_params_kwargs = {
            # which memory type to use
            "memory": ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            ),
            # which llm to use to generate questions
            "question_generator": LLMChain(
                llm=llm,
                prompt=CONDENSE_QUESTION_PROMPT
            ),
            # which chain to use to combine retrieved documents
            "combine_docs_chain": load_qa_chain(
                llm,
                chain_type="stuff"
            ),
        }
    if "vector_db_params" not in st.session_state:
        st.session_state.vector_db_params = VectorDBParams(**st.session_state.vector_db_kwargs)
    if "chat_params" not in st.session_state:
        st.session_state.chat_params = ChatParams(**st.session_state.chat_params_kwargs)
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatWithData(st.session_state.vector_db_params, st.session_state.chat_params)

    with st.sidebar:
        # retriever algorithm
        st.session_state.vector_db_kwargs["retriever_kwargs"]["search_type"] = st.radio(
            "Retriever Algorithm",
            ("similarity", "mmr"), # similarityatscore_threshold
            horizontal=True,
            format_func=lambda x: "Similarity" if x == "similarity" else "Maximum Marginal Relevance"
        )
        # fetch k for mmr
        if st.session_state.vector_db_kwargs["retriever_kwargs"]["search_type"] == "mmr":
            st.session_state.vector_db_kwargs["retriever_kwargs"]["search_kwargs"]["fetch_k"] = st.number_input(
                "Number of documents to fetch",
                min_value=1,
                max_value=30,
                value=5,
                step=1
            )
        # k for retriever
        st.session_state.vector_db_kwargs["retriever_kwargs"]["search_kwargs"]["k"] = st.number_input(
            "Number of documents to retrieve",
            min_value=1,
            max_value=10,
            value=2,
            step=1

        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "title_count" not in st.session_state:
        st.session_state.title_count = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

 
    
    def generate_response(prompt):
    
        if not hasattr(st.session_state, 'chatbot'):
            return "Chatbot is not initialized."
        
        if not hasattr(st.session_state, 'title_count'):
            st.session_state.title_count = []
        
       
        response, metadatas = st.session_state.chatbot.chat(prompt)
        
       
        markdown_str = f"{response}\n\n \n\n"

     
        for metadata in metadatas:
            print("Metadata: ", json.dumps(metadata, indent=2))
            
          
            if 'title' not in metadata or 'url' not in metadata:
                continue   
            
            title = metadata["title"]
            url = metadata["url"]

            
            # markdown_str += f"- [{title}]({url})\n"
            
        print(metadata)
        print('--------------------------------')
        return markdown_str

    

   
    def get_random_phrase():
        phrases = [
             'Хм... Дай мне секунду!',
             'Минутку, мне надо подумать...',
             'Хороший вопрос однако..'
        ]
        return random.choice(phrases)

 
    if prompt := st.chat_input("Ваш вопрос по найденным статьям"):
      
        st.chat_message("user").markdown(prompt)
       
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner(get_random_phrase()):
            response = generate_response(prompt)

   
        with st.chat_message("assistant"):
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})