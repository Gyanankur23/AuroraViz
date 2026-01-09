from auroraviz import charts, theme

def test_line_chart():
    theme.apply()
    fig, ax = charts.line([1, 2, 3])
    assert fig is not None
    assert ax is not None

def test_bar_chart():
    theme.apply()
    fig, ax = charts.bar(["A", "B"], [1, 2])
    assert fig is not None
    assert ax is not None
