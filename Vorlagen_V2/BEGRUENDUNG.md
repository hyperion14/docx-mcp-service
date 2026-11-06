# Warum wir unsere Briefvorlagen grundlegend ändern müssen

*Entscheidungsgrundlage für die Freigabe der Vorlagen V2 (FREIBURG.dotx und Textbausteine „Adresse")*
*Stand: 06.11.2026*

---

## 1. Kurzfassung

Unsere Briefvorlage sieht auf dem Papier gut aus. Die Technik dahinter trägt aber den Arbeitsalltag
nicht mehr. Gliederungen zählen falsch oder beginnen unkontrolliert neu, Fließtext steht in
Listenvorlagen, Abstände werden mit Leerzeilen gebaut, und Texte aus KI-Werkzeugen kommen ohne unsere
Formatierung in Word an. Die Ursache liegt nicht bei den Anwendern, sondern im Aufbau der Vorlage:

* Fast alle Formatvorlagen hängen an **einer** Vorlage („Standard"). Wer sie anpasst, verändert
  Briefkopf, Gliederung, Listen und Fußnoten gleichzeitig.
* Es gibt **zwei konkurrierende Gliederungssysteme**, und keines bildet unser Kanzleischema
  **I. / 1. / a. / aa. / i.** ab.
* Für **Randzähler, Folgeabsätze, Beweisangebote und Anträge** gibt es keine Vorlage. Sie werden von
  Hand nachgebaut, und genau diese Handarbeit bricht beim Kopieren, Überarbeiten und Exportieren.
* Das **Anschriftfeld** weicht von DIN 5008 ab, und das Datum steht in einer veralteten Form.

Die Vorlagen V2 beheben das, ohne den Briefkopf optisch zu verändern und ohne bestehende Dokumente
unbrauchbar zu machen. Alle Altvorlagen bleiben erhalten.

---

## 2. Ausgangslage: Wie die Vorlage heute aufgebaut ist

Ausgewertet wurden die Systemvorlage `FREIBURG.DOTX`, der Briefkopf als Word-Dokument, die
AnNoText-Textbausteine und zwei echte Arbeitsdokumente: eine Stellungnahme (26 Seiten) und eine
Klageerwiderung an das Landgericht (10 Seiten).

### 2.1 Alles hängt an „Standard"

In Word erbt jede Formatvorlage die Eigenschaften der Vorlage, auf der sie aufbaut. In unserer Vorlage
bauen Überschrift 1 und 2, Listenabsatz, Zitat, Fußnotentext, Kopf- und Fußzeile und BHK_Standard
direkt auf „Standard" auf. Überschrift 3 baut auf Überschrift 1 auf, Überschrift 4 auf Überschrift 3.

**Folge:** Eine Änderung an „Standard", etwa ein anderer Zeilenabstand für den Fließtext, wirkt
gleichzeitig auf Anschrift, Infoblock, Überschriften, Fußnoten und Listen. Deshalb traut sich niemand,
die Vorlage anzupassen, und stattdessen wird jeder Absatz einzeln von Hand formatiert.

### 2.2 Zwei Gliederungen, keine passt

| Gliederungssystem | Zählweise | gekoppelt an |
|---|---|---|
| Überschriften | I. / A. / 1. / a) | Überschrift 1–4 (Überschrift 5 ohne Zählung) |
| BHKVertrag | I. / 1. / a) / (1) / (a) / (i) | BHKVertrag, BHKVertrag_1 bis _5 |
| **Kanzleischema** | **I. / 1. / a. / aa. / i.** | – |

Keines der beiden Systeme entspricht unserem Schema. In der Praxis werden sie deshalb gemischt.

### 2.3 Was das im Alltag bedeutet – zwei echte Dokumente

| Kennzahl | Stellungnahme | Erwiderung an das LG |
|---|---:|---:|
| Absätze gesamt | 484 | 145 |
| verschiedene Absatzvorlagen | 11 | 6 |
| Leerabsätze nur für Abstände | 88 | 48 |
| Absätze mit von Hand gesetztem Einzug | 200 | 57 |
| Absätze mit von Hand gesetzter Nummerierung | 39 | 58 |

**In der Stellungnahme** stammt „I." aus einem leeren, zentrierten Absatz in Überschrift 1. Die
Überschrift darunter, etwa „1. Fragestellung", stammt aus BHKVertrag_1, also aus dem anderen
Gliederungssystem. Damit „1." nach jedem „I." wieder bei 1 beginnt, wurden von Hand neue Listen
angelegt. 90 Absätze stehen ohne Nummer in der Vorlage „Listennummer", 61 in „Listenabsatz" –
überwiegend Fließtext. Zitate
erben von „Listennummer". Spiegelstriche sind auf drei verschiedene Arten gebaut.

**In der Erwiderung an das LG** funktionieren die Randzähler, weil „I." und „1." aus derselben Liste
kommen. Die Absätze ohne Zahl zwischen den Randzählern entstehen aber durch Abschalten der Nummer plus
Einzug von Hand (58 Absätze). Beweisangebote sind mit Tabulatoren ausgerichtet, Anträge von Hand
nummeriert („1.die Klage …", ohne Abstand), Zwischenüberschriften sind fett formatierter Standardtext.

### 2.4 Warum Handarbeit hier zum Risiko wird

Von Hand gesetzte Nummern, Einzüge und Leerzeilen sind unsichtbare Sonderformatierungen. Sie gehen
verloren oder verrutschen, sobald

* ein Absatz in ein anderes Dokument kopiert wird (er bringt seine eigene Liste mit und beginnt neu),
* jemand „Formatierung löschen" verwendet,
* ein Abschnitt verschoben wird (der Neustart wandert mit oder fehlt),
* ein Text aus einem KI-Werkzeug übernommen wird (dort gibt es keine Sonderformatierung).

Im Schriftsatz an das Gericht ist eine falsch fortlaufende oder doppelt vergebene Gliederungsnummer
kein Schönheitsfehler. Auf Randzähler und Gliederungspunkte wird verwiesen („siehe oben unter II. 3."),
und ein Fehler fällt oft erst nach dem Versand auf.

### 2.5 Technischer Ballast

* Die Briefkopf-Datei enthält 17 Listendefinitionen mit 44 Listeninstanzen, davon 9 allein für die
  Überschriften-Gliederung. Die Systemvorlage FREIBURG.DOTX enthält 23 Listeninstanzen, davon 22 ungenutzt.
  Mehrere Instanzen derselben Liste sind die häufigste technische Ursache für „zerrissene" Zählungen.
* Die Grundeinstellung des Dokuments ist Calibri 11 pt mit 8 pt Abstand. Alles, wofür keine
  Formatvorlage greift, erscheint in Calibri statt Arial.
* In der Briefkopf-Datei ist die Word-Vorlage „Textkörper" Times New Roman 12 pt mit Sprache
  **Englisch**; in der Systemvorlage fehlt sie ganz.

---

## 3. Neue Anforderung: KI-Werkzeuge

Wir nutzen OpenWebUI und Libra und damit Werkzeuge, die Texte als Word-Datei ausgeben. Diese Werkzeuge
kennen nur die **Word-eigenen Formatvorlagen** (Überschrift 1–9, Textkörper, Aufzählungszeichen,
Listennummer, Zitat, Fußnotentext). Unsere eigenen Namen wie „BHK_Standard1" oder „BHKVertrag_1" kennen
sie nicht.

**Heute heißt das:** Ein KI-Text landet in „Standard" oder „Textkörper", ohne Gliederungszählung, und
muss vollständig neu formatiert werden. In der Briefkopf-Datei sogar in Times New Roman mit englischer
Rechtschreibprüfung.

**Mit V2:** Das BHK-Layout liegt genau auf diesen Word-Namen. Eine Markdown-Überschrift `##` wird
automatisch zu Überschrift 2 und damit zu „1." in unserer Gliederung, normaler Text zu Textkörper,
`-` zu einem Spiegelstrich. Die Vorlage wird damit zum gemeinsamen Nenner für Word, AnNoText und KI.

---

## 4. DIN 5008: Wo der Brief heute abweicht

| Element | DIN 5008, Form B | heute | V2 |
|---|---|---|---|
| Versandvermerk („per beA") | Zusatz- und Vermerkzone 45–62,7 mm | 55,4–59,8 mm, ohne feste Zone | 58,4–62,7 mm, feste Zone, unten ausgerichtet |
| Anschrift | Anschriftzone 62,7–90 mm, max. 6 Zeilen | ab 63 mm, Zeile „mindestens 45,7 mm" hoch | 62,8–85 mm, Zone exakt 27,3 mm |
| Datum | im Informationsblock, ohne Ort und „den" | „Freiburg, den …" über dem Infoblock | „Datum: …" im Infoblock |
| Falz- und Lochmarken | 105 mm, 210 mm, Lochmarke 148,5 mm | nur 105 mm | alle drei |
| Ränder | links ≥ 25 mm | 25 mm | unverändert |

Messwerte aus einer Simulation mit LibreOffice (Brief an das LG Freiburg). Der Informationsblock bleibt
als Hausvariante unter dem Anschriftfeld, weil rechts die Partnerleiste steht.

Das ortsneutrale „Datum:" hat einen Nebeneffekt: Der Textbaustein passt ohne Änderung für alle
Standorte. Heute steht im gemeinsamen Baustein fest „Freiburg, den".

---

## 5. Was V2 ändert – die Grundprinzipien

### 5.1 Drei getrennte Grundlagen statt einer Kette

| Gruppe | Formatvorlagen | wofür |
|---|---|---|
| Briefrahmen | Standard, Adresse, Vermerk, Betreff, Anrede, Grußformel, Unterschrift, Kopf-/Fußzeile | ändert man selten |
| Fließtext | Textkörper, Erster Absatz, Listenfortsetzung, Beweis, Aufzählungszeichen, Listennummer, Antrag, Zitat, Blocktext | Zeilenabstand, Blocksatz, Absatzabstand |
| Gliederung | Überschrift 1–7, Randzahl | Zählung und Hierarchie |

Eine Änderung am Fließtext berührt weder Anschrift noch Gliederung. Die Schrift (Arial) wird zentral
als Design-Schriftart gesetzt.

### 5.2 Eine Gliederung nach Kanzleischema

Überschrift 1–5 zählen **I. / 1. / a. / aa. / i.** in einer einzigen Liste, Überschrift 6–7 als Reserve
(1) / (a). Untergeordnete Ebenen beginnen automatisch neu. Ein „Neu beginnen" von Hand ist nie nötig.

### 5.3 Randzähler, Folgeabsatz, Beweis, Antrag

| Bedarf im Schriftsatz | heute | V2 |
|---|---|---|
| Randzähler 1., 2., 3. | BHKVertrag_1 | Vorlage **Randzahl**; Tab ergibt a), b) |
| Absatz ohne Zahl im Randzähler | Nummer abschalten + Einzug von Hand | Vorlage **Listenfortsetzung** |
| Beweisangebot | Tabulatoren + Einzug von Hand | Vorlage **Beweis** |
| Anträge | Zahlen von Hand getippt | Vorlage **Antrag** |
| Spiegelstriche, „1.)" | drei verschiedene Bauweisen | **Aufzählungszeichen**, **Listennummer** |

Randzahl, Antrag und Aufzählungen sind eigene Listen. Sie können mitten in der Gliederung stehen, ohne
deren Zählung zu verändern. Randzähler laufen durch und lassen sich mit Rechtsklick
„Neu beginnen mit 1" neu starten.

### 5.4 Ein Vorlagenset für alles

Brief, Stellungnahme und Schriftsatz nutzen dieselben Formatvorlagen. Es gibt keine getrennte
„Schriftsatz-Familie", die wieder auseinanderläuft.

### 5.5 Abstände aus der Vorlage

Abstände vor und nach Überschriften, Absätzen, Gruß und Unterschrift sind in den Vorlagen hinterlegt.
Leerabsätze werden nicht mehr gebraucht. Für die Unterschrift sind drei Leerzeilen vorgesehen
(heute eine).

---

## 6. Was sich für die Anwender ändert

* **Weniger Handarbeit:** Formatvorlage wählen statt Nummer, Einzug und Leerzeile von Hand setzen.
* **Neue Namen im Formatvorlagen-Katalog:** Textkörper, Randzahl, Listenfortsetzung, Beweis, Antrag.
  Eine einseitige Kurzanleitung liegt bei (`KURZANLEITUNG.md`).
* **Die Optik des Briefkopfs bleibt:** Logo, Partnerleiste, Fußzeile, Schrift und Ränder sind unverändert.
* **Gewohnte Tastenkürzel bleiben:** Strg+Umschalt+2 setzt weiterhin BHK_Standard1.
* **Altdokumente bleiben unverändert.** Ein bestehendes Dokument ändert sich nicht, nur weil die Vorlage
  neu ist. Alle Altvorlagen sind weiter vorhanden, nur nicht mehr in der Schnellauswahl.

---

## 7. Was bewusst nicht geändert wird

* Optik von Briefkopf, Logo, Partnerleiste und Fußzeilen
* AnNoText-Platzhalter und -Felder (`[M_…]`, `[ADDRESS_LAYOUT]`)
* ADR-Adresslayouts, Textbausteine Anrede, Betreff und Aktenvermerk
* Lage des Informationsblocks (Hausvariante unter dem Anschriftfeld)
* Altvorlagen (BHKVertrag, BHK_Standard1, Abrechnung, FordAufstellung u. a.)

---

## 8. Erwogene Alternativen

| Alternative | Warum nicht |
|---|---|
| Nur die Zählformate der vorhandenen Überschriften ändern | Die Kette ab „Standard", die zwei Gliederungssysteme und die fehlenden Vorlagen für Randzähler, Folgeabsatz und Beweis blieben bestehen. Die Handarbeit bliebe. |
| Eigene Schriftsatz-Vorlage mit eigenem Formatvorlagenset | Zwei Sets laufen auseinander, Texte zwischen Brief und Schriftsatz lassen sich nicht sauber austauschen. Genau dieses Nebeneinander verursacht heute die Fehler. |
| Makros für Nummerierung und Formatierung | Makros sind sicherheitstechnisch problematisch, wirken nicht bei KI-Exporten und brechen bei Office-Updates. Die Lösung mit reinen Word-Bordmitteln ist robuster. |
| Nichts ändern | Die Fehlerquellen bleiben, und jede KI-Ausgabe muss weiter vollständig nachformatiert werden. |

---

## 9. Risiken und Grenzen

* **Ebene „aa.":** Word kennt kein fertiges Format „aa, bb". V2 nutzt das Nummernmuster `%4%4.`, das
  Word als aa., bb. darstellt. LibreOffice zeigt stattdessen „a%4%4.". **Vor dem Rollout in Word prüfen.**
* **Anschriftzone mit fester Höhe:** Anschriften mit mehr als sechs Zeilen werden abgeschnitten.
  Das entspricht DIN 5008, kann aber bei langen Gerichtsanschriften auffallen.
* **AnNoText-Einstellung „oben 5 cm":** Falls AnNoText diesen Wert als Seitenrand setzt, verschiebt sich
  das Anschriftfeld um 5 mm nach unten. Das ist in der Administration zu prüfen.
* **DOTX und Textbausteine gehören zusammen.** Wer nur eines davon einspielt, verschiebt das
  Anschriftfeld um etwa 10 mm.
* **Umfang:** V2 umfasst den Standort Freiburg (Postweg). Die übrigen Standorte sowie die Rechnungs- und
  Mail-/beA-Varianten werden nach Freigabe nach demselben Verfahren umgestellt.
* **Prüfung bisher nur mit LibreOffice.** Ein Test in Word über AnNoText steht aus.

---

## 10. Vorschlag zum Vorgehen

1. **Freigabe** dieses Konzepts durch die Organisation.
2. **Test** auf einem Testarbeitsplatz: Textbausteine importieren, FREIBURG.dotx V2 verknüpfen, je einen
   Brief per Post, per beA und an ein Gericht erzeugen, Fensterumschlag prüfen, Gliederung mit dem
   Musterdokument prüfen (Testplan in `README.md`).
3. **Pilot** mit wenigen Anwenderinnen und Anwendern über zwei bis drei Wochen.
4. **Rollout** für Freiburg, danach Übertragung auf die übrigen Standorte und Varianten.
5. **Rückfall** jederzeit möglich: Die Originale liegen unverändert unter `tools/vorlagen/`.

---

## 11. Entscheidungsbedarf

* Freigabe der Vorlagen V2 für einen Test
* Zustimmung zur Datumsform „Datum: TT.MM.JJJJ" im Informationsblock statt „Freiburg, den …"
* Benennung einer Ansprechperson für den Test in AnNoText
