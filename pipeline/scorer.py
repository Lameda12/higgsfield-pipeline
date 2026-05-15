"""Copy variant scorer."""

from __future__ import annotations


def score_variants(variants: list[dict]) -> dict:
    """Score copy variants and return the best one.

    Heuristic: word count × lexical diversity (unique/total words).

    Args:
        variants: List of variant dicts from generate_copy().

    Returns:
        The single best-scoring variant dict (mutated with score key).
    """
    if not variants:
        raise ValueError("score_variants received an empty variants list.")

    def _heuristic(v: dict) -> float:
        words = v.get("copy", "").lower().split()
        if not words:
            return 0.0
        return len(words) * (len(set(words)) / len(words))

    scored = sorted(variants, key=_heuristic, reverse=True)
    best = scored[0]
    best["score"] = round(_heuristic(best), 4)
    return best
