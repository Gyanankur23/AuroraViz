from auroraviz import charts, theme, palettes

theme.apply()  # set global style

charts.line(
    data=[1, 3, 2, 5, 4],
    title="Line demo",
    subtitle="AuroraViz default theme",
    xlabel="Index",
    ylabel="Value",
    color=palettes.CATEGORICAL[0]
)
