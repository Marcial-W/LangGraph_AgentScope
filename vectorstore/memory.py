from typing import Any, Dict, List, Tuple
import math


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class SimpleVectorStore:
    def __init__(self) -> None:
        self._items: List[Tuple[List[float], Dict[str, Any]]] = []

    def add(self, vec: List[float], meta: Dict[str, Any]) -> None:
        self._items.append((list(vec), dict(meta)))

    def query(self, vec: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        scored = [(_cosine(vec, v), m) for v, m in self._items]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"score": s, "meta": m} for s, m in scored[:top_k]]


