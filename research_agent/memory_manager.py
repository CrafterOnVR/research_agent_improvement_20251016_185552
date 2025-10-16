import os
import chromadb
from chromadb.utils import embedding_functions
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemoryManager:
    """
    Manages a persistent long-term memory for the agent using ChromaDB.

    This class handles the initialization of the database, adding memories (documents),
    and searching for relevant memories based on a query.
    """
    def __init__(self, root: str, collection_name: str = "agent_memory"):
        """
        Initializes the MemoryManager.

        Args:
            root (str): The root directory of the project.
            collection_name (str): The name of the ChromaDB collection to use.
        """
        self.root = root
        self.collection_name = collection_name
        self.db_path = os.path.join(self.root, "data", "chroma_db")
        self._ensure_db_path_exists()

        # Initialize the ChromaDB client
        self.client = chromadb.PersistentClient(path=self.db_path)

        # Use the default SentenceTransformer embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction()

        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        logging.info(f"MemoryManager initialized. Collection '{self.collection_name}' loaded/created.")

    def _ensure_db_path_exists(self):
        """Ensures the database storage directory exists."""
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
            logging.info(f"Created ChromaDB storage directory at: {self.db_path}")

    def add_memory(self, document: str, metadata: Dict[str, Any], doc_id: str):
        """
        Adds a single memory (document) to the collection.

        Args:
            document (str): The text content of the memory.
            metadata (Dict[str, Any]): A dictionary of metadata associated with the memory.
            doc_id (str): A unique identifier for the memory.
        """
        try:
            self.collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logging.info(f"Added memory with ID: {doc_id}")
        except Exception as e:
            logging.error(f"Failed to add memory with ID {doc_id}: {e}")

    def add_memories(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Adds multiple memories (documents) to the collection.

        Args:
            documents (List[str]): A list of text contents of the memories.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries.
            ids (List[str]): A list of unique identifiers for the memories.
        """
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logging.info(f"Added {len(documents)} memories.")
        except Exception as e:
            logging.error(f"Failed to add batch of memories: {e}")

    def search_memory(self, query: str, n_results: int = 5) -> Dict[str, List[Any]]:
        """
        Searches for memories relevant to a given query.

        Args:
            query (str): The query text to search for.
            n_results (int): The number of results to return.

        Returns:
            Dict[str, List[Any]]: A dictionary containing the search results,
                                  including documents, metadatas, and distances.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            logging.info(f"Searched memory for '{query}', found {len(results.get('documents', [[]])[0])} results.")
            return results
        except Exception as e:
            logging.error(f"Failed to search memory: {e}")
            return {{}}

if __name__ == '__main__':
    # Example usage:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))

    # 1. Initialize the manager
    memory = MemoryManager(root=project_root)

    # 2. Add some memories
    memories_to_add = {
        "doc1": ("The agent's primary goal is self-improvement.", {"source": "core_directive"}),
        "doc2": ("The SelfEditor class uses AST for safe code modification.", {"source": "self_edit.py"}),
        "doc3": ("Python's asyncio library is used for concurrent tasks.", {"source": "automation_engine.py"}),
        "doc4": ("The agent should always prioritize safety and avoid critical system files.", {"source": "safety_controller.py"}),
    }

    for doc_id, (doc, meta) in memories_to_add.items():
        memory.add_memory(document=doc, metadata=meta, doc_id=doc_id)

    # 3. Search for a relevant memory
    search_query = "How does the agent handle concurrency?"
    search_results = memory.search_memory(query=search_query, n_results=2)

    print(f"\n--- Search Results for: '{search_query}' ---")
    if search_results and search_results.get('documents'):
        for i, doc in enumerate(search_results['documents'][0]):
            dist = search_results['distances'][0][i]
            meta = search_results['metadatas'][0][i]
            print(f"  Result {i+1} (Distance: {dist:.4f}):")
            print(f"    Document: {doc}")
            print(f"    Metadata: {meta}")
    else:
        print("  No relevant memories found.")
