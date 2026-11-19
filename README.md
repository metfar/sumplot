# sumplot

Backend-neutral Grammar-of-Graphics semantics and PlotSpec for SUM.

## r20.1 histogram path

`geom_histogram()` now resolves `stat_bin` and `after_stat(density)` before rendering. `ggsave()` writes a real image through Matplotlib when installed.

## r20.2 coordinates and angular convention

`PlotSpec` now carries a backend-neutral coordinate specification. `coord_flip()` is resolved by the renderer rather than by rebuilding layers, and `coord_polar()` follows the SUM mathematical convention: angle zero lies on the positive x-axis and positive angles run counterclockwise.

Angular conversion helpers are re-exported from SumUtilsRuntime, including degrees, radians, gradians and the `gon` aliases. Historical BGI compatibility calls remain separate and are not silently reinterpreted.

<p align=center><b>- oOo -</b></p>
