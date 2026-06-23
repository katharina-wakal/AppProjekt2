import webbrowser
import pathlib
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
from wissen_api import suche_thema


class WissenFenster(QMainWindow):

    def __init__(self, titel, suchbegriff):
        super().__init__()

        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(
            working_dir + "/wissen_fenster.ui", self
        )

        ergebnis = suche_thema(suchbegriff)

        self.main_window.lblTitel.setText(titel)
        self.main_window.lblBeschreibung.setText(ergebnis["beschreibung"])

        self.main_window.btnWikipedia.clicked.connect(
            lambda: webbrowser.open(ergebnis["url"])
        )