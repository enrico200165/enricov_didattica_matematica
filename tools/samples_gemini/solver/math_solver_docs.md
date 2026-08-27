# Documentazione Ufficiale - Risolutore Matematico Liceo Scientifico (`math_solver.py`)

Questa guida descrive l'utilizzo, le funzionalità e l'architettura interna dello script Python `math_solver.py`, progettato per coprire i temi fondamentali di matematica del liceo scientifico dal primo al quinto anno tramite l'uso di librerie specializzate (`SymPy`, `NumPy`, `Matplotlib`).

---

## 1. Guida Utente (User Guide)

### Panoramica
`math_solver.py` è uno strumento didattico ed esplorativo che automatizza la risoluzione di problemi tipici dei programmi ministeriali del liceo scientifico italiano:
- **Biennio (1° e 2° anno):** Semplificazione di espressioni algebriche e risoluzione di equazioni letterali/parametriche.
- **Secondo Biennio e Triennio (3° - 5° anno):** Geometria analitica nel piano (sistemi retta-parabola), trigonometria (identità ed equazioni) e calcolo infinitesimale (limiti, derivate, massimi/minimi e integrali definiti/indefiniti).

### Requisiti di Sistema
Per eseguire lo script sono necessarie le seguenti librerie Python:
- `sympy` (Calcolo simbolico)
- `numpy` (Calcolo numerico e vettoriale)
- `matplotlib` (Visualizzazione grafica)

È possibile installarle tramite `pip`:
```bash
pip install sympy numpy matplotlib
```

### Come Usare lo Script (Parametri da Linea di Comando)
Lo script accetta argomenti opzionali tramite riga di comando per personalizzare l'esecuzione:

1. **Esecuzione Completa di Tutti i Problemi (Default):**
   Esegue in sequenza tutti gli esempi dal 1° al 5° anno e mostra il grafico finale.
   ```bash
   python math_solver.py
   ```

2. **Esecuzione di uno Specifico Problema (`--problem`):**
   Permette di isolare una singola annualità/argomento:
   - `--problem 1`: Algebra e equazioni (1°/2° anno)
   - `--problem 2`: Geometria analitica (3° anno)
   - `--problem 3`: Trigonometria (4° anno)
   - `--problem 4`: Analisi matematica e studio di funzione (5° anno)
   
   *Esempio:*
   ```bash
   python math_solver.py --problem 4
   ```

3. **Disattivazione dei Grafici (`--no-plots`):**
   Utile in ambienti privi di interfaccia grafica (server headless o container Docker) per evitare errori legati a display non disponibili:
   ```bash
   python math_solver.py --no-plots
   ```

---

## 2. Guida Programmatore (Programmer Guide)

### Architettura e Struttura del Codice
Lo script è organizzato in funzioni modulari, ciascuna dedicata a un argomento scolastico specifico. Il flusso di esecuzione è gestito centralmente dalla funzione `main()` tramite il modulo `argparse`.

- **Gestione del calcolo simbolico (`SymPy`):**
  Le variabili vengono dichiarate esplicitamente tramite `sp.Symbol('x')` o `sp.Symbol('k', real=True)`. Questo consente di preservare i valori esatti (es. frazioni e radici) senza gli errori di arrotondamento tipici della virgola mobile (`float`).
- **Gestione dell'uscita "dolce" (Graceful Exit):**
  Ciascuna funzione problematica è racchiusa in un blocco `try...except Exception as e`. Se si verifica un'anomalia (es. espressione non definita o fallimento del solutore), lo script intercetta l'eccezione, stampa una spiegazione comprensibile del problema ed esce in modo controllato dalla singola routine senza causare un crash anomalo dell'intero programma.

### Dettaglio delle Funzioni Principali
1. `problema_1_algebra_biennio()`:
   - Utilizza `sp.simplify()` per le semplificazioni algebriche e `sp.solve()` per ricavare le soluzioni in funzione del parametro $k$.
2. `problema_2_geometria_analitica()`:
   - Risolve un sistema non lineare tra una parabola e una retta. Restituisce un dizionario contenente i vettori numpy per il tracciamento grafico tramite Matplotlib.
3. `problema_3_trigonometria()`:
   - Verifica identità trigonometriche notevoli e risolve equazioni goniometriche elementari.
4. `problema_4_analisi_matematica()`:
   - Sfrutta `sp.limit()`, `sp.diff()` (derivata prima) e `sp.integrate()` (integrale indefinito e definito) per coprire i capisaldi del programma di quinta liceo.

### Estensibilità
Per aggiungere un nuovo problema (ad esempio di calcolo combinatorio o di geometria nello spazio):
1. Creare una nuova funzione `problema_5_nuovo_argomento()` seguendo lo schema protetto da `try...except`.
2. Aggiungere il nuovo numero alle scelte del parametro `--problem` nell'oggetto `argparse`.
3. Integrare la chiamata nella funzione `main()`.
