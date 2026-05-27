# Einstellungen-Seite – FemHealth
# Wird vom Dashboard über btnSettings geöffnet

import sys
import pathlib
import webbrowser
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox


class SettingsWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(
            working_dir + "/settings.ui", self
        )

        # Passwort-Felder zu Beginn versteckt
        self.pw_offen = False
        self.passwort_felder_verstecken()

        # ── Buttons verbinden ──────────────────────────────────────────────

        # Zurück-Button
        self.main_window.btnBack.clicked.connect(self.on_zurueck)

        # ── Account ───────────────────────────────────────────────────────
        self.main_window.btnEmailAendern.clicked.connect(self.on_email_aendern)
        self.main_window.btnPasswortAendern.clicked.connect(self.on_passwort_toggle)
        self.main_window.btnPwSpeichern.clicked.connect(self.on_passwort_speichern)
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

    def passwort_felder_zeigen(self):
        # Felder aufklappen und untereinander positionieren
        y_start = 248
        abstand = 50
        hoehe   = 40

        felder = [
            self.main_window.txtPwAlt,
            self.main_window.txtPwNeu,
            self.main_window.txtPwNeu2,
        ]
        for i in range(len(felder)):
            felder[i].setVisible(True)
            felder[i].setMaximumHeight(hoehe)
            felder[i].setGeometry(14, y_start + i * abstand, 339, hoehe)

        btn = self.main_window.btnPwSpeichern
        btn.setVisible(True)
        btn.setMaximumHeight(40)
        btn.setGeometry(14, y_start + 3 * abstand, 339, 40)

        # Karte etwas größer machen damit Felder reinpassen
        karte = self.main_window.cardAccount
        karte.setGeometry(10, 40, 367, 490)

    # ── Account-Slots ──────────────────────────────────────────────────────

    def on_zurueck(self):
        # Settings-Fenster schließen → Dashboard bleibt offen
        self.close()

    def on_email_aendern(self):
        # TODO: E-Mail-Änderungs-Dialog einbauen
        QMessageBox.information(
            self,
            "E-Mail ändern",
            "Bitte gib deine neue E-Mail-Adresse ein.\n(TODO: Eingabefeld einblenden)"
        )

    def on_passwort_toggle(self):
        # Passwortfelder ein- oder ausklappen
        if not self.pw_offen:
            self.passwort_felder_zeigen()
            self.pw_offen = True
        else:
            self.passwort_felder_verstecken()
            self.pw_offen = False

    def on_passwort_speichern(self):
        alt  = self.main_window.txtPwAlt.text()
        neu  = self.main_window.txtPwNeu.text()
        neu2 = self.main_window.txtPwNeu2.text()

        # Pflichtfelder prüfen
        if not alt or not neu or not neu2:
            self.zeige_fehler("Bitte alle Passwortfelder ausfüllen.")
            return

        # Neue Passwörter vergleichen
        if neu != neu2:
            self.zeige_fehler("Die neuen Passwörter stimmen nicht überein.")
            return

        # Mindestlänge prüfen
        if len(neu) < 6:
            self.zeige_fehler("Das Passwort muss mindestens 6 Zeichen haben.")
            return

        # TODO: Passwort in Datenbank aktualisieren
        print("Passwort wird geändert")
        QMessageBox.information(self, "Erfolg", "Passwort wurde erfolgreich geändert!")
        self.on_passwort_toggle()

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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if antwort == QMessageBox.StandardButton.Yes:
            # TODO: Session beenden, Login-Fenster öffnen
            print("Nutzer abgemeldet")
            self.close()

    def on_account_loeschen(self):
        antwort = QMessageBox.question(
            self,
            "Account löschen",
            "Achtung: Alle deine Daten werden unwiderruflich gelöscht.\n"
            "Möchtest du fortfahren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if antwort == QMessageBox.StandardButton.Yes:
            # TODO: Account aus Datenbank löschen
            print("Account wird gelöscht")
            QMessageBox.information(self, "Gelöscht", "Dein Account wurde gelöscht.")
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
