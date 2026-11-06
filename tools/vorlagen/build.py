"""Baut den neuen BHK-Briefkopf aus dem Original-Briefkopf.

Aufruf: python3 build.py <original.docx> <ziel.docx> [<ziel.dotx>]
"""
import copy
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def q(tag):
    p, t = tag.split(":")
    return "{%s}%s" % ({"w": W}[p], t)


def el(tag, **attrs):
    e = etree.Element(q(tag))
    for k, v in attrs.items():
        e.set(q("w:" + k), str(v))
    return e


def frag(xml):
    """XML-Fragment mit w:-Präfix parsen."""
    return etree.fromstring('<root xmlns:w="%s">%s</root>' % (W, xml))[0]


# ---------------------------------------------------------------- Maße (Twips)
CM = 567            # 1 cm
NUMCOL = CM         # Nummernspalte 1 cm
LINE = 'w:line="312" w:lineRule="auto"'   # 1,3-zeilig

# --------------------------------------------------------- Listendefinitionen
ABS_GLIEDERUNG = 90
ABS_RANDZAHL = 91
ABS_BULLET = 92
ABS_NUMMER = 93
ABS_ANTRAG = 94
NUM_GLIEDERUNG = 90
NUM_RANDZAHL = 91
NUM_BULLET = 92
NUM_NUMMER = 93
NUM_ANTRAG = 94


def lvl(ilvl, fmt, text, left, hanging, pstyle=None, bold=None, font=None):
    x = '<w:lvl w:ilvl="%d"><w:start w:val="1"/><w:numFmt w:val="%s"/>' % (ilvl, fmt)
    if pstyle:
        x += '<w:pStyle w:val="%s"/>' % pstyle
    x += '<w:lvlText w:val="%s"/><w:lvlJc w:val="left"/>' % text
    x += '<w:pPr><w:tabs><w:tab w:val="num" w:pos="%d"/></w:tabs><w:ind w:left="%d" w:hanging="%d"/></w:pPr>' % (left, left, hanging)
    if font:
        x += '<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s" w:hint="default"/></w:rPr>' % (font, font, font)
    x += '</w:lvl>'
    return x


def abstract(aid, name, levels, multi=True):
    x = '<w:abstractNum w:abstractNumId="%d"><w:multiLevelType w:val="%s"/><w:name w:val="%s"/>' % (
        aid, "multilevel" if multi else "hybridMultilevel", name)
    x += "".join(levels) + "</w:abstractNum>"
    return frag(x)


def build_numbering(numbering):
    # Gliederung I. / 1. / a. / aa. / i. / (1) / (a) – eine Liste, an Überschrift 1-7 gekoppelt
    g = [
        lvl(0, "upperRoman", "%1.", NUMCOL, NUMCOL, "berschrift1"),
        lvl(1, "decimal", "%2.", NUMCOL, NUMCOL, "berschrift2"),
        lvl(2, "lowerLetter", "%3.", NUMCOL, NUMCOL, "berschrift3"),
        lvl(3, "lowerLetter", "%4%4.", NUMCOL, NUMCOL, "berschrift4"),
        lvl(4, "lowerRoman", "%5.", NUMCOL, NUMCOL, "berschrift5"),
        lvl(5, "decimal", "(%6)", NUMCOL, NUMCOL, "berschrift6"),
        lvl(6, "lowerLetter", "(%7)", NUMCOL, NUMCOL, "berschrift7"),
        lvl(7, "lowerRoman", "(%8)", NUMCOL, NUMCOL),
        lvl(8, "decimal", "%9.", NUMCOL, NUMCOL),
    ]
    # Randzahl: eigene einfache Liste, Tab -> a) -> i)
    r = [
        lvl(0, "decimal", "%1.", NUMCOL, NUMCOL, "Randzahl"),
        lvl(1, "lowerLetter", "%2)", 2 * NUMCOL, NUMCOL),
        lvl(2, "lowerRoman", "%3)", 3 * NUMCOL, NUMCOL),
    ] + [lvl(i, "decimal", "%" + str(i + 1) + ".", (i + 1) * NUMCOL, NUMCOL) for i in range(3, 9)]
    # Aufzählungszeichen – und •
    bl = [
        lvl(0, "bullet", "–", 567, 283, "Aufzhlungszeichen", font="Arial"),
        lvl(1, "bullet", "•", 1134, 283, "Aufzhlungszeichen2", font="Arial"),
    ] + [lvl(i, "bullet", "–", 567 * (i + 1), 283, font="Arial") for i in range(2, 9)]
    # Listennummer 1.) / a.)
    nl = [
        lvl(0, "decimal", "%1.)", 851, 567, "Listennummer"),
        lvl(1, "lowerLetter", "%2.)", 1418, 567, "Listennummer2"),
    ] + [lvl(i, "decimal", "%" + str(i + 1) + ".)", 851 + 567 * i, 567) for i in range(2, 9)]
    # Anträge 1. 2. 3. (eingerückt)
    an = [lvl(0, "decimal", "%1.", 1134, 567, "Antrag")] + [
        lvl(i, "lowerLetter", "%" + str(i + 1) + ")", 1134 + 567 * i, 567) for i in range(1, 9)]

    new_abs = [abstract(ABS_GLIEDERUNG, "BHK Gliederung", g),
               abstract(ABS_RANDZAHL, "BHK Randzahl", r),
               abstract(ABS_BULLET, "BHK Aufzählung", bl, multi=False),
               abstract(ABS_NUMMER, "BHK Nummerierung", nl, multi=False),
               abstract(ABS_ANTRAG, "BHK Antrag", an, multi=False)]

    # alte Kopplungen der Überschriften an Altlisten lösen
    for p in list(numbering.iter(q("w:pStyle"))):
        if p.get(q("w:val")) in ("berschrift1", "berschrift2", "berschrift3", "berschrift4"):
            p.getparent().remove(p)

    first_num = numbering.find("w:num", NS)
    for a in new_abs:
        first_num.addprevious(a)
    for nid, aid in ((NUM_GLIEDERUNG, ABS_GLIEDERUNG), (NUM_RANDZAHL, ABS_RANDZAHL),
                     (NUM_BULLET, ABS_BULLET), (NUM_NUMMER, ABS_NUMMER), (NUM_ANTRAG, ABS_ANTRAG)):
        numbering.append(frag('<w:num w:numId="%d"><w:abstractNumId w:val="%d"/></w:num>' % (nid, aid)))


def prune_numbering(numbering, texts):
    """Nicht referenzierte Listeninstanzen und Definitionen entfernen."""
    used = set()
    for t in texts:
        used |= set(re.findall(r'<w:numId w:val="(\d+)"', t))
    removed = 0
    for n in numbering.findall("w:num", NS):
        if n.get(q("w:numId")) not in used:
            numbering.remove(n)
            removed += 1
    used_abs = {n.find("w:abstractNumId", NS).get(q("w:val")) for n in numbering.findall("w:num", NS)}
    # über numStyleLink/styleLink verbundene Definitionen behalten
    for a in numbering.findall("w:abstractNum", NS):
        if a.get(q("w:abstractNumId")) not in used_abs:
            numbering.remove(a)
            removed += 1
    return removed


# ------------------------------------------------------------------- Vorlagen
def style(sid, name, based=None, nxt=None, ppr="", rpr="", custom=False, prio=None, qf=True,
          link=None):
    x = '<w:style w:type="paragraph" w:styleId="%s"%s>' % (sid, ' w:customStyle="1"' if custom else "")
    x += '<w:name w:val="%s"/>' % name
    if based:
        x += '<w:basedOn w:val="%s"/>' % based
    if nxt:
        x += '<w:next w:val="%s"/>' % nxt
    if link:
        x += '<w:link w:val="%s"/>' % link
    if prio is not None:
        x += '<w:uiPriority w:val="%d"/>' % prio
    if qf:
        x += "<w:qFormat/>"
    if ppr:
        x += "<w:pPr>%s</w:pPr>" % ppr
    if rpr:
        x += "<w:rPr>%s</w:rPr>" % rpr
    return frag(x + "</w:style>")


def heading(n, rpr, before):
    ilvl = n - 1
    ppr = ('<w:keepNext/><w:keepLines/><w:numPr><w:ilvl w:val="%d"/><w:numId w:val="%d"/></w:numPr>'
           '<w:spacing w:before="%d" w:after="120" %s/>'
           '<w:jc w:val="left"/><w:outlineLvl w:val="%d"/>' % (ilvl, NUM_GLIEDERUNG, before, LINE, ilvl))
    return style("berschrift%d" % n, "heading %d" % n, nxt="Textkrper", ppr=ppr,
                 rpr=rpr + '<w:kern w:val="0"/>', prio=9, link="berschrift%dZchn" % n)


BODY_PPR = '<w:spacing w:before="0" w:after="200" %s/><w:jc w:val="both"/>' % LINE
BODY_RPR = '<w:lang w:val="de-DE" w:eastAsia="en-US" w:bidi="ar-SA"/>'


def new_styles():
    s = []
    s.append(style("Textkrper", "Body Text", nxt="Textkrper", ppr=BODY_PPR, rpr=BODY_RPR, prio=1,
                   link="TextkrperZchn"))
    s.append(style("ErsterAbsatz", "First Paragraph", based="Textkrper", nxt="Textkrper", custom=True,
                   prio=2))
    s.append(style("Compact", "Compact", based="Textkrper", custom=True, prio=40, qf=False,
                   ppr='<w:spacing w:after="80"/>'))
    s.append(heading(1, "<w:b/><w:bCs/>", 360))
    s.append(heading(2, "<w:b/><w:bCs/>", 240))
    s.append(heading(3, "<w:b/><w:bCs/>", 240))
    s.append(heading(4, "<w:i/><w:iCs/>", 240))
    s.append(heading(5, "", 240))
    s.append(heading(6, "", 240))
    s.append(heading(7, "", 240))
    s.append(style("Randzahl", "Randzahl", based="Textkrper", nxt="Randzahl", custom=True, prio=3,
                   ppr='<w:numPr><w:numId w:val="%d"/></w:numPr>' % NUM_RANDZAHL))
    s.append(style("Listenfortsetzung", "List Continue", based="Textkrper", prio=4,
                   ppr='<w:ind w:left="%d"/>' % NUMCOL))
    s.append(style("Listenfortsetzung2", "List Continue 2", based="Textkrper", prio=5,
                   ppr='<w:ind w:left="851"/>'))
    s.append(style("Beweis", "Beweis", based="Textkrper", custom=True, prio=6,
                   ppr='<w:tabs><w:tab w:val="left" w:pos="1985"/></w:tabs><w:jc w:val="left"/>'
                       '<w:ind w:left="1985" w:hanging="1418"/>'))
    s.append(style("Antrag", "Antrag", based="Textkrper", nxt="Antrag", custom=True, prio=7,
                   ppr='<w:numPr><w:numId w:val="%d"/></w:numPr>' % NUM_ANTRAG))
    lst = '<w:spacing w:after="80"/>'
    s.append(style("Aufzhlungszeichen", "List Bullet", based="Textkrper", prio=10,
                   ppr='<w:numPr><w:numId w:val="%d"/></w:numPr>%s'
                   % (NUM_BULLET, lst)))
    s.append(style("Aufzhlungszeichen2", "List Bullet 2", based="Textkrper", prio=11,
                   ppr='<w:numPr><w:ilvl w:val="1"/><w:numId w:val="%d"/></w:numPr>%s'
                       '' % (NUM_BULLET, lst)))
    s.append(style("Listennummer", "List Number", based="Textkrper", prio=12,
                   ppr='<w:numPr><w:numId w:val="%d"/></w:numPr>%s'
                   % (NUM_NUMMER, lst)))
    s.append(style("Listennummer2", "List Number 2", based="Textkrper", prio=13,
                   ppr='<w:numPr><w:ilvl w:val="1"/><w:numId w:val="%d"/></w:numPr>%s'
                       '' % (NUM_NUMMER, lst)))
    s.append(style("Blocktext", "Block Text", based="Textkrper", nxt="Textkrper", prio=20,
                   ppr='<w:ind w:left="567" w:right="567"/>'))
    s.append(style("Zitat", "Quote", based="Blocktext", nxt="Textkrper", prio=21, rpr="<w:i/><w:iCs/>",
                   link="ZitatZchn"))
    s.append(style("Funotentext", "footnote text", prio=99, qf=False, link="FunotentextZchn",
                   ppr='<w:spacing w:after="40" w:line="240" w:lineRule="auto"/><w:jc w:val="both"/>'
                       '<w:ind w:left="170" w:hanging="170"/>',
                   rpr='<w:sz w:val="18"/><w:szCs w:val="18"/>'))
    s.append(style("Listenabsatz", "List Paragraph", based="Textkrper", prio=34, qf=False,
                   ppr='<w:ind w:left="720"/>'))
    # Briefrahmen
    s.append(style("Vermerk", "Vermerk", based="Standard", custom=True, prio=30,
                   rpr='<w:sz w:val="20"/><w:szCs w:val="20"/>'))
    s.append(style("Betreff", "Betreff", based="Standard", nxt="Textkrper", custom=True, prio=31,
                   ppr='<w:keepNext/><w:spacing w:before="0" w:after="0"/><w:contextualSpacing/>',
                   rpr="<w:b/><w:bCs/>"))
    s.append(style("Anrede", "Salutation", based="Standard", nxt="Textkrper", prio=32,
                   ppr='<w:spacing w:before="0" w:after="200" %s/>' % LINE, link="AnredeZchn"))
    s.append(style("Gruformel", "Closing", based="Standard", nxt="Unterschrift", prio=33,
                   ppr='<w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="0" %s/>' % LINE))
    # 3 Leerzeilen Platz für die Unterschrift; Folgezeilen (Rechtsanwalt) ohne Abstand
    s.append(style("Unterschrift", "Signature", based="Standard", prio=33,
                   ppr='<w:keepLines/><w:spacing w:before="900" w:after="0"/><w:contextualSpacing/>'))
    return s


LEGACY = ["BHKStandard", "BHKStandard1", "BHKStruktur", "BHKVertrag", "BHKVertrag1", "BHKVertrag2",
          "BHKVertrag3", "BHKVertrag4", "BHKVertrag5", "BHKVF1", "BHKVF2", "Abrechnung",
          "FordAufstellung", "Aufzhler", "LF1", "Makrotext", "KeinAbsatzformat", "Standardeinzug",
          "BK1", "BK2", "BK3", "BK4"]


def build_styles(styles):
    by_id = {s.get(q("w:styleId")): s for s in styles.findall("w:style", NS)}
    # Grundeinstellung: Arial 11, Deutsch, 0 pt Abstand, einfach
    dd = styles.find("w:docDefaults", NS)
    dd.getparent().replace(dd, frag(
        '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:eastAsia="Times New Roman" '
        'w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/>'
        '<w:lang w:val="de-DE" w:eastAsia="de-DE" w:bidi="ar-SA"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
        '</w:pPrDefault></w:docDefaults>'))

    for ns in new_styles():
        sid = ns.get(q("w:styleId"))
        if sid in by_id:
            old = by_id[sid]
            # Zeichenvorlagen-Verknüpfung (link) aus der alten Vorlage übernehmen, falls vorhanden
            old_link = old.find("w:link", NS)
            if old_link is not None and ns.find("w:link", NS) is None:
                ns.find("w:name", NS).addnext(copy.deepcopy(old_link))
            old.getparent().replace(old, ns)
        else:
            styles.append(ns)
        by_id[sid] = ns

    # Zeichenvorlagen der Überschriften: Fett/Kursiv passend
    for n, rpr in ((1, "<w:b/>"), (2, "<w:b/>"), (3, "<w:b/>"), (4, "<w:i/>"), (5, ""), (6, ""), (7, "")):
        cid = "berschrift%dZchn" % n
        x = ('<w:style w:type="character" w:customStyle="1" w:styleId="%s"><w:name w:val="Überschrift %d Zchn"/>'
             '<w:basedOn w:val="Absatz-Standardschriftart"/><w:link w:val="berschrift%d"/><w:uiPriority w:val="9"/>'
             '<w:rPr>%s</w:rPr></w:style>' % (cid, n, n, rpr))
        if cid in by_id:
            by_id[cid].getparent().replace(by_id[cid], frag(x))
        else:
            styles.append(frag(x))
    for cid, rpr in (("TextkrperZchn", ""), ("ZitatZchn", "<w:i/><w:iCs/>"),
                     ("FunotentextZchn", '<w:sz w:val="18"/><w:szCs w:val="18"/>')):
        if cid in by_id:
            st = by_id[cid]
            r = st.find("w:rPr", NS)
            if r is not None:
                st.remove(r)
            if rpr:
                st.append(frag("<w:rPr>%s</w:rPr>" % rpr))

    # Altvorlagen bleiben, verschwinden aber aus der Schnellauswahl
    for sid in LEGACY:
        st = by_id.get(sid)
        if st is None:
            continue
        for qfe in st.findall("w:qFormat", NS):
            st.remove(qfe)
        up = st.find("w:uiPriority", NS)
        if up is None:
            up = el("w:uiPriority", val=99)
            st.find("w:name", NS).addnext(up)
        up.set(q("w:val"), "99")
    # LF_1 erbt von Überschrift 1 – nicht in Navigation/Inhaltsverzeichnis
    lf = by_id.get("LF1")
    if lf is not None:
        ppr = lf.find("w:pPr", NS)
        for o in ppr.findall("w:outlineLvl", NS):
            ppr.remove(o)
        ppr.append(el("w:outlineLvl", val=9))
    # Alt-Absatzvorlagen mit Bezug auf Blocktext/Textkörper: nichts zu tun. Adresse ohne Abstände
    adr = by_id.get("Adresse")
    if adr is not None:
        adr.find("w:pPr", NS).getparent().replace(adr.find("w:pPr", NS), frag(
            '<w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'))


# ------------------------------------------------------------------- Dokument
def build_document(doc):
    s = doc
    # --- Anschriftfeld DIN 5008 Form B: Zeile A = Zusatz-/Vermerkzone (17,7 mm),
    #     Zeile B = Anschriftzone (27,3 mm); Tabelle beginnt bei 45 mm (oberer Rand)
    tbl = re.search(r"<w:tbl>.*?</w:tbl>", s, re.S).group(0)
    rows = re.findall(r"<w:tr[ >].*?</w:tr>", tbl, re.S)
    row0 = rows[0]
    paras = re.findall(r"<w:p[ >].*?</w:p>", row0, re.S)
    addr = [p for p in paras if 'w:val="Adresse"' in p]
    vermerk = [p for p in paras if "Per E-Mail" in p][0]
    addr = [re.sub(r'<w:spacing w:before="40"/><w:contextualSpacing/>', "", p) for p in addr]
    vermerk = re.sub(r"<w:pPr>.*?</w:pPr>", '<w:pPr><w:pStyle w:val="Vermerk"/></w:pPr>', vermerk, count=1,
                     flags=re.S)
    # Fettung aus dem Vermerk nehmen
    vermerk = re.sub(r"<w:b/>|<w:bCs/>", "", vermerk)
    tcpr = '<w:tcPr><w:tcW w:w="5557" w:type="dxa"/><w:gridSpan w:val="2"/>%s</w:tcPr>'
    rowA = ('<w:tr><w:trPr><w:gridAfter w:val="1"/><w:wAfter w:w="539" w:type="dxa"/><w:cantSplit/>'
            '<w:trHeight w:val="1003" w:hRule="exact"/></w:trPr><w:tc>%s%s</w:tc></w:tr>'
            % (tcpr % '<w:vAlign w:val="bottom"/>', vermerk))
    rowB = ('<w:tr><w:trPr><w:gridAfter w:val="1"/><w:wAfter w:w="539" w:type="dxa"/><w:cantSplit/>'
            '<w:trHeight w:val="1548" w:hRule="exact"/></w:trPr><w:tc>%s%s</w:tc></w:tr>'
            % (tcpr % "", "".join(addr)))
    # Zeile 1 (Datum): zwei Leerabsätze vor dem Datum entfernen, Abstand fest
    row1 = rows[1]
    r1p = re.findall(r"<w:p[ >].*?</w:p>", row1, re.S)
    date_p = r1p[-1].replace("<w:pPr>", '<w:pPr><w:spacing w:before="360"/>', 1)
    row1 = row1.replace("".join(r1p), date_p) if "".join(r1p) in row1 else row1
    new_tbl = tbl.replace(row0, rowA + rowB).replace(rows[1], row1)
    s = s.replace(tbl, new_tbl)

    # Oberer Rand Seite 1 = Beginn Anschriftfeld (45 mm)
    s = s.replace('w:top="2665"', 'w:top="2552"', 1)
    # --- Briefkörper nach der Tabelle neu ordnen
    head, rest = s.split("</w:tbl>", 1)
    body_end = rest.index("<w:sectPr")
    tail = rest[body_end:]
    paras = re.findall(r"<w:p[ >].*?</w:p>", rest[:body_end], re.S)
    betreff = [p for p in paras if 'w:val="Betreff"' in p]
    betreff[0] = betreff[0].replace('<w:pStyle w:val="Betreff"/>',
                                    '<w:pStyle w:val="Betreff"/><w:spacing w:before="480"/>', 1)
    text = [p for p in paras if "{{text}}" in p][0].replace('w:val="BHKStandard1"', 'w:val="ErsterAbsatz"')
    text = text.replace("<w:pPr>", "<w:pPr>", 1)
    # Betreff -> Text: Abstand 2 Zeilen über die erste Textzeile
    text = text.replace('<w:pStyle w:val="ErsterAbsatz"/>',
                        '<w:pStyle w:val="ErsterAbsatz"/><w:spacing w:before="480"/>', 1)

    def restyle(p, sid):
        return re.sub(r"<w:pPr>.*?</w:pPr>", '<w:pPr><w:pStyle w:val="%s"/></w:pPr>' % sid, p, count=1,
                      flags=re.S)
    gruss = restyle([p for p in paras if "Mit freundlichen" in p][0], "Gruformel")
    name = restyle([p for p in paras if "Justus Kampp" in p][0], "Unterschrift")
    titel = restyle([p for p in paras if ">Rechtsanwalt<" in p][0], "Unterschrift")
    body = "".join(betreff) + text + gruss + name + titel
    return head + "</w:tbl>" + body + tail


LINE_ANCHOR_RE = re.compile(r'<w:r>(?:(?!<w:r>).)*?<wp:anchor[^>]*>(?:(?!</wp:anchor>).)*?'
                            r'<wp:posOffset>3780790</wp:posOffset>.*?</w:r>', re.S)


def add_marks(header):
    """Zweite Falzmarke (210 mm) und Lochmarke (148,5 mm) neben der vorhandenen Falzmarke (105 mm)."""
    m = LINE_ANCHOR_RE.search(header)
    if not m:
        raise SystemExit("Falzmarke nicht gefunden")
    run = m.group(0)
    out = []
    for i, (pos, name) in enumerate(((5346000, "Lochmarke"), (7560000, "Falzmarke 2"))):
        r = run.replace("<wp:posOffset>3780790</wp:posOffset>", "<wp:posOffset>%d</wp:posOffset>" % pos)
        r = re.sub(r'<wp:docPr id="\d+" name="[^"]*"', '<wp:docPr id="%d" name="%s"' % (9001 + i, name), r)
        r = re.sub(r' wp14:anchorId="[0-9A-F]+"', ' wp14:anchorId="7A1B2C%02d"' % (i + 1), r)
        r = re.sub(r' wp14:editId="[0-9A-F]+"', "", r)
        r = re.sub(r' relativeHeight="\d+"', ' relativeHeight="%d"' % (251657729 + i), r)
        out.append(r)
    return header.replace(run, run + "".join(out), 1)


def main(src, dst_docx, dst_dotx=None):
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(src) as z:
        z.extractall(tmp)
    wd = tmp / "word"
    parser = etree.XMLParser(remove_blank_text=False)

    # Design-Schriftarten -> Arial
    th = wd / "theme" / "theme1.xml"
    t = th.read_text(encoding="utf-8")
    t = re.sub(r'(<a:(?:major|minor)Font><a:latin typeface=")[^"]*(")', r"\1Arial\2", t)
    th.write_text(t, encoding="utf-8")

    st = etree.parse(str(wd / "styles.xml"), parser)
    build_styles(st.getroot())
    st.write(str(wd / "styles.xml"), xml_declaration=True, encoding="UTF-8", standalone=True)

    doc = (wd / "document.xml").read_text(encoding="utf-8")
    doc = build_document(doc)
    (wd / "document.xml").write_text(doc, encoding="utf-8")

    h3 = (wd / "header3.xml").read_text(encoding="utf-8")
    # leere Kopfzeilenabsätze der ersten Seite schieben den Text unter 45 mm – entfernen
    h3 = re.sub(r'<w:p [^>]*><w:pPr><w:pStyle w:val="Kopfzeile"/>(?:<w:spacing w:after="200"/>)?</w:pPr></w:p>', "", h3)
    (wd / "header3.xml").write_text(add_marks(h3), encoding="utf-8")

    nb = etree.parse(str(wd / "numbering.xml"), parser)
    build_numbering(nb.getroot())
    texts = [p.read_text(encoding="utf-8") for p in wd.glob("*.xml") if p.name != "numbering.xml"]
    removed = prune_numbering(nb.getroot(), texts)
    nb.write(str(wd / "numbering.xml"), xml_declaration=True, encoding="UTF-8", standalone=True)
    print("entfernte Altlisten-Einträge:", removed)

    def pack(dst, template=False):
        ct = (tmp / "[Content_Types].xml").read_text(encoding="utf-8")
        main_doc = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
        main_tpl = "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"
        ct2 = ct.replace(main_doc, main_tpl) if template else ct.replace(main_tpl, main_doc)
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
            names = sorted(p for p in tmp.rglob("*") if p.is_file())
            z.writestr("[Content_Types].xml", ct2)
            for p in names:
                arc = p.relative_to(tmp).as_posix()
                if arc == "[Content_Types].xml":
                    continue
                z.write(p, arc)
    pack(dst_docx)
    if dst_dotx:
        pack(dst_dotx, template=True)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main(*sys.argv[1:])
