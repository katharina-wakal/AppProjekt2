# Analyse-Seite – zeigt Zyklusstatistiken, Prognosen, Trends, Insights und Diagramme

import sys
import pathlib

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QWidget,
    QVBoxLayout
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from database import (
    zykluslaengen_laden,
    perioden_dauer_laden,
    periodenstarts_laden,
    credit_points_laden,
    erweiterte_analysen_freischalten,
    analysen_freigeschaltet_laden
)

from calculation import calculate_cycle_prediction
from kalender import KalenderWindow
from eintrag import EintragWindow
from arzttermin import ArztterminWindow


class AnalyseWindow(QMainWindow):

    def __init__(self, daten=None, user_id=None):
        super().__init__()

        self.user_id = user_id
        self.daten = daten if daten is not None else {}

        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/analyse.ui", self)

        self.buttons_verbinden()
        self.anzeige_befuellen()
        self.diagramme_anzeigen()

    # ── Grundaufbau ──────────────────────────────────────────────────────────

    def buttons_verbinden(self):
        self.main_window.btnBack.clicked.connect(self.on_zurueck)
        self.main_window.btnFreischalten.clicked.connect(self.on_freischalten)
        self.main_window.btnMehrPeriode.clicked.connect(self.on_mehr_periode)
        self.main_window.btnMehrTrend.clicked.connect(self.on_mehr_trend)
        self.main_window.btnMehrInsights.clicked.connect(self.on_mehr_insights)

        self.main_window.navHome.clicked.connect(self.on_nav_home)
        self.main_window.navKalender.clicked.connect(self.on_nav_kalender)
        self.main_window.navTrackenMain.clicked.connect(self.on_nav_eintrag)
        self.main_window.navArzt.clicked.connect(self.on_nav_arzt)
        self.main_window.navAnalyse.clicked.connect(self.on_nav_analyse)

    # ── Anzeige befüllen ─────────────────────────────────────────────────────

    def anzeige_befuellen(self):
        freigeschaltet = False

        if self.user_id is not None:
            freigeschaltet = analysen_freigeschaltet_laden(self.user_id)

        self.symptom_analyse_anzeigen(freigeschaltet)
        self.freischalt_button_setzen(freigeschaltet)

        zyklus_dauer = self.zyklus_dauer_berechnen()
        schwankung = self.schwankung_berechnen()
        periode_dauer = self.periode_dauer_berechnen()
        score = self.score_berechnen(zyklus_dauer, schwankung)
        anzahl_zyklen = self.anzahl_zyklen_laden()

        self.statistik_texte_setzen(anzahl_zyklen)
        self.statistik_werte_setzen(
            zyklus_dauer,
            schwankung,
            periode_dauer,
            score,
            anzahl_zyklen
        )
        self.prognose_anzeigen()

    def freischalt_button_setzen(self, freigeschaltet):
        if freigeschaltet:
            self.main_window.btnFreischalten.setText(
                "🔓 Erweiterte Analysen freigeschaltet"
            )
        else:
            self.main_window.btnFreischalten.setText(
                "🔒 Weitere Analysen freischalten"
            )

    def anzahl_zyklen_laden(self):
        if self.user_id is None:
            return 0

        return len(zykluslaengen_laden(self.user_id))

    def statistik_texte_setzen(self, anzahl_zyklen):
        if anzahl_zyklen == 0:
            self.main_window.lblStatSubInfo.setText("Noch nicht genug Zyklusdaten")
            self.main_window.lblStatistikSub.setText(
                "Erste Werte basieren auf Standardannahmen"
            )
        else:
            self.main_window.lblStatSubInfo.setText(
                "Basierend auf " + str(anzahl_zyklen) + " Zyklen"
            )
            self.main_window.lblStatistikSub.setText(
                "Durchschnittswerte deiner letzten "
                + str(min(anzahl_zyklen, 6))
                + " Zyklen"
            )

    def statistik_werte_setzen(self, zyklus_dauer, schwankung,
                               periode_dauer, score, anzahl_zyklen):
        self.main_window.lblZyklusDauerWert.setText(
            str(zyklus_dauer) + " Tage"
        )

        self.schwankungs_badge_setzen(schwankung)
        self.periodendauer_setzen(periode_dauer)
        self.score_setzen(score, anzahl_zyklen)
        self.trend_text_setzen(schwankung)

    def schwankungs_badge_setzen(self, schwankung):
        if schwankung <= 2:
            self.main_window.badgeUntypisch.setText("✓ stabil")
        elif schwankung <= 5:
            self.main_window.badgeUntypisch.setText("~ normal")
        else:
            self.main_window.badgeUntypisch.setText("⚠ unregelmäßig")

    def periodendauer_setzen(self, periode_dauer):
        if periode_dauer == 1:
            self.main_window.lblPeriodeDauerWert.setText("1 Tag")
        else:
            self.main_window.lblPeriodeDauerWert.setText(
                str(periode_dauer) + " Tage"
            )

    def score_setzen(self, score, anzahl_zyklen):
        if anzahl_zyklen == 0:
            self.main_window.lblScoreWert.setText("-")
            self.main_window.lblStatScore.setText("-")
            self.main_window.badgeStabil.setText("neu")
            self.main_window.lblStatScoreSub.setText("Noch nicht aussagekräftig")
            self.main_window.lblStatTrend.setText(
                "💡 Trage weitere Perioden ein, damit die Analyse genauer wird."
            )
            return

        self.main_window.lblScoreWert.setText(str(score) + " / 100")
        self.main_window.lblStatScore.setText(str(score) + " / 100")

        if score >= 80:
            self.main_window.badgeStabil.setText("stabil")
            self.main_window.lblStatScoreSub.setText(
                "Dein Zyklus ist sehr regelmäßig"
            )
            self.main_window.lblStatTrend.setText(
                "💡 Weiter so – sehr gute Regelmäßigkeit!"
            )
        elif score >= 60:
            self.main_window.badgeStabil.setText("leicht unreg.")
            self.main_window.lblStatScoreSub.setText("Leicht unregelmäßig")
            self.main_window.lblStatTrend.setText(
                "💡 Dein Zyklus wird stabiler – weiter so!"
            )
        else:
            self.main_window.badgeStabil.setText("stark schwankend")
            self.main_window.lblStatScoreSub.setText(
                "Stärkere Schwankungen erkannt"
            )
            self.main_window.lblStatTrend.setText(
                "💡 Bitte beobachte deine Schwankungen weiter."
            )

    def trend_text_setzen(self, schwankung):
        if schwankung <= 2:
            self.main_window.lblTrendText.setText("Dein Zyklus wird stabiler  📈")
        elif schwankung <= 4:
            self.main_window.lblTrendText.setText("Leichte Schwankungen erkannt  📊")
        else:
            self.main_window.lblTrendText.setText("Schwankungen nehmen zu  ⚠️")

    def prognose_anzeigen(self):
        if self.user_id is None:
            self.prognose_leer_setzen("Noch keine Prognose verfügbar")
            return

        periodenstarts = periodenstarts_laden(self.user_id)

        if len(periodenstarts) == 0:
            self.prognose_leer_setzen("Noch keine Periode eingetragen")
            return

        try:
            prognose = calculate_cycle_prediction(periodenstarts)
        except Exception:
            self.prognose_leer_setzen("Prognose konnte nicht berechnet werden")
            return

        naechste_periode = prognose["predicted_period_start"]
        eisprung = prognose["predicted_ovulation"]
        genauigkeit = self.genauigkeit_berechnen(len(periodenstarts))

        self.main_window.lblPrognoseWert.setText(
            "Voraussichtlich am " + naechste_periode.strftime("%d.%m.%Y")
        )
        self.main_window.lblPrognoseGenau.setText(
            "Genauigkeit: " + str(genauigkeit) + " %"
        )
        self.main_window.lblEissprungWert.setText(
            "Fruchtbare Phase ca. " + eisprung.strftime("%d.%m.%Y")
        )
        self.main_window.lblEissprungInfo.setText(
            "Eisprung: ca. " + eisprung.strftime("%d.%m.%Y")
        )

    def prognose_leer_setzen(self, text):
        self.main_window.lblPrognoseWert.setText(text)
        self.main_window.lblPrognoseGenau.setText("Genauigkeit: -")
        self.main_window.lblEissprungWert.setText("Noch keine Eisprung-Prognose")
        self.main_window.lblEissprungInfo.setText("Eisprung: -")

    def genauigkeit_berechnen(self, anzahl_periodenstarts):
        if anzahl_periodenstarts == 1:
            return 50
        if anzahl_periodenstarts == 2:
            return 65
        if anzahl_periodenstarts <= 4:
            return 75
        return 85

    def symptom_analyse_anzeigen(self, sichtbar):
        symptom_elemente = [
            self.main_window.lblSekSymptome,
            self.main_window.cardSymptom1,
            self.main_window.cardSymptom2,
            self.main_window.cardSymptom3,
            self.main_window.lblKorrelation
        ]

        for element in symptom_elemente:
            element.setVisible(sichtbar)

    # ── Diagramme / Plots ────────────────────────────────────────────────────

    def diagramme_anzeigen(self):
        if self.user_id is None:
            return

        zykluslaengen = zykluslaengen_laden(self.user_id)[-6:]
        perioden_dauern = perioden_dauer_laden(self.user_id)[-6:]

        if len(zykluslaengen) == 0 and len(perioden_dauern) == 0:
            return

        self.diagramm_container = QWidget(self)
        self.diagramm_container.setGeometry(24, 620, 340, 360)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.diagramm_container.setLayout(layout)

        if len(zykluslaengen) > 0:
            canvas_zyklus = self.liniendiagramm_erstellen(
                zykluslaengen,
                "Zykluslängen",
                "Zyklus",
                "Tage"
            )
            layout.addWidget(canvas_zyklus)

        if len(perioden_dauern) > 0:
            canvas_periode = self.balkendiagramm_erstellen(
                perioden_dauern,
                "Periodendauer",
                "Periode",
                "Tage"
            )
            layout.addWidget(canvas_periode)

        self.diagramm_container.show()

    def liniendiagramm_erstellen(self, werte, titel, x_label, y_label):
        figure = Figure(figsize=(4, 2.2))
        canvas = FigureCanvas(figure)
        achse = figure.add_subplot(111)

        x_werte = list(range(1, len(werte) + 1))

        achse.plot(x_werte, werte, marker="o")
        achse.set_title(titel)
        achse.set_xlabel(x_label)
        achse.set_ylabel(y_label)
        achse.grid(True)
        figure.tight_layout()

        return canvas

    def balkendiagramm_erstellen(self, werte, titel, x_label, y_label):
        figure = Figure(figsize=(4, 2.2))
        canvas = FigureCanvas(figure)
        achse = figure.add_subplot(111)

        x_werte = list(range(1, len(werte) + 1))

        achse.bar(x_werte, werte)
        achse.set_title(titel)
        achse.set_xlabel(x_label)
        achse.set_ylabel(y_label)
        achse.grid(True)
        figure.tight_layout()

        return canvas

    # ── Berechnungs-Hilfsmethoden ────────────────────────────────────────────

    def zyklus_dauer_berechnen(self):
        if self.user_id is None:
            return 28

        zykluslaengen = zykluslaengen_laden(self.user_id)

        if len(zykluslaengen) == 0:
            return 28

        letzte_zyklen = zykluslaengen[-6:]
        return round(sum(letzte_zyklen) / len(letzte_zyklen))

    def schwankung_berechnen(self):
        if self.user_id is None:
            return 0

        zykluslaengen = zykluslaengen_laden(self.user_id)

        if len(zykluslaengen) == 0:
            return 0

        letzte_zyklen = zykluslaengen[-6:]
        return (max(letzte_zyklen) - min(letzte_zyklen)) // 2

    def periode_dauer_berechnen(self):
        if self.user_id is None:
            return 0

        perioden_dauern = perioden_dauer_laden(self.user_id)

        if len(perioden_dauern) == 0:
            return 0

        letzte_perioden = perioden_dauern[-6:]
        return round(sum(letzte_perioden) / len(letzte_perioden))

    def score_berechnen(self, zyklus_dauer, schwankung):
        score = 100
        score = score - (schwankung * 10)

        if zyklus_dauer < 21 or zyklus_dauer > 35:
            score = score - 20

        if score < 0:
            score = 0
        if score > 100:
            score = 100

        return score

    # ── Slots ────────────────────────────────────────────────────────────────

    def on_zurueck(self):
        from dashboard import DashboardWindow

        self.dashboard = DashboardWindow(user_id=self.user_id)
        self.dashboard.show()
        self.close()

    def on_freischalten(self):
        if self.user_id is None:
            QMessageBox.warning(self, "Fehler", "Es ist kein Benutzer angemeldet.")
            return

        bereits_freigeschaltet = analysen_freigeschaltet_laden(self.user_id)

        if bereits_freigeschaltet:
            QMessageBox.information(
                self,
                "🔓 Bereits freigeschaltet",
                "Die erweiterten Analysen sind für deinen Account bereits freigeschaltet."
            )
            return

        credit_points = credit_points_laden(self.user_id)

        if credit_points < 60:
            fehlende_punkte = 60 - credit_points
            QMessageBox.information(
                self,
                "🔒 Analysen freischalten",
                "Dein aktueller Punktestand: "
                + str(credit_points)
                + " / 60 Punkte\n\nDir fehlen noch "
                + str(fehlende_punkte)
                + " Punkte, um die erweiterten Analysen freizuschalten."
            )
            return

        antwort = QMessageBox.question(
            self,
            "🔓 Analysen freischalten",
            "Du hast "
            + str(credit_points)
            + " Punkte gesammelt.\n\nMöchtest du 60 Punkte einlösen und die erweiterten Analysen dauerhaft freischalten?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if antwort != QMessageBox.StandardButton.Yes:
            return

        erfolgreich = erweiterte_analysen_freischalten(self.user_id)

        if erfolgreich:
            neuer_punktestand = credit_points_laden(self.user_id)
            QMessageBox.information(
                self,
                "🎉 Freigeschaltet",
                "Die erweiterten Analysen wurden erfolgreich freigeschaltet!\n\n"
                + "Dein neuer Punktestand: "
                + str(neuer_punktestand)
                + " Punkte"
            )
            self.anzeige_befuellen()
        else:
            QMessageBox.warning(
                self,
                "Freischaltung fehlgeschlagen",
                "Die erweiterten Analysen konnten nicht freigeschaltet werden."
            )

    def on_mehr_periode(self):
        print("Mehr Infos: Periodenstärke")

    def on_mehr_trend(self):
        print("Mehr Infos: Trend-Verlauf")

    def on_mehr_insights(self):
        print("Mehr Infos: Insights")

    # ── Navigation ───────────────────────────────────────────────────────────

    def on_nav_home(self):
        from dashboard import DashboardWindow

        self.dashboard = DashboardWindow(user_id=self.user_id)
        self.dashboard.show()
        self.close()

    def on_nav_kalender(self):
        self.kalender = KalenderWindow(user_id=self.user_id)
        self.kalender.show()
        self.close()

    def on_nav_eintrag(self):
        self.eintrag = EintragWindow(user_id=self.user_id)
        self.eintrag.show()
        self.close()

    def on_nav_arzt(self):
        self.arzt = ArztterminWindow(user_id=self.user_id)
        self.arzt.show()
        self.close()

    def on_nav_analyse(self):
        print("Analyse bereits geöffnet")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyseWindow()
    window.show()
    sys.exit(app.exec())
