import sys  # Importiert sys-Modul für Systemfunktionen (z. B. Kommandozeilenargumente, Beenden)
from PyQt6.QtWidgets import QApplication  # Importiert QApplication-Klasse, die jede PyQt6-App braucht
from login_femhealth import LoginWindow  # Importiert LoginWindow aus eigenen Datei login_femhealth.py


def main():
    """
    Startet die FemHealth-App.
    Zuerst wird die PyQt-Anwendung erstellt.
    Anschließend wird das Login-Fenster geöffnet.
    """

    app = QApplication(sys.argv)  # Erstellt die Qt-Anwendung; sys.argv übergibt mögliche Startparameter

    login_window = LoginWindow()  # Erstellt eine Instanz des Login-Fensters
    login_window.show()           # Zeigt das Login-Fenster auf dem Bildschirm an

    sys.exit(app.exec())  # Startet die Qt-Event-Loop; sys.exit beendet das Programm sauber, wenn sie endet


if __name__ == "__main__":  # Prüft, ob diese Datei direkt ausgeführt wird (nicht als Modul importiert)
    main()                  # Ruft die main()-Funktion auf und startet damit die App


