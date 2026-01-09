def test_import():
    import auroraviz
    assert hasattr(auroraviz, "line")
    assert hasattr(auroraviz, "apply")
