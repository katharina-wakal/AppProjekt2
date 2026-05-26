# Dashboard Seite – Hauptansicht nach dem Login

import sys
import pathlib
from datetime import date
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox


class DashboardWindow(QMainWindow):

    def __init__(self, vorname="Emma"):
        super().__init__()

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/femhealth_dashboard_v5(3).ui", self)

        # Nutzername merken (kommt später aus der Datenbank)
        self.vorname = vorname

        # Beim Start alles aufbauen
        self.begruessung_setzen()
        self.zyklus_info_setzen()
        self.news_karten_verbinden()

        # Buttons mit Funktionen verbinden
        self.main_window.btnHelp.clicked.connect(self.on_hilfe)

        # Navigation verbinden
        self.main_window.navHome.clicked.connect(self.on_nav_home)
        self.main_window.navKalender.clicked.connect(self.on_nav_kalender)
        self.main_window.navTracken.clicked.connect(self.on_nav_tracken)
        self.main_window.navArzt.clicked.connect(self.on_nav_arzt)
        self.main_window.navAnalyse.clicked.connect(self.on_nav_analyse)

        # Filter-Chips verbinden (Kategorien für Newsletter)
        self.main_window.chipAlle.clicked.connect(self.on_filter_alle)
        self.main_window.chipEndo.clicked.connect(self.on_filter_endo)
        self.main_window.chipSTI.clicked.connect(self.on_filter_sti)
        self.main_window.chipZyklus.clicked.connect(self.on_filter_zyklus)

    # ── Aufbau beim Start ─────────────────────────────────────────────────────

    def begruessung_setzen(self):
        # Tageszeit auslesen und passende Begrüßung wählen
        stunde = date.today().timetuple().tm_yday  # Platzhalter: TODO echte Uhrzeit
        # TODO: datetime.now().hour verwenden wenn Uhrzeit gebraucht wird
        begruessung = "Guten Tag"

        # Begrüßungs-Label aktualisieren
        self.main_window.lblGreeting.setText(begruessung + ", " + self.vorname + " 👋")

    def zyklus_info_setzen(self):
        # TODO: Zyklusdaten aus Datenbank laden
        # Beispieldaten vorerst fest eingetragen
        zyklusphase   = "Ovulationsphase 🌸"
        tag_aktuell   = 14
        tag_gesamt    = 28
        tage_bis_mens = 14
        tipp          = "💡 Gute Zeit für Sport & soziale Aktivitäten"

        # Labels befüllen
        self.main_window.lblCyclePhase.setText(zyklusphase)
        self.main_window.lblCycleDay.setText(
            "Tag " + str(tag_aktuell) + " von " + str(tag_gesamt)
        )
        self.main_window.lblDaysInfo.setText(
            "Nächste Periode in ca. " + str(tage_bis_mens) + " Tagen"
        )
        self.main_window.lblTip.setText(tipp)

    def news_karten_verbinden(self):
        # Jede News-Karte bekommt einen Klick-Handler
        # TODO: Artikelinhalt aus Datenbank oder API laden
        self.main_window.newsCard1.mousePressEvent = lambda e: self.on_artikel_oeffnen("Endometriose – Früherkennung")
        self.main_window.newsCard2.mousePressEvent = lambda e: self.on_artikel_oeffnen("STI & Schutz")
        self.main_window.newsCard3.mousePressEvent = lambda e: self.on_artikel_oeffnen("PMS vs. PMDS")

    # ── Slots: Navigation ─────────────────────────────────────────────────────

    def on_nav_home(self):
        # Bereits auf dem Startbildschirm – nichts tun
        print("Navigation: Home")

    def on_nav_kalender(self):
        # TODO: KalenderWindow öffnen
        # from kalender_femhealth import KalenderWindow
        print("Navigation: Kalender")
        QMessageBox.information(self, "Kalender", "Kalender-Ansicht kommt noch!")

    def on_nav_tracken(self):
        # Eintrag-Fenster öffnen (Symptome, Blutung, Gefühle eintragen)
        # TODO: from eintrag_femhealth import EintragWindow
        print("Navigation: Tracken")
        QMessageBox.information(self, "Tracken", "Tagebuch-Eintrag kommt noch!")

    def on_nav_arzt(self):
        # Arzttermin-Fenster öffnen
        # TODO: from arzttermin_femhealth import ArztterminWindow
        print("Navigation: Arzttermin")
        QMessageBox.information(self, "Arzttermine", "Arzttermin-Verwaltung kommt noch!")

    def on_nav_analyse(self):
        # TODO: AnalyseWindow öffnen (Auswertung & Graphen)
        print("Navigation: Analyse")
        QMessageBox.information(self, "Analyse", "Analyse-Ansicht kommt noch!")

    # ── Slots: Sonstige Buttons ───────────────────────────────────────────────

    def on_hilfe(self):
        # Hilfe / Einstellungen anzeigen
        QMessageBox.information(
            self,
            "Hilfe & Kontakt",
            "Bei Fragen: support@femhealth.de\nVersion 1.0"
        )

    def on_artikel_oeffnen(self, titel):
        # Artikel aufrufen – TODO: echten Artikel-Viewer öffnen
        print("Artikel geöffnet: " + titel)
        QMessageBox.information(self, "Artikel", "'" + titel + "' wird geladen...")

    # ── Slots: Filter-Chips ───────────────────────────────────────────────────

    def on_filter_alle(self):
        # Alle Artikel anzeigen – TODO: Sichtbarkeit der News-Karten steuern
        print("Filter: Alle")
        self.main_window.newsCard1.setVisible(True)
        self.main_window.newsCard2.setVisible(True)
        self.main_window.newsCard3.setVisible(True)

    def on_filter_endo(self):
        # Nur Endometriose-Artikel anzeigen
        print("Filter: Endometriose")
        self.main_window.newsCard1.setVisible(True)
        self.main_window.newsCard2.setVisible(False)
        self.main_window.newsCard3.setVisible(False)

    def on_filter_sti(self):
        # Nur STI-Artikel anzeigen
        print("Filter: STI")
        self.main_window.newsCard1.setVisible(False)
        self.main_window.newsCard2.setVisible(True)
        self.main_window.newsCard3.setVisible(False)

    def on_filter_zyklus(self):
        # Nur Zyklus-Artikel anzeigen
        print("Filter: Zyklus")
        self.main_window.newsCard1.setVisible(False)
        self.main_window.newsCard2.setVisible(False)
        self.main_window.newsCard3.setVisible(True)

    # ── Hilfsmethode ─────────────────────────────────────────────────────────

    def zeige_fehler(self, text):
        QMessageBox.warning(self, "Fehler", text)


# ── Programm starten ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow(vorname="Emma")
    window.show()
    sys.exit(app.exec())
