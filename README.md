# 3σ Steinberg Limit

**[Open the calculator in your browser →](https://aiden-azarnoush.github.io/3_sigma_steinberg_limit/)**

Steinberg's relative displacement limits for PCB-mounted components — the
standard check for whether a component survives 20 million stress cycles
in random vibration or a shock event. Pick the component type and its
position on the board (a sketch of each updates as you choose), enter the
board dimensions, and read the limits in inches and millimeters. Optional
inputs give the expected displacement and a margin of safety. A Python
version (module, GUI, command line) is in [`python/`](python/), with the
original Excel worksheet in [`excel/`](excel/).

<p align="center">
<img src="figures/bending_motion.png" width="520" alt="Component and lead wires undergoing bending motion">
</p>

## The limits

For a component of length $L$ mounted on a board of thickness $h$, on the
edge of length $B$ parallel to the component:

```math
Z_{3\sigma} = \frac{0.00022\,B}{C\,h\,r\,\sqrt{L}} \quad \text{(random vibration)}
\qquad\qquad
Z_{peak} = \frac{0.00132\,B}{C\,h\,r\,\sqrt{L}} \quad \text{(shock)}
```

All lengths in inches. If the board's expected relative displacement stays
below the limit, the component's solder joints and lead wires are expected
to survive 20 million cycles.

### Relative position factor r

| Position | r |
|---|---|
| Center of PCB | 1.0 |
| Half point X, quarter point Y (near an edge) | 0.707 |
| Quarter point X and Y (near a corner) | 0.5 |
| Not sure | 1.0 (conservative) |

### Component constant C

| Component type | C |
|---|---|
| Resistors, capacitors, diodes | 0.75 |
| Standard DIP | 1.00 |
| DIP with side-brazed lead wires | 1.26 |
| Through-hole PGA | 1.00 |
| Surface-mounted LCCC | 2.25 |
| Surface-mounted chip carrier, J / gull-wing leads | 1.26 |
| Surface-mounted BGA | 1.75 |
| Fine-pitch surface-mounted, leads around the perimeter | 0.75 |
| Two parallel rows of wires (hybrid, PGA, VLSI, ASIC, VHSIC, MCM) | 1.26 |
| Not sure | 2.25 (conservative) |

> [!TIP]
> Larger C (a stiffer, less compliant attachment) and larger r (closer to
> the board center) both **shrink** the allowable displacement, so when in
> doubt choose "Not sure" for both — it is the conservative answer.

## Beyond the 20-Mcycle point

**Irvine's fatigue-curve extension.** The vibration limit is one point at
20 million cycles. Irvine (2013) extends it to a full displacement-vs-cycles
curve through $N \cdot Z^{6.4} = \text{const}$, so a different design life
rescales the allowable displacement:

```math
Z(N) = Z_{3\sigma}\left(\frac{2\times 10^{7}}{N}\right)^{1/6.4}
```

<p align="center">
<img src="figures/fatigue_curve.png" width="460" alt="Allowable displacement vs cycles">
</p>

**Margin of safety.** Given the board natural frequency $f_n$, the input
PSD $P$ at $f_n$, and transmissibility $Q$ (Steinberg's estimate
$Q = \sqrt{f_n}$ when unknown), Miles' equation gives the response and the
expected displacement:

```math
G_{rms} = \sqrt{\tfrac{\pi}{2} P f_n Q}, \qquad
Z^{exp}_{3\sigma} = \frac{3 \times 9.8\, G_{rms}}{f_n^2}, \qquad
Z^{exp}_{shock} = \frac{9.8\, G_{peak}}{f_n^2}
```

(inches, $f_n$ in Hz). The margin of safety is
$\text{MoS} = Z_{limit}/Z_{exp} - 1$; $\text{MoS} \ge 0$ passes.

> [!NOTE]
> The component sketches on the web page are schematic line drawings
> meant to make the package types recognizable, not photographs.

## Run it locally (Python)

```bash
cd python
python steinberg_gui.py                              # desktop GUI
python steinberg.py -B 6 -L 2 -t 0.062 -C 1.75 -r 0.707   # command line
```

```python
from steinberg import z_limits, z_limit_at_cycles, expected_z_random, margin
zv, zs = z_limits(B=6, L=2, h=0.062, C=1.75, r=0.707)
```

The Python module reproduces the Excel workbook in `excel/` exactly.

## Repository layout

```
index.html          the web calculator (GitHub Pages serves this)
python/             steinberg.py (module + CLI), steinberg_gui.py
excel/              the original worksheet
figures/
```

## References

1. D. S. Steinberg, *Vibration Analysis for Electronic Equipment*,
   3rd ed., John Wiley & Sons, 2000.
2. T. Irvine, "Extending Steinberg's Fatigue Analysis of Electronics
   Equipment Methodology to a Full Relative Displacement vs. Cycles
   Curve," pp. 1–29, 2013.

## License

MIT — see [LICENSE](LICENSE).
