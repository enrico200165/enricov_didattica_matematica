# -*- coding: utf-8 -*-
"""
genera_esercizi_matematica_primo_liceo.py

Generatore di esercizi per il primo anno di liceo scientifico, con livelli
di difficolta' (1 = piu' facile, 5 = piu' difficile; il livello 3 corrisponde
alla difficolta' "storica" del programma originale, prima dell'introduzione
dei livelli).

Il programma genera, per ogni gruppo di esercizi e per ogni livello richiesto,
due file Markdown:
- un file con soli esercizi;
- un file con esercizi e soluzioni passo passo.

Dipendenze:
    py -m pip install sympy

Esempi:
    py genera_esercizi_matematica_primo_liceo.py --all --n 8
    py genera_esercizi_matematica_primo_liceo.py --chapters 1 2 6 G1 --n 10 --seed 123
    py genera_esercizi_matematica_primo_liceo.py --chapters 6 --levels 1 3 5 --n 5
    py genera_esercizi_matematica_primo_liceo.py --list
"""

from __future__ import annotations

import argparse
import math
import random
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from statistics import mean, median, multimode
from typing import Callable, Iterable

import sympy as sp

x, y, a, b = sp.symbols("x y a b")

LEVELS: list[int] = [1, 2, 3, 4, 5]


@dataclass(frozen=True)
class Exercise:
    text: str
    solution: str


@dataclass(frozen=True)
class Group:
    code: str
    title: str
    generator: Callable[[random.Random, int, int], list[Exercise]]


def s(expr) -> str:
    return sp.sstr(expr).replace("**", "^")


def frac_text(q: Fraction) -> str:
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def safe_slug(text: str) -> str:
    text = text.lower().replace("à", "a").replace("è", "e").replace("é", "e")
    text = text.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def random_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    if lo > hi:
        lo, hi = hi, lo
    value = 0
    while value == 0:
        value = rng.randint(lo, hi)
    return value


def lcm_int(a_: int, b_: int) -> int:
    return abs(a_ * b_) // math.gcd(a_, b_)


def divisors(n: int) -> list[int]:
    n = abs(n)
    return [d for d in range(1, n + 1) if n % d == 0]


def scale_range(level: int, base_lo: int, base_hi: int) -> tuple[int, int]:
    """Allarga o restringe l'intervallo [base_lo, base_hi] in base al livello.

    Il livello 3 restituisce l'intervallo originale (comportamento storico
    del programma). I livelli 1-2 lo restringono (esercizi piu' semplici),
    i livelli 4-5 lo allargano (numeri piu' grandi, calcoli piu' lunghi).
    """
    factor = 1 + (level - 3) * 0.35
    factor = max(0.3, factor)
    span = base_hi - base_lo
    new_span = max(2, round(span * factor))
    center = (base_hi + base_lo) / 2
    lo = int(round(center - new_span / 2))
    hi = int(round(center + new_span / 2))
    if lo >= hi:
        hi = lo + 1
    return lo, hi


def pick_choice(rng: random.Random, level: int, choices: list[str]) -> str:
    """Restringe il ventaglio di sottotipi di esercizio disponibili ai livelli
    piu' bassi. I sottotipi vanno elencati dal piu' semplice al piu' complesso:
    al livello 1 e' disponibile solo il primo, al livello 2 i primi due, e
    cosi' via, fino a tutti dal livello pari al numero di sottotipi in poi."""
    n = len(choices)
    n_allowed = min(n, max(1, level))
    return rng.choice(choices[:n_allowed])


def clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def write_group_files(
    group: Group, level: int, exercises: list[Exercise], out_dir: Path
) -> tuple[Path, Path]:
    base = f"{group.code}_{safe_slug(group.title)}_livello{level}"
    no_sol_dir = out_dir / "esercizi_senza_soluzioni"
    sol_dir = out_dir / "esercizi_con_soluzioni"
    no_sol_dir.mkdir(parents=True, exist_ok=True)
    sol_dir.mkdir(parents=True, exist_ok=True)

    no_sol_path = no_sol_dir / f"{base}_esercizi.md"
    sol_path = sol_dir / f"{base}_soluzioni.md"

    heading = f"# {group.code} - {group.title} (livello {level}/5)"
    no_sol_lines = [heading, "", "## Esercizi", ""]
    sol_lines = [heading, "", "## Esercizi e soluzioni", ""]

    for i, ex in enumerate(exercises, 1):
        no_sol_lines.append(f"{i}. {ex.text}")
        no_sol_lines.append("")
        sol_lines.append(f"## Esercizio {i}")
        sol_lines.append("")
        sol_lines.append(ex.text)
        sol_lines.append("")
        sol_lines.append("Soluzione passo passo:")
        sol_lines.append("")
        for line in ex.solution.splitlines():
            sol_lines.append(f"- {line}" if line else "")
        sol_lines.append("")

    no_sol_path.write_text("\n".join(no_sol_lines), encoding="utf-8")
    sol_path.write_text("\n".join(sol_lines), encoding="utf-8")
    return no_sol_path, sol_path


def gen_cap1(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    choices = ["expr", "mcd"]
    for _ in range(n):
        choice = pick_choice(rng, level, choices)
        if choice == "expr":
            lo, hi = scale_range(level, -12, 12)
            A, B, D = [rng.randint(lo, hi) for _ in range(3)]
            c_lo, c_hi = scale_range(level, -8, 8)
            C = random_nonzero(rng, c_lo, c_hi)
            expr = A + B * C - D
            text = f"Calcolare il valore dell'espressione: {A} + ({B}) · ({C}) - ({D})."
            sol = (
                f"Prima svolgere la moltiplicazione: ({B}) · ({C}) = {B*C}.\n"
                f"Sostituire nell'espressione: {A} + ({B*C}) - ({D}).\n"
                f"Calcolare da sinistra a destra: {A + B*C} - ({D}) = {expr}.\n"
                f"Risultato: {expr}."
            )
        else:
            lo, hi = scale_range(level, 12, 96)
            lo = max(6, lo)
            A, B = rng.randint(lo, hi), rng.randint(lo, hi)
            g = math.gcd(A, B)
            l = lcm_int(A, B)
            text = f"Determinare MCD e mcm di {A} e {B}."
            sol = (
                f"Divisori di {A}: {divisors(A)}.\n"
                f"Divisori di {B}: {divisors(B)}.\n"
                f"Il massimo divisore comune è {g}.\n"
                f"Usare la relazione mcm(a,b) = |a·b|/MCD(a,b).\n"
                f"mcm({A},{B}) = {A*B}/{g} = {l}."
            )
        out.append(Exercise(text, sol))
    return out


def gen_cap2(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    choices = ["fraction", "percent", "scientific"]
    for _ in range(n):
        choice = pick_choice(rng, level, choices)
        if choice == "fraction":
            d_lo, d_hi = scale_range(level, 2, 12)
            d_lo = max(2, d_lo)
            n_lo, n_hi = scale_range(level, 1, 9)
            n_lo = max(1, n_lo)
            q1 = Fraction(rng.randint(n_lo, n_hi), rng.randint(d_lo, d_hi))
            q2 = Fraction(rng.randint(n_lo, n_hi), rng.randint(d_lo, d_hi))
            op = rng.choice(["+", "-", "*"])
            res = q1 + q2 if op == "+" else q1 - q2 if op == "-" else q1 * q2
            text = f"Calcolare: {frac_text(q1)} {op} {frac_text(q2)}."
            if op in ["+", "-"]:
                den = lcm_int(q1.denominator, q2.denominator)
                a1 = q1.numerator * (den // q1.denominator)
                a2 = q2.numerator * (den // q2.denominator)
                sol = (
                    f"Trovare il denominatore comune: mcm({q1.denominator},{q2.denominator}) = {den}.\n"
                    f"Riscrivere le frazioni: {frac_text(q1)} = {a1}/{den}, {frac_text(q2)} = {a2}/{den}.\n"
                    f"Operare sui numeratori: {a1} {op} {a2} = {a1 + a2 if op == '+' else a1 - a2}.\n"
                    f"Semplificare: {a1 + a2 if op == '+' else a1 - a2}/{den} = {frac_text(res)}."
                )
            else:
                sol = (
                    f"Moltiplicare i numeratori: {q1.numerator} · {q2.numerator} = {q1.numerator*q2.numerator}.\n"
                    f"Moltiplicare i denominatori: {q1.denominator} · {q2.denominator} = {q1.denominator*q2.denominator}.\n"
                    f"Semplificare la frazione ottenuta: {frac_text(res)}."
                )
        elif choice == "percent":
            if level <= 2:
                perc_pool = [10, 20, 25, 50]
                base_pool = [40, 80, 100, 120]
            elif level == 3:
                perc_pool = [5, 10, 12, 15, 20, 25, 30, 40]
                base_pool = [80, 120, 150, 200, 240, 300]
            else:
                perc_pool = [7, 13, 17, 22, 35, 45, 55, 65, 75, 85]
                base_pool = [90, 140, 175, 225, 260, 320, 450]
            base = rng.choice(base_pool)
            perc = rng.choice(perc_pool)
            val = Fraction(base * perc, 100)
            text = f"Calcolare il {perc}% di {base}."
            sol = (
                f"Scrivere la percentuale come frazione: {perc}% = {perc}/100.\n"
                f"Moltiplicare: {base} · {perc}/100 = {base*perc}/100.\n"
                f"Semplificare: {frac_text(val)}."
            )
        else:
            exp_lo, exp_hi = scale_range(level, 3, 7)
            exp_lo = max(2, exp_lo)
            exp = rng.randint(exp_lo, exp_hi)
            coeff = rng.randint(12, 987)
            num = coeff * (10 ** exp)
            sci_coeff = coeff / 100
            text = f"Scrivere {num} in notazione scientifica."
            sol = (
                f"Spostare la virgola fino a ottenere un numero compreso tra 1 e 10: {sci_coeff}.\n"
                f"La virgola è stata spostata di {exp + 2} posizioni.\n"
                f"Risultato: {sci_coeff} · 10^{exp + 2}."
            )
        out.append(Exercise(text, sol))
    return out


def gen_cap3(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    choices = ["sets", "relation"]
    lo_size, hi_size = scale_range(level, 4, 7)
    lo_size = max(3, lo_size)
    universe_hi = clamp(12 + (level - 3) * 3, 8, 20)
    universe = set(range(1, universe_hi + 1))
    for _ in range(n):
        A = set(rng.sample(list(universe), clamp(rng.randint(lo_size, hi_size), 3, len(universe))))
        B = set(rng.sample(list(universe), clamp(rng.randint(lo_size, hi_size), 3, len(universe))))
        choice = pick_choice(rng, level, choices)
        if choice == "sets":
            text = f"Dati A = {sorted(A)} e B = {sorted(B)}, calcolare A ∪ B, A ∩ B e A - B."
            sol = (
                f"A ∪ B contiene tutti gli elementi presenti in A oppure in B: {sorted(A | B)}.\n"
                f"A ∩ B contiene solo gli elementi comuni: {sorted(A & B)}.\n"
                f"A - B contiene gli elementi di A che non appartengono a B: {sorted(A - B)}."
            )
        else:
            pairs = [(u, v) for u in sorted(A) for v in sorted(B) if (u + v) % rng.choice([2, 3]) == 0]
            text = f"Dati A = {sorted(A)} e B = {sorted(B)}, considerare la relazione R da A a B definita da 'a+b è divisibile'. Elencare alcune coppie ordinate di R e dire se R è una funzione."
            sol = (
                f"Le coppie ordinate che soddisfano la regola sono: {pairs[:12]}{' ...' if len(pairs) > 12 else ''}.\n"
                "Una relazione da A a B è funzione solo se ogni elemento di A ha una e una sola immagine in B.\n"
                "In questo caso, in generale, uno stesso elemento di A può essere collegato a più elementi di B oppure a nessuno.\n"
                "Quindi la relazione non è necessariamente una funzione; controllare le coppie elencate per il caso specifico."
            )
        out.append(Exercise(text, sol))
    return out


def gen_cap4(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    choices = ["sum", "product", "mcd_lcm"]
    for _ in range(n):
        choice = pick_choice(rng, level, choices)
        exp_lo, exp_hi = scale_range(level, 1, 4)
        exp_lo = max(1, exp_lo)
        if choice == "sum":
            c_lo, c_hi = scale_range(level, -9, 9)
            c1, c2 = random_nonzero(rng, c_lo, c_hi), random_nonzero(rng, c_lo, c_hi)
            px, py = rng.randint(exp_lo, exp_hi), rng.randint(0, exp_hi - 1)
            mono = x**px * y**py
            expr = c1 * mono + c2 * mono
            text = f"Semplificare la somma di monomi simili: {s(c1*mono)} + {s(c2*mono)}."
            sol = (
                "I monomi sono simili perché hanno la stessa parte letterale.\n"
                f"Somma dei coefficienti: {c1} + ({c2}) = {c1+c2}.\n"
                f"La parte letterale resta invariata: {s(mono)}.\n"
                f"Risultato: {s(sp.expand(expr))}."
            )
        elif choice == "product":
            c_lo, c_hi = scale_range(level, -6, 6)
            c1, c2 = random_nonzero(rng, c_lo, c_hi), random_nonzero(rng, c_lo, c_hi)
            m1 = c1 * x**rng.randint(1, exp_hi) * y**rng.randint(0, exp_hi - 1)
            m2 = c2 * x**rng.randint(0, exp_hi) * y**rng.randint(1, exp_hi)
            res = sp.expand(m1 * m2)
            text = f"Calcolare il prodotto: ({s(m1)}) · ({s(m2)})."
            sol = (
                "Moltiplicare i coefficienti.\n"
                "Per le potenze con la stessa base, sommare gli esponenti.\n"
                f"Prodotto sviluppato: {s(res)}."
            )
        else:
            c_lo, c_hi = scale_range(level, 2, 12)
            c_lo = max(2, c_lo)
            c1, c2 = rng.randint(c_lo, c_hi), rng.randint(c_lo, c_hi)
            p1, p2 = rng.randint(1, exp_hi), rng.randint(1, exp_hi)
            q1, q2 = rng.randint(0, exp_hi), rng.randint(0, exp_hi)
            m1, m2 = c1*x**p1*y**q1, c2*x**p2*y**q2
            coeff_gcd = math.gcd(c1, c2)
            coeff_lcm = lcm_int(c1, c2)
            mcd = coeff_gcd * x**min(p1, p2) * y**min(q1, q2)
            mcm = coeff_lcm * x**max(p1, p2) * y**max(q1, q2)
            text = f"Determinare MCD e mcm dei monomi {s(m1)} e {s(m2)}."
            sol = (
                f"MCD: MCD dei coefficienti = {coeff_gcd}; per le lettere prendere gli esponenti minimi.\n"
                f"MCD = {s(mcd)}.\n"
                f"mcm: mcm dei coefficienti = {coeff_lcm}; per le lettere prendere gli esponenti massimi.\n"
                f"mcm = {s(mcm)}."
            )
        out.append(Exercise(text, sol))
    return out


def gen_cap5(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    choices = ["expand", "notable"]
    for _ in range(n):
        choice = pick_choice(rng, level, choices)
        c_lo, c_hi = scale_range(level, -5, 5)
        A, B, C, D = [random_nonzero(rng, c_lo, c_hi) for _ in range(4)]
        if choice == "expand":
            p = A*x + B
            q = C*x + D
            res = sp.expand(p*q)
            text = f"Sviluppare il prodotto tra polinomi: ({s(p)})({s(q)})."
            sol = (
                "Applicare la proprietà distributiva: ogni termine del primo polinomio moltiplica ogni termine del secondo.\n"
                f"Prodotti parziali: ({A}x)({C}x), ({A}x)({D}), ({B})({C}x), ({B})({D}).\n"
                f"Somma dei prodotti parziali e riduzione dei termini simili: {s(res)}."
            )
        else:
            p = A*x + B*y
            res = sp.expand(p**2)
            text = f"Sviluppare il quadrato di binomio: ({s(p)})^2."
            sol = (
                "Usare la formula (u+v)^2 = u^2 + 2uv + v^2.\n"
                f"Qui u = {A}x e v = {B}y.\n"
                f"Risultato: {s(res)}."
            )
        out.append(Exercise(text, sol))
    return out


def gen_cap6(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        if level <= 3:
            c_lo, c_hi = scale_range(level, -8, 8)
            A = random_nonzero(rng, c_lo, c_hi)
            C = random_nonzero(rng, c_lo, c_hi)
            while A == C:
                C = random_nonzero(rng, c_lo, c_hi)
            k_lo, k_hi = scale_range(level, -20, 20)
            B, D = rng.randint(k_lo, k_hi), rng.randint(k_lo, k_hi)
            sol_x = Fraction(D - B, A - C)
            text = f"Risolvere l'equazione: {A}x + ({B}) = {C}x + ({D})."
            sol = (
                f"Portare i termini con x a sinistra e i termini noti a destra: {A}x - {C}x = {D} - ({B}).\n"
                f"Ridurre: {A-C}x = {D-B}.\n"
                f"Dividere per {A-C}: x = ({D-B})/({A-C}).\n"
                f"Risultato: x = {frac_text(sol_x)}."
            )
        else:
            # Livelli 4-5: equazione con parentesi da sviluppare prima di ridurre.
            c_lo, c_hi = scale_range(level, -6, 6)
            A = random_nonzero(rng, c_lo, c_hi)
            C = random_nonzero(rng, c_lo, c_hi)
            P, Q = rng.randint(-6, 6), rng.randint(-6, 6)
            E = random_nonzero(rng, -5, 5)
            D_extra = rng.randint(-10, 10)
            left = sp.expand(A * (x + P) + E * x)
            right = sp.expand(C * (x + Q) + D_extra)
            sol_list = sp.solve(sp.Eq(left, right), x)
            sol_x_val = sol_list[0] if sol_list else None
            text = (
                f"Risolvere l'equazione: {A}(x + ({P})) + {E}x = {C}(x + ({Q})) + ({D_extra})."
            )
            sol = (
                "Sviluppare le parentesi a sinistra e a destra.\n"
                f"Membro sinistro sviluppato: {s(left)}.\n"
                f"Membro destro sviluppato: {s(right)}.\n"
                "Portare i termini con x a sinistra e i numeri a destra, poi dividere per il coefficiente di x.\n"
                f"Risultato: x = {s(sol_x_val)}."
            )
        out.append(Exercise(text, sol))
    return out


def gen_cap7(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        m_lo, m_hi = scale_range(level, -5, 5)
        m = random_nonzero(rng, m_lo, m_hi)
        q_lo, q_hi = scale_range(level, -8, 8)
        q = rng.randint(q_lo, q_hi)
        count = clamp(3 + (level - 3), 3, 6)
        pool_lo, pool_hi = scale_range(level, -4, 4)
        pool = list(range(pool_lo, pool_hi + 1))
        count = min(count, len(pool))
        values = sorted(rng.sample(pool, count))
        points = [(v, m*v + q) for v in values]
        text = f"Data la funzione lineare f(x) = {m}x + ({q}), calcolare f(x) per x = {values} e indicare coefficiente angolare e intercetta."
        sol = (
            f"Sostituire ogni valore di x nella formula f(x) = {m}x + ({q}).\n"
            f"Valori ottenuti: {points}.\n"
            f"Il coefficiente angolare è m = {m}.\n"
            f"L'intercetta sull'asse y è q = {q}, cioè il punto (0, {q})."
        )
        out.append(Exercise(text, sol))
    return out


def gen_cap8(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        lo, hi = scale_range(level, -5, 5)
        if level <= 3:
            r1, r2 = rng.randint(lo, hi), rng.randint(lo, hi)
            while r1 == 0 or r2 == 0:
                r1, r2 = rng.randint(lo, hi), rng.randint(lo, hi)
            poly = sp.expand((x - r1) * (x - r2) * rng.choice([1, 2, -1]))
        else:
            # Livelli 4-5: polinomio di terzo grado (tre radici) invece di secondo.
            r1, r2, r3 = [rng.randint(lo, hi) for _ in range(3)]
            while 0 in (r1, r2, r3):
                r1, r2, r3 = [rng.randint(lo, hi) for _ in range(3)]
            poly = sp.expand((x - r1) * (x - r2) * (x - r3))
        divisor = x - r1
        q, rem = sp.div(poly, divisor)
        text = f"Dividere il polinomio P(x) = {s(poly)} per D(x) = {s(divisor)} e poi scomporre P(x), se possibile."
        sol = (
            "Eseguire la divisione polinomiale P(x) : D(x).\n"
            f"Quoziente: {s(q)}.\n"
            f"Resto: {s(rem)}.\n"
            f"Poiché il resto è {s(rem)}, vale P(x) = ({s(divisor)})({s(q)}) + {s(rem)}.\n"
            f"Scomposizione: P(x) = {s(sp.factor(poly))}."
        )
        out.append(Exercise(text, sol))
    return out


def gen_cap9(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        lo, hi = scale_range(level, -5, 5)
        r1, r2 = rng.randint(lo, hi), rng.randint(lo, hi)
        while r1 == r2:
            r2 = rng.randint(lo, hi)
        extra_lo, extra_hi = scale_range(level, 1, 5)
        extra_lo = max(1, extra_lo)
        num = sp.expand((x - r1) * (x + rng.randint(extra_lo, extra_hi)))
        den = sp.expand((x - r1) * (x - r2))
        simp = sp.cancel(num / den)
        text = f"Semplificare la frazione algebrica ({s(num)}) / ({s(den)}) e indicare le condizioni di esistenza."
        sol = (
            f"Scomporre numeratore e denominatore: numeratore = {s(sp.factor(num))}, denominatore = {s(sp.factor(den))}.\n"
            f"Le condizioni di esistenza si ottengono imponendo il denominatore diverso da zero: x ≠ {r1}, x ≠ {r2}.\n"
            "Semplificare il fattore comune, senza dimenticare le condizioni di esistenza.\n"
            f"Frazione semplificata: {s(simp)}."
        )
        out.append(Exercise(text, sol))
    return out


def gen_cap10(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        sign = rng.choice([">", "<"])
        if level <= 3:
            c_lo, c_hi = scale_range(level, -8, 8)
            A = random_nonzero(rng, c_lo, c_hi)
            k_lo, k_hi = scale_range(level, -12, 12)
            B, C = rng.randint(k_lo, k_hi), rng.randint(k_lo, k_hi)
            threshold = Fraction(C - B, A)
            final_sign = sign if A > 0 else ("<" if sign == ">" else ">")
            text = f"Risolvere la disequazione: {A}x + ({B}) {sign} {C}."
            sol = (
                f"Isolare il termine con x: {A}x {sign} {C} - ({B}) = {C-B}.\n"
                f"Dividere per {A}.\n"
                "Se si divide per un numero negativo, il verso della disequazione cambia.\n"
                f"Risultato: x {final_sign} {frac_text(threshold)}."
            )
        else:
            # Livelli 4-5: disequazione con parentesi da sviluppare prima di isolare x.
            c_lo, c_hi = scale_range(level, -6, 6)
            A = random_nonzero(rng, c_lo, c_hi)
            P = rng.randint(-6, 6)
            C = rng.randint(-15, 15)
            left = sp.expand(A * (x + P))
            const_term = A * P
            rhs = C - const_term
            final_sign = sign if A > 0 else ("<" if sign == ">" else ">")
            threshold = Fraction(rhs, A)
            text = f"Risolvere la disequazione: {A}(x + ({P})) {sign} {C}."
            sol = (
                f"Sviluppare la parentesi: {s(left)} {sign} {C}.\n"
                f"Isolare il termine con x: {A}x {sign} {rhs}.\n"
                "Dividere per il coefficiente di x; se è negativo il verso della disequazione si inverte.\n"
                f"Risultato: x {final_sign} {frac_text(threshold)}."
            )
        out.append(Exercise(text, sol))
    return out


def gen_cap11(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        size_lo = 8 + (level - 1) * 2
        size_hi = size_lo + 5
        lo, hi = scale_range(level, 1, 12)
        lo = max(1, lo)
        data = [rng.randint(lo, hi) for _ in range(rng.randint(size_lo, size_hi))]
        freq = {v: data.count(v) for v in sorted(set(data))}
        modes = multimode(data)
        text = f"Dato il campione statistico {data}, costruire la tabella delle frequenze e calcolare media, mediana, moda e campo di variazione."
        sol = (
            f"Ordinare i dati: {sorted(data)}.\n"
            f"Tabella delle frequenze assolute: {freq}.\n"
            f"Media = somma dei dati / numero dei dati = {sum(data)} / {len(data)} = {mean(data):.2f}.\n"
            f"Mediana = valore centrale dei dati ordinati = {median(data)}.\n"
            f"Moda = valore o valori più frequenti = {modes}.\n"
            f"Campo di variazione = massimo - minimo = {max(data)} - {min(data)} = {max(data)-min(data)}."
        )
        out.append(Exercise(text, sol))
    return out


def gen_g1(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        lo, hi = scale_range(level, 4, 30)
        lo = max(2, lo)
        AB = rng.randint(lo, hi)
        BC = rng.randint(lo, hi)
        k_lo, k_hi = scale_range(level, 2, 5)
        k_lo = max(2, k_lo)
        k = rng.randint(k_lo, k_hi)
        if level <= 3:
            text = f"Su una stessa retta sono dati due segmenti consecutivi AB = {AB} cm e BC = {BC} cm. Calcolare AC e il segmento lungo {k} volte AC."
            sol = (
                "Poiché i segmenti sono consecutivi sulla stessa retta, AC = AB + BC.\n"
                f"AC = {AB} + {BC} = {AB + BC} cm.\n"
                f"Il segmento richiesto misura {k} · {AB + BC} = {k*(AB+BC)} cm."
            )
        else:
            # Livelli 4-5: tre segmenti consecutivi invece di due.
            CD = rng.randint(lo, hi)
            text = f"Su una stessa retta sono dati tre segmenti consecutivi AB = {AB} cm, BC = {BC} cm e CD = {CD} cm. Calcolare AD e il segmento lungo {k} volte AD."
            sol = (
                "Poiché i segmenti sono consecutivi sulla stessa retta, AD = AB + BC + CD.\n"
                f"AD = {AB} + {BC} + {CD} = {AB + BC + CD} cm.\n"
                f"Il segmento richiesto misura {k} · {AB + BC + CD} = {k*(AB+BC+CD)} cm."
            )
        out.append(Exercise(text, sol))
    return out


def gen_g2(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        if level <= 3:
            lo, hi = scale_range(level, 30, 75)
            lo = clamp(lo, 1, 88)
            hi = clamp(hi, lo + 1, 89)
            angle = rng.randint(lo, hi)
            vertex = 180 - 2 * angle
            text = f"In un triangolo isoscele gli angoli alla base misurano ciascuno {angle}°. Calcolare l'angolo al vertice e indicare la proprietà usata."
            sol = (
                "In un triangolo la somma degli angoli interni è 180°.\n"
                "In un triangolo isoscele gli angoli alla base sono congruenti.\n"
                f"Angolo al vertice = 180° - 2 · {angle}° = {vertex}°."
            )
        else:
            # Livelli 4-5: triangolo qualsiasi con due angoli dati, da classificare.
            a1 = rng.randint(20, 90)
            a2 = rng.randint(20, 90)
            while a1 + a2 >= 170:
                a1 = rng.randint(20, 90)
                a2 = rng.randint(20, 90)
            a3 = 180 - a1 - a2
            largest = max(a1, a2, a3)
            if largest == 90:
                classification = "rettangolo"
            elif largest > 90:
                classification = "ottusangolo"
            else:
                classification = "acutangolo"
            text = f"In un triangolo due angoli interni misurano {a1}° e {a2}°. Calcolare il terzo angolo e stabilire se il triangolo è acutangolo, rettangolo o ottusangolo."
            sol = (
                "In un triangolo la somma degli angoli interni è 180°.\n"
                f"Terzo angolo = 180° - {a1}° - {a2}° = {a3}°.\n"
                f"L'angolo più grande tra i tre è {largest}°, quindi il triangolo è {classification}."
            )
        out.append(Exercise(text, sol))
    return out


def gen_g3(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        lo, hi = scale_range(level, 35, 145)
        lo = clamp(lo, 1, 178)
        hi = clamp(hi, lo + 1, 179)
        alpha = rng.randint(lo, hi)
        if level <= 3:
            text = f"Due rette parallele sono tagliate da una trasversale. Un angolo misura {alpha}°. Calcolare l'angolo corrispondente e l'angolo adiacente supplementare."
            sol = (
                "Con due rette parallele tagliate da una trasversale, gli angoli corrispondenti sono congruenti.\n"
                f"L'angolo corrispondente misura quindi {alpha}°.\n"
                "Due angoli adiacenti su una retta sono supplementari.\n"
                f"Angolo adiacente = 180° - {alpha}° = {180-alpha}°."
            )
        else:
            # Livelli 4-5: richiede anche l'angolo alterno interno e il coniugato interno.
            text = f"Due rette parallele sono tagliate da una trasversale. Un angolo misura {alpha}°. Calcolare l'angolo corrispondente, l'angolo alterno interno e l'angolo coniugato interno (supplementare)."
            sol = (
                "Con due rette parallele tagliate da una trasversale, gli angoli corrispondenti sono congruenti.\n"
                f"L'angolo corrispondente misura {alpha}°.\n"
                "Anche gli angoli alterni interni sono congruenti tra loro.\n"
                f"L'angolo alterno interno misura quindi {alpha}°.\n"
                "Gli angoli coniugati interni sono invece supplementari (la loro somma è 180°).\n"
                f"L'angolo coniugato interno misura 180° - {alpha}° = {180-alpha}°."
            )
        out.append(Exercise(text, sol))
    return out


def gen_g4(rng: random.Random, n: int, level: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        b1_lo, b1_hi = scale_range(level, 20, 60)
        b1_lo = max(12, b1_lo)
        b1 = rng.randint(b1_lo, b1_hi)
        b2_hi = max(b1 - 2, 11)
        b2_lo, _ = scale_range(level, 10, b2_hi)
        b2_lo = clamp(b2_lo, 5, b2_hi - 1)
        b2 = rng.randint(b2_lo, b2_hi)
        s_lo, s_hi = scale_range(level, 8, 30)
        s_lo = max(4, s_lo)
        side = rng.randint(s_lo, s_hi)
        per = b1 + b2 + 2 * side
        if level <= 3:
            text = f"Un trapezio isoscele ha base maggiore {b1} cm, base minore {b2} cm e lato obliquo {side} cm. Calcolare il perimetro e indicare perché i due lati obliqui sono uguali."
            sol = (
                "In un trapezio isoscele i lati obliqui sono congruenti per definizione.\n"
                f"Il perimetro è la somma dei lati: {b1} + {b2} + {side} + {side}.\n"
                f"Perimetro = {per} cm."
            )
        else:
            # Livelli 4-5: viene chiesta anche l'area, nota l'altezza.
            h = rng.randint(6, 20)
            area = Fraction((b1 + b2) * h, 2)
            text = f"Un trapezio isoscele ha base maggiore {b1} cm, base minore {b2} cm, lato obliquo {side} cm e altezza {h} cm. Calcolare perimetro e area."
            sol = (
                "In un trapezio isoscele i lati obliqui sono congruenti per definizione.\n"
                f"Perimetro = {b1} + {b2} + {side} + {side} = {per} cm.\n"
                "L'area di un trapezio si calcola con la formula (base maggiore + base minore) · altezza / 2.\n"
                f"Area = ({b1} + {b2}) · {h} / 2 = {frac_text(area)} cm^2."
            )
        out.append(Exercise(text, sol))
    return out


GROUPS: list[Group] = [
    Group("cap01", "Numeri naturali e numeri interi", gen_cap1),
    Group("cap02", "Numeri razionali e numeri reali", gen_cap2),
    Group("cap03", "Insiemi, logica e relazioni", gen_cap3),
    Group("cap04", "Monomi", gen_cap4),
    Group("cap05", "Polinomi", gen_cap5),
    Group("cap06", "Equazioni lineari", gen_cap6),
    Group("cap07", "Funzioni", gen_cap7),
    Group("cap08", "Divisione tra polinomi e scomposizione in fattori", gen_cap8),
    Group("cap09", "Frazioni algebriche ed equazioni fratte e letterali", gen_cap9),
    Group("cap10", "Disequazioni lineari", gen_cap10),
    Group("cap11", "Statistica", gen_cap11),
    Group("G1", "Enti geometrici fondamentali", gen_g1),
    Group("G2", "Triangoli", gen_g2),
    Group("G3", "Rette perpendicolari e rette parallele", gen_g3),
    Group("G4", "Parallelogrammi e trapezi", gen_g4),
]


def normalize_code(code: str) -> str:
    c = code.strip().lower()
    if c.startswith("cap"):
        number = int(re.sub(r"[^0-9]", "", c))
        return f"cap{number:02d}"
    if c.isdigit():
        return f"cap{int(c):02d}"
    if c in {"g1", "g2", "g3", "g4"}:
        return c.upper()
    raise ValueError(f"Codice capitolo non riconosciuto: {code}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera esercizi di matematica per primo liceo.")
    parser.add_argument("--out-dir", default="output_esercizi_matematica", help="Cartella di output.")
    parser.add_argument("--n", type=int, default=8, help="Numero di esercizi per gruppo e per livello.")
    parser.add_argument("--seed", type=int, default=None, help="Seed casuale per risultati riproducibili.")
    parser.add_argument("--all", action="store_true", help="Genera tutti i gruppi.")
    parser.add_argument("--chapters", nargs="*", default=[], help="Capitoli da generare: 1 2 6 G1, oppure cap01 cap02.")
    parser.add_argument(
        "--levels",
        nargs="*",
        type=int,
        default=LEVELS,
        help="Livelli di difficoltà da generare, tra 1 (più facile) e 5 (più difficile). Default: tutti (1 2 3 4 5).",
    )
    parser.add_argument("--list", action="store_true", help="Mostra i gruppi disponibili.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list:
        for group in GROUPS:
            print(f"{group.code}\t{group.title}")
        return 0

    group_by_code = {g.code.lower(): g for g in GROUPS}

    if args.all or not args.chapters:
        selected = GROUPS
    else:
        selected = []
        for raw_code in args.chapters:
            code = normalize_code(raw_code)
            selected.append(group_by_code[code.lower()])

    levels = sorted(set(args.levels))
    for lv in levels:
        if lv not in LEVELS:
            raise ValueError(f"Livello non valido: {lv}. Usare valori tra 1 e 5.")

    rng = random.Random(args.seed)
    out_dir = Path(args.out_dir)
    generated: list[tuple[Path, Path]] = []

    for group in selected:
        for level in levels:
            exercises = group.generator(rng, args.n, level)
            generated.append(write_group_files(group, level, exercises, out_dir))

    print(f"Generati {len(generated)} file di gruppo/livello in: {out_dir.resolve()}")
    for no_sol, sol in generated:
        print(f"- {no_sol}")
        print(f"- {sol}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
