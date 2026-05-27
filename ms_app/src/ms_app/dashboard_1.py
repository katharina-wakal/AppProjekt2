# Dashboard – FemHealth
# Navbar ist IMMER unten sichtbar – Inhalt scrollt dahinter

import sys
import pathlib
import webbrowser
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

# Settings-Fenster importieren – Datei muss im selben Ordner liegen
from settings import SettingsWindow

# Zyklus-Ring-Widget importieren
from cycle_ring_widget import CycleRingWidget


# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════

class DashboardWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(
            working_dir + "/dashboard.ui", self
        )

        # Settings-Fenster-Referenz (damit es nicht sofort geschlossen wird)
        self.settings_fenster = None

        # ── Zyklus-Ring einbauen ───────────────────────────────────────────
        # Den Platzhalter-QLabel durch unser eigenes Widget ersetzen
        # (Alternative zu Qt Designer Promotion – funktioniert immer)
        self.ring_widget = CycleRingWidget(self.main_window.framePrognose)

        # Position und Größe des Ring-Widgets gleich wie der Platzhalter
        platzhalter = self.main_window.lblCycleRingPlaceholder
        self.ring_widget.setGeometry(platzhalter.geometry())

        # Platzhalter-Label verstecken – Ring-Widget übernimmt
        platzhalter.hide()
        self.ring_widget.show()

        # ── Zyklus-Daten setzen ────────────────────────────────────────────
        # TODO: Diese Werte aus der Datenbank holen
        self.ring_widget.zyklus_setzen(
            heute         = 14,    # TODO: aktuellen Zyklustag aus DB
            laenge        = 28,    # TODO: durchschnittliche Zykluslänge aus DB
            periode_start = 1,     # TODO: Periodenstart aus DB
            periode_ende  = 5,     # TODO: Periodenende aus DB
            eisprung_start= 12,    # TODO: Eisprung-Fenster aus DB
            eisprung_ende = 16     # TODO: Eisprung-Fenster aus DB
        )

        # Navbar initial korrekt positionieren
        self.navbar_fixieren()

        # ── Buttons verbinden ──────────────────────────────────────────────

        self.main_window.btnSettings.clicked.connect(self.on_settings)
        self.main_window.btnHelp.clicked.connect(self.on_help)

        # Social-Media
        self.main_window.btnInstagram.clicked.connect(self.on_instagram)
        self.main_window.btnX.clicked.connect(self.on_x)
        self.main_window.btnTikTok.clicked.connect(self.on_tiktok)

        # Bottom-Navigation
        self.main_window.navKalender.clicked.connect(self.on_nav_kalender)
        self.main_window.navTracken.clicked.connect(self.on_nav_eintrag)
        self.main_window.navArzt.clicked.connect(self.on_nav_arzt)
        self.main_window.navAnalyse.clicked.connect(self.on_nav_analyse)

        # Filter-Chips (nur einer aktiv gleichzeitig)
        self.filter_chips = [
            self.main_window.chipAlle,
            self.main_window.chipEndo,
            self.main_window.chipSTI,
            self.main_window.chipZyklus,
        ]
        for chip in self.filter_chips:
            chip.clicked.connect(self.on_chip_gewaehlt)

    # ── Navbar immer am unteren Rand ─────────────────────────────────────

    def navbar_fixieren(self):
        # Navbar-Höhe: 76px – bleibt immer am unteren Fensterrand
        navbar_hoehe  = 76
        fenster_hoehe = self.height()
        fenster_breite = self.width()

        navbar = self.main_window.frameNavBar
        navbar.setGeometry(0, fenster_hoehe - navbar_hoehe, fenster_breite, navbar_hoehe)

        # Scroll-Bereich: von unter dem Header bis direkt über die Navbar
        header_hoehe = 125
        scroll = self.main_window.scrollArea
        scroll.setGeometry(
            0,
            header_hoehe,
            fenster_breite,
            fenster_hoehe - header_hoehe - navbar_hoehe
        )

    def resizeEvent(self, event):
        # Wird automatisch aufgerufen wenn das Fenster die Größe ändert
        self.navbar_fixieren()
        super().resizeEvent(event)

    # ── Slots ──────────────────────────────────────────────────────────────

    def on_settings(self):
        # ⚙ Einstellungs-Fenster öffnen
        self.settings_fenster = SettingsWindow()
        self.settings_fenster.show()

    def on_help(self):
        QMessageBox.information(
            self, "Hilfe", "Hilfe & Support – hier erscheint der Support-Dialog."
        )

    def on_instagram(self):
        # TODO: Ersetze URL durch euren echten Instagram-Link
        webbrowser.open("https://www.instagram.com/")

    def on_x(self):
        # TODO: Ersetze URL durch euren echten X-Link
        webbrowser.open("https://x.com/")

    def on_tiktok(self):
        # TODO: Ersetze URL durch euren echten TikTok-Link
        webbrowser.open("https://www.tiktok.com/")

    def on_chip_gewaehlt(self):
        # Nur einen Chip gleichzeitig aktiv halten
        geklickt = self.sender()
        for chip in self.filter_chips:
            if chip is not geklickt:
                chip.setChecked(False)
        print("Filter: " + geklickt.text())

    # ── Navigation ─────────────────────────────────────────────────────────

    def on_nav_kalender(self):
        print("Navigation: Kalender")

    def on_nav_eintrag(self):
        print("Navigation: Eintrag")

    def on_nav_arzt(self):
        print("Navigation: Arzt")

    def on_nav_analyse(self):
        print("Navigation: Analyse")


# ═══════════════════════════════════════════════════════════════
# Programm starten
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
