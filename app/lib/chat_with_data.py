from typing import List, Any
from dataclasses import dataclass
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever
from langchain.schema import Document
from langchain.embeddings.base import Embeddings
from langchain.memory.chat_memory import BaseChatMemory
from langchain.chains.base import Chain
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chat_models.gigachat import GigaChat
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.text_splitter import TextSplitter
from langchain.chains.query_constructor.base import AttributeInfo
import os, re

os.environ["TOKENIZERS_PARALLELISM"] = "false"


@dataclass
class VectorDBParams:
    docs: List[Document]
    splitter: TextSplitter
    llm: GigaChat
    document_content_description: str
    metadata_field_info: List[AttributeInfo]
    embedding: Embeddings
    persist_directory: str
    vector_db: VectorStore
    retriever_kwargs: Any

 

@dataclass
class ChatParams:
    memory: BaseChatMemory
    question_generator: Chain
    combine_docs_chain: BaseCombineDocumentsChain


 
def remove_extra_whitespace_in_parentheses(text):
    def replace(match):
        # Replace multiple spaces with a single space
        return re.sub(r"\s+", " ", match.group())

    return re.sub(r"\(.*?\)", replace, text)


def basic_preprocessing(doc):
    # remove whitespace
    doc.page_content = doc.page_content.replace("\n", " ")
    doc.page_content = doc.page_content.replace("\xa0", " ")
    doc.page_content = doc.page_content.strip()
    doc.page_content = remove_extra_whitespace_in_parentheses(doc.page_content)
    return doc


class ChatWithData:
    def __init__(self, vector_db_params: VectorDBParams, chat_params: ChatParams):
        # assign params
        print(vector_db_params)
        self.memory = chat_params.memory
        self.question_generator = chat_params.question_generator
        self.combine_docs_chain = chat_params.combine_docs_chain
        # set up vector db
        if os.path.isdir(vector_db_params.persist_directory):
            # load existing vector db
            print("Loading existing vector db...") 
            
            print()
            vectordb = vector_db_params.vector_db(
                persist_directory=vector_db_params.persist_directory,
                embedding_function=vector_db_params.embedding,
            )
          
            self.retriever = SelfQueryRetriever.from_llm(
                vector_db_params.llm,
                vectordb,
                vector_db_params.document_content_description,
                vector_db_params.metadata_field_info,
                verbose=True,
                **vector_db_params.retriever_kwargs
            )
        else:
            # create new vector db
            print("Creating new vector db...")
            
            # preprocess and chunk docs
            chunked_docs = vector_db_params.splitter.create_documents(
                [doc for doc in vector_db_params.docs]
            )

     

            vectordb = vector_db_params.vector_db.from_documents(
                documents=chunked_docs,
                embedding=vector_db_params.embedding,
                persist_directory=vector_db_params.persist_directory,
            )
            self.retriever = SelfQueryRetriever.from_llm(
                vector_db_params.llm,
                vectordb,
                vector_db_params.document_content_description,
                vector_db_params.metadata_field_info,
                verbose=True,
                **vector_db_params.retriever_kwargs
            )
        print("Loaded!")
        print("Initializing chat...")
        self.qa = ConversationalRetrievalChain(
            retriever=self.retriever,
            memory=self.memory,
            question_generator=self.question_generator,
            combine_docs_chain=self.combine_docs_chain,
            return_source_documents=True,
            return_generated_question=True,
        )
        print("Initialized!")

    def chat(self, query):
        result = self.qa({"question": query})
        print(result)

        print(result["answer"])  
        print([doc.metadata for doc in result["source_documents"]])  
        return result["answer"], [doc.metadata for doc in result["source_documents"]]