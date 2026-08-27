#!/usr/bin/env python3
"""
Risolutore di Problemi di Matematica - Liceo Scientifico (1° - 5° anno)
Questo script dimostra l'uso di SymPy, NumPy e Matplotlib per risolvere problemi
tipici del programma scolastico italiano (equazioni, geometria analitica, derivate, integrali).

Uso da linea di comando:
    python math_solver.py [--problem N] [--no-plots]

Parametri:
    --problem N : Esegue solo il problema N (da 1 a 4). Se non specificato, li esegue tutti.
    --no-plots  : Disabilita la visualizzazione grafica (utile per ambienti headless).
"""

import sys
import argparse
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

def problema_1_algebra_biennio():
    """
    Problema 1 (1°/2° Anno - Biennio):
    Risoluzione di un'equazione di secondo grado parametrica o letterale,
    e scomposizione/semplificazione di espressioni algebriche.
    Utilizza SymPy per il calcolo simbolico esatto.
    """
    print("=" * 60)
    print(" PROBLEMA 1: Algebra e Equazioni (1°/2° Anno)")
    print("=" * 60)
    
    try:
        # Definizione delle variabili simboliche con SymPy
        # 'x' è l'incognita, 'k' è un parametro reale
        x = sp.Symbol('x')
        k = sp.Symbol('k', real=True)
        
        # Esempio di espressione algebrica da semplificare
        espressione = (x**2 - 4) / (x - 2) + k
        print(f"Espressione iniziale da semplificare: {espressione}")
        
        # .simplify() semplifica algebricamente l'espressione (es. scompone e semplifica il fattore comune)
        espressione_semplificata = sp.simplify(espressione)
        print(f"Risultato semplificato per x != 2: {espressione_semplificata}")
        
        # Risoluzione di un'equazione di secondo grado parametrica: x^2 - k*x + 4 = 0
        eq = sp.Eq(x**2 - k*x + 4, 0)
        print(f"Risoluzione dell'equazione parametrica: {eq}")
        
        # sp.solve() restituisce le soluzioni in forma simbolica rispetto a 'x'
        soluzioni = sp.solve(eq, x)
        print(f"Soluzioni in funzione del parametro k: {soluzioni}")
        
    except Exception as e:
        # Gestione "dolce" dell'errore (graceful exit)
        print(f"[ATTENZIONE] Si è verificato un problema durante la risoluzione algebrica: {e}")
        print("Uscita controllata dalla procedura di algebra.")
        return False
        
    print("Problema 1 completato con successo.\n")
    return True


def problema_2_geometria_analitica():
    """
    Problema 2 (3° Anno):
    Geometria Analitica del piano cartesiano.
    Intersezione tra retta e parabola e calcolo della distanza.
    Utilizza SymPy per il sistema e Matplotlib per la visualizzazione.
    """
    print("=" * 60)
    print(" PROBLEMA 2: Geometria Analitica - Rette e Parabole (3° Anno)")
    print("=" * 60)
    
    try:
        x, y = sp.symbols('x y')
        
        # Equazione della parabola: y = x^2 - 4x + 3
        parabola = sp.Eq(y, x**2 - 4*x + 3)
        # Equazione della retta: y = x - 1
        retta = sp.Eq(y, x - 1)
        
        print(f"Sistema non lineare:\n  1) {parabola}\n  2) {retta}")
        
        # sp.nonlinsolve o sp.solve risolvono sistemi di equazioni
        punti_intersezione = sp.solve((parabola, retta), (x, y))
        print(f"Punti di intersezione trovati: {punti_intersezione}")
        
        # Estrazione delle coordinate per il grafico
        # Valori di x per tracciare la curva
        x_vals = np.linspace(-1, 5, 400)
        y_parabola = x_vals**2 - 4*x_vals + 3
        y_retta = x_vals - 1
        
        # Restituiamo i dati per l'eventuale plotting esterno
        return {
            'x_vals': x_vals,
            'y_parabola': y_parabola,
            'y_retta': y_retta,
            'intersezioni': punti_intersezione
        }
        
    except Exception as e:
        print(f"[ATTENZIONE] Errore nel calcolo geometrico: {e}")
        print("Uscita controllata dalla procedura di geometria analitica.")
        return None
        
    print("Problema 2 completato con successo.\n")


def problema_3_trigonometria():
    """
    Problema 3 (4° Anno):
    Trigonometria - Identità ed equazioni trigonometriche.
    """
    print("=" * 60)
    print(" PROBLEMA 3: Trigonometria (4° Anno)")
    print("=" * 60)
    
    try:
        alpha = sp.Symbol('alpha')
        
        # Identità fondamentale: sin^2(alpha) + cos^2(alpha) == 1
        identita = sp.sin(alpha)**2 + sp.cos(alpha)**2
        semplificata = sp.simplify(identita)
        print(f"Verifica identità fondamentale sin^2(a) + cos^2(a): {semplificata}")
        
        # Risoluzione di un'equazione trigonometrica elementare: sin(alpha) = 1/2
        eq_trig = sp.Eq(sp.sin(alpha), sp.Rational(1, 2))
        sol_trig = sp.solve(eq_trig, alpha)
        print(f"Soluzioni dell'equazione sin(alpha) = 1/2 in radianti: {sol_trig}")
        
    except Exception as e:
        print(f"[ATTENZIONE] Errore nella risoluzione trigonometrica: {e}")
        print("Uscita controllata dalla procedura di trigonometria.")
        return False
        
    print("Problema 3 completato con successo.\n")
    return True


def problema_4_analisi_matematica():
    """
    Problema 4 (5° Anno):
    Calcolo Infinitesimale - Studio di funzione (limiti, derivate, integrali).
    """
    print("=" * 60)
    print(" PROBLEMA 4: Analisi Matematica - Limiti, Derivate e Integrali (5° Anno)")
    print("=" * 60)
    
    try:
        x = sp.Symbol('x')
        
        # Definizione di una funzione tipica da studio di funzione: f(x) = x^3 - 3*x^2 + 2
        f = x**3 - 3*x**2 + 2
        print(f"Funzione assegnata: f(x) = {f}")
        
        # 1. Calcolo dei limiti (es. a più infinito)
        limite_inf = sp.limit(f, x, sp.oo)
        print(f"Limiti per x -> +inf: {limite_inf}")
        
        # 2. Calcolo della derivata prima f'(x) per la ricerca di massimi/minimi
        derivata_prima = sp.diff(f, x)
        print(f"Derivata prima f'(x): {derivata_prima}")
        
        # Ricerca punti stazionari ponendo f'(x) = 0
        punti_stazionari = sp.solve(derivata_prima, x)
        print(f"Ascisse dei punti stazionari: {punti_stazionari}")
        
        # 3. Calcolo dell'integrale indefinito F(x) = int f(x) dx
        integrale_indefinito = sp.integrate(f, x)
        print(f"Integrale indefinito int f(x) dx: {integrale_indefinito} + C")
        
        # 4. Calcolo dell'integrale definito tra x = 0 e x = 2
        integrale_definito = sp.integrate(f, (x, 0, 2))
        print(f"Integrale definito int_0^2 f(x) dx: {integrale_definito}")
        
    except Exception as e:
        print(f"[ATTENZIONE] Errore nel calcolo di analisi matematica: {e}")
        print("Uscita controllata dalla procedura di analisi.")
        return False
        
    print("Problema 4 completato con successo.\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Risolutore di problemi di matematica per il liceo scientifico.")
    parser.add_argument("--problem", type=int, choices=[1, 2, 3, 4], help="Esegue uno specifico problema (1-4)")
    parser.add_argument("--no-plots", action="store_true", help="Disabilita la generazione dei grafici Matplotlib")
    args = parser.parse_args()
    
    print("Avvio del dimostratore di problemi di matematica - Liceo Scientifico\n")
    
    geo_data = None
    
    if args.problem is None or args.problem == 1:
        problema_1_algebra_biennio()
        
    if args.problem is None or args.problem == 2:
        geo_data = problema_2_geometria_analitica()
        
    if args.problem is None or args.problem == 3:
        problema_3_trigonometria()
        
    if args.problem is None or args.problem == 4:
        problema_4_analisi_matematica()
        
    # Se abbiamo dati geometrici e non è richiesto di saltare i grafici, mostriamo il grafico con Matplotlib
    if geo_data and not args.no_plots:
        try:
            print("Generazione del grafico con Matplotlib (Geometria Analitica)...")
            plt.figure(figsize=(8, 6))
            plt.plot(geo_data['x_vals'], geo_data['y_parabola'], label='Parabola: $y = x^2 - 4x + 3$', color='blue')
            plt.plot(geo_data['x_vals'], geo_data['y_retta'], label='Retta: $y = x - 1$', color='red')
            
            # Evidenziamo i punti di intersezione
            for pt in geo_data['intersezioni']:
                px, py = float(pt[0]), float(pt[1])
                plt.scatter([px], [py], color='green', zorder=5)
                plt.annotate(f"Intersezione ({px:.1f}, {py:.1f})", (px, py), textcoords="offset points", xytext=(0,10), ha='center')
                
            plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
            plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
            plt.title("Intersezione Parabola-Retta (Geometria Analitica 3° anno)")
            plt.xlabel("Asse x")
            plt.ylabel("Asse y")
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.legend()
            plt.tight_layout()
            
            # Mostriamo il grafico a schermo (se l'ambiente supporta GUI)
            plt.show()
        except Exception as plot_err:
            print(f"[NOTA] Impossibile aprire la finestra grafica (probabile ambiente non interattivo): {plot_err}")

    print("Esecuzione terminata correttamente.")

if __name__ == '__main__':
    main()
