# Eintrag-Seite – Symptome, Gefühle & Verhütung für einen Tag eintragen

import sys
import pathlib
from datetime import date
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox


class EintragWindow(QMainWindow):

    def __init__(self, eintrag_datum=None):
        super().__init__()

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/eintrag_femhealth.ui", self)

        # Datum setzen (Standard: heute)
        if eintrag_datum is None:
            self.eintrag_datum = date.today()
        else:
            self.eintrag_datum = eintrag_datum

        # Header-Datum aktualisieren
        self.datum_anzeigen()

        # ── Buttons verbinden ─────────────────────────────────────────────────

        # Schließen & Speichern
        self.main_window.btnClose.clicked.connect(self.on_schliessen)
        self.main_window.btnSpeichern.clicked.connect(self.on_speichern)
        self.main_window.btnPersonalisieren.clicked.connect(self.on_personalisieren)

        # Wochenstreifen – Tage
        self.main_window.btnDay25.clicked.connect(lambda: self.on_tag_gewaehlt(25))
        self.main_window.dayToday.clicked.connect(lambda: self.on_tag_gewaehlt(26))
        self.main_window.btnDay27.clicked.connect(lambda: self.on_tag_gewaehlt(27))
        self.main_window.btnDay28.clicked.connect(lambda: self.on_tag_gewaehlt(28))
        self.main_window.btnDay29.clicked.connect(lambda: self.on_tag_gewaehlt(29))
        self.main_window.btnDay30.clicked.connect(lambda: self.on_tag_gewaehlt(30))
        self.main_window.btnDay31.clicked.connect(lambda: self.on_tag_gewaehlt(31))

        # "Mehr erfahren"-Links
        self.main_window.btnMehrPeriode.clicked.connect(
            lambda: self.on_mehr_erfahren("Periode"))
        self.main_window.btnMehrSchmier.clicked.connect(
            lambda: self.on_mehr_erfahren("Schmierblutung"))
        self.main_window.btnMehrGefuehle.clicked.connect(
            lambda: self.on_mehr_erfahren("Gefühle"))
        self.main_window.btnMehrSchmerzen.clicked.connect(
            lambda: self.on_mehr_erfahren("Schmerzen"))
        self.main_window.btnMehrSexleben.clicked.connect(
            lambda: self.on_mehr_erfahren("Sexleben"))
        self.main_window.btnMehrAusfluss.clicked.connect(
            lambda: self.on_mehr_erfahren("Ausfluss"))
        self.main_window.btnMehrHaut.clicked.connect(
            lambda: self.on_mehr_erfahren("Haut"))
        self.main_window.btnMehrVerdauung.clicked.connect(
            lambda: self.on_mehr_erfahren("Verdauung"))
        self.main_window.btnMehrStuhlgang.clicked.connect(
            lambda: self.on_mehr_erfahren("Stuhlgang"))
        self.main_window.btnMehrTests.clicked.connect(
            lambda: self.on_mehr_erfahren("Tests"))
        self.main_window.btnMehrPille.clicked.connect(
            lambda: self.on_mehr_erfahren("Antibabypille"))
        self.main_window.btnMehrSpirale.clicked.connect(
            lambda: self.on_mehr_erfahren("Spirale"))
        self.main_window.btnMehrSpritze.clicked.connect(
            lambda: self.on_mehr_erfahren("Verhütungsspritze"))
        self.main_window.btnMehrImplantat.clicked.connect(
            lambda: self.on_mehr_erfahren("Hormonimplantat"))
        self.main_window.btnMehrPflaster.clicked.connect(
            lambda: self.on_mehr_erfahren("Verhütungspflaster"))
        self.main_window.btnMehrRing.clicked.connect(
            lambda: self.on_mehr_erfahren("Verhütungsring"))

    # ── Datum anzeigen ────────────────────────────────────────────────────────

    def datum_anzeigen(self):
        # Datum im Header formatieren: "Heute: 26. Mai 2026"
        monatsnamen = [
            "", "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        datum_text = (
            str(self.eintrag_datum.day) + ". "
            + monatsnamen[self.eintrag_datum.month] + " "
            + str(self.eintrag_datum.year)
        )

        if self.eintrag_datum == date.today():
            self.main_window.lblHeaderDate.setText("Heute: " + datum_text)
        else:
            self.main_window.lblHeaderDate.setText(datum_text)

        # Badge oben rechts (Tageszahl)
        self.main_window.lblTodayBadge.setText(str(self.eintrag_datum.day))

        print("Datum gesetzt: " + datum_text)

    # ── Slots: Wochenstreifen ─────────────────────────────────────────────────

    def on_tag_gewaehlt(self, tag_nr):
        # Ausgewählten Tag im aktuellen Monat setzen
        self.eintrag_datum = date(
            self.eintrag_datum.year,
            self.eintrag_datum.month,
            tag_nr
        )
        self.datum_anzeigen()
        print("Tag gewählt: " + str(self.eintrag_datum))

    # ── Slots: Allgemein ──────────────────────────────────────────────────────

    def on_personalisieren(self):
        # TODO: Personalisierungsdialog öffnen (Kategorien ein-/ausblenden)
        print("Personalisieren geöffnet")
        QMessageBox.information(
            self,
            "Personalisieren",
            "Hier kannst du später Kategorien anpassen."
        )

    def on_mehr_erfahren(self, kategorie):
        # TODO: Infoseite zur gewählten Kategorie öffnen
        print("Mehr erfahren: " + kategorie)
        QMessageBox.information(
            self,
            "Mehr erfahren – " + kategorie,
            "Informationen zu '" + kategorie + "' kommen noch!"
        )

    def on_schliessen(self):
        # Zurück zum Kalender ohne zu speichern
        print("Eintrag geschlossen ohne Speichern")
        self.close()

    def on_speichern(self):
        # ── Alle ausgewählten Karten auslesen ─────────────────────────────────

        # Periode
        periode = ""
        if self.main_window.cardLeicht.isChecked():
            periode = "Leicht"
        elif self.main_window.cardMittel.isChecked():
            periode = "Mittel"
        elif self.main_window.cardStark.isChecked():
            periode = "Stark"
        elif self.main_window.cardSehrStark.isChecked():
            periode = "Sehr stark"

        # Schmierblutung
        schmier = ""
        if self.main_window.cardRot.isChecked():
            schmier = "Rot"
        elif self.main_window.cardBraun.isChecked():
            schmier = "Braun"

        # Gefühle (Mehrfachauswahl möglich)
        gefuehle = []
        if self.main_window.cardStimmung.isChecked():
            gefuehle.append("Stimmungsschwankungen")
        if self.main_window.cardGut.isChecked():
            gefuehle.append("Gut")
        if self.main_window.cardTraurig.isChecked():
            gefuehle.append("Traurig")
        if self.main_window.cardSensibel.isChecked():
            gefuehle.append("Sensibel")
        if self.main_window.cardWuetend.isChecked():
            gefuehle.append("Wütend")
        if self.main_window.cardReizbar.isChecked():
            gefuehle.append("Reizbar")
        if self.main_window.cardUnruhig.isChecked():
            gefuehle.append("Unruhig")
        if self.main_window.cardGleichweit.isChecked():
            gefuehle.append("Gleichmütig")

        # Schmerzen (Mehrfachauswahl möglich)
        schmerzen = []
        if self.main_window.cardSchmerzfrei.isChecked():
            schmerzen.append("Schmerzfrei")
        if self.main_window.cardKraempfe.isChecked():
            schmerzen.append("Krämpfe")
        if self.main_window.cardBrueste.isChecked():
            schmerzen.append("Sensible Brüste")
        if self.main_window.cardKopf.isChecked():
            schmerzen.append("Kopfschmerzen")
        if self.main_window.cardRuecken.isChecked():
            schmerzen.append("Rückenschmerzen")

        # Sexleben
        sexleben = []
        if self.main_window.cardGeschuetzt.isChecked():
            sexleben.append("Geschützt")
        if self.main_window.cardUngeschuetzt.isChecked():
            sexleben.append("Ungeschützt")
        if self.main_window.cardInterruptus.isChecked():
            sexleben.append("Interruptus")
        if self.main_window.cardKeinSex.isChecked():
            sexleben.append("Kein Sex")
        if self.main_window.cardStarkLib.isChecked():
            sexleben.append("Starke Libido")
        if self.main_window.cardSchwachLib.isChecked():
            sexleben.append("Schwache Libido")
        if self.main_window.cardSchmerzSex.isChecked():
            sexleben.append("Schmerzhafter Sex")

        # Tägliche Notiz
        notiz = self.main_window.txtNotiz.toPlainText().strip()

        # Ausfluss
        ausfluss = []
        if self.main_window.cardKeinAusfluss.isChecked():
            ausfluss.append("Keinen")
        if self.main_window.cardKlebrig.isChecked():
            ausfluss.append("Klebrig")
        if self.main_window.cardCremig.isChecked():
            ausfluss.append("Cremig")
        if self.main_window.cardFadenziehend.isChecked():
            ausfluss.append("Fadenziehend")
        if self.main_window.cardUntypisch.isChecked():
            ausfluss.append("Untypisch")

        # Haut
        haut = []
        if self.main_window.cardHautOk.isChecked():
            haut.append("Ok")
        if self.main_window.cardHautGut.isChecked():
            haut.append("Gut")
        if self.main_window.cardPickel.isChecked():
            haut.append("Pickel")
        if self.main_window.cardTrocken.isChecked():
            haut.append("Trocken")
        if self.main_window.cardFettig.isChecked():
            haut.append("Fettig")
        if self.main_window.cardJuckend.isChecked():
            haut.append("Juckend")

        # Verdauung
        verdauung = []
        if self.main_window.cardVerdOk.isChecked():
            verdauung.append("Ok")
        if self.main_window.cardBlaehbauch.isChecked():
            verdauung.append("Aufgebläht")
        if self.main_window.cardBlaehungen.isChecked():
            verdauung.append("Blähungen")
        if self.main_window.cardSodbrennen.isChecked():
            verdauung.append("Sodbrennen")
        if self.main_window.cardUebel.isChecked():
            verdauung.append("Übel")
        if self.main_window.cardErbrechen.isChecked():
            verdauung.append("Erbrechen")

        # Stuhlgang
        stuhlgang = ""
        if self.main_window.cardStOk.isChecked():
            stuhlgang = "Ok"
        elif self.main_window.cardVerstopfung.isChecked():
            stuhlgang = "Verstopfung"
        elif self.main_window.cardDurchfall.isChecked():
            stuhlgang = "Durchfall"

        # Tests
        tests = []
        if self.main_window.cardPosOvu.isChecked():
            tests.append("Pos. Ovulationstest")
        if self.main_window.cardNegOvu.isChecked():
            tests.append("Neg. Ovulationstest")
        if self.main_window.cardPosSchwanger.isChecked():
            tests.append("Pos. Schwangerschaftstest")
        if self.main_window.cardNegSchwanger.isChecked():
            tests.append("Neg. Schwangerschaftstest")

        # Antibabypille
        pille = ""
        if self.main_window.cardPilleGenommen.isChecked():
            pille = "Genommen"
        elif self.main_window.cardPilleVergessen.isChecked():
            pille = "Vergessen"
        elif self.main_window.cardPilleSpat.isChecked():
            pille = "Spät genommen"
        elif self.main_window.cardPilleDoppel.isChecked():
            pille = "Doppelte Dosis"
        elif self.main_window.cardPillenfrei.isChecked():
            pille = "Pillenfreier Tag"

        # Spirale
        spirale = ""
        if self.main_window.cardSpirFaden.isChecked():
            spirale = "Faden überprüft"
        elif self.main_window.cardSpirEingesetzt.isChecked():
            spirale = "Eingesetzt"
        elif self.main_window.cardSpirEntfernt.isChecked():
            spirale = "Entfernt"
        elif self.main_window.cardSpirAusgewechselt.isChecked():
            spirale = "Ausgewechselt"

        # Verhütungsspritze
        spritze = "Verabreicht" if self.main_window.cardSpritzVer.isChecked() else ""

        # Hormonimplantat
        implantat = ""
        if self.main_window.cardImplEingesetzt.isChecked():
            implantat = "Eingesetzt"
        elif self.main_window.cardImplEntfernt.isChecked():
            implantat = "Entfernt"
        elif self.main_window.cardImplAusgewechselt.isChecked():
            implantat = "Ausgewechselt"

        # Verhütungspflaster
        pflaster = ""
        if self.main_window.cardPflAufgeklebt.isChecked():
            pflaster = "Aufgeklebt"
        elif self.main_window.cardPflEntfernt.isChecked():
            pflaster = "Entfernt"
        elif self.main_window.cardPflSpatAuf.isChecked():
            pflaster = "Spät aufgeklebt"
        elif self.main_window.cardPflSpatEnt.isChecked():
            pflaster = "Spät entfernt"
        elif self.main_window.cardPflAusgewechselt.isChecked():
            pflaster = "Ausgewechselt"

        # Verhütungsring
        ring = ""
        if self.main_window.cardRingEingesetzt.isChecked():
            ring = "Eingesetzt"
        elif self.main_window.cardRingEntfernt.isChecked():
            ring = "Entfernt"
        elif self.main_window.cardRingSpatEin.isChecked():
            ring = "Spät eingesetzt"
        elif self.main_window.cardRingSpatEnt.isChecked():
            ring = "Spät entfernt"
        elif self.main_window.cardRingAusgewechselt.isChecked():
            ring = "Ausgewechselt"

        # ── Alles in der Konsole ausgeben (Debug) ─────────────────────────────
        print("── Eintrag für " + str(self.eintrag_datum) + " ──")
        print("Periode:          " + periode)
        print("Schmierblutung:   " + schmier)
        print("Gefühle:          " + ", ".join(gefuehle))
        print("Schmerzen:        " + ", ".join(schmerzen))
        print("Sexleben:         " + ", ".join(sexleben))
        print("Notiz:            " + notiz)
        print("Ausfluss:         " + ", ".join(ausfluss))
        print("Haut:             " + ", ".join(haut))
        print("Verdauung:        " + ", ".join(verdauung))
        print("Stuhlgang:        " + stuhlgang)
        print("Tests:            " + ", ".join(tests))
        print("Pille:            " + pille)
        print("Spirale:          " + spirale)
        print("Spritze:          " + spritze)
        print("Implantat:        " + implantat)
        print("Pflaster:         " + pflaster)
        print("Ring:             " + ring)

        # TODO: Eintrag in Datenbank speichern
        # Beispiel: db.speichere_eintrag(self.eintrag_datum, periode, gefuehle, ...)

        QMessageBox.information(self, "Gespeichert", "Dein Eintrag wurde gespeichert! ✅")
        self.close()

    # ── Hilfsmethode ─────────────────────────────────────────────────────────

    def zeige_fehler(self, text):
        QMessageBox.warning(self, "Fehler", text)


# ── Programm starten ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EintragWindow()
    window.show()
    sys.exit(app.exec())
