# Arzttermin-Seite zum Eintragen und Verwalten von Arztterminen

import sys
import pathlib
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QDate, QTime
from database import arzttermin_speichern


class ArztterminWindow(QMainWindow):

    def __init__(self, user_id=None):

        super().__init__()
        self.user_id = user_id

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/arzttermin.ui", self)

        # Datum auf heute setzen beim Öffnen
        heute = QDate.currentDate()
        self.main_window.datTermin.setDate(heute)

        # Uhrzeit auf 08:00 setzen als Standardwert
        self.main_window.timTermin.setTime(QTime(8, 0))

        # Wochenstreifen beim Start befüllen
        self.woche_aktualisieren(heute)

        # ── Buttons mit Funktionen verbinden ──────────────────────────────────

        self.main_window.btnClose.clicked.connect(self.on_schliessen)
        self.main_window.btnSpeichern.clicked.connect(self.on_speichern)

        # Datum-Auswahl: Wochenstreifen springt zum gewählten Datum
        self.main_window.datTermin.dateChanged.connect(self.on_datum_gewaehlt)

        # Tages-Buttons im Wochenstreifen
        self.main_window.btnDay1.clicked.connect(lambda: self.on_tag_gewaehlt(0))
        self.main_window.dayToday.clicked.connect(lambda: self.on_tag_gewaehlt(1))
        self.main_window.btnDay2.clicked.connect(lambda: self.on_tag_gewaehlt(2))
        self.main_window.btnDay3.clicked.connect(lambda: self.on_tag_gewaehlt(3))
        self.main_window.btnDay4.clicked.connect(lambda: self.on_tag_gewaehlt(4))
        self.main_window.btnDay5.clicked.connect(lambda: self.on_tag_gewaehlt(5))
        self.main_window.btnDay6.clicked.connect(lambda: self.on_tag_gewaehlt(6))

        # Erinnerungs-Chips: nur einen gleichzeitig auswählen
        self.erinnerungs_chips = [
            self.main_window.chipAmTag,
            self.main_window.chip1Tag,
            self.main_window.chip3Tage,
            self.main_window.chip1Woche,
        ]
        for chip in self.erinnerungs_chips:
            chip.clicked.connect(self.on_erinnerung_gewaehlt)

        # Folgetermin-Chips
        self.main_window.chipFolgeJa.clicked.connect(self.on_folgetermin_ja)
        self.main_window.chipFolgeNein.clicked.connect(self.on_folgetermin_nein)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def on_schliessen(self):
        from dashboard import DashboardWindow

        self.dashboard = DashboardWindow(
            user_id=self.user_id
        )

        self.dashboard.show()
        self.close()

    def on_speichern(self):
        # Alle Eingaben auslesen
        arzt_name    = self.main_window.txtArztName.text().strip()
        arzt_typ     = self.main_window.cmbArztTyp.currentText()
        ort          = self.main_window.txtOrt.text().strip()
        datum        = self.main_window.datTermin.date().toString("dd.MM.yyyy")
        uhrzeit      = self.main_window.timTermin.time().toString("HH:mm")
        notiz        = self.main_window.txtNotiz.toPlainText().strip()
        vorbereitung = self.main_window.txtVorbereitung.toPlainText().strip()
        befund       = self.main_window.txtBefund.toPlainText().strip()

        # Pflichtfelder prüfen
        if not arzt_name:
            self.zeige_fehler("Bitte den Namen des Arztes / der Ärztin eingeben.")
            return

        if arzt_typ == "🩺  Bitte wählen …":
            self.zeige_fehler("Bitte eine Fachrichtung auswählen.")
            return

        if self.user_id is None:
            self.zeige_fehler("Kein Benutzer angemeldet.")
            return

        erinnerung = ""

        if self.main_window.chipAmTag.isChecked():
            erinnerung = "Am selben Tag"
        elif self.main_window.chip1Tag.isChecked():
            erinnerung = "1 Tag vorher"
        elif self.main_window.chip3Tage.isChecked():
            erinnerung = "3 Tage vorher"
        elif self.main_window.chip1Woche.isChecked():
            erinnerung = "1 Woche vorher"

        folgetermin = 0

        if self.main_window.chipFolgeJa.isChecked():
            folgetermin = 1
        elif self.main_window.chipFolgeNein.isChecked():
            folgetermin = 0

        arzttermin_speichern(
            self.user_id,
            arzt_name,
            arzt_typ,
            ort,
            datum,
            uhrzeit,
            erinnerung,
            notiz,
            vorbereitung,
            befund,
            folgetermin
        )

        print("Arzttermin wurde in der Datenbank gespeichert.")

        QMessageBox.information(self, "Gespeichert", "Termin wurde erfolgreich eingetragen! 🩺")


    def on_datum_gewaehlt(self, neues_datum):
        # Wird aufgerufen wenn das Datum im QDateEdit geändert wird
        # Wochenstreifen springt automatisch zum neuen Datum
        self.woche_aktualisieren(neues_datum)

    def on_tag_gewaehlt(self, offset):
        # Wird aufgerufen wenn ein Tages-Button im Wochenstreifen gedrückt wird
        # offset = Position des Tages in der Woche (0 = Mo, 1 = Di, …, 6 = So)
        montag = self.woche_start_berechnen(self.main_window.datTermin.date())
        gewaehlt = montag.addDays(offset)

        # Datum im DateEdit setzen – löst on_datum_gewaehlt aus
        self.main_window.datTermin.setDate(gewaehlt)

    def on_erinnerung_gewaehlt(self):
        # Stellt sicher dass immer nur ein Erinnerungs-Chip ausgewählt ist
        geklickt = self.sender()
        for chip in self.erinnerungs_chips:
            if chip is not geklickt:
                chip.setChecked(False)

        # TODO: Erinnerung planen
        print("Erinnerung gesetzt: " + geklickt.text())

    def on_folgetermin_ja(self):
        # Folgetermin "Ja" → "Nein"-Chip deaktivieren
        self.main_window.chipFolgeNein.setChecked(False)
        print("Folgetermin: Ja")

    def on_folgetermin_nein(self):
        # Folgetermin "Nein" → "Ja"-Chip deaktivieren
        self.main_window.chipFolgeJa.setChecked(False)
        print("Folgetermin: Nein")

    # ── Hilfsmethoden ─────────────────────────────────────────────────────────

    def woche_start_berechnen(self, datum):
        # Gibt den Montag der Woche zurück in der das Datum liegt
        # dayOfWeek(): Montag = 1, Dienstag = 2, ..., Sonntag = 7
        tage_seit_montag = datum.dayOfWeek() - 1
        return datum.addDays(-tage_seit_montag)

    def woche_aktualisieren(self, datum):
        # Aktualisiert die 7 Tages-Buttons im Wochenstreifen
        montag = self.woche_start_berechnen(datum)

        # Liste der Tages-Buttons in Reihenfolge Mo–So
        tages_buttons = [
            self.main_window.btnDay1,
            self.main_window.dayToday,
            self.main_window.btnDay2,
            self.main_window.btnDay3,
            self.main_window.btnDay4,
            self.main_window.btnDay5,
            self.main_window.btnDay6,
        ]

        for i in range(7):
            tag = montag.addDays(i)
            tages_buttons[i].setText(str(tag.day()))

        print("Woche angezeigt ab: " + montag.toString("dd.MM.yyyy"))

    def zeige_fehler(self, text):
        QMessageBox.warning(self, "Fehler", text)


# ── Programm starten ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArztterminWindow()
    window.show()
    sys.exit(app.exec())
