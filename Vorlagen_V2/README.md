# Vorlagen V2 – Briefvorlage FREIBURG und Textbausteine „Adresse"

**Status: Entwurf – nicht einspielen ohne Freigabe durch die Organisation.**
Die Originale unter `tools/vorlagen/` (FREIBURG_original.dotx, `Textbausteine-WIR/`,
`Adressvorlagen/`, `Aktenvermerk Textbaustein/`) bleiben unverändert und sind der Rückfallstand.

## Inhalt

| Datei | Gegenüber Original |
|---|---|
| `BEGRUENDUNG.md` | warum die Vorlagen grundlegend geändert werden müssen (Entscheidungsgrundlage) |
| `KURZANLEITUNG.md` | welche Formatvorlage wofür, Regeln für stabile Zählung, Prompt-Baustein für KI-Tools |
| `Musterdokument_Formatvorlagen.docx` | alle Formatvorlagen und Prüffälle, erzeugt aus `FREIBURG.dotx` V2 |
| `FREIBURG.dotx` | neue Formatvorlagen und Listen (wie `templates/FREIBURG.dotx`) **plus** Anschriftfeld-Anpassung: oberer Rand 45 mm statt 47 mm, vier leere Kopfzeilenabsätze auf Seite 1 entfernt |
| `Textbausteine-WIR/00000000.rtf` (Adresse Abrechnung) | Anschriftfeld nach DIN 5008, Datum in den Informationsblock |
| `Textbausteine-WIR/00000001.rtf` (Adresse allgemein) | wie 00000000 |
| `Textbausteine-WIR/00000002.rtf`, `00000003.rtf`, `bsimpexp.ini` | unverändert (nur, damit der Ordner vollständig importierbar ist) |

`Adressvorlagen/` (ADR-Layouts) und `Aktenvermerk Textbaustein/` sind **nicht** geändert.

## Änderungen im Einzelnen

**FREIBURG.dotx**
1. Formatvorlagen: Textkörper, Überschrift 1–7 (I. / 1. / a. / aa. / i. / (1) / (a)), Randzahl,
   Listenfortsetzung, Beweis, Antrag, Aufzählungszeichen, Listennummer; Arial als Design-Schriftart.
   Altvorlagen (BHK_Standard1 usw.) bleiben erhalten. Details: `KURZANLEITUNG.md`.
2. Zweite Falzmarke (210 mm) und Lochmarke (148,5 mm) auf Seite 1.
3. Textbeginn Seite 1 exakt bei 45 mm (Beginn Anschriftfeld DIN 5008 Form B). Bisher begann der Text
   wegen leerer Kopfzeilenabsätze erst bei ca. 55 mm.

**Textbausteine „Adresse" (00000000, 00000001)**
1. Zeile Versandart (`[M_VERSANDART]`, z. B. „per beA") = Zusatz- und Vermerkzone: Höhe exakt 17,7 mm,
   Text unten ausgerichtet.
2. Zeile `[ADDRESS_LAYOUT]` = Anschriftzone: Höhe exakt 27,3 mm (max. 6 Zeilen) statt „mindestens 45,7 mm".
3. „Freiburg, den [M_TAGDATUM]" entfällt; neue erste Zeile im Informationsblock „Datum: [M_TAGDATUM]"
   (DIN 5008; zugleich ortsneutral für alle Standorte).

Gemessen in einer Simulation (LibreOffice, Brief an das LG Freiburg):

| | Original | Entwurf v2 | DIN 5008 Form B |
|---|---|---|---|
| Versandvermerk | 55,4–59,8 mm | 58,4–62,7 mm | Vermerkzone 45–62,7 mm |
| Anschrift erste / letzte Zeile | 63,0 / 85,2 mm | 62,8 / 85,0 mm | Anschriftzone 62,7–90 mm |
| Datum | 116 mm, „Freiburg, den" | 101 mm, im Infoblock | im Infoblock |
| Betreff | 146 mm | 131 mm | nach dem Infoblock |

## Voraussetzungen und Risiken – bitte vor Freigabe prüfen

* **Beide Teile gehören zusammen.** Die exakten Zeilenhöhen setzen voraus, dass der Baustein bei 45 mm
  beginnt (FREIBURG.dotx v2). Mit der alten FREIBURG.DOTX säße das Anschriftfeld ca. 10 mm zu tief.
* **AnNoText-Administration „oben 5 cm":** Falls AnNoText diesen Wert als Seitenrand setzt, verschiebt
  sich alles um 5 mm nach unten. Dann in der Administration auf 4,5 cm stellen oder prüfen, ob der Wert
  nur die Formatierung ab Zeile 4 betrifft.
* **Anschriften mit mehr als 6 Zeilen** werden in der Anschriftzone abgeschnitten (DIN 5008 erlaubt 6).
  ADR-Layout „Gericht" (ADR00000002) enthält zwei Leerzeilen – sofern AnNoText sie nicht entfernt,
  bleiben für das Gericht 5 Textzeilen.
* **Andere Standorte** (Lörrach, Karlsruhe, Pforzheim, Bonn) und die Rechnungs- bzw. Mail-/beA-Varianten
  sind nicht enthalten; sie müssten nach Freigabe genauso umgestellt werden.
* Geprüft nur mit LibreOffice. Abschlusstest in Word über AnNoText erforderlich.

## Test nach Freigabe (Testarbeitsplatz)

1. Textbausteine aus `Vorlagen_V2/Textbausteine-WIR` in einer Testumgebung importieren, FREIBURG.dotx v2
   mit der Vorlage FREIBURG verknüpfen.
2. Je einen Brief per Post, per beA und an ein Gericht erzeugen; Anschrift im Fensterumschlag (DL/C5/6)
   prüfen, Datum und Infoblock prüfen.
3. Gliederung und Randzahl mit `Musterdokument_Formatvorlagen.docx` gegenprüfen
   (insbesondere Ebene „aa.").

## Rückfall

Originale aus `tools/vorlagen/` wieder einspielen (FREIBURG_original.dotx, `Textbausteine-WIR/`).

## Neu erzeugen

```bash
python3 tools/vorlagen/build.py --din-anschriftfeld tools/vorlagen/FREIBURG_original.dotx Vorlagen_V2/FREIBURG.dotx
python3 tools/vorlagen/textbaustein_v2.py tools/vorlagen/Textbausteine-WIR/00000001.rtf Vorlagen_V2/Textbausteine-WIR/00000001.rtf
python3 tools/vorlagen/textbaustein_v2.py tools/vorlagen/Textbausteine-WIR/00000000.rtf Vorlagen_V2/Textbausteine-WIR/00000000.rtf
python3 tools/vorlagen/build.py --din-anschriftfeld tools/vorlagen/FREIBURG_original.dotx /tmp/v2basis.docx
python3 tools/vorlagen/muster.py /tmp/v2basis.docx Vorlagen_V2/Musterdokument_Formatvorlagen.docx
```
