"""
Steinberg displacement-limit calculator GUI.

Enter the board and component dimensions, pick the component type and its
position on the board from the dropdowns (both default to the conservative
choice), and the vibration and shock limits update live in inches and mm.

Run:  python steinberg_gui.py
"""

import tkinter as tk
from tkinter import ttk

from steinberg import (COMPONENT_C, POSITION_R, z_limits, MM_PER_IN,
                       z_limit_at_cycles, expected_z_random,
                       expected_z_shock, margin, N_REF)


class SteinbergGUI:
    def __init__(self, root):
        self.root = root
        root.title('Steinberg Displacement Limits (20 Mcycles)')
        root.resizable(False, False)
        pad = dict(padx=8, pady=4)

        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky='nsew')

        # --- numeric inputs ---
        self.vars = {}
        rows = [('B — PCB edge parallel to component (in)', 'B', '6.0'),
                ('L — component length (in)', 'L', '2.0'),
                ('h — board thickness (in)', 'h', '0.062'),
                ('N — design life, stress cycles', 'N', '20e6'),
                ('fn — board natural frequency (Hz), optional', 'fn', ''),
                ('PSD at fn (G²/Hz), optional', 'P', ''),
                ('Q — transmissibility (blank = √fn)', 'Q', ''),
                ('G peak — shock level (G), optional', 'G', '')]
        for i, (label, key, default) in enumerate(rows):
            ttk.Label(frm, text=label).grid(row=i, column=0, sticky='w', **pad)
            v = tk.StringVar(value=default)
            v.trace_add('write', lambda *a: self.update())
            ttk.Entry(frm, textvariable=v, width=10,
                      justify='right').grid(row=i, column=1, **pad)
            self.vars[key] = v

        # --- dropdowns ---
        ttk.Label(frm, text='Component type (sets C)'
                  ).grid(row=8, column=0, sticky='w', **pad)
        self.comp = tk.StringVar(value='Not sure (conservative)')
        cb1 = ttk.Combobox(frm, textvariable=self.comp, state='readonly',
                           values=list(COMPONENT_C), width=44)
        cb1.grid(row=8, column=1, **pad)
        cb1.bind('<<ComboboxSelected>>', lambda e: self.update())

        ttk.Label(frm, text='Component position (sets r)'
                  ).grid(row=9, column=0, sticky='w', **pad)
        self.pos = tk.StringVar(value='Not sure (conservative)')
        cb2 = ttk.Combobox(frm, textvariable=self.pos, state='readonly',
                           values=list(POSITION_R), width=44)
        cb2.grid(row=9, column=1, **pad)
        cb2.bind('<<ComboboxSelected>>', lambda e: self.update())

        # --- constants echo ---
        self.cr_label = ttk.Label(frm, text='', foreground='#555')
        self.cr_label.grid(row=10, column=0, columnspan=2, sticky='w', **pad)

        # --- results ---
        sep = ttk.Separator(frm, orient='horizontal')
        sep.grid(row=11, column=0, columnspan=2, sticky='ew', pady=6)
        self.out_vib = ttk.Label(frm, text='', font=('Helvetica', 13, 'bold'))
        self.out_vib.grid(row=12, column=0, columnspan=2, sticky='w', **pad)
        self.out_shk = ttk.Label(frm, text='', font=('Helvetica', 13, 'bold'))
        self.out_shk.grid(row=13, column=0, columnspan=2, sticky='w', **pad)
        self.out_mv = ttk.Label(frm, text='')
        self.out_mv.grid(row=14, column=0, columnspan=2, sticky='w', **pad)
        self.out_ms = ttk.Label(frm, text='')
        self.out_ms.grid(row=15, column=0, columnspan=2, sticky='w', **pad)
        self.err = ttk.Label(frm, text='', foreground='#b00')
        self.err.grid(row=16, column=0, columnspan=2, sticky='w', **pad)

        self.update()

    def update(self):
        try:
            B = float(self.vars['B'].get())
            L = float(self.vars['L'].get())
            h = float(self.vars['h'].get())
            N = float(self.vars['N'].get() or N_REF)
            C = COMPONENT_C[self.comp.get()]
            r = POSITION_R[self.pos.get()]
            _, zs = z_limits(B, L, h, C, r)
            zv = z_limit_at_cycles(N, B, L, h, C, r)
        except (ValueError, KeyError) as e:
            self.out_vib.config(text='')
            self.out_shk.config(text='')
            self.err.config(text=f'Check inputs: {e}')
            return
        self.err.config(text='')
        self.cr_label.config(text=f'C = {C}    r = {r}')
        self.out_vib.config(
            text=f'Z 3σ limit (random vibration):  {zv:.6f} in   '
                 f'=  {zv*MM_PER_IN:.4f} mm')
        self.out_shk.config(
            text=f'Z peak (shock):                 {zs:.6f} in   '
                 f'=  {zs*MM_PER_IN:.4f} mm')

        # optional margin of safety
        def _opt(key):
            s = self.vars[key].get().strip()
            return float(s) if s else None
        try:
            fn, P, Q, G = _opt('fn'), _opt('P'), _opt('Q'), _opt('G')
        except ValueError:
            fn = P = Q = G = None
        if fn and P:
            za = expected_z_random(fn, P, Q)
            m = margin(zv, za)
            self.out_mv.config(
                text=f'Vibration MoS: expected 3σ Z = {za:.6f} in  →  '
                     f'{m:+.2f}  {"PASS" if m >= 0 else "FAIL"}',
                foreground='#0a7a2f' if m >= 0 else '#b00020')
        else:
            self.out_mv.config(text='')
        if fn and G:
            zshk = expected_z_shock(fn, G)
            m = margin(zs, zshk)
            self.out_ms.config(
                text=f'Shock MoS:     expected Z = {zshk:.6f} in  →  '
                     f'{m:+.2f}  {"PASS" if m >= 0 else "FAIL"}',
                foreground='#0a7a2f' if m >= 0 else '#b00020')
        else:
            self.out_ms.config(text='')


if __name__ == '__main__':
    root = tk.Tk()
    SteinbergGUI(root)
    root.mainloop()
