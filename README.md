# benzina-data

Archivio giornaliero degli open data [MIMIT — Osservatorio Prezzi Carburanti](https://carburanti.mise.gov.it/ospzSearch/home):
prezzi comunicati dai gestori e anagrafica degli impianti attivi in Italia.

Alimenta l'app **benzina.io** (in sviluppo): serve a costruire lo storico per i
confronti settimanali ("oggi è il minimo degli ultimi 7 giorni") che i file
ufficiali da soli non permettono, dato che gli archivi trimestrali escono a
trimestre chiuso.

## Come funziona

Una GitHub Action ([collect.yml](.github/workflows/collect.yml)) gira due volte
al giorno, scarica i due CSV ufficiali e li archivia gzippati, nominandoli per
**data di estrazione** dichiarata nel file (non per data di download). Lo script
è idempotente: la stessa estrazione non viene mai archiviata due volte.

```
data/
  2026/
    07/
      prezzo_alle_8-20260729.csv.gz
      anagrafica_impianti_attivi-20260729.csv.gz
  last_update.json
```

Formato dei file (pipe-delimited, 2 righe di intestazione):

- `prezzo_alle_8`: `idImpianto|descCarburante|prezzo|isSelf|dtComu` (~93k righe/giorno)
- `anagrafica_impianti_attivi`: `idImpianto|Gestore|Bandiera|Tipo Impianto|Nome Impianto|Indirizzo|Comune|Provincia|Latitudine|Longitudine` (~24k impianti)

## Consumo

Ogni file è raggiungibile direttamente via raw URL:

```
https://raw.githubusercontent.com/LucaDDDD/benzina-data/main/data/2026/07/prezzo_alle_8-20260729.csv.gz
```

`data/last_update.json` riporta l'ultima estrazione archiviata.

## Licenza dati

I dati appartengono al MIMIT e sono pubblicati come open data (attribuzione:
"Ministero delle Imprese e del Made in Italy — Osservatorio Prezzi Carburanti").
Questo repo si limita ad archiviarne le pubblicazioni giornaliere.
