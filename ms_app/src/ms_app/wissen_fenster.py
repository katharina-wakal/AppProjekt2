import webbrowser  # zum Öffnen von URLs im Standardbrowser
import pathlib      # Arbeiten mit Ordner & Dateien
import threading    # für das Laden der API-Daten im Hintergrund
from PyQt6 import uic                        # uic = UI Compiler: lädt .ui-Dateien
from PyQt6.QtWidgets import QMainWindow      # Basisklasse für das Hauptfenster einer PyQt6-App
from PyQt6.QtCore import QTimer              # QTimer: prüft regelmäßig, ob der Thread fertig ist
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

        # Titel sofort setzen – der ist immer bekannt, kein API-Aufruf nötig
        self.main_window.lblTitel.setText(titel)

        # Platzhalter anzeigen, solange die API noch lädt
        # Der Nutzer sieht das Fenster sofort – ohne Wartezeit
        self.main_window.lblBeschreibung.setText("Wird geladen ...")
        self.main_window.btnWikipedia.setEnabled(False)
        # Button deaktivieren, bis die URL bekannt ist

        # Hier wird das API-Ergebnis später gespeichert
        # Solange der Thread läuft, ist self._ergebnis noch None
        self._ergebnis = None

        print("Starte Hintergrund-Thread für:", suchbegriff)

        # Hintergrund-Thread starten:
        # suche_thema läuft jetzt parallel – die UI bleibt dabei reaktionsfähig
        self._thread = threading.Thread(
            target=self._lade_im_hintergrund,
            args=(suchbegriff,),
            daemon=True
            # daemon=True: Thread wird automatisch beendet,
            # wenn das Hauptprogramm geschlossen wird
        )
        self._thread.start()

        # QTimer prüft alle 100 ms, ob der Thread fertig ist
        # Sobald das Ergebnis da ist, wird die UI aktualisiert
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._ergebnis_pruefen)
        self._timer.start(100)
        # 100 ms = kurze Pause zwischen den Prüfungen → kein spürbarer Overhead

    def _lade_im_hintergrund(self, suchbegriff):
        # Diese Methode läuft im Hintergrund-Thread
        # Sie darf KEINE UI-Elemente verändern – das ist nur im Haupt-Thread erlaubt
        print("Thread läuft – hole Wikipedia-Daten für:", suchbegriff)
        ergebnis = suche_thema(suchbegriff)
        self._ergebnis = ergebnis  # Ergebnis ablegen, damit der Timer es findet
        print("Thread fertig – Ergebnis gespeichert")

    def _ergebnis_pruefen(self):
        # Wird alle 100 ms vom QTimer aufgerufen
        # Sobald self._ergebnis nicht mehr None ist, ist der Thread fertig
        if self._ergebnis is None:
            return  # noch nicht fertig – nächste Runde abwarten

        # Thread ist fertig → Timer stoppen, UI aktualisieren
        self._timer.stop()
        print("Ergebnis empfangen – UI wird aktualisiert")

        ergebnis = self._ergebnis

        # Geladenen Text in das Label schreiben
        self.main_window.lblBeschreibung.setText(ergebnis["beschreibung"])

        # Button aktivieren und mit der Wikipedia-URL verknüpfen
        self.main_window.btnWikipedia.setEnabled(True)
        self.main_window.btnWikipedia.clicked.connect(
            lambda: webbrowser.open(ergebnis["url"]))
        # Verknüpft den Button btnWikipedia mit einer Aktion:
        # lambda = anonyme Funktion, die erst beim Klick ausgeführt wird
        # webbrowser.open(...) öffnet die Wikipedia-URL aus dem API-Ergebnis im Standardbrowser