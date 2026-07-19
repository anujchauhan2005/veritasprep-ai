"""
rag/generator.py
------------------
Sends the question + retrieved resume chunks + chat history to the LLM
(Groq) and returns a generated answer. Supports streaming (tokens arrive
one at a time, like ChatGPT's typing effect) as well as a plain one-shot call.
"""

from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def build_messages(question: str, context_chunks: list[str], chat_history: list[dict]) -> list[dict]:
    context_text = "\n\n".join(context_chunks)

    system_message = {
        "role": "system",
        "content": (
            "You are an interview preparation coach. Only use the resume "
            "context provided below to answer. If the answer isn't in the "
            "context, say so honestly instead of guessing.\n\n"
            f"RESUME CONTEXT:\n{context_text}"
        ),
    }
    return [system_message] + chat_history + [{"role": "user", "content": question}]


def generate_answer(question: str, context_chunks: list[str], chat_history: list[dict]) -> str:
    """One-shot (non-streaming) answer generation."""
    messages = build_messages(question, context_chunks, chat_history)
    response = client.chat.completions.create(
        model=settings.LLM_MODEL, messages=messages, temperature=0.3
    )
    return response.choices[0].message.content


def generate_answer_stream(question: str, context_chunks: list[str], chat_history: list[dict]):
    """
    Streaming version: yields text pieces as they're generated, instead of
    waiting for the full answer. Used by the /chat/stream API endpoint.
    """
    messages = build_messages(question, context_chunks, chat_history)
    stream = client.chat.completions.create(
        model=settings.LLM_MODEL, messages=messages, temperature=0.3, stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
