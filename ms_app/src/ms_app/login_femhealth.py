# ---------------------------------------------------------------------------
# Login-Seite der FemHealth-App
# ---------------------------------------------------------------------------
#
# In dieser Datei wird das Login-Fenster der App verwaltet.
# Benutzer können sich anmelden, zur Registrierung wechseln
# oder einen Hinweis bei vergessenem Passwort anzeigen lassen.
# Nach erfolgreichem Login wird das Dashboard geöffnet.

import sys# sys wird benötigt, um die Anwendung zu starten und beim Beenden einen passenden Rückgabewert an das Betriebssystem zu übergeben.
import pathlib# pathlib wird verwendet, um den Pfad zur UI-Datei zuverlässig zu bestimmen.
import hashlib # hashlib wird genutzt, um das eingegebene Passwort mit SHA-256 zu hashen

from PyQt6 import uic# uic lädt die im Qt Designer erstellte Benutzeroberfläche.
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox)# Benötigte PyQt6-Komponenten für Fenster, Anwendung und Meldungen.

from database import login_pruefen# Datenbankfunktion zur Überprüfung der Login-Daten.
from dashboard import DashboardWindow# Fenster, das nach erfolgreichem Login geöffnet wird.
from register import RegisterWindow# Registrierungsfenster für neue Benutzer.


class LoginWindow(QMainWindow):
    """
        Verwaltet das Login-Fenster der FemHealth-App.

        Die Klasse lädt die Benutzeroberfläche aus der Qt-Designer-Datei,
        verarbeitet die Anmeldung und ermöglicht den Wechsel zur Registrierung.
        """

    def __init__(self):
        """
            Initialisiert das Login-Fenster.

            Dabei wird die UI-Datei geladen und die Buttons werden
            mit den zugehörigen Funktionen verbunden.
            """
        # Den Konstruktor der übergeordneten Klasse QMainWindow ausführen.
        super().__init__()


        # .ui-Datei laden
        # Den Ordner bestimmen, in dem sich diese Python-Datei befindet.
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        # Die im Qt Designer erstellte Login-Oberfläche laden.
        self.main_window = uic.loadUi(working_dir + "/login_femhealth.ui", self)

        # Buttons mit Funktionen verbinden
        self.main_window.loginButton.clicked.connect(self.on_login)
        self.main_window.registerButton.clicked.connect(self.on_register)
        self.main_window.forgotPasswordButton.clicked.connect(self.on_passwort_vergessen)

    # ── Slots ────────────────────────────────────────────────────────────────

    def on_login(self):
        email    = self.main_window.emailLineEdit.text().strip()
        passwort = self.main_window.passwordLineEdit.text()

        # Eingabe prüfen
        if not email or not passwort:
            self.zeige_fehler("Bitte E-Mail und Passwort eingeben.")
            return

        passwort_hash = hashlib.sha256(passwort.encode()).hexdigest()

        user = login_pruefen(email, passwort_hash)

        if user is None:
            self.zeige_fehler("E-Mail oder Passwort ist falsch.")
            return

        print("Login erfolgreich:", user)

        user_id = user[0]
        vorname = user[1]

        self.dashboard = DashboardWindow(
            vorname=vorname,
            user_id=user_id
        )
        self.dashboard.show()
        self.close()

    def on_register(self):
        self.register_window = RegisterWindow()

        self.register_window.login_requested.connect(
            self.login_wieder_anzeigen
        )

        self.register_window.show()
        self.hide()

    def on_passwort_vergessen(self):
        QMessageBox.information(
            self,
            "Passwort vergessen",
            "Bitte wende dich an den Support.")

    # ── Hilfsmethode ─────────────────────────────────────────────────────────

    def zeige_fehler(self, text):
        QMessageBox.warning(self, "Fehler", text)

    def login_wieder_anzeigen(self):
        self.main_window.emailLineEdit.clear()
        self.main_window.passwordLineEdit.clear()

        self.show()
        self.raise_()
        self.activateWindow()


# ── Programm starten ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
