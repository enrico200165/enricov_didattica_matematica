---
title: "Python e le librerie per la matematica: panoramica"
---

# Python

Python è un linguaggio di programmazione di alto livello, interpretato e general purpose. Il codice viene eseguito riga per riga da un interprete, senza una fase separata di compilazione, e la sintassi è pensata per essere leggibile: l'indentazione definisce i blocchi, le istruzioni sono vicine al linguaggio naturale.

Caratteristiche rilevanti per lo studio della matematica:

- sintassi essenziale, adatta a chi inizia a programmare;  
- ampio ecosistema di librerie scientifiche, gratuite e open source;  
- esecuzione interattiva: un'espressione si scrive, si esegue e si ottiene subito il risultato;  
- stessi strumenti usati in ambito scientifico, universitario e industriale (analisi dei dati, machine learning, simulazione).  

Esempio minimo:

```python
x = 3
y = 2 * x**2 - 5
print(y)   # 13
```

# Ambiente di lavoro: notebook Jupyter

Un notebook Jupyter è un documento composto da celle di testo (in formato Markdown, con formule in LaTeX) e da celle di codice. Il codice di ogni cella viene eseguito singolarmente e il risultato, testo o grafico, compare subito sotto la cella. Un notebook unisce spiegazione, codice e risultati nello stesso file, ed è quindi adatto a documentare un'attività di laboratorio.

Si può usare in locale, dopo aver installato Python e Jupyter, oppure online tramite servizi che offrono notebook ospitati nel browser.

# Librerie

Una libreria è un insieme di funzioni già scritte e collaudate, che si importa con `import`. Le librerie usate negli esempi sono le seguenti.

## NumPy

NumPy fornisce l'array, una struttura che contiene molti numeri dello stesso tipo e permette di eseguire un'operazione su tutti gli elementi insieme, senza cicli espliciti. È la base numerica di quasi tutte le altre librerie scientifiche.

```python
import numpy as np

x = np.linspace(-3, 3, 7)     # 7 punti equidistanti tra -3 e 3
y = x**2                      # il quadrato di ogni elemento
print(y)
```

Usi tipici: calcolo di valori di una funzione su molti punti, operazioni su vettori e matrici (`np.linalg.det`, `np.linalg.solve`), funzioni matematiche (`np.sin`, `np.exp`, `np.log`).

## Matplotlib

Matplotlib è la libreria di riferimento per costruire grafici: grafici di funzioni, diagrammi a dispersione, istogrammi, figure geometriche. Il grafico si compone indicando i dati, gli assi, le etichette e gli elementi da evidenziare.

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-3, 3, 200)
plt.plot(x, x**2 - 2*x - 3)
plt.axhline(0, color="black", linewidth=0.8)
plt.grid(True)
plt.show()
```

Usi tipici: grafici di rette, parabole, circonferenze, funzioni goniometriche ed esponenziali; soluzione grafica di equazioni e sistemi come intersezione di curve.

## SymPy

SymPy è una libreria di calcolo simbolico: lavora con espressioni algebriche e non solo con numeri approssimati. Può semplificare espressioni, risolvere equazioni e sistemi, calcolare derivate e integrali, e restituisce risultati esatti, per esempio frazioni e radicali.

```python
from sympy import symbols, solve, sqrt, simplify

x = symbols("x")
print(solve(x**2 - 2, x))          # [-sqrt(2), sqrt(2)]
print(simplify(sqrt(8)))           # 2*sqrt(2)
```

Usi tipici: verificare un calcolo svolto a mano, risolvere equazioni e sistemi, calcolare determinanti, controllare identità goniometriche.

## pandas

pandas gestisce dati in forma di tabella (`DataFrame`): righe, colonne con nome, lettura da file CSV o da fogli di calcolo, selezione e filtro dei dati, calcolo di medie e altre statistiche.

```python
import pandas as pd

dati = pd.DataFrame({"t": [0, 1, 2, 3], "x": [0.0, 4.9, 19.6, 44.1]})
print(dati["x"].mean())
```

Usi tipici: tabelle di valori di una funzione, dati reali da interpolare con una retta o una parabola, confronto tra valori esatti e approssimati.

## SciPy

SciPy raccoglie algoritmi scientifici: ottimizzazione, interpolazione, integrazione numerica, statistica. Negli esempi sul modello esponenziale la funzione `curve_fit` determina i parametri di una curva che meglio approssima un insieme di dati.

## Moduli della libreria standard

- `math`: funzioni matematiche di base (`sqrt`, `sin`, `log`, `pi`);  
- `fractions`: numeri razionali in forma esatta;  
- `random`: generazione di numeri casuali, per esempio per costruire esercizi.  

## ipywidgets

ipywidgets aggiunge ai notebook controlli interattivi, come cursori (slider) e menu. Collegati a una funzione di disegno, permettono di variare un parametro, per esempio il coefficiente angolare di una retta, e vedere il grafico cambiare in tempo reale.

# Quale libreria per quale argomento

| Argomento | Librerie | Attività tipica |
|---|---|---|
| Algebra, equazioni e sistemi | SymPy, Matplotlib | risolvere e verificare, rappresentare le rette di un sistema |
| Retta e piano cartesiano | NumPy, Matplotlib, pandas | tracciare rette, retta di tendenza su dati |
| Parabola e circonferenza | NumPy, Matplotlib, SymPy | variare i coefficienti, tangenti, intersezioni |
| Goniometria | NumPy, Matplotlib, SymPy | circonferenza goniometrica, verifica di identità |
| Trigonometria | NumPy, Matplotlib | risoluzione di triangoli, problemi di misura |
| Esponenziali e logaritmi | NumPy, Matplotlib, SciPy, pandas | grafici, equazioni, modelli di crescita |

# Intelligenza artificiale generativa come supporto allo studio

Gli assistenti basati su modelli di linguaggio (per esempio Gemini e DeepSeek) producono testo in risposta a una richiesta, chiamata prompt. Possono spiegare un concetto in più modi, proporre esercizi, indicare dove si trova un errore in una risoluzione.

Un modello di linguaggio genera testo plausibile, non un risultato garantito corretto: può sbagliare calcoli e passaggi, anche con tono sicuro. Ogni risposta con contenuto matematico va quindi verificata con un secondo metodo indipendente, per esempio con SymPy o con un controllo numerico.

Gli stessi servizi si possono interrogare da Python tramite chiamate API: lo script invia il prompt, riceve la risposta e la confronta in automatico con il risultato calcolato da SymPy. Questo schema, in cui l'AI propone e il calcolo simbolico verifica, è usato nelle attività di generazione e verifica degli esercizi.

Indicazioni per formulare un prompt efficace:

- indicare l'argomento e il livello (classe, prerequisiti disponibili);  
- chiedere una spiegazione a passi, con un esempio svolto;  
- chiedere un esercizio senza soluzione e, dopo averlo svolto, farsi correggere la propria risoluzione;  
- chiedere di segnalare gli errori tipici su quell'argomento;  
- verificare sempre il risultato con un metodo indipendente.  
