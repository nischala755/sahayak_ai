"""
============================================
SAHAYAK AI - RAG (Retrieval Augmented Generation) Service
============================================
Grounded response pipeline with vector store.
Retrieval-before-generation for accurate pedagogy.
============================================
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


class RAGService:
    """
    Retrieval Augmented Generation Service.
    
    Pipeline:
    1. Embed query using sentence transformer
    2. Search FAISS index for similar documents
    3. Retrieve relevant context
    4. Augment Gemini prompt with retrieved context
    5. Generate grounded response
    """
    
    def __init__(self):
        self.embedding_model = None
        self.faiss_index = None
        self.documents: List[Dict] = []
        self.document_embeddings = []
        self.index_path = "data/faiss_index"
        self.docs_path = "data/rag_documents.json"
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        # Initialize if dependencies available
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model and FAISS index."""
        if HAS_EMBEDDINGS:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ RAG: Sentence transformer loaded")
            except Exception as e:
                print(f"⚠️ RAG: Could not load embedding model: {e}")
        
        if HAS_FAISS and HAS_NUMPY:
            try:
                self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
                self._load_index()
                print(f"✅ RAG: FAISS index ready with {len(self.documents)} documents")
            except Exception as e:
                print(f"⚠️ RAG: Could not initialize FAISS: {e}")
    
    def _load_index(self):
        """Load existing index and documents from disk."""
        if os.path.exists(self.docs_path):
            try:
                with open(self.docs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    
                # Rebuild embeddings
                if self.documents and self.embedding_model:
                    texts = [d.get('text', '') for d in self.documents]
                    embeddings = self.embedding_model.encode(texts)
                    self.faiss_index.add(np.array(embeddings).astype('float32'))
            except Exception as e:
                print(f"⚠️ RAG: Error loading documents: {e}")
    
    def _save_index(self):
        """Save documents to disk."""
        os.makedirs(os.path.dirname(self.docs_path), exist_ok=True)
        try:
            with open(self.docs_path, 'w', encoding='utf-8') as f:
                json.dump({'documents': self.documents}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ RAG: Error saving documents: {e}")
    
    def add_document(
        self,
        text: str,
        metadata: Dict[str, Any] = None,
        doc_type: str = "general"
    ) -> str:
        """
        Add a document to the RAG index.
        
        Args:
            text: Document text content
            metadata: Additional metadata (subject, grade, topic, etc.)
            doc_type: Type of document (ncert, solution, playbook, etc.)
        
        Returns:
            Document ID
        """
        if not self.embedding_model or not HAS_NUMPY:
            return None
        
        # Generate document ID
        doc_id = hashlib.md5(text.encode()).hexdigest()[:12]
        
        # Check for duplicates
        if any(d.get('id') == doc_id for d in self.documents):
            return doc_id
        
        # Create document
        doc = {
            'id': doc_id,
            'text': text,
            'type': doc_type,
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Generate embedding and add to index
        try:
            embedding = self.embedding_model.encode([text])[0]
            self.faiss_index.add(np.array([embedding]).astype('float32'))
            self.documents.append(doc)
            self._save_index()
            return doc_id
        except Exception as e:
            print(f"⚠️ RAG: Error adding document: {e}")
            return None
    
    def add_ncert_reference(
        self,
        chapter_name: str,
        topics: List[str],
        learning_objectives: List[str],
        class_level: str,
        subject: str
    ) -> str:
        """Add NCERT chapter as a RAG document."""
        text = f"""
        NCERT Reference - Class {class_level} {subject}
        Chapter: {chapter_name}
        Topics: {', '.join(topics)}
        Learning Objectives: {'. '.join(learning_objectives)}
        """
        
        metadata = {
            'class_level': class_level,
            'subject': subject,
            'chapter_name': chapter_name,
            'topics': topics
        }
        
        return self.add_document(text.strip(), metadata, doc_type='ncert')
    
    def add_shared_solution(
        self,
        problem: str,
        solution: str,
        subject: str = None,
        grade: str = None,
        trust_score: float = 0.0
    ) -> str:
        """Add a teacher-shared solution to RAG index."""
        text = f"""
        Classroom Problem: {problem}
        Teacher Solution: {solution}
        Subject: {subject or 'General'}
        Grade: {grade or 'All'}
        """
        
        metadata = {
            'subject': subject,
            'grade': grade,
            'trust_score': trust_score,
            'type': 'teacher_solution'
        }
        
        return self.add_document(text.strip(), metadata, doc_type='solution')
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_type: str = None,
        filter_subject: str = None,
        filter_grade: str = None
    ) -> List[Dict]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_type: Filter by document type
            filter_subject: Filter by subject
            filter_grade: Filter by grade
        
        Returns:
            List of relevant documents with scores
        """
        if not self.embedding_model or not self.faiss_index or not HAS_NUMPY:
            return []
        
        if len(self.documents) == 0:
            return []
        
        try:
            # Embed query
            query_embedding = self.embedding_model.encode([query])[0]
            query_vec = np.array([query_embedding]).astype('float32')
            
            # Search FAISS
            distances, indices = self.faiss_index.search(query_vec, min(top_k * 2, len(self.documents)))
            
            # Get results with filtering
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    
                    # Apply filters
                    if filter_type and doc.get('type') != filter_type:
                        continue
                    
                    metadata = doc.get('metadata', {})
                    if filter_subject and metadata.get('subject', '').lower() != filter_subject.lower():
                        continue
                    if filter_grade and str(metadata.get('grade', '')) != str(filter_grade):
                        continue
                    
                    results.append({
                        'id': doc.get('id'),
                        'text': doc.get('text'),
                        'type': doc.get('type'),
                        'metadata': metadata,
                        'score': float(1 / (1 + distances[0][i]))  # Convert distance to similarity
                    })
                    
                    if len(results) >= top_k:
                        break
            
            return results
            
        except Exception as e:
            print(f"⚠️ RAG: Search error: {e}")
            return []
    
    def get_augmented_context(
        self,
        query: str,
        subject: str = None,
        grade: str = None
    ) -> Tuple[str, List[Dict]]:
        """
        Get augmented context for Gemini prompt.
        
        Returns:
            Tuple of (context_string, sources)
        """
        # Search for relevant documents
        results = self.search(
            query=query,
            top_k=3,
            filter_subject=subject,
            filter_grade=grade
        )
        
        if not results:
            # Try without filters
            results = self.search(query=query, top_k=3)
        
        if not results:
            return "", []
        
        # Build context string
        context_parts = []
        sources = []
        
        for i, doc in enumerate(results):
            if doc['score'] > 0.3:  # Only include if reasonably relevant
                context_parts.append(f"Reference {i+1}: {doc['text'][:500]}")
                sources.append({
                    'type': doc['type'],
                    'id': doc['id'],
                    'score': doc['score'],
                    'metadata': doc['metadata']
                })
        
        context = "\n\n".join(context_parts)
        return context, sources
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics."""
        type_counts = {}
        for doc in self.documents:
            doc_type = doc.get('type', 'unknown')
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        return {
            'total_documents': len(self.documents),
            'types': type_counts,
            'embedding_model': 'all-MiniLM-L6-v2' if self.embedding_model else None,
            'faiss_ready': self.faiss_index is not None
        }


# Singleton instance
rag_service = RAGService()
