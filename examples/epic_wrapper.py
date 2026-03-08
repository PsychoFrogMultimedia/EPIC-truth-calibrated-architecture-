import os
import json
import numpy as np
import faiss
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer
from epic import epic_loader  # Assuming this is the main entry point from src/ (loads JSON spec and runs the 8-step loop)
# If your src/ has a different import (e.g., from src.epic_runtime import run_pipeline), adjust accordingly.

class EpicWrapper:
    def __init__(self, model="claude-3.5-sonnet-20240620", api_key=None):
        """
        Initialize the EPIC wrapper with an LLM client.
        - model: Anthropic model name (easy to swap for 'grok-beta' if xAI API available, or OpenAI via openai SDK).
        - api_key: Anthropic API key (defaults to os.environ['ANTHROPIC_API_KEY']).
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment or passed to init.")
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        
        # Basic RAG setup for ARC (Adaptive Reality-binding)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, fast embedder (~80MB)
        self.index = None  # FAISS index (flat for simplicity; scalable to large corpora)
        self.documents = []  # List of doc strings for retrieval
        
    def add_knowledge_base(self, documents):
        """
        Add a list of documents (strings) to the RAG index for grounding in ARC.
        Example: wrapper.add_knowledge_base(["Doc1 text...", "Doc2 text..."])
        """
        if not documents:
            return
        embeddings = self.embedder.encode(documents, convert_to_tensor=False)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)  # Simple L2 distance index
        self.index.add(embeddings.astype(np.float32))
        self.documents.extend(documents)
        print(f"Added {len(documents)} documents to RAG index.")

    def _llm_call(self, prompt, max_tokens=1024, temperature=0.7):
        """
        Internal LLM call wrapper. This is used for sub-tasks in the EPIC pipeline (e.g., probing, CFI forecasting).
        Returns the generated text.
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _rag_retrieve(self, query, top_k=3):
        """
        Simple RAG retrieval for ARC grounding: Embed query, search index, return top docs.
        Returns list of (doc, score) tuples or empty if no index.
        """
        if self.index is None:
            return []
        query_emb = self.embedder.encode([query], convert_to_tensor=False).astype(np.float32)
        distances, indices = self.index.search(query_emb, top_k)
        results = [(self.documents[idx], dist) for idx, dist in zip(indices[0], distances[0]) if idx != -1]
        return results

    def process(self, query, debug=False):
        """
        Main entry point: Process a query through the full EPIC pipeline.
        - Integrates LLM calls where needed (e.g., for regime classification, inference, speculation).
        - Uses RAG in ARC step for grounding.
        - Returns the final epistemically tagged response (dict or string based on your runtime output).
        
        Assumptions based on EPIC spec:
        - epic_loader.load_spec() returns the operational config.
        - The 8-step loop (Probe -> Branch -> ... -> Maintain) is run via epic_loader.run_pipeline(query, config, callbacks).
        - We provide callbacks for 'model_call' and 'arc_retrieve' to hook in LLM/RAG.
        """
        # Load EPIC operational spec (from your docs/ JSON)
        config = epic_loader.load_spec('docs/EPIC-v10-Operational-Spec.json')  # Adjust path if needed
        
        # Define callbacks for integration points (customize based on your exact runtime impl)
        def model_callback(step, input_data):
            # Example: At steps needing LLM (e.g., CFI forecasting or claim resolution), generate with prompt
            prompt = f"EPIC {step}: {json.dumps(input_data)}"  # Build prompt from step/input (tune this!)
            return self._llm_call(prompt)
        
        def arc_callback(query):
            # ARC reality-binding: Retrieve grounding docs
            retrieved = self._rag_retrieve(query)
            return {"grounding": retrieved}  # Format as needed for your ARC resolver
        
        # Run the pipeline with hooks
        result = epic_loader.run_pipeline(
            query=query,
            config=config,
            callbacks={
                'model_call': model_callback,
                'arc_retrieve': arc_callback
            },
            debug=debug
        )
        
        return result  # e.g., {'tagged_response': '...', 'epistemic_breakdown': {...}}

# Demo usage
if __name__ == "__main__":
    wrapper = EpicWrapper()
    wrapper.add_knowledge_base([
        "Grounded fact: The capital of France is Paris.",  # Sample docs; users add real ones
        "Inference example: Based on trends, AI adoption will grow 20% YoY."
    ])
    response = wrapper.process("What is the capital of France and future AI trends?")
    print(response)
