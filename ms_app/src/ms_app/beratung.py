# ---------------------------------------------------------------------------
# Beratungs- und Kontaktfenster der FemHealth-App
# ---------------------------------------------------------------------------
#
# In dieser Datei wird ein kleines Dialog-Fenster verwaltet, das Beratungs-
# und Kontaktinformationen anzeigt (Telefonberatung, E-Mail und Online-
# Beratung sowie einen Notfall-Hinweis).
#
# Das Fenster wird vom Dashboard aus über den Hilfe-Button ("?") geöffnet.
# Die Oberfläche wird aus der Datei beratung.ui geladen, die Texte und die
# anklickbaren Links werden anschließend hier im Code gesetzt.

# pathlib wird verwendet, um den Speicherort dieser Python-Datei
# und damit den Pfad zur beratung.ui-Datei zuverlässig zu bestimmen.
import pathlib

# uic wird benötigt, um die im Qt Designer erstellte UI-Datei zu laden.
from PyQt6 import uic

# QDialog ist die Basisklasse für dieses Fenster.
# Ein Dialog eignet sich gut für ein kleines Info-Fenster, das sich
# über das Dashboard legt und mit exec() geöffnet werden kann.
from PyQt6.QtWidgets import QDialog

# Qt wird benötigt, um das Textformat eines Labels auf RichText (HTML)
# umzustellen. Nur dadurch lassen sich anklickbare Links darstellen.
from PyQt6.QtCore import Qt


# ---------------------------------------------------------------------------
# Klasse für das Beratungs-Dialogfenster
# ---------------------------------------------------------------------------
class BeratungDialog(QDialog):
    """
        Verwaltet das Beratungs- und Kontaktfenster der FemHealth-App.

        Die Klasse lädt die Benutzeroberfläche aus der Datei beratung.ui,
        befüllt die Labels mit den Kontaktinformationen und stellt die
        Telefonnummer, E-Mail-Adresse und Webadresse als anklickbare
        Links dar.
        """

    def __init__(self, parent=None):
        """
            Initialisiert das Beratungsfenster.

            Dabei wird die UI-Datei geladen, die Texte werden gesetzt
            und der Schließen-Button wird mit der passenden Funktion
            verbunden.

            Parameter:
                parent: Das übergeordnete Fenster (z. B. das Dashboard).
                    Dadurch erscheint der Dialog mittig über dem Fenster,
                    von dem aus er geöffnet wurde. Standardwert ist None.
            """
        # Der Konstruktor der übergeordneten Klasse QDialog wird ausgeführt.
        # parent wird weitergegeben, damit der Dialog dem aufrufenden
        # Fenster zugeordnet ist.
        super().__init__(parent)

        # .ui-Datei laden – genau wie bei euren anderen Fenstern
        # Der Ordner wird bestimmt, in dem sich diese Python-Datei befindet.
        # Dadurch kann die beratung.ui-Datei unabhängig vom aktuellen
        # Arbeitsverzeichnis zuverlässig gefunden werden.
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        # Die im Qt Designer erstellte Oberfläche wird geladen.
        # self wird dabei als das eigentliche Dialog-Fenster verwendet.
        self.main_window = uic.loadUi(
            working_dir + "/beratung.ui", self
        )

        # ── Texte setzen ──────────────────────────────────────────────

        # Die Überschrift des Fensters wird gesetzt.
        self.main_window.lblTitel.setText("Beratung & Kontakt")

        # Kontaktinfos mit anklickbaren Links
        # Der Text wird als HTML formatiert. Die <a href=...>-Bereiche
        # erzeugen anklickbare Links für Telefon (tel:), E-Mail (mailto:)
        # und die Webseite (https:).
        self.main_window.lblKontakt.setText(
            "<div style='font-size:14px; color:#403744; line-height:160%;'>"
            "📞 <b>Telefonberatung</b><br>"
            "<a href='tel:080012345 67' style='color:#6C4A7E;'>0800 / 123 456 7</a><br>"
            "<span style='color:#8A7B92;'>Mo–Fr, 9–18 Uhr · kostenlos &amp; anonym</span>"
            "<br><br>"
            "✉️ <b>E-Mail</b><br>"
            "<a href='mailto:beratung@femhealth.de' style='color:#6C4A7E;'>"
            "beratung@femhealth.de</a>"
            "<br><br>"
            "🌐 <b>Online-Beratung</b><br>"
            "<a href='https://www.femhealth.de/beratung' style='color:#6C4A7E;'>"
            "www.femhealth.de/beratung</a>"
            "</div>"
        )
        # Lange Texte werden umgebrochen, statt aus dem Fenster zu laufen.
        self.main_window.lblKontakt.setWordWrap(True)
        # Das Label wird auf RichText gestellt, damit das HTML
        # (Fettschrift, Links, Farben) korrekt dargestellt wird.
        self.main_window.lblKontakt.setTextFormat(Qt.TextFormat.RichText)
        # Erlaubt, dass die Links beim Anklicken im Standardprogramm
        # geöffnet werden (z. B. Telefon-App, E-Mail-Programm, Browser).
        self.main_window.lblKontakt.setOpenExternalLinks(True)

        # Der Notfall-Hinweis wird gesetzt.
        self.main_window.lblNotfall.setText(
            "Im Notfall wende dich an den ärztlichen Notdienst: 116 117"
        )
        # Auch dieser Text wird bei Bedarf umgebrochen.
        self.main_window.lblNotfall.setWordWrap(True)

        # ── Schließen-Button verbinden ────────────────────────────────

        # Beim Klick auf den Schließen-Button wird das Fenster geschlossen.
        # close() ist eine eingebaute Methode von QDialog.
        self.main_window.btnSchliessen.clicked.connect(self.close)