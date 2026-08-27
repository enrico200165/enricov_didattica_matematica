# Documentazione: genera_esercizi_matematica_primo_liceo.py

> Versione con supporto a 5 livelli di difficoltà (1 = più facile, 5 = più difficile).

## 1. Come si usa

Il programma è uno script a riga di comando: non ha interfaccia grafica, va lanciato da terminale con Python. Richiede la libreria `sympy`, che gestisce i calcoli simbolici (espansione di polinomi, fattorizzazione, semplificazione di frazioni algebriche).

Installazione della dipendenza:

```
py -m pip install sympy
```

Il programma produce, per ogni argomento scelto e per ogni livello di difficoltà scelto, due file in formato Markdown:

- un file con i soli testi degli esercizi, dentro la sottocartella `esercizi_senza_soluzioni`;
- un file con esercizi e soluzione passo passo, dentro la sottocartella `esercizi_con_soluzioni`.

Entrambe le sottocartelle vengono create automaticamente dentro la cartella di output (di default `output_esercizi_matematica`, personalizzabile).

### I cinque livelli di difficoltà

Ogni argomento viene generato su 5 livelli, numerati da 1 (più facile) a 5 (più difficile). Per default il programma genera tutti e 5 i livelli; con l'opzione `--levels` si può scegliere un sottoinsieme.

```
py genera_esercizi_matematica_primo_liceo.py --chapters 6 --levels 1 3 5 --n 5
```

Questo comando genera solo i livelli 1, 3 e 5 per l'argomento "Equazioni lineari", con 5 esercizi ciascuno. Il livello 3 corrisponde alla difficoltà del programma originale (prima dell'introduzione dei livelli), quindi resta un buon punto di riferimento "standard".

I file prodotti includono il livello nel nome, ad esempio:

```
esercizi_senza_soluzioni/cap06_equazioni_lineari_livello1_esercizi.md
esercizi_senza_soluzioni/cap06_equazioni_lineari_livello5_esercizi.md
```

Per capire in pratica la differenza, ecco lo stesso tipo di esercizio (equazione lineare) su tre livelli diversi:

- **Livello 1**: `1x + (-6) = -2x + (4)` — numeri piccoli, nessuna parentesi da sviluppare.
- **Livello 3**: `-4x + (-8) = 4x + (18)` — numeri più grandi, stessa struttura del livello 1.
- **Livello 5**: `5(x + (-4)) + 4x = -9(x + (2)) + (0)` — richiede prima di sviluppare le parentesi, poi ridurre e risolvere.

In generale la difficoltà cresce in due modi, a seconda dell'argomento:

- **numericamente**: gli intervalli da cui vengono estratti i numeri casuali si allargano (numeri più grandi, calcoli più lunghi);
- **strutturalmente**, solo per alcuni argomenti (equazioni, disequazioni, divisione tra polinomi, enti geometrici, triangoli, rette parallele, trapezi): ai livelli 4 e 5 viene richiesto un passaggio in più rispetto ai livelli 1-3 (ad esempio sviluppare una parentesi prima di risolvere, lavorare con tre segmenti invece di due, o calcolare anche l'area oltre al perimetro).

Per gli argomenti con più "sottotipi" di esercizio (ad esempio nel capitolo 2 la scelta fra operazioni con frazioni, percentuali e notazione scientifica), al livello 1 viene proposto solo il sottotipo più semplice; i sottotipi via via più complessi si sbloccano salendo di livello, fino a comparire tutti dal livello 3 in poi.

### Vedere l'elenco degli argomenti disponibili

```
py genera_esercizi_matematica_primo_liceo.py --list
```

Stampa a schermo il codice e il titolo di ogni argomento (ad esempio `cap06    Equazioni lineari`, `G3    Rette perpendicolari e rette parallele`), senza generare file.

### Generare tutti gli argomenti

```
py genera_esercizi_matematica_primo_liceo.py --all --n 8
```

Genera 8 esercizi per ciascuno dei 15 argomenti disponibili (11 di algebra, 4 di geometria), per un totale di 120 esercizi, distribuiti su 30 file (15 con soli esercizi, 15 con soluzioni).

### Generare solo alcuni argomenti

```
py genera_esercizi_matematica_primo_liceo.py --chapters 1 2 6 G1 --n 10 --seed 123
```

Genera 10 esercizi ciascuno per: numeri naturali/interi (capitolo 1), numeri razionali/reali (capitolo 2), equazioni lineari (capitolo 6) ed enti geometrici fondamentali (G1). I capitoli di algebra si indicano con un numero (`1`, `2`, ... oppure `cap01`, `cap02`, ...), quelli di geometria con la sigla `G1`-`G4`.

### Il parametro `--seed`

Se non specificato, ogni esecuzione genera esercizi diversi. Specificando `--seed 123` (un numero qualsiasi a scelta), la sequenza di numeri casuali usata è sempre la stessa: eseguendo due volte lo stesso comando con lo stesso seed si ottengono esattamente gli stessi esercizi. Utile per rigenerare una prova già assegnata, o per condividere con altri lo stesso set di esercizi.

### Il parametro `--out-dir`

Permette di scegliere dove salvare i file, ad esempio:

```
py genera_esercizi_matematica_primo_liceo.py --chapters 6 --out-dir compiti_settembre
```

### Generare un solo livello per tutti gli argomenti

```
py genera_esercizi_matematica_primo_liceo.py --all --n 10 --levels 2
```

Utile per costruire, ad esempio, un compito di recupero con esercizi tutti allo stesso livello di difficoltà su tutto il programma.

### Esempio di file prodotto (estratto)

File `esercizi_senza_soluzioni/cap06_equazioni_lineari_esercizi.md`:

```
# cap06 - Equazioni lineari

## Esercizi

1. Risolvere l'equazione: 4x + (-7) = -2x + (5).
```

File corrispondente `esercizi_con_soluzioni/cap06_equazioni_lineari_soluzioni.md`:

```
## Esercizio 1

Risolvere l'equazione: 4x + (-7) = -2x + (5).

Soluzione passo passo:

- Portare i termini con x a sinistra e i termini noti a destra: 4x - -2x = 5 - (-7).
- Ridurre: 6x = 12.
- Dividere per 6: x = (12)/(6).
- Risultato: x = 2.
```

## 2. Argomenti del programma scolastico coperti e loro provenienza

Il file copre il programma tipico del **primo anno di liceo scientifico** (primo biennio), diviso in due blocchi: algebra (undici argomenti, codici `cap01`-`cap11`) e geometria (quattro argomenti, codici `G1`-`G4`).

| Codice | Argomento | Contenuto disciplinare |
|---|---|---|
| cap01 | Numeri naturali e numeri interi | Espressioni aritmetiche con precedenza delle operazioni; MCD e mcm tra numeri interi |
| cap02 | Numeri razionali e numeri reali | Operazioni tra frazioni, percentuali, notazione scientifica |
| cap03 | Insiemi, logica e relazioni | Unione, intersezione e differenza tra insiemi; relazioni tra insiemi e concetto di funzione |
| cap04 | Monomi | Somma di monomi simili, prodotto di monomi, MCD e mcm tra monomi |
| cap05 | Polinomi | Prodotto tra polinomi (proprietà distributiva), prodotti notevoli (quadrato di binomio) |
| cap06 | Equazioni lineari | Risoluzione di equazioni di primo grado a un'incognita |
| cap07 | Funzioni | Funzione lineare, coefficiente angolare, intercetta |
| cap08 | Divisione tra polinomi e scomposizione in fattori | Divisione con quoziente e resto, scomposizione in fattori |
| cap09 | Frazioni algebriche ed equazioni fratte e letterali | Semplificazione di frazioni algebriche, condizioni di esistenza |
| cap10 | Disequazioni lineari | Disequazioni di primo grado, cambio di verso dividendo per un numero negativo |
| cap11 | Statistica | Tabelle di frequenza, media, mediana, moda, campo di variazione |
| G1 | Enti geometrici fondamentali | Segmenti consecutivi sulla stessa retta e loro somma |
| G2 | Triangoli | Somma degli angoli interni, triangolo isoscele |
| G3 | Rette perpendicolari e rette parallele | Angoli corrispondenti e supplementari con trasversale |
| G4 | Parallelogrammi e trapezi | Perimetro del trapezio isoscele |

Questa sequenza corrisponde, nell'ordine e nei contenuti, alla progressione standard usata dalla maggior parte dei libri di testo italiani per il primo anno di liceo scientifico: prima i numeri (naturali, interi, razionali, reali), poi insiemi e logica, poi il calcolo letterale (monomi, polinomi), le equazioni, le funzioni, la scomposizione in fattori, le frazioni algebriche, le disequazioni e la statistica; in parallelo, un percorso di geometria euclidea del piano (enti fondamentali, triangoli, rette parallele, quadrilateri).

**Sulla provenienza**: il file non contiene alcun riferimento esplicito (commento, citazione, nome di autore o editore) a un libro di testo specifico. La struttura dei capitoli non è quindi tratta letteralmente da un testo identificabile, ma ricalca l'indice tipico e comune a molti manuali scolastici italiani per il biennio del liceo scientifico, coerente con le Indicazioni Nazionali per i licei. Non è possibile stabilire con certezza, sulla sola base del codice, se chi lo ha scritto si sia ispirato a un manuale preciso oppure abbia semplicemente riprodotto la sequenza standard del primo anno.

## 3. Meccanismi interni (per chi deve leggere o modificare il codice)

### Struttura dei dati

Il programma usa due `dataclass` immutabili (`frozen=True`):

- `Exercise(text, solution)`: rappresenta un singolo esercizio, con il testo della consegna e la soluzione passo passo come stringa multi-riga.
- `Group(code, title, generator)`: rappresenta un argomento (capitolo). Il campo `generator` è un riferimento a una funzione (`Callable[[random.Random, int, int], list[Exercise]]`) che, dato un generatore di numeri casuali, un numero `n` e un livello di difficoltà (1-5), restituisce `n` oggetti `Exercise` calibrati su quel livello.

Il livello non è un campo di `Exercise`: è un parametro della *chiamata* al generatore, non una proprietà salvata in ogni singolo esercizio. Questo tiene la struttura dati semplice: chi scrive o modifica i generatori lavora con lo stesso oggetto `Exercise` di prima, e il livello entra in gioco solo nel calcolo dei parametri numerici e nella scelta del sottotipo di esercizio.

La lista globale `GROUPS` è il registro di tutti gli argomenti disponibili: ogni elemento associa un codice (`cap01`, `G1`, ecc.) alla relativa funzione generatrice `gen_capXX` / `gen_gX`. Aggiungere un nuovo argomento significa scrivere una nuova funzione `gen_*` con la stessa firma e aggiungerla a `GROUPS`.

### Funzioni di supporto

- `s(expr)`: converte un'espressione `sympy` in stringa, sostituendo `**` con `^` per una notazione più leggibile in italiano (es. `x^2` invece di `x**2`).
- `frac_text(q)`: formatta un oggetto `Fraction` come stringa (`"3/4"`, oppure solo `"5"` se il denominatore è 1).
- `safe_slug(text)`: normalizza il titolo di un gruppo per usarlo nel nome del file (minuscolo, sostituzione delle vocali accentate, ogni carattere non alfanumerico diventa `_`).
- `random_nonzero(rng, lo, hi)`: estrae interi casuali nell'intervallo finché non ottiene un valore diverso da zero; usata per evitare coefficienti nulli che renderebbero l'esercizio banale o degenere.
- `lcm_int`, `divisors`: funzioni matematiche elementari (minimo comune multiplo tramite `math.gcd`, elenco dei divisori per forza bruta).
- `scale_range(level, base_lo, base_hi)`: è il cuore del meccanismo di difficoltà numerica. Prende un intervallo "base" (quello usato dal programma originale, corrispondente al livello 3) e lo allarga o restringe in proporzione alla distanza del livello richiesto da 3: `fattore = 1 + (livello - 3) · 0.35`. Al livello 3 il fattore è 1 (intervallo invariato), al livello 1 si restringe (fattore 0.3), al livello 5 si allarga (fattore 1.7). L'intervallo resta centrato sullo stesso punto medio di quello originale. Ogni generatore chiama questa funzione al posto di scrivere direttamente `rng.randint(lo, hi)` con numeri fissi.
- `pick_choice(rng, level, choices)`: gestisce la difficoltà "di scelta" per gli argomenti che hanno più sottotipi di esercizio (ad esempio, nel capitolo 2, "frazione", "percentuale" o "notazione scientifica"). L'elenco `choices` va scritto dal sottotipo più semplice al più complesso: al livello 1 la funzione sceglie solo tra il primo elemento, al livello 2 tra i primi due, e così via, fino a includere l'intero elenco dal livello pari al numero di sottotipi in poi.
- `clamp(value, lo, hi)`: forza un valore dentro un intervallo, usata dopo `scale_range` quando il risultato calcolato potrebbe uscire da limiti fisicamente o didatticamente necessari (ad esempio un angolo di un triangolo non può essere 0° o superare 180°).

### Generazione degli esercizi

Ogni funzione `gen_capXX(rng, n, level)` / `gen_gX(rng, n, level)` segue lo stesso schema:

1. Ciclo `for _ in range(n)`.
2. Scelta del sottotipo di esercizio con `pick_choice(rng, level, [...])` al posto del semplice `rng.choice([...])` originale (ad esempio, per il capitolo 2: frazione, percentuale o notazione scientifica), così che ai livelli bassi siano disponibili solo i sottotipi più semplici.
3. Estrazione di parametri numerici casuali tramite `scale_range(level, base_lo, base_hi)` invece di intervalli fissi, in modo che l'ampiezza dei numeri cresca con il livello; per gli argomenti a struttura variabile, un ramo `if level <= 3: ... else: ...` sceglie inoltre tra la struttura originale (livelli 1-3) e una struttura più complessa riservata ai livelli 4-5.
4. Calcolo del risultato corretto, in due modi alternativi a seconda del tipo di esercizio:
   - aritmetica pura con `Fraction` per garantire risultati esatti (nessun errore di arrotondamento in virgola mobile) nei casi con frazioni, percentuali, equazioni, disequazioni;
   - calcolo simbolico con `sympy` (`sp.expand`, `sp.factor`, `sp.div`, `sp.cancel`, `sp.solve`) quando sono coinvolti polinomi, frazioni algebriche o equazioni con parentesi da sviluppare.
5. Costruzione della stringa di soluzione passo passo, con i valori calcolati inseriti tramite f-string; ogni riga della spiegazione diventerà un punto elenco nel file Markdown finale.
6. Creazione dell'oggetto `Exercise(text, sol)` e accumulo nella lista di output.

I simboli `x, y, a, b` sono definiti una sola volta a livello di modulo con `sp.symbols(...)`; si noti che `a` e `b` non risultano utilizzati in nessuna funzione generatrice al momento (simboli dichiarati ma non impiegati).

### Scrittura dei file

`write_group_files(group, level, exercises, out_dir)`:

- costruisce un nome base combinando codice, titolo normalizzato (`safe_slug`) e livello, ad esempio `cap06_equazioni_lineari_livello4`;
- crea (se non esistono) le due sottocartelle `esercizi_senza_soluzioni` e `esercizi_con_soluzioni`;
- costruisce riga per riga il contenuto dei due file come liste di stringhe, poi le unisce con `"\n".join(...)` e le scrive con `Path.write_text(..., encoding="utf-8")`;
- nel file con soluzioni, ogni riga della stringa `ex.solution` (separata internamente da `\n`) diventa un punto elenco Markdown (prefisso `- `), a meno che sia una riga vuota.

### Interfaccia a riga di comando

`parse_args()` definisce le opzioni con `argparse`: `--out-dir`, `--n`, `--seed`, `--all`, `--chapters` (a lunghezza variabile, `nargs="*"`), `--levels` (anch'essa `nargs="*"`, di tipo intero, default `[1,2,3,4,5]`), `--list`.

`normalize_code(code)` uniforma le diverse forme con cui si può indicare un argomento (`"1"`, `"cap1"`, `"cap01"` diventano tutti `"cap01"`; `"g1"` diventa `"G1"`); solleva `ValueError` (non gestita esplicitamente più in alto, quindi il programma termina con traceback) se il codice non è riconosciuto.

`main()`:

1. Se `--list` è presente, stampa i codici/titoli di `GROUPS` ed esce.
2. Costruisce un dizionario `group_by_code` (chiave: codice in minuscolo) per la ricerca rapida.
3. Determina la lista di gruppi da generare: tutti i `GROUPS` se è passato `--all` oppure se `--chapters` è vuoto (comportamento di default), altrimenti solo i gruppi corrispondenti ai codici indicati, nell'ordine in cui sono stati passati sulla riga di comando.
4. Normalizza e ordina l'elenco dei livelli richiesti (`sorted(set(args.levels))`) e verifica che ciascuno sia tra 1 e 5, sollevando `ValueError` altrimenti.
5. Crea **un solo** oggetto `random.Random(args.seed)`, condiviso da tutte le chiamate ai generatori nel doppio ciclo successivo (gruppo esterno, livello interno). Questo significa che, a parità di seed, il risultato per un dato argomento e un dato livello dipende anche dall'ordine e dal numero di combinazioni gruppo/livello generate prima nella stessa esecuzione: la riproducibilità è garantita solo ripetendo esattamente lo stesso comando (stessi argomenti, stesso ordine, stessi livelli, stesso `--n`, stesso `--seed`), non generando un singolo gruppo/livello isolatamente e aspettandosi lo stesso risultato ottenuto dentro una run con `--all`.
6. Per ciascuna combinazione (gruppo, livello) chiama `group.generator(rng, args.n, level)`, poi `write_group_files(group, level, exercises, out_dir)`, accumulando i percorsi dei file creati.
7. Stampa un riepilogo dei file generati.

### Punti di attenzione per eventuali modifiche

- Non c'è gestione esplicita degli errori sui codici capitolo non validi passati a `--chapters`, né sui livelli fuori range passati a `--levels`: in entrambi i casi si ottiene un `ValueError` non catturato e uno stack trace, non un messaggio d'errore amichevole.
- Non c'è escaping dei caratteri speciali Markdown nei testi generati (ad esempio `*`, `|`, `_`): con i dati numerici attuali non crea problemi visibili, ma va tenuto presente se si estendono i generatori con testo libero.
- Il modulo non include test automatici: la correttezza dei generatori più elaborati (in particolare `gen_cap8` e `gen_cap9`, che usano divisione polinomiale e cancellazione con `sympy`, e i rami di livello 4-5 di `gen_cap6`/`gen_cap10` che usano `sp.solve`) andrebbe verificata rieseguendo lo script con vari seed e controllando a campione i risultati.
- Per aggiungere un livello di difficoltà qualitativamente diverso a un argomento che oggi scala solo numericamente, il punto d'intervento è sempre lo stesso: aggiungere un ramo `if level <= 3: ... else: ...` (o più granulare) dentro la relativa funzione `gen_*`, seguendo lo schema già usato in `gen_cap6`, `gen_cap8`, `gen_cap10`, `gen_g1`, `gen_g2`, `gen_g3` e `gen_g4`.
