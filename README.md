# Grouppy
Applicazione web sviluppata in linguaggio Python (versione 2.7) con framework Flask su platform Google App Engine.

## Premessa
L'applicazione nasce come progetto estivo per estendere le mie capacità con queste tecnologie ed apprendere concetti nuovi. Il risultato non è dei migliori, lo ammetto, ma il percorso che ho seguito è stato non banale.

## Presentazione
Il mio progetto nasce a fronte di un'esigenza della mia compagnia di amici, che, essendo molto numerosa, fa sempre fatica a decidere chi debba prendere la macchina quando si esce. Il risultato è che sono sempre poche persone a prenderla sempre. Con grouppy potremo avere un'evidenza di ciò e stabilire in modo democratico chi debba guidare.
Inoltre molte compagnie di amici, come la mia, hanno una 'Cassa Comune', ovvero un portafoglio con gli avanzi/resti di cene, feste, grigliate.

## Funzionalità

### Utente
Per 'utente' si intende chi gestice la compagnia di amici. A questo sarà richiesto di iscriversi a Grouppy e il gioco è fatto.

### Amici
L'utente può aggiungere tutti gli amici che vuole, modificarne i dati, eliminarli.

### Uscite
L'utente può aggiungere le uscite, indicando la distanza in KM, chi ha guidato e chi è stato trasportato. Guidando si guadagnano punti, altrimenti se ne perdono.

### Cassa Comune
L'utente può annotare spese e incassi della compagnia.

## Istruzioni per il testing e il deploy
Il file 'app.yaml' stabilisce le specifiche per il deploy su Google App Engine.
Per il testing si utilizzi il comando:
```bash
dev_appserver.py app.yaml
```
Per il deploy si crei il progetto su GCloud e si utilizzi il comando:
```bash
gcloud app deploy [index.yaml]
```
Indicare anche 'index.yaml' la prima volta