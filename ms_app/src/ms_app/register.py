# ---------------------------------------------------------------------------
# Registrierungsseite der FemHealth-App
# ---------------------------------------------------------------------------
#
# In dieser Datei wird das Registrierungsfenster verwaltet.
# Neue Benutzer können hier ihre persönlichen Daten eingeben,
# ein Passwort festlegen und ein Benutzerkonto erstellen.
#
# Nach erfolgreicher Registrierung wird das Konto über database.py
# in der SQLite-Datenbank gespeichert. Anschließend wird wieder
# das Login-Fenster angezeigt.

import sys#sys wird benötigt, um die PyQt-Andwendung zu starten
# #und beim Beenden einen Rückgabewert an das Betriebssystem zu übergeben

# pathlib wird verwendet, um den Speicherort dieser Python-Datei
# und damit den Pfad zur register.ui-Datei zu bestimmen.
import pathlib

# hashlib wird verwendet, um das Passwort vor dem Speichern zu hashen.
# Dadurch wird das Passwort nicht direkt im Klartext gespeichert.
import hashlib
from PyQt6 import uic# uic wird benötigt, um die im Qt Designer erstellte UI-Datei zu laden.

# QApplication verwaltet die gesamte PyQt-Anwendung.
# # QMainWindow ist die Basisklasse des Registrierungsfensters.
from PyQt6.QtWidgets import QApplication, QMainWindow

# pyqtSignal wird benötigt, um ein eigenes Signal zu erstellen.
# Dieses Signal informiert das Login-Fenster darüber,
# dass es wieder angezeigt werden soll.
from PyQt6.QtCore import pyqtSignal

# user_anlegen speichert einen neuen Benutzer
# in der Datenbank.
from database import user_anlegen

# Das MessageMixin stellt wiederverwendbare Methoden
# für Fehler- und Informationsmeldungen bereit.
from message_mixin import MessageMixin

# ---------------------------------------------------------------------------
# Klasse für das Registrierungsfenster
# ---------------------------------------------------------------------------

# RegisterWindow erbt gleichzeitig von zwei Klassen:
#
# QMainWindow stellt die Funktionen eines PyQt-Hauptfensters bereit.
# MessageMixin ergänzt einheitliche Methoden für Meldungsfenster.
#
# Da RegisterWindow von zwei Elternklassen erbt,
# wird Mehrfachvererbung verwendet.
class RegisterWindow(QMainWindow, MessageMixin):
    """
        Verwaltet das Registrierungsfenster der FemHealth-App.

        Die Klasse lädt die Benutzeroberfläche, prüft die eingegebenen Daten
        und speichert einen neuen Benutzer in der Datenbank.

        Zusätzlich wird während der Eingabe angezeigt, ob das Passwort
        die festgelegten Regeln erfüllt.
        """
    # Dieses eigene Signal wird ausgelöst, wenn die Benutzerin
    # von der Registrierung zurück zum Login wechseln möchte.
    #
    # Das Login-Fenster kann dieses Signal empfangen und sich
    # anschließend wieder sichtbar machen.
    login_requested = pyqtSignal()

    def __init__(self):
        """
                Initialisiert das Registrierungsfenster.

                Dabei wird die UI-Datei geladen und die Buttons sowie
                Eingabefelder werden mit den passenden Funktionen verbunden.
                """
        # Der Konstruktor der übergeordneten Klasse QMainWindow wird ausgeführt.
        super().__init__()

        # Der Ordner wird bestimmt, in dem sich diese Python-Datei befindet.
        # Dadurch kann die register.ui-Datei unabhängig vom aktuellen
        # Arbeitsverzeichnis zuverlässig gefunden werden.
        working_dir = str(pathlib.Path(__file__).parent.resolve())

        # Die im Qt Designer erstellte Registrierungsoberfläche wird geladen.
        # self wird als Hauptfenster verwendet.
        self.main_window = uic.loadUi(working_dir + "/register.ui", self)

        # Buttons mit Funktionen verbinden
        self.main_window.registerButton.clicked.connect(self.on_registrieren)
        self.main_window.toLoginButton.clicked.connect(self.on_zurueck_zum_login)


        # Sobald sich der Inhalt des ersten Passwortfeldes verändert,
        # werden die Passwortregeln erneut geprüft.
        #
        # Dadurch sieht die Benutzerin bereits während des Tippens,
        # welche Anforderungen erfüllt sind.
        self.main_window.pw1LineEdit.textChanged.connect(self.passwort_regeln_pruefen)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def on_registrieren(self):
        """
                Liest die eingegebenen Registrierungsdaten aus, prüft sie
                und speichert einen neuen Benutzer in der Datenbank.

                Ablauf:
                    1. Eingabefelder auslesen.
                    2. Pflichtfelder prüfen.
                    3. E-Mail-Adressen vergleichen.
                    4. Passwörter vergleichen.
                    5. Passwortregeln überprüfen.
                    6. Zustimmung zum Datenschutz prüfen.
                    7. Passwort hashen.
                    8. Benutzer in der Datenbank speichern.
                    9. Erfolgsmeldung anzeigen.
                    10. Zum Login zurückkehren.
                """

        # -------------------------------------------------------------------
        # Eingaben aus der Benutzeroberfläche auslesen
        # -------------------------------------------------------------------
        vorname    = self.main_window.vornameLineEdit.text().strip()
        nachname   = self.main_window.nachnameLineEdit.text().strip()
        email1     = self.main_window.email1LineEdit.text().strip()
        email2     = self.main_window.email2LineEdit.text().strip()
        pw1        = self.main_window.pw1LineEdit.text()
        pw2        = self.main_window.pw2LineEdit.text()
        datenschutz = self.main_window.cbDatenschutz.isChecked()

        # Pflichtfelder prüfen
        # Es wird geprüft, ob mindestens eines der Pflichtfelder leer ist.
        if not vorname or not nachname or not email1 or not email2 or not pw1 or not pw2:
            # Wenn ein Pflichtfeld leer ist, wird eine Fehlermeldung angezeigt.
            self.zeige_fehler("Bitte alle Pflichtfelder ausfüllen.")
            # Die Funktion wird beendet.
            # Dadurch werden keine weiteren Prüfungen durchgeführt.
            return

        # E-Mails prüfen
        if email1 != email2:
            # Wenn sie nicht übereinstimmen, wird ein Hinweis
            # direkt im Registrierungsfenster angezeigt.
            self.main_window.lblEmailHint.setText("E-Mail-Adressen stimmen nicht überein.")
            # Die Registrierung wird an dieser Stelle abgebrochen.
            return
        else:
            # Falls beide E-Mail-Adressen übereinstimmen,
            # wird eine vorherige Fehlermeldung entfernt.
            self.main_window.lblEmailHint.setText("")

        # Passwörter prüfen
        if pw1 != pw2:
            # Wenn sie nicht übereinstimmen, wird ein Hinweis
            # direkt unter den Passwortfeldern angezeigt.
            self.main_window.lblPwHint.setText("Passwörter stimmen nicht überein.")
            # Die Registrierung wird abgebrochen.
            return
        else:
            # Falls beide Passwörter übereinstimmen,
            # wird eine vorherige Fehlermeldung entfernt.
            self.main_window.lblPwHint.setText("")

        # Die Hilfsfunktion passwort_gueltig() prüft,
        # ob das Passwort alle festgelegten Regeln erfüllt.
        if not self.passwort_gueltig(pw1):
            # Bei einem ungültigen Passwort wird eine Meldung angezeigt.
            self.zeige_fehler("Das Passwort erfüllt nicht alle Anforderungen.")
            # Die Registrierung wird abgebrochen.
            return

        # Für eine Registrierung muss die Datenschutzerklärung
        # akzeptiert worden sein.
        if not datenschutz:
            # Wenn die Checkbox nicht aktiviert wurde,
            # wird eine Fehlermeldung angezeigt.
            self.zeige_fehler("Bitte die Datenschutzerklärung akzeptieren.")
            # Die Registrierung wird abgebrochen.
            return

        # Das Passwort wird zunächst in Bytes umgewandelt.
        # Anschließend wird mit SHA-256 ein Hash erzeugt.
        #
        # hexdigest() wandelt den Hash in eine lesbare Zeichenkette um.
        password_hash = hashlib.sha256(pw1.encode()).hexdigest()

        # Der Newsletter ist standardmäßig nicht abonniert.
        # 0 bedeutet "nein", 1 würde "ja" bedeuten.
        newsletter = 0

        # Das Geburtsdatum wird derzeit noch nicht aus einem Eingabefeld
        # ausgelesen, sondern als fester Platzhalter gespeichert.
        geburtsdatum = "2000-01-01"

        # Die Funktion user_anlegen() aus database.py wird aufgerufen.
        #
        # Die Werte werden in derselben Reihenfolge übergeben,
        # wie sie von der Funktion erwartet werden.
        user_anlegen(
            vorname,
            nachname,
            geburtsdatum,
            email1,
            password_hash,
            1,
            newsletter
        )
        # Die Zahl 1 steht hier dafür,
        # dass die Datenschutzerklärung akzeptiert wurde.
        #
        # Diese Prüfung wurde bereits weiter oben durchgeführt.

        # Eine Kontrollmeldung wird in der Konsole ausgegeben.
        print("Registrierung erfolgreich gespeichert")

        # Über die geerbte Methode des MessageMixins
        # wird die erfolgreiche Registrierung bestätigt.
        self.zeige_information(
            "Erfolg",
            "Konto wurde erfolgreich erstellt!"
        )
        # Nach dem Bestätigen der Meldung wird wieder
        # zum Login-Fenster gewechselt.
        self.on_zurueck_zum_login()

    def on_zurueck_zum_login(self):
        """
                Informiert das Login-Fenster darüber, dass es wieder angezeigt
                werden soll, und schließt anschließend das Registrierungsfenster.
                """
        # Eine Kontrollmeldung wird in der Konsole ausgegeben.
        print("Zurück zum Login")

        # Das eigene Signal login_requested wird ausgelöst.
        #
        # Das Login-Fenster hat dieses Signal zuvor mit seiner Funktion
        # login_wieder_anzeigen verbunden.
        self.login_requested.emit()

        # Registrierungsfenster schließen
        self.close()

    def passwort_regeln_pruefen(self):
        """
                Prüft während der Eingabe, welche Passwortregeln bereits
                erfüllt sind.

                Erfüllte Regeln werden grün dargestellt.
                Noch nicht erfüllte Regeln werden grau dargestellt.

                Geprüfte Regeln:
                    1. Mindestens sechs Zeichen.
                    2. Mindestens eine Zahl.
                    3. Mindestens ein Großbuchstabe.
                """
        # Wird aufgerufen während der Nutzer das Passwort tippt
        pw = self.main_window.pw1LineEdit.text()

        # Regel 1: Mindestens 6 Zeichen
        # len(pw) liefert die Anzahl der Zeichen im Passwort.
        if len(pw) >= 6:

            #Wenn das Passwort mindestens sechs Zeichen enthält,
            # wird die erste Regel grün dargestellt.
            self.main_window.lblRule1.setStyleSheet(
                "QLabel{color:#4CAF50;font-size:11px;background:transparent;}")
        else:
            # Wenn das Passwort zu kurz ist,
            # bleibt die erste Regel grau.
            self.main_window.lblRule1.setStyleSheet(
                "QLabel{color:#BDBDBD;font-size:11px;background:transparent;}")

        # Regel 2: Mindestens eine Zahl

        # Zu Beginn wird angenommen,
        # dass das Passwort noch keine Zahl enthält.
        hat_zahl = False

        # Jedes einzelne Zeichen des Passworts wird durchlaufen.
        for zeichen in pw:

            # isdigit() prüft, ob das Zeichen eine Zahl ist.
            if zeichen.isdigit():
                # Sobald eine Zahl gefunden wurde,
                # wird die Variable auf True gesetzt.
                hat_zahl = True

        # Es wird geprüft, ob mindestens eine Zahl gefunden wurde.
        if hat_zahl:
            # Wenn eine Zahl vorhanden ist,
            # wird die zweite Regel grün dargestellt.
            self.main_window.lblRule2.setStyleSheet(
                "QLabel{color:#4CAF50;font-size:11px;background:transparent;}")
        else:
            # Wenn keine Zahl vorhanden ist,
            # bleibt die zweite Regel grau.
            self.main_window.lblRule2.setStyleSheet(
                "QLabel{color:#BDBDBD;font-size:11px;background:transparent;}")

        # Regel 3: Mindestens ein Großbuchstabe

        # Wenn keine Zahl vorhanden ist,
        # bleibt die zweite Regel grau.
        hat_gross = False

        # Jedes einzelne Zeichen wird erneut überprüft.
        for zeichen in pw:
            # isupper() prüft, ob das Zeichen ein Großbuchstabe ist.
            if zeichen.isupper():
                # Sobald ein Großbuchstabe gefunden wurde,
                # wird die Variable auf True gesetzt.
                hat_gross = True

        # Es wird geprüft, ob mindestens ein Großbuchstabe gefunden wurde.
        if hat_gross:
            # Wenn ein Großbuchstabe vorhanden ist,
            # wird die dritte Regel grün dargestellt.
            self.main_window.lblRule3.setStyleSheet(
                "QLabel{color:#4CAF50;font-size:11px;background:transparent;}")
        else:
            # Wenn kein Großbuchstabe vorhanden ist,
            # bleibt die dritte Regel grau.
            self.main_window.lblRule3.setStyleSheet(
                "QLabel{color:#BDBDBD;font-size:11px;background:transparent;}")

    # ── Hilfsmethoden ─────────────────────────────────────────────────────────

    def passwort_gueltig(self, pw):
        """
                Prüft, ob ein Passwort alle festgelegten Regeln erfüllt.

                Parameter:
                    pw (str): Das zu überprüfende Passwort.

                Rückgabewert:
                    bool: True, wenn das Passwort mindestens sechs Zeichen,
                    mindestens eine Zahl und mindestens einen Großbuchstaben
                    enthält. Andernfalls wird False zurückgegeben.
                """

        # Gibt True zurück wenn alle 3 Regeln erfüllt sind
        # Wenn das Passwort weniger als sechs Zeichen enthält,
        # ist es direkt ungültig.
        if len(pw) < 6:
            return False

        #Zu Beginn wird angenommen, dass keine Zahl vorhanden ist
        hat_zahl = False
        # Alle Zeichen des Passworts werden durchlaufen.
        for zeichen in pw:
            # isdigit() prüft, ob das aktuelle Zeichen eine Zahl ist.
            if zeichen.isdigit():
                # Sobald eine Zahl gefunden wurde,
                # wird die Variable auf True gesetzt.
                hat_zahl = True

        # Zu Beginn wird angenommen,dass kein Großbuchstabe vorhanden ist.
        hat_gross = False
        # Alle Zeichen werden erneut durchlaufen.
        for zeichen in pw:
            # Wenn das aktuelle Zeichen ein Großbuchstabe ist,
            # wird hat_gross auf True gesetzt.
            if zeichen.isupper():
                hat_gross = True

        # Die Funktion gibt nur dann True zurück,
        # wenn beide Bedingungen erfüllt sind.
        return hat_zahl and hat_gross


# ── Programm starten ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())