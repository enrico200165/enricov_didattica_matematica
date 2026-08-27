# Documentazione: genera_esercizi_da_programma.py

Questo file spiega il programma a tre livelli diversi:

1. una guida semplice per chi lo usa, senza bisogno di conoscere la programmazione;
2. una spiegazione della struttura e dei meccanismi interni, per chi programma ma non vuole leggere il codice riga per riga;
3. una descrizione del codice vero e proprio, per chi deve aprirlo e modificarlo.

Nota su una scelta fatta in questa documentazione: invece di riscrivere il programma aggiungendo commenti dentro ogni funzione, ho preferito descrivere il codice qui, in una sezione dedicata. Il motivo è che un programma commentato e un programma documentato a parte tendono a "scollegarsi" nel tempo: se in futuro il codice cambia, è più facile dimenticarsi di aggiornare i commenti sparsi in 90 funzioni che aggiornare un'unica sezione di riferimento. Se in seguito preferisci comunque una versione del codice con i commenti inline, posso prepararla.

## 1. Guida per chi usa il programma

### Cosa fa questo programma

Il programma crea esercizi di matematica pronti da studiare, scegliendo tra gli argomenti di un libro di testo. Tu scegli un capitolo e una o più lezioni di quel capitolo, il programma inventa un certo numero di esercizi su misura per ciascuna lezione scelta, e li salva in due tipi di file: uno con solo le domande, uno con le domande e la soluzione spiegata passo passo.

### Cosa ti serve prima di iniziare

Nella stessa cartella dove si trova il file `genera_esercizi_da_programma.py` deve esserci anche un secondo file, chiamato esattamente `programma_studio.md`. È l'indice del libro di testo (i capitoli, le lezioni, le pagine): il programma lo legge sempre da lì. Se questo file manca, il programma te lo dice chiaramente e si chiude, senza generare nulla.

Serve anche Python installato sul computer, con la libreria `sympy` (serve per i calcoli con le formule). Si installa una sola volta, aprendo il terminale (su Windows si chiama "Prompt dei comandi" o "PowerShell") e scrivendo:

```
python.exe -m pip install sympy
```

Se il computer non riconosce il comando `python.exe`, prova con `python` al posto di `python.exe`.

### Come si avvia

Apri il terminale nella cartella dove si trovano i due file (`genera_esercizi_da_programma.py` e `programma_studio.md`) e scrivi:

```
python genera_esercizi_da_programma.py
```

### Cosa succede dopo l'avvio

Il programma ti mostra prima un elenco di eventuali "cose strane" trovate nel file del programma di studio, che non sono né capitoli né lezioni (per esempio le sezioni di "Approfondimenti" del libro): non è un errore, è solo un modo per farti sapere che quelle parti sono state viste ma ignorate.

Poi ti mostra l'elenco dei capitoli, numerati. Scrivi il numero del capitolo che vuoi e premi invio.

Subito dopo ti mostra le lezioni di quel capitolo, ciascuna con il numero di pagina del libro. Scrivi uno o più numeri separati da uno spazio (per esempio `2 5 6`) per scegliere più lezioni insieme, oppure scrivi `tutte` per sceglierle tutte.

A questo punto il programma genera gli esercizi e ti dice dove li ha salvati.

Nota: alcune pochissime lezioni del libro (quelle che richiedono un disegno o un grafico, come "Piano cartesiano e grafici di funzioni") non compaiono tra le lezioni scelte, perché il programma genera solo esercizi scritti in testo, non immagini. Vengono comunque mostrate nell'elenco con la scritta "non selezionabili", così sai che esistono ma non puoi generarci esercizi.

### Dove trovare i file generati

I file vengono salvati dentro una cartella chiamata `output_esercizi_matematica`, creata automaticamente accanto al programma. Dentro trovi due sottocartelle:

- `esercizi_senza_soluzioni`: solo le domande, utile per allenarti prima di controllare le risposte;
- `esercizi_con_soluzioni`: le stesse domande con la spiegazione di come si risolvono, passo passo.

Ogni file ha nel titolo il nome del capitolo e della lezione a cui appartiene, così è sempre chiaro da dove viene.

### Opzioni utili (facoltative)

Se scrivi solo `python genera_esercizi_da_programma.py`, il programma genera 8 esercizi per ogni lezione scelta. Puoi cambiare questo numero e altre impostazioni aggiungendo delle opzioni al comando:

```
python genera_esercizi_da_programma.py --n 5
```

genera 5 esercizi per lezione invece di 8.

```
python genera_esercizi_da_programma.py --seed 42
```

fa sì che, rilanciando il comando con lo stesso numero (`42` in questo caso), gli esercizi generati siano sempre gli stessi. Utile se vuoi rifare esattamente lo stesso compito un'altra volta.

```
python genera_esercizi_da_programma.py --out-dir compiti_di_settembre
```

salva i file in una cartella con un nome scelto da te, invece del nome predefinito.

Queste opzioni si possono anche combinare tra loro nello stesso comando.

## 2. Come funziona (struttura e meccanismi, per un programmatore)

Questa sezione descrive l'architettura del programma senza fare riferimento a righe di codice specifiche: descrive cosa fa ciascuna parte e come le parti comunicano tra loro.

### Panoramica del flusso

Il programma è organizzato in cinque fasi eseguite in sequenza:

1. **Caricamento**: viene verificata l'esistenza del file `programma_studio.md` nella cartella corrente; se manca, il programma termina subito con un messaggio chiaro, senza generare nulla e senza sollevare un'eccezione non gestita.
2. **Interpretazione (parsing)**: il contenuto testuale del file viene trasformato in una struttura dati navigabile: un elenco di capitoli, ciascuno con il proprio elenco di lezioni (numero, titolo, pagina), più un elenco separato di "contenuti accessori" (tutto ciò che non è stato riconosciuto come capitolo o lezione).
3. **Selezione interattiva**: l'utente sceglie un capitolo tra quelli disponibili, poi una o più lezioni all'interno di quel capitolo.
4. **Generazione**: per ciascuna lezione scelta, il programma richiama la funzione responsabile di produrre esercizi per quella specifica lezione (non per l'intero capitolo).
5. **Scrittura**: per ciascuna lezione vengono scritti due file Markdown, distinti solo per la presenza o assenza delle soluzioni, entrambi con capitolo, lezione e pagina riportati come intestazione.

### Il modello dei dati

Quattro strutture dati minimali rappresentano tutto ciò che serve:

- un **Esercizio**, che è semplicemente una coppia testo della domanda / testo della soluzione;
- una **Lezione**, con numero, titolo e pagina (la pagina può mancare, se il file di origine non la riporta);
- un **Capitolo**, con codice, titolo e la lista delle sue lezioni;
- un **elemento accessorio**, che registra un contenuto non riconosciuto insieme al contesto in cui è stato trovato (a quale capitolo appartiene, o se è comparso prima di ogni capitolo) e a una motivazione sintetica del perché non è stato considerato una lezione.

Nessuna di queste strutture contiene logica: sono solo contenitori di dati, letti e scritti da funzioni esterne.

### Il meccanismo di interpretazione del file

L'interpretazione avviene leggendo il file una riga alla volta e mantenendo una sola informazione di contesto: "in quale capitolo mi trovo adesso" (oppure "in nessun capitolo", se non se ne è ancora incontrato uno, o se l'ultima intestazione incontrata non era un capitolo riconosciuto).

Ogni riga viene fatta rientrare in una di quattro categorie, verificate in quest'ordine:

1. è l'intestazione di un capitolo riconosciuto, nel qual caso si apre un nuovo capitolo e da questo momento in poi il contesto corrente punta a lui;
2. è un'intestazione dello stesso livello ma non riconosciuta come capitolo (per esempio una sezione introduttiva del libro), nel qual caso il contesto corrente viene azzerato e la riga stessa viene registrata come contenuto accessorio;
3. se ci si trova dentro un capitolo, è una riga che rispetta lo schema di una lezione numerata, nel qual caso viene aggiunta alle lezioni del capitolo corrente;
4. in tutti gli altri casi, la riga viene registrata come contenuto accessorio, insieme a una motivazione scelta in base a parole chiave riconoscibili nel testo (per esempio "riepilogo", "teoria in sintesi", oppure il fatto che compaia nel blocco di attività ed approfondimenti); se nessuna parola chiave viene riconosciuta, la motivazione resta generica ("non corrisponde al formato di una lezione").

Il punto centrale di questo meccanismo è che ogni riga del file trova sempre una collocazione: o diventa una lezione, o diventa un elemento accessorio con una spiegazione. Non ci sono righe che vengono scartate silenziosamente: questo è ciò che permette di mostrare all'utente un resoconto di trasparenza su cosa non è stato interpretato come lezione.

### Il registro lezione → generatore

Il meccanismo che collega ogni lezione a un modo di generare esercizi è un semplice dizionario (una tabella di corrispondenza), che associa la coppia (codice del capitolo, numero della lezione) a una funzione capace di produrre esercizi per quella lezione specifica.

Questo registro è anche il meccanismo che stabilisce, in un solo punto, quali lezioni sono "disponibili" e quali no: una lezione compare come selezionabile nell'interfaccia se e solo se esiste una voce corrispondente nel registro. Le due lezioni che richiedono un grafico non hanno una voce nel registro, e per questo vengono automaticamente escluse dalla lista delle lezioni scelgibili, senza bisogno di un meccanismo separato per gestire l'eccezione: l'assenza dal registro è di per sé l'informazione "non disponibile".

Tutte le funzioni generatrici, indipendentemente da quanto siano diverse le une dalle altre nel contenuto matematico, condividono la stessa modalità di essere chiamate: ricevono un generatore di numeri casuali e un numero di esercizi da produrre, e restituiscono una lista di esercizi. Questa uniformità è ciò che permette al resto del programma (menu, scrittura dei file) di trattare tutte le quasi 90 lezioni allo stesso modo, senza bisogno di sapere nulla del loro contenuto specifico.

### La casualità e la riproducibilità

Un solo generatore di numeri casuali viene creato all'avvio del programma (a partire dal seed fornito, se presente) e viene passato in sequenza a ogni funzione generatrice invocata durante l'esecuzione. Questo significa che la sequenza di numeri prodotti dipende dall'ordine in cui le lezioni vengono generate nella singola esecuzione: a parità di seed, rieseguire lo stesso identico comando (stesso capitolo, stesse lezioni, nello stesso ordine, stesso numero di esercizi) restituisce sempre gli stessi esercizi; scegliere lezioni diverse o in un ordine diverso, anche con lo stesso seed, produce risultati diversi.

### La scrittura dei file di output

Per ogni lezione selezionata viene generata una lista di esercizi, e la stessa lista viene usata per produrre due file distinti: uno che elenca solo il testo delle domande, l'altro che alterna ogni domanda alla sua soluzione passo passo. In entrambi i file compare la stessa intestazione con capitolo, lezione e pagina, così i due file restano riconoscibili e tracciabili anche se vengono spostati o rinominati separatamente.

## 3. Descrizione del codice

Questa sezione descrive come è organizzato il file sorgente e cosa fa ciascuna sua parte, per chi deve aprirlo e modificarlo.

### Struttura generale del file, in ordine

1. Importazioni delle librerie usate: `argparse` per le opzioni a riga di comando, `math`, `random`, `re` (espressioni regolari), `sys`, `dataclasses`, `fractions.Fraction` (per i calcoli esatti con le frazioni), `pathlib.Path` (per i percorsi dei file), `statistics` (media, mediana, moda) e `sympy` (calcolo simbolico: espansione, fattorizzazione, divisione tra polinomi, semplificazione di frazioni algebriche).
2. Definizione delle quattro strutture dati (`Exercise`, `Lesson`, `Chapter`, `AccessoryItem`), tutte implementate come `dataclass`, cioè classi il cui unico scopo è contenere dati con un costruttore generato automaticamente.
3. Un gruppo di funzioni di supporto matematiche e di formattazione, riutilizzate da molte funzioni generatrici: conversione di un'espressione simbolica in testo leggibile, formattazione di una frazione, normalizzazione di un titolo per usarlo come nome di file, estrazione di un numero casuale diverso da zero, calcolo di MCD/mcm e dei divisori di un numero, verifica se una frazione ha una rappresentazione decimale finita.
4. Le due espressioni regolari e le funzioni di interpretazione del file (`programma_studio.md`): il riconoscimento delle intestazioni di capitolo, il riconoscimento delle righe di lezione, la classificazione dei contenuti accessori, la funzione che scandisce l'intero testo riga per riga applicando questa logica, e la funzione che stampa a schermo il resoconto dei contenuti non riconosciuti.
5. Il blocco più esteso del file: circa 90 funzioni generatrici di esercizi, una per lezione, raggruppate per capitolo con un commento di separazione all'inizio di ogni gruppo. Sono nominate in modo sistematico: `lez_<capitolo>_<lezione>` per le lezioni di algebra e statistica (per esempio `lez_6_3` per la lezione 3 del capitolo 6), `lez_g<capitolo>_<lezione>` per le lezioni di geometria (per esempio `lez_g2_4` per la lezione 4 del capitolo G2).
6. Il registro che associa ogni coppia (capitolo, lezione) alla funzione generatrice corrispondente, insieme a un breve testo che spiega perché due lezioni ne sono intenzionalmente prive.
7. Le funzioni dell'interfaccia interattiva: la normalizzazione del codice di un capitolo per costruire un nome di file valido, la funzione che mostra il menu dei capitoli e ne legge la scelta, la funzione che mostra il menu delle lezioni disponibili in un capitolo (escludendo quelle senza generatore, ma segnalandole comunque) e ne legge la scelta (anche multipla), e la funzione che scrive su disco i due file Markdown per una singola lezione.
8. Il programma principale: lettura delle opzioni a riga di comando, caricamento e interpretazione del file, stampa del resoconto dei contenuti accessori, menu di scelta del capitolo e delle lezioni, ciclo di generazione ed effettiva scrittura dei file, messaggio finale di riepilogo.

### Come sono scritte le singole funzioni generatrici

Ogni funzione generatrice segue lo stesso schema interno: un ciclo che si ripete tante volte quanti sono gli esercizi richiesti; a ogni iterazione vengono estratti alcuni valori casuali (numeri, o talvolta la scelta tra due o tre varianti dello stesso tipo di esercizio), quindi il risultato corretto viene calcolato con uno tra due strumenti, a seconda dei casi:

- aritmetica esatta con `Fraction`, quando il risultato è un numero razionale e occorre evitare arrotondamenti (equazioni, disequazioni, percentuali, operazioni tra frazioni);
- calcolo simbolico con `sympy`, quando sono coinvolte espressioni con lettere (monomi, polinomi, frazioni algebriche, funzioni), per svolgere in modo affidabile operazioni come lo sviluppo di un prodotto, la scomposizione in fattori, la divisione polinomiale o la semplificazione.

Il testo della domanda e il testo della soluzione vengono poi costruiti componendo i valori calcolati dentro delle stringhe, e restituiti insieme come un oggetto Esercizio.

### Cosa non fa questo codice (limiti noti)

- Non genera immagini o grafici: le due lezioni che li richiederebbero sono escluse dal registro, come spiegato nella sezione precedente, invece di essere approssimate con un esercizio non pertinente.
- Non ha una suite di test automatizzati salvata insieme al programma: la correttezza delle quasi 90 funzioni generatrici è stata verificata eseguendole ripetutamente con diversi seed durante lo sviluppo, ma modifiche future ai singoli generatori andrebbero controllate con lo stesso tipo di verifica manuale.
- Non gestisce input da riga di comando scorretti in modo evoluto (per esempio un valore non numerico passato a `--n`): in quel caso il programma termina mostrando l'errore standard prodotto dalla libreria delle opzioni a riga di comando, senza un messaggio personalizzato.
- Il livello di dettaglio degli esercizi generati non è uniforme su tutte le 90 lezioni: per gli argomenti prettamente di calcolo (equazioni, polinomi, frazioni algebriche) gli esercizi sono quantitativi; per alcuni argomenti più teorici (per esempio le prime lezioni introduttive di un capitolo, che nel libro sono spesso solo definizioni) l'esercizio generato è più concettuale ("vero o falso", "classifica", "verifica una proprietà") che di calcolo, perché è la forma più fedele possibile al contenuto reale di quella lezione.
