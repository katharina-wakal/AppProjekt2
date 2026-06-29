# Analyse-Seite – zeigt Zyklusstatistiken, Prognosen, Trends und Insights

import sys          # Wird für den Programmstart (sys.exit) benötigt
import pathlib      # Ermittelt den Speicherort dieser Datei, um die .ui-Datei zu finden

from PyQt6 import uic                   # Lädt die .ui-Datei (grafisches Layout)
from PyQt6.QtWidgets import (
    QApplication,                        # Startet die Qt-Anwendung
    QMainWindow,                         # Basisklasse für das Hauptfenster
)

from database import (
    zykluslaengen_laden,                 # Gibt eine Liste der bisherigen Zykluslängen zurück
    perioden_dauer_laden,               # Gibt eine Liste der Periodendauern zurück
    periodenstarts_laden,               # Gibt alle erkannten Periodenstarts zurück
    credit_points_laden,                # Lädt den aktuellen Punktestand des Nutzers
    erweiterte_analysen_freischalten,   # Schaltet die erweiterten Analysen frei (kostet 60 Punkte)
    analysen_freigeschaltet_laden       # Prüft, ob die erweiterten Analysen bereits freigeschaltet sind
)

from calculation import calculate_cycle_prediction  # Berechnet Prognosen (nächste Periode, Eisprung)
from kalender import KalenderWindow                 # Fenster für den Kalender
from eintrag import EintragWindow                   # Fenster zum Eintragen von Tracking-Daten
from arzttermin import ArztterminWindow             # Fenster für Arzttermine
# Das MessageMixin stellt wiederverwendbare Methoden
# für Fehler-, Informations- und Bestätigungsdialoge bereit.
from message_mixin import MessageMixin

# AnalyseWindow erbt gleichzeitig von zwei Klassen:
#
# QMainWindow stellt die Funktionen eines PyQt-Hauptfensters bereit.
# MessageMixin ergänzt einheitliche Methoden für Meldungsfenster.
#
# Da die Klasse von zwei Elternklassen erbt,
# handelt es sich um Mehrfachvererbung.
class AnalyseWindow(QMainWindow, MessageMixin):
    # Diese Klasse stellt das Analyse-Fenster der App dar

    def __init__(self, daten=None, user_id=None):
        # Wird aufgerufen, sobald das Fenster erstellt wird
        super().__init__()  # Initialisiert das Qt-Hauptfenster

        self.user_id = user_id              # Speichert die ID des eingeloggten Nutzers
        self.daten = daten if daten is not None else {}  # Übernimmt optionale Zusatzdaten

        # Pfad zum Ordner dieser Datei ermitteln, damit die .ui-Datei gefunden wird
        working_dir = str(pathlib.Path(__file__).parent.resolve())

        # Das grafische Layout (analyse.ui) laden und auf dieses Fenster anwenden
        self.main_window = uic.loadUi(working_dir + "/analyse.ui", self)

        self.buttons_verbinden()   # Buttons mit ihren Funktionen verknüpfen
        self.anzeige_befuellen()   # Alle Felder mit echten Daten füllen

    # ── Grundaufbau ──────────────────────────────────────────────────────────

    def buttons_verbinden(self):
        # Jeder Button wird mit der passenden Funktion verbunden (clicked → Funktion)
        self.main_window.btnBack.clicked.connect(self.on_zurueck)
        self.main_window.btnFreischalten.clicked.connect(self.on_freischalten)
        self.main_window.btnMehrPeriode.clicked.connect(self.on_mehr_periode)
        self.main_window.btnMehrTrend.clicked.connect(self.on_mehr_trend)
        self.main_window.btnMehrInsights.clicked.connect(self.on_mehr_insights)

        # Untere Navigationsleiste
        self.main_window.navHome.clicked.connect(self.on_nav_home)
        self.main_window.navKalender.clicked.connect(self.on_nav_kalender)
        self.main_window.navTrackenMain.clicked.connect(self.on_nav_eintrag)
        self.main_window.navArzt.clicked.connect(self.on_nav_arzt)
        self.main_window.navAnalyse.clicked.connect(self.on_nav_analyse)

    # ── Anzeige befüllen ─────────────────────────────────────────────────────

    def anzeige_befuellen(self):
        freigeschaltet = False  # Standardmäßig sind erweiterte Analysen gesperrt

        if self.user_id is not None:
            # Datenbank prüfen: Hat dieser Nutzer die Analysen freigeschaltet?
            freigeschaltet = analysen_freigeschaltet_laden(self.user_id)

        # Symptom-Analyse aus der Anzeige entfernen (nicht mehr Teil des Projekts)
        self.symptom_elemente_entfernen()

        # Freischalt-Button je nach Status beschriften
        self.freischalt_button_setzen(freigeschaltet)

        # Alle Statistikwerte aus der Datenbank berechnen
        zyklus_dauer  = self.zyklus_dauer_berechnen()   # Durchschnittliche Zykluslänge
        schwankung    = self.schwankung_berechnen()      # Wie stark schwankt der Zyklus?
        periode_dauer = self.periode_dauer_berechnen()  # Durchschnittliche Periodendauer
        score         = self.score_berechnen(zyklus_dauer, schwankung)  # Regelmäßigkeits-Score 0–100
        anzahl_zyklen = self.anzahl_zyklen_laden()       # Wie viele Zyklen sind gespeichert?

        # Hilfstext unter der Statistik-Überschrift setzen
        self.statistik_texte_setzen(anzahl_zyklen)

        # Alle Zahlenwerte in die UI-Labels schreiben
        self.statistik_werte_setzen(zyklus_dauer, schwankung,
                                    periode_dauer, score, anzahl_zyklen)

        # Prognose (nächste Periode, Eisprung) berechnen und anzeigen
        self.prognose_anzeigen()

    def symptom_elemente_entfernen(self):
        """Blendet die Symptom-Sektion aus und schiebt den Leerraum weg.

        Die Symptom-Widgets (div3 bis lblKorrelation) belegen y=738–900.
        Alle Elemente darunter werden um genau diesen Abstand nach oben
        verschoben, damit kein Leerblock entsteht.
        """
        # Liste aller Widget-Namen, die zur Symptom-Sektion gehören
        symptom_widgets = [
            "div3",           # Trennlinie vor der Symptom-Sektion
            "lblSekSymptome", # Überschrift "Symptom-Analyse"
            "cardSymptom1",   # Karte Symptom 1 (z. B. Krämpfe)
            "cardSymptom2",   # Karte Symptom 2 (z. B. Kopfschmerzen)
            "cardSymptom3",   # Karte Symptom 3 (z. B. Müdigkeit)
            "lblKorrelation", # Korrelationshinweis-Text unter den Karten
        ]

        # Obere Grenze des Symptom-Blocks: y-Position von div3
        symptom_oben  = self.main_window.div3.y()

        # Untere Grenze: y-Position von lblKorrelation + seine Höhe
        symptom_unten = (self.main_window.lblKorrelation.y()
                         + self.main_window.lblKorrelation.height())

        # Höhe des gesamten Symptom-Blocks berechnen (ca. 162 Pixel)
        symptom_hoehe = symptom_unten - symptom_oben

        # Alle Symptom-Widgets unsichtbar machen
        for name in symptom_widgets:
            widget = getattr(self.main_window, name, None)  # Widget anhand seines Namens holen
            if widget is not None:
                widget.hide()  # Widget ausblenden (bleibt im Speicher, nur nicht sichtbar)

        # Alle anderen Widgets im Scroll-Bereich, die unterhalb des Symptom-Blocks liegen,
        # werden nach oben verschoben, damit der leere Bereich verschwindet
        for kind in self.main_window.scrollContents.children():
            if not hasattr(kind, "geometry"):
                continue  # Kein visuelles Widget (z. B. Layout-Objekte) → überspringen

            if kind.objectName() in symptom_widgets:
                continue  # Symptom-Widgets selbst nicht verschieben

            geo = kind.geometry()  # Aktuelle Position und Größe des Widgets holen

            if geo.y() > symptom_unten:
                # Widget liegt unterhalb des Symptom-Blocks → nach oben schieben
                kind.setGeometry(geo.x(), geo.y() - symptom_hoehe,
                                 geo.width(), geo.height())

        # Den gesamten Scroll-Bereich um die entfernte Symptom-Höhe verkleinern,
        # damit der Scrollbalken korrekt bleibt
        aktuell = self.main_window.scrollContents.height()
        self.main_window.scrollContents.resize(390, aktuell - symptom_hoehe)

    def freischalt_button_setzen(self, freigeschaltet):
        # Button-Text je nach Freischalt-Status anpassen
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
            return 0  # Kein Nutzer eingeloggt → 0 Zyklen
        return len(zykluslaengen_laden(self.user_id))  # Anzahl der gespeicherten Zyklen

    def statistik_texte_setzen(self, anzahl_zyklen):
        if anzahl_zyklen == 0:
            # Noch keine Daten vorhanden → Hinweistexte anzeigen
            self.main_window.lblStatSubInfo.setText("Noch nicht genug Zyklusdaten")
            self.main_window.lblStatistikSub.setText(
                "Erste Werte basieren auf Standardannahmen"
            )
        else:
            # Anzahl der Zyklen als Info ausgeben (maximal 6 werden berücksichtigt)
            self.main_window.lblStatSubInfo.setText(
                "Basierend auf " + str(anzahl_zyklen) + " Zyklen"
            )
            self.main_window.lblStatistikSub.setText(
                "Durchschnittswerte deiner letzten "
                + str(min(anzahl_zyklen, 6))  # Maximal 6 Zyklen anzeigen
                + " Zyklen"
            )

    def statistik_werte_setzen(self, zyklus_dauer, schwankung,
                               periode_dauer, score, anzahl_zyklen):
        # Zykluslänge als Text ins Label schreiben
        self.main_window.lblZyklusDauerWert.setText(str(zyklus_dauer) + " Tage")

        # Badge-Farbe/Text für Schwankung setzen
        self.schwankungs_badge_setzen(schwankung)

        # Periodendauer anzeigen
        self.periodendauer_setzen(periode_dauer)

        # Score-Badge und Trend-Text setzen
        self.score_setzen(score, anzahl_zyklen)

        # Trend-Text je nach Schwankungsstärke setzen
        self.trend_text_setzen(schwankung)

    def schwankungs_badge_setzen(self, schwankung):
        # Kleines Badge neben der Zykluslänge beschriften
        if schwankung <= 2:
            self.main_window.badgeUntypisch.setText("✓ stabil")       # Kaum Schwankung
        elif schwankung <= 5:
            self.main_window.badgeUntypisch.setText("~ normal")        # Normale Schwankung
        else:
            self.main_window.badgeUntypisch.setText("⚠ unregelmäßig") # Starke Schwankung

    def periodendauer_setzen(self, periode_dauer):
        # Grammatikalisch korrekte Ausgabe: "1 Tag" vs. "X Tage"
        if periode_dauer == 1:
            self.main_window.lblPeriodeDauerWert.setText("1 Tag")
        else:
            self.main_window.lblPeriodeDauerWert.setText(
                str(periode_dauer) + " Tage"
            )

    def score_setzen(self, score, anzahl_zyklen):
        if anzahl_zyklen == 0:
            # Noch keine Daten → alle Score-Felder auf Standardwerte setzen
            self.main_window.lblScoreWert.setText("-")
            self.main_window.lblStatScore.setText("-")
            self.main_window.badgeStabil.setText("neu")
            self.main_window.lblStatScoreSub.setText("Noch nicht aussagekräftig")
            self.main_window.lblStatTrend.setText(
                "💡 Trage weitere Perioden ein, damit die Analyse genauer wird."
            )
            return  # Funktion hier beenden, der Rest ist nicht nötig

        # Score in beiden Anzeigefeldern setzen
        self.main_window.lblScoreWert.setText(str(score) + " / 100")
        self.main_window.lblStatScore.setText(str(score) + " / 100")

        # Je nach Score-Bereich verschiedene Texte und Badges setzen
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
        # Kurzen Trendtext unter der Trend-Karte setzen
        if schwankung <= 2:
            self.main_window.lblTrendText.setText("Dein Zyklus wird stabiler  📈")
        elif schwankung <= 4:
            self.main_window.lblTrendText.setText("Leichte Schwankungen erkannt  📊")
        else:
            self.main_window.lblTrendText.setText("Schwankungen nehmen zu  ⚠️")

    def prognose_anzeigen(self):
        if self.user_id is None:
            # Kein Nutzer eingeloggt → Platzhaltertexte anzeigen
            self.prognose_leer_setzen("Noch keine Prognose verfügbar")
            return

        # Alle Periodenstarts aus der Datenbank laden
        periodenstarts = periodenstarts_laden(self.user_id)

        if len(periodenstarts) == 0:
            # Noch keine Periode eingetragen → Hinweis anzeigen
            self.prognose_leer_setzen("Noch keine Periode eingetragen")
            return

        try:
            # Prognose berechnen (aus calculation.py)
            prognose = calculate_cycle_prediction(periodenstarts)
        except Exception:
            # Falls die Berechnung fehlschlägt → Fehlerhinweis anzeigen
            self.prognose_leer_setzen("Prognose konnte nicht berechnet werden")
            return

        naechste_periode = prognose["predicted_period_start"]  # Voraussichtlicher Periodenstart
        eisprung         = prognose["predicted_ovulation"]     # Voraussichtlicher Eisprung
        genauigkeit      = self.genauigkeit_berechnen(len(periodenstarts))  # Genauigkeit in %

        # Alle Prognosewerte in die UI-Labels schreiben
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
        # Alle Prognose-Labels mit Platzhaltertexten füllen
        self.main_window.lblPrognoseWert.setText(text)
        self.main_window.lblPrognoseGenau.setText("Genauigkeit: -")
        self.main_window.lblEissprungWert.setText("Noch keine Eisprung-Prognose")
        self.main_window.lblEissprungInfo.setText("Eisprung: -")

    def genauigkeit_berechnen(self, anzahl_periodenstarts):
        # Je mehr Periodenstarts gespeichert sind, desto genauer die Prognose
        if anzahl_periodenstarts == 1:
            return 50   # Nur 1 Eintrag → grobe Schätzung
        if anzahl_periodenstarts == 2:
            return 65
        if anzahl_periodenstarts <= 4:
            return 75
        return 85       # Ab 5 Einträgen → gute Genauigkeit

    # ── Berechnungs-Hilfsmethoden ────────────────────────────────────────────

    def zyklus_dauer_berechnen(self):
        if self.user_id is None:
            return 28  # Standardwert wenn kein Nutzer eingeloggt

        zykluslaengen = zykluslaengen_laden(self.user_id)

        if len(zykluslaengen) == 0:
            return 28  # Noch keine Daten → Standardwert 28 Tage

        letzte_zyklen = zykluslaengen[-6:]  # Nur die letzten 6 Zyklen berücksichtigen
        return round(sum(letzte_zyklen) / len(letzte_zyklen))  # Durchschnitt berechnen

    def schwankung_berechnen(self):
        if self.user_id is None:
            return 0  # Kein Nutzer → keine Schwankung

        zykluslaengen = zykluslaengen_laden(self.user_id)

        if len(zykluslaengen) == 0:
            return 0  # Keine Daten → keine Schwankung

        letzte_zyklen = zykluslaengen[-6:]  # Letzte 6 Zyklen

        # Schwankung = halbe Spanne zwischen längstem und kürzestem Zyklus
        return (max(letzte_zyklen) - min(letzte_zyklen)) // 2

    def periode_dauer_berechnen(self):
        if self.user_id is None:
            return 0

        perioden_dauern = perioden_dauer_laden(self.user_id)

        if len(perioden_dauern) == 0:
            return 0  # Keine Periodendaten vorhanden

        letzte_perioden = perioden_dauern[-6:]  # Letzte 6 Perioden
        return round(sum(letzte_perioden) / len(letzte_perioden))  # Durchschnitt

    def score_berechnen(self, zyklus_dauer, schwankung):
        score = 100  # Start bei 100 Punkten

        # Für jede Schwankungseinheit (±1 Tag) werden 10 Punkte abgezogen
        score = score - (schwankung * 10)

        # Liegt die Zykluslänge außerhalb des Normalbereichs (21–35 Tage)?
        if zyklus_dauer < 21 or zyklus_dauer > 35:
            score = score - 20  # Zusätzlicher Abzug

        # Score darf nicht unter 0 oder über 100 liegen
        if score < 0:
            score = 0
        if score > 100:
            score = 100

        return score

    # ── Slots (Button-Funktionen) ─────────────────────────────────────────────

    def on_zurueck(self):
        # Zurück zum Dashboard wechseln
        from dashboard import DashboardWindow
        self.dashboard = DashboardWindow(user_id=self.user_id)
        self.dashboard.show()
        self.close()  # Dieses Fenster schließen

    def on_freischalten(self):
        """
        Prüft, ob die erweiterten Analysen freigeschaltet werden können.

        Für die Freischaltung werden 60 Credit Points benötigt.
        Die Punkte werden nur abgezogen, wenn die nutzende Person
        die Freischaltung ausdrücklich bestätigt.
        """

        # Ohne Benutzer-ID können weder der Punktestand
        # noch der Freischaltungsstatus geladen werden.
        if self.user_id is None:
            # Über das MessageMixin wird eine Fehlermeldung angezeigt.
            self.zeige_fehler(
                "Es ist kein Benutzer angemeldet."
            )
            return

        # Prüfen, ob die erweiterten Analysen für diesen Nutzer
        # bereits dauerhaft freigeschaltet wurden.
        bereits_freigeschaltet = analysen_freigeschaltet_laden(
            self.user_id
        )

        # Wenn die Analysen bereits freigeschaltet sind,
        # muss kein weiterer Punktabzug erfolgen.
        if bereits_freigeschaltet:
            # Eine Informationsmeldung über das MessageMixin anzeigen.
            self.zeige_information(
                "🔓 Bereits freigeschaltet",
                "Die erweiterten Analysen sind für deinen Account "
                "bereits freigeschaltet."
            )
            return

        # Den aktuellen Punktestand aus der Datenbank laden.
        credit_points = credit_points_laden(
            self.user_id
        )

        # Prüfen, ob weniger als 60 Punkte vorhanden sind.
        if credit_points < 60:
            # Berechnen, wie viele Punkte noch fehlen.
            fehlende_punkte = 60 - credit_points

            # Den aktuellen Punktestand und die noch fehlenden
            # Punkte in einer Informationsmeldung anzeigen.
            self.zeige_information(
                "🔒 Analysen freischalten",
                "Dein aktueller Punktestand: "
                + str(credit_points)
                + " / 60 Punkte\n\n"
                + "Dir fehlen noch "
                + str(fehlende_punkte)
                + " Punkte, um die erweiterten Analysen freizuschalten."
            )
            return

        # Wenn genügend Punkte vorhanden sind,
        # wird eine abschließende Bestätigung abgefragt.
        bestaetigt = self.frage_bestaetigung(
            "🔓 Analysen freischalten",
            "Du hast "
            + str(credit_points)
            + " Punkte gesammelt.\n\n"
            + "Möchtest du 60 Punkte einlösen und die "
            + "erweiterten Analysen dauerhaft freischalten?"
        )

        # Die Methode beenden, wenn die nutzende Person
        # die Freischaltung nicht bestätigt.
        if not bestaetigt:
            return

        # Die Freischaltung über die Datenbankfunktion durchführen.
        #
        # Dabei werden 60 Credit Points abgezogen.
        erfolgreich = erweiterte_analysen_freischalten(
            self.user_id
        )

        # Prüfen, ob die Freischaltung erfolgreich war.
        if erfolgreich:
            # Den aktualisierten Punktestand aus der Datenbank laden.
            neuer_punktestand = credit_points_laden(
                self.user_id
            )

            # Die erfolgreiche Freischaltung bestätigen.
            self.zeige_information(
                "🎉 Freigeschaltet",
                "Die erweiterten Analysen wurden erfolgreich "
                "freigeschaltet!\n\n"
                + "Dein neuer Punktestand: "
                + str(neuer_punktestand)
                + " Punkte"
            )

            # Die Analyseansicht neu befüllen,
            # damit die freigeschalteten Bereiche sichtbar werden.
            self.anzeige_befuellen()

        else:
            # Eine Fehlermeldung mit einem besonderen Titel anzeigen,
            # wenn die Datenbankänderung nicht erfolgreich war.
            self.zeige_fehler(
                "Die erweiterten Analysen konnten nicht "
                "freigeschaltet werden.",
                titel="Freischaltung fehlgeschlagen"
            )

    def on_mehr_periode(self):
        print("Mehr Infos: Periodenstärke")  # Platzhalter – noch nicht implementiert

    def on_mehr_trend(self):
        print("Mehr Infos: Trend-Verlauf")   # Platzhalter – noch nicht implementiert

    def on_mehr_insights(self):
        print("Mehr Infos: Insights")        # Platzhalter – noch nicht implementiert

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
        print("Analyse bereits geöffnet")  # Wir sind bereits hier – nichts tun


if __name__ == "__main__":
    app = QApplication(sys.argv)   # Qt-Anwendung starten
    window = AnalyseWindow()       # Analyse-Fenster erstellen
    window.show()                  # Fenster anzeigen
    sys.exit(app.exec())           # App-Schleife starten (bis Fenster geschlossen wird)
