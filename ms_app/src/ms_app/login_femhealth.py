# Login Seite wo man sich anmelden muss oder registrieren

import sys
import pathlib
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox


class LoginWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # .ui-Datei laden – genau wie in VL 4 gezeigt
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

        # TODO: Datenbankabfrage hier einfügen
        # Beispiel: if not user_db.verify_login(email, passwort): ...
        print("Login mit: " + email)

        # Erfolg → Hauptfenster öffnen (TODO)
        QMessageBox.information(self, "Erfolg", "Willkommen zurück! 👋")

    def on_register(self):
        # Registrierungsfenster öffnen
        # TODO: from register_femhealth import RegisterWindow
        print("Registrieren geöffnet")

    def on_passwort_vergessen(self):
        QMessageBox.information(
            self,
            "Passwort vergessen",
            "Bitte wende dich an den Support."
        )

    # ── Hilfsmethode ─────────────────────────────────────────────────────────

    def zeige_fehler(self, text):
        QMessageBox.warning(self, "Fehler", text)


# ── Programm starten ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
