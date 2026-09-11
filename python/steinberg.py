"""
Steinberg relative displacement limits for circuit-board components.

For 20 million stress cycles (Steinberg, "Vibration Analysis for
Electronic Equipment", 3rd ed., Wiley, 2000):

    Z_3sigma = 0.00022 B / (C h r sqrt(L))     random vibration limit  [in]
    Z_peak   = 0.00132 B / (C h r sqrt(L))     shock limit             [in]

where
    B : length of the PCB edge parallel to the component  [in]
    L : length of the electronic component                [in]
    h : circuit board thickness                           [in]
    r : relative position factor (component location on the board)
    C : component-type constant, 0.75 <= C <= 2.25
"""

import math

# Component-type constants (Steinberg). Order preserved for GUI dropdowns.
COMPONENT_C = {
    'Resistors, capacitors, diodes': 0.75,
    'Standard DIP': 1.00,
    'DIP with side-brazed lead wires': 1.26,
    'Through-hole PGA': 1.00,
    'Surface-mounted LCCC': 2.25,
    'Surface-mounted chip carrier, J / gull-wing wires': 1.26,
    'Surface-mounted BGA': 1.75,
    'Fine-pitch surface-mounted axial leads': 0.75,
    'Two parallel rows of wires (hybrid, VLSI, ASIC, MCM)': 1.26,
    'Not sure (conservative)': 2.25,
}

# Relative position factors.
POSITION_R = {
    'Center of PCB': 1.0,
    'Near edge (half point X, quarter point Y)': 0.707,
    'Near corner (quarter point X and Y)': 0.5,
    'Not sure (conservative)': 1.0,
}

MM_PER_IN = 25.4


def z_limits(B, L, h, C, r):
    """Return (Z_3sigma, Z_peak) in inches.

    B, L, h in inches; C and r dimensionless. Raises ValueError on
    non-physical input.
    """
    for name, val in (('B', B), ('L', L), ('h', h), ('C', C), ('r', r)):
        if val <= 0:
            raise ValueError(f'{name} must be positive, got {val}')
    denom = C * h * r * math.sqrt(L)
    return 0.00022 * B / denom, 0.00132 * B / denom


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(
        description='Steinberg displacement limits (20 Mcycles).')
    p.add_argument('-B', type=float, required=True, help='PCB edge length, in')
    p.add_argument('-L', type=float, required=True, help='component length, in')
    p.add_argument('-t', type=float, required=True, help='board thickness, in')
    p.add_argument('-C', type=float, default=2.25,
                   help='component constant (default 2.25, conservative)')
    p.add_argument('-r', type=float, default=1.0,
                   help='position factor (default 1.0, conservative)')
    a = p.parse_args()
    zv, zs = z_limits(a.B, a.L, a.t, a.C, a.r)
    print(f'Z_3sigma (random vibration): {zv:.6f} in  = {zv*MM_PER_IN:.4f} mm')
    print(f'Z_peak   (shock)           : {zs:.6f} in  = {zs*MM_PER_IN:.4f} mm')


# ---------------------------------------------------------------- extensions

FATIGUE_EXPONENT = 6.4      # b in N * Z^b = const (Steinberg / Irvine)
N_REF = 20e6                # cycles at which z_limits applies


def z_limit_at_cycles(N, B, L, h, C, r):
    """Irvine's extension: allowable displacement at N cycles (vibration).

    Scales the 20-Mcycle limit along the fatigue curve N * Z^b = const
    with b = 6.4:   Z(N) = Z_ref * (N_ref / N) ** (1/b)
    """
    if N <= 0:
        raise ValueError('N must be positive')
    z_ref, _ = z_limits(B, L, h, C, r)
    return z_ref * (N_REF / N) ** (1.0 / FATIGUE_EXPONENT)


def grms_miles(fn, P, Q=None):
    """Miles' equation: G_rms response of the board at resonance.

    fn : natural frequency [Hz], P : input PSD at fn [G^2/Hz],
    Q  : transmissibility (default Steinberg's estimate Q = sqrt(fn)).
    """
    if Q is None:
        Q = math.sqrt(fn)
    return math.sqrt(math.pi / 2.0 * P * fn * Q)


def expected_z_random(fn, P, Q=None):
    """3-sigma expected relative displacement in random vibration [in].

    Z_rms = 9.8 * G_rms / fn^2  (inches, fn in Hz), reported at 3 sigma.
    """
    return 3.0 * 9.8 * grms_miles(fn, P, Q) / fn**2


def expected_z_shock(fn, G_peak):
    """Peak expected displacement for a shock of G_peak at fn [in]."""
    return 9.8 * G_peak / fn**2


def margin(z_limit, z_actual):
    """Margin of safety: MoS = limit/actual - 1 (>= 0 passes)."""
    return z_limit / z_actual - 1.0
