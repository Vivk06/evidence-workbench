from simopt.solver import drag

def test_drag_minimum():
    assert drag(0.0) == 0.01

def test_drag_grows():
    assert drag(1.0) > drag(0.5)
