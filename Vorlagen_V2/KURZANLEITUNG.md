# BHK-Formatvorlagen – Kurzanleitung

Gilt für die Vorlagen der Version 2 in diesem Verzeichnis (`FREIBURG.dotx`) und für die Briefkopf-Vorlage
des MCP-Dienstes (`templates/BHK_Briefkopf.dotx`). Ein Beispiel aller Formatvorlagen zeigt
`Musterdokument_Formatvorlagen.docx`. Die Gründe für die Umstellung stehen in `BEGRUENDUNG.md`,
Änderungsliste, Risiken und Testplan in `README.md`.

> Lage und Aufbau von Anschriftfeld, Versandvermerk und Infoblock bestimmt in AnNoText der Textbaustein
> „Adresse" (`Textbausteine-WIR/00000001.rtf`, Abrechnung: `00000000.rtf`), nicht die DOTX.

## Welche Vorlage wofür

| Zweck | Formatvorlage (deutsch) | Word-Name | Ergebnis |
|---|---|---|---|
| Fließtext | Textkörper | Body Text | Arial 11, Blocksatz, 1,3-zeilig, 10 pt nach |
| erster Absatz nach Überschrift/Betreff | Erster Absatz | First Paragraph | wie Textkörper |
| Gliederung Ebene 1–5 | Überschrift 1–5 | Heading 1–5 | I. / 1. / a. / aa. / i. |
| Reserve-Ebenen | Überschrift 6–7 | Heading 6–7 | (1) / (a) |
| Randzähler (Schriftsatz) | Randzahl | – | 1. 2. 3. am linken Rand, Text bei 1 cm |
| Unterpunkt eines Randzählers | Randzahl + **Tab** | – | a) b) c) |
| Folgeabsatz ohne Zahl | Listenfortsetzung | List Continue | bündig mit dem Text der Randzahl |
| Beweisangebot | Beweis | – | „Beweis:" + Tab, Folgezeilen mit Umschalt+Eingabe |
| Anträge | Antrag | – | 1. 2. 3., eingerückt |
| Spiegelstriche | Aufzählungszeichen (2) | List Bullet (2) | – / • |
| Aufzählung mit Zähler | Listennummer (2) | List Number (2) | 1.) / a.) |
| Zitat | Zitat | Quote | eingerückt, kursiv |
| eingerückter Block | Blocktext | Block Text | eingerückt |

Briefrahmen (nur im Briefkopf, selten anzufassen): Vermerk, Adresse, Betreff, Anrede, Grußformel,
Unterschrift, Kopfzeile, Fußzeile.

## Regeln für eine stabile Zählung

1. **Nummern nur über Formatvorlagen**, nie über die Schaltfläche *Nummerierung* oder *Aufzählungszeichen*.
2. **Gliederung zählt automatisch neu**: 1. beginnt nach jedem I. neu, a. nach jedem 1. usw.
3. **Randzahl, Antrag und Listennummer** laufen jeweils als eigene Liste. Neu beginnen bei 1:
   Rechtsklick auf die Zahl → *Neu beginnen mit 1*. Durchlaufen lassen: *Fortlaufende Nummerierung*.
4. **Aufzählungen stören die Gliederung nicht** – sie sind eigene Listen.
5. **Keine Leerabsätze** für Abstände; die Abstände stecken in den Vorlagen.
6. Empfehlung in Word: *Datei → Optionen → Erweitert → Einfügen aus anderen Dokumenten:
   Nur den Text übernehmen* bzw. *Formatvorlagen des Zieldokuments verwenden*.

## Was „Standard" noch steuert

Nur den Briefrahmen (Adresse, Infoblock, Kopf-/Fußzeile, Altvorlagen). Fließtext, Gliederung und
Listen hängen **nicht** mehr an „Standard". Schriftart zentral: *Entwurf → Schriftarten* (Arial).

## Altvorlagen

BHK_Standard, BHK_Standard1, BHK_Struktur, BHKVertrag, BHKVertrag_1–5, BHKVF_1–2, Abrechnung,
FordAufstellung, Aufzähler, LF_1 u. a. sind unverändert enthalten (für Altdokumente und Verträge),
aber aus dem Schnellformatvorlagen-Katalog entfernt.

## DIN 5008 (Form B)

* Anschriftfeld ab 45 mm: Zusatz- und Vermerkzone (17,7 mm, Vorlage *Vermerk*, z. B. „per beA"),
  darunter Anschriftzone ab 62,7 mm (27,3 mm, max. 6 Zeilen).
* Falzmarken 105 mm und 210 mm, Lochmarke 148,5 mm – nur auf Seite 1 (dem Blatt, das gefaltet
  und gelocht wird; Folgeseiten ohne Marken wie im bisherigen Briefkopf).
* Grußformel mit 3 Leerzeilen Platz für die Unterschrift.
* Informationsblock bleibt als Hausvariante unter dem Anschriftfeld (rechts steht die Partnerleiste).

## Prompt-Baustein für KI-Tools (OpenWebUI, Libra)

```
Gliederung ausschließlich mit Markdown-Überschriften (#, ##, ###, ####, #####).
Überschriften NICHT selbst nummerieren (kein "I.", "1.", "a." im Überschriftentext) –
die Nummerierung erzeugt die Word-Vorlage automatisch.
Aufzählungen mit "-" oder "1)". Zitate mit ">".
```

## Bekannte Grenzen

* **„aa."** wird über das Nummernmuster `%4%4.` erzeugt. Word stellt das als aa., bb. dar;
  **LibreOffice zeigt „a%4%4."**. Vor dem Rollout bitte in Word prüfen.
* Pandoc-Exporte erzeugen Aufzählungen mit eigener Nummerierung; Schrift und Abstände kommen aus der
  Vorlage *Compact*. Randzähler aus KI-Texten gibt es nur über den MCP-Dienst.

## Vorlage neu erzeugen

```bash
python3 tools/vorlagen/build.py tools/vorlagen/FREIBURG_original.dotx templates/FREIBURG.dotx
python3 tools/vorlagen/build.py tools/vorlagen/BHK_Briefkopf_original.docx templates/BHK_Briefkopf.docx templates/BHK_Briefkopf.dotx
python3 tools/vorlagen/muster.py templates/BHK_Briefkopf.docx templates/BHK_Muster_Formatvorlagen.docx
```
