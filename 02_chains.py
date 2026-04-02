"""
LESSON 2: Chains, Memory & Structured Output
==============================================
Concepts covered:
  - RunnablePassthrough: pass input through unchanged
  - RunnableLambda: wrap any Python function as a chain step
  - RunnableParallel: run multiple chains in parallel
  - Conversational memory: maintain chat history across turns
  - Pydantic structured output: extract typed data from LLM responses

Get a free Groq API key at: https://console.groq.com
Run: python 02_chains.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import List


llm = ChatGroq(model="llama-3.3-70b-versatile", max_tokens=1024)
parser = StrOutputParser()


# ── 1. RunnablePassthrough ────────────────────────────────────────────────────
# Passes the input through to the next step unchanged.
# Useful when you need the original input alongside LLM output.
print("=" * 50)
print("EXAMPLE 1: RunnablePassthrough")
print("=" * 50)

prompt = ChatPromptTemplate.from_messages([
    ("human", "Translate to French: {text}"),
])

# This chain returns both the original input AND the translation
chain = RunnableParallel(
    original=RunnablePassthrough(),          # passes {"text": "..."} through
    translation=(prompt | llm | parser),     # runs the translation
)

result = chain.invoke({"text": "Hello, how are you?"})
print(f"Original input: {result['original']}")
print(f"Translation:    {result['translation']}\n")


# ── 2. RunnableLambda ─────────────────────────────────────────────────────────
# Wraps any Python function as a chainable step.
print("=" * 50)
print("EXAMPLE 2: RunnableLambda (custom step)")
print("=" * 50)

def count_words(text: str) -> dict:
    """A custom step: count words in text."""
    words = text.split()
    return {"text": text, "word_count": len(words)}

summary_prompt = ChatPromptTemplate.from_messages([
    ("human", "Summarize in one sentence: {text}"),
])

# Chain: summarize → count words in the summary
pipeline = (
    summary_prompt
    | llm
    | parser
    | RunnableLambda(count_words)
)

result = pipeline.invoke({
    "text": "LangChain is a framework for building LLM applications. "
            "It provides tools for chaining, memory, and agents."
})
print(f"Summary: {result['text']}")
print(f"Word count: {result['word_count']}\n")


# ── 3. RunnableParallel (multiple outputs) ────────────────────────────────────
# Run multiple chains on the same input simultaneously.
print("=" * 50)
print("EXAMPLE 3: RunnableParallel (run two chains at once)")
print("=" * 50)

topic = "neural networks"

summary_chain = (
    ChatPromptTemplate.from_messages([("human", "Summarize {topic} in one sentence.")])
    | llm | parser
)

analogy_chain = (
    ChatPromptTemplate.from_messages([("human", "Give a simple analogy for {topic}.")])
    | llm | parser
)

parallel_chain = RunnableParallel(
    summary=summary_chain,
    analogy=analogy_chain,
)

result = parallel_chain.invoke({"topic": topic})
print(f"Topic: {topic}")
print(f"Summary: {result['summary']}")
print(f"Analogy: {result['analogy']}\n")


# ── 4. Manual Conversation Memory ────────────────────────────────────────────
# MessagesPlaceholder injects the full message history into the prompt.
# We maintain a messages list and pass it to the prompt each turn.
print("=" * 50)
print("EXAMPLE 4: Conversational Memory (manual history)")
print("=" * 50)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Be concise."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chat_chain = chat_prompt | llm | parser

history: List = []

def chat(user_input: str) -> str:
    response = chat_chain.invoke({
        "input": user_input,
        "history": history,
    })
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response))
    return response

print("Turn 1:")
r1 = chat("My name is Alex. I'm learning LangChain.")
print(f"  User: My name is Alex. I'm learning LangChain.")
print(f"  AI:   {r1}\n")

print("Turn 2 (tests memory — does it remember 'Alex'?):")
r2 = chat("What is my name?")
print(f"  User: What is my name?")
print(f"  AI:   {r2}\n")

print("Turn 3:")
r3 = chat("What framework am I learning?")
print(f"  User: What framework am I learning?")
print(f"  AI:   {r3}\n")


# ── 5. Structured Output with Pydantic ────────────────────────────────────────
# Force the LLM to return output matching a Pydantic schema.
# .with_structured_output() uses tool-calling under the hood.
print("=" * 50)
print("EXAMPLE 5: Structured output (Pydantic)")
print("=" * 50)

class TechConcept(BaseModel):
    """Structured representation of a technical concept."""
    name: str = Field(description="Name of the concept")
    category: str = Field(description="Category: e.g. 'ML', 'Python', 'Database'")
    difficulty: str = Field(description="Difficulty level: Beginner, Intermediate, or Advanced")
    one_liner: str = Field(description="One-sentence plain-English explanation")
    related_concepts: List[str] = Field(description="3 related concepts")

structured_llm = llm.with_structured_output(TechConcept)

structured_prompt = ChatPromptTemplate.from_messages([
    ("human", "Extract structured information about: {concept}"),
])

structured_chain = structured_prompt | structured_llm

concept = structured_chain.invoke({"concept": "Transformer architecture in deep learning"})

print(f"Name:       {concept.name}")
print(f"Category:   {concept.category}")
print(f"Difficulty: {concept.difficulty}")
print(f"Summary:    {concept.one_liner}")
print(f"Related:    {', '.join(concept.related_concepts)}")

print("\nLesson 2 complete! Next: run python 03_rag_chatbot.py")
