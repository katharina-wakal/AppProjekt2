# settings.py
# Einstellungsseite der FemHealth-Anwendung.
#
# Dieses Modul stellt das Fenster für die Accountverwaltung,
# App-Einstellungen, Datenschutzfunktionen und Datenexporte bereit.
#
# Das Einstellungsfenster wird über den Settings-Button
# des Dashboards geöffnet

# sys wird am Ende der Datei benötigt, wenn die Einstellungsseite
# unabhängig vom restlichen Projekt direkt getestet wird.
import sys
# pathlib wird verwendet, um den Pfad zur settings.ui-Datei
# unabhängig vom verwendeten Betriebssystem zu bestimmen.
import pathlib
# webbrowser öffnet Internetseiten und E-Mail-Links
# im Standardbrowser beziehungsweise Standard-Mailprogramm.
import webbrowser
# re stellt reguläre Ausdrücke bereit.
# Hier wird es zur Prüfung des Formats einer E-Mail-Adresse verwendet.
import re
# hashlib stellt Hashfunktionen bereit.
# Im Code wird SHA-256 verwendet, um aus einem Passwort
# einen nicht direkt umkehrbaren Hashwert zu erzeugen.
import hashlib
# csv wird verwendet, um die Trackingdaten
# als CSV-Datei zu exportieren.
import csv
# json wird verwendet, um eine vollständige Kopie
# der Nutzerdaten als JSON-Datei zu speichern.
import json
# uic ermöglicht das Laden einer mit Qt Designer
# erstellten .ui-Datei.
from PyQt6 import uic
# pyqtSignal wird für das eigene Logout-Signal benötigt.
# Qt enthält verschiedene PyQt-Aufzählungen und Einstellungen.
# QTimer ermöglicht einen zeitlich verzögerten Methodenaufruf.
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
# QApplication verwaltet die PyQt-Anwendung beim direkten Teststart.
# QMainWindow ist die Elternklasse des Einstellungsfensters.
# QMessageBox zeigt Informations-, Warn- und Bestätigungsdialoge an.
# QInputDialog ermöglicht einfache Texteingaben.
# QLineEdit stellt ein einzeiliges Eingabefeld bereit.
# QDialog wird für den selbst erstellten Passwortdialog verwendet.
# QFormLayout ordnet Beschriftungen und Eingabefelder zeilenweise an.
# QVBoxLayout ordnet Elemente senkrecht untereinander an.
# QPushButton stellt einen anklickbaren Button bereit.
# QWidget wird bei der Größenberechnung des Scrollbereichs benötigt.
# QFileDialog öffnet einen Dialog zur Auswahl eines Speicherorts.
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QInputDialog, QLineEdit,
                             QDialog, QFormLayout, QVBoxLayout, QPushButton, QWidget, QFileDialog)
# Die benötigten Datenbankfunktionen werden
# aus dem Modul database importiert.
# user_email_laden Lädt die E-Mail-Adresse eines Nutzers aus der Datenbank.
# email_existiert prüft, ob eine bestimmte E-Mail-Adresse bereits in der Datenbank vorhanden ist.
#email_aendern Ändert die gespeicherte E-Mail-Adresse eines Nutzers.
#passwort_pruefen Prüft, ob das eingegebene Passwort mit dem gespeicherten Passwort übereinstimmt.
#passwort_aendern Speichert ein neues Passwort für den Nutzer.
#account_loeschen Löscht den Account und die dazugehörigen Nutzerdaten.
#tracking_daten_laden Lädt die gespeicherten Trackingdaten eines Nutzers.
#alle_nutzerdaten_laden Lädt alle gespeicherten Daten eines Nutzers, beispielsweise für einen Datenexport.
from database import (user_email_laden,email_existiert,email_aendern, passwort_pruefen, passwort_aendern,
                      account_loeschen, tracking_daten_laden, alle_nutzerdaten_laden)

# Eigene Klasse für das Einstellungsfenster.
# Die Klasse erbt von QMainWindow und besitzt dadurch
# alle Eigenschaften und Methoden eines PyQt-Hauptfensters.
class SettingsWindow(QMainWindow):
    # Eigenes Signal, das beim Abmelden oder nach dem Löschen
    # eines Accounts ausgesendet wird.
    #
    # Das übergeordnete Fenster kann dieses Signal empfangen
    # und anschließend wieder das Loginfenster anzeigen.
    logout_requested = pyqtSignal()

    def __init__(self, user_id=None,s_show_main_page=None):
        """
                Erstellt und konfiguriert das Einstellungsfenster.

                Args:
                    user_id:
                        ID des aktuell angemeldeten Nutzers.

                    s_show_main_page:
                        Optional übergebene Funktion für die Rückkehr
                        zur Hauptseite. Sie wird im aktuellen Code
                        gespeichert, aber noch nicht verwendet.
                """
        # Konstruktor der Elternklasse QMainWindow aufrufen.
        super().__init__()

        # Das Fensterobjekt beim Schließen vollständig löschen.
        #
        # Ohne dieses Attribut könnte das Fenster nur ausgeblendet
        # werden und weiterhin im Speicher vorhanden bleiben.
        self.setAttribute(
            Qt.WidgetAttribute.WA_DeleteOnClose,
            True
        )
        # ID des angemeldeten Nutzers speichern.
        # Die ID wird für alle nutzerbezogenen Datenbankzugriffe benötigt.
        self.user_id = user_id
        # Optional übergebene Funktion speichern.
        # Sie wird im aktuellen Stand noch nicht aufgerufen.
        self.s_show_main_page = s_show_main_page

        # Den absoluten Pfad des Ordners bestimmen,
        # in dem sich diese Python-Datei befindet.
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        # Die mit Qt Designer erstellte settings.ui-Datei laden.
        #
        # self wird als zweites Argument übergeben, damit die UI-Elemente
        # Teil des aktuellen SettingsWindow-Objekts werden.
        self.main_window = uic.loadUi(
            working_dir + "/settings.ui",
            self
        )

        # Verhindern, dass das Inhaltswidget des Scrollbereichs
        # automatisch auf die Größe des sichtbaren Bereichs angepasst wird.
        #
        # Die benötigte Höhe wird später manuell
        # in scrollbereich_anpassen() festgelegt.
        self.main_window.scrollArea.setWidgetResizable(False)

        # Die vertikale Scrollleiste nur anzeigen,
        # wenn der Inhalt höher als der sichtbare Bereich ist.
        self.main_window.scrollArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Die horizontale Scrollleiste immer ausblenden.
        self.main_window.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # scrollbereich_anpassen() beim nächsten Durchlauf
        # der PyQt-Ereignisschleife aufrufen.
        #
        # Die Verzögerung von 0 Millisekunden sorgt dafür,
        # dass die UI zunächst vollständig aufgebaut und vermessen wird.
        QTimer.singleShot(0, self.scrollbereich_anpassen)

        # Die in der UI vorhandenen Passwortfelder so einstellen,
        # dass eingegebene Zeichen nicht als Klartext angezeigt werden.
        self.main_window.txtPwAlt.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        # Auch das erste Feld für das neue Passwort verdeckt anzeigen.
        self.main_window.txtPwNeu.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        # Auch die Wiederholung des neuen Passworts verdeckt anzeigen.
        self.main_window.txtPwNeu2.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        # Speichern, dass die Passwortfelder zunächst nicht geöffnet sind.
        #
        # Dieses Attribut wird im aktuellen Code nur gesetzt,
        # später aber nicht mehr ausgewertet.
        self.pw_offen = False
        # Die Passwortfelder aus der UI und den dortigen
        # Speichern-Button zu Beginn ausblenden.
        #
        # Das Passwort wird stattdessen über einen
        # separat erzeugten Dialog geändert.
        self.passwort_felder_verstecken()

        # ── Buttons verbinden ──────────────────────────────────────────────

        # Einen Klick auf den Zurück-Button mit der Methode on_zurueck verbinden.
        self.main_window.btnBack.clicked.connect(self.on_zurueck)

        # ── Account ───────────────────────────────────────────────────────
        #Buttons mit Funktionen verbinden
        self.main_window.btnEmailAendern.clicked.connect(self.on_email_aendern)
        self.main_window.btnPasswortAendern.clicked.connect(self.on_passwort_dialog)
        self.main_window.btnEmailVerify.clicked.connect(self.on_email_verify)
        self.main_window.btnAbmelden.clicked.connect(self.on_abmelden)
        self.main_window.btnLoeschen.clicked.connect(self.on_account_loeschen)

        # ── App-Einstellungen ─────────────────────────────────────────────
        # Für noch nicht umgesetzte Bereiche wird jeweils
        # eine allgemeine Platzhaltermeldung geöffnet.
        #
        # lambda ermöglicht es, der Methode on_platzhalter
        # den jeweiligen Namen der Einstellung zu übergeben.
        self.main_window.btnTracking.clicked.connect(
            lambda: self.on_platzhalter("Tracking personalisieren")
        )
        self.main_window.btnZyklus.clicked.connect(
            lambda: self.on_platzhalter("Zyklus personalisieren")
        )
        self.main_window.btnErinnerungen.clicked.connect(
            lambda: self.on_platzhalter("Erinnerungen & Benachrichtigungen")
        )
        self.main_window.btnSprache.clicked.connect(
            lambda: self.on_platzhalter("Sprache")
        )
        self.main_window.btnDesignmodus.clicked.connect(
            lambda: self.on_platzhalter("Designmodus")
        )
        self.main_window.btnEinheiten.clicked.connect(
            lambda: self.on_platzhalter("Einheiten")
        )

        # ── Toggle-Switches ───────────────────────────────────────────────
        #Änderung an den Schaltern an die zugehörige Methode senden
        self.main_window.toggleFaceID.stateChanged.connect(self.on_toggle_face_id)
        self.main_window.toggleWidget.stateChanged.connect(self.on_toggle_widget)
        self.main_window.toggleSperre.stateChanged.connect(self.on_toggle_sperre)

        # ── Datenschutz & Daten ───────────────────────────────────────────
        # weitere Buttons verbinden
        self.main_window.btnDatenDownload.clicked.connect(self.on_daten_download)
        self.main_window.btnDatenExport.clicked.connect(self.on_daten_export)
        self.main_window.btnDatenschutz.clicked.connect(
            lambda: self.on_platzhalter("Datenschutzeinstellungen")
        )
        self.main_window.btnEinwilligungen.clicked.connect(
            lambda: self.on_platzhalter("Einwilligungen verwalten")
        )
        self.main_window.btnDatenLoeschen.clicked.connect(self.on_daten_loeschen)

        # ── Rechtliches & Support ─────────────────────────────────────────
        self.main_window.btnDatenschutzLink.clicked.connect(
            # TODO: Ersetze URL durch eure echte Datenschutz-Seite
            lambda: webbrowser.open("https://www.example.com/datenschutz")
        )
        self.main_window.btnImpressum.clicked.connect(
            # TODO: Ersetze URL durch euer echtes Impressum
            lambda: webbrowser.open("https://www.example.com/impressum")
        )
        self.main_window.btnNutzungsbedingungen.clicked.connect(
            # TODO: Ersetze URL durch eure echten Nutzungsbedingungen
            lambda: webbrowser.open("https://www.example.com/nutzungsbedingungen")
        )
        self.main_window.btnHilfe.clicked.connect(
            lambda: self.on_platzhalter("Hilfe & Support")
        )
        self.main_window.btnFeedback.clicked.connect(self.on_feedback)

    # ── Passwort-Felder ein-/ausklappen ────────────────────────────────────

    def passwort_felder_verstecken(self):
        """
                Blendet die in der settings.ui vorhandenen Passwortfelder aus.

                Die Passwortänderung wird aktuell nicht direkt über diese Felder,
                sondern über den separaten Dialog in on_passwort_dialog() ausgeführt.
                """
        # Alle auszublendenden Widgets in einer Liste zusammenfassen.
        for widget in [
            self.main_window.txtPwAlt,
            self.main_window.txtPwNeu,
            self.main_window.txtPwNeu2,
            self.main_window.btnPwSpeichern,
        ]:
            # Das aktuelle Widget unsichtbar machen.
            widget.setVisible(False)
            # Die maximale Höhe auf 0 setzen,
            # damit es im Layout keinen sichtbaren Platz belegt.
            widget.setMaximumHeight(0)

    def on_passwort_dialog(self):
        """
                Öffnet einen Dialog zum Ändern des Passworts.

                Das bisherige Passwort wird geprüft, bevor der neue
                Passwort-Hash in der Datenbank gespeichert wird.
                """
        # Ohne Nutzer-ID kann kein Passwort geändert werden.
        if self.user_id is None:
            self.zeige_fehler(
                "Der angemeldete Benutzer konnte nicht ermittelt werden."
            )
            return
        # Einen neuen Dialog erstellen.
        # self wird als Elternfenster übergeben.
        dialog = QDialog(self)
        # Titel des Dialogfensters festlegen.
        dialog.setWindowTitle("Passwort ändern")
        # Mindestbreite des Dialogs festlegen.
        dialog.setMinimumWidth(380)

        # Hauptlayout erstellen, das alle Elemente
        # senkrecht untereinander anordnet.
        haupt_layout = QVBoxLayout(dialog)
        # Formularlayout für Beschriftungen und Eingabefelder erstellen.
        formular = QFormLayout()

        # Eingabefeld für das aktuelle Passwort erstellen.
        txt_alt = QLineEdit()
        # Hinweistext im leeren Eingabefeld anzeigen.
        txt_alt.setPlaceholderText("Aktuelles Passwort")
        # Das eingegebene Passwort verdeckt anzeigen.
        txt_alt.setEchoMode(QLineEdit.EchoMode.Password)

        # Eingabefeld für das neue Passwort erstellen.
        txt_neu = QLineEdit()
        # Hinweistext für das neue Passwort festlegen.
        txt_neu.setPlaceholderText("Neues Passwort")
        # Auch das neue Passwort verdeckt anzeigen.
        txt_neu.setEchoMode(QLineEdit.EchoMode.Password)

        # Eingabefeld für die Wiederholung
        # des neuen Passworts erstellen.
        txt_neu2 = QLineEdit()
        # Hinweistext für die Passwortwiederholung festlegen.
        txt_neu2.setPlaceholderText("Neues Passwort wiederholen")
        # Die Passwortwiederholung verdeckt anzeigen.
        txt_neu2.setEchoMode(QLineEdit.EchoMode.Password)

        # Das Feld für das aktuelle Passwort
        # mit seiner Beschriftung zum Formular hinzufügen.
        formular.addRow("Aktuelles Passwort:", txt_alt)
        # Das Feld für das neue Passwort hinzufügen.
        formular.addRow("Neues Passwort:", txt_neu)
        # Das Feld für die Passwortwiederholung hinzufügen.
        formular.addRow("Passwort wiederholen:", txt_neu2)

        # Das fertige Formular zum Hauptlayout hinzufügen.
        haupt_layout.addLayout(formular)

        # Button zum Speichern des neuen Passworts erstellen.
        btn_speichern = QPushButton("Passwort speichern")
        # Button zum Abbrechen des Dialogs erstellen.
        btn_abbrechen = QPushButton("Abbrechen")

        # Speichern-Button zum Hauptlayout hinzufügen.
        haupt_layout.addWidget(btn_speichern)
        # Abbrechen-Button zum Hauptlayout hinzufügen.
        haupt_layout.addWidget(btn_abbrechen)

        # Beim Klick auf „Abbrechen“ den Dialog ablehnen
        # und ohne Änderung schließen.
        btn_abbrechen.clicked.connect(dialog.reject)

        def passwort_speichern():
            """
                        Prüft die Eingaben und speichert das neue Passwort.

                        Diese innere Funktion kann direkt auf die Eingabefelder
                        und den umgebenden Dialog zugreifen.
                        """
            alt = txt_alt.text()  # Aktuelles Passwort auslesen.
            neu = txt_neu.text() # Neues Passwort auslesen.
            neu2 = txt_neu2.text() # Wiederholung des neuen Passworts auslesen.

            # Prüfen, ob mindestens eines der Felder leer ist.
            if not alt or not neu or not neu2:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Bitte alle Passwortfelder ausfüllen."
                )
                return

            # Prüfen, ob beide Eingaben des neuen Passworts
            # exakt übereinstimmen.
            if neu != neu2:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Die neuen Passwörter stimmen nicht überein."
                )
                return

            # Prüfen, ob das neue Passwort
            # die festgelegte Mindestlänge erfüllt.
            if len(neu) < 6:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Das neue Passwort muss mindestens 6 Zeichen haben."
                )
                return

            # Verhindern, dass das bisherige Passwort
            # erneut als neues Passwort gespeichert wird.
            if alt == neu:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Das neue Passwort muss sich vom bisherigen Passwort unterscheiden."
                )
                return

            # Das aktuelle Klartextpasswort in Bytes umwandeln,
            # mit SHA-256 hashen und als Hexadezimaltext speichern.
            alter_passwort_hash = hashlib.sha256(
                alt.encode()
            ).hexdigest()

            # Prüfen, ob der erzeugte Hash mit dem
            # in der Datenbank gespeicherten Hash übereinstimmt.
            if not passwort_pruefen(
                    self.user_id,
                    alter_passwort_hash
            ):
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Das bisherige Passwort ist nicht korrekt."
                )
                return

            # Auch für das neue Passwort einen SHA-256-Hash erzeugen.
            neuer_passwort_hash = hashlib.sha256(
                neu.encode()
            ).hexdigest()

            # Den neuen Passwort-Hash in der Datenbank speichern.
            erfolgreich = passwort_aendern(
                self.user_id,
                neuer_passwort_hash
            )

            # Prüfen, ob die Datenbankänderung fehlgeschlagen ist.
            if not erfolgreich:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Das Passwort konnte nicht geändert werden."
                )
                return

            # Den Nutzer über die erfolgreiche Änderung informieren.
            QMessageBox.information(
                dialog,
                "Passwort geändert",
                "Dein Passwort wurde erfolgreich geändert."
            )

            dialog.accept() # Den Dialog erfolgreich beenden und schließen.

        # Beim Klick auf den Speichern-Button
        # die innere Prüffunktion aufrufen.
        btn_speichern.clicked.connect(passwort_speichern)

        # Den Dialog modal öffnen.
        #
        # Modal bedeutet, dass zunächst dieser Dialog geschlossen
        # werden muss, bevor das Einstellungsfenster weiter bedient wird.
        dialog.exec()

    # ── Account-Slots ──────────────────────────────────────────────────────

    def on_zurueck(self):
        """
                Schließt das Einstellungsfenster.
                """
        # Das aktuelle Einstellungsfenster schließen.
        self.close()

    def on_email_aendern(self):
        """
                Prüft und ändert die E-Mail-Adresse des aktuellen Nutzers.
                """
        # Ohne Nutzer-ID können keine Accountdaten geändert werden.
        if self.user_id is None:
            self.zeige_fehler(
                "Der angemeldete Benutzer konnte nicht ermittelt werden."
            )
            return

        # Die aktuell gespeicherte E-Mail-Adresse
        # aus der Datenbank laden.
        aktuelle_email = user_email_laden(self.user_id)

        # Einen Eingabedialog für die neue E-Mail-Adresse öffnen.
        #
        # Die aktuelle Adresse wird bereits als Ausgangswert eingetragen.
        neue_email, bestaetigt = QInputDialog.getText(
            self,
            "E-Mail ändern",
            "Bitte gib deine neue E-Mail-Adresse ein:",
            text=aktuelle_email
        )

        # Die Methode beenden, wenn der Dialog abgebrochen wurde.
        if not bestaetigt:
            return

        # Leerzeichen am Anfang und Ende entfernen
        # und die Adresse in Kleinbuchstaben umwandeln.
        neue_email = neue_email.strip().lower()

        # Prüfen, ob nach der Bereinigung noch eine Eingabe vorhanden ist.
        if not neue_email:
            self.zeige_fehler("Bitte gib eine E-Mail-Adresse ein.")
            return

        # Regulärer Ausdruck für eine einfache Prüfung
        # des grundlegenden E-Mail-Formats.
        email_muster = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        # Prüfen, ob die vollständige Eingabe
        # dem festgelegten Muster entspricht.
        if re.fullmatch(email_muster, neue_email) is None:
            self.zeige_fehler(
                "Bitte gib eine gültige E-Mail-Adresse ein."
            )
            return

        # Prüfen, ob die neue E-Mail-Adresse
        # mit der bisher gespeicherten Adresse übereinstimmt.
        if neue_email == aktuelle_email.lower():
            QMessageBox.information(
                self,
                "Keine Änderung",
                "Diese E-Mail-Adresse ist bereits in deinem Account gespeichert."
            )
            return

        # Prüfen, ob die Adresse bereits von einem
        # anderen Nutzerkonto verwendet wird.
        if email_existiert(neue_email, self.user_id):
            self.zeige_fehler(
                "Diese E-Mail-Adresse wird bereits von einem anderen Account verwendet."
            )
            return

        # Zur Vermeidung von Tippfehlern einen zweiten
        # Eingabedialog zur Bestätigung öffnen.
        email_wiederholung, bestaetigt = QInputDialog.getText(
            self,
            "E-Mail bestätigen",
            "Bitte gib die neue E-Mail-Adresse erneut ein:"
        )

        # Die Methode beenden, wenn auch dieser Dialog
        # abgebrochen wurde.
        if not bestaetigt:
            return

        # Auch die wiederholte Eingabe bereinigen.
        email_wiederholung = email_wiederholung.strip().lower()

        # Prüfen, ob beide E-Mail-Eingaben übereinstimmen.
        if neue_email != email_wiederholung:
            self.zeige_fehler(
                "Die beiden E-Mail-Adressen stimmen nicht überein."
            )
            return

        # Eine abschließende Bestätigungsfrage anzeigen.
        antwort = QMessageBox.question(
            self,
            "E-Mail ändern",
            "Möchtest du deine E-Mail-Adresse wirklich ändern?\n\n"
            f"Alt: {aktuelle_email}\n"
            f"Neu: {neue_email}",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        # Nur fortfahren, wenn ausdrücklich „Ja“ ausgewählt wurde.
        if antwort != QMessageBox.StandardButton.Yes:
            return

        # Die neue E-Mail-Adresse in der Datenbank speichern.
        erfolgreich = email_aendern(
            self.user_id,
            neue_email
        )

        # Bei erfolgreicher Änderung eine Bestätigung anzeigen.
        if erfolgreich:
            QMessageBox.information(
                self,
                "E-Mail geändert",
                "Deine E-Mail-Adresse wurde erfolgreich geändert.\n\n"
                "Bitte bestätige anschließend deine neue E-Mail-Adresse."
            )
        # Bei einem Datenbankfehler eine Fehlermeldung anzeigen.
        else:
            self.zeige_fehler(
                "Die E-Mail-Adresse konnte nicht geändert werden."
            )

    def on_email_verify(self):
        """
                Zeigt momentan nur eine Beispielmeldung zur Verifizierung an.

                Ein tatsächlicher Versand einer Bestätigungs-E-Mail
                ist im aktuellen Code noch nicht umgesetzt.
                """
        # Informationsmeldung anzeigen.
        #
        # Diese Meldung bestätigt aktuell keinen echten E-Mail-Versand.
        QMessageBox.information(
            self,
            "E-Mail bestätigen",
            "Eine Bestätigungs-E-Mail wurde an deine Adresse gesendet."
        )

    def on_abmelden(self):
        """
                Fragt nach einer Bestätigung und meldet den Nutzer ab.
                """
        # Sicherheitsfrage anzeigen, bevor die Sitzung beendet wird.
        antwort = QMessageBox.question(
            self,
            "Abmelden",
            "Möchtest du dich wirklich abmelden?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        # Bei „Nein“ oder Schließen des Dialogs
        # keine Abmeldung durchführen.
        if antwort != QMessageBox.StandardButton.Yes:
            return

        # Konsolenausgabe für Test- und Entwicklungszwecke.
        print("Nutzer abgemeldet")

        # Das Logout-Signal aussenden.
        #
        # Das verbundene übergeordnete Fenster kann daraufhin
        # wieder das Loginfenster öffnen.
        self.logout_requested.emit()

        # Das Einstellungsfenster schließen.
        self.close()

        # Dieser zweite Aufruf von self.close() ist im aktuellen Code
        # redundant, weil das Fenster bereits geschlossen wurde.
        self.close()

    def on_account_loeschen(self):
        """
                Löscht den Account nach zwei Bestätigungen
                und einer erfolgreichen Passwortprüfung.
                """
        # Ohne Nutzer-ID kann kein Account gelöscht werden.
        if self.user_id is None:
            self.zeige_fehler(
                "Der angemeldete Benutzer konnte nicht ermittelt werden."
            )
            return

        # Erste ausführliche Warnung anzeigen.
        antwort = QMessageBox.warning(
            self,
            "Account dauerhaft löschen",
            "Achtung!\n\n"
            "Dein Account und alle damit verbundenen Daten werden "
            "unwiderruflich gelöscht.\n\n"
            "Dazu gehören unter anderem:\n"
            "• deine Accountdaten\n"
            "• alle Tracking-Einträge\n"
            "• Arzttermine\n"
            "• App-Einstellungen\n\n"
            "Möchtest du wirklich fortfahren?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        # Die Methode beenden, wenn der Nutzer
        # die erste Warnung nicht bestätigt.
        if antwort != QMessageBox.StandardButton.Yes:
            return

        # Das aktuelle Passwort zur Identitätsbestätigung abfragen.
        passwort, bestaetigt = QInputDialog.getText(
            self,
            "Löschen bestätigen",
            "Bitte gib zur Bestätigung dein aktuelles Passwort ein:",
            QLineEdit.EchoMode.Password
        )
        # Bei Abbruch des Eingabedialogs nichts löschen.
        if not bestaetigt:
            return

        # Prüfen, ob überhaupt ein Passwort eingegeben wurde.
        if not passwort:
            self.zeige_fehler(
                "Bitte gib dein aktuelles Passwort ein."
            )
            return

        # Aus dem eingegebenen Passwort
        # einen SHA-256-Hash erzeugen.
        passwort_hash = hashlib.sha256(
            passwort.encode()
        ).hexdigest()

        # Den erzeugten Hash mit dem gespeicherten Hash vergleichen.
        if not passwort_pruefen(
                self.user_id,
                passwort_hash
        ):
            self.zeige_fehler(
                "Das eingegebene Passwort ist nicht korrekt."
            )
            return

        # Nach erfolgreicher Passwortprüfung
        # eine letzte Sicherheitsabfrage anzeigen.
        letzte_bestaetigung = QMessageBox.question(
            self,
            "Endgültig löschen",
            "Dies ist die letzte Bestätigung.\n\n"
            "Der Account kann nach dem Löschen nicht wiederhergestellt werden.\n\n"
            "Account jetzt endgültig löschen?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        # Nur bei einer eindeutigen Bestätigung fortfahren.
        if letzte_bestaetigung != QMessageBox.StandardButton.Yes:
            return

        # Den Account und die zugehörigen Daten
        # über die Datenbankfunktion löschen.
        erfolgreich = account_loeschen(
            self.user_id
        )

        # Bei einem Fehler eine Meldung anzeigen
        # und die Methode beenden.
        if not erfolgreich:
            self.zeige_fehler(
                "Der Account konnte nicht gelöscht werden."
            )
            return

        # Erfolgreiche Löschung bestätigen.
        QMessageBox.information(
            self,
            "Account gelöscht",
            "Dein Account und alle zugehörigen Daten wurden gelöscht."
        )

        # Wie beim Abmelden das Logout-Signal aussenden,
        # damit wieder das Loginfenster angezeigt werden kann.
        self.logout_requested.emit()
        # Das Einstellungsfenster schließen.
        self.close()

    # ── Toggle-Funktionen ─────────────────────────────────────────────────

    def on_toggle_face_id(self, zustand):
        """
                Reagiert auf eine Änderung des Face-ID-Schalters.

                Die Einstellung wird aktuell nur in der Konsole ausgegeben
                und noch nicht in der Datenbank gespeichert.
                """
        # Der Wert 2 steht bei einer Checkbox für „aktiviert“.
        # Der Wert 0 steht für „deaktiviert“.
        aktiv = zustand == 2
        # Aktuellen Zustand für Testzwecke ausgeben.
        print("Face ID: " + str(aktiv))
        # Die dauerhafte Speicherung ist noch nicht umgesetzt.

    def on_toggle_widget(self, zustand):
        """
                Reagiert auf den Datenschutzschalter für Widgets.

                Die Einstellung wird momentan noch nicht dauerhaft gespeichert.
                """
        # Den übergebenen Checkbox-Zustand
        # in einen booleschen Wert umwandeln.
        aktiv = zustand == 2
        # Aktuellen Wert in der Konsole ausgeben.
        print("Daten in Widgets ausblenden: " + str(aktiv))
        # Die dauerhafte Speicherung ist noch nicht umgesetzt.

    def on_toggle_sperre(self, zustand):
        """
                Reagiert auf eine Änderung der App-Sperre.

                Die Einstellung wird aktuell nur ausgegeben
                und noch nicht in der Datenbank gespeichert.
                """
        # Den Checkbox-Zustand in True oder False umwandeln.
        aktiv = zustand == 2
        # Zustand für Testzwecke in der Konsole anzeigen.
        print("App-Sperre: " + str(aktiv))
        # Die dauerhafte Speicherung ist noch nicht umgesetzt.

    # ── Datenschutz-Slots ──────────────────────────────────────────────────

    def on_daten_download(self):
        """
                Speichert eine vollständige Kopie der Nutzerdaten als JSON-Datei.
                """
        # Ohne Nutzer-ID können keine Nutzerdaten geladen werden.
        if self.user_id is None:
            self.zeige_fehler(
                "Der angemeldete Benutzer konnte nicht ermittelt werden."
            )
            return

        # Alle verfügbaren Daten des Nutzers
        # aus der Datenbank laden.
        daten = alle_nutzerdaten_laden(self.user_id)

        # Prüfen, ob das Laden der Daten fehlgeschlagen ist.
        if daten is None:
            self.zeige_fehler(
                "Die gespeicherten Nutzerdaten konnten nicht geladen werden."
            )
            return

        # Einen Dialog zur Auswahl des Speicherorts öffnen.
        #
        # getSaveFileName gibt den gewählten Dateipfad
        # und den ausgewählten Dateifilter zurück.
        dateipfad, ausgewaehlter_filter = QFileDialog.getSaveFileName(
            self,
            "Vollständige Datenkopie speichern",
            "FemHealth_Datenkopie.json",
            "JSON-Dateien (*.json)"
        )

        # Die Methode beenden, wenn kein Speicherort gewählt wurde.
        if not dateipfad:
            return

        # Die Dateiendung ergänzen, falls sie nicht
        # bereits vom Nutzer angegeben wurde.
        if not dateipfad.lower().endswith(".json"):
            dateipfad += ".json"

        try:
            # Die Zieldatei im Schreibmodus öffnen.
            #
            # UTF-8 ermöglicht die korrekte Speicherung
            # von Umlauten und anderen Sonderzeichen.
            with open(
                    dateipfad,
                    mode="w",
                    encoding="utf-8"
            ) as json_datei:

                # Die geladenen Daten in die JSON-Datei schreiben.
                json.dump(
                    daten,
                    json_datei,
                    # Deutsche Sonderzeichen direkt speichern
                    # und nicht als Unicode-Ersatzfolgen ausgeben.
                    ensure_ascii=False,
                    # Die Datei mit Einrückungen lesbar formatieren.
                    indent=4
                )

            # Erfolgreiches Speichern bestätigen.
            QMessageBox.information(
                self,
                "Download erfolgreich",
                "Deine vollständige Datenkopie wurde erfolgreich gespeichert."
            )

        # Fehler beim Öffnen oder Schreiben der Datei abfangen.
        except OSError as fehler:
            # Technische Fehlermeldung in der Konsole ausgeben.
            print("Fehler beim Speichern der Datenkopie:", fehler)

            # Verständliche Fehlermeldung im Fenster anzeigen.
            self.zeige_fehler(
                "Die Datenkopie konnte nicht gespeichert werden."
            )


    def on_daten_export(self):
        """
                Exportiert die gespeicherten Trackingdaten als CSV-Datei.
                """
        # Ohne Nutzer-ID können keine Trackingdaten geladen werden.
        if self.user_id is None:
            self.zeige_fehler(
                "Der angemeldete Benutzer konnte nicht ermittelt werden."
            )
            return

        # Alle Trackingdaten des aktuellen Nutzers laden.
        daten = tracking_daten_laden(self.user_id)

        # Prüfen, ob überhaupt Daten zum Export vorhanden sind.
        if len(daten) == 0:
            QMessageBox.information(
                self,
                "Keine Trackingdaten",
                "Es sind noch keine Trackingdaten zum Exportieren vorhanden."
            )
            return

        # Einen Dialog zur Auswahl des Speicherorts öffnen.
        dateipfad, ausgewaehlter_filter = QFileDialog.getSaveFileName(
            self,
            "Trackingdaten exportieren",
            "FemHealth_Trackingdaten.csv",
            "CSV-Dateien (*.csv)"
        )

        # Die Methode beenden, wenn der Speicherdialog abgebrochen wurde.
        if not dateipfad:
            return

        # Die CSV-Dateiendung automatisch ergänzen, wenn sie noch nicht vorhanden ist.
        if not dateipfad.lower().endswith(".csv"):
            dateipfad += ".csv"

        # Überschriften für die einzelnen Spalten der exportierten CSV-Datei festlegen.
        spaltennamen = [
            "Datum",
            "Periodenstärke",
            "Schmierblutung",
            "Gefühle",
            "Schmerzen",
            "Sexualleben",
            "Notiz",
            "Ausfluss",
            "Haut",
            "Verdauung",
            "Stuhlgang",
            "Tests",
            "Pille",
            "Spirale",
            "Spritze",
            "Implantat",
            "Pflaster",
            "Ring"
        ]

        try:
            # Die CSV-Datei im Schreibmodus öffnen.
            #
            # newline="" verhindert zusätzliche Leerzeilen.
            #
            # utf-8-sig schreibt eine UTF-8-Datei mit BOM,
            # wodurch Umlaute beispielsweise in Excel
            # häufiger korrekt erkannt werden.
            with open(
                    dateipfad,
                    mode="w",
                    newline="",
                    encoding="utf-8-sig"
            ) as csv_datei:
                # CSV-Schreibobjekt erstellen.
                #
                # Als Trennzeichen wird ein Semikolon verwendet,
                # was im deutschen Excel-Umfeld üblich ist.

                writer = csv.writer(
                    csv_datei,
                    delimiter=";"
                )
                # Die Überschriften als erste Zeile schreiben.
                writer.writerow(spaltennamen)

                # Alle geladenen Datenzeilen nacheinander durchlaufen.
                for zeile in daten:
                    # Für jeden Wert der aktuellen Zeile prüfen,
                    # ob er den Wert None enthält.
                    #
                    # None-Werte werden durch leere Texte ersetzt,
                    # damit in der CSV-Datei leere Felder entstehen.
                    bereinigte_zeile = [
                        wert if wert is not None else ""
                        for wert in zeile
                    ]

                    # Die bereinigte Datenzeile in die CSV-Datei schreiben.
                    writer.writerow(bereinigte_zeile)

            # Erfolgreichen Export bestätigen.
            QMessageBox.information(
                self,
                "Export erfolgreich",
                "Deine Trackingdaten wurden erfolgreich exportiert."
            )

        # Fehler beim Erstellen oder Schreiben der Datei abfangen.
        except OSError as fehler:
            # Technische Fehlermeldung in der Konsole ausgeben.
            print("Fehler beim Exportieren:", fehler)
            # Verständliche Fehlermeldung anzeigen.
            self.zeige_fehler(
                "Die Datei konnte nicht gespeichert werden."
            )

    def on_daten_loeschen(self):
        """
                Fragt nach einer Bestätigung zum Löschen der Trackingdaten.

                Wichtig:
                Die tatsächliche Datenbanklöschung ist im aktuellen Code
                noch nicht umgesetzt.
                """
        # Sicherheitsfrage anzeigen.
        antwort = QMessageBox.question(
            self,
            "Tracking-Daten löschen",
            "Alle Tracking-Einträge werden unwiderruflich gelöscht.\n"
            "Fortfahren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        # Nur bei einer Bestätigung fortfahren.
        if antwort == QMessageBox.StandardButton.Yes:
            # TODO: Daten aus Datenbank löschen
            # Konsolenausgabe für Testzwecke.
            print("Tracking-Daten gelöscht")
            # Die folgende Erfolgsmeldung wird bereits angezeigt,
            # obwohl die Daten im aktuellen Stand noch nicht gelöscht werden.
            QMessageBox.information(
                self, "Gelöscht", "Alle Tracking-Daten wurden gelöscht."
            )

    def on_feedback(self):
        """
                Öffnet das Standard-Mailprogramm für eine Feedback-E-Mail.
                """
        # Einen mailto-Link mit bereits eingetragenem Betreff öffnen.
        #
        # Die Supportadresse sollte vor der Veröffentlichung
        # auf ihre Gültigkeit geprüft werden.
        webbrowser.open("mailto:support@femhealth.app?subject=Feedback")

    # ── Platzhalter ────────────────────────────────────────────────────────

    def on_platzhalter(self, name):
        """
                Zeigt eine allgemeine Meldung für noch nicht
                fertiggestellte Einstellungsbereiche an.

                Args:
                    name:
                        Name des Einstellungsbereichs,
                        der in der Meldung angezeigt wird.
                """
        # Informationsdialog mit dem übergebenen Namen anzeigen.
        QMessageBox.information(
            self,
            name,
            name + " – hier erscheint der zugehörige Dialog.\n(TODO)"
        )

    # ── Hilfsmethode ───────────────────────────────────────────────────────

    def zeige_fehler(self, text):
        """
                Zeigt eine einheitliche Fehlermeldung an.

                Args:
                    text:
                        Text, der im Warnfenster angezeigt werden soll.
                """
        # Warnfenster mit dem einheitlichen Titel „Fehler“ öffnen.
        QMessageBox.warning(self, "Fehler", text)

    def scrollbereich_anpassen(self):
        """
                Passt die Größe des Inhaltswidgets an die sichtbaren Elemente an.

                Dadurch kann die vertikale Scrollleiste korrekt erkennen,
                wie hoch der gesamte Inhalt des Einstellungsfensters ist.
                """
        # Das Inhaltswidget des Scrollbereichs abrufen.
        inhalt = self.main_window.scrollArea.widget()

        # Startwert für die bisher tiefste gefundene Position eines Elements.
        unterste_position = 0

        # Alle direkten untergeordneten Widgets
        # des Scroll-Inhalts durchlaufen.
        #
        # FindDirectChildrenOnly verhindert, dass zusätzlich
        # tiefer verschachtelte Widgets zurückgegeben werden.
        for widget in inhalt.findChildren(
                QWidget,
                options=Qt.FindChildOption.FindDirectChildrenOnly
        ):
            # Nur sichtbare Widgets für die Höhenberechnung verwenden.
            if widget.isVisible():
                # Die Unterkante des Widgets aus seiner y-Position und seiner Höhe berechnen.
                unterkante = widget.y() + widget.height()
                # Den bisher größten Wert beibehalten.
                unterste_position = max(
                    unterste_position,
                    unterkante
                )

        # Unterhalb des letzten sichtbaren Elements zusätzlich 40 Pixel Abstand einplanen.
        neue_hoehe = unterste_position + 40

        # Die aktuelle Breite des sichtbaren
        # Scrollbereichs bestimmen.
        viewport_breite = (
            self.main_window.scrollArea.viewport().width()
        )

        # Die Mindestgröße des Inhaltswidgets festlegen.
        #
        # Dadurch wird verhindert, dass der Inhalt kleiner
        # als die berechnete Höhe dargestellt wird.
        inhalt.setMinimumSize(
            viewport_breite,
            neue_hoehe
        )

        # Das Inhaltswidget unmittelbar auf die berechnete Größe setzen.
        inhalt.resize(
            viewport_breite,
            neue_hoehe
        )

# ── Direkter Teststart ────────────────────────────────────────────────────

# Dieser Abschnitt wird nur ausgeführt, wenn settings.py
# direkt gestartet wird.
#
# Wird SettingsWindow aus einem anderen Modul importiert,
# wird dieser Abschnitt nicht ausgeführt.

if __name__ == "__main__":
    # Eine neue PyQt-Anwendung erstellen.
    app = QApplication(sys.argv)
    # Ein Einstellungsfenster ohne eingeloggten Nutzer
    # für einen direkten Oberflächentest erstellen.
    window = SettingsWindow()
    # Das Fenster sichtbar machen.
    window.show()
    # Die PyQt-Ereignisschleife starten und den Python-Prozess
    # nach dem Schließen der Anwendung mit dem Rückgabewert beenden.
    sys.exit(app.exec())
