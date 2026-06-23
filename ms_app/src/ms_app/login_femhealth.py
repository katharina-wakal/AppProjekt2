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

# ---------------------------------------------------------------------------
# Klasse für das Login-Fenster
# ---------------------------------------------------------------------------
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
        """
                Liest die eingegebene E-Mail-Adresse und das Passwort aus
                und überprüft die Zugangsdaten über die Datenbank.

                Ablauf:
                    1. E-Mail-Adresse und Passwort auslesen.
                    2. Prüfen, ob beide Felder ausgefüllt sind.
                    3. Passwort mit SHA-256 hashen.
                    4. Zugangsdaten über login_pruefen kontrollieren.
                    5. Bei erfolgreichem Login das Dashboard öffnen.
                    6. Bei einem Fehler eine Warnmeldung anzeigen.
                """
        # Der Text aus dem E-Mail-Eingabefeld wird ausgelesen.
        # strip() entfernt Leerzeichen am Anfang und Ende.
        email    = self.main_window.emailLineEdit.text().strip()

        # Das eingegebene Passwort wird aus dem Passwortfeld ausgelesen.
        passwort = self.main_window.passwordLineEdit.text()

        # Es wird geprüft, ob mindestens eines der beiden Felder leer ist.
        if not email or not passwort:
            # Falls ein Feld leer ist, wird eine Fehlermeldung angezeigt.
            self.zeige_fehler("Bitte E-Mail und Passwort eingeben.")
            # Die Funktion wird hier beendet,
            # damit keine Datenbankabfrage durchgeführt wird.
            return

        # Die Funktion wird hier beendet,
        # damit keine Datenbankabfrage durchgeführt wird.
        passwort_hash = hashlib.sha256(passwort.encode()).hexdigest()

        # Die Datenbankfunktion überprüft,
        # ob die E-Mail-Adresse und der Passwort-Hash zusammenpassen.
        user = login_pruefen(email, passwort_hash)

        # Wenn kein passender Benutzer gefunden wurde,
        # liefert login_pruefen den Wert None zurück.
        if user is None:
            # Eine Fehlermeldung wird angezeigt.
            self.zeige_fehler("E-Mail oder Passwort ist falsch.")
            # Die Funktion wird beendet.
            return

        # Für Test- und Kontrollzwecke wird der gefundene Benutzer
        # in der Konsole ausgegeben.
        print("Login erfolgreich:", user)

        # Der erste Wert des zurückgegebenen Tupels
        # enthält die ID des Benutzers.
        user_id = user[0]
        vorname = user[1]

        # Ein neues Dashboard-Fenster wird erstellt.
        # Dabei werden Vorname und Benutzer-ID übergeben.
        self.dashboard = DashboardWindow(
            vorname=vorname,
            user_id=user_id
        )
        # Das Dashboard wird sichtbar gemacht.
        self.dashboard.show()
        # Das Login-Fenster wird geschlossen,
        # weil die Anmeldung erfolgreich war.
        self.close()

    def on_register(self):
        """
                Öffnet das Registrierungsfenster.

                Das Login-Fenster wird währenddessen ausgeblendet.
                Wenn das Registrierungsfenster das Signal login_requested sendet,
                wird das Login-Fenster wieder angezeigt.

                Rückgabewert:
                    Die Funktion gibt keinen Wert zurück.
                """
        # Ein neues Registrierungsfenster wird erstellt.
        self.register_window = RegisterWindow()

        # Das Signal login_requested des Registrierungsfensters
        # wird mit der Funktion login_wieder_anzeigen verbunden.
        #
        # Das Signal wird ausgelöst, wenn der Benutzer
        # von der Registrierung zurück zum Login wechseln möchte.
        self.register_window.login_requested.connect(
            self.login_wieder_anzeigen)

        # Das Registrierungsfenster wird angezeigt.
        self.register_window.show()
        # Das Login-Fenster wird ausgeblendet,
        # aber nicht vollständig geschlossen.
        self.hide()

    def on_passwort_vergessen(self):
        """
                Zeigt einen Hinweis an, wenn der Benutzer
                auf „Passwort vergessen“ klickt.

                Eine automatische Passwort-Wiederherstellung
                ist aktuell nicht umgesetzt.
                """
        QMessageBox.information(
            self,
            "Passwort vergessen",
            "Bitte wende dich an den Support.")

    # ── Hilfsmethode ─────────────────────────────────────────────────────────

    def zeige_fehler(self, text):
        """
                Zeigt eine Warnmeldung mit einem übergebenen Fehlertext an.

                Parameter:
                    text (str): Text, der in der Fehlermeldung angezeigt wird.
                """
        QMessageBox.warning(self, "Fehler", text)

    def login_wieder_anzeigen(self):
        """
                Zeigt das Login-Fenster wieder an.

                Vorher werden die bisherigen Eingaben aus den Feldern gelöscht.
                Anschließend wird das Fenster nach vorne geholt und aktiviert.
                """
        # Der Inhalt des E-Mail-Feldes wird gelöscht.
        self.main_window.emailLineEdit.clear()
        # Der Inhalt des Passwortfeldes wird gelöscht.
        self.main_window.passwordLineEdit.clear()

        # Das zuvor ausgeblendete Login-Fenster
        # wird wieder sichtbar gemacht.
        self.show()
        # Das Login-Fenster wird vor andere geöffnete Fenster geholt.
        self.raise_()
        # Das Login-Fenster wird als aktives Fenster festgelegt.
        self.activateWindow()


# ── Programm starten ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
