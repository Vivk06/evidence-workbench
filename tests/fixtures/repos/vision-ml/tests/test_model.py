from anomaly.model import score

def test_score_identity():
    assert score(2) == 2
