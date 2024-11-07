from src.chatbot import (embed_webpages, embedding_function, fetch_webpages,
                         search, split_webpages)

if __name__ == '__main__':
    results = search("Weather in Kolkata", 5)
    pages = split_webpages(fetch_webpages(results))
    vector_store = embed_webpages(pages)