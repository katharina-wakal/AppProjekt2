import sys

from PyQt6.QtWidgets import QApplication

from login_femhealth import LoginWindow


def main():
    """
    Startet die FemHealth-App.

    Zuerst wird die PyQt-Anwendung erstellt.
    Anschließend wird das Login-Fenster geöffnet.
    """

    app = QApplication(sys.argv)

    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()