# PDF Blank Page Remover

Ein Python-Skript, das automatisch leere Seiten aus PDF-Dokumenten entfernt, mehrere Dateien parallel verarbeitet und dabei Fortschrittsbalken für jede Datei anzeigt.

## Funktionen

- Entfernt automatisch leere Seiten aus PDF-Dokumenten.
- Verarbeitet mehrere Dateien parallel, um die Effizienz zu erhöhen.
- Zeigt Fortschrittsbalken für jede Datei an.
- Erstellt einen Bericht, wie viele leere Seiten aus jeder Datei entfernt wurden.

## Voraussetzungen

Stellen Sie sicher, dass Sie die folgenden Abhängigkeiten installiert haben:

- Python 3.6 oder höher
- `tqdm` Bibliothek
- `pdf2image` Bibliothek
- `poppler-utils`

### Installation der Abhängigkeiten

```sh
sudo python3.12 -m pip install tqdm pdf2image
brew install poppler
```
