# Einstellungen-Seite – FemHealth
# Wird vom Dashboard über btnSettings geöffnet

import sys
import pathlib
import webbrowser
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QInputDialog, QLineEdit,
                             QDialog, QFormLayout, QVBoxLayout, QPushButton)
import re
from database import (user_email_laden,email_existiert,email_aendern, passwort_pruefen, passwort_aendern,
                      account_loeschen)
import hashlib

class SettingsWindow(QMainWindow):

    logout_requested = pyqtSignal()

    def __init__(self, user_id=None,s_show_main_page=None):
        super().__init__()
        self.user_id = user_id
        self.s_show_main_page = s_show_main_page

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(
            working_dir + "/settings.ui", self
        )

        #Passwort-Eingabe als Punkte anzeigen
        self.main_window.txtPwAlt.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.main_window.txtPwNeu.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.main_window.txtPwNeu2.setEchoMode(
            QLineEdit.EchoMode.Password
        )


        # Passwort-Felder zu Beginn versteckt
        self.pw_offen = False
        self.passwort_felder_verstecken()

        # ── Buttons verbinden ──────────────────────────────────────────────

        # Zurück-Button
        self.main_window.btnBack.clicked.connect(self.on_zurueck)

        # ── Account ───────────────────────────────────────────────────────
        self.main_window.btnEmailAendern.clicked.connect(self.on_email_aendern)
        self.main_window.btnPasswortAendern.clicked.connect(self.on_passwort_dialog)
        self.main_window.btnEmailVerify.clicked.connect(self.on_email_verify)
        self.main_window.btnAbmelden.clicked.connect(self.on_abmelden)
        self.main_window.btnLoeschen.clicked.connect(self.on_account_loeschen)

        # ── App-Einstellungen ─────────────────────────────────────────────
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

        # Toggle-Switches
        self.main_window.toggleFaceID.stateChanged.connect(self.on_toggle_face_id)
        self.main_window.toggleWidget.stateChanged.connect(self.on_toggle_widget)
        self.main_window.toggleSperre.stateChanged.connect(self.on_toggle_sperre)

        # ── Datenschutz & Daten ───────────────────────────────────────────
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
        # Alle drei Felder und den Speichern-Button ausblenden
        for widget in [
            self.main_window.txtPwAlt,
            self.main_window.txtPwNeu,
            self.main_window.txtPwNeu2,
            self.main_window.btnPwSpeichern,
        ]:
            widget.setVisible(False)
            widget.setMaximumHeight(0)

    def on_passwort_dialog(self):
        if self.user_id is None:
            self.zeige_fehler(
                "Der angemeldete Benutzer konnte nicht ermittelt werden."
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Passwort ändern")
        dialog.setMinimumWidth(380)

        haupt_layout = QVBoxLayout(dialog)
        formular = QFormLayout()

        txt_alt = QLineEdit()
        txt_alt.setPlaceholderText("Aktuelles Passwort")
        txt_alt.setEchoMode(QLineEdit.EchoMode.Password)

        txt_neu = QLineEdit()
        txt_neu.setPlaceholderText("Neues Passwort")
        txt_neu.setEchoMode(QLineEdit.EchoMode.Password)

        txt_neu2 = QLineEdit()
        txt_neu2.setPlaceholderText("Neues Passwort wiederholen")
        txt_neu2.setEchoMode(QLineEdit.EchoMode.Password)

        formular.addRow("Aktuelles Passwort:", txt_alt)
        formular.addRow("Neues Passwort:", txt_neu)
        formular.addRow("Passwort wiederholen:", txt_neu2)

        haupt_layout.addLayout(formular)

        btn_speichern = QPushButton("Passwort speichern")
        btn_abbrechen = QPushButton("Abbrechen")

        haupt_layout.addWidget(btn_speichern)
        haupt_layout.addWidget(btn_abbrechen)

        btn_abbrechen.clicked.connect(dialog.reject)

        def passwort_speichern():
            alt = txt_alt.text()
            neu = txt_neu.text()
            neu2 = txt_neu2.text()

            if not alt or not neu or not neu2:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Bitte alle Passwortfelder ausfüllen."
                )
                return

            if neu != neu2:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Die neuen Passwörter stimmen nicht überein."
                )
                return

            if len(neu) < 6:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Das neue Passwort muss mindestens 6 Zeichen haben."
                )
                return

            if alt == neu:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Das neue Passwort muss sich vom bisherigen Passwort unterscheiden."
                )
                return

            alter_passwort_hash = hashlib.sha256(
                alt.encode()
            ).hexdigest()

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

            neuer_passwort_hash = hashlib.sha256(
                neu.encode()
            ).hexdigest()

            erfolgreich = passwort_aendern(
                self.user_id,
                neuer_passwort_hash
            )

            if not erfolgreich:
                QMessageBox.warning(
                    dialog,
                    "Fehler",
                    "Das Passwort konnte nicht geändert werden."
                )
                return

            QMessageBox.information(
                dialog,
                "Passwort geändert",
                "Dein Passwort wurde erfolgreich geändert."
            )

            dialog.accept()

        btn_speichern.clicked.connect(passwort_speichern)

        dialog.exec()

    # ── Account-Slots ──────────────────────────────────────────────────────

    def on_zurueck(self):
        self.close()

    def on_email_aendern(self):
        if self.user_id is None:
            self.zeige_fehler(
                "Der angemeldete Benutzer konnte nicht ermittelt werden."
            )
            return

        aktuelle_email = user_email_laden(self.user_id)

        neue_email, bestaetigt = QInputDialog.getText(
            self,
            "E-Mail ändern",
            "Bitte gib deine neue E-Mail-Adresse ein:",
            text=aktuelle_email
        )

        if not bestaetigt:
            return

        neue_email = neue_email.strip().lower()

        if not neue_email:
            self.zeige_fehler("Bitte gib eine E-Mail-Adresse ein.")
            return

        # Einfache Prüfung des E-Mail-Formats
        email_muster = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if re.fullmatch(email_muster, neue_email) is None:
            self.zeige_fehler(
                "Bitte gib eine gültige E-Mail-Adresse ein."
            )
            return

        if neue_email == aktuelle_email.lower():
            QMessageBox.information(
                self,
                "Keine Änderung",
                "Diese E-Mail-Adresse ist bereits in deinem Account gespeichert."
            )
            return

        if email_existiert(neue_email, self.user_id):
            self.zeige_fehler(
                "Diese E-Mail-Adresse wird bereits von einem anderen Account verwendet."
            )
            return

        email_wiederholung, bestaetigt = QInputDialog.getText(
            self,
            "E-Mail bestätigen",
            "Bitte gib die neue E-Mail-Adresse erneut ein:"
        )

        if not bestaetigt:
            return

        email_wiederholung = email_wiederholung.strip().lower()

        if neue_email != email_wiederholung:
            self.zeige_fehler(
                "Die beiden E-Mail-Adressen stimmen nicht überein."
            )
            return

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

        if antwort != QMessageBox.StandardButton.Yes:
            return

        erfolgreich = email_aendern(
            self.user_id,
            neue_email
        )

        if erfolgreich:
            QMessageBox.information(
                self,
                "E-Mail geändert",
                "Deine E-Mail-Adresse wurde erfolgreich geändert.\n\n"
                "Bitte bestätige anschließend deine neue E-Mail-Adresse."
            )
        else:
            self.zeige_fehler(
                "Die E-Mail-Adresse konnte nicht geändert werden."
            )

    def on_email_verify(self):
        # TODO: Verifizierungs-E-Mail versenden
        QMessageBox.information(
            self,
            "E-Mail bestätigen",
            "Eine Bestätigungs-E-Mail wurde an deine Adresse gesendet."
        )

    def on_abmelden(self):
        antwort = QMessageBox.question(
            self,
            "Abmelden",
            "Möchtest du dich wirklich abmelden?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if antwort != QMessageBox.StandardButton.Yes:
            return

        print("Nutzer abgemeldet")

        # Dem Dashboard mitteilen, dass zum Login gewechselt werden soll
        self.logout_requested.emit()

        # Einstellungsfenster schließen
        self.close()
            #TODO: zur Loginseite zurück

        #Einstellungsfenster schließen
        self.close()

    def on_account_loeschen(self):
        if self.user_id is None:
            self.zeige_fehler(
                "Der angemeldete Benutzer konnte nicht ermittelt werden."
            )
            return

        # Erste Warnung
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

        if antwort != QMessageBox.StandardButton.Yes:
            return

        # Passwort zur Bestätigung abfragen
        passwort, bestaetigt = QInputDialog.getText(
            self,
            "Löschen bestätigen",
            "Bitte gib zur Bestätigung dein aktuelles Passwort ein:",
            QLineEdit.EchoMode.Password
        )

        if not bestaetigt:
            return

        if not passwort:
            self.zeige_fehler(
                "Bitte gib dein aktuelles Passwort ein."
            )
            return

        passwort_hash = hashlib.sha256(
            passwort.encode()
        ).hexdigest()

        if not passwort_pruefen(
                self.user_id,
                passwort_hash
        ):
            self.zeige_fehler(
                "Das eingegebene Passwort ist nicht korrekt."
            )
            return

        # Letzte Sicherheitsabfrage
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

        if letzte_bestaetigung != QMessageBox.StandardButton.Yes:
            return

        erfolgreich = account_loeschen(
            self.user_id
        )

        if not erfolgreich:
            self.zeige_fehler(
                "Der Account konnte nicht gelöscht werden."
            )
            return

        QMessageBox.information(
            self,
            "Account gelöscht",
            "Dein Account und alle zugehörigen Daten wurden gelöscht."
        )

        # Dieselbe Fenstersteuerung wie beim Abmelden verwenden
        self.logout_requested.emit()
        self.close()

    # ── Toggle-Slots ───────────────────────────────────────────────────────

    def on_toggle_face_id(self, zustand):
        # zustand: 2 = aktiviert, 0 = deaktiviert
        aktiv = zustand == 2
        print("Face ID: " + str(aktiv))
        # TODO: Einstellung in Datenbank speichern

    def on_toggle_widget(self, zustand):
        aktiv = zustand == 2
        print("Daten in Widgets ausblenden: " + str(aktiv))
        # TODO: Einstellung in Datenbank speichern

    def on_toggle_sperre(self, zustand):
        aktiv = zustand == 2
        print("App-Sperre: " + str(aktiv))
        # TODO: Einstellung in Datenbank speichern

    # ── Datenschutz-Slots ──────────────────────────────────────────────────

    def on_daten_download(self):
        # TODO: Daten-Export als JSON/CSV starten
        QMessageBox.information(
            self,
            "Daten herunterladen",
            "Deine Daten werden vorbereitet.\n"
            "Du erhältst eine E-Mail mit dem Download-Link."
        )

    def on_daten_export(self):
        # TODO: Export-Dialog öffnen (z. B. als CSV oder PDF)
        QMessageBox.information(
            self,
            "Daten exportieren",
            "Export als CSV/PDF – hier erscheint der Export-Dialog."
        )

    def on_daten_loeschen(self):
        antwort = QMessageBox.question(
            self,
            "Tracking-Daten löschen",
            "Alle Tracking-Einträge werden unwiderruflich gelöscht.\n"
            "Fortfahren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if antwort == QMessageBox.StandardButton.Yes:
            # TODO: Daten aus Datenbank löschen
            print("Tracking-Daten gelöscht")
            QMessageBox.information(
                self, "Gelöscht", "Alle Tracking-Daten wurden gelöscht."
            )

    def on_feedback(self):
        # TODO: Ersetze E-Mail-Adresse durch eure Support-Mail
        webbrowser.open("mailto:support@femhealth.app?subject=Feedback")

    # ── Platzhalter ────────────────────────────────────────────────────────

    def on_platzhalter(self, name):
        # Temporäre Meldung – TODO: jeweiligen Dialog einbauen
        QMessageBox.information(
            self,
            name,
            name + " – hier erscheint der zugehörige Dialog.\n(TODO)"
        )

    # ── Hilfsmethode ───────────────────────────────────────────────────────

    def zeige_fehler(self, text):
        QMessageBox.warning(self, "Fehler", text)


# ── Programm starten (nur zum direkten Testen der Settings-Seite) ──────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
