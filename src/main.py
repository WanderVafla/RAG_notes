from rag import rag_search

if __name__ == "__main__":
    while True: 
        user_ask = input("What is your ask? : ")
        
        [response, metadatas] = rag_search(user_ask)
        metadatas = metadatas or {}
        
        print(f"\n{response}")
        
        sources = [meta['file_path'] for meta in metadatas.values() if meta.get('file_path')] or {}
        
        print(f"\nSources:\n\n{'\n'.join(s for s in sources or "Not found files")}\n")