from vectorstore.memory import SimpleVectorStore


def test_simple_vector_store_query():
    vs = SimpleVectorStore()
    vs.add([1.0, 0.0, 0.0], {"id": "a"})
    vs.add([0.0, 1.0, 0.0], {"id": "b"})
    vs.add([0.9, 0.1, 0.0], {"id": "c"})
    res = vs.query([1.0, 0.0, 0.0], top_k=2)
    assert len(res) == 2
    assert res[0]["meta"]["id"] in {"a", "c"}


