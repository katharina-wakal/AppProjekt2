# Dashboard – FemHealth (v6)
# Fix: Navbar ist jetzt IMMER unten sichtbar – Inhalt scrollt dahinter

import sys
import pathlib
import webbrowser
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

# Settings-Fenster importieren – Datei muss im selben Ordner liegen
from settings import SettingsWindow
from eintrag import EintragWindow
from database import periodenstarts_laden
from calculation import calculate_cycle_prediction
from cycle_ring_widget import CycleRingWidget
from datetime import date
from arzttermin import ArztterminWindow
from kalender import KalenderWindow
from analyse import AnalyseWindow

# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════

class DashboardWindow(QMainWindow):

    def __init__(self, vorname="", user_id=None):

        super().__init__()
        self.vorname = vorname
        self.user_id = user_id


        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(
            working_dir + "/dashboard.ui", self
        )

        # Platzhalter verstecken
        self.main_window.lblCycleRingPlaceholder.hide()

        # Echtes CycleRingWidget erstellen
        self.cycle_ring = CycleRingWidget(self.main_window.framePrognose)

        # An dieselbe Stelle setzen wie der Platzhalter
        self.cycle_ring.setGeometry(
            self.main_window.lblCycleRingPlaceholder.geometry()
        )

        # anzeigen
        self.cycle_ring.show()

        self.zyklus_prognose_laden()

        # Settings-Fenster-Referenz (damit es nicht sofort geschlossen wird)
        self.settings_fenster = None
        if self.vorname:
            self.main_window.lblGreeting.setText(
                "Guten Morgen, " + self.vorname + " 👋"
            )

        # Navbar initial korrekt positionieren
        self.navbar_fixieren()

        # ── Buttons verbinden ──────────────────────────────────────────────

        # ⚙ Zahnrad → Settings-Fenster öffnen
        self.main_window.btnSettings.clicked.connect(self.on_settings)

        # ? Hilfe-Button
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

    # ── Navbar immer am unteren Rand ─────────────────────────────────────

    def navbar_fixieren(self):
        # Navbar-Höhe: 76px – bleibt immer am unteren Fensterrand
        navbar_hoehe = 76
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
        # Referenz wird in self gespeichert damit das Fenster nicht sofort
        # vom Garbage Collector geschlossen wird
        self.settings_fenster = SettingsWindow()
        self.settings_fenster.show()

    def on_help(self):
        QMessageBox.information(
            self, "Hilfe", "Hilfe & Support – hier erscheint der Support-Dialog."
        )

    def on_instagram(self):
        # TODO: Ersetze URL durch euren echten Instagram-Link
        webbrowser.open("https://www.instagram.com/")
        print("Instagram geöffnet")

    def on_x(self):
        # TODO: Ersetze URL durch euren echten X-Link
        webbrowser.open("https://x.com/")
        print("X geöffnet")

    def on_tiktok(self):
        # TODO: Ersetze URL durch euren echten TikTok-Link
        webbrowser.open("https://www.tiktok.com/")
        print("TikTok geöffnet")

    # ── Navigation ─────────────────────────────────────────────────────────

    def on_nav_kalender(self):
        print("Navigation: Kalender")

        self.kalender_fenster = KalenderWindow(
            user_id=self.user_id
        )

        self.kalender_fenster.show()

    def on_nav_eintrag(self):
        self.eintrag_fenster = EintragWindow(
            user_id=self.user_id
        )

        self.eintrag_fenster.show()

    def on_nav_arzt(self):
        print("Navigation: Arzt")

        self.arzt_fenster = ArztterminWindow(
            user_id=self.user_id
        )

        self.arzt_fenster.show()

    def on_nav_analyse(self):
        print("Navigation: Analyse")

        self.analyse_fenster = AnalyseWindow(
            user_id=self.user_id
        )

        self.analyse_fenster.show()

    def zyklus_prognose_laden(self):
        if self.user_id is None:
            return

        periodenstarts = periodenstarts_laden(self.user_id)

        if len(periodenstarts) == 0:
            self.main_window.lblDaysInfo.setText("Noch keine Periode eingetragen")
            self.main_window.lblCycleDay.setText("Keine Zyklusdaten")
            self.main_window.lblCyclePhase.setText("Noch keine Prognose")
            return

        prognose = calculate_cycle_prediction(periodenstarts)

        naechste_periode = prognose["predicted_period_start"]
        eisprung = prognose["predicted_ovulation"]
        durchschnitt = prognose["average_cycle"]

        letzte_periode = prognose["predicted_period_start"]

        heute = date.today()

        zyklus_tag = (
                             (heute - letzte_periode).days
                             % durchschnitt
                     ) + 1

        eisprung_tag = durchschnitt - 14

        self.cycle_ring.zyklus_setzen(
            heute=zyklus_tag,
            laenge=durchschnitt,
            periode_start=1,
            periode_ende=5,
            eisprung_start=eisprung_tag - 2,
            eisprung_ende=eisprung_tag + 2
        )

        self.main_window.lblDaysInfo.setText(
            "Nächste Periode: " + naechste_periode.strftime("%d.%m.%Y")
        )

        self.main_window.lblCycleDay.setText(
            str(durchschnitt) + "-Tage-Zyklus"
        )

        self.main_window.lblCyclePhase.setText(
            "Eisprung ca. am " + eisprung.strftime("%d.%m.%Y")
        )






# ═══════════════════════════════════════════════════════════════
# Programm starten
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
