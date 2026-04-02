# LangChain + Groq Learning Project
### A Progressive 3-Lesson Course to Build a RAG Chatbot from Scratch

---

## What Is This Project?

This project teaches you **LangChain** — the most popular framework for building AI applications — using **Groq's free API** as the LLM backend.

You will learn by building real, working code across 3 progressive lessons:

| Lesson | File | What You Build |
|--------|------|----------------|
| 1 | `01_basics.py` | Prompts, chains, parsers, streaming |
| 2 | `02_chains.py` | Parallel chains, memory, structured output |
| 3 | `03_rag_chatbot.py` | Full RAG chatbot with document retrieval |

By the end, you will have a **chatbot that reads your own documents and answers questions about them** — which is exactly how real AI products like Notion AI, GitHub Copilot Chat, and customer support bots work.

---

## Why LangChain?

Without LangChain, building an AI app means writing hundreds of lines of boilerplate:
- Manually formatting prompts
- Manually managing conversation history
- Manually calling embedding APIs
- Manually building retrieval logic

LangChain gives you **ready-made building blocks** for all of this, so you focus on your application logic instead.

---

## Project Structure

```
AI_Project/
│
├── 01_basics.py          ← Lesson 1: Core LangChain concepts
├── 02_chains.py          ← Lesson 2: Advanced chains & memory
├── 03_rag_chatbot.py     ← Lesson 3: Full RAG chatbot
│
├── documents/            ← Knowledge base for the RAG chatbot
│   ├── ai_concepts.txt   ← Document 1: AI/ML terminology
│   └── python_tips.txt   ← Document 2: Python best practices
│
├── faiss_index/          ← Auto-created when you run Lesson 3
│   ├── index.faiss       ← Vector index (binary file)
│   └── index.pkl         ← Metadata for the index
│
├── requirements.txt      ← All Python dependencies
├── .env                  ← Your secret API key (never share this)
└── .env.example          ← Template showing which keys are needed
```

---

## Core Concepts Explained

### What is an LLM?
A **Large Language Model** (LLM) is an AI that understands and generates text. Groq hosts open-source LLMs (like Llama 3.3) and lets you call them via API. We use `llama-3.3-70b-versatile` — a 70 billion parameter model available for free.

### What is LangChain?
LangChain is a Python framework that wraps LLMs and provides:
- **Prompt Templates** — reusable, parameterized prompts
- **Chains** — sequences of operations connected by `|` pipes
- **Memory** — storing and passing conversation history
- **Document Loaders** — reading files, PDFs, web pages
- **Vector Stores** — storing and searching text by meaning

### What is RAG?
**Retrieval-Augmented Generation** solves a key problem: LLMs don't know about *your* documents.

```
WITHOUT RAG:  User asks → LLM guesses from training data → often wrong
WITH RAG:     User asks → fetch relevant docs → LLM reads docs → accurate answer
```

RAG is used in: Notion AI, GitHub Copilot Chat, customer support bots, legal research tools, medical Q&A systems.

### What are Embeddings?
An **embedding** converts text into a list of numbers (a vector) that captures its *meaning*. Texts with similar meanings get similar vectors. This lets us do **semantic search** — finding documents that are *about* the same thing, even if they use different words.

Example:
- "How do I read a file?" and "Python file reading" → very similar vectors
- "How do I read a file?" and "gradient descent" → very different vectors

### What is FAISS?
**FAISS** (Facebook AI Similarity Search) is a library that stores vectors and finds the nearest neighbors (most similar vectors) extremely fast. When you ask a question, FAISS finds the document chunks whose vectors are closest to your question's vector.

---

## Lesson 1 — `01_basics.py`

### Purpose
Introduces the absolute fundamentals of LangChain. After this lesson you understand how to call an LLM, use templates, and build basic chains.

### Sections Explained

#### `ChatGroq` — The LLM Wrapper
```python
llm = ChatGroq(model="llama-3.3-70b-versatile", max_tokens=1024)
```
**Why:** LangChain wraps different LLMs (OpenAI, Groq, Anthropic, etc.) behind a common interface. Swapping LLMs later means changing one line.

#### `SystemMessage / HumanMessage` — Message Types
```python
messages = [
    SystemMessage(content="You are a concise assistant."),
    HumanMessage(content="What is LangChain?"),
]
```
**Why:** Chat models expect a list of messages with roles. `SystemMessage` sets behavior; `HumanMessage` is the user's input; `AIMessage` is the model's reply. LangChain gives these as typed Python objects.

#### `ChatPromptTemplate` — Reusable Prompts
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}."),
    ("human", "Define: {concept}"),
])
```
**Why:** Hard-coding prompts creates duplicate code. Templates let you define the prompt once with `{variables}` and fill them in at runtime. This is the foundation of every LangChain chain.

#### LCEL — The `|` Pipe Syntax
```python
chain = prompt | llm | parser
result = chain.invoke({"domain": "Python", "concept": "list comprehension"})
```
**Why:** LCEL (LangChain Expression Language) lets you compose components like Unix pipes. Each component receives the previous component's output. This makes chains readable, composable, and easy to debug.

#### `StrOutputParser` — Extract the Text
```python
parser = StrOutputParser()
```
**Why:** `llm.invoke()` returns an `AIMessage` object. The parser extracts just the `.content` string so downstream steps receive plain text.

#### Streaming
```python
for chunk in chain.stream({"topic": "RAG"}):
    print(chunk, end="", flush=True)
```
**Why:** Without streaming, you wait for the full response before seeing anything. Streaming shows tokens as they are generated — essential for good UX in chatbots.

---

## Lesson 2 — `02_chains.py`

### Purpose
Teaches advanced chain composition, parallel execution, conversation memory, and structured (typed) output from LLMs.

### Sections Explained

#### `RunnablePassthrough` — Pass Input Unchanged
```python
chain = RunnableParallel(
    original=RunnablePassthrough(),
    translation=(prompt | llm | parser),
)
```
**Why:** Sometimes you need the original input alongside the LLM's output. `RunnablePassthrough` is a no-op that just forwards its input to the output dict. Here we get both `original` and `translation` in one call.

#### `RunnableLambda` — Any Python Function as a Chain Step
```python
def count_words(text: str) -> dict:
    return {"text": text, "word_count": len(text.split())}

pipeline = summary_prompt | llm | parser | RunnableLambda(count_words)
```
**Why:** Not every step needs an LLM. `RunnableLambda` wraps any Python function so it can live inside a chain. Use it for data transformation, validation, logging, or calling external APIs.

#### `RunnableParallel` — Run Multiple Chains Simultaneously
```python
parallel_chain = RunnableParallel(
    summary=summary_chain,
    analogy=analogy_chain,
)
result = parallel_chain.invoke({"topic": "neural networks"})
```
**Why:** Running two LLM calls sequentially doubles the latency. `RunnableParallel` fires both at the same time and collects results into a dict. The total time equals the slowest chain, not the sum.

#### Conversational Memory
```python
history: List = []
history.append(HumanMessage(content=user_input))
history.append(AIMessage(content=response))
```
**Why:** LLMs are stateless — each API call is independent. To have a conversation, you must send the full history every time. We use `MessagesPlaceholder` in the prompt to inject history, and manage the list ourselves. We cap it at 10 messages to avoid hitting token limits.

#### Structured Output with Pydantic
```python
class TechConcept(BaseModel):
    name: str
    difficulty: str
    one_liner: str

structured_llm = llm.with_structured_output(TechConcept)
```
**Why:** Raw LLM output is a string. For real applications you need typed, validated data. `.with_structured_output()` uses tool-calling under the hood to guarantee the response matches your Pydantic schema — you get a real Python object, not a string to parse.

---

## Lesson 3 — `03_rag_chatbot.py`

### Purpose
Assembles everything into a production-pattern RAG chatbot. The chatbot answers questions grounded in your documents and gracefully declines out-of-scope questions.

### Sections Explained

#### Step 1: Document Loading
```python
loader = DirectoryLoader(path="documents/", glob="*.txt", loader_cls=TextLoader)
raw_docs = loader.load()
```
**Why:** `DirectoryLoader` walks a folder and loads every matching file. Each file becomes a `Document` object with `.page_content` (the text) and `.metadata` (filename, etc.). LangChain has loaders for PDFs, Word docs, web pages, Notion, GitHub, and 50+ other sources — swap the loader to change the data source.

#### Step 2: Text Splitting
```python
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(raw_docs)
```
**Why:** LLMs have token limits, so you can't feed an entire book as context. We split documents into small overlapping chunks. `chunk_overlap=100` means adjacent chunks share 100 characters so context isn't lost at boundaries. The splitter tries to split on paragraphs first, then sentences, then words — preserving semantic units.

#### Step 3: Embeddings
```python
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
```
**Why:** We use `all-MiniLM-L6-v2` — a small (90MB), fast sentence embedding model that runs locally on your CPU for free. It converts each text chunk into a 384-dimensional vector. No extra API key needed. In production you might use OpenAI's `text-embedding-3-small` for better quality.

#### Step 4: Vector Store (FAISS)
```python
vector_store = FAISS.from_documents(chunks, embeddings)
vector_store.save_local("faiss_index")
```
**Why:** FAISS stores all the chunk vectors in an index file on disk. `save_local()` means you only pay the embedding cost once — on subsequent runs you can call `FAISS.load_local()` to skip re-embedding. In production you'd use Pinecone, Weaviate, or ChromaDB for cloud persistence and scale.

#### Step 5: Retriever
```python
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
```
**Why:** The retriever wraps FAISS with a simple interface: give it a string, get back the top `k` most similar chunks. `k=3` is a good default — enough context without overwhelming the LLM's context window.

#### Step 6: RAG Chain
```python
def retrieve_and_format(inputs):
    docs = retriever.invoke(inputs["question"])
    return {"context": format_docs(docs), "question": ..., "history": ...}

chain = RunnableLambda(retrieve_and_format) | RunnablePassthrough.assign(
    answer=rag_prompt | llm | StrOutputParser()
)
```
**Why:** The chain does two things in sequence:
1. Retrieve relevant chunks and format them into a `context` string
2. Pass `context + question + history` into the LLM prompt to generate a grounded answer

The system prompt explicitly tells the LLM: *"answer using ONLY the provided context"*. This is what prevents hallucination.

#### Step 7: Interactive Loop
```python
while True:
    user_input = input("You: ")
    result = rag_chain.invoke({"question": user_input, "history": history})
    print(f"Assistant: {result['answer']}")
```
**Why:** The loop maintains conversation history across turns so the chatbot can handle follow-up questions like "tell me more about that" or "what about the second point?". History is capped at 10 messages to stay within token limits.

---

## How to Copy and Run This Project Independently

Follow these steps exactly on a new machine:

### Step 1 — Prerequisites
Make sure you have Python 3.10 or higher installed:
```bash
python3 --version   # should print 3.10 or above
```

If not, download Python from [python.org](https://python.org).

### Step 2 — Copy the Project Files
Copy the entire `AI_Project` folder to the new machine. The minimum required files are:

```
AI_Project/
├── 01_basics.py
├── 02_chains.py
├── 03_rag_chatbot.py
├── documents/
│   ├── ai_concepts.txt
│   └── python_tips.txt
├── requirements.txt
└── .env.example
```

> **Note:** Do NOT copy `.env` — it contains your secret API key. Create a fresh one on the new machine.

### Step 3 — Create a Virtual Environment (Recommended)
A virtual environment keeps your project's dependencies isolated from other Python projects:
```bash
cd AI_Project

# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate       # Mac / Linux
.venv\Scripts\activate          # Windows
```

Your terminal prompt will change to show `(.venv)` when it's active.

### Step 4 — Install Dependencies
```bash
pip install -r requirements.txt
```

This installs everything: LangChain, Groq SDK, FAISS, sentence-transformers, etc.

### Step 5 — Get a Free Groq API Key
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Go to **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)

### Step 6 — Set Up the `.env` File
```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your real key:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

> **Security rule:** Never commit `.env` to Git. Add it to `.gitignore`.

### Step 7 — Run the Lessons

```bash
# Lesson 1: LangChain basics
python3 01_basics.py

# Lesson 2: Chains, memory, structured output
python3 02_chains.py

# Lesson 3: Interactive RAG chatbot
python3 03_rag_chatbot.py

# Lesson 3: Non-interactive demo (preset questions)
python3 03_rag_chatbot.py --demo
```

> **First run of Lesson 3** downloads the `all-MiniLM-L6-v2` embedding model (~90MB). This happens only once; subsequent runs load it from cache.

---

## Chatbot Commands (Lesson 3 Interactive Mode)

Once the chatbot is running, you can use these special inputs:

| Input | Action |
|-------|--------|
| Any question | Get an answer grounded in your documents |
| `sources` | Show which document chunks were used for the last answer |
| `quit` or `exit` or `q` | Exit the chatbot |

**Example session:**
```
You: What is RAG?
Assistant: RAG (Retrieval-Augmented Generation) is a technique that combines
a retrieval system with a generative model...

You: sources
Retrieved sources for last question:
  [1] documents/ai_concepts.txt
      Retrieval-Augmented Generation (RAG) is a technique...

You: What are f-strings?
Assistant: f-strings are a way to format strings in Python...

You: quit
Goodbye!
```

---

## Adding Your Own Documents

To make the chatbot answer questions about YOUR content:

1. Add any `.txt` files to the `documents/` folder
2. Delete the old `faiss_index/` folder (so the index is rebuilt)
3. Run `python3 03_rag_chatbot.py` again

The chatbot will automatically load, split, embed, and index your new documents.

**Supported sources (swap the loader in Step 1):**

| Content Type | LangChain Loader |
|---|---|
| Text files | `TextLoader` |
| PDF files | `PyPDFLoader` |
| Word documents | `Docx2txtLoader` |
| Web pages | `WebBaseLoader` |
| YouTube transcripts | `YoutubeLoader` |
| Notion pages | `NotionDirectoryLoader` |

---

## Dependencies Reference

| Package | Version | Purpose |
|---------|---------|---------|
| `langchain` | latest | Core LangChain framework |
| `langchain-groq` | latest | Groq LLM integration for LangChain |
| `langchain-community` | latest | Community loaders, FAISS, HuggingFace embeddings |
| `langchain-text-splitters` | latest | `RecursiveCharacterTextSplitter` and others |
| `faiss-cpu` | latest | Fast vector similarity search (CPU version) |
| `sentence-transformers` | latest | Local embedding model (`all-MiniLM-L6-v2`) |
| `python-dotenv` | latest | Load API keys from `.env` file |

---

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `AuthenticationError` | Wrong or missing Groq API key | Check your `.env` file has the correct `GROQ_API_KEY` |
| `ModuleNotFoundError: langchain_groq` | Packages not installed | Run `pip install -r requirements.txt` |
| `No module named 'langchain_groq'` on `python3` | Wrong Python version | Use `python3.13` or activate your virtual environment |
| `FAISS index not found` | Running chatbot before building index | Just run `03_rag_chatbot.py` normally — it builds the index automatically |
| `RateLimitError` from Groq | Too many requests on free tier | Wait 60 seconds and try again |
| Chatbot says "I don't have information" for everything | Index is stale | Delete `faiss_index/` folder and re-run |

---

## How RAG Works — Visual Summary

```
┌─────────────────────────────────────────────────────────┐
│                    INDEXING PHASE                        │
│          (runs once when you start the chatbot)          │
│                                                         │
│  documents/*.txt                                        │
│       │                                                 │
│       ▼ DirectoryLoader                                 │
│  [Document, Document, ...]                              │
│       │                                                 │
│       ▼ RecursiveCharacterTextSplitter                  │
│  [Chunk1, Chunk2, Chunk3, ... Chunk10]                  │
│       │                                                 │
│       ▼ HuggingFaceEmbeddings (all-MiniLM-L6-v2)       │
│  [[0.12, -0.34, ...], [0.89, 0.23, ...], ...]          │
│       │                                                 │
│       ▼ FAISS.from_documents()                          │
│  faiss_index/ (saved to disk)                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    QUERY PHASE                           │
│              (runs on every user question)               │
│                                                         │
│  User: "What is a vector database?"                     │
│       │                                                 │
│       ▼ HuggingFaceEmbeddings                           │
│  [0.45, -0.12, ...]  ← question vector                  │
│       │                                                 │
│       ▼ FAISS similarity search (k=3)                   │
│  Top 3 matching chunks from your documents              │
│       │                                                 │
│       ▼ format_docs()                                   │
│  "A Vector Database stores and indexes..."              │
│       │                                                 │
│       ▼ Inject into RAG prompt + conversation history   │
│  System: "Answer using ONLY this context: ..."         │
│       │                                                 │
│       ▼ ChatGroq (llama-3.3-70b-versatile)              │
│  "A vector database stores and indexes vector           │
│   embeddings. Examples include FAISS, Pinecone..."      │
│       │                                                 │
│       ▼ StrOutputParser                                 │
│  Final answer string shown to user                      │
└─────────────────────────────────────────────────────────┘
```

---

## What to Learn Next

Once you're comfortable with this project, explore these topics:

1. **LangGraph** — Build stateful, multi-step AI agents with conditional logic and loops
2. **Streaming in RAG** — Stream the chatbot's answer token by token for better UX
3. **PDF support** — Swap `TextLoader` for `PyPDFLoader` to chat with PDF files
4. **Better embeddings** — Try `OpenAIEmbeddings` (`text-embedding-3-small`) for higher retrieval accuracy
5. **Reranking** — Add a cross-encoder reranker after FAISS retrieval to improve result quality
6. **Persistent memory** — Store conversation history in a database instead of in-memory
7. **Evaluation** — Use RAGAS to measure your chatbot's accuracy, faithfulness, and relevance
