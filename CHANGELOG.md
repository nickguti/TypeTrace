# Changelog

Tutte le modifiche rilevanti a TypeTrace. Il formato segue
[Keep a Changelog](https://keepachangelog.com/it/1.1.0/) e le versioni usano
il [versionamento semantico](https://semver.org/lang/it/).

## [3.2.0] - 2026-08-19

Una revisione completa: 31 difetti corretti, quattro funzioni che non erano mai
entrate in funzione, e la prima copertura di test sull'interfaccia.

### Corretto

- **Cambio automatico di profilo**: non era mai scattato. Il processo veniva
  aperto con `PROCESS_QUERY_LIMITED_INFORMATION` e poi interrogato con
  `GetModuleBaseNameW`, che richiede diritti maggiori: la chiamata falliva
  sempre in silenzio. Con essa non funzionavano nemmeno le mappature
  processo-profilo, l'elenco delle app recenti e il banner "gaming mode".
- **Scheda Telemetria**: leggeva il profilo `Total` letterale invece
  dell'aggregato interno, quindi grafico, record e contatore erano sempre
  vuoti; e si interrompeva a meta' disegno ordinando i bigrammi annidati.
- **Modalita' incognito**: irraggiungibile. La voce del menu nell'area di
  notifica inviava un evento che nessuno gestiva, e la scorciatoia
  `Ctrl+Shift+I` non scattava mai.
- **Nomi dei tasti**: 28 tasti su 104 non potevano illuminarsi, perche' il
  tracciatore e la tastiera disegnata usavano due convenzioni diverse.
- **Tasti premuti con Ctrl**: venivano archiviati come caratteri di controllo
  (`\x13` invece di `S`).
- **Modificatori bloccati** dopo `Alt+Tab`: ogni tasto successivo finiva
  registrato come scorciatoia `Alt+…`.
- **AltGr** generava combinazioni `Ctrl+Alt` mai premute.
- **Modificatore da solo**: premere Ctrl registrava la combinazione
  `Ctrl+Ctrl_L`.
- **Azzeramento statistiche**, **creazione profilo** e **cambio profilo**
  sollevavano eccezioni per nomi di metodo inesistenti.
- **Dati nell'eseguibile**: finivano nella cartella temporanea di PyInstaller e
  sparivano a ogni chiusura. Ora stanno in `%APPDATA%\TypeTrace`.
- **Traduzioni assenti nel binario**: la build non includeva `lang.json`, e
  l'interfaccia mostrava le chiavi al posto dei testi.
- **Salvataggio non atomico**: un'interruzione a meta' scrittura troncava il
  database. Ora si scrive su file temporaneo e si sostituisce, con copia `.bak`.
- **Esportazione**: segnalava successo anche quando la scrittura falliva, e
  ignorava due delle proprie caselle di scelta.
- **Overlay**: poteva aprirsi vuoto e fuori dallo schermo, senza modo di
  recuperarlo.
- **Avvio con Windows**: registrava un comando che Windows non sapeva eseguire.
- Perdita di memoria nelle animazioni a finestra ridotta, istantanea del tema
  che restava sospesa sull'interfaccia, modalita' compatta non ripristinata,
  log senza rotazione, doppia istanza non impedita, chiusura ricorsiva.

### Aggiunto

- **Precisione di battitura**: rapporto fra correzioni e battute totali.
- **Attivita' giornaliera**: grafico degli ultimi 30 giorni.
- **Serie in corso e migliore**, e **record giornaliero**.
- **Gestione profili** dall'interfaccia: creazione ed eliminazione.
- **Interruttore per il cambio automatico** di profilo.
- `CHANGELOG.md`, `LICENSE` (MIT, che il README dichiarava senza includerlo) e
  38 test, di cui 23 sull'interfaccia, eseguiti in CI prima della build.

### Modificato

- **Aggregazione incrementale**: i totali non vengono piu' ricalcolati a ogni
  tasto premuto. Il costo e' costante invece di crescere con lo storico.
- **Ridisegni**: la tastiera non viene piu' ridisegnata 33 volte al secondo a
  schermo fermo, e i timer si fermano quando la finestra e' nell'area di
  notifica.
- **Compattazione dello storico**: i dati orari oltre i 180 giorni diventano
  giornalieri, a parita' di totali.
- `requirements.txt` ridotto alle cinque dipendenze reali: prima era l'elenco
  completo di una macchina di sviluppo e conteneva un riferimento a un percorso
  locale, che impediva alla build di installare qualunque cosa.

### Migrazione

Al primo avvio i dati esistenti vengono copiati in `%APPDATA%\TypeTrace`, i
nomi dei tasti corretti e lo storico oltre i 180 giorni compattato. Gli
originali non vengono toccati e viene conservata una copia `.bak`.
La variabile `TYPETRACE_DATA_DIR` permette di scegliere un'altra cartella.
