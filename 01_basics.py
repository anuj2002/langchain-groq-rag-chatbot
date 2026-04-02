"""
LESSON 1: LangChain Basics with Groq
========================================
Concepts covered:
  - ChatGroq: wrapping a Groq LLM as a LangChain chat model
  - HumanMessage / AIMessage / SystemMessage: LangChain message types
  - ChatPromptTemplate: reusable, parameterized prompts
  - Output parsers: StrOutputParser, CommaSeparatedListOutputParser
  - LCEL (LangChain Expression Language): the | pipe syntax

Get a free Groq API key at: https://console.groq.com
Run: python 01_basics.py
"""

import os
from dotenv import load_dotenv

# Load GROQ_API_KEY from .env file
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser


# ── 1. Create the LLM ─────────────────────────────────────────────────────────
# ChatGroq wraps a Groq-hosted model so LangChain can use it like any other LLM.
# llama-3.3-70b-versatile is free and very capable on Groq's free tier.
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    max_tokens=1024,
)


# ── 2. Basic invocation with message objects ───────────────────────────────────
print("=" * 50)
print("EXAMPLE 1: Direct message invocation")
print("=" * 50)

messages = [
    SystemMessage(content="You are a concise assistant. Keep answers under 2 sentences."),
    HumanMessage(content="What is LangChain?"),
]

response = llm.invoke(messages)
# response is an AIMessage object; .content holds the text
print(f"Response: {response.content}\n")


# ── 3. ChatPromptTemplate ──────────────────────────────────────────────────────
# Templates let you define reusable prompts with variables like {topic}.
print("=" * 50)
print("EXAMPLE 2: ChatPromptTemplate")
print("=" * 50)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {domain}. Give a one-sentence definition."),
    ("human", "Define: {concept}"),
])

# .invoke() fills in the variables and returns a list of messages
filled_messages = prompt.invoke({"domain": "machine learning", "concept": "gradient descent"})
print(f"Filled prompt messages: {filled_messages.messages}\n")

response = llm.invoke(filled_messages)
print(f"Response: {response.content}\n")


# ── 4. LCEL Chains with | pipe ────────────────────────────────────────────────
# LCEL lets you compose components: prompt | llm | parser
# Each component's output becomes the next component's input.
print("=" * 50)
print("EXAMPLE 3: LCEL Chain (prompt | llm | parser)")
print("=" * 50)

str_parser = StrOutputParser()  # Extracts .content string from AIMessage

chain = prompt | llm | str_parser

result = chain.invoke({"domain": "Python programming", "concept": "list comprehension"})
print(f"Chain result (string): {result}\n")


# ── 5. CommaSeparatedListOutputParser ─────────────────────────────────────────
# Parsers transform raw LLM output into structured Python objects.
print("=" * 50)
print("EXAMPLE 4: List output parser")
print("=" * 50)

list_prompt = ChatPromptTemplate.from_messages([
    ("system", "Respond ONLY with a comma-separated list, no other text."),
    ("human", "List 5 key LangChain components."),
])

list_parser = CommaSeparatedListOutputParser()

list_chain = list_prompt | llm | list_parser

items = list_chain.invoke({})
print(f"Parsed list ({len(items)} items):")
for i, item in enumerate(items, 1):
    print(f"  {i}. {item.strip()}")


# ── 6. Streaming ──────────────────────────────────────────────────────────────
# .stream() yields tokens as they are generated, enabling real-time output.
print("\n" + "=" * 50)
print("EXAMPLE 5: Streaming output")
print("=" * 50)

stream_prompt = ChatPromptTemplate.from_messages([
    ("human", "Explain {topic} in exactly 3 bullet points."),
])

stream_chain = stream_prompt | llm | str_parser

print("Streaming: Explain RAG in 3 bullet points\n")
for chunk in stream_chain.stream({"topic": "Retrieval-Augmented Generation (RAG)"}):
    print(chunk, end="", flush=True)
print("\n")

print("Lesson 1 complete! Next: run python 02_chains.py")
