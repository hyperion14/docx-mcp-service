"""Entwurf v2 der AnNoText-Textbausteine „Adresse" (DIN 5008 Form B).

Ändert das Original-RTF minimal und schreibt eine neue Datei; das Original bleibt unverändert.
Aufruf: python3 textbaustein_v2.py <original.rtf> <ziel.rtf>

Änderungen:
1. Zeile 1 (Versandvermerk, [M_VERSANDART]) = Zusatz- und Vermerkzone: Höhe exakt 17,7 mm,
   Inhalt unten ausgerichtet (direkt über der Anschrift).
2. Zeile 2 ([ADDRESS_LAYOUT]) = Anschriftzone: Höhe exakt 27,3 mm (max. 6 Zeilen) statt „mindestens 45,7 mm".
   Damit beginnt die Anschrift bei 62,7 mm und endet bei 90 mm – vorausgesetzt, der Baustein beginnt bei
   45 mm (FREIBURG.dotx Entwurf v2).
3. Datum: „Freiburg, den [M_TAGDATUM]" entfällt; stattdessen erste Zeile im Informationsblock
   „Datum: [M_TAGDATUM]" (DIN 5008, ortsneutral für alle Standorte).
"""
import re
import sys

VERMERK_H = 1003   # 17,7 mm
ANSCHRIFT_H = 1548  # 27,3 mm


def main(src, dst):
    s = open(src, encoding="cp1252", newline="").read()
    n = 0

    # 1. Versandart-Zeile (\irow0, Zeilendefinition steht zweimal): exakte Höhe, Zelle unten ausgerichtet
    def row0(m):
        return m.group(0).replace("\\clvertalt", "\\clvertalb")
    s, k1 = re.subn(r"\\irow0\\irowband0", "\\\\irow0\\\\irowband0\\\\trrh-%d" % VERMERK_H, s)
    s, k2 = re.subn(r"\\trowd \\irow0\\irowband0.*?\\cellx\d+", row0, s, flags=re.S)
    # 2. Anschriftzone: exakte Höhe
    s, k3 = re.subn(r"\\trrh2591", "\\\\trrh-%d" % ANSCHRIFT_H, s)
    assert (k1, k2, k3) == (2, 2, 2), (k1, k2, k3)
    # 3. Datum in den Informationsblock
    old_date = "Freiburg, den [M_TAGDATUM]"
    assert s.count(old_date) == 1, "Datumszeile nicht eindeutig"
    s = s.replace(old_date, "")
    lab = re.compile(r"\{\\rtlch\\fcs1 \\ab\\af\d+\\afs18 \\ltrch\\fcs0\s+\\b\\fs18")

    def insert_before_group(s, marker, text):
        i = s.index(marker)
        starts = [m.start() for m in lab.finditer(s, 0, i)]
        j = starts[-1]
        return s[:j] + "{\\rtlch\\fcs1 \\af1\\afs18 \\ltrch\\fcs0 \\fs18 %s\\par }" % text + s[j:]
    s = insert_before_group(s, "Unser Zeichen:", "Datum:")
    s = insert_before_group(s, "[M_AZ] [M_RAKZ]", "[M_TAGDATUM]")
    open(dst, "w", encoding="cp1252", newline="").write(s)
    print("geschrieben:", dst)


if __name__ == "__main__":
    main(*sys.argv[1:])
