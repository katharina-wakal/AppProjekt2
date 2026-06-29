# Analyse-Seite – zeigt Zyklusstatistiken, Prognosen, Trends, Insights und Diagramme

import sys
import pathlib

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
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

# FemHealth Farben
PINK_HAUPT  = "#C2185B"
PINK_HELL   = "#F48FB1"
PINK_BG     = "#FFF5F8"
ORANGE_WARN = "#FF7043"
GRAU_RASTER = "#EEEEEE"


class AnalyseWindow(QMainWindow):

    def __init__(self, daten=None, user_id=None):
        super().__init__()

        self.user_id = user_id
        self.daten = daten if daten is not None else {}

        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/analyse.ui", self)

        self.buttons_verbinden()
        self.anzeige_befuellen()

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

        # Symptom-Analyse wird nicht mehr angezeigt
        self.symptom_elemente_entfernen()

        self.freischalt_button_setzen(freigeschaltet)

        zyklus_dauer  = self.zyklus_dauer_berechnen()
        schwankung    = self.schwankung_berechnen()
        periode_dauer = self.periode_dauer_berechnen()
        score         = self.score_berechnen(zyklus_dauer, schwankung)
        anzahl_zyklen = self.anzahl_zyklen_laden()

        self.statistik_texte_setzen(anzahl_zyklen)
        self.statistik_werte_setzen(zyklus_dauer, schwankung,
                                    periode_dauer, score, anzahl_zyklen)
        self.prognose_anzeigen()

        # Diagramme nur bei freigeschalteten Analysen anzeigen
        if freigeschaltet:
            self.diagramme_anzeigen()

    def symptom_elemente_entfernen(self):
        """Blendet die Symptom-Sektion aus und schiebt den Leerraum weg.

        Die Symptom-Widgets (div3 bis lblKorrelation) belegen y=738–900.
        Alle Elemente darunter werden um genau diesen Abstand nach oben
        verschoben, damit kein Leerblock entsteht.
        """
        symptom_widgets = [
            "div3",
            "lblSekSymptome",
            "cardSymptom1",
            "cardSymptom2",
            "cardSymptom3",
            "lblKorrelation",
        ]

        # Grenzen des Symptom-Blocks bestimmen
        symptom_oben  = self.main_window.div3.y()               # 738
        symptom_unten = (self.main_window.lblKorrelation.y()
                         + self.main_window.lblKorrelation.height())  # 900
        symptom_hoehe = symptom_unten - symptom_oben            # 162

        # Symptom-Widgets ausblenden
        for name in symptom_widgets:
            widget = getattr(self.main_window, name, None)
            if widget is not None:
                widget.hide()

        # Alle sichtbaren Geschwister-Widgets unterhalb des Symptom-Blocks
        # um symptom_hoehe nach oben schieben
        for kind in self.main_window.scrollContents.children():
            if not hasattr(kind, "geometry"):
                continue
            if kind.objectName() in symptom_widgets:
                continue
            geo = kind.geometry()
            if geo.y() > symptom_unten:
                kind.setGeometry(geo.x(), geo.y() - symptom_hoehe,
                                 geo.width(), geo.height())

        # Scroll-Bereich entsprechend verkleinern
        aktuell = self.main_window.scrollContents.height()
        self.main_window.scrollContents.resize(390, aktuell - symptom_hoehe)

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
        self.main_window.lblZyklusDauerWert.setText(str(zyklus_dauer) + " Tage")
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
            self.main_window.lblStatScoreSub.setText("Dein Zyklus ist sehr regelmäßig")
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
            self.main_window.lblStatScoreSub.setText("Stärkere Schwankungen erkannt")
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
        eisprung         = prognose["predicted_ovulation"]
        genauigkeit      = self.genauigkeit_berechnen(len(periodenstarts))

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

    # ── Diagramme / Plots ────────────────────────────────────────────────────

    def diagramme_anzeigen(self):
        """Baut zwei matplotlib-Plots in die bestehenden UI-Cards ein.

        Diagramm 1 (Linienplot) – Zykluslänge der letzten 6 Monate
            → Verlauf mit Datenpunkten, Ausreißer farblich markiert

        Diagramm 2 (Balkenplot) – Vergleich Ø-Zyklus vs. Normalbereich
            → Normalbereich als Bereich (21–35 T), Dein Ø als Marker
        """
        if self.user_id is None:
            return

        zykluslaengen = zykluslaengen_laden(self.user_id)[-6:]

        if len(zykluslaengen) == 0:
            return

        zyklus_avg = round(sum(zykluslaengen) / len(zykluslaengen))

        # ── Diagramm 1: Linienplot in cardTrend ──────────────────────────────

        neue_trend_hoehe     = 210
        alte_trend_unterkante = (self.main_window.cardTrend.y()
                                 + self.main_window.cardTrend.height())  # 726

        canvas_linie = self._linienplot_erstellen(zykluslaengen)
        canvas_linie.setParent(self.main_window.cardTrend)
        self.main_window.lblTrendChart.hide()
        canvas_linie.setGeometry(8, 46, 354, neue_trend_hoehe - 54)
        self.main_window.cardTrend.resize(370, neue_trend_hoehe)
        canvas_linie.show()

        # Alle Elemente unterhalb der alten cardTrend-Unterkante nach unten schieben
        delta_trend = neue_trend_hoehe - self.main_window.cardTrend.height()
        # (height() gibt hier bereits neue_trend_hoehe zurück, deshalb manuell):
        delta_trend = neue_trend_hoehe - 120   # 120 war die Original-Höhe
        self._elemente_verschieben(alte_trend_unterkante, +delta_trend,
                                   ausnahmen=["cardTrend"])

        # ── Diagramm 2: Balkenplot in cardVergleich ───────────────────────────

        neue_vergleich_hoehe    = 120
        alte_vergleich_unterkante = (self.main_window.cardVergleich.y()
                                     + self.main_window.cardVergleich.height())

        canvas_balken = self._balkenplot_erstellen(zyklus_avg)
        canvas_balken.setParent(self.main_window.cardVergleich)
        self.main_window.lblVergleichBar.hide()
        canvas_balken.setGeometry(8, 4, 354, neue_vergleich_hoehe - 8)
        self.main_window.cardVergleich.resize(370, neue_vergleich_hoehe)
        canvas_balken.show()

        delta_vergleich = neue_vergleich_hoehe - 60   # 60 war die Original-Höhe
        self._elemente_verschieben(alte_vergleich_unterkante, +delta_vergleich,
                                   ausnahmen=["cardVergleich"])

        # Scroll-Bereich anpassen
        aktuell = self.main_window.scrollContents.height()
        self.main_window.scrollContents.resize(390,
                                               aktuell + delta_trend + delta_vergleich)

    def _elemente_verschieben(self, ab_y, versatz, ausnahmen=None):
        """Verschiebt alle Kinder von scrollContents mit y > ab_y um versatz Pixel.

        Positiver versatz = nach unten, negativer versatz = nach oben.
        """
        if ausnahmen is None:
            ausnahmen = []

        for kind in self.main_window.scrollContents.children():
            if not hasattr(kind, "geometry"):
                continue
            if kind.objectName() in ausnahmen:
                continue
            geo = kind.geometry()
            if geo.y() > ab_y:
                kind.setGeometry(geo.x(), geo.y() + versatz,
                                 geo.width(), geo.height())

    def _linienplot_erstellen(self, werte):
        """Liniendiagramm: Zykluslänge über die letzten Zyklen.

        - Normalbereich 21–35 Tage als rosa Fläche hinterlegt
        - Punkte außerhalb des Normalbereichs werden orange markiert
        """
        fig = Figure(figsize=(3.54, 1.56), facecolor=PINK_BG)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.set_facecolor(PINK_BG)

        x = list(range(1, len(werte) + 1))

        # Normalbereich als Fläche
        ax.axhspan(21, 35, color=PINK_HELL, alpha=0.25,
                   label="Normalbereich (21–35 T)")

        # Verbindungslinie
        ax.plot(x, werte, color=PINK_HAUPT, linewidth=2, zorder=3)

        # Datenpunkte: innerhalb = pink, Ausreißer = orange
        for xi, yi in zip(x, werte):
            farbe = PINK_HAUPT if 21 <= yi <= 35 else ORANGE_WARN
            ax.scatter(xi, yi, color=farbe, s=45, zorder=4)

        ax.set_xticks(x)
        ax.set_xticklabels(["Z" + str(i) for i in x], fontsize=8)
        ax.set_ylabel("Tage", fontsize=8)
        ax.tick_params(labelsize=8)
        ax.grid(axis="y", color=GRAU_RASTER, linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Legende nur wenn Ausreißer vorhanden
        if any(w < 21 or w > 35 for w in werte):
            ax.scatter([], [], color=ORANGE_WARN, s=45, label="Ausreißer")
            ax.legend(fontsize=7, loc="upper right", framealpha=0.7)

        fig.tight_layout(pad=0.4)
        return canvas

    def _balkenplot_erstellen(self, zyklus_avg):
        """Balkendiagramm: Dein Ø-Zyklus im Vergleich zum Normalbereich.

        - Normalbereich: hellrosa Bereich von 21 bis 35 Tage
        - Dein Ø: schmaler Marker am tatsächlichen Durchschnittswert
          (kein Balken ab 0, sondern eine farbige Markierung an der richtigen Stelle)
        """
        fig = Figure(figsize=(3.54, 1.12), facecolor=PINK_BG)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.set_facecolor(PINK_BG)

        # Normalbereich: Balken von 21 bis 35 Tage
        ax.barh(["Normalbereich"], [35 - 21], left=21,
                color=PINK_HELL, height=0.5, alpha=0.85)

        # Dein Ø: schmaler Marker (2 Tage breit) am Durchschnittswert
        # → startet NICHT bei 0, sondern ist ein Bereich um den Mittelwert
        avg_farbe = PINK_HAUPT if 21 <= zyklus_avg <= 35 else ORANGE_WARN
        ax.barh(["Dein Ø"], [3], left=zyklus_avg - 1.5,
                color=avg_farbe, height=0.5)

        # Wert als Beschriftung
        ax.text(zyklus_avg + 2, 1,
                str(zyklus_avg) + " T",
                va="center", fontsize=8, color=avg_farbe, fontweight="bold")

        # Begrenzungslinien Normalbereich
        ax.axvline(21, color="#BDBDBD", linewidth=0.9, linestyle="--")
        ax.axvline(35, color="#BDBDBD", linewidth=0.9, linestyle="--")

        ax.set_xlim(10, 45)
        ax.set_xlabel("Tage", fontsize=8)
        ax.tick_params(labelsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", color=GRAU_RASTER, linewidth=0.8)

        fig.tight_layout(pad=0.4)
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
            + " Punkte gesammelt.\n\nMöchtest du 60 Punkte einlösen und die "
            + "erweiterten Analysen dauerhaft freischalten?",
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
