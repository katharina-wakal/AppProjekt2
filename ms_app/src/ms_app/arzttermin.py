# Arzttermin-Seite zum Eintragen & Verwalten von Arztterminen

import sys  # Systemfunktionen (z. B. Kommandozeilenargumente, Beenden)
import pathlib  # Arbeiten mit Ordner & Dateien
from PyQt6 import uic  # Lädt .ui-Datei
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox  # Qt-Klassen für App, Fenster, Meldungen
from PyQt6.QtCore import QDate, QTime  # Qt-Klassen für Datum & Uhrzeit
from database import arzttermin_speichern  # Speicherfunktion aus Datenbankdatei

# Definiert das ArztterminWindow als Unterklasse von QMainWindow
class ArztterminWindow(QMainWindow):

    def __init__(self, user_id=None):  # Konstruktor: wird aufgerufen, wenn ArztterminWindow erstellt wird

        super().__init__()  # Ruft den Konstruktor der Elternklasse (QMainWindow) auf – immer nötig bei Vererbung
        self.user_id = user_id  # Speichert Benutzer-ID im Objekt

        working_dir = str(pathlib.Path(__file__).parent.resolve())  # Ermittelt Ordner dieser Python-Datei
        self.main_window = uic.loadUi(working_dir + "/arzttermin.ui", self)  # Lädt UI-Datei

        heute = QDate.currentDate()  # Holt das heutige Datum
        self.main_window.datTermin.setDate(heute)  # Setzt das Datumsfeld auf heutige Datum

        self.main_window.timTermin.setTime(QTime(8, 0))  # Setzt die Uhrzeit standardmäßig auf 08:00 Uhr

        self.woche_aktualisieren(heute)  # Füllt den Wochenstreifen mit der aktuellen Woche

        self.main_window.btnClose.clicked.connect(self.on_schliessen)  # Verbindet Schließen-Button mit Funktion
        self.main_window.btnSpeichern.clicked.connect(self.on_speichern)  # Verbindet Speichern-Button mit Funktion

        self.main_window.datTermin.dateChanged.connect(self.on_datum_gewaehlt)  # Reagiert auf Datumsänderung

        self.main_window.btnDay1.clicked.connect(lambda: self.on_tag_gewaehlt(0))  # Montag im Wochenstreifen
        self.main_window.dayToday.clicked.connect(lambda: self.on_tag_gewaehlt(1))  # Dienstag im Wochenstreifen
        self.main_window.btnDay2.clicked.connect(lambda: self.on_tag_gewaehlt(2))  # Mittwoch im Wochenstreifen
        self.main_window.btnDay3.clicked.connect(lambda: self.on_tag_gewaehlt(3))  # Donnerstag im Wochenstreifen
        self.main_window.btnDay4.clicked.connect(lambda: self.on_tag_gewaehlt(4))  # Freitag im Wochenstreifen
        self.main_window.btnDay5.clicked.connect(lambda: self.on_tag_gewaehlt(5))  # Samstag im Wochenstreifen
        self.main_window.btnDay6.clicked.connect(lambda: self.on_tag_gewaehlt(6))  # Sonntag im Wochenstreifen

        self.erinnerungs_chips = [  # Liste mit allen Erinnerungs-Chips
            self.main_window.chipAmTag,  # Chip für Erinnerung am selben Tag
            self.main_window.chip1Tag,  # Chip für Erinnerung 1 Tag vorher
            self.main_window.chip3Tage,  # Chip für Erinnerung 3 Tage vorher
            self.main_window.chip1Woche,  # Chip für Erinnerung 1 Woche vorher
        ]

        for chip in self.erinnerungs_chips:  # Geht jeden Erinnerungs-Chip einzeln durch
            chip.clicked.connect(self.on_erinnerung_gewaehlt)  # Verbindet jeden Chip mit derselben Funktion

        self.main_window.chipFolgeJa.clicked.connect(self.on_folgetermin_ja)  # Verbindet Folgetermin-Ja-Chip
        self.main_window.chipFolgeNein.clicked.connect(self.on_folgetermin_nein)  # Verbindet Folgetermin-Nein-Chip

    def on_schliessen(self):  # Wird ausgeführt, wenn das Fenster geschlossen werden soll
        from dashboard import DashboardWindow  # Importiert Dashboard hier, um Import-Probleme zu vermeiden

        self.dashboard = DashboardWindow(  # Erstellt ein neues Dashboard-Fenster
            user_id=self.user_id  # Übergibt die aktuelle Benutzer-ID
        )

        self.dashboard.show()  # Zeigt das Dashboard an
        self.close()  # Schließt das aktuelle Arzttermin-Fenster


    def on_speichern(self):  # Ausgeführt, wenn Speichern-Button gedrückt
        arzt_name = self.main_window.txtArztName.text().strip()  # Liest den Arztnamen aus & entfernt Leerzeichen
        arzt_typ = self.main_window.cmbArztTyp.currentText()  # Liest ausgewählte Fachrichtung aus
        ort = self.main_window.txtOrt.text().strip()  # Liest Ort aus & entfernt Leerzeichen
        datum = self.main_window.datTermin.date().toString("dd.MM.yyyy")  # Liest Datum als Text aus
        uhrzeit = self.main_window.timTermin.time().toString("HH:mm")  # Liest Uhrzeit als Text aus
        notiz = self.main_window.txtNotiz.toPlainText().strip()  # Liest Notiz aus
        vorbereitung = self.main_window.txtVorbereitung.toPlainText().strip()  # Liest Vorbereitung aus
        befund = self.main_window.txtBefund.toPlainText().strip()  # Liest dBefund aus

        if not arzt_name:  # Prüft, ob kein Arztname eingegeben wurde
            self.zeige_fehler("Bitte den Namen des Arztes / der Ärztin eingeben.")  # Zeigt Fehlermeldung
            return  # Bricht Funktion ab

        if arzt_typ == "🩺  Bitte wählen …":  # Prüft, ob keine Fachrichtung gewählt wurde
            self.zeige_fehler("Bitte eine Fachrichtung auswählen.")  # Zeigt Fehlermeldung
            return  # Bricht Funktion ab

        if self.user_id is None:  # Prüft, ob kein Benutzer angemeldet ist
            self.zeige_fehler("Kein Benutzer angemeldet.")  # Zeigt Fehlermeldung
            return  # Bricht Funktion ab

        erinnerung = ""  # Standardwert: keine Erinnerung ausgewählt

        if self.main_window.chipAmTag.isChecked():  # Prüft, ob Erinnerung am selben Tag gewählt wurde
            erinnerung = "Am selben Tag"  # Speichert die Auswahl als Text
        elif self.main_window.chip1Tag.isChecked():  # Prüft, ob 1 Tag vorher gewählt wurde
            erinnerung = "1 Tag vorher"  # Speichert die Auswahl als Text
        elif self.main_window.chip3Tage.isChecked():  # Prüft, ob 3 Tage vorher gewählt wurde
            erinnerung = "3 Tage vorher"  # Speichert die Auswahl als Text
        elif self.main_window.chip1Woche.isChecked():  # Prüft, ob 1 Woche vorher gewählt wurde
            erinnerung = "1 Woche vorher"  # Speichert die Auswahl als Text

        folgetermin = 0  # Standardwert: kein Folgetermin

        if self.main_window.chipFolgeJa.isChecked():  # Prüft, ob Folgetermin Ja gewählt wurde
            folgetermin = 1  # Speichert Ja als 1
        elif self.main_window.chipFolgeNein.isChecked():  # Prüft, ob Folgetermin Nein gewählt wurde
            folgetermin = 0  # Speichert Nein als 0

        arzttermin_speichern(  # Ruft die Datenbankfunktion zum Speichern auf
            self.user_id,  # Benutzer-ID
            arzt_name,  # Name des Arztes / der Ärztin
            arzt_typ,  # Fachrichtung
            ort,  # Ort der Praxis
            datum,  # Datum des Termins
            uhrzeit,  # Uhrzeit des Termins
            erinnerung,  # Erinnerungsauswahl
            notiz,  # Notizen zum Termin
            vorbereitung,  # Vorbereitung für den Termin
            befund,  # Befund / Ergebnis
            folgetermin  # Information, ob ein Folgetermin nötig ist
        )

        print("Arzttermin wurde in der Datenbank gespeichert.")  # Gibt Bestätigung in der Konsole aus

        QMessageBox.information(  # Zeigt eine Erfolgsmeldung im Fenster
            self,  # Elternfenster der Meldung
            "Gespeichert",  # Titel der Meldung
            "Termin wurde erfolgreich eingetragen! 🩺"  # Text der Meldung
        )

    def on_datum_gewaehlt(self, neues_datum):  # Wird ausgeführt, wenn ein neues Datum gewählt wird
        self.woche_aktualisieren(neues_datum)  # Aktualisiert den Wochenstreifen passend zum Datum

    def on_tag_gewaehlt(self, offset):  # Wird ausgeführt, wenn ein Button im Wochenstreifen geklickt wird
        montag = self.woche_start_berechnen(self.main_window.datTermin.date())  # Berechnet Montag der aktuellen Woche
        gewaehlt = montag.addDays(offset)  # Berechnet den gewünschten Tag über den Offset
        self.main_window.datTermin.setDate(gewaehlt)  # Setzt das Datum im Datumsfeld

    def on_erinnerung_gewaehlt(self):  # Wird ausgeführt, wenn ein Erinnerungs-Chip geklickt wird
        geklickt = self.sender()  # Ermittelt, welcher Chip geklickt wurde

        for chip in self.erinnerungs_chips:  # Geht alle Erinnerungs-Chips durch
            if chip is not geklickt:  # Prüft, ob es nicht der angeklickte Chip ist
                chip.setChecked(False)  # Deaktiviert alle anderen Chips

        print("Erinnerung gesetzt: " + geklickt.text())  # Gibt die gewählte Erinnerung in der Konsole aus

    def on_folgetermin_ja(self):  # Wird ausgeführt, wenn Folgetermin Ja geklickt wird
        self.main_window.chipFolgeNein.setChecked(False)  # Deaktiviert den Nein-Chip
        print("Folgetermin: Ja")  # Gibt Auswahl in der Konsole aus

    def on_folgetermin_nein(self):  # Wird ausgeführt, wenn Folgetermin Nein geklickt wird
        self.main_window.chipFolgeJa.setChecked(False)  # Deaktiviert den Ja-Chip
        print("Folgetermin: Nein")  # Gibt Auswahl in der Konsole aus

    def woche_start_berechnen(self, datum):  # Berechnet den Wochenanfang zu einem Datum
        tage_seit_montag = datum.dayOfWeek() - 1  # Berechnet Anzahl Tage seit Montag
        return datum.addDays(-tage_seit_montag)  # Gibt den Montag der Woche zurück

    def woche_aktualisieren(self, datum):  # Aktualisiert die sichtbare Wochenleiste
        montag = self.woche_start_berechnen(datum)  # Berechnet den Montag der Woche

        tages_buttons = [  # Liste der sieben Tages-Buttons
            self.main_window.btnDay1,  # Montag
            self.main_window.dayToday,  # Dienstag
            self.main_window.btnDay2,  # Mittwoch
            self.main_window.btnDay3,  # Donnerstag
            self.main_window.btnDay4,  # Freitag
            self.main_window.btnDay5,  # Samstag
            self.main_window.btnDay6,  # Sonntag
        ]

        for i in range(7):  # Schleife läuft für 7 Tage
            tag = montag.addDays(i)  # Berechnet den jeweiligen Tag
            tages_buttons[i].setText(str(tag.day()))  # Setzt die Tageszahl auf den passenden Button

        print("Woche angezeigt ab: " + montag.toString("dd.MM.yyyy"))  # Gibt Wochenstart in der Konsole aus

    def zeige_fehler(self, text):  # Hilfsfunktion für Fehlermeldungen
        QMessageBox.warning(self, "Fehler", text)  # Zeigt eine Warnmeldung an


if __name__ == "__main__":  # Prüft, ob diese Datei direkt gestartet wird
    app = QApplication(sys.argv)  # Erstellt die Qt-Anwendung
    window = ArztterminWindow()  # Erstellt das Arzttermin-Fenster
    window.show()  # Zeigt das Fenster an
    sys.exit(app.exec())  # Startet die App-Schleife und beendet das Programm sauber