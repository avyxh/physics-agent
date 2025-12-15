"""
ChromaDB-based Memory for Agentic Physics System
"""
import chromadb
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import json

class AgenticMemory:
    def __init__(self, memory_path: str = "data/agentic_memory"):
        self.memory_path = memory_path
        os.makedirs(memory_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=memory_path)
        self.experiences = self.client.get_or_create_collection("experiences")
        self.knowledge = self.client.get_or_create_collection("knowledge")

    def add_experience(self, problem_text: str, solution: str, success: bool, metadata: Dict[str, Any]):
        self.experiences.add(
            documents=[problem_text],
            metadatas=[{"solution": solution, "success": success, **metadata}],
            ids=[f"exp_{datetime.now().timestamp()}"]
        )

    def get_similar_experiences(self, problem_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = self.experiences.query(query_texts=[problem_text], n_results=limit)
        return [
            {
                "problem_text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            }
            for i in range(len(results['ids'][0]))
        ]

    def add_knowledge(self, concept: str, description: str, formulas: List[str], examples: List[str]):
        self.knowledge.add(
            documents=[concept],
            metadatas=[{"description": description, "formulas": formulas, "examples": examples}],
            ids=[f"knowledge_{concept}"]
        )

    def get_knowledge(self, concept: str) -> Optional[Dict[str, Any]]:
        results = self.knowledge.get(where={"concept": concept})
        if results['ids']:
            metadata = results['metadatas'][0]
            return {
                "concept": concept,
                "description": metadata["description"],
                "formulas": metadata["formulas"],
                "examples": metadata["examples"]
            }
        return None

    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        results = self.knowledge.query(query_texts=[query], n_results=limit)
        return [
            {
                "concept": results['documents'][0][i],
                "description": results['metadatas'][0][i]["description"],
                "formulas": results['metadatas'][0][i]["formulas"],
                "examples": results['metadatas'][0][i]["examples"]
            }
            for i in range(len(results['ids'][0]))
        ] 