# Dashboard – FemHealth (v6)
# Fix: Navbar ist jetzt IMMER unten sichtbar – Inhalt scrollt dahinter

import sys
import pathlib
import webbrowser
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QShowEvent

import webbrowser

# Settings-Fenster importieren – Datei muss im selben Ordner liegen
from settings import SettingsWindow
from eintrag import EintragWindow
from database import periodenstarts_laden, user_vorname_laden
from calculation import calculate_cycle_prediction
from cycle_ring_widget import CycleRingWidget
from datetime import date, datetime
from arzttermin import ArztterminWindow
from kalender import KalenderWindow
from analyse import AnalyseWindow


# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════
from wissen_fenster import WissenFenster

class DashboardWindow(QMainWindow):

    def __init__(self, vorname="", user_id=None):

        super().__init__()
        self.vorname = vorname
        self.user_id = user_id

        if not self.vorname and self.user_id is not None:
            self.vorname = user_vorname_laden(self.user_id)

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(
            working_dir + "/dashboard.ui", self
        )

        #Thumbnail für Youtube Video
        pixmap = QPixmap(
            working_dir + "/resources/youtube_thumbnail.png"
        )

        self.main_window.lblYoutubeThumbnail.setPixmap(
            pixmap.scaled(
                self.main_window.lblYoutubeThumbnail.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding
            )
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

        self.main_window.newsCard1.mousePressEvent = lambda event: self.oeffne_endometriose()
        self.main_window.newsCard2.mousePressEvent = lambda event: self.oeffne_sti()
        self.main_window.newsCard3.mousePressEvent = lambda event: self.oeffne_zyklus()

        # Youtube-Video-Button
        self.main_window.buttonYoutube.clicked.connect(self.on_youtube)


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


    def on_settings(self):
        # Einstellungsfenster erstellen
        self.settings_fenster = SettingsWindow(
            user_id=self.user_id
        )

        # Beim Abmelden zurück zum Login wechseln
        self.settings_fenster.logout_requested.connect(
            self.on_logout_requested
        )

        # Beim Schließen der Einstellungen das Dashboard wieder anzeigen
        self.settings_fenster.destroyed.connect(
            self.dashboard_wieder_anzeigen
        )

        self.settings_fenster.show()

        # Dashboard nur verstecken, nicht endgültig schließen
        self.hide()

    def dashboard_wieder_anzeigen(self):
        # Nur wieder anzeigen, wenn nicht gerade abgemeldet wurde
        if not getattr(self, "wird_abgemeldet", False):
            self.show()

    def on_logout_requested(self):
        self.wird_abgemeldet = True

        # Import an deinen tatsächlichen Dateinamen anpassen
        from login_femhealth import LoginWindow

        self.login_fenster = LoginWindow()
        self.login_fenster.show()

        # Einstellungen und Dashboard schließen
        if hasattr(self, "settings_fenster"):
            self.settings_fenster.close()

        self.close()

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

    def on_youtube(self):
        webbrowser.open("https://www.youtube.com/watch?v=tdj2CIzI7Hs")

    # ── Navigation ─────────────────────────────────────────────────────────

    def on_nav_kalender(self):
        print("Navigation: Kalender")

        self.kalender_fenster = KalenderWindow(
            user_id=self.user_id
        )

        self.kalender_fenster.show()
        self.close()

    def on_nav_eintrag(self):
        self.eintrag_fenster = EintragWindow(
            user_id=self.user_id
        )

        self.eintrag_fenster.show()
        self.close()

    def on_nav_arzt(self):
        print("Navigation: Arzt")

        self.arzt_fenster = ArztterminWindow(
            user_id=self.user_id
        )

        self.arzt_fenster.show()
        self.close()

    def on_nav_analyse(self):
        print("Navigation: Analyse")

        self.analyse_fenster = AnalyseWindow(
            user_id=self.user_id
        )

        self.analyse_fenster.show()
        self.close()

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

    def oeffne_endometriose(self):
        self.wissen_fenster = WissenFenster(
            "Endometriose",
            "endometriosis symptoms diagnosis"
        )
        self.wissen_fenster.show()

    def oeffne_sti(self):
        self.wissen_fenster = WissenFenster(
            "STI & Schutz",
            "sexually transmitted infections prevention"
        )
        self.wissen_fenster.show()

    def oeffne_zyklus(self):
        self.wissen_fenster = WissenFenster(
            "Zyklus & PMS",
            "premenstrual syndrome menstrual cycle"
        )
        self.wissen_fenster.show()

    def zeige_perioden_popup(self):
        QMessageBox.information(
            self,
            "Voraussichtlicher Periodenbeginn",
            "Deine Periode beginnt voraussichtlich heute.\n\n"
            "Denke daran, deine Blutungsstärke und mögliche Symptome einzutragen."
        )

    def zeige_ovulations_popup(self):
        QMessageBox.information(
            self,
            "Voraussichtliche Ovulation",
            "Heute ist voraussichtlich dein Ovulationstag.\n\n"
            "Bitte beachte, dass es sich hierbei nur um eine berechnete Prognose handelt."
        )

    def pruefe_zyklus_benachrichtigungen(
            self,
            prognostizierter_periodenstart,
            prognostizierte_ovulation
    ):
        heute = date.today()

        if heute == prognostizierter_periodenstart:
            self.zeige_perioden_popup()

        if heute == prognostizierte_ovulation:
            self.zeige_ovulations_popup()

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)

        app = QApplication.instance()

        if not app.property("zyklus_popups_geprueft"):
            app.setProperty("zyklus_popups_geprueft", True)

            QTimer.singleShot(
                500,
                self.zyklus_benachrichtigungen_pruefen
            )

    def zyklus_benachrichtigungen_pruefen(self):
        if self.user_id is None:
            return

        periodenstarts = periodenstarts_laden(self.user_id)

        # Ohne eingetragene Periodendaten ist keine Prognose möglich
        if len(periodenstarts) == 0:
            return

        prognose = calculate_cycle_prediction(periodenstarts)

        prognostizierter_periodenstart = prognose[
            "predicted_period_start"
        ]

        prognostizierte_ovulation = prognose[
            "predicted_ovulation"
        ]

        self.pruefe_zyklus_benachrichtigungen(
            prognostizierter_periodenstart,
            prognostizierte_ovulation
        )







# ═══════════════════════════════════════════════════════════════
# Programm starten
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
