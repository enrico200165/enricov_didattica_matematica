# -*- coding: utf-8 -*-
"""
genera_esercizi_da_programma.py

Genera esercizi di matematica navigando l'indice di un libro di testo,
letto sempre dal file "programma_studio.md" (capitoli e lezioni), che deve
trovarsi nella cartella corrente.

Flusso:
  1. Viene letto e interpretato "programma_studio.md".
  2. Le parti del file che non corrispondono allo schema capitolo/lezione
     vengono segnalate a schermo (non sono lezioni, quindi non generano
     esercizi).
  3. L'utente sceglie UN capitolo da un menu.
  4. Nel capitolo scelto, l'utente sceglie UNA O PIU' lezioni.
  5. Per ciascuna lezione selezionata vengono generati N esercizi specifici
     di quella lezione (non genericamente del capitolo).
  6. Vengono scritti file Markdown con e senza soluzioni. Per default tutte
     le lezioni scelte finiscono in un unico file di ciascun tipo; con
     l'opzione --per-lezione si ottiene invece un file separato per
     ciascuna lezione. In entrambi i casi capitolo, lezione e pagina sono
     riportati esplicitamente.
  7. Ogni esercizio che contiene una formula matematica vera e propria
     riporta, su una riga separata, anche la stessa formula in LaTeX,
     chiaramente segnalata come versione aggiuntiva che potrebbe non
     essere visualizzata correttamente da chi legge il file.

Dipendenze:
    py -m pip install sympy   (oppure: python.exe -m pip install sympy)

Esempio:
    python genera_esercizi_da_programma.py --n 6 --seed 42
    python genera_esercizi_da_programma.py --per-lezione
"""

from __future__ import annotations

import argparse
import math
import random
import re
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from statistics import mean, median, multimode
from typing import Callable

import sympy as sp

x, y = sp.symbols("x y")

PROGRAM_FILENAME = "programma_studio.md"

LATEX_NOTE = (
    "Versione LaTeX della domanda qui sopra (duplicato aggiuntivo — "
    "potrebbe non essere visualizzata correttamente se il lettore non supporta LaTeX)"
)


# --------------------------------------------------------------------------
# Strutture dati
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Exercise:
    text: str
    solution: str
    latex: str = ""  # formula in LaTeX, duplicato del testo; "" se non applicabile


@dataclass
class Lesson:
    number: int
    title: str
    page: str | None


@dataclass
class Chapter:
    code: str  # cosi' come compare nel file: "1", "G1", "online", ...
    title: str
    lessons: list[Lesson] = field(default_factory=list)


@dataclass
class AccessoryItem:
    context: str
    text: str
    reason: str


# --------------------------------------------------------------------------
# Helper matematici e di formattazione (in comune fra i generatori)
# --------------------------------------------------------------------------

def s(expr) -> str:
    return sp.sstr(expr).replace("**", "^")


def frac_text(q: Fraction) -> str:
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def latex_frac(q: Fraction) -> str:
    if q.denominator == 1:
        return str(q.numerator)
    sign = "-" if q.numerator < 0 else ""
    return f"{sign}\\frac{{{abs(q.numerator)}}}{{{q.denominator}}}"


def latex_deg(v) -> str:
    return f"{v}^{{\\circ}}"


def latex_x_minus(r) -> str:
    """Restituisce 'x - r' in LaTeX, gestendo il segno se r è negativo (evita 'x - -3')."""
    return f"x - {r}" if r >= 0 else f"x + {abs(r)}"


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


def is_finite_decimal(den: int) -> bool:
    d = den
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


# --------------------------------------------------------------------------
# Parsing di programma_studio.md
# --------------------------------------------------------------------------

CHAPTER_RE = re.compile(r"^##\s+Capitolo\s+(?P<code>\S+)(?:\s*-\s*(?P<title>.+))?$")
LESSON_RE = re.compile(r"^(?P<num>\d+)\.\s*(?P<title>.+?):\s*T:\s*(?P<page>\S+?)(?:\s*-|\s*$)")

ACTIVITY_PREFIXES = (
    "coding con python", "matematica per", "esplora con geogebra",
    "competenze alla prova", "accetti la sfida", "prova di verifica",
    "attività e approfondimenti",
)


def classify_accessory(text: str) -> str:
    low = text.lstrip("-").strip().lower()
    if low.startswith("riepilogo"):
        return "riepilogo di fine sezione, non è una lezione numerata"
    if low.startswith("teoria in sintesi"):
        return "sintesi finale del capitolo, non è una lezione"
    if low.startswith("disponibile su"):
        return "nota informativa: il capitolo non elenca lezioni numerate"
    if any(low.startswith(p) for p in ACTIVITY_PREFIXES):
        return "voce del blocco attività e approfondimenti, non è una lezione curricolare"
    return "non corrisponde al formato di una lezione numerata ('N. Titolo: T: ... - E: ...')"


def parse_programma(text: str) -> tuple[list[Chapter], list[AccessoryItem]]:
    chapters: list[Chapter] = []
    accessories: list[AccessoryItem] = []
    current_chapter: Chapter | None = None
    heading_context = "Prima dei capitoli"

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        if stripped.startswith("## "):
            m_chap = CHAPTER_RE.match(stripped)
            if m_chap:
                code = m_chap.group("code")
                title = (m_chap.group("title") or "").strip()
                current_chapter = Chapter(code=code, title=title)
                chapters.append(current_chapter)
                heading_context = f"Capitolo {code} - {title}" if title else f"Capitolo {code}"
            else:
                current_chapter = None
                heading_context = stripped[3:].strip()
                accessories.append(AccessoryItem(
                    context=heading_context,
                    text=stripped,
                    reason="intestazione di secondo livello che non segue lo schema 'Capitolo <codice> - <titolo>'",
                ))
            continue

        if stripped.startswith("# "):
            heading_context = "Prima dei capitoli"
            continue

        if current_chapter is not None:
            m_les = LESSON_RE.match(stripped)
            if m_les:
                current_chapter.lessons.append(Lesson(
                    number=int(m_les.group("num")),
                    title=m_les.group("title").strip(),
                    page=m_les.group("page"),
                ))
                continue

        display_text = stripped if len(stripped) <= 90 else stripped[:87] + "..."
        accessories.append(AccessoryItem(
            context=heading_context,
            text=display_text,
            reason=classify_accessory(stripped),
        ))

    return chapters, accessories


def print_accessory_report(accessories: list[AccessoryItem]) -> None:
    if not accessories:
        return
    print("\nContenuti del file non riconosciuti come capitoli o lezioni:")
    print("(vengono mostrati solo per trasparenza, non generano esercizi)\n")
    last_context = None
    for item in accessories:
        if item.context != last_context:
            print(f"[{item.context}]")
            last_context = item.context
        print(f"  - \"{item.text}\" -> {item.reason}")
    print()


# --------------------------------------------------------------------------
# Generatori di esercizi, uno per lezione
# --------------------------------------------------------------------------
# Ogni funzione ha la firma (rng: random.Random, n: int) -> list[Exercise].
# Le funzioni sono raggruppate per capitolo e nominate lez_<capitolo>_<lezione>.
# Il campo "latex" di ogni Exercise è la formula matematica dell'esercizio in
# LaTeX; resta vuoto quando l'esercizio non contiene una formula da duplicare
# (per esempio affermazioni vero/falso puramente verbali).

# ---- Capitolo 1 - Numeri naturali e numeri interi ----

def lez_1_1(rng, n):
    out = []
    for _ in range(n):
        nums = [rng.randint(0, 500) for _ in range(4)]
        text = f"Dati i numeri naturali {nums}, ordinarli in senso crescente e decrescente, poi calcolarne la somma."
        sol = (
            f"Ordine crescente: {sorted(nums)}.\n"
            f"Ordine decrescente: {sorted(nums, reverse=True)}.\n"
            f"Somma = {' + '.join(map(str, nums))} = {sum(nums)}."
        )
        latex = " + ".join(str(v) for v in nums) + f" = {sum(nums)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_1_2(rng, n):
    out = []
    for _ in range(n):
        a_, b_, c_ = [rng.randint(2, 20) for _ in range(3)]
        left = a_ * (b_ + c_)
        right = a_ * b_ + a_ * c_
        text = f"Verificare la proprietà distributiva calcolando {a_} · ({b_} + {c_}) in due modi diversi."
        sol = (
            f"Primo modo: {a_} · ({b_} + {c_}) = {a_} · {b_+c_} = {left}.\n"
            f"Secondo modo: {a_}·{b_} + {a_}·{c_} = {a_*b_} + {a_*c_} = {right}.\n"
            f"I due risultati coincidono: {left}."
        )
        latex = f"{a_}({b_}+{c_}) = {a_}\\cdot {b_} + {a_}\\cdot {c_} = {left}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_1_3(rng, n):
    out = []
    for _ in range(n):
        base = rng.randint(2, 9)
        choice = rng.choice(["prod", "quot", "pow"])
        if choice == "prod":
            e1, e2 = rng.randint(1, 6), rng.randint(1, 6)
            text = f"Semplificare applicando le proprietà delle potenze: {base}^{e1} · {base}^{e2}."
            sol = f"Nel prodotto di potenze con la stessa base si sommano gli esponenti.\n{base}^{e1} · {base}^{e2} = {base}^{e1+e2}."
            latex = f"{base}^{{{e1}}} \\cdot {base}^{{{e2}}} = {base}^{{{e1+e2}}}"
        elif choice == "quot":
            e1 = rng.randint(3, 8)
            e2 = rng.randint(1, e1 - 1)
            text = f"Semplificare applicando le proprietà delle potenze: {base}^{e1} : {base}^{e2}."
            sol = f"Nel quoziente di potenze con la stessa base si sottraggono gli esponenti.\n{base}^{e1} : {base}^{e2} = {base}^{e1-e2}."
            latex = f"{base}^{{{e1}}} \\div {base}^{{{e2}}} = {base}^{{{e1-e2}}}"
        else:
            e1, e2 = rng.randint(2, 4), rng.randint(2, 4)
            text = f"Semplificare applicando le proprietà delle potenze: ({base}^{e1})^{e2}."
            sol = f"Nella potenza di potenza si moltiplicano gli esponenti.\n({base}^{e1})^{e2} = {base}^{e1*e2}."
            latex = f"\\left({base}^{{{e1}}}\\right)^{{{e2}}} = {base}^{{{e1*e2}}}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_1_4(rng, n):
    out = []
    for _ in range(n):
        A, B = rng.randint(12, 96), rng.randint(12, 96)
        g = math.gcd(A, B)
        l = lcm_int(A, B)
        text = f"Determinare MCD e mcm di {A} e {B}."
        sol = (
            f"Divisori di {A}: {divisors(A)}.\n"
            f"Divisori di {B}: {divisors(B)}.\n"
            f"MCD({A},{B}) = {g}.\n"
            f"mcm({A},{B}) = {A}·{B}/{g} = {l}."
        )
        latex = f"\\gcd({A},{B})={g}, \\quad \\operatorname{{mcm}}({A},{B})={l}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_1_5(rng, n):
    out = []
    for _ in range(n):
        nums = [rng.randint(-30, 30) for _ in range(5)]
        text = f"Ordinare in senso crescente i seguenti numeri interi: {nums}."
        sol = (
            "Si confrontano prima i segni; tra due negativi è maggiore quello con valore assoluto minore.\n"
            f"Ordine crescente: {sorted(nums)}."
        )
        latex = " < ".join(str(v) for v in sorted(nums))
        out.append(Exercise(text, sol, latex))
    return out


def lez_1_6(rng, n):
    out = []
    for _ in range(n):
        A, B, D = [rng.randint(-12, 12) for _ in range(3)]
        C = random_nonzero(rng, -8, 8)
        expr = A + B * C - D
        text = f"Calcolare il valore dell'espressione in Z: {A} + ({B}) · ({C}) - ({D})."
        sol = (
            f"Prima la moltiplicazione: ({B})·({C}) = {B*C}.\n"
            f"Sostituendo: {A} + ({B*C}) - ({D}).\n"
            f"Da sinistra a destra: {A + B*C} - ({D}) = {expr}.\n"
            f"Risultato: {expr}."
        )
        latex = f"{A} + ({B}) \\cdot ({C}) - ({D}) = {expr}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_1_7(rng, n):
    out = []
    for _ in range(n):
        base = random_nonzero(rng, -9, 9)
        exp = rng.randint(2, 5)
        val = base ** exp
        segno = "positivo" if (base > 0 or exp % 2 == 0) else "negativo"
        text = f"Calcolare la potenza {base}^{exp}, stabilendo prima il segno del risultato."
        sol = (
            "Se la base è negativa, il risultato è positivo se l'esponente è pari, negativo se è dispari.\n"
            f"Base {base}, esponente {exp}: il risultato è {segno}.\n"
            f"{base}^{exp} = {val}."
        )
        latex = f"({base})^{{{exp}}} = {val}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 2 - Numeri razionali e numeri reali ----

def lez_2_1(rng, n):
    out = []
    for _ in range(n):
        num = rng.randint(-60, 60)
        den = random_nonzero(rng, 2, 24)
        q = Fraction(num, den)
        text = f"Scrivere la frazione {num}/{den} ridotta ai minimi termini."
        sol = (
            f"MCD(|{num}|, {den}) permette di semplificare numeratore e denominatore.\n"
            f"Frazione ridotta: {frac_text(q)}."
        )
        latex = f"\\frac{{{num}}}{{{den}}} = {latex_frac(q)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_2_2(rng, n):
    out = []
    for _ in range(n):
        q1 = Fraction(rng.randint(1, 9), rng.randint(2, 12))
        q2 = Fraction(rng.randint(1, 9), rng.randint(2, 12))
        cmp_word = "maggiore" if q1 > q2 else ("minore" if q1 < q2 else "uguale")
        rel = ">" if q1 > q2 else ("<" if q1 < q2 else "=")
        text = f"Confrontare le frazioni {frac_text(q1)} e {frac_text(q2)}."
        sol = (
            f"Valori decimali: {float(q1):.3f} e {float(q2):.3f}.\n"
            f"{frac_text(q1)} è {cmp_word} rispetto a {frac_text(q2)}."
        )
        latex = f"{latex_frac(q1)} {rel} {latex_frac(q2)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_2_3(rng, n):
    out = []
    for _ in range(n):
        q1 = Fraction(rng.randint(1, 9), rng.randint(2, 12))
        q2 = Fraction(rng.randint(1, 9), rng.randint(2, 12))
        op = rng.choice(["+", "-", "*"])
        res = q1 + q2 if op == "+" else q1 - q2 if op == "-" else q1 * q2
        text = f"Calcolare: {frac_text(q1)} {op} {frac_text(q2)}."
        if op in ("+", "-"):
            den = lcm_int(q1.denominator, q2.denominator)
            a1 = q1.numerator * (den // q1.denominator)
            a2 = q2.numerator * (den // q2.denominator)
            sol = (
                f"mcm({q1.denominator},{q2.denominator}) = {den}.\n"
                f"{frac_text(q1)} = {a1}/{den}, {frac_text(q2)} = {a2}/{den}.\n"
                f"Risultato: {frac_text(res)}."
            )
        else:
            sol = f"Si moltiplicano numeratori e denominatori: {q1.numerator*q2.numerator}/{q1.denominator*q2.denominator}.\nSemplificato: {frac_text(res)}."
        op_latex = "\\cdot" if op == "*" else op
        latex = f"{latex_frac(q1)} {op_latex} {latex_frac(q2)} = {latex_frac(res)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_2_4(rng, n):
    out = []
    for _ in range(n):
        den = rng.choice([2, 4, 5, 8, 10, 20, 25, 3, 6, 7, 9, 11])
        num = rng.randint(1, den * 3)
        q = Fraction(num, den)
        finito = is_finite_decimal(q.denominator)
        text = f"Scrivere in forma decimale la frazione {frac_text(q)} e dire se è un numero decimale finito o periodico."
        sol = (
            "Una frazione ridotta ai minimi termini dà un decimale finito se il suo denominatore ha solo i fattori primi 2 e/o 5; altrimenti è periodico.\n"
            f"Valore approssimato: {float(q):.4f}\n"
            f"Il numero è decimale {'finito' if finito else 'periodico'}."
        )
        latex = f"{latex_frac(q)} \\approx {float(q):.4f}\\ldots"
        out.append(Exercise(text, sol, latex))
    return out


def lez_2_5(rng, n):
    out = []
    for _ in range(n):
        choice = rng.choice(["proporzione", "percentuale"])
        if choice == "proporzione":
            a_, b_, c_ = rng.randint(2, 20), rng.randint(2, 20), rng.randint(2, 20)
            x_val = Fraction(b_ * c_, a_)
            text = f"Risolvere la proporzione: {a_} : {b_} = {c_} : x."
            sol = f"In una proporzione il prodotto dei medi è uguale al prodotto degli estremi.\n{a_} · x = {b_} · {c_}, quindi x = ({b_}·{c_})/{a_} = {frac_text(x_val)}."
            latex = f"{a_} : {b_} = {c_} : x \\ \\Rightarrow \\ x = {latex_frac(x_val)}"
        else:
            base = rng.choice([60, 80, 120, 150, 200, 250])
            perc = rng.choice([5, 10, 15, 20, 25, 30, 40, 50])
            val = Fraction(base * perc, 100)
            text = f"Calcolare il {perc}% di {base}."
            sol = f"{perc}% = {perc}/100.\n{base} · {perc}/100 = {frac_text(val)}."
            latex = f"{perc}\\% \\ \\text{{di}} \\ {base} = {latex_frac(val)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_2_6(rng, n):
    out = []
    for _ in range(n):
        choice = rng.choice(["irrazionale", "razionale"])
        if choice == "irrazionale":
            k = rng.choice([2, 3, 5, 6, 7, 8, 10, 11, 12, 13])
            text = f"Il numero √{k} è razionale o irrazionale? Motivare la risposta."
            sol = (
                f"{k} non è un quadrato perfetto: nessun intero elevato al quadrato dà {k}.\n"
                f"√{k} non può essere scritto come frazione di due interi: è irrazionale."
            )
            latex = f"\\sqrt{{{k}}}"
        else:
            k = rng.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
            r = int(math.isqrt(k))
            text = f"Il numero √{k} è razionale o irrazionale? Motivare la risposta."
            sol = f"{k} è un quadrato perfetto, perché {r}^2 = {k}.\n√{k} = {r}, un numero intero, quindi razionale."
            latex = f"\\sqrt{{{k}}} = {r}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_2_7(rng, n):
    out = []
    for _ in range(n):
        coeff = rng.randint(12, 987)
        exp = rng.randint(3, 8)
        num = coeff * (10 ** exp)
        sci_coeff = coeff / 100
        text = f"Scrivere {num} in notazione scientifica."
        sol = (
            f"Si sposta la virgola fino a ottenere un numero tra 1 e 10: {sci_coeff}.\n"
            f"La virgola è stata spostata di {exp + 2} posizioni.\n"
            f"Risultato: {sci_coeff} · 10^{exp + 2}."
        )
        latex = f"{num} = {sci_coeff} \\times 10^{{{exp+2}}}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 3 - Insiemi, logica e relazioni ----

def lez_3_1(rng, n):
    out = []
    universe = list(range(1, 15))
    for _ in range(n):
        A = sorted(rng.sample(universe, rng.randint(3, 6)))
        text = f"Dato l'insieme A = {A}, elencare tre suoi sottoinsiemi (incluso l'insieme vuoto) e dire quanti sottoinsiemi ha in totale A."
        sol = (
            f"Alcuni sottoinsiemi di A: ∅, {{{A[0]}}}, {A[:2]}.\n"
            f"Un insieme con {len(A)} elementi ha 2^{len(A)} = {2**len(A)} sottoinsiemi in totale."
        )
        latex = "A = \\{" + ", ".join(map(str, A)) + "\\}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_3_2(rng, n):
    out = []
    universe = list(range(1, 13))
    for _ in range(n):
        A = sorted(rng.sample(universe, rng.randint(4, 7)))
        B = sorted(rng.sample(universe, rng.randint(4, 7)))
        text = f"Dati A = {A} e B = {B}, calcolare A ∪ B, A ∩ B e A - B."
        sol = (
            f"A ∪ B = {sorted(set(A)|set(B))}.\n"
            f"A ∩ B = {sorted(set(A)&set(B))}.\n"
            f"A - B = {sorted(set(A)-set(B))}."
        )
        latex = "A \\cup B, \\quad A \\cap B, \\quad A - B"
        out.append(Exercise(text, sol, latex))
    return out


def lez_3_3(rng, n):
    out = []
    for _ in range(n):
        p, q = rng.choice([True, False]), rng.choice([True, False])
        conn = rng.choice(["and", "or", "not_and", "implica"])
        if conn == "and":
            text = f"Sapendo che p è {p} e q è {q}, stabilire il valore di verità di 'p AND q'."
            sol = f"La congiunzione è vera solo se entrambe le proposizioni sono vere.\np AND q = {p and q}."
            latex = "p \\land q"
        elif conn == "or":
            text = f"Sapendo che p è {p} e q è {q}, stabilire il valore di verità di 'p OR q'."
            sol = f"La disgiunzione è vera se almeno una proposizione è vera.\np OR q = {p or q}."
            latex = "p \\lor q"
        elif conn == "not_and":
            text = f"Sapendo che p è {p} e q è {q}, stabilire il valore di verità di 'NOT p AND q'."
            sol = f"NOT p = {not p}.\nNOT p AND q = {not p and q}."
            latex = "\\lnot p \\land q"
        else:
            text = f"Sapendo che p è {p} e q è {q}, stabilire il valore di verità dell'implicazione 'p → q'."
            sol = f"L'implicazione è falsa solo se p è vera e q è falsa.\np → q = {(not p) or q}."
            latex = "p \\to q"
        out.append(Exercise(text, sol, latex))
    return out


def lez_3_4(rng, n):
    out = []
    for _ in range(n):
        p, q, r = [rng.choice([True, False]) for _ in range(3)]
        res = (p and q) or (not r)
        text = f"Sapendo che p è {p}, q è {q} e r è {r}, calcolare il valore di verità di '(p AND q) OR (NOT r)'."
        sol = (
            f"p AND q = {p and q}.\n"
            f"NOT r = {not r}.\n"
            f"(p AND q) OR (NOT r) = {res}."
        )
        latex = "(p \\land q) \\lor (\\lnot r)"
        out.append(Exercise(text, sol, latex))
    return out


def lez_3_5(rng, n):
    out = []
    for _ in range(n):
        lo, hi = 1, 20
        k = rng.randint(2, 5)
        A = sorted(v for v in range(lo, hi + 1) if v % k == 0)
        text = f"Scrivere in forma caratteristica l'insieme A = {A} dei numeri da {lo} a {hi} multipli di {k}."
        sol = f"A = {{x ∈ N : {lo} ≤ x ≤ {hi} e x è multiplo di {k}}}.\nElencazione: A = {A}."
        latex = f"A = \\{{x \\in \\mathbb{{N}} : {lo} \\le x \\le {hi},\\ {k} \\mid x\\}}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_3_6(rng, n):
    out = []
    universe = list(range(1, 13))
    for _ in range(n):
        A = sorted(rng.sample(universe, rng.randint(4, 6)))
        B = sorted(rng.sample(universe, rng.randint(4, 6)))
        div = rng.choice([2, 3])
        pairs = [(a, b) for a in A for b in B if (a + b) % div == 0]
        text = f"Dati A = {A} e B = {B}, elencare le coppie della relazione R = {{(a,b) : a+b è divisibile per {div}}}."
        sol = f"Coppie che soddisfano la condizione: {pairs[:12]}{' ...' if len(pairs) > 12 else ''}."
        latex = f"R = \\{{(a,b) : {div} \\mid (a+b)\\}}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_3_7(rng, n):
    out = []
    for _ in range(n):
        A = sorted(rng.sample(range(1, 8), 4))
        pairs = [(a, b) for a in A for b in A if a <= b]
        text = f"Nell'insieme A = {A}, la relazione R è 'a R b se a ≤ b'. Verificare se R è riflessiva, simmetrica, transitiva."
        sol = (
            "Riflessiva: a ≤ a è sempre vera, quindi R è riflessiva.\n"
            "Simmetrica: a ≤ b non implica b ≤ a (salvo a=b), quindi R non è simmetrica.\n"
            "Transitiva: se a ≤ b e b ≤ c allora a ≤ c, quindi R è transitiva.\n"
            f"Alcune coppie di R: {pairs[:10]}{' ...' if len(pairs) > 10 else ''}."
        )
        latex = "a \\, R \\, b \\iff a \\le b"
        out.append(Exercise(text, sol, latex))
    return out


def lez_3_8(rng, n):
    out = []
    for _ in range(n):
        choice = rng.choice(["equivalenza", "ordine"])
        A = sorted(rng.sample(range(1, 20), 6))
        if choice == "equivalenza":
            k = rng.choice([2, 3])
            classes: dict[int, list[int]] = {}
            for v in A:
                classes.setdefault(v % k, []).append(v)
            text = f"Nell'insieme A = {A}, R è 'a R b se a e b hanno lo stesso resto nella divisione per {k}'. Verificare che è una relazione di equivalenza e determinare le classi."
            sol = (
                "R è riflessiva, simmetrica e transitiva rispetto all'uguaglianza dei resti: è una relazione di equivalenza.\n"
                f"Classi di equivalenza: {classes}."
            )
            latex = f"a \\, R \\, b \\iff a \\equiv b \\pmod{{{k}}}"
        else:
            text = f"Nell'insieme A = {A}, R è 'a R b se a è un divisore di b'. Verificare che è una relazione d'ordine."
            sol = (
                "Riflessiva: ogni numero divide se stesso.\n"
                "Antisimmetrica: se a divide b e b divide a (con a,b positivi), allora a = b.\n"
                "Transitiva: se a divide b e b divide c, allora a divide c.\n"
                "R è quindi una relazione d'ordine (parziale)."
            )
            latex = "a \\, R \\, b \\iff a \\mid b"
        out.append(Exercise(text, sol, latex))
    return out


def lez_3_9(rng, n):
    out = []
    for _ in range(n):
        A = sorted(rng.sample(range(1, 10), 4))
        B = sorted(rng.sample(range(1, 10), 4))
        mapping = {a: rng.choice(B) for a in A}
        images = list(mapping.values())
        iniettiva = len(set(images)) == len(images)
        text = f"Dati A = {A} e B = {B}, f associa a ogni elemento di A il valore: {mapping}. Dire se f è una funzione e se è iniettiva."
        sol = (
            "f è una funzione perché ogni elemento di A ha una e una sola immagine in B.\n"
            f"Immagini: {images}.\n"
            f"f è {'iniettiva' if iniettiva else 'non iniettiva, perché almeno due elementi hanno la stessa immagine'}."
        )
        latex = "f : A \\to B"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 4 - Monomi ----

def lez_4_1(rng, n):
    out = []
    for _ in range(n):
        c = random_nonzero(rng, -9, 9)
        px, py = rng.randint(0, 4), rng.randint(0, 4)
        mono = c * x**px * y**py
        text = f"Dato il monomio {s(mono)}, indicare coefficiente e grado complessivo."
        sol = f"Coefficiente: {c}.\nGrado complessivo: {px} + {py} = {px+py}."
        latex = sp.latex(mono)
        out.append(Exercise(text, sol, latex))
    return out


def lez_4_2(rng, n):
    out = []
    for _ in range(n):
        choice = rng.choice(["sum", "product"])
        if choice == "sum":
            c1, c2 = random_nonzero(rng, -9, 9), random_nonzero(rng, -9, 9)
            px, py = rng.randint(1, 4), rng.randint(0, 3)
            mono = x**px * y**py
            expr = c1 * mono + c2 * mono
            res = sp.expand(expr)
            text = f"Semplificare la somma di monomi simili: {s(c1*mono)} + {s(c2*mono)}."
            sol = f"I monomi sono simili: stessa parte letterale.\nSomma coefficienti: {c1}+({c2}) = {c1+c2}.\nRisultato: {s(res)}."
            second_sign = "-" if c2 < 0 else "+"
            latex = f"{sp.latex(c1*mono)} {second_sign} {sp.latex(abs(c2)*mono)} = {sp.latex(res)}"
        else:
            c1, c2 = random_nonzero(rng, -6, 6), random_nonzero(rng, -6, 6)
            m1 = c1 * x**rng.randint(1, 3) * y**rng.randint(0, 2)
            m2 = c2 * x**rng.randint(0, 3) * y**rng.randint(1, 3)
            res = sp.expand(m1 * m2)
            text = f"Calcolare il prodotto: ({s(m1)}) · ({s(m2)})."
            sol = f"Si moltiplicano i coefficienti; per le stesse basi si sommano gli esponenti.\nRisultato: {s(res)}."
            latex = f"({sp.latex(m1)}) \\cdot ({sp.latex(m2)}) = {sp.latex(res)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_4_3(rng, n):
    out = []
    for _ in range(n):
        choice = rng.choice(["div", "pow"])
        if choice == "div":
            c1 = random_nonzero(rng, -12, 12)
            c2 = random_nonzero(rng, 1, 6)
            px1, py1 = rng.randint(2, 5), rng.randint(1, 4)
            px2, py2 = rng.randint(0, px1), rng.randint(0, py1)
            m1 = c1 * x**px1 * y**py1
            m2 = c2 * x**px2 * y**py2
            res = sp.cancel(m1 / m2)
            text = f"Calcolare il quoziente: ({s(m1)}) : ({s(m2)})."
            sol = f"Si dividono i coefficienti; per le stesse basi si sottraggono gli esponenti.\nRisultato: {s(res)}."
            latex = f"\\dfrac{{{sp.latex(m1)}}}{{{sp.latex(m2)}}} = {sp.latex(res)}"
        else:
            c = random_nonzero(rng, -5, 5)
            px, py = rng.randint(1, 3), rng.randint(0, 3)
            e = rng.randint(2, 3)
            mono = c * x**px * y**py
            res = sp.expand(mono**e)
            text = f"Calcolare la potenza: ({s(mono)})^{e}."
            sol = f"Si eleva a potenza il coefficiente e si moltiplica ogni esponente per l'esponente esterno.\nRisultato: {s(res)}."
            latex = f"\\left({sp.latex(mono)}\\right)^{{{e}}} = {sp.latex(res)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_4_4(rng, n):
    out = []
    for _ in range(n):
        c1, c2 = rng.randint(2, 12), rng.randint(2, 12)
        p1, p2 = rng.randint(1, 5), rng.randint(1, 5)
        q1, q2 = rng.randint(0, 4), rng.randint(0, 4)
        m1, m2 = c1 * x**p1 * y**q1, c2 * x**p2 * y**q2
        g, l = math.gcd(c1, c2), lcm_int(c1, c2)
        mcd = g * x**min(p1, p2) * y**min(q1, q2)
        mcm = l * x**max(p1, p2) * y**max(q1, q2)
        text = f"Determinare MCD e mcm dei monomi {s(m1)} e {s(m2)}."
        sol = f"MCD coefficienti = {g}; esponenti minimi -> MCD = {s(mcd)}.\nmcm coefficienti = {l}; esponenti massimi -> mcm = {s(mcm)}."
        latex = f"\\text{{MCD}} = {sp.latex(mcd)}, \\quad \\text{{mcm}} = {sp.latex(mcm)}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 5 - Polinomi ----

def lez_5_1(rng, n):
    out = []
    for _ in range(n):
        poly = sp.Integer(0)
        while poly == 0:
            terms = [(random_nonzero(rng, -9, 9), rng.randint(0, 4)) for _ in range(4)]
            poly = sp.expand(sum(c * x**p for c, p in terms))
        deg = sp.degree(poly, x)
        ordered = sp.Poly(poly, x).as_expr()
        text = f"Dato il polinomio P(x) = {s(poly)}, indicarne il grado e riordinarlo secondo le potenze decrescenti di x."
        sol = f"Il grado è il massimo esponente di x presente: {deg}.\nOrdinato: {s(ordered)}."
        latex = f"P(x) = {sp.latex(poly)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_5_2(rng, n):
    out = []
    for _ in range(n):
        A, B, C, D = [random_nonzero(rng, -6, 6) for _ in range(4)]
        p, q = A * x + B, C * x + D
        is_sum = rng.choice([True, False])
        if is_sum:
            res = sp.expand(p + q)
            text = f"Calcolare la somma tra polinomi: ({s(p)}) + ({s(q)})."
            sol = f"Si sommano i coefficienti dei termini simili.\nRisultato: {s(res)}."
            latex = f"({sp.latex(p)}) + ({sp.latex(q)}) = {sp.latex(res)}"
        else:
            res = sp.expand(p * q)
            text = f"Calcolare il prodotto tra polinomi: ({s(p)})({s(q)})."
            sol = f"Si applica la proprietà distributiva tra ogni termine del primo e ogni termine del secondo polinomio.\nRisultato: {s(res)}."
            latex = f"({sp.latex(p)}) \\cdot ({sp.latex(q)}) = {sp.latex(res)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_5_3(rng, n):
    out = []
    for _ in range(n):
        A, B = random_nonzero(rng, -6, 6), random_nonzero(rng, -6, 6)
        is_square = rng.choice([True, False])
        if is_square:
            p = A * x + B * y
            res = sp.expand(p**2)
            text = f"Sviluppare il quadrato di binomio: ({s(p)})^2."
            sol = f"Formula: (u+v)^2 = u^2+2uv+v^2, con u={A}x e v={B}y.\nRisultato: {s(res)}."
            latex = f"({sp.latex(p)})^{{2}} = {sp.latex(res)}"
        else:
            res = sp.expand((A * x + B * y) * (A * x - B * y))
            text = f"Calcolare il prodotto notevole: ({A}x + {B}y)({A}x - {B}y)."
            sol = f"Formula: (u+v)(u-v) = u^2 - v^2.\nRisultato: {s(res)}."
            sum_part = sp.latex(A * x + B * y)
            diff_part = sp.latex(A * x - B * y)
            latex = f"({sum_part})({diff_part}) = {sp.latex(res)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_5_4(rng, n):
    out = []
    for _ in range(n):
        A, B = random_nonzero(rng, -4, 4), random_nonzero(rng, -4, 4)
        p = A * x + B * y
        res = sp.expand(p**3)
        text = f"Sviluppare il cubo di binomio: ({s(p)})^3."
        sol = f"Formula: (u+v)^3 = u^3 + 3u^2v + 3uv^2 + v^3.\nRisultato: {s(res)}."
        latex = f"({sp.latex(p)})^{{3}} = {sp.latex(res)}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 6 - Equazioni lineari ----

def lez_6_1(rng, n):
    out = []
    for _ in range(n):
        A, C = random_nonzero(rng, -6, 6), rng.randint(-15, 15)
        candidate = rng.randint(-8, 8)
        left_val = A * candidate
        is_sol = left_val == C
        text = f"Verificare se x = {candidate} è soluzione dell'equazione {A}x = {C}."
        sol = (
            f"Sostituendo x = {candidate}: {A}·{candidate} = {left_val}.\n"
            f"Il valore {'coincide' if is_sol else 'non coincide'} con {C}: x = {candidate} {'è' if is_sol else 'non è'} soluzione."
        )
        latex = f"{A}x = {C}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_6_2(rng, n):
    out = []
    for _ in range(n):
        B = rng.randint(-15, 15)
        C = rng.randint(-15, 15)
        sol_x = C - B
        text = f"Applicando i principi di equivalenza, risolvere l'equazione: x + ({B}) = {C}."
        sol = f"Per il primo principio di equivalenza si somma lo stesso numero a entrambi i membri.\nx = {C} - ({B}) = {sol_x}."
        latex = f"x + ({B}) = {C}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_6_3(rng, n):
    out = []
    for _ in range(n):
        A = random_nonzero(rng, -8, 8)
        C = random_nonzero(rng, -8, 8)
        while A == C:
            C = random_nonzero(rng, -8, 8)
        B, D = rng.randint(-20, 20), rng.randint(-20, 20)
        sol_x = Fraction(D - B, A - C)
        text = f"Risolvere l'equazione: {A}x + ({B}) = {C}x + ({D})."
        sol = f"{A}x - {C}x = {D} - ({B}).\n{A-C}x = {D-B}.\nx = ({D-B})/({A-C}) = {frac_text(sol_x)}."
        latex = f"{A}x + ({B}) = {C}x + ({D})"
        out.append(Exercise(text, sol, latex))
    return out


def lez_6_4(rng, n):
    out = []
    for _ in range(n):
        k = rng.randint(2, 9)
        add = rng.randint(3, 30)
        result = rng.randint(20, 100)
        sol_x = Fraction(result - add, k)
        text = f"Un numero moltiplicato per {k} e aumentato di {add} dà come risultato {result}. Qual è il numero?"
        sol = (
            f"Indicando con x il numero cercato: {k}x + {add} = {result}.\n"
            f"{k}x = {result-add}.\nx = {frac_text(sol_x)}."
        )
        latex = f"{k}x + {add} = {result}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 7 - Funzioni ----

def lez_7_1(rng, n):
    out = []
    for _ in range(n):
        a_ = random_nonzero(rng, -4, 4)
        b_ = rng.randint(-5, 5)
        c_ = rng.randint(-5, 5)
        val = rng.randint(-5, 5)
        fx = a_ * x**2 + b_ * x + c_
        result = fx.subs(x, val)
        text = f"Data la funzione f(x) = {s(fx)}, calcolare f({val})."
        sol = f"Sostituendo x = {val}: f({val}) = {a_}·({val})^2 + {b_}·({val}) + {c_} = {result}."
        latex = f"f(x) = {sp.latex(fx)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_7_3(rng, n):
    out = []
    for _ in range(n):
        m = random_nonzero(rng, -6, 6)
        q = rng.randint(-10, 10)
        text = f"Data la funzione f(x) = {m}x + ({q}), determinare la funzione inversa f^-1(x)."
        sol = (
            f"Si pone y = {m}x + ({q}) e si ricava x: x = (y - ({q}))/{m}.\n"
            f"Scambiando x e y: f^-1(x) = (x - ({q}))/{m}."
        )
        latex = f"f(x) = {m}x + ({q})"
        out.append(Exercise(text, sol, latex))
    return out


def lez_7_4(rng, n):
    out = []
    for _ in range(n):
        a1, b1 = random_nonzero(rng, -5, 5), rng.randint(-8, 8)
        a2, b2 = random_nonzero(rng, -5, 5), rng.randint(-8, 8)
        fx, gx = a1 * x + b1, a2 * x + b2
        comp = sp.expand(fx.subs(x, gx))
        text = f"Date f(x) = {s(fx)} e g(x) = {s(gx)}, calcolare (f∘g)(x) = f(g(x))."
        sol = f"Si sostituisce g(x) al posto di x in f(x): {a1}·({s(gx)}) + ({b1}).\nSviluppando: {s(comp)}."
        latex = f"f(x) = {sp.latex(fx)}, \\quad g(x) = {sp.latex(gx)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_7_5(rng, n):
    out = []
    for _ in range(n):
        choice = rng.choice(["diretta", "inversa"])
        k = rng.randint(2, 12)
        x0 = rng.randint(2, 15)
        x1 = rng.randint(2, 15)
        if choice == "diretta":
            y0 = k * x0
            y1 = k * x1
            text = f"x e y sono direttamente proporzionali. A x = {x0} corrisponde y = {y0}. Determinare k e y quando x = {x1}."
            sol = f"k = y/x = {y0}/{x0} = {k}.\nQuando x = {x1}: y = k·x = {k*x1}."
            latex = f"y = {k}\\,x"
        else:
            y0 = Fraction(k, x0)
            y1 = Fraction(k, x1)
            text = f"x e y sono inversamente proporzionali. A x = {x0} corrisponde y = {frac_text(y0)}. Determinare k e y quando x = {x1}."
            sol = f"k = x·y = {x0}·{frac_text(y0)} = {k}.\nQuando x = {x1}: y = k/x = {frac_text(y1)}."
            latex = f"y = \\dfrac{{{k}}}{{x}}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_7_6(rng, n):
    out = []
    for _ in range(n):
        m = random_nonzero(rng, -5, 5)
        q = rng.randint(-8, 8)
        values = sorted(rng.sample(range(-4, 5), 3))
        points = [(v, m * v + q) for v in values]
        text = f"Data f(x) = {m}x + ({q}), calcolare f(x) per x = {values} e indicare coefficiente angolare e intercetta."
        sol = f"Valori: {points}.\nCoefficiente angolare m = {m}. Intercetta: (0, {q})."
        latex = f"f(x) = {m}x + ({q})"
        out.append(Exercise(text, sol, latex))
    return out


def lez_7_7(rng, n):
    out = []
    for _ in range(n):
        power = rng.choice([2, 3])
        k = rng.randint(2, 8)
        x0 = rng.randint(2, 6)
        x1 = rng.randint(2, 6)
        y0 = k * x0**power
        y1 = k * x1**power
        text = f"y = k·x^{power}. A x = {x0} corrisponde y = {y0}. Determinare k e y quando x = {x1}."
        sol = f"k = y/x^{power} = {y0}/{x0**power} = {k}.\nQuando x = {x1}: y = {k}·{x1}^{power} = {y1}."
        latex = f"y = {k}\\,x^{{{power}}}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_7_8(rng, n):
    out = []
    angles = [0, 30, 45, 60, 90]
    for _ in range(n):
        deg = rng.choice(angles)
        func = rng.choice(["sin", "cos"])
        val = sp.sin(sp.rad(deg)) if func == "sin" else sp.cos(sp.rad(deg))
        text = f"Calcolare {func}({deg}°), uno degli angoli notevoli."
        sol = f"Per gli angoli notevoli si usano i valori noti a memoria.\n{func}({deg}°) = {s(val)}."
        latex = f"\\{func}({latex_deg(deg)}) = {sp.latex(val)}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 8 - Divisione tra polinomi e scomposizione in fattori ----

def lez_8_1(rng, n):
    out = []
    for _ in range(n):
        coeffs = [random_nonzero(rng, -6, 6) for _ in range(4)]
        dividend = sum(c * x**i for i, c in enumerate(reversed(coeffs)))
        divisor = random_nonzero(rng, 1, 4) * x + rng.randint(-6, 6)
        q, rem = sp.div(dividend, divisor, x)
        text = f"Eseguire la divisione: ({s(dividend)}) : ({s(divisor)})."
        sol = f"Quoziente: {s(q)}.\nResto: {s(rem)}.\nVerifica: ({s(divisor)})·({s(q)}) + ({s(rem)}) = {s(sp.expand(divisor*q+rem))}."
        latex = f"\\left({sp.latex(dividend)}\\right) : \\left({sp.latex(divisor)}\\right)"
        out.append(Exercise(text, sol, latex))
    return out


def lez_8_2(rng, n):
    out = []
    for _ in range(n):
        coeffs = [random_nonzero(rng, -6, 6) for _ in range(4)]
        dividend = sum(c * x**i for i, c in enumerate(reversed(coeffs)))
        r = rng.randint(-5, 5)
        q, rem = sp.div(dividend, x - r, x)
        text = f"Applicare la regola di Ruffini per dividere P(x) = {s(dividend)} per (x - {r})."
        sol = (
            "Si scrivono i coefficienti di P(x) e si moltiplicano progressivamente per la radice del divisore, sommando ai coefficienti successivi.\n"
            f"Quoziente: {s(q)}.\nResto: {s(rem)}."
        )
        latex = f"P(x) = {sp.latex(dividend)}, \\quad D(x) = {latex_x_minus(r)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_8_3(rng, n):
    out = []
    for _ in range(n):
        coeffs = [random_nonzero(rng, -6, 6) for _ in range(4)]
        dividend = sum(c * x**i for i, c in enumerate(reversed(coeffs)))
        r = rng.randint(-5, 5)
        val = dividend.subs(x, r)
        divisible = val == 0
        text = f"Usando il teorema del resto, stabilire se P(x) = {s(dividend)} è divisibile per (x - {r})."
        sol = (
            f"Il teorema del resto dice che il resto della divisione per (x-{r}) è uguale a P({r}).\n"
            f"P({r}) = {val}.\n"
            f"P(x) {'è' if divisible else 'non è'} divisibile per (x - {r})."
        )
        latex = f"P(x) = {sp.latex(dividend)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_8_4(rng, n):
    out = []
    for _ in range(n):
        c = random_nonzero(rng, 2, 9)
        px, py = rng.randint(1, 3), rng.randint(1, 3)
        common = c * x**px * y**py
        t1 = rng.randint(1, 6)
        t2 = random_nonzero(rng, -6, 6)
        poly = sp.expand(common * (x**t1 + t2))
        text = f"Scomporre in fattori raccogliendo il fattore comune: {s(poly)}."
        sol = f"Il fattore comune a tutti i termini è {s(common)}.\nScomposizione: {s(common)} · ({s(x**t1+t2)})."
        latex = sp.latex(poly)
        out.append(Exercise(text, sol, latex))
    return out


def lez_8_5(rng, n):
    out = []
    for _ in range(n):
        r1, r2 = rng.randint(-8, 8), rng.randint(-8, 8)
        poly = sp.expand((x - r1) * (x - r2))
        text = f"Scomporre in fattori il trinomio speciale: {s(poly)}."
        sol = (
            "Si cercano due numeri la cui somma è il coefficiente di x cambiato di segno e il cui prodotto è il termine noto.\n"
            f"I due numeri sono {r1} e {r2}.\nScomposizione: (x - ({r1}))(x - ({r2}))."
        )
        latex = sp.latex(poly)
        out.append(Exercise(text, sol, latex))
    return out


def lez_8_6(rng, n):
    out = []
    for _ in range(n):
        A, B = random_nonzero(rng, 1, 6), random_nonzero(rng, 1, 6)
        is_square = rng.choice([True, False])
        if is_square:
            poly = sp.expand((A * x + B) ** 2)
            text = f"Riconoscere il prodotto notevole e scomporre in fattori: {s(poly)}."
            sol = f"È lo sviluppo di un quadrato di binomio.\nScomposizione: ({A}x + {B})^2."
        else:
            poly = sp.expand((A * x) ** 2 - B ** 2)
            text = f"Riconoscere il prodotto notevole e scomporre in fattori: {s(poly)}."
            sol = f"È una differenza di quadrati.\nScomposizione: ({A}x - {B})({A}x + {B})."
        latex = sp.latex(poly)
        out.append(Exercise(text, sol, latex))
    return out


def lez_8_7(rng, n):
    out = []
    for _ in range(n):
        r1 = r2 = r3 = 0
        while 0 in (r1, r2, r3):
            r1, r2, r3 = [rng.randint(-5, 5) for _ in range(3)]
        poly = sp.expand((x - r1) * (x - r2) * (x - r3))
        text = f"Scomporre in fattori utilizzando il metodo di Ruffini: {s(poly)}."
        sol = (
            f"Si cerca una radice tra i divisori del termine noto: una radice è x = {r1}.\n"
            f"Dividendo per (x - {r1}) con Ruffini si ottiene un quoziente di secondo grado, ulteriormente scomponibile.\n"
            f"Scomposizione completa: {s(sp.factor(poly))}."
        )
        latex = sp.latex(poly)
        out.append(Exercise(text, sol, latex))
    return out


def lez_8_8(rng, n):
    out = []
    for _ in range(n):
        common_r = rng.randint(-5, 5)
        r2 = rng.randint(-5, 5)
        while r2 == common_r:
            r2 = rng.randint(-5, 5)
        r3 = rng.randint(-5, 5)
        while r3 in (common_r, r2):
            r3 = rng.randint(-5, 5)
        p1 = sp.expand((x - common_r) * (x - r2))
        p2 = sp.expand((x - common_r) * (x - r3))
        mcm = sp.expand((x - common_r) * (x - r2) * (x - r3))
        text = f"Determinare MCD e mcm dei polinomi P(x) = {s(p1)} e Q(x) = {s(p2)}."
        sol = (
            f"Scomponendo: P(x) = (x-{common_r})(x-{r2}), Q(x) = (x-{common_r})(x-{r3}).\n"
            f"MCD = fattore comune = (x - {common_r}).\n"
            f"mcm = {s(mcm)}."
        )
        latex = f"P(x) = {sp.latex(p1)}, \\quad Q(x) = {sp.latex(p2)}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 9 - Frazioni algebriche ed equazioni fratte e letterali ----

def lez_9_1(rng, n):
    out = []
    for _ in range(n):
        r = rng.randint(-8, 8)
        num = random_nonzero(rng, -9, 9)
        text = f"Determinare le condizioni di esistenza della frazione algebrica: {num} / (x - {r})."
        sol = f"Il denominatore deve essere diverso da zero: x - {r} ≠ 0, quindi x ≠ {r}."
        latex = f"\\dfrac{{{num}}}{{{latex_x_minus(r)}}}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_9_2(rng, n):
    out = []
    for _ in range(n):
        r = rng.randint(-6, 6)
        num = x + r
        den = x - r if r != 0 else x + r + 1
        k = random_nonzero(rng, 2, 5)
        text = f"Scrivere una frazione equivalente a ({s(num)})/({s(den)}) moltiplicando numeratore e denominatore per {k}."
        sol = f"({k}·({s(num)}))/({k}·({s(den)})) = ({s(sp.expand(k*num))})/({s(sp.expand(k*den))})."
        latex = f"\\dfrac{{{sp.latex(num)}}}{{{sp.latex(den)}}}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_9_3(rng, n):
    out = []
    for _ in range(n):
        r1, r2 = rng.randint(-5, 5), rng.randint(-5, 5)
        while r1 == r2:
            r2 = rng.randint(-5, 5)
        num = sp.expand((x - r1) * (x + rng.randint(1, 5)))
        den = sp.expand((x - r1) * (x - r2))
        simp = sp.cancel(num / den)
        text = f"Semplificare la frazione algebrica ({s(num)}) / ({s(den)}) indicando le condizioni di esistenza."
        sol = (
            f"Scomponendo: numeratore = {s(sp.factor(num))}, denominatore = {s(sp.factor(den))}.\n"
            f"Condizioni di esistenza: x ≠ {r1}, x ≠ {r2}.\nSemplificata: {s(simp)}."
        )
        latex = f"\\dfrac{{{sp.latex(num)}}}{{{sp.latex(den)}}} = {sp.latex(simp)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_9_4(rng, n):
    out = []
    for _ in range(n):
        r = random_nonzero(rng, -6, 6)
        A = random_nonzero(rng, -6, 6)
        Bnz = random_nonzero(rng, -6, 6)
        sol_x = Fraction(A, Bnz) + r
        text = f"Risolvere l'equazione fratta: {A} / (x - {r}) = {Bnz}, indicando le condizioni di esistenza."
        sol = (
            f"Condizione di esistenza: x ≠ {r}.\n"
            f"Moltiplicando per (x - {r}): {A} = {Bnz}(x - {r}).\n"
            f"x - {r} = {frac_text(Fraction(A,Bnz))}.\nx = {frac_text(sol_x)}."
        )
        latex = f"\\dfrac{{{A}}}{{{latex_x_minus(r)}}} = {Bnz}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_9_5(rng, n):
    out = []
    for _ in range(n):
        B = rng.randint(-15, 15)
        text = f"Risolvere rispetto a x l'equazione letterale: a·x = {B}, discutendo il caso a = 0."
        sol = (
            f"Se a ≠ 0: x = {B}/a.\n"
            f"Se a = 0, l'equazione diventa 0 = {B}: " + ("è sempre vera (infinite soluzioni)." if B == 0 else "è impossibile (nessuna soluzione).")
        )
        latex = f"a \\cdot x = {B}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 10 - Disequazioni lineari ----

def lez_10_1(rng, n):
    out = []
    for _ in range(n):
        a_, b_ = rng.randint(-20, 20), rng.randint(-20, 20)
        while a_ == b_:
            b_ = rng.randint(-20, 20)
        rel = ">" if a_ > b_ else "<"
        text = f"Confrontare i numeri {a_} e {b_} scrivendo la disuguaglianza corretta."
        sol = f"{a_} {rel} {b_}."
        latex = f"{a_} \\ ? \\ {b_}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_10_2(rng, n):
    out = []
    for _ in range(n):
        sign = rng.choice([">", "<"])
        A = random_nonzero(rng, -8, 8)
        B, C = rng.randint(-12, 12), rng.randint(-12, 12)
        threshold = Fraction(C - B, A)
        final_sign = sign if A > 0 else ("<" if sign == ">" else ">")
        text = f"Risolvere la disequazione: {A}x + ({B}) {sign} {C}."
        sol = f"Isolare x: {A}x {sign} {C-B}.\nDividendo per {A} (se negativo il verso si inverte): x {final_sign} {frac_text(threshold)}."
        latex = f"{A}x + ({B}) {sign} {C}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_10_3(rng, n):
    out = []
    for _ in range(n):
        t1 = rng.randint(-10, 10)
        t2 = rng.randint(-10, 10)
        text = f"Risolvere il sistema di disequazioni: x > {t1}  e  x < {t2}."
        if t1 < t2:
            sol = f"L'insieme soluzione è l'intersezione delle due condizioni: {t1} < x < {t2}."
        else:
            sol = "Le due condizioni non hanno valori in comune: il sistema non ha soluzioni."
        latex = f"\\begin{{cases}} x > {t1} \\\\ x < {t2} \\end{{cases}}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_10_4(rng, n):
    out = []
    for _ in range(n):
        A = random_nonzero(rng, -6, 6)
        B = rng.randint(-10, 10)
        C = rng.randint(1, 15)
        sol1 = Fraction(C - B, A)
        sol2 = Fraction(-C - B, A)
        text = f"Risolvere l'equazione con valore assoluto: |{A}x + ({B})| = {C}."
        sol = (
            f"Si pone {A}x + ({B}) = {C} oppure {A}x + ({B}) = -{C}.\n"
            f"Primo caso: x = {frac_text(sol1)}.\nSecondo caso: x = {frac_text(sol2)}."
        )
        latex = f"|{A}x + ({B})| = {C}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_10_5(rng, n):
    out = []
    for _ in range(n):
        A = random_nonzero(rng, 1, 6)
        B = rng.randint(-10, 10)
        C = rng.randint(1, 15)
        sign = rng.choice(["<", ">"])
        lo, hi = Fraction(-C - B, A), Fraction(C - B, A)
        text = f"Risolvere la disequazione con valore assoluto: |{A}x + ({B})| {sign} {C}."
        if sign == "<":
            sol = f"|{A}x+({B})| < {C} equivale a -{C} < {A}x+({B}) < {C}.\nSoluzione: {frac_text(lo)} < x < {frac_text(hi)}."
        else:
            sol = f"|{A}x+({B})| > {C} equivale a {A}x+({B}) < -{C} oppure {A}x+({B}) > {C}.\nSoluzione: x < {frac_text(lo)} oppure x > {frac_text(hi)}."
        latex = f"|{A}x + ({B})| {sign} {C}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_10_6(rng, n):
    out = []
    for _ in range(n):
        r1, r2 = rng.randint(-8, 8), rng.randint(-8, 8)
        while r1 == r2:
            r2 = rng.randint(-8, 8)
        r1, r2 = sorted([r1, r2])
        text = f"Studiare il segno del prodotto (x - {r1})(x - {r2}) e risolvere (x - {r1})(x - {r2}) > 0."
        sol = (
            f"Il primo fattore è positivo per x > {r1}, il secondo per x > {r2}.\n"
            "Il prodotto è positivo quando i due fattori hanno lo stesso segno.\n"
            f"Soluzione: x < {r1} oppure x > {r2}."
        )
        latex = f"({latex_x_minus(r1)})({latex_x_minus(r2)}) > 0"
        out.append(Exercise(text, sol, latex))
    return out


def lez_10_7(rng, n):
    out = []
    for _ in range(n):
        r1, r2 = rng.randint(-8, 8), rng.randint(-8, 8)
        while r1 == r2:
            r2 = rng.randint(-8, 8)
        lo, hi = sorted([r1, r2])
        text = f"Risolvere la disequazione fratta: (x - {r1}) / (x - {r2}) > 0, indicando le condizioni di esistenza."
        sol = (
            f"Condizione di esistenza: x ≠ {r2}.\n"
            f"Numeratore positivo per x > {r1}; denominatore positivo per x > {r2}.\n"
            f"La frazione è positiva quando numeratore e denominatore hanno lo stesso segno: x < {lo} oppure x > {hi}."
        )
        latex = f"\\dfrac{{{latex_x_minus(r1)}}}{{{latex_x_minus(r2)}}} > 0"
        out.append(Exercise(text, sol, latex))
    return out


def lez_10_8(rng, n):
    out = []
    for _ in range(n):
        B = rng.randint(-15, 15)
        text = f"Risolvere rispetto a x la disequazione letterale: a·x > {B}, discutendo i casi a > 0, a < 0, a = 0."
        sol = (
            f"Se a > 0: x > {B}/a.\n"
            f"Se a < 0: dividendo si inverte il verso, x < {B}/a.\n"
            f"Se a = 0: la disequazione diventa 0 > {B}, che è " + ("sempre vera." if B < 0 else "sempre falsa (nessuna soluzione).")
        )
        latex = f"a \\cdot x > {B}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo 11 - Statistica ----

_CONTEXT_POOL_11_1 = [
    ("colore degli occhi di un gruppo di studenti", "qualitativa"),
    ("numero di fratelli di ciascuno studente", "quantitativa discreta"),
    ("altezza in cm degli studenti", "quantitativa continua"),
    ("marca di smartphone posseduto", "qualitativa"),
    ("voto riportato in un compito (numero intero)", "quantitativa discreta"),
    ("tempo impiegato per svolgere una gara podistica", "quantitativa continua"),
]


def lez_11_1(rng, n):
    out = []
    for _ in range(n):
        ctx, tipo = rng.choice(_CONTEXT_POOL_11_1)
        text = f"Classificare il seguente carattere statistico: {ctx}. È qualitativo, quantitativo discreto o quantitativo continuo?"
        sol = f"Il carattere '{ctx}' è di tipo {tipo}."
        out.append(Exercise(text, sol, ""))
    return out


def lez_11_2(rng, n):
    out = []
    for _ in range(n):
        data = [rng.randint(1, 6) for _ in range(rng.randint(10, 15))]
        freq = {v: data.count(v) for v in sorted(set(data))}
        rel = {v: round(c / len(data), 3) for v, c in freq.items()}
        text = f"Dato il campione {data}, costruire la tabella delle frequenze assolute e relative."
        sol = f"Frequenze assolute: {freq}.\nFrequenze relative (assoluta/{len(data)}): {rel}."
        latex = "f_i = \\dfrac{n_i}{N}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_11_4(rng, n):
    out = []
    for _ in range(n):
        data = [rng.randint(1, 12) for _ in range(rng.randint(8, 13))]
        modes = multimode(data)
        text = f"Dato il campione {data}, calcolare media, mediana e moda."
        sol = f"Ordinati: {sorted(data)}.\nMedia = {sum(data)}/{len(data)} = {mean(data):.2f}.\nMediana = {median(data)}.\nModa = {modes}."
        latex = "\\bar{x} = \\dfrac{\\sum_i x_i}{n}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_11_5(rng, n):
    out = []
    for _ in range(n):
        data = [rng.randint(1, 20) for _ in range(rng.randint(6, 10))]
        m = mean(data)
        var = sum((v - m) ** 2 for v in data) / len(data)
        std = math.sqrt(var)
        text = f"Dato il campione {data}, calcolare campo di variazione, varianza e deviazione standard."
        sol = (
            f"Campo di variazione = {max(data)} - {min(data)} = {max(data)-min(data)}.\n"
            f"Media ≈ {m:.2f}.\nVarianza ≈ {var:.2f}.\nDeviazione standard ≈ {std:.2f}."
        )
        latex = "\\sigma^{2} = \\dfrac{\\sum_i (x_i - \\bar{x})^{2}}{n}, \\quad \\sigma = \\sqrt{\\sigma^{2}}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo G1 - Enti geometrici fondamentali ----

_STATEMENTS_G1_1 = [
    ("Per due punti distinti passa una e una sola retta.", True),
    ("Per un punto passano infinite rette.", True),
    ("Due rette distinte possono avere due punti in comune.", False),
    ("Un segmento ha una sola estremità.", False),
    ("Una retta ha lunghezza infinita.", True),
]


def lez_g1_1(rng, n):
    out = []
    for _ in range(n):
        frase, vero = rng.choice(_STATEMENTS_G1_1)
        text = f"Stabilire se la seguente affermazione è vera o falsa, motivando la risposta: '{frase}'"
        sol = f"L'affermazione è {'vera' if vero else 'falsa'}, in base ai postulati della geometria euclidea."
        out.append(Exercise(text, sol, ""))
    return out


_POLY_NAMES = {3: "triangolo", 4: "quadrilatero", 5: "pentagono", 6: "esagono", 7: "ettagono", 8: "ottagono"}


def lez_g1_2(rng, n):
    out = []
    for _ in range(n):
        sides = rng.randint(3, 8)
        total = (sides - 2) * 180
        text = f"Un poligono ha {sides} lati. Come si chiama e quanto vale la somma dei suoi angoli interni?"
        sol = f"Un poligono di {sides} lati si chiama {_POLY_NAMES.get(sides, str(sides)+'-agono')}.\nSomma angoli interni = (n-2)·180° = {total}°."
        latex = f"({sides}-2)\\cdot {latex_deg(180)} = {latex_deg(total)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g1_3(rng, n):
    out = []
    for _ in range(n):
        sides = rng.randint(4, 10)
        diagonals = sides * (sides - 3) // 2
        text = f"Calcolare il numero di diagonali di un poligono di {sides} lati."
        sol = f"Il numero di diagonali è n(n-3)/2.\nCon n = {sides}: {sides}·({sides}-3)/2 = {diagonals}."
        latex = f"d = \\dfrac{{n(n-3)}}{{2}} = \\dfrac{{{sides}\\cdot({sides}-3)}}{{2}} = {diagonals}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g1_4(rng, n):
    out = []
    for _ in range(n):
        is_segment = rng.choice([True, False])
        if is_segment:
            AB, BC = rng.randint(4, 30), rng.randint(4, 30)
            text = f"Su una retta sono dati due segmenti consecutivi AB = {AB} cm e BC = {BC} cm. Calcolare AC."
            sol = f"AC = AB + BC = {AB} + {BC} = {AB+BC} cm."
            latex = f"AC = AB + BC = {AB} + {BC} = {AB+BC}"
        else:
            a1, a2 = rng.randint(20, 80), rng.randint(20, 80)
            text = f"Due angoli consecutivi misurano {a1}° e {a2}°. Calcolare l'ampiezza dell'angolo somma."
            sol = f"Angolo somma = {a1}° + {a2}° = {a1+a2}°."
            latex = f"{latex_deg(a1)} + {latex_deg(a2)} = {latex_deg(a1+a2)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g1_5(rng, n):
    out = []
    for _ in range(n):
        AB = rng.randint(6, 60)
        k = rng.randint(2, 6)
        multiplo = AB * k
        sottomultiplo = Fraction(AB, k)
        text = f"Un segmento AB misura {AB} cm. Calcolare la misura di un segmento {k} volte AB e di un segmento pari a AB diviso {k}."
        sol = f"Multiplo: {k} · {AB} = {multiplo} cm.\nSottomultiplo: {AB} / {k} = {frac_text(sottomultiplo)} cm."
        latex = f"{k}\\cdot AB = {multiplo}, \\quad AB / {k} = {latex_frac(sottomultiplo)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g1_6(rng, n):
    out = []
    for _ in range(n):
        is_length = rng.choice([True, False])
        if is_length:
            cm = rng.randint(50, 950)
            m_val = Fraction(cm, 100)
            text = f"Convertire {cm} cm in metri."
            sol = f"1 m = 100 cm, quindi {cm} cm = {cm}/100 m = {frac_text(m_val)} m."
            latex = f"{cm}\\text{{ cm}} = {latex_frac(m_val)}\\text{{ m}}"
        else:
            deg = rng.randint(1, 180)
            minuti = rng.randint(0, 59)
            totale = deg * 60 + minuti
            text = f"Esprimere in soli primi (minuti sessagesimali) l'ampiezza {deg}° {minuti}'."
            sol = f"1° = 60'. {deg}° = {deg*60}'. Totale: {deg*60}' + {minuti}' = {totale}'."
            latex = f"{latex_deg(deg)}\\,{minuti}' = {totale}'"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo G2 - Triangoli ----

def lez_g2_1(rng, n):
    out = []
    for _ in range(n):
        choice = rng.choice(["scaleno", "isoscele", "equilatero"])
        a_ = rng.randint(3, 15)
        if choice == "equilatero":
            b_ = c_ = a_
        elif choice == "isoscele":
            b_ = a_
            c_ = rng.randint(3, 15)
            while c_ == a_:
                c_ = rng.randint(3, 15)
        else:
            b_, c_ = rng.randint(3, 15), rng.randint(3, 15)
            while len({a_, b_, c_}) < 3:
                b_, c_ = rng.randint(3, 15), rng.randint(3, 15)
        text = f"Un triangolo ha lati {a_} cm, {b_} cm e {c_} cm. Classificarlo rispetto ai lati."
        if a_ == b_ == c_:
            tipo = "equilatero"
        elif a_ == b_ or b_ == c_ or a_ == c_:
            tipo = "isoscele"
        else:
            tipo = "scaleno"
        sol = f"Confrontando le lunghezze dei lati, il triangolo è {tipo}."
        latex = f"a={a_}, \\ b={b_}, \\ c={c_}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g2_2(rng, n):
    out = []
    for _ in range(n):
        l1, l2, ang = rng.randint(4, 15), rng.randint(4, 15), rng.randint(20, 150)
        text = f"Due triangoli hanno un lato di {l1} cm, un lato di {l2} cm e l'angolo compreso di {ang}° rispettivamente congruenti. Sono congruenti? In base a quale criterio?"
        sol = "Sì, per il primo criterio di congruenza: due lati e l'angolo tra essi compreso rispettivamente congruenti."
        latex = f"{l1}, \\ {l2}, \\ {latex_deg(ang)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g2_3(rng, n):
    out = []
    for _ in range(n):
        l1, a1, a2 = rng.randint(4, 15), rng.randint(20, 80), rng.randint(20, 80)
        text = f"Due triangoli hanno un lato di {l1} cm congruente e i due angoli adiacenti, di {a1}° e {a2}°, rispettivamente congruenti. Sono congruenti? In base a quale criterio?"
        sol = "Sì, per il secondo criterio di congruenza: un lato e i due angoli a esso adiacenti rispettivamente congruenti."
        latex = f"{l1}, \\ {latex_deg(a1)}, \\ {latex_deg(a2)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g2_4(rng, n):
    out = []
    for _ in range(n):
        angle = rng.randint(30, 75)
        vertex = 180 - 2 * angle
        text = f"In un triangolo isoscele gli angoli alla base misurano {angle}° ciascuno. Calcolare l'angolo al vertice."
        sol = f"Somma angoli interni = 180°; angoli alla base congruenti.\nAngolo al vertice = 180° - 2·{angle}° = {vertex}°."
        latex = f"{latex_deg(180)} - 2\\cdot {latex_deg(angle)} = {latex_deg(vertex)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g2_5(rng, n):
    out = []
    for _ in range(n):
        a_, b_, c_ = rng.randint(4, 15), rng.randint(4, 15), rng.randint(4, 15)
        text = f"Due triangoli hanno tutti e tre i lati rispettivamente congruenti: {a_} cm, {b_} cm, {c_} cm. Sono congruenti? In base a quale criterio?"
        sol = "Sì, per il terzo criterio di congruenza: tre lati rispettivamente congruenti."
        latex = f"a={a_}, \\ b={b_}, \\ c={c_}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g2_6(rng, n):
    out = []
    for _ in range(n):
        a_, b_, c_ = rng.randint(3, 20), rng.randint(3, 20), rng.randint(3, 20)
        possible = (a_ + b_ > c_) and (a_ + c_ > b_) and (b_ + c_ > a_)
        text = f"Verificare se è possibile costruire un triangolo con lati {a_} cm, {b_} cm e {c_} cm."
        sol = (
            "Per la disuguaglianza triangolare, ogni lato deve essere minore della somma degli altri due.\n"
            f"Il triangolo {'è' if possible else 'non è'} costruibile."
        )
        latex = f"{a_}+{b_} > {c_}, \\ {a_}+{c_} > {b_}, \\ {b_}+{c_} > {a_}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo G3 - Rette perpendicolari e rette parallele ----

def lez_g3_1(rng, n):
    out = []
    for _ in range(n):
        angle = rng.randint(10, 80)
        compl = 90 - angle
        text = f"Un angolo acuto misura {angle}°. Quanto misura il suo complementare (in modo che la somma sia 90°)?"
        sol = f"Complementare di {angle}° = 90° - {angle}° = {compl}°."
        latex = f"{latex_deg(90)} - {latex_deg(angle)} = {latex_deg(compl)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g3_2(rng, n):
    out = []
    for _ in range(n):
        alpha = rng.randint(20, 160)
        text = f"Due rette parallele sono tagliate da una trasversale. Un angolo misura {alpha}°. Quanto misura l'angolo corrispondente?"
        sol = f"Gli angoli corrispondenti tra rette parallele sono congruenti.\nL'angolo corrispondente misura {alpha}°."
        latex = latex_deg(alpha)
        out.append(Exercise(text, sol, latex))
    return out


def lez_g3_3(rng, n):
    out = []
    for _ in range(n):
        alpha = rng.randint(20, 160)
        text = f"Due rette tagliate da una trasversale formano una coppia di angoli alterni interni entrambi di {alpha}°. Cosa si può concludere sulle due rette?"
        sol = "Se una trasversale forma con due rette una coppia di angoli alterni interni congruenti, le due rette sono parallele."
        latex = latex_deg(alpha)
        out.append(Exercise(text, sol, latex))
    return out


def lez_g3_4(rng, n):
    out = []
    for _ in range(n):
        sides = rng.randint(3, 10)
        total = (sides - 2) * 180
        text = f"Calcolare la somma degli angoli interni e la somma degli angoli esterni di un poligono convesso di {sides} lati."
        sol = f"Somma angoli interni = (n-2)·180° = {total}°.\nSomma angoli esterni = 360° (sempre, per un poligono convesso)."
        latex = f"(n-2)\\cdot {latex_deg(180)} = {latex_deg(total)}, \\quad {latex_deg(360)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g3_5(rng, n):
    out = []
    for _ in range(n):
        ipotenusa = rng.randint(8, 20)
        cateto = rng.randint(3, ipotenusa - 1)
        text = f"Due triangoli rettangoli hanno l'ipotenusa congruente ({ipotenusa} cm) e un cateto congruente ({cateto} cm). Sono congruenti? In base a quale criterio?"
        sol = "Sì: per il criterio di congruenza dei triangoli rettangoli, ipotenusa e un cateto rispettivamente congruenti implicano la congruenza."
        latex = f"{ipotenusa}, \\ {cateto}"
        out.append(Exercise(text, sol, latex))
    return out


# ---- Capitolo G4 - Parallelogrammi e trapezi ----

def lez_g4_1(rng, n):
    out = []
    for _ in range(n):
        base, lato, angolo = rng.randint(10, 40), rng.randint(5, 25), rng.randint(30, 150)
        perim = 2 * (base + lato)
        adj = 180 - angolo
        text = f"In un parallelogramma un lato misura {base} cm, il lato consecutivo {lato} cm e un angolo misura {angolo}°. Calcolare perimetro e angolo consecutivo."
        sol = f"Lati opposti congruenti: perimetro = 2·({base}+{lato}) = {perim} cm.\nAngoli consecutivi supplementari: 180° - {angolo}° = {adj}°."
        latex = f"P = 2({base}+{lato}) = {perim}, \\quad {latex_deg(180)} - {latex_deg(angolo)} = {latex_deg(adj)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g4_2(rng, n):
    out = []
    for _ in range(n):
        choice = rng.choice(["rettangolo", "quadrato", "rombo"])
        if choice == "rettangolo":
            b_, h_ = rng.randint(6, 30), rng.randint(4, 20)
            text = f"Un rettangolo ha base {b_} cm e altezza {h_} cm. Calcolare area e perimetro."
            sol = f"Area = {b_}·{h_} = {b_*h_} cm^2.\nPerimetro = 2·({b_}+{h_}) = {2*(b_+h_)} cm."
            latex = f"A = b\\cdot h = {b_}\\cdot {h_} = {b_*h_}"
        elif choice == "quadrato":
            l_ = rng.randint(4, 25)
            text = f"Un quadrato ha lato {l_} cm. Calcolare area, perimetro e diagonale (in forma esatta)."
            sol = f"Area = {l_}^2 = {l_**2} cm^2.\nPerimetro = 4·{l_} = {4*l_} cm.\nDiagonale = {l_}·√2 cm."
            latex = f"A = l^{{2}} = {l_}^{{2}} = {l_**2}"
        else:
            d1, d2 = rng.randint(6, 30), rng.randint(6, 30)
            area = Fraction(d1 * d2, 2)
            text = f"Un rombo ha diagonali {d1} cm e {d2} cm. Calcolare l'area."
            sol = f"Area = (d1·d2)/2 = ({d1}·{d2})/2 = {frac_text(area)} cm^2."
            latex = f"A = \\dfrac{{d_1 \\cdot d_2}}{{2}} = \\dfrac{{{d1}\\cdot {d2}}}{{2}} = {latex_frac(area)}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g4_3(rng, n):
    out = []
    for _ in range(n):
        b1 = rng.randint(20, 60)
        b2 = rng.randint(10, b1 - 2)
        side = rng.randint(8, 30)
        per = b1 + b2 + 2 * side
        text = f"Un trapezio isoscele ha basi {b1} cm e {b2} cm e lato obliquo {side} cm. Calcolare il perimetro."
        sol = f"Perimetro = {b1} + {b2} + {side} + {side} = {per} cm."
        latex = f"P = {b1} + {b2} + 2\\cdot {side} = {per}"
        out.append(Exercise(text, sol, latex))
    return out


def lez_g4_4(rng, n):
    out = []
    for _ in range(n):
        a_, b_, c_ = rng.randint(4, 15), rng.randint(4, 15), rng.randint(4, 15)
        d_val = Fraction(b_ * c_, a_)
        text = (
            f"Per il teorema di Talete, su una trasversale due segmenti misurano {a_} cm e {b_} cm; "
            f"sull'altra trasversale il segmento corrispondente al primo misura {c_} cm. Calcolare il segmento corrispondente al secondo."
        )
        sol = f"Per la proporzionalità: {a_} : {b_} = {c_} : x, quindi x = ({b_}·{c_})/{a_} = {frac_text(d_val)} cm."
        latex = f"{a_} : {b_} = {c_} : x"
        out.append(Exercise(text, sol, latex))
    return out


# --------------------------------------------------------------------------
# Registro lezione -> generatore
# --------------------------------------------------------------------------

LessonGenerator = Callable[[random.Random, int], list[Exercise]]

LESSON_GENERATORS: dict[tuple[str, int], LessonGenerator] = {
    ("1", 1): lez_1_1, ("1", 2): lez_1_2, ("1", 3): lez_1_3, ("1", 4): lez_1_4,
    ("1", 5): lez_1_5, ("1", 6): lez_1_6, ("1", 7): lez_1_7,

    ("2", 1): lez_2_1, ("2", 2): lez_2_2, ("2", 3): lez_2_3, ("2", 4): lez_2_4,
    ("2", 5): lez_2_5, ("2", 6): lez_2_6, ("2", 7): lez_2_7,

    ("3", 1): lez_3_1, ("3", 2): lez_3_2, ("3", 3): lez_3_3, ("3", 4): lez_3_4,
    ("3", 5): lez_3_5, ("3", 6): lez_3_6, ("3", 7): lez_3_7, ("3", 8): lez_3_8,
    ("3", 9): lez_3_9,

    ("4", 1): lez_4_1, ("4", 2): lez_4_2, ("4", 3): lez_4_3, ("4", 4): lez_4_4,

    ("5", 1): lez_5_1, ("5", 2): lez_5_2, ("5", 3): lez_5_3, ("5", 4): lez_5_4,

    ("6", 1): lez_6_1, ("6", 2): lez_6_2, ("6", 3): lez_6_3, ("6", 4): lez_6_4,

    ("7", 1): lez_7_1,
    # ("7", 2) "Piano cartesiano e grafici di funzioni": richiede un grafico, non disponibile.
    ("7", 3): lez_7_3, ("7", 4): lez_7_4, ("7", 5): lez_7_5, ("7", 6): lez_7_6,
    ("7", 7): lez_7_7, ("7", 8): lez_7_8,

    ("8", 1): lez_8_1, ("8", 2): lez_8_2, ("8", 3): lez_8_3, ("8", 4): lez_8_4,
    ("8", 5): lez_8_5, ("8", 6): lez_8_6, ("8", 7): lez_8_7, ("8", 8): lez_8_8,

    ("9", 1): lez_9_1, ("9", 2): lez_9_2, ("9", 3): lez_9_3, ("9", 4): lez_9_4,
    ("9", 5): lez_9_5,

    ("10", 1): lez_10_1, ("10", 2): lez_10_2, ("10", 3): lez_10_3, ("10", 4): lez_10_4,
    ("10", 5): lez_10_5, ("10", 6): lez_10_6, ("10", 7): lez_10_7, ("10", 8): lez_10_8,

    ("11", 1): lez_11_1, ("11", 2): lez_11_2,
    # ("11", 3) "Rappresentazioni grafiche dei dati": richiede un grafico, non disponibile.
    ("11", 4): lez_11_4, ("11", 5): lez_11_5,

    ("G1", 1): lez_g1_1, ("G1", 2): lez_g1_2, ("G1", 3): lez_g1_3, ("G1", 4): lez_g1_4,
    ("G1", 5): lez_g1_5, ("G1", 6): lez_g1_6,

    ("G2", 1): lez_g2_1, ("G2", 2): lez_g2_2, ("G2", 3): lez_g2_3, ("G2", 4): lez_g2_4,
    ("G2", 5): lez_g2_5, ("G2", 6): lez_g2_6,

    ("G3", 1): lez_g3_1, ("G3", 2): lez_g3_2, ("G3", 3): lez_g3_3, ("G3", 4): lez_g3_4,
    ("G3", 5): lez_g3_5,

    ("G4", 1): lez_g4_1, ("G4", 2): lez_g4_2, ("G4", 3): lez_g4_3, ("G4", 4): lez_g4_4,
}

UNAVAILABLE_REASON = "richiede una rappresentazione grafica (disegno/grafico), non producibile come testo"


# --------------------------------------------------------------------------
# Interfaccia interattiva
# --------------------------------------------------------------------------

def file_code(chapter_code: str) -> str:
    c = chapter_code.strip()
    if c.isdigit():
        return f"cap{int(c):02d}"
    return c


def lesson_key(chapter_code: str, lesson_number: int) -> tuple[str, int]:
    return (chapter_code.strip(), lesson_number)


def choose_chapter(chapters: list[Chapter]) -> Chapter:
    print("\nCapitoli disponibili:\n")
    for i, ch in enumerate(chapters, 1):
        n_available = sum(1 for les in ch.lessons if lesson_key(ch.code, les.number) in LESSON_GENERATORS)
        title_part = f" - {ch.title}" if ch.title else ""
        status = "" if n_available > 0 else "  [non selezionabile: nessuna lezione con esercizi disponibili]"
        print(f"{i}. Capitolo {ch.code}{title_part} ({n_available}/{len(ch.lessons)} lezioni con esercizi disponibili){status}")

    while True:
        raw = input("\nScegli UN capitolo (numero): ").strip()
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(chapters):
                ch = chapters[idx - 1]
                if any(lesson_key(ch.code, les.number) in LESSON_GENERATORS for les in ch.lessons):
                    return ch
                print("Capitolo non selezionabile: nessuna lezione ha un generatore di esercizi disponibile.")
                continue
        print("Scelta non valida, riprova.")


def choose_lessons(chapter: Chapter) -> list[Lesson]:
    available = [les for les in chapter.lessons if lesson_key(chapter.code, les.number) in LESSON_GENERATORS]
    unavailable = [les for les in chapter.lessons if lesson_key(chapter.code, les.number) not in LESSON_GENERATORS]

    print(f"\nLezioni del capitolo {chapter.code} - {chapter.title}:\n")
    for i, les in enumerate(available, 1):
        page_part = f" (p. {les.page})" if les.page else ""
        print(f"{i}. {les.title}{page_part}")

    if unavailable:
        print("\nNon selezionabili (nessun generatore di esercizi disponibile):")
        for les in unavailable:
            page_part = f" (p. {les.page})" if les.page else ""
            print(f"  - {les.title}{page_part} -> {UNAVAILABLE_REASON}")

    print("\nPuoi indicare più numeri separati da spazio o virgola (es. 1 3 4), oppure 'tutte'.")
    while True:
        raw = input("Scegli una o più lezioni: ").strip().lower()
        if raw in {"tutte", "all"}:
            return list(available)
        parts = re.split(r"[,\s]+", raw)
        idxs = []
        valid = True
        for p in parts:
            if not p:
                continue
            if not p.isdigit() or not (1 <= int(p) <= len(available)):
                valid = False
                break
            idxs.append(int(p))
        if valid and idxs:
            seen = sorted(set(idxs))
            return [available[i - 1] for i in seen]
        print("Scelta non valida, riprova.")


# --------------------------------------------------------------------------
# Scrittura dei file di output
# --------------------------------------------------------------------------

def build_lesson_block(lesson: Lesson, exercises: list[Exercise], with_solutions: bool) -> list[str]:
    page_part = f" (p. {lesson.page})" if lesson.page else ""
    lines = [f"## Lezione {lesson.number} - {lesson.title}{page_part}", ""]

    if with_solutions:
        lines += ["### Esercizi e soluzioni", ""]
        for i, ex in enumerate(exercises, 1):
            lines.append(f"#### Esercizio {i}")
            lines.append("")
            lines.append(ex.text)
            lines.append("")
            if ex.latex:
                lines.append(f"*{LATEX_NOTE}: ${ex.latex}$*")
                lines.append("")
            lines.append("Soluzione passo passo:")
            lines.append("")
            for line in ex.solution.splitlines():
                lines.append(f"- {line}" if line else "")
            lines.append("")
    else:
        lines += ["### Esercizi", ""]
        for i, ex in enumerate(exercises, 1):
            lines.append(f"{i}. {ex.text}")
            lines.append("")
            if ex.latex:
                lines.append(f"   *{LATEX_NOTE}: ${ex.latex}$*")
                lines.append("")

    return lines


def write_files(
    chapter: Chapter,
    lesson_exercise_pairs: list[tuple[Lesson, list[Exercise]]],
    out_dir: Path,
    per_lezione: bool,
) -> list[tuple[Path, Path]]:
    code = file_code(chapter.code)
    chap_heading = f"# Capitolo {chapter.code} - {chapter.title}" if chapter.title else f"# Capitolo {chapter.code}"
    no_sol_dir = out_dir / "esercizi_senza_soluzioni"
    sol_dir = out_dir / "esercizi_con_soluzioni"
    no_sol_dir.mkdir(parents=True, exist_ok=True)
    sol_dir.mkdir(parents=True, exist_ok=True)

    generated: list[tuple[Path, Path]] = []

    if per_lezione:
        for lesson, exercises in lesson_exercise_pairs:
            base = f"{code}_lez{lesson.number:02d}_{safe_slug(lesson.title)}"
            no_sol_lines = [chap_heading, ""] + build_lesson_block(lesson, exercises, False)
            sol_lines = [chap_heading, ""] + build_lesson_block(lesson, exercises, True)
            no_sol_path = no_sol_dir / f"{base}_esercizi.md"
            sol_path = sol_dir / f"{base}_soluzioni.md"
            no_sol_path.write_text("\n".join(no_sol_lines), encoding="utf-8")
            sol_path.write_text("\n".join(sol_lines), encoding="utf-8")
            generated.append((no_sol_path, sol_path))
    else:
        lesson_numbers = "-".join(f"{les.number:02d}" for les, _ in lesson_exercise_pairs)
        base = f"{code}_lez{lesson_numbers}"
        no_sol_lines = [chap_heading, ""]
        sol_lines = [chap_heading, ""]
        for lesson, exercises in lesson_exercise_pairs:
            no_sol_lines += build_lesson_block(lesson, exercises, False)
            sol_lines += build_lesson_block(lesson, exercises, True)
        no_sol_path = no_sol_dir / f"{base}_esercizi.md"
        sol_path = sol_dir / f"{base}_soluzioni.md"
        no_sol_path.write_text("\n".join(no_sol_lines), encoding="utf-8")
        sol_path.write_text("\n".join(sol_lines), encoding="utf-8")
        generated.append((no_sol_path, sol_path))

    return generated


# --------------------------------------------------------------------------
# Programma principale
# --------------------------------------------------------------------------

def load_programma() -> str:
    path = Path(PROGRAM_FILENAME)
    if not path.exists():
        print(f"Errore: file '{PROGRAM_FILENAME}' non trovato nella cartella corrente.")
        print("Il programma ha bisogno del file 'programma_studio.md' (indice di capitoli e lezioni) per funzionare.")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera esercizi navigando l'indice di programma_studio.md.")
    parser.add_argument("--n", type=int, default=8, help="Numero di esercizi da generare per ciascuna lezione selezionata.")
    parser.add_argument("--seed", type=int, default=None, help="Seed casuale per risultati riproducibili.")
    parser.add_argument("--out-dir", default="output_esercizi_matematica", help="Cartella di output.")
    parser.add_argument(
        "--per-lezione",
        action="store_true",
        help="Scrive un file separato per ciascuna lezione selezionata, invece di un unico file con tutte le lezioni scelte (comportamento di default).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text = load_programma()
    chapters, accessories = parse_programma(text)

    print_accessory_report(accessories)

    selectable = [c for c in chapters if any(lesson_key(c.code, les.number) in LESSON_GENERATORS for les in c.lessons)]
    if not selectable:
        print("Nessun capitolo con lezioni ed esercizi disponibili è stato trovato nel file.")
        return 1

    chapter = choose_chapter(chapters)
    lessons = choose_lessons(chapter)

    rng = random.Random(args.seed)
    out_dir = Path(args.out_dir)

    lesson_exercise_pairs: list[tuple[Lesson, list[Exercise]]] = []
    for lesson in lessons:
        generator = LESSON_GENERATORS[lesson_key(chapter.code, lesson.number)]
        exercises = generator(rng, args.n)
        lesson_exercise_pairs.append((lesson, exercises))

    generated = write_files(chapter, lesson_exercise_pairs, out_dir, args.per_lezione)

    print(f"\nGenerati {len(generated)} file di output in: {out_dir.resolve()}")
    for no_sol, sol in generated:
        print(f"- {no_sol}")
        print(f"- {sol}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
