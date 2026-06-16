# Login Seite wo man sich anmelden muss oder registrieren

import sys
import pathlib
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox)
import hashlib
from database import login_pruefen
from dashboard import DashboardWindow
from register import RegisterWindow


class LoginWindow(QMainWindow):

    def __init__(self):
        super().__init__()


        # .ui-Datei laden
        working_dir = str(pathlib.Path(__file__).parent.resolve())
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
