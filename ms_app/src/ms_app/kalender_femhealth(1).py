# Kalender-Seite – Monatsübersicht mit Zyklus-Markierungen

import sys
import pathlib
from datetime import date, timedelta
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QGridLayout, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt


class KalenderWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/kalender_femhealth_neu(1).ui", self)

        # ── Zyklus-Beispieldaten (TODO: aus Datenbank laden) ──────────────────
        self.perioden_tage = [
            date(2026, 5, 5),
            date(2026, 5, 6),
            date(2026, 5, 7),
            date(2026, 5, 8),
            date(2026, 5, 9),
        ]
        self.eisprung_zone = [
            date(2026, 5, 14),
            date(2026, 5, 15),
            date(2026, 5, 16),
            date(2026, 5, 17),
        ]

        # Zyklusbeginn für Zyklustag-Berechnung
        self.zyklus_start  = date(2026, 5, 5)
        self.zyklus_laenge = 28

        # Aktuell ausgewählter Tag
        self.ausgewaehlter_tag = date.today()

        # Buttons mit Funktionen verbinden
        self.main_window.btnBack.clicked.connect(self.on_zurueck)
        self.main_window.btnTracken.clicked.connect(self.on_tracken)
        self.main_window.btnMehrErfahren.clicked.connect(self.on_mehr_erfahren)

        # Kalender aufbauen und Sheet befüllen
        self.kalender_aufbauen()
        self.detail_sheet_befuellen(date.today())

    # ── Kalender aufbauen ─────────────────────────────────────────────────────

    def kalender_aufbauen(self):
        # Platzhalter-Label verstecken
        self.main_window.lblPlaceholderInfo.setVisible(False)

        # Haupt-Layout für calContents anlegen
        haupt_layout = QVBoxLayout()
        haupt_layout.setContentsMargins(8, 4, 8, 4)
        haupt_layout.setSpacing(0)

        # Aktuellen und nächsten Monat anzeigen
        heute     = date.today()
        naechster = (heute.replace(day=1) + timedelta(days=32)).replace(day=1)

        self.monat_hinzufuegen(haupt_layout, heute.year, heute.month)
        self.monat_hinzufuegen(haupt_layout, naechster.year, naechster.month)

        haupt_layout.addStretch()
        self.main_window.calContents.setLayout(haupt_layout)

    def monat_hinzufuegen(self, eltern_layout, jahr, monat):
        # Monatsname als Label
        monatsnamen = [
            "", "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        monat_label = QLabel(monatsnamen[monat] + "  " + str(jahr))
        monat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        monat_label.setStyleSheet(
            "color:#880E4F; font-size:14px; font-weight:bold; background:transparent; padding:8px 0 4px;"
        )
        eltern_layout.addWidget(monat_label)

        # Grid für die Tages-Buttons
        grid = QGridLayout()
        grid.setSpacing(1)

        # Erster Tag des Monats → Wochentag bestimmen (0=Montag, 6=Sonntag)
        erster_tag   = date(jahr, monat, 1)
        start_spalte = erster_tag.weekday()

        # Anzahl Tage im Monat bestimmen
        if monat == 12:
            tage_im_monat = (date(jahr + 1, 1, 1) - timedelta(days=1)).day
        else:
            tage_im_monat = (date(jahr, monat + 1, 1) - timedelta(days=1)).day

        # Tages-Buttons einfügen
        zelle = start_spalte
        for tag_nr in range(1, tage_im_monat + 1):
            aktuelles_datum = date(jahr, monat, tag_nr)
            zeile  = (zelle // 7) + 1
            spalte = zelle % 7

            btn = QPushButton(str(tag_nr))
            btn.setMinimumHeight(38)
            btn.setMaximumHeight(38)
            btn.setStyleSheet(self.tag_stil_bestimmen(aktuelles_datum))

            # Klick-Handler verbinden – Lambda mit Default-Argument!
            btn.clicked.connect(
                lambda checked, d=aktuelles_datum: self.on_tag_geklickt(d)
            )

            grid.addWidget(btn, zeile, spalte)
            zelle += 1

        eltern_layout.addLayout(grid)

    def tag_stil_bestimmen(self, datum):
        # Grundstil für alle Tage
        basis = (
            "border:none; border-radius:10px; font-size:13px; "
            "font-weight:500; min-height:38px; max-height:38px;"
        )

        # Perioden-Tag (rot)
        if datum in self.perioden_tage:
            index = self.perioden_tage.index(datum)
            if index == 0:
                return basis + "background:#E91E63; color:#fff; border-radius:10px 2px 2px 10px;"
            if index == len(self.perioden_tage) - 1:
                return basis + "background:#E91E63; color:#fff; border-radius:2px 10px 10px 2px;"
            return basis + "background:#E91E63; color:#fff; border-radius:2px;"

        # Eisprung-Zone (hellblau)
        if datum in self.eisprung_zone:
            index = self.eisprung_zone.index(datum)
            if index == 0:
                return basis + "background:#E3F2FD; color:#1565C0; border-radius:10px 2px 2px 10px;"
            if index == len(self.eisprung_zone) - 1:
                return basis + "background:#E3F2FD; color:#1565C0; border-radius:2px 10px 10px 2px;"
            return basis + "background:#E3F2FD; color:#1565C0; border-radius:2px;"

        # Heutiger Tag (rosa Rahmen)
        if datum == date.today():
            return basis + "color:#E91E63; font-weight:700; border:2px solid #E91E63;"

        # Zukünftige Tage (ausgegraut)
        if datum > date.today():
            return basis + "color:#CBA8B5;"

        # Vergangene normale Tage
        return basis + "color:#4A0010;"

    # ── Detail-Sheet befüllen ─────────────────────────────────────────────────

    def detail_sheet_befuellen(self, datum):
        # Datum formatieren: "26. Mai"
        monatsnamen = [
            "", "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        datum_text = str(datum.day) + ". " + monatsnamen[datum.month]

        # Zyklustag berechnen
        delta      = (datum - self.zyklus_start).days
        zyklus_tag = (delta % self.zyklus_laenge) + 1

        # Zyklusphase bestimmen
        phase = self.phase_berechnen(zyklus_tag)

        # Labels aktualisieren
        self.main_window.sheetDate.setText("Getrackt am " + datum_text)
        self.main_window.sheetCycleDay.setText("Zyklustag " + str(zyklus_tag))
        self.main_window.sheetPhase.setText(phase)

        print("Sheet: " + datum_text + " – Zyklustag " + str(zyklus_tag) + " – " + phase)

    def phase_berechnen(self, zyklus_tag):
        # Zyklusphase für 28-Tage-Zyklus bestimmen
        if zyklus_tag <= 5:
            return "Menstruation"
        elif zyklus_tag <= 13:
            return "Follikelphase"
        elif zyklus_tag <= 16:
            return "Ovulationsphase"
        elif zyklus_tag <= 22:
            return "Frühe Lutealphase"
        elif zyklus_tag <= 25:
            return "Mittlere Lutealphase"
        else:
            return "Späte Lutealphase"

    # ── Slots ─────────────────────────────────────────────────────────────────

    def on_tag_geklickt(self, datum):
        # Ausgewählten Tag speichern und Sheet aktualisieren
        self.ausgewaehlter_tag = datum
        self.detail_sheet_befuellen(datum)

    def on_tracken(self):
        # TODO: EintragWindow öffnen mit dem ausgewählten Datum
        print("Tracken für: " + str(self.ausgewaehlter_tag))
        QMessageBox.information(
            self,
            "Tracken",
            "Eintrag für " + str(self.ausgewaehlter_tag) + " kommt noch!"
        )

    def on_mehr_erfahren(self):
        # TODO: Infoseite zur aktuellen Phase öffnen
        print("Mehr erfahren geöffnet")
        QMessageBox.information(
            self,
            "Mehr erfahren",
            "Infos zur Zyklusphase kommen noch!"
        )

    def on_zurueck(self):
        # Zurück zum Dashboard
        print("Zurück zum Dashboard")
        self.close()

    # ── Hilfsmethode ─────────────────────────────────────────────────────────

    def zeige_fehler(self, text):
        QMessageBox.warning(self, "Fehler", text)


# ── Programm starten ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KalenderWindow()
    window.show()
    sys.exit(app.exec())
