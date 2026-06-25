import pathlib
from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt


class BeratungDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # .ui-Datei laden – genau wie bei euren anderen Fenstern
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(
            working_dir + "/beratung.ui", self
        )

        # ── Texte setzen ──────────────────────────────────────────────

        self.main_window.lblTitel.setText("Beratung & Kontakt")

        # Kontaktinfos mit anklickbaren Links
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
        self.main_window.lblKontakt.setWordWrap(True)
        self.main_window.lblKontakt.setTextFormat(Qt.TextFormat.RichText)
        self.main_window.lblKontakt.setOpenExternalLinks(True)

        self.main_window.lblNotfall.setText(
            "Im Notfall wende dich an den ärztlichen Notdienst: 116 117"
        )
        self.main_window.lblNotfall.setWordWrap(True)

        # ── Schließen-Button verbinden ────────────────────────────────

        self.main_window.btnSchliessen.clicked.connect(self.close)