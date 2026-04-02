"""
LESSON 3: Full RAG Chatbot with Conversational Memory
=======================================================
Concepts covered:
  - Document loaders: load text files as LangChain Documents
  - RecursiveCharacterTextSplitter: split docs into overlapping chunks
  - HuggingFaceEmbeddings: turn text into vectors (runs locally, free)
  - FAISS vector store: store & search embeddings by similarity
  - Retriever: fetch the most relevant chunks for a query
  - RAG chain: combines retrieval + memory + Groq LLM

How RAG works:
  User question
       ↓
  Embed question → find similar chunks in FAISS
       ↓
  Inject chunks as context into the prompt
       ↓
  LLM answers using ONLY the retrieved context

Get a free Groq API key at: https://console.groq.com
Run: python 03_rag_chatbot.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from typing import List


# ── Step 1: Load Documents ────────────────────────────────────────────────────
# DirectoryLoader walks a folder and loads every matching file.
# Each file becomes one or more LangChain Document objects with:
#   .page_content  → the raw text
#   .metadata      → {"source": "path/to/file"}
print("Loading documents...")

loader = DirectoryLoader(
    path="documents/",
    glob="*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)
raw_docs = loader.load()
print(f"  Loaded {len(raw_docs)} document(s)")
for doc in raw_docs:
    print(f"    - {doc.metadata['source']} ({len(doc.page_content)} chars)")


# ── Step 2: Split into Chunks ─────────────────────────────────────────────────
# LLMs have token limits, so we split documents into smaller overlapping chunks.
# overlap ensures context is not lost at chunk boundaries.
print("\nSplitting into chunks...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # max characters per chunk
    chunk_overlap=100,    # characters shared between adjacent chunks
    separators=["\n\n", "\n", ". ", " ", ""],
)

chunks = splitter.split_documents(raw_docs)
print(f"  {len(raw_docs)} documents → {len(chunks)} chunks")
print(f"  Sample chunk:\n    '{chunks[0].page_content[:120]}...'\n")


# ── Step 3: Create Embeddings & Vector Store ──────────────────────────────────
# Embeddings convert text into vectors (lists of numbers).
# Semantically similar texts have vectors that are "close" in space.
# HuggingFaceEmbeddings runs locally — no extra API key needed.
print("Building vector store (downloads model on first run ~90MB)...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)

# FAISS stores vectors for fast nearest-neighbor search
vector_store = FAISS.from_documents(chunks, embeddings)
print(f"  Vector store ready with {len(chunks)} vectors")

# Save the index so you can reload it later without re-embedding
vector_store.save_local("faiss_index")
print("  Index saved to ./faiss_index/\n")


# ── Step 4: Create Retriever ──────────────────────────────────────────────────
# A retriever takes a query string and returns the k most similar chunks.
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},  # return top 3 most relevant chunks
)


# ── Step 5: Build the RAG Chain ───────────────────────────────────────────────
llm = ChatGroq(model="llama-3.3-70b-versatile", max_tokens=1024)

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that answers questions using ONLY the
provided context. If the answer is not in the context, say "I don't have information
about that in my documents."

Context:
{context}"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

def format_docs(docs) -> str:
    """Format retrieved documents into a single context string."""
    return "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    )


def build_rag_chain():
    """
    Build the full RAG chain:
      question → retrieve relevant chunks → inject into prompt → LLM → answer
    """
    def retrieve_and_format(inputs: dict) -> dict:
        question = inputs["question"]
        docs = retriever.invoke(question)
        return {
            "context": format_docs(docs),
            "question": question,
            "history": inputs.get("history", []),
            "source_docs": docs,
        }

    chain = (
        RunnableLambda(retrieve_and_format)
        | RunnablePassthrough.assign(
            answer=rag_prompt | llm | StrOutputParser()
        )
    )
    return chain


rag_chain = build_rag_chain()


# ── Step 6: Interactive Chat Loop ─────────────────────────────────────────────
def run_chatbot():
    print("\n" + "=" * 60)
    print("RAG CHATBOT — Ask questions about your documents!")
    print("  Documents: ai_concepts.txt, python_tips.txt")
    print("  Type 'quit' to exit, 'sources' to see last retrieved docs")
    print("=" * 60 + "\n")

    history: List = []
    last_sources: List = []

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if user_input.lower() == "sources":
            if last_sources:
                print("\nRetrieved sources for last question:")
                for i, doc in enumerate(last_sources, 1):
                    print(f"  [{i}] {doc.metadata.get('source', 'unknown')}")
                    print(f"      {doc.page_content[:100]}...")
                print()
            else:
                print("No sources yet.\n")
            continue

        result = rag_chain.invoke({
            "question": user_input,
            "history": history,
        })

        answer = result["answer"]
        last_sources = result["source_docs"]

        print(f"\nAssistant: {answer}\n")

        history.append(HumanMessage(content=user_input))
        history.append(AIMessage(content=answer))

        # Keep history to last 10 messages to avoid token overflow
        if len(history) > 10:
            history = history[-10:]


# ── Step 7: Demo mode (non-interactive) ──────────────────────────────────────
def run_demo():
    """Run a few preset questions to demonstrate the RAG chatbot."""
    print("\n" + "=" * 60)
    print("RAG CHATBOT DEMO")
    print("=" * 60)

    questions = [
        "What is RAG and how does it work?",
        "What is a vector database? Give me some examples.",
        "How do I use environment variables in Python?",
        "What are list comprehensions in Python?",
        "What is the meaning of life?",  # not in docs — tests graceful fallback
    ]

    history: List = []

    for question in questions:
        print(f"\nQ: {question}")
        result = rag_chain.invoke({"question": question, "history": history})
        answer = result["answer"]
        sources = {doc.metadata.get("source", "?") for doc in result["source_docs"]}
        print(f"A: {answer}")
        print(f"   [Sources: {', '.join(sources)}]")

        history.append(HumanMessage(content=question))
        history.append(AIMessage(content=answer))


if __name__ == "__main__":
    import sys

    if "--demo" in sys.argv:
        run_demo()
    else:
        if sys.stdin.isatty():
            run_chatbot()
        else:
            run_demo()
