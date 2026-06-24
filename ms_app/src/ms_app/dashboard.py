# Dashboard – FemHealth (v6)
# Fix: Navbar ist jetzt IMMER unten sichtbar – Inhalt scrollt dahinter

import sys
import pathlib
import webbrowser
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                             QDialog, QLabel, QVBoxLayout, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QSettings
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

#push benachrichtigungen
class NotificationPopup(QDialog):

    def __init__(self, parent, titel, nachricht):
        super().__init__(parent)

        # Fenster ohne normale Titelleiste
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )

        self.setFixedSize(380, 120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)

        titel_label = QLabel(titel)
        titel_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #6C4A7E;
        """)

        nachricht_label = QLabel(nachricht)
        nachricht_label.setWordWrap(True)
        nachricht_label.setStyleSheet("""
            font-size: 13px;
            color: #403744;
        """)

        layout.addWidget(titel_label)
        layout.addWidget(nachricht_label)

        self.setStyleSheet("""
            QDialog {
                background-color: #F7F0F4;
                border: 2px solid #B59AC4;
                border-radius: 16px;
            }
        """)

        # Nach fünf Sekunden automatisch schließen
        QTimer.singleShot(5000, self.close)

    def showEvent(self, event):
        super().showEvent(event)

        parent = self.parentWidget()

        if parent is not None:
            x = parent.x() + (
                parent.width() - self.width()
            ) // 2

            y = parent.y() + 20

            self.move(x, y)

from wissen_fenster import WissenFenster

class BeratungDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Beratung & Kontakt")
        self.setFixedWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # Überschrift
        titel = QLabel("Beratung & Kontakt")
        titel.setStyleSheet(
            "font-size:20px; font-weight:bold; color:#6C4A7E;"
        )
        layout.addWidget(titel)

        # Untertitel
        untertitel = QLabel(
            "Du bist nicht allein – hier findest du Unterstützung."
        )
        untertitel.setWordWrap(True)
        untertitel.setStyleSheet("font-size:13px; color:#8A7B92;")
        layout.addWidget(untertitel)

        # Kontaktinfos mit anklickbaren Links
        kontakt = QLabel(
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
        kontakt.setWordWrap(True)
        kontakt.setTextFormat(Qt.TextFormat.RichText)
        kontakt.setOpenExternalLinks(True)
        layout.addWidget(kontakt)

        # Notfall-Hinweis (rosa hervorgehoben)
        notfall = QLabel(
            "Im Notfall wende dich an den ärztlichen Notdienst: 116 117"
        )
        notfall.setWordWrap(True)
        notfall.setStyleSheet(
            "font-size:12px; color:#A03050; background:#FBE9EE; "
            "border-radius:10px; padding:10px;"
        )
        layout.addWidget(notfall)

        # Schließen-Button
        btn_schliessen = QPushButton("Schließen")
        btn_schliessen.clicked.connect(self.close)
        btn_schliessen.setStyleSheet(
            "QPushButton {"
            "  background:#6C4A7E; color:#fff; border:none;"
            "  border-radius:12px; padding:10px;"
            "  font-size:14px; font-weight:bold;"
            "}"
            "QPushButton:hover { background:#5A3D6A; }"
        )
        layout.addWidget(btn_schliessen)

        # Gesamt-Stil des Dialogs
        self.setStyleSheet(
            "QDialog {"
            "  background:#F7F0F4;"
            "  border:2px solid #B59AC4;"
            "  border-radius:16px;"
            "}"
        )

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
        dialog = BeratungDialog(self)
        dialog.exec()

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
        self.wissen_fenster = WissenFenster("Endometriose", "Endometriose")
        self.wissen_fenster.show()

    def oeffne_sti(self):
        self.wissen_fenster = WissenFenster("STI & Schutz", "Geschlechtskrankheit")
        self.wissen_fenster.show()

    def oeffne_zyklus(self):
        self.wissen_fenster = WissenFenster("Zyklus & PMS", "Menstruationszyklus")
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

        if not app.property("tracking_reminder_geprueft"):
            app.setProperty("tracking_reminder_geprueft", True)

            QTimer.singleShot(
                1000,
                self.taeglichen_tracking_reminder_pruefen
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

    def zeige_tracking_reminder(self):
        self.tracking_reminder = NotificationPopup(
            self,
            "Täglicher Check-in",
            "Zeit für deinen täglichen Eintrag. "
            "Öffne den Tracking-Bereich und halte dein heutiges Befinden fest."
        )

        self.tracking_reminder.show()

    def taeglichen_tracking_reminder_pruefen(self):
        heute = date.today().isoformat()

        settings = QSettings(
            "FemHealth",
            "FemHealthApp"
        )

        # Für jeden Account ein eigener Speicherwert
        schluessel = f"letzter_tracking_reminder_{self.user_id}"

        letztes_datum = settings.value(
            schluessel,
            ""
        )

        if letztes_datum == heute:
            return

        self.zeige_tracking_reminder()

        settings.setValue(
            schluessel,
            heute
        )











# ═══════════════════════════════════════════════════════════════
# Programm starten
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
