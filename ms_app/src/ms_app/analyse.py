# Analyse-Seite – zeigt Zyklusstatistiken, Prognosen, Trends & Insights

import sys
import pathlib
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from database import (zykluslaengen_laden, perioden_dauer_laden,
                      periodenstarts_laden, credit_points_laden,
                      erweiterte_analysen_freischalten, analysen_freigeschaltet_laden)
from calculation import calculate_cycle_prediction
from kalender import KalenderWindow
from eintrag import EintragWindow
from arzttermin import ArztterminWindow

class AnalyseWindow(QMainWindow):

    def __init__(self, daten=None, user_id=None):

        super().__init__()
        self.user_id = user_id

        # .ui-Datei laden
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/analyse.ui", self)

        # Eingetragene Daten aus anderen Fenstern übernehmen (optional)
        # daten = Dictionary mit Einträgen aus Eintrag- und Arzttermin-Fenster
        self.daten = daten if daten is not None else {}

        # Anzeige mit echten Nutzerdaten befüllen
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
        # Status der erweiterten Analysen prüfen
        if self.user_id is not None:
            freigeschaltet = analysen_freigeschaltet_laden(
                self.user_id
            )
        else:
            freigeschaltet = False

        #Symptom-Analyse nur nach Freischaltung anzeigen
        self.symptom_analyse_anzeigen(freigeschaltet)

        if freigeschaltet:
            self.main_window.btnFreischalten.setText(
                "🔓 Erweiterte Analysen freigeschaltet"
            )
        else:
            self.main_window.btnFreischalten.setText(
                "🔒 Weitere Analysen freischalten"
            )

        # Credit Points laden
        if self.user_id is None:
            credit_points = 0
        else:
            credit_points = credit_points_laden(self.user_id)

        # Zyklusstatistiken berechnen und anzeigen
        # Zyklusstatistiken aus gespeicherten Nutzerdaten berechnen
        zyklus_dauer  = self.zyklus_dauer_berechnen()
        schwankung    = self.schwankung_berechnen()
        periode_dauer = self.periode_dauer_berechnen()
        score         = self.score_berechnen(zyklus_dauer, schwankung)

        anzahl_zyklen = 0

        if self.user_id is not None:
            anzahl_zyklen = len(zykluslaengen_laden(self.user_id))

        if anzahl_zyklen == 0:
            self.main_window.lblStatSubInfo.setText("Noch nicht genug Zyklusdaten")
            self.main_window.lblStatistikSub.setText("Erste Werte basieren auf Standardannahmen")
        else:
            self.main_window.lblStatSubInfo.setText(
                "Basierend auf " + str(anzahl_zyklen) + " Zyklen"
            )
            self.main_window.lblStatistikSub.setText(
                "Durchschnittswerte deiner letzten " + str(min(anzahl_zyklen, 6)) + " Zyklen"
            )

        # Werte in UI eintragen
        # Werte in UI eintragen
        self.main_window.lblZyklusDauerWert.setText(str(zyklus_dauer) + " Tage")

        # Badge für Zyklus-Schwankung anpassen
        if schwankung <= 2:
            self.main_window.badgeUntypisch.setText("✓ stabil")
        elif schwankung <= 5:
            self.main_window.badgeUntypisch.setText("~ normal")
        else:
            self.main_window.badgeUntypisch.setText("⚠ unregelmäßig")


        #Periodendauer grammatikalisch richtig ausgeben
        if periode_dauer == 1:
            self.main_window.lblPeriodeDauerWert.setText("1 Tag")
        else:
            self.main_window.lblPeriodeDauerWert.setText(
                str(periode_dauer) + " Tage"
            )

        if anzahl_zyklen == 0:
            self.main_window.lblScoreWert.setText("-")
            self.main_window.lblStatScore.setText("-")
        else:
            self.main_window.lblScoreWert.setText(str(score) + " / 100")
            self.main_window.lblStatScore.setText(str(score) + " / 100")

        # Score-Badge und Hauptkarte anpassen
        # Score-Badge und Hauptkarte anpassen
        if anzahl_zyklen == 0:
            self.main_window.badgeStabil.setText("neu")
            self.main_window.lblStatScoreSub.setText("Noch nicht aussagekräftig")
            self.main_window.lblStatTrend.setText(
                "💡 Trage weitere Perioden ein, damit die Analyse genauer wird."
            )

        elif score >= 80:
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

        # Prognosen aus echten Periodendaten berechnen
        if self.user_id is None:
            self.main_window.lblPrognoseWert.setText("Noch keine Prognose verfügbar")
            self.main_window.lblPrognoseGenau.setText("Genauigkeit: -")
            self.main_window.lblEissprungWert.setText("Noch keine Eisprung-Prognose")
            self.main_window.lblEissprungInfo.setText("Eisprung: -")
        else:
            periodenstarts = periodenstarts_laden(self.user_id)

            if len(periodenstarts) == 0:
                self.main_window.lblPrognoseWert.setText("Noch keine Periode eingetragen")
                self.main_window.lblPrognoseGenau.setText("Genauigkeit: -")
                self.main_window.lblEissprungWert.setText("Noch keine Eisprung-Prognose")
                self.main_window.lblEissprungInfo.setText("Eisprung: -")

            else:
                prognose = calculate_cycle_prediction(periodenstarts)

                naechste_periode = prognose["predicted_period_start"]
                frueheste_periode = prognose["earliest_period_start"]
                spaeteste_periode = prognose["latest_period_start"]
                eisprung = prognose["predicted_ovulation"]

                self.main_window.lblPrognoseWert.setText(
                    "Voraussichtlich am " + naechste_periode.strftime("%d.%m.%Y")
                )

                # Einfache Genauigkeit: mehr gespeicherte Periodenstarts = höhere Genauigkeit
                if len(periodenstarts) == 1:
                    genauigkeit = 50
                elif len(periodenstarts) == 2:
                    genauigkeit = 65
                elif len(periodenstarts) <= 4:
                    genauigkeit = 75
                else:
                    genauigkeit = 85

                self.main_window.lblPrognoseGenau.setText(
                    "Genauigkeit: " + str(genauigkeit) + " %"
                )

                self.main_window.lblEissprungWert.setText(
                    "Fruchtbare Phase ca. " +
                    eisprung.strftime("%d.%m.%Y")
                )

                self.main_window.lblEissprungInfo.setText(
                    "Eisprung: ca. " + eisprung.strftime("%d.%m.%Y")
                )

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


    # ── Berechnungs-Hilfsmethoden ─────────────────────────────────────────────

    def zyklus_dauer_berechnen(self):
        if self.user_id is None:
            return 28

        zykluslaengen = zykluslaengen_laden(self.user_id)

        if len(zykluslaengen) == 0:
            return 28

        letzte_zyklen = zykluslaengen[-6:]

        summe = 0
        for laenge in letzte_zyklen:
            summe = summe + laenge

        return round(summe / len(letzte_zyklen))

    def schwankung_berechnen(self):
        if self.user_id is None:
            return 0

        zykluslaengen = zykluslaengen_laden(self.user_id)

        if len(zykluslaengen) == 0:
            return 0

        letzte_zyklen = zykluslaengen[-6:]

        maximum = max(letzte_zyklen)
        minimum = min(letzte_zyklen)

        return (maximum - minimum) // 2

    def periode_dauer_berechnen(self):
        if self.user_id is None:
            return 0

        perioden_dauern = perioden_dauer_laden(self.user_id)

        if len(perioden_dauern) == 0:
            return 0

        letzte_perioden = perioden_dauern[-6:]

        summe = 0
        for dauer in letzte_perioden:
            summe = summe + dauer

        return round(summe / len(letzte_perioden))

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
        from dashboard import DashboardWindow

        self.dashboard = DashboardWindow(
            user_id=self.user_id
        )

        self.dashboard.show()
        self.close()

    def on_freischalten(self):

        if self.user_id is None:
            QMessageBox.warning(
                self,
                "Fehler",
                "Es ist kein Benutzer angemeldet."
            )
            return

        bereits_freigeschaltet = analysen_freigeschaltet_laden(
            self.user_id
        )

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
                + " / 60 Punkte\n\n"
                + "Dir fehlen noch "
                + str(fehlende_punkte)
                + " Punkte, um die erweiterten Analysen freizuschalten."
            )
            return

        antwort = QMessageBox.question(
            self,
            "🔓 Analysen freischalten",
            "Du hast "
            + str(credit_points)
            + " Punkte gesammelt.\n\n"
            + "Möchtest du 60 Punkte einlösen und die erweiterten Analysen dauerhaft freischalten?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if antwort == QMessageBox.StandardButton.Yes:

            erfolgreich = erweiterte_analysen_freischalten(
                self.user_id
            )

            if erfolgreich:
                neuer_punktestand = credit_points_laden(
                    self.user_id
                )

                QMessageBox.information(
                    self,
                    "🎉 Freigeschaltet",
                    "Die erweiterten Analysen wurden erfolgreich freigeschaltet!\n\n"
                    + "Dein neuer Punktestand: "
                    + str(neuer_punktestand)
                    + " Punkte"
                )

            else:
                QMessageBox.warning(
                    self,
                    "Freischaltung fehlgeschlagen",
                    "Die erweiterten Analysen konnten nicht freigeschaltet werden."
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
        # Lokaler Import verhindert Circular-Import zwischen analyse.py und dashboard.py
        from dashboard import DashboardWindow

        self.dashboard = DashboardWindow(
            user_id=self.user_id
        )
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
        pass
        # Bereits auf der Analyse-Seite
        print("Analyse bereits geöffnet")


# ── Programm starten ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyseWindow()
    window.show()
    sys.exit(app.exec())
