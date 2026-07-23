# Raccolta di risorse gratuite per matematica - Primo anno liceo scientifico

Data di preparazione: 23/06/2026.

Criterio usato: selezionare risorse gratuite, accessibili via web, adatte a uno studio autonomo del primo anno di liceo scientifico. Quando il sito non pubblica voti o recensioni numeriche, la dicitura "ottimi feedback" è stata interpretata in modo prudente come alta diffusione, reputazione didattica, stabilità della fonte e utilità scolastica verificabile.

Nota sui risolutori: usarli per controllare un procedimento già svolto, non per sostituire lo studio. Alcuni strumenti possono mostrare solo parte dei passaggi oppure richiedere account per funzioni avanzate.

## Uso del generatore Python

File separato: genera_esercizi_matematica_primo_liceo.py

Dipendenza richiesta:

    py -m pip install sympy

Generare tutti i gruppi di esercizi:

    py genera_esercizi_matematica_primo_liceo.py --all --n 8 --out-dir esercizi_matematica

Generare solo alcuni capitoli:

    py genera_esercizi_matematica_primo_liceo.py --chapters 1 2 6 G1 --n 10 --seed 123 --out-dir esercizi_matematica

Elencare i gruppi disponibili:

    py genera_esercizi_matematica_primo_liceo.py --list

Per ogni gruppo vengono create due cartelle:

- esercizi_senza_soluzioni
- esercizi_con_soluzioni

Ogni gruppo produce un file con soli esercizi e un file con esercizi più soluzioni passo passo.

## Capitolo 1 - Numeri naturali e numeri interi

Tutorial intuitivo e visuale:

- GeoGebra - I numeri interi - https://www.geogebra.org/m/zYr5awsQ - Attività visuale sulla rappresentazione e sul confronto dei numeri interi. Estensione: 1 pagina web interattiva.

Tutorial classico:

- GeoGebra - Matematica classico - https://www.geogebra.org/m/busucpzh - Raccolta classica di materiali su aritmetica, algebra e geometria di base. Estensione: raccolta web con attività collegate.

Risorse gratuite consigliate:

- Khan Academy - Matematica - https://it.khanacademy.org/math - Esercizi guidati e lezioni gratuite su aritmetica e algebra di base.
- GeoGebra Math Practice - https://www.geogebra.org/mathpractice/it/ - Esercizi interattivi con guida passo passo.
- GeoGebra Math Solver - https://www.geogebra.org/solver/en-GB - Risolutore con passaggi, utile per controllare calcoli e proprietà.
- WolframAlpha Equation Solver - https://www.wolframalpha.com/calculators/equation-solver-calculator - Risolutore utile per controllare espressioni ed equazioni semplici.
- Symbolab - https://www.symbolab.com/ - Risolutore con passaggi, da usare come controllo e non come sostituto dello svolgimento.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap01 --n 10 --out-dir esercizi_matematica

## Capitolo 2 - Numeri razionali e numeri reali

Tutorial intuitivo e visuale:

- GeoGebra - Frazioni e percentuali - https://www.geogebra.org/m/HjGAVbR2 - Attività visuale su frazioni, percentuali e passaggi tra rappresentazioni. Estensione: 1 pagina web interattiva.

Tutorial classico:

- WeSchool - Frazioni, numeri decimali e notazione scientifica - https://library.weschool.com/corso/frazioni-numeri-decimali-e-notazione-scientifica-spiegazioni-ed-esercizi-2970.html - Corso classico con spiegazioni ed esercizi su frazioni, decimali e notazione scientifica. Estensione: corso web con più lezioni.

Risorse gratuite consigliate:

- GeoGebra - Notazione scientifica - https://www.geogebra.org/m/ys5ynfk8 - Visualizzazione del passaggio alla notazione scientifica.
- WeSchool - Proporzionalità diretta e inversa - https://library.weschool.com/lezione/proporzionalita-diretta-inversa-proporzioni-proprieta-delle-proporzioni-inverse-dirette-15921.html - Lezione su proporzioni e proporzionalità. Durata dichiarata: 7 minuti.
- Khan Academy - Matematica - https://it.khanacademy.org/math - Esercizi gratuiti su frazioni, decimali, percentuali e potenze.
- GeoGebra Math Practice - https://www.geogebra.org/mathpractice/it/ - Allenamento guidato su calcoli con numeri razionali.
- GeoGebra Math Solver - https://www.geogebra.org/solver/en-GB - Controllo dei passaggi nei calcoli con frazioni e potenze.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap02 --n 10 --out-dir esercizi_matematica

## Capitolo 3 - Insiemi, logica e relazioni

Tutorial intuitivo e visuale:

- GeoGebra - Insiemi - https://www.geogebra.org/m/na7jf6c4 - Attività visuale su insiemi e rappresentazioni con diagrammi. Estensione: 1 pagina web interattiva.

Tutorial classico:

- LezioniDiMatematica - Insiemi - https://www.lezionidimatematica.net/indici/insiemi.htm - Indice classico con lezioni su insiemi, sottoinsiemi, operazioni, relazioni, equivalenza e ordine. Estensione: 1 pagina indice più lezioni collegate.

Risorse gratuite consigliate:

- GeoGebra - Relazioni e funzioni - https://www.geogebra.org/m/PecCCtsR - Attività interattiva su relazioni e funzioni.
- GeoGebra - Relazioni e funzioni - https://www.geogebra.org/m/sns7desj - Seconda attività visuale per distinguere relazione e funzione.
- Khan Academy - Matematica - https://it.khanacademy.org/math - Materiali gratuiti di base per logica matematica e funzioni.
- GeoGebra Math Practice - https://www.geogebra.org/mathpractice/it/ - Esercizi guidati, utile per parti numeriche e funzionali del capitolo.
- WolframAlpha - https://www.wolframalpha.com/ - Strumento di controllo per relazioni, insiemi finiti e funzioni semplici.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap03 --n 10 --out-dir esercizi_matematica

## Capitolo 4 - Monomi

Tutorial intuitivo e visuale:

- GeoGebra - Monomi e polinomi - https://www.geogebra.org/m/vWRjFpfe - Raccolta visuale su monomi, polinomi e operazioni. Estensione: 1 pagina web interattiva.

Tutorial classico:

- LezioniDiMatematica - Monomi - https://www.lezionidimatematica.net/indici/monomi.htm - Lezioni classiche su definizione, grado, operazioni, MCD e mcm di monomi. Estensione: 1 pagina indice più lezioni collegate.

Risorse gratuite consigliate:

- GeoGebra Math Practice - https://www.geogebra.org/mathpractice/it/ - Esercizi guidati per il calcolo letterale.
- GeoGebra Math Solver - https://www.geogebra.org/solver/en-GB - Controllo dei passaggi nelle operazioni tra monomi.
- Symbolab - https://www.symbolab.com/ - Risolutore algebrico con passaggi per espressioni letterali.
- Khan Academy - Matematica - https://it.khanacademy.org/math - Materiali su algebra introduttiva e manipolazione simbolica.
- Microsoft Math Solver - https://mathsolver.microsoft.com/ - Risolutore gratuito utile per controllare calcoli algebrici semplici.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap04 --n 10 --out-dir esercizi_matematica

## Capitolo 5 - Polinomi

Tutorial intuitivo e visuale:

- GeoGebra - Prodotti notevoli - https://www.geogebra.org/m/s9MyDqnJ - Attività visuale per interpretare geometricamente i prodotti notevoli. Estensione: 1 pagina web interattiva.

Tutorial classico:

- LezioniDiMatematica - Polinomi - https://www.lezionidimatematica.net/indici/polinomi.htm - Lezioni classiche su definizione, operazioni tra polinomi e prodotti notevoli. Estensione: 1 pagina indice più lezioni collegate.

Risorse gratuite consigliate:

- Matematika - Prodotti notevoli - https://www.matematika.it/public/esercizi/13/03_12_prodotti_notevoli_7_3.pdf - Esercizi PDF sui prodotti notevoli. Estensione: 13 pagine.
- UbiMath - Prodotti notevoli - https://www.ubimath.org/letterale/CalcoloLetterale_EserciziProdottiNotevoli_UbiMath.pdf - Schede gratuite di esercizi sui prodotti notevoli.
- GeoGebra Math Solver - https://www.geogebra.org/solver/en-GB - Controllo di sviluppi e semplificazioni.
- Symbolab - https://www.symbolab.com/ - Risolutore per espansioni, prodotti notevoli e semplificazioni.
- Khan Academy - Matematica - https://it.khanacademy.org/math - Percorsi gratuiti di algebra introduttiva.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap05 --n 10 --out-dir esercizi_matematica

## Capitolo 6 - Equazioni lineari

Tutorial intuitivo e visuale:

- GeoGebra - Equazioni lineari - https://www.geogebra.org/m/faMEBDHu - Attività visuale per collegare equazioni lineari, passaggi algebrici e rappresentazione. Estensione: 1 pagina web interattiva.

Tutorial classico:

- LezioniDiMatematica - Equazioni di primo grado - https://www.lezionidimatematica.net/indici/equazioni1.htm - Lezioni classiche sui principi di equivalenza, equazioni intere e problemi. Estensione: 1 pagina indice più lezioni collegate.

Risorse gratuite consigliate:

- Matematika - Equazioni di primo grado numeriche intere - https://www.matematika.it/public/esercizi/13/03_21_equazioni_primo_grado_7_8.pdf - Esercizi PDF su equazioni di primo grado. Estensione: 28 pagine.
- GeoGebra - Equazioni lineari, argomento - https://www.geogebra.org/t/linear-equation?lang=it - Raccolta di attività su equazioni lineari.
- GeoGebra Math Practice - https://www.geogebra.org/mathpractice/it/ - Esercizi guidati con feedback passo passo.
- WolframAlpha Equation Solver - https://www.wolframalpha.com/calculators/equation-solver-calculator - Risolutore per controllare soluzioni di equazioni.
- Microsoft Math Solver - https://mathsolver.microsoft.com/ - Risolutore gratuito per equazioni e passaggi.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap06 --n 10 --out-dir esercizi_matematica

## Capitolo 7 - Funzioni

Tutorial intuitivo e visuale:

- GeoGebra - Funzioni lineari - https://www.geogebra.org/m/GKexBqxs - Attività visuale su grafico, coefficiente angolare e intercetta. Estensione: 1 pagina web interattiva.

Tutorial classico:

- LezioniDiMatematica - Equazione della retta - https://www.lezionidimatematica.net/indici/equazione_retta.htm - Lezioni classiche su piano cartesiano, retta, coefficiente angolare e grafici. Estensione: 1 pagina indice più lezioni collegate.

Risorse gratuite consigliate:

- GeoGebra - Proporzionalità diretta e inversa - https://www.geogebra.org/m/NrXfG3rd - Attività visuale su proporzionalità e grafici.
- GeoGebra Math Practice - https://www.geogebra.org/mathpractice/it/ - Esercizi guidati per funzioni e grafici.
- Khan Academy - Geometria e funzioni - https://it.khanacademy.org/math - Materiali gratuiti su piano cartesiano e funzioni.
- WolframAlpha - https://www.wolframalpha.com/ - Controllo di grafici, valori di funzione e intersezioni.
- GeoGebra Classic - https://www.geogebra.org/classic - Strumento gratuito per disegnare grafici e verificare funzioni.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap07 --n 10 --out-dir esercizi_matematica

## Capitolo 8 - Divisione tra polinomi - Scomposizione in fattori

Tutorial intuitivo e visuale:

- GeoGebra - Scomposizione di polinomi - https://www.geogebra.org/m/zkzbp9ha - Attività visuale sulla fattorizzazione e sul riconoscimento dei fattori. Estensione: 1 pagina web interattiva.

Tutorial classico:

- LezioniDiMatematica - Polinomi - https://www.lezionidimatematica.net/indici/polinomi.htm - Lezioni classiche su polinomi, divisione e prodotti notevoli utili alla scomposizione. Estensione: 1 pagina indice più lezioni collegate.

Risorse gratuite consigliate:

- GeoGebra Math Solver - https://www.geogebra.org/solver/en-GB - Risolutore per controllare divisioni, espansioni e fattorizzazioni.
- Symbolab - https://www.symbolab.com/ - Risolutore algebrico per fattorizzazioni e divisioni tra polinomi.
- WolframAlpha - https://www.wolframalpha.com/ - Controllo di fattorizzazioni, zeri e divisioni polinomiali.
- UbiMath - Prodotti notevoli - https://www.ubimath.org/letterale/CalcoloLetterale_EserciziProdottiNotevoli_UbiMath.pdf - Esercizi utili per riconoscere le scomposizioni da prodotti notevoli.
- GeoGebra Classic - https://www.geogebra.org/classic - Strumento grafico per verificare zeri e fattori di polinomi.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap08 --n 10 --out-dir esercizi_matematica

## Capitolo 9 - Frazioni algebriche ed equazioni fratte e letterali

Tutorial intuitivo e visuale:

- GeoGebra - Frazioni algebriche - https://www.geogebra.org/m/k7be3793 - Attività visuale sulle frazioni algebriche e sulle condizioni di esistenza. Estensione: 1 pagina web interattiva.

Tutorial classico:

- LezioniDiMatematica - Frazioni algebriche - https://www.lezionidimatematica.net/indici/frazioni_algebriche.htm - Lezioni classiche su frazioni algebriche, semplificazione e operazioni. Estensione: 1 pagina indice più lezioni collegate.

Risorse gratuite consigliate:

- GeoGebra - Equazioni frazionarie - https://www.geogebra.org/m/VcFU2a2U - Attività interattiva sulle equazioni fratte.
- Matematika - Frazioni algebriche - https://www.matematika.it/public/esercizi/13/03_20_frazioni_algebriche_7_0.pdf - Esercizi PDF su frazioni algebriche. Estensione: 34 pagine.
- GeoGebra Math Solver - https://www.geogebra.org/solver/en-GB - Controllo di semplificazioni ed equazioni fratte.
- Symbolab - https://www.symbolab.com/ - Risolutore per espressioni razionali ed equazioni fratte.
- WolframAlpha Equation Solver - https://www.wolframalpha.com/calculators/equation-solver-calculator - Controllo delle soluzioni e delle eventuali esclusioni.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap09 --n 10 --out-dir esercizi_matematica

## Capitolo 10 - Disequazioni lineari

Tutorial intuitivo e visuale:

- GeoGebra - Equazioni e disequazioni con rappresentazione grafica - https://www.geogebra.org/m/zz9RDH3t - Attività visuale per collegare disequazioni e intervalli sulla retta. Estensione: 1 pagina web interattiva.

Tutorial classico:

- LezioniDiMatematica - Disequazioni di primo grado - https://www.lezionidimatematica.net/indici/disequazioni1.htm - Lezioni classiche su disequazioni intere, principi e intervalli di soluzione. Estensione: 1 pagina indice più lezioni collegate.

Risorse gratuite consigliate:

- GeoGebra - Disequazioni lineari - https://www.geogebra.org/m/vydNFgnc - Attività interattiva sulle disequazioni lineari.
- GeoGebra - Soluzione grafica di una disequazione - https://www.geogebra.org/m/crq4EEe6 - Visualizzazione grafica dell’insieme soluzione.
- LezioniDiMatematica - Sistemi di disequazioni - https://www.lezionidimatematica.net/indici/sistemi_dis1.htm - Lezioni sui sistemi di disequazioni.
- Zanichelli - Disequazioni lineari - https://staticmy.zanichelli.it/catalogo/assets/9788808942739_04_CAP.pdf - Capitolo PDF su disequazioni lineari.
- GeoGebra Math Solver - https://www.geogebra.org/solver/en-GB - Controllo dei passaggi e dell’intervallo soluzione.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap10 --n 10 --out-dir esercizi_matematica

## Capitolo 11 - Statistica

Tutorial intuitivo e visuale:

- GeoGebra - Media, mediana e moda - https://www.geogebra.org/m/zgwupsnd - Attività visuale per comprendere indici di posizione. Estensione: 1 pagina web interattiva.

Tutorial classico:

- HubScuola - Frequenze, grafici e indici statistici - https://campus.hubscuola.it/discipline-scientifiche/matematica/frequenze-e-grafici-indici-statistici/ - Lezione classica su frequenze, grafici e indici statistici. Estensione: 1 pagina web.

Risorse gratuite consigliate:

- GeoGebra - Sintesi dei dati statistici - https://www.geogebra.org/m/fpktzuud - Attività interattiva su tabelle e sintesi dei dati.
- GeoGebra - Probability and Statistics - https://www.geogebra.org/m/wqq69srx - Raccolta di attività su statistica e probabilità.
- UbiMath - Tabelle e grafici statistici - https://www.ubimath.org/statistica/StatisticaTabelleGraficiEsercizi_UbiMath.pdf - Schede gratuite di esercizi su tabelle e grafici.
- Zanichelli - Media, mediana e moda - https://online.scuola.zanichelli.it/bergamini-files/Biennio/Recupero/bergamini_statistica_R2_ALFAVB.pdf - Scheda PDF di recupero sugli indici statistici.
- GeoGebra Classic - https://www.geogebra.org/classic - Strumento gratuito per grafici statistici semplici.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters cap11 --n 10 --out-dir esercizi_matematica

## Capitolo online - Il coding

Tutorial intuitivo e visuale:

- Google Colab - https://developers.google.com/colab - Ambiente online per scrivere codice, testo, formule e grafici nello stesso documento. Estensione: 1 pagina web introduttiva più notebook collegati.

Tutorial classico:

- Python - Tutorial ufficiale in italiano - https://docs.python.org/it/3/tutorial/index.html - Tutorial ufficiale su sintassi, tipi, strutture dati, funzioni e moduli. Estensione: manuale web articolato in capitoli.

Risorse gratuite consigliate:

- Python.org - Documentazione ufficiale - https://www.python.org/doc/ - Documentazione e guide ufficiali di Python.
- Python 3.14 - Documentazione ufficiale - https://docs.python.org/ - Manuale ufficiale aggiornato di Python.
- GeoGebra Classic - https://www.geogebra.org/classic - Strumento gratuito per integrare geometria, algebra e grafici.
- GeoGebra Math Practice - https://www.geogebra.org/mathpractice/it/ - Ambiente guidato utile per collegare esercizi e verifica automatica.
- Khan Academy - Matematica - https://it.khanacademy.org/math - Esercizi interattivi da affiancare a piccoli script Python.

Per questo capitolo usare direttamente il generatore Python allegato come esempio di coding applicato alla matematica.

## Capitolo G1 - Enti geometrici fondamentali

Tutorial intuitivo e visuale:

- GeoGebra - Enti geometrici fondamentali - https://www.geogebra.org/m/RUrVq7sB - Attività visuale su punto, retta, piano, segmenti e angoli. Estensione: 1 pagina web interattiva.

Tutorial classico:

- UbiMath - Geometria di base - https://www.ubimath.org/geometriabasi/ - Raccolta di schede ed esercizi su enti geometrici, segmenti e angoli. Estensione: sezione web con materiali PDF collegati.

Risorse gratuite consigliate:

- GeoGebra - Enti primitivi - https://www.geogebra.org/m/Z6xyqmsq - Attività visuale sugli enti primitivi della geometria.
- GeoGebra - Geometria euclidea - https://www.geogebra.org/m/ReXeaBpX - Raccolta di attività su geometria euclidea.
- Zanichelli - Enti geometrici fondamentali - https://staticmy.zanichelli.it/catalogo/assets/9788808803269_04_CAP.pdf - Capitolo PDF su enti geometrici e prime proprietà.
- GeoGebra Classic - https://www.geogebra.org/classic - Strumento per costruire punti, rette, segmenti e angoli.
- Khan Academy - Geometry - https://it.khanacademy.org/math/geometry - Materiali gratuiti di geometria.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters G1 --n 10 --out-dir esercizi_matematica

## Capitolo G2 - Triangoli

Tutorial intuitivo e visuale:

- GeoGebra - Criteri di congruenza dei triangoli - https://www.geogebra.org/m/WP256nte - Attività visuale per osservare quando due triangoli sono congruenti. Estensione: 1 pagina web interattiva.

Tutorial classico:

- Matematika - Criteri di congruenza dei triangoli - https://www.matematika.it/public/esercizi/10/04_02_criteri_congruenza_3_6.pdf - Scheda PDF con esercizi sui criteri di congruenza. Estensione: PDF scolastico.

Risorse gratuite consigliate:

- GeoGebra - Triangoli e criteri di congruenza - https://www.geogebra.org/m/bvd7ppym - Attività interattiva sui criteri di congruenza.
- GeoGebra - Terzo criterio di congruenza - https://www.geogebra.org/m/pbjVuppQ - Attività specifica sul terzo criterio.
- UbiMath - Triangoli, problemi e angoli - https://www.ubimath.org/triangoli/TriangoliProblemi_Angoli_UbiMath.pdf - Esercizi PDF su triangoli e angoli.
- Zanichelli - Triangoli e congruenza - https://online.scuola.zanichelli.it/bergamini-files/Biennio/Esercizi/bergamini_triangoli_E1_G2B.pdf - Esercizi PDF sui triangoli.
- GeoGebra Classic - https://www.geogebra.org/classic - Strumento per costruire triangoli e verificare proprietà.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters G2 --n 10 --out-dir esercizi_matematica

## Capitolo G3 - Rette perpendicolari e rette parallele

Tutorial intuitivo e visuale:

- GeoGebra - Rette perpendicolari e parallele - https://www.geogebra.org/m/bGJFftWB - Attività visuale su costruzioni, parallelismo e perpendicolarità. Estensione: 1 pagina web interattiva.

Tutorial classico:

- Matematica in rete - Geometria, rette e angoli - https://matematicainrete.it/assets/appunti/Umanistico_1/U_1.7.Geometria.pdf - Appunti PDF classici su rette, angoli e geometria piana. Estensione: PDF.

Risorse gratuite consigliate:

- GeoGebra - Rette parallele e angoli - https://www.geogebra.org/m/ZezNun2E - Attività interattiva sugli angoli formati da parallele e trasversale.
- GeoGebra - Appunti di geometria - https://www.geogebra.org/m/d94BSXkz - Raccolta con attività su rette parallele e perpendicolari.
- GeoGebra Classic - https://www.geogebra.org/classic - Strumento per costruzioni con rette, angoli e trasversali.
- Khan Academy - Geometry - https://it.khanacademy.org/math/geometry - Materiali gratuiti su geometria piana.
- GeoGebra Math Practice - https://www.geogebra.org/mathpractice/it/ - Allenamento guidato per parti numeriche con angoli.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters G3 --n 10 --out-dir esercizi_matematica

## Capitolo G4 - Parallelogrammi e trapezi

Tutorial intuitivo e visuale:

- GeoGebra - Parallelogrammi - https://www.geogebra.org/m/MGpSP3tM - Attività visuale sulle proprietà dei parallelogrammi. Estensione: 1 pagina web interattiva.

Tutorial classico:

- UbiMath - Parallelogramma - https://www.ubimath.org/quadrilateri/Quadrilateri_Parallelogramma_UbiMath.pdf - Scheda PDF classica con esercizi sui parallelogrammi. Estensione: PDF.

Risorse gratuite consigliate:

- UbiMath - Trapezio - https://www.ubimath.org/quadrilateri/Quadrilateri_Trapezio_UbiMath.pdf - Scheda PDF con esercizi sui trapezi.
- GeoGebra - Teorema di Talete - https://www.geogebra.org/m/erbzrmkd - Attività visuale sul teorema di Talete.
- GeoGebra - Teorema di Talete, prima parte - https://www.geogebra.org/m/FcKP77kr - Attività interattiva di costruzione e osservazione.
- GeoGebra - Parallelogrammi, Talete e triangoli simili - https://www.geogebra.org/m/kVgxq9E8 - Raccolta di attività collegate.
- Zanichelli - Mappa parallelogrammi e trapezi - https://online.scuola.zanichelli.it/matematicamultimedialeazzurro2ed-files/Mappe/capitoli/bergamini_mappa_93069_cG4.pdf - Mappa PDF di sintesi.

Generatore Python per questo capitolo:

    py genera_esercizi_matematica_primo_liceo.py --chapters G4 --n 10 --out-dir esercizi_matematica

## Avvertenze didattiche

- Prima guardare o leggere il tutorial intuitivo, per costruire un’immagine mentale del concetto.
- Poi studiare il tutorial classico, per fissare definizioni, proprietà e procedimenti.
- Infine svolgere esercizi senza soluzioni, correggere con il file delle soluzioni e usare i risolutori solo per controllare passaggi dubbi.
- Per argomenti algebrici, fare attenzione alle condizioni di esistenza, ai segni e alle proprietà delle potenze.
- Per argomenti geometrici, costruire figure con GeoGebra prima di passare alla dimostrazione scritta.
