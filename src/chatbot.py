import os
from typing import List, Optional

from duckduckgo_search import DDGS
from langchain_chroma.vectorstores import Chroma
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_core.documents import Document
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama.chat_models import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

from .logging import logger
from .models import DuckDuckGoResult

OLLAMA_URL = 'http://localhost:11434'
EMBED_MODEL = 'nomic-embed-text'
CHROMA_URL = "localhost"
CHROMA_PORT = 8001

embedding_function = OllamaEmbeddings(
    base_url = OLLAMA_URL,
    model = EMBED_MODEL
)

chroma_client = chromadb.HttpClient(CHROMA_URL, CHROMA_PORT)

document_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)

def search(query: str, max_pages: int = 10) -> Optional[List[DuckDuckGoResult]]:
    try: #TODO: Make Async
        results = DDGS().text(query, max_results=max_pages)
        logger.debug(f'[OK] Completed Search. Found {len(results)} pages')
        
        data = [DuckDuckGoResult(**result) for result in results]
        logger.debug("[OK] Parsed Results")
        
    except Exception as e:
        logger.error(str(e))
        return None
    
    return data


def fetch_webpages(results: List[DuckDuckGoResult]) -> Optional[List[Document]]:
    # extract the Urls
    urls = [result.href for result in results]
    
    # fetch the webpages
    try:
        pages = UnstructuredURLLoader(urls).load() #TODO: Make Async
        logger.debug(f'[OK] fetched {len(pages)} webpages')
        
    except Exception as e:
        logger.error(str(e))
        pages = None
        
    return pages


def split_webpages(pages: List[Document]) -> List[Document]:
    chunks = document_splitter.split_documents(pages)
    logger.debug(f'[OK] Split the {len(pages)} webpages into {len(chunks)} chunks')
    return chunks
    
    
def embed_webpages(chunks: List[Document]) -> Optional[Chroma]:
    collection_name = os.urandom(8).hex()
    logger.debug(f'[STATUS] creating a new Vector Store: {collection_name}')
    
    try:
        vector_store = Chroma(collection_name, embedding_function, client=chroma_client)
        vector_store.add_documents(chunks)
        logger.debug(f'[OK] added {len(chunks)} to vector store')

    except Exception as e:
        logger.error(str(e))
        return None
    
    return vector_store