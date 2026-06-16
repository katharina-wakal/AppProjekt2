#Seite zur Registrierung


import sys
import pathlib
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import pyqtSignal
from database import user_anlegen
import hashlib

class RegisterWindow(QMainWindow):

    login_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/register.ui", self)

        # Buttons mit Funktionen verbinden
        self.main_window.registerButton.clicked.connect(self.on_registrieren)
        self.main_window.toLoginButton.clicked.connect(self.on_zurueck_zum_login)

        # Passwort-Regeln live prüfen während Nutzer tippt
        self.main_window.pw1LineEdit.textChanged.connect(self.passwort_regeln_pruefen)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def on_registrieren(self):
        # Felder auslesen
        vorname    = self.main_window.vornameLineEdit.text().strip()
        nachname   = self.main_window.nachnameLineEdit.text().strip()
        email1     = self.main_window.email1LineEdit.text().strip()
        email2     = self.main_window.email2LineEdit.text().strip()
        pw1        = self.main_window.pw1LineEdit.text()
        pw2        = self.main_window.pw2LineEdit.text()
        datenschutz = self.main_window.cbDatenschutz.isChecked()

        # Pflichtfelder prüfen
        if not vorname or not nachname or not email1 or not email2 or not pw1 or not pw2:
            self.zeige_fehler("Bitte alle Pflichtfelder ausfüllen.")
            return

        # E-Mails prüfen
        if email1 != email2:
            self.main_window.lblEmailHint.setText("E-Mail-Adressen stimmen nicht überein.")
            return
        else:
            self.main_window.lblEmailHint.setText("")

        # Passwörter prüfen
        if pw1 != pw2:
            self.main_window.lblPwHint.setText("Passwörter stimmen nicht überein.")
            return
        else:
            self.main_window.lblPwHint.setText("")

        # Passwort-Regeln prüfen
        if not self.passwort_gueltig(pw1):
            self.zeige_fehler("Das Passwort erfüllt nicht alle Anforderungen.")
            return

        # Datenschutz prüfen
        if not datenschutz:
            self.zeige_fehler("Bitte die Datenschutzerklärung akzeptieren.")
            return

        # Passwort hashen
        password_hash = hashlib.sha256(pw1.encode()).hexdigest()

        # Newsletter optional
        newsletter = 0

        # Geburtsdatum vorerst als Platzhalter
        geburtsdatum = "2000-01-01"

        # Nutzer speichern
        user_anlegen(
            vorname,
            nachname,
            geburtsdatum,
            email1,
            password_hash,
            1,
            newsletter
        )

        print("Registrierung erfolgreich gespeichert")

        QMessageBox.information(self, "Erfolg", "Konto wurde erfolgreich erstellt!")
        self.on_zurueck_zum_login()

    def on_zurueck_zum_login(self):
        print("Zurück zum Login")

        # Dem bestehenden Loginfenster mitteilen,
        # dass es wieder angezeigt werden soll
        self.login_requested.emit()

        # Registrierungsfenster schließen
        self.close()

    def passwort_regeln_pruefen(self):
        # Wird aufgerufen während der Nutzer das Passwort tippt
        pw = self.main_window.pw1LineEdit.text()

        # Regel 1: Mindestens 6 Zeichen
        if len(pw) >= 6:
            self.main_window.lblRule1.setStyleSheet(
                "QLabel{color:#4CAF50;font-size:11px;background:transparent;}")
        else:
            self.main_window.lblRule1.setStyleSheet(
                "QLabel{color:#BDBDBD;font-size:11px;background:transparent;}")

        # Regel 2: Mindestens eine Zahl
        hat_zahl = False
        for zeichen in pw:
            if zeichen.isdigit():
                hat_zahl = True
        if hat_zahl:
            self.main_window.lblRule2.setStyleSheet(
                "QLabel{color:#4CAF50;font-size:11px;background:transparent;}")
        else:
            self.main_window.lblRule2.setStyleSheet(
                "QLabel{color:#BDBDBD;font-size:11px;background:transparent;}")

        # Regel 3: Mindestens ein Großbuchstabe
        hat_gross = False
        for zeichen in pw:
            if zeichen.isupper():
                hat_gross = True
        if hat_gross:
            self.main_window.lblRule3.setStyleSheet(
                "QLabel{color:#4CAF50;font-size:11px;background:transparent;}")
        else:
            self.main_window.lblRule3.setStyleSheet(
                "QLabel{color:#BDBDBD;font-size:11px;background:transparent;}")

    # ── Hilfsmethoden ─────────────────────────────────────────────────────────

    def passwort_gueltig(self, pw):
        # Gibt True zurück wenn alle 3 Regeln erfüllt sind
        if len(pw) < 6:
            return False

        hat_zahl = False
        for zeichen in pw:
            if zeichen.isdigit():
                hat_zahl = True

        hat_gross = False
        for zeichen in pw:
            if zeichen.isupper():
                hat_gross = True

        return hat_zahl and hat_gross

    def zeige_fehler(self, text):
        QMessageBox.warning(self, "Fehler", text)


# ── Programm starten ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())
