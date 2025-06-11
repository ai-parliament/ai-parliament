import os
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores  import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorDatabase:
    """
    Handles vector database integration for storing and retrieving embeddings.
    """
    def __init__(self, index_name: str = "parliament"):
        """
        Initialize the vector database.
        
        Args:
            index_name: The name of the index
        """
        self.index_name = index_name
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Path for storing the vector database
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.db_path = os.path.join(project_root, "data", "vector_db")
        
        # Create the directory if it doesn't exist
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize or load the vector store
        self.vector_store = self._load_or_create_vector_store()
    
    def _load_or_create_vector_store(self) -> FAISS:
        """
        Load an existing vector store or create a new one.
        
        Returns:
            A FAISS vector store
        """
        index_path = os.path.join(self.db_path, self.index_name)
        
        if os.path.exists(index_path):
            try:
                return FAISS.load_local(index_path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return self._create_empty_vector_store()
        else:
            return self._create_empty_vector_store()
    
    def _create_empty_vector_store(self) -> FAISS:
        """
        Create a new empty vector store with a placeholder document.
        
        Returns:
            A FAISS vector store
        """
        # Create a placeholder document to initialize the vector store
        placeholder_text = "Placeholder document for initialization"
        placeholder_doc = Document(page_content=placeholder_text, metadata={"type": "placeholder"})
        
        # Create the vector store with the placeholder
        vector_store = FAISS.from_documents([placeholder_doc], self.embeddings)
        
        # Remove the placeholder document (optional)
        # We could keep it, but removing it keeps the DB clean
        try:
            # Get the embedding for the placeholder
            placeholder_embedding = self.embeddings.embed_query(placeholder_text)
            # Remove the placeholder from the index
            vector_store.delete([0])  # Assuming it's the first document with ID 0
        except Exception as e:
            print(f"Warning: Could not remove placeholder document: {e}")
            
        return vector_store

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: A list of texts to add
            metadatas: A list of metadata dictionaries
            
        Returns:
            A list of document IDs
        """
        # Split texts into chunks
        if metadatas:
            documents = []
            for i, text in enumerate(texts):
                chunks = self.text_splitter.split_text(text)
                for chunk in chunks:
                    documents.append(Document(
                        page_content=chunk,
                        metadata=metadatas[i]
                    ))
            
            # Add documents to the vector store
            ids = self.vector_store.add_documents(documents)
        else:
            # Split and add texts without metadata
            split_texts = []
            for text in texts:
                chunks = self.text_splitter.split_text(text)
                split_texts.extend(chunks)
            
            # Add texts to the vector store
            ids = self.vector_store.add_texts(split_texts)
        
        # Save the updated vector store
        self._save_vector_store()
        
        return ids
    
    def add_party_data(self, party_name: str, party_data: str) -> List[str]:
        """
        Add party data to the vector store.
        
        Args:
            party_name: The name of the party
            party_data: The party data
            
        Returns:
            A list of document IDs
        """
        metadata = {
            "type": "party",
            "name": party_name
        }
        
        return self.add_texts([party_data], [metadata])
    
    def add_politician_data(self, politician_name: str, party_name: str, politician_data: str) -> List[str]:
        """
        Add politician data to the vector store.
        
        Args:
            politician_name: The name of the politician
            party_name: The name of the party
            politician_data: The politician data
            
        Returns:
            A list of document IDs
        """
        metadata = {
            "type": "politician",
            "name": politician_name,
            "party": party_name
        }
        
        return self.add_texts([politician_data], [metadata])
    
    def add_legislation_data(self, topic: str, legislation_data: str) -> List[str]:
        """
        Add legislation data to the vector store.
        
        Args:
            topic: The topic of the legislation
            legislation_data: The legislation data
            
        Returns:
            A list of document IDs
        """
        metadata = {
            "type": "legislation",
            "topic": topic
        }
        
        return self.add_texts([legislation_data], [metadata])
    
    def search(self, query: str, k: int = 5, filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Search the vector store for similar documents.
        
        Args:
            query: The search query
            k: The number of results to return
            filter: A filter to apply to the search
            
        Returns:
            A list of documents
        """
        if filter:
            return self.vector_store.similarity_search(query, k=k, filter=filter)
        else:
            return self.vector_store.similarity_search(query, k=k)
    
    def search_parties(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for parties in the vector store.
        
        Args:
            query: The search query
            k: The number of results to return
            
        Returns:
            A list of documents
        """
        return self.search(query, k=k, filter={"type": "party"})
    
    def search_politicians(self, query: str, k: int = 5, party_name: Optional[str] = None) -> List[Document]:
        """
        Search for politicians in the vector store.
        
        Args:
            query: The search query
            k: The number of results to return
            party_name: The name of the party to filter by
            
        Returns:
            A list of documents
        """
        if party_name:
            return self.search(query, k=k, filter={"type": "politician", "party": party_name})
        else:
            return self.search(query, k=k, filter={"type": "politician"})
    
    def search_legislation(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for legislation in the vector store.
        
        Args:
            query: The search query
            k: The number of results to return
            
        Returns:
            A list of documents
        """
        return self.search(query, k=k, filter={"type": "legislation"})
    
    def _save_vector_store(self):
        """
        Save the vector store to disk.
        """
        index_path = os.path.join(self.db_path, self.index_name)
        self.vector_store.save_local(index_path)