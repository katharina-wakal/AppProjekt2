import webbrowser  # zum Öffnen von URLs im Standardbrowser
import pathlib      # Arbeiten mit Ordner & Dateien
from PyQt6 import uic                        # uic = UI Compiler: lädt .ui-Dateien
from PyQt6.QtWidgets import QMainWindow      # Basisklasse für das Hauptfenster einer PyQt6-App
from wissen_api import suche_thema           # Importiert eigene Funktion: suche_thema aus wissen_api.py


class WissenFenster(QMainWindow):  # Definiert das WissenFenster als Unterklasse von QMainWindow

    def __init__(self, titel, suchbegriff):  # Konstruktor: wird aufgerufen wenn WissenFenster() erstellt wird
        super().__init__()  # Ruft den Konstruktor der Elternklasse (QMainWindow) auf – immer nötig bei Vererbung

        # Ermittelt Order-Pfad der aktuellen Datei, um später die .ui-Datei zu laden
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        # __file__ = Pfad dieser .py-Datei
        # .parent = Verzeichnis, in dem die Datei liegt
        # .resolve() = macht den Pfad absolut
        # str(...)   = wandelt das Path-Objekt in normalen String um

        # Lädt wissen_fenster.ui & verbindet sie mit Python-Code.
        # danach Widgets aus .ui-Datei über self.main_window erreichbar
        self.main_window = uic.loadUi(working_dir + "/wissen_fenster.ui", self)

        # Ruft API-Funktion mit übergebenen Suchbegriff auf
        # Erwartet Dictionary zurück, z. B. {"beschreibung": "...", "url": "..."}
        ergebnis = suche_thema(suchbegriff)

        # Setzt den Text des Labels lblTitel auf den übergebenen Titel-Parameter
        self.main_window.lblTitel.setText(titel)

        # Setzt den Text des Labels lblBeschreibung auf die "Beschreibung" aus dem Dictionary
        self.main_window.lblBeschreibung.setText(ergebnis["beschreibung"])

        self.main_window.btnWikipedia.clicked.connect(
            lambda: webbrowser.open(ergebnis["url"]))
        # Verknüpft den Button btnWikipedia mit einer Aktion:
        # lambda = anonyme Funktion, die erst beim Klick ausgeführt wird
        # webbrowser.open(...) öffnet die Wikipedia-URL aus dem API-Ergebnis im Standardbrowser