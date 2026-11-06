"""Musterdokument mit allen Formatvorlagen und Prüffällen erzeugen.

Aufruf: python3 muster.py <BHK_Briefkopf.docx> <ziel.docx>
"""
import copy
import sys

from docx import Document
from docx.oxml.ns import qn
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def restart(doc, para, num_style_id):
    """Wie Word „Neu beginnen mit 1": neue Listeninstanz mit startOverride am ersten Absatz."""
    numbering = doc.part.numbering_part.element
    style = doc.styles[num_style_id] if False else None  # noqa: F841 (Lesbarkeit)
    st_el = [s for s in doc.styles.element.findall(qn("w:style")) if s.get(qn("w:styleId")) == num_style_id][0]
    num_id = st_el.find(qn("w:pPr")).find(qn("w:numPr")).find(qn("w:numId")).get(qn("w:val"))
    abs_id = [n for n in numbering.findall(qn("w:num")) if n.get(qn("w:numId")) == num_id][0] \
        .find(qn("w:abstractNumId")).get(qn("w:val"))
    new_id = max(int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))) + 1
    num = etree.SubElement(numbering, qn("w:num"))
    num.set(qn("w:numId"), str(new_id))
    a = etree.SubElement(num, qn("w:abstractNumId"))
    a.set(qn("w:val"), abs_id)
    ov = etree.SubElement(num, qn("w:lvlOverride"))
    ov.set(qn("w:ilvl"), "0")
    so = etree.SubElement(ov, qn("w:startOverride"))
    so.set(qn("w:val"), "1")
    ppr = para._p.get_or_add_pPr()
    numpr = etree.SubElement(ppr, qn("w:numPr"))
    il = etree.SubElement(numpr, qn("w:ilvl"))
    il.set(qn("w:val"), "0")
    ni = etree.SubElement(numpr, qn("w:numId"))
    ni.set(qn("w:val"), str(new_id))
    # numPr muss direkt nach pStyle stehen
    ps = ppr.find(qn("w:pStyle"))
    ppr.remove(numpr)
    ps.addnext(numpr)


def tab_level(para, ilvl):
    """Wie Tab in einer Liste: Ebene tiefer, gleiche Liste."""
    ppr = para._p.get_or_add_pPr()
    numpr = etree.SubElement(ppr, qn("w:numPr"))
    il = etree.SubElement(numpr, qn("w:ilvl"))
    il.set(qn("w:val"), str(ilvl))
    ps = ppr.find(qn("w:pStyle"))
    ppr.remove(numpr)
    ps.addnext(numpr)


CONTENT = [
    ("Betreff", "Musterdokument der Formatvorlagen"),
    ("ErsterAbsatz", "Dieses Dokument zeigt alle neuen Formatvorlagen im Zusammenspiel. Die grauen Hinweise in "
                     "eckigen Klammern nennen die jeweils verwendete Vorlage."),
    ("berschrift1", "Gliederung für Stellungnahmen [Überschrift 1]"),
    ("berschrift2", "Akten- und Entscheidungsgrundlage [Überschrift 2]"),
    ("ErsterAbsatz", "Folgende Einzelmaßnahmen sind in der Gesamtmaßnahme vorgesehen [Erster Absatz]:"),
    ("Listennummer", "Neubau Schulgebäude [Listennummer]"),
    ("Listennummer", "Umbauarbeiten im Mensagebäude"),
    ("Listennummer2", "Ganztagsbetreuung [Listennummer 2]"),
    ("Listennummer2", "Küche und Ausgabe"),
    ("Listennummer", "Neubau 2-Feld-Sporthalle"),
    ("Textkrper", "Die Zählung der Gliederung läuft nach diesem Block unverändert weiter [Textkörper]."),
    ("berschrift2", "Gesetzlicher Rahmen [Überschrift 2 – zählt weiter mit 2.]"),
    ("berschrift3", "Technische Gründe [Überschrift 3]"),
    ("ErsterAbsatz", "Die technischen Gründe wirken unmittelbar auf"),
    ("Aufzhlungszeichen", "Lage, Kubatur und Erschließung der Gebäude, [Aufzählungszeichen]"),
    ("Aufzhlungszeichen", "Tragwerksraster und Gründung,"),
    ("Aufzhlungszeichen2", "Bodenplatte und Pfahlgründung, [Aufzählungszeichen 2]"),
    ("Aufzhlungszeichen", "Brand- und Rettungswege"),
    ("Textkrper", "ein."),
    ("berschrift4", "Innerstädtische Lage [Überschrift 4]"),
    ("berschrift5", "Verkehrliche Erschließung [Überschrift 5]"),
    ("ErsterAbsatz", "Text unter der fünften Ebene."),
    ("berschrift5", "Wärmeversorgung [Überschrift 5 – zählt weiter mit ii.]"),
    ("berschrift4", "Schulbetrieb [Überschrift 4 – zählt weiter mit bb.]"),
    ("berschrift3", "Wirtschaftliche Gründe [Überschrift 3 – zählt weiter mit b.]"),
    ("Zitat", "„Erforderlich ist vielmehr, dass sich der Auftraggeber im Einzelnen mit dem grundsätzlichen "
              "Gebot der Fachlosvergabe auseinandersetzt.“ (OLG München, Beschluss vom 25.03.2019 – Verg 10/18) [Zitat]"),
    ("berschrift1", "Gliederung mit Randzählern für Schriftsätze [Überschrift 1 – II.]"),
    ("ErsterAbsatz", "Wir werden in der mündlichen Verhandlung beantragen, [Erster Absatz]"),
    ("Antrag", "die Klage einschließlich des Hilfsantrags abzuweisen; [Antrag]"),
    ("Antrag", "auf die Widerklage die Klägerin zu verurteilen, an die Beklagten 12.345,00 € nebst Zinsen "
               "hieraus in Höhe von 9 Prozentpunkten über dem Basiszinssatz zu zahlen;"),
    ("Antrag", "die Kosten des Rechtsstreits der Klägerin aufzuerlegen."),
    ("Randzahl", "Die Klägerin vertritt weiterhin die unzutreffende Ansicht, es lägen drei getrennte Verträge "
                 "vor. Dem wurde von unserer Seite hinreichend widersprochen. [Randzahl]"),
    ("Listenfortsetzung", "Im Übrigen ist die Frage auch unerheblich, macht doch die Klägerin keinerlei "
                          "Restwerklohnvergütung geltend. [Listenfortsetzung]"),
    ("Randzahl", "Die Beklagten haben keine dieser Leistungen abgenommen. Sie haben sie vielmehr ausdrücklich "
                 "gerügt."),
    ("Beweis", "Beweis:\tFotos vom 01.11.2026 (Anlage B 8);\nSachverständigengutachten unter Verwahrung gegen "
               "die Beweislast [Beweis]"),
    ("Randzahl", "Mit Nichtwissen werden die angesetzten Einheitspreise bestritten, insbesondere für"),
    ("Randzahl+1", "Pos. 01.002 Solarkabel, [Randzahl + Tab]"),
    ("Randzahl+1", "Pos. 01.010 Aluprofile."),
    ("Randzahl", "Unstreitig ist schließlich, dass die Klägerin nicht im Gewerk Dachdeckerei tätig ist. "
                 "[Randzahl – zählt nach dem Unterpunkt weiter]"),
    ("berschrift1", "Zur Widerklage [Überschrift 1 – III.]"),
    ("Randzahl!", "Die Widerklage ist begründet. [Randzahl – „Neu beginnen mit 1“]"),
    ("Randzahl", "Die Rechnung RE260210 genügt nicht den Anforderungen an eine prüffähige Schlussrechnung."),
    ("berschrift2", "Zinsanspruch [Überschrift 2]"),
    ("Randzahl", "Der Zinsanspruch folgt aus § 288 Abs. 2 BGB. [Randzahl – ohne Neubeginn läuft sie durch]"),
]


def main(src, dst):
    doc = Document(src)
    ids = {s.get(qn("w:styleId")): s for s in doc.styles.element.findall(qn("w:style"))}
    body = doc.element.body
    anchor = [p for p in doc.paragraphs if "{{text}}" in p.text][0]
    betreff = [p for p in doc.paragraphs if p.style.style_id == "Betreff"]
    # Betreff-Zeile füllen
    betreff[0].add_run(CONTENT[0][1])
    first = True
    for sid, text in CONTENT[1:]:
        p = anchor.insert_paragraph_before()
        real = sid[:-2] if sid.endswith("+1") else sid.rstrip("!")
        name = ids[real].find(qn("w:name")).get(qn("w:val"))
        p.style = doc.styles[name]
        parts = text.split("\n")
        for i, part in enumerate(parts):
            r = p.add_run(part)
            if i < len(parts) - 1:
                r.add_break()
        if first:
            # Abstand Betreff -> Text wie im Briefkopf
            p.paragraph_format.space_before = anchor.paragraph_format.space_before
            first = False
        if sid.endswith("!"):
            restart(doc, p, real)
        if sid.endswith("+1"):
            tab_level(p, 1)
    anchor._p.getparent().remove(anchor._p)
    doc.save(dst)


if __name__ == "__main__":
    main(*sys.argv[1:])
