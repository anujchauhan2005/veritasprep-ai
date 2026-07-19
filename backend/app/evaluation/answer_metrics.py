"""
evaluation/answer_metrics.py
------------------------------
Measures how GOOD the final generated answer is. Two metrics:

1. Groundedness (faithfulness) -- does the answer actually rely on the
   retrieved resume context, or did the LLM make things up?
2. Answer relevance -- does the answer actually address the question
   that was asked?

These are simplified, dependency-free versions of what the RAGAS library
measures more rigorously. Swapping these for real RAGAS calls is a
natural next upgrade once this works (see README "Next upgrades").
"""


def groundedness_score(answer: str, context_chunks: list[str]) -> float:
    """
    Word-overlap heuristic: what fraction of meaningful words in the
    answer also appear in the retrieved context? Higher = more grounded
    in the real resume, lower = more likely to contain invented details.
    """
    context_words = set(" ".join(context_chunks).lower().split())
    answer_words = [w for w in answer.lower().split() if len(w) > 4]

    if not answer_words:
        return 0.0

    overlap = sum(1 for w in answer_words if w in context_words)
    return round(overlap / len(answer_words), 2)


def answer_relevance_score(answer: str, question: str) -> float:
    """
    Word-overlap heuristic in the other direction: does the answer
    actually engage with the words/topic in the question, rather than
    going off on an unrelated tangent?
    """
    question_words = set(w for w in question.lower().split() if len(w) > 3)
    answer_words = set(w for w in answer.lower().split() if len(w) > 3)

    if not question_words:
        return 0.0

    overlap = len(question_words & answer_words)
    return round(overlap / len(question_words), 2)


def evaluate_answer(answer: str, question: str, context_chunks: list[str]) -> dict:
    """Convenience wrapper returning all answer-level metrics together."""
    return {
        "groundedness": groundedness_score(answer, context_chunks),
        "answer_relevance": answer_relevance_score(answer, question),
    }
