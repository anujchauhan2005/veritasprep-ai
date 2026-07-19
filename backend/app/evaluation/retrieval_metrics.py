"""
evaluation/retrieval_metrics.py
---------------------------------
Measures how GOOD the retrieval step is -- separate from whether the
final answer sounds good. This answers: "out of the chunks we fetched,
how many were actually relevant?"

To use these, you need a small labeled evaluation set: a list of
questions where you (a human) have marked which chunk(s) are actually
relevant. See eval_data/eval_dataset.json for the format.
"""


def precision_at_k(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """
    Of the chunks we retrieved, what fraction were actually relevant?
    Example: retrieved 3 chunks, 2 of them were truly relevant -> 0.67
    """
    if not retrieved_ids:
        return 0.0
    hits = sum(1 for cid in retrieved_ids if cid in relevant_ids)
    return round(hits / len(retrieved_ids), 2)


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """
    Of all the truly relevant chunks that exist, how many did we
    successfully retrieve?
    Example: 4 relevant chunks exist total, we found 2 of them -> 0.5
    """
    if not relevant_ids:
        return 0.0
    hits = sum(1 for cid in retrieved_ids if cid in relevant_ids)
    return round(hits / len(relevant_ids), 2)


def mean_reciprocal_rank(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """
    How high up the list did the FIRST relevant chunk appear?
    If it's the 1st result -> score 1.0. If it's the 2nd result -> score 0.5.
    If none of the retrieved chunks were relevant -> score 0.
    """
    for rank, cid in enumerate(retrieved_ids, start=1):
        if cid in relevant_ids:
            return round(1 / rank, 2)
    return 0.0


def evaluate_retrieval(eval_dataset: list[dict], retrieve_fn) -> dict:
    """
    Runs precision/recall/MRR over an entire labeled evaluation set and
    returns the averages. `retrieve_fn` should be a function that takes
    a question and returns a list of retrieved chunk IDs.

    eval_dataset format: [{"question": ..., "relevant_ids": [...]}, ...]
    """
    precisions, recalls, mrrs = [], [], []

    for item in eval_dataset:
        retrieved_ids = retrieve_fn(item["question"])
        precisions.append(precision_at_k(retrieved_ids, item["relevant_ids"]))
        recalls.append(recall_at_k(retrieved_ids, item["relevant_ids"]))
        mrrs.append(mean_reciprocal_rank(retrieved_ids, item["relevant_ids"]))

    n = len(eval_dataset) or 1
    return {
        "avg_precision_at_k": round(sum(precisions) / n, 2),
        "avg_recall_at_k": round(sum(recalls) / n, 2),
        "avg_mrr": round(sum(mrrs) / n, 2),
    }
