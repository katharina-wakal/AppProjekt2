# Analyse-Seite – zeigt Zyklusstatistiken, Prognosen, Trends und Insights

import sys
import pathlib
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox


class AnalyseWindow(QMainWindow):

    def __init__(self, daten=None):
        super().__init__()

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/analyse_femhealth.ui", self)

        # Eingetragene Daten aus anderen Fenstern übernehmen (optional)
        # daten = Dictionary mit Einträgen aus Eintrag- und Arzttermin-Fenster
        self.daten = daten if daten is not None else {}

        # Anzeige mit Beispieldaten befüllen
        # TODO: echte Berechnungen aus Datenbank einfügen
        self.anzeige_befuellen()

        # ── Buttons mit Funktionen verbinden ──────────────────────────────────

        self.main_window.btnBack.clicked.connect(self.on_zurueck)
        self.main_window.btnFreischalten.clicked.connect(self.on_freischalten)
        self.main_window.btnMehrPeriode.clicked.connect(self.on_mehr_periode)
        self.main_window.btnMehrTrend.clicked.connect(self.on_mehr_trend)
        self.main_window.btnMehrInsights.clicked.connect(self.on_mehr_insights)

        # Bottom-Navigation
        self.main_window.navHome.clicked.connect(self.on_nav_home)
        self.main_window.navKalender.clicked.connect(self.on_nav_kalender)
        self.main_window.navTrackenMain.clicked.connect(self.on_nav_eintrag)
        self.main_window.navArzt.clicked.connect(self.on_nav_arzt)
        self.main_window.navAnalyse.clicked.connect(self.on_nav_analyse)

    # ── Anzeige befüllen ──────────────────────────────────────────────────────

    def anzeige_befuellen(self):
        # Zyklusstatistiken berechnen und anzeigen
        # TODO: Werte aus Datenbank berechnen statt Beispielwerte
        zyklus_dauer  = self.zyklus_dauer_berechnen()
        schwankung    = self.schwankung_berechnen()
        periode_dauer = self.periode_dauer_berechnen()
        score         = self.score_berechnen(zyklus_dauer, schwankung)

        # Werte in UI eintragen
        self.main_window.lblZyklusDauerWert.setText(str(zyklus_dauer) + " Tage")
        self.main_window.lblSchwankungWert.setText("±" + str(schwankung) + " Tage")
        self.main_window.lblPeriodeDauerWert.setText(str(periode_dauer) + " Tage")
        self.main_window.lblScoreWert.setText(str(score) + " / 100")
        self.main_window.lblStatScore.setText(str(score) + " / 100")

        # Score-Badge und Hauptkarte anpassen
        if score >= 80:
            self.main_window.badgeStabil.setText("stabil")
            self.main_window.lblStatScoreSub.setText("Dein Zyklus ist sehr regelmäßig")
            self.main_window.lblStatTrend.setText("💡 Weiter so – sehr gute Regelmäßigkeit!")
        elif score >= 60:
            self.main_window.badgeStabil.setText("leicht unreg.")
            self.main_window.lblStatScoreSub.setText("Leicht unregelmäßig")
            self.main_window.lblStatTrend.setText("💡 Dein Zyklus wird stabiler – weiter so!")
        else:
            self.main_window.badgeStabil.setText("stark schwankend")
            self.main_window.lblStatScoreSub.setText("Stärkere Schwankungen erkannt")
            self.main_window.lblStatTrend.setText("💡 Bitte beobachte deine Schwankungen weiter.")

        # Trend-Text anpassen je nach Schwankung
        if schwankung <= 2:
            self.main_window.lblTrendText.setText("Dein Zyklus wird stabiler  📈")
        elif schwankung <= 4:
            self.main_window.lblTrendText.setText("Leichte Schwankungen erkannt  📊")
        else:
            self.main_window.lblTrendText.setText("Schwankungen nehmen zu  ⚠️")

        # Prognosen eintragen
        # TODO: Datum aus letzter Periode berechnen
        self.main_window.lblPrognoseWert.setText(
            "Voraussichtlich in 5 Tagen · 31. Mai"
        )
        self.main_window.lblPrognoseGenau.setText("Genauigkeit: 82 %")
        self.main_window.lblEissprungWert.setText(
            "Voraussichtlich 10.–15. Juni"
        )
        self.main_window.lblEissprungInfo.setText("Eissprung: ca. 12. Juni")

        print("Analyse geladen – Score: " + str(score))

    # ── Berechnungs-Hilfsmethoden ─────────────────────────────────────────────

    def zyklus_dauer_berechnen(self):
        # Gibt die durchschnittliche Zyklusdauer zurück
        # TODO: Aus Datenbankeinträgen berechnen
        beispiel_zyklen = [27, 28, 29, 28, 27, 28]
        summe = 0
        for laenge in beispiel_zyklen:
            summe = summe + laenge
        return summe // len(beispiel_zyklen)

    def schwankung_berechnen(self):
        # Gibt die Schwankungsbreite zurück (Max minus Min, halbiert)
        # TODO: Aus Datenbankeinträgen berechnen
        beispiel_zyklen = [27, 28, 29, 28, 27, 28]
        maximum = max(beispiel_zyklen)
        minimum = min(beispiel_zyklen)
        return (maximum - minimum) // 2

    def periode_dauer_berechnen(self):
        # Gibt die durchschnittliche Periodendauer zurück
        # TODO: Aus Datenbankeinträgen berechnen
        beispiel_perioden = [4, 4, 5, 3, 4, 4]
        summe = 0
        for dauer in beispiel_perioden:
            summe = summe + dauer
        return summe // len(beispiel_perioden)

    def score_berechnen(self, zyklus_dauer, schwankung):
        # Berechnet den Zyklus-Regelmäßigkeits-Score (0–100)
        # Je weniger Schwankung, desto höher der Score
        score = 100

        # Punkte abziehen für Schwankung (je ±1 Tag = -10 Punkte)
        score = score - (schwankung * 10)

        # Punkte abziehen wenn außerhalb Normalbereich 21–35 Tage
        if zyklus_dauer < 21 or zyklus_dauer > 35:
            score = score - 20

        # Score begrenzen auf 0–100
        if score < 0:
            score = 0
        if score > 100:
            score = 100

        return score

    # ── Slots ─────────────────────────────────────────────────────────────────

    def on_zurueck(self):
        # Zurück zum Dashboard
        self.close()

    def on_freischalten(self):
        # Erweiterte Analysen freischalten (TODO: Kauf-Flow)
        QMessageBox.information(
            self,
            "🔒 Analysen freischalten",
            "Hier würde der Kauf-Prozess für erweiterte Analysen geöffnet."
        )

    def on_mehr_periode(self):
        # Detailansicht Periodenstärke öffnen (TODO)
        print("Mehr Infos: Periodenstärke")

    def on_mehr_trend(self):
        # Detailansicht Trend-Grafik öffnen (TODO)
        print("Mehr Infos: Trend-Verlauf")

    def on_mehr_insights(self):
        # Detailansicht Insights öffnen (TODO)
        print("Mehr Infos: Insights")

    # ── Navigation ────────────────────────────────────────────────────────────

    def on_nav_home(self):
        # TODO: Dashboard öffnen
        print("Navigation: Start")
        self.close()

    def on_nav_kalender(self):
        # TODO: Kalender-Ansicht öffnen
        print("Navigation: Kalender")

    def on_nav_eintrag(self):
        # TODO: Eintrag-Fenster öffnen
        print("Navigation: Eintrag")

    def on_nav_arzt(self):
        # TODO: Arzttermin-Fenster öffnen
        print("Navigation: Arzt")

    def on_nav_analyse(self):
        # Bereits auf der Analyse-Seite
        print("Navigation: Analyse (aktiv)")


# ── Programm starten ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyseWindow()
    window.show()
    sys.exit(app.exec())
