# -*- coding: utf-8 -*-
"""
genera_esercizi_matematica_primo_liceo.py

Generatore di esercizi per il primo anno di liceo scientifico.

Il programma genera, per ogni gruppo di esercizi, due file Markdown:
- un file con soli esercizi;
- un file con esercizi e soluzioni passo passo.

Dipendenze:
    py -m pip install sympy

Esempi:
    py genera_esercizi_matematica_primo_liceo.py --all --n 8
    py genera_esercizi_matematica_primo_liceo.py --chapters 1 2 6 G1 --n 10 --seed 123
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


@dataclass(frozen=True)
class Exercise:
    text: str
    solution: str


@dataclass(frozen=True)
class Group:
    code: str
    title: str
    generator: Callable[[random.Random, int], list[Exercise]]


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
    value = 0
    while value == 0:
        value = rng.randint(lo, hi)
    return value


def lcm_int(a_: int, b_: int) -> int:
    return abs(a_ * b_) // math.gcd(a_, b_)


def divisors(n: int) -> list[int]:
    n = abs(n)
    return [d for d in range(1, n + 1) if n % d == 0]


def write_group_files(group: Group, exercises: list[Exercise], out_dir: Path) -> tuple[Path, Path]:
    base = f"{group.code}_{safe_slug(group.title)}"
    no_sol_dir = out_dir / "esercizi_senza_soluzioni"
    sol_dir = out_dir / "esercizi_con_soluzioni"
    no_sol_dir.mkdir(parents=True, exist_ok=True)
    sol_dir.mkdir(parents=True, exist_ok=True)

    no_sol_path = no_sol_dir / f"{base}_esercizi.md"
    sol_path = sol_dir / f"{base}_soluzioni.md"

    no_sol_lines = [f"# {group.code} - {group.title}", "", "## Esercizi", ""]
    sol_lines = [f"# {group.code} - {group.title}", "", "## Esercizi e soluzioni", ""]

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


def gen_cap1(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        choice = rng.choice(["expr", "mcd"])
        if choice == "expr":
            A, B, C, D = [rng.randint(-12, 12) for _ in range(4)]
            C = random_nonzero(rng, -8, 8)
            expr = A + B * C - D
            text = f"Calcolare il valore dell'espressione: {A} + ({B}) · ({C}) - ({D})."
            sol = (
                f"Prima svolgere la moltiplicazione: ({B}) · ({C}) = {B*C}.\n"
                f"Sostituire nell'espressione: {A} + ({B*C}) - ({D}).\n"
                f"Calcolare da sinistra a destra: {A + B*C} - ({D}) = {expr}.\n"
                f"Risultato: {expr}."
            )
        else:
            A, B = rng.randint(12, 96), rng.randint(12, 96)
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


def gen_cap2(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        choice = rng.choice(["fraction", "percent", "scientific"])
        if choice == "fraction":
            q1 = Fraction(rng.randint(1, 9), rng.randint(2, 12))
            q2 = Fraction(rng.randint(1, 9), rng.randint(2, 12))
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
            base = rng.choice([80, 120, 150, 200, 240, 300])
            perc = rng.choice([5, 10, 12, 15, 20, 25, 30, 40])
            val = Fraction(base * perc, 100)
            text = f"Calcolare il {perc}% di {base}."
            sol = (
                f"Scrivere la percentuale come frazione: {perc}% = {perc}/100.\n"
                f"Moltiplicare: {base} · {perc}/100 = {base*perc}/100.\n"
                f"Semplificare: {frac_text(val)}."
            )
        else:
            coeff = rng.randint(12, 987)
            exp = rng.randint(3, 7)
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


def gen_cap3(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    universe = set(range(1, 13))
    for _ in range(n):
        A = set(rng.sample(list(universe), rng.randint(4, 7)))
        B = set(rng.sample(list(universe), rng.randint(4, 7)))
        choice = rng.choice(["sets", "relation"])
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


def gen_cap4(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    vars_ = [x, y]
    for _ in range(n):
        choice = rng.choice(["sum", "product", "mcd_lcm"])
        if choice == "sum":
            c1, c2 = random_nonzero(rng, -9, 9), random_nonzero(rng, -9, 9)
            px, py = rng.randint(1, 4), rng.randint(0, 3)
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
            c1, c2 = random_nonzero(rng, -6, 6), random_nonzero(rng, -6, 6)
            m1 = c1 * x**rng.randint(1, 3) * y**rng.randint(0, 2)
            m2 = c2 * x**rng.randint(0, 3) * y**rng.randint(1, 3)
            res = sp.expand(m1 * m2)
            text = f"Calcolare il prodotto: ({s(m1)}) · ({s(m2)})."
            sol = (
                "Moltiplicare i coefficienti.\n"
                "Per le potenze con la stessa base, sommare gli esponenti.\n"
                f"Prodotto sviluppato: {s(res)}."
            )
        else:
            c1, c2 = rng.randint(2, 12), rng.randint(2, 12)
            p1, p2 = rng.randint(1, 5), rng.randint(1, 5)
            q1, q2 = rng.randint(0, 4), rng.randint(0, 4)
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


def gen_cap5(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        choice = rng.choice(["expand", "notable"])
        A, B, C, D = [random_nonzero(rng, -5, 5) for _ in range(4)]
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


def gen_cap6(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        A = random_nonzero(rng, -8, 8)
        C = random_nonzero(rng, -8, 8)
        while A == C:
            C = random_nonzero(rng, -8, 8)
        B, D = rng.randint(-20, 20), rng.randint(-20, 20)
        sol_x = Fraction(D - B, A - C)
        text = f"Risolvere l'equazione: {A}x + ({B}) = {C}x + ({D})."
        sol = (
            f"Portare i termini con x a sinistra e i termini noti a destra: {A}x - {C}x = {D} - ({B}).\n"
            f"Ridurre: {A-C}x = {D-B}.\n"
            f"Dividere per {A-C}: x = ({D-B})/({A-C}).\n"
            f"Risultato: x = {frac_text(sol_x)}."
        )
        out.append(Exercise(text, sol))
    return out


def gen_cap7(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        m = random_nonzero(rng, -5, 5)
        q = rng.randint(-8, 8)
        values = sorted(rng.sample(range(-4, 5), 3))
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


def gen_cap8(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        r1, r2 = rng.randint(-5, 5), rng.randint(-5, 5)
        while r1 == 0 or r2 == 0:
            r1, r2 = rng.randint(-5, 5), rng.randint(-5, 5)
        poly = sp.expand((x - r1) * (x - r2) * rng.choice([1, 2, -1]))
        divisor = x - r1
        q, rem = sp.div(poly, divisor)
        text = f"Dividere il polinomio P(x) = {s(poly)} per D(x) = {s(divisor)} e poi scomporre P(x), se possibile."
        sol = (
            f"Eseguire la divisione polinomiale P(x) : D(x).\n"
            f"Quoziente: {s(q)}.\n"
            f"Resto: {s(rem)}.\n"
            f"Poiché il resto è {s(rem)}, vale P(x) = ({s(divisor)})({s(q)}) + {s(rem)}.\n"
            f"Scomposizione: P(x) = {s(sp.factor(poly))}."
        )
        out.append(Exercise(text, sol))
    return out


def gen_cap9(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        r1, r2 = rng.randint(-5, 5), rng.randint(-5, 5)
        while r1 == r2:
            r2 = rng.randint(-5, 5)
        num = sp.expand((x - r1) * (x + rng.randint(1, 5)))
        den = sp.expand((x - r1) * (x - r2))
        simp = sp.cancel(num / den)
        text = f"Semplificare la frazione algebrica ({s(num)}) / ({s(den)}) e indicare le condizioni di esistenza."
        sol = (
            f"Scomporre numeratore e denominatore: numeratore = {s(sp.factor(num))}, denominatore = {s(sp.factor(den))}.\n"
            f"Le condizioni di esistenza si ottengono imponendo il denominatore diverso da zero: x ≠ {r1}, x ≠ {r2}.\n"
            f"Semplificare il fattore comune, senza dimenticare le condizioni di esistenza.\n"
            f"Frazione semplificata: {s(simp)}."
        )
        out.append(Exercise(text, sol))
    return out


def gen_cap10(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        A = random_nonzero(rng, -8, 8)
        B = rng.randint(-12, 12)
        C = rng.randint(-12, 12)
        sign = rng.choice([">", "<"])
        threshold = Fraction(C - B, A)
        if A > 0:
            final_sign = sign
        else:
            final_sign = "<" if sign == ">" else ">"
        text = f"Risolvere la disequazione: {A}x + ({B}) {sign} {C}."
        sol = (
            f"Isolare il termine con x: {A}x {sign} {C} - ({B}) = {C-B}.\n"
            f"Dividere per {A}.\n"
            f"Se si divide per un numero negativo, il verso della disequazione cambia.\n"
            f"Risultato: x {final_sign} {frac_text(threshold)}."
        )
        out.append(Exercise(text, sol))
    return out


def gen_cap11(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        data = [rng.randint(1, 12) for _ in range(rng.randint(8, 13))]
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


def gen_g1(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        AB = rng.randint(4, 30)
        BC = rng.randint(4, 30)
        k = rng.randint(2, 5)
        text = f"Su una stessa retta sono dati due segmenti consecutivi AB = {AB} cm e BC = {BC} cm. Calcolare AC e il segmento lungo {k} volte AC."
        sol = (
            f"Poiché i segmenti sono consecutivi sulla stessa retta, AC = AB + BC.\n"
            f"AC = {AB} + {BC} = {AB + BC} cm.\n"
            f"Il segmento richiesto misura {k} · {AB + BC} = {k*(AB+BC)} cm."
        )
        out.append(Exercise(text, sol))
    return out


def gen_g2(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        angle = rng.randint(30, 75)
        vertex = 180 - 2 * angle
        text = f"In un triangolo isoscele gli angoli alla base misurano ciascuno {angle}°. Calcolare l'angolo al vertice e indicare la proprietà usata."
        sol = (
            "In un triangolo la somma degli angoli interni è 180°.\n"
            "In un triangolo isoscele gli angoli alla base sono congruenti.\n"
            f"Angolo al vertice = 180° - 2 · {angle}° = {vertex}°."
        )
        out.append(Exercise(text, sol))
    return out


def gen_g3(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        alpha = rng.randint(35, 145)
        text = f"Due rette parallele sono tagliate da una trasversale. Un angolo misura {alpha}°. Calcolare l'angolo corrispondente e l'angolo adiacente supplementare."
        sol = (
            "Con due rette parallele tagliate da una trasversale, gli angoli corrispondenti sono congruenti.\n"
            f"L'angolo corrispondente misura quindi {alpha}°.\n"
            "Due angoli adiacenti su una retta sono supplementari.\n"
            f"Angolo adiacente = 180° - {alpha}° = {180-alpha}°."
        )
        out.append(Exercise(text, sol))
    return out


def gen_g4(rng: random.Random, n: int) -> list[Exercise]:
    out: list[Exercise] = []
    for _ in range(n):
        b1 = rng.randint(20, 60)
        b2 = rng.randint(10, b1 - 2)
        side = rng.randint(8, 30)
        per = b1 + b2 + 2 * side
        text = f"Un trapezio isoscele ha base maggiore {b1} cm, base minore {b2} cm e lato obliquo {side} cm. Calcolare il perimetro e indicare perché i due lati obliqui sono uguali."
        sol = (
            "In un trapezio isoscele i lati obliqui sono congruenti per definizione.\n"
            f"Il perimetro è la somma dei lati: {b1} + {b2} + {side} + {side}.\n"
            f"Perimetro = {per} cm."
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
    parser.add_argument("--n", type=int, default=8, help="Numero di esercizi per gruppo.")
    parser.add_argument("--seed", type=int, default=None, help="Seed casuale per risultati riproducibili.")
    parser.add_argument("--all", action="store_true", help="Genera tutti i gruppi.")
    parser.add_argument("--chapters", nargs="*", default=[], help="Capitoli da generare: 1 2 6 G1, oppure cap01 cap02.")
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

    rng = random.Random(args.seed)
    out_dir = Path(args.out_dir)
    generated: list[tuple[Path, Path]] = []

    for group in selected:
        exercises = group.generator(rng, args.n)
        generated.append(write_group_files(group, exercises, out_dir))

    print(f"Generati {len(generated)} gruppi in: {out_dir.resolve()}")
    for no_sol, sol in generated:
        print(f"- {no_sol}")
        print(f"- {sol}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
