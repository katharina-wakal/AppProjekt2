# Kalender-Seite – Monatsübersicht mit Zyklus-Markierungen

import sys
import pathlib
from datetime import date, timedelta
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QGridLayout, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from database import perioden_tage_laden, eintrag_fuer_tag_laden, arzttermine_laden, arzttermin_fuer_tag_laden
from datetime import datetime



class KalenderWindow(QMainWindow):

    def __init__(self, user_id=None):

        super().__init__()
        self.user_id = user_id

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/kalender.ui", self)

        self.perioden_tage = []
        self.arzttermin_tage = []  # Liste mit Daten gespeicherter Arzttermine

        if self.user_id is not None:

            perioden_daten = perioden_tage_laden(self.user_id)

            for datum_text in perioden_daten:
                datum = datetime.strptime(
                    datum_text,
                    "%Y-%m-%d"
                ).date()

                self.perioden_tage.append(datum)

            # Arzttermine aus der Datenbank laden
            # Das Datum ist im Format 'dd.MM.yyyy' gespeichert (siehe arzttermin.py)
            termin_daten = arzttermine_laden(self.user_id)

            for datum_text in termin_daten:
                try:
                    datum = datetime.strptime(datum_text, "%d.%m.%Y").date()
                    self.arzttermin_tage.append(datum)  # Datum zur Liste hinzufügen
                except ValueError:
                    pass  # Ungültiges Datumsformat wird übersprungen

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
        # Mehrere Monate anzeigen: 6 Monate zurück bis 6 Monate voraus
        heute = date.today()
        start_monat = heute.replace(day=1)

        # 6 Monate zurückgehen
        for i in range(6):
            start_monat = (start_monat - timedelta(days=1)).replace(day=1)

        aktueller_monat = start_monat

        for i in range(13):
            self.monat_hinzufuegen(
                haupt_layout,
                aktueller_monat.year,
                aktueller_monat.month
            )

            aktueller_monat = (
                    aktueller_monat.replace(day=28) + timedelta(days=4)
            ).replace(day=1)

        haupt_layout.addStretch()
        self.main_window.calContents.setLayout(haupt_layout)

        # Nach dem Aufbau automatisch zum aktuellen Monat scrollen
        # Nach dem Anzeigen automatisch ungefähr zum aktuellen Monat scrollen
        QTimer.singleShot(100, self.zum_aktuellen_monat_scrollen)

    def zum_aktuellen_monat_scrollen(self):
        scrollbar = self.main_window.calScrollArea.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum() // 2)

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

        # Arzttermin-Tag (lila)
        if datum in self.arzttermin_tage:
            return basis + "background:#7B1FA2; color:#fff; border-radius:10px;"

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

        # ── Tagesdaten laden ─────────────────────────────

        if self.user_id is not None:

            # Prüfen ob ein Arzttermin für diesen Tag gespeichert ist
            # Das Datum wird ins Format 'dd.MM.yyyy' umgewandelt, so wie es gespeichert wird
            datum_arzt = datum.strftime("%d.%m.%Y")
            termin = arzttermin_fuer_tag_laden(self.user_id, datum_arzt)

            if termin is not None:

                # Arzttermin-Felder mit lesbaren Labels zusammenstellen
                arzt_labels = [
                    ("🩺 Arzt / Ärztin", termin[0]),
                    ("🏥 Fachrichtung", termin[1]),
                    ("📍 Ort", termin[2]),
                    ("🕐 Uhrzeit", termin[3]),
                    ("🔔 Erinnerung", termin[4]),
                    ("📝 Notiz", termin[5]),
                    ("📋 Vorbereitung", termin[6]),
                    ("🔬 Befund", termin[7]),
                    ("🔁 Folgetermin", "Ja" if termin[8] == 1 else None),
                ]

                text = ""

                for name, wert in arzt_labels:
                    if wert:
                        text += name + ": " + wert + "\n"

                if text:
                    self.main_window.sheetEmpty.setText(text.strip())
                else:
                    self.main_window.sheetEmpty.setText("Keine Arzttermin-Details vorhanden")

            else:

                eintrag = eintrag_fuer_tag_laden(
                    self.user_id,
                    datum.strftime("%Y-%m-%d")
                )

                if eintrag is not None:

                    labels = [
                        ("🩸 Periode", eintrag[0]),
                        ("🔴 Schmierblutung", eintrag[1]),
                        ("💭 Gefühle", eintrag[2]),
                        ("🤕 Schmerzen", eintrag[3]),
                        ("❤️ Sexleben", eintrag[4]),
                        ("📝 Notiz", eintrag[5]),
                        ("💧 Ausfluss", eintrag[6]),
                        ("✨ Haut", eintrag[7]),
                        ("🍽 Verdauung", eintrag[8]),
                        ("🚽 Stuhlgang", eintrag[9]),
                        ("🧪 Tests", eintrag[10]),
                        ("💊 Pille", eintrag[11]),
                        ("🔵 Spirale", eintrag[12]),
                        ("💉 Spritze", eintrag[13]),
                        ("🌱 Implantat", eintrag[14]),
                        ("🩹 Pflaster", eintrag[15]),
                        ("⭕ Ring", eintrag[16]),
                    ]

                    text = ""

                    for name, wert in labels:
                        if wert:
                            text += name + ": " + wert + "\n"

                    if text:
                        self.main_window.sheetEmpty.setText(text.strip())
                    else:
                        self.main_window.sheetEmpty.setText("Keine getrackten Erfahrungen")

                else:
                    self.main_window.sheetEmpty.setText("Keine getrackten Erfahrungen")

        else:
            self.main_window.sheetEmpty.setText("Keine getrackten Erfahrungen")





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

        from dashboard import DashboardWindow

        self.dashboard = DashboardWindow(
            user_id=self.user_id
        )

        self.dashboard.show()
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
