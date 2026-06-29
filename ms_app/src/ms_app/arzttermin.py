# Arzttermin-Seite zum Eintragen & Verwalten von Arztterminen

import sys  # Systemfunktionen (z. B. Kommandozeilenargumente, Beenden)
import pathlib  # Arbeiten mit Ordner & Dateien
from PyQt6 import uic  # Lädt .ui-Datei
# QApplication verwaltet die PyQt-Anwendung beim direkten Teststart.
# QMainWindow ist die Elternklasse des Arztterminfensters.
from PyQt6.QtWidgets import QApplication, QMainWindow

# Das MessageMixin stellt einheitliche Methoden
# für Fehler- und Informationsmeldungen bereit.
from message_mixin import MessageMixin
from PyQt6.QtCore import QDate, QTime  # Qt-Klassen für Datum & Uhrzeit
from database import arzttermin_speichern  # Speicherfunktion aus Datenbankdatei

# ArztterminWindow erbt gleichzeitig von zwei Klassen:
#
# QMainWindow stellt die Funktionen eines PyQt-Hauptfensters bereit.
# MessageMixin ergänzt das Fenster um einheitliche Meldungsmethoden.
#
# Da von zwei Elternklassen geerbt wird,
# handelt es sich um Mehrfachvererbung.
class ArztterminWindow(QMainWindow, MessageMixin):

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

    def on_schliessen(self):  # ausgeführt, wenn Fenster geschlossen werden soll
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
        notiz = self.main_window.txtNotiz.toPlainText().strip()  # Liest das kombinierte Notizfeld aus

        if not arzt_name:  # Prüft, ob kein Arztname eingegeben wurde
            self.zeige_fehler("Bitte den Namen des Arztes / der Ärztin eingeben.")  # Zeigt Fehlermeldung
            return  # Bricht Funktion ab

        if arzt_typ == "🩺  Bitte wählen …":  # Prüft, ob keine Fachrichtung gewählt wurde
            self.zeige_fehler("Bitte eine Fachrichtung auswählen.")  # Zeigt Fehlermeldung
            return  # Bricht Funktion ab

        if self.user_id is None:  # Prüft, ob kein Benutzer angemeldet ist
            self.zeige_fehler("Kein Benutzer angemeldet.")  # Zeigt Fehlermeldung
            return  # Bricht Funktion ab

        arzttermin_speichern(  # Ruft die Datenbankfunktion zum Speichern auf
            self.user_id,  # Benutzer-ID
            arzt_name,  # Name des Arztes / der Ärztin
            arzt_typ,  # Fachrichtung
            ort,  # Ort der Praxis
            datum,  # Datum des Termins
            uhrzeit,  # Uhrzeit des Termins
            notiz  # Kombinierte Notizen zum Termin
        )

        print("Arzttermin wurde in der Datenbank gespeichert.")  # Gibt Bestätigung in der Konsole aus

        # Über die geerbte Methode des MessageMixins
        # wird der erfolgreiche Speichervorgang bestätigt.
        self.zeige_information(
            "Gespeichert",
            "Termin wurde erfolgreich eingetragen! 🩺"
        )

    def on_datum_gewaehlt(self, neues_datum):  # Wird ausgeführt, wenn ein neues Datum gewählt wird
        self.woche_aktualisieren(neues_datum)  # Aktualisiert den Wochenstreifen passend zum Datum

    def on_tag_gewaehlt(self, offset):  # Wird ausgeführt, wenn ein Button im Wochenstreifen geklickt wird
        montag = self.woche_start_berechnen(self.main_window.datTermin.date())  # Berechnet Montag der aktuellen Woche
        gewaehlt = montag.addDays(offset)  # Berechnet den gewünschten Tag über den Offset
        self.main_window.datTermin.setDate(gewaehlt)  # Setzt das Datum im Datumsfeld

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


if __name__ == "__main__":  # Prüft, ob diese Datei direkt gestartet wird
    app = QApplication(sys.argv)  # Erstellt die Qt-Anwendung
    window = ArztterminWindow()  # Erstellt das Arzttermin-Fenster
    window.show()  # Zeigt das Fenster an
    sys.exit(app.exec())  # Startet die App-Schleife und beendet das Programm sauber
