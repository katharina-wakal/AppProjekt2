# ---------------------------------------------------------------------------
# Eintrag-Seite der FemHealth-App
# Symptome, Gefühle & Verhütung für einen Tag eintragen
# ---------------------------------------------------------------------------
#
# In dieser Datei wird das Eintrag-Fenster verwaltet. Die Benutzerin kann
# hier für einen bestimmten Tag verschiedene Beobachtungen festhalten:
# Periodenstärke, Schmierblutung, Gefühle, Schmerzen, Sexleben, Ausfluss,
# Haut, Verdauung, Stuhlgang, Tests und Verhütungsmethoden sowie eine Notiz.
#
# Über einen Wochenstreifen kann zwischen den Tagen gewechselt werden.
# Bereits gespeicherte Einträge werden beim Öffnen automatisch geladen,
# neue Eingaben werden über database.py in der Datenbank gespeichert.

# sys wird benötigt, um die PyQt-Anwendung zu starten (beim direkten
# Ausführen dieser Datei) und beim Beenden einen Rückgabewert zu übergeben.
import sys
# pathlib wird verwendet, um den Pfad zur eintrag.ui-Datei zu bestimmen.
import pathlib
# date und timedelta werden für die Datums- und Wochenberechnungen genutzt.
from datetime import date, timedelta
# uic lädt die im Qt Designer erstellte Benutzeroberfläche.
from PyQt6 import uic
# QApplication verwaltet die PyQt-Anwendung.
# QMainWindow ist die Basisklasse des Eintragfensters.
from PyQt6.QtWidgets import QApplication, QMainWindow

# Das MessageMixin stellt einheitliche Methoden
# für Fehler- und Informationsmeldungen bereit.
from message_mixin import MessageMixin
# Datenbankfunktionen: Eintrag speichern und gespeicherten Eintrag laden.
from database import eintrag_speichern, eintrag_fuer_tag_laden


# ---------------------------------------------------------------------------
# Klasse für das Eintrag-Fenster
# ---------------------------------------------------------------------------
# EintragWindow erbt gleichzeitig von zwei Klassen:
#
# QMainWindow stellt die Funktionen eines PyQt-Hauptfensters bereit.
# MessageMixin ergänzt einheitliche Methoden für Meldungsfenster.
#
# Da EintragWindow von zwei Elternklassen erbt,
# wird Mehrfachvererbung verwendet.
class EintragWindow(QMainWindow, MessageMixin):
    """
        Verwaltet das Eintrag-Fenster der FemHealth-App.

        Die Klasse lädt die Benutzeroberfläche, stellt einen Wochenstreifen
        zum Wechseln des Tages bereit, lädt bereits gespeicherte Einträge
        und speichert neue Eingaben in der Datenbank.
        """

    def __init__(self, eintrag_datum=None, user_id=None):
        """
            Initialisiert das Eintrag-Fenster.

            Dabei wird die UI-Datei geladen, das anzuzeigende Datum festgelegt,
            die Buttons werden verbunden, der Wochenstreifen wird aufgebaut und
            ein eventuell bereits vorhandener Eintrag wird geladen.

            Parameter:
                eintrag_datum (date): Der Tag, für den ein Eintrag erfasst
                    wird. Wird kein Datum übergeben (None), wird der heutige
                    Tag verwendet.
                user_id: Die ID des angemeldeten Benutzers. Ohne Benutzer
                    (None) kann kein Eintrag gespeichert werden.
            """
        # Der Konstruktor der übergeordneten Klasse QMainWindow wird ausgeführt.
        super().__init__()
        # Die übergebene Benutzer-ID speichern.
        self.user_id = user_id

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/eintrag.ui", self)

        # Datum setzen (Standard: heute)
        # Wenn kein Datum übergeben wurde, wird der heutige Tag verwendet.
        if eintrag_datum is None:
            self.eintrag_datum = date.today()
        else:
            self.eintrag_datum = eintrag_datum

        # Header-Datum aktualisieren
        self.datum_anzeigen()

        # ── Buttons verbinden ─────────────────────────────────────────────────

        # Schließen & Speichern
        self.main_window.btnClose.clicked.connect(self.on_schliessen)
        self.main_window.btnSpeichern.clicked.connect(self.on_speichern)
        self.main_window.btnPersonalisieren.clicked.connect(self.on_personalisieren)

        # Wochenstreifen – Tage dynamisch vorbereiten
        # Die sieben Buttons des Wochenstreifens in Reihenfolge Mo–So.
        self.tages_buttons = [
            self.main_window.btnDay25,
            self.main_window.dayToday,
            self.main_window.btnDay27,
            self.main_window.btnDay28,
            self.main_window.btnDay29,
            self.main_window.btnDay30,
            self.main_window.btnDay31,
        ]

        # Jeden Wochentag-Button mit seinem Index (0–6) verbinden.
        # index=i speichert den Wert pro Button fest (sonst hätten alle 6).
        for i, button in enumerate(self.tages_buttons):
            button.clicked.connect(lambda checked, index=i: self.on_tag_gewaehlt(index))

        # Wochenstreifen mit den Tagen der aktuellen Woche befüllen.
        self.woche_aktualisieren()

        # Bereits gespeicherte Daten laden
        self.gespeicherten_eintrag_laden()


    # ── Datum anzeigen ────────────────────────────────────────────────────────

    def datum_anzeigen(self):
        """
            Aktualisiert die Datumsanzeige im Kopfbereich des Fensters.

            Beim heutigen Tag wird zusätzlich der Hinweis "Heute" vorangestellt.
            Außerdem wird die Tageszahl im Badge oben rechts gesetzt.
            """
        # Index 0 bleibt leer, damit der Monat direkt als Index passt.
        monatsnamen = [
            "", "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        # Datum als lesbaren Text zusammensetzen, z. B. "26. Mai 2026".
        datum_text = (
            str(self.eintrag_datum.day) + ". "
            + monatsnamen[self.eintrag_datum.month] + " "
            + str(self.eintrag_datum.year)
        )

        # Beim heutigen Tag "Heute:" voranstellen, sonst nur das Datum zeigen.
        if self.eintrag_datum == date.today():
            self.main_window.lblHeaderDate.setText("Heute: " + datum_text)
        else:
            self.main_window.lblHeaderDate.setText(datum_text)

        # Badge oben rechts (Tageszahl)
        self.main_window.lblTodayBadge.setText(str(self.eintrag_datum.day))

        print("Datum gesetzt: " + datum_text)

    # ── Slots: Wochenstreifen ─────────────────────────────────────────────────

    def on_tag_gewaehlt(self, index):
        """
            Wird aufgerufen, wenn ein Tag im Wochenstreifen angeklickt wird.

            Das ausgewählte Datum wird übernommen, die Anzeige und der
            Wochenstreifen werden aktualisiert, die bisherige Auswahl wird
            zurückgesetzt und ein eventuell gespeicherter Eintrag des neuen
            Tages wird geladen.

            Parameter:
                index (int): Position des Tages im Wochenstreifen (0 = Montag).
            """
        # Aus der Liste der Wochentage das gewählte Datum übernehmen.
        self.eintrag_datum = self.button_daten[index]
        # Anzeige, Wochenstreifen und Auswahl aktualisieren bzw. zurücksetzen.
        self.datum_anzeigen()
        self.woche_aktualisieren()
        self.auswahl_zuruecksetzen()
        # Gespeicherten Eintrag des neuen Tages laden (falls vorhanden).
        self.gespeicherten_eintrag_laden()

        print("Tag gewählt: " + str(self.eintrag_datum))

    # ── Alte Auswahl zurücksetzen ─────────────────────────────────────────────

    def auswahl_zuruecksetzen(self):
        """
            Setzt alle Auswahl-Karten und das Notizfeld zurück.

            Dadurch startet jeder Tag ohne Vorauswahl, bevor die gespeicherten
            Daten des Tages geladen werden.
            """
        # Liste aller Auswahl-Karten (Buttons) auf der Seite.
        alle_karten = [
            self.main_window.cardLeicht,
            self.main_window.cardMittel,
            self.main_window.cardStark,
            self.main_window.cardSehrStark,
            self.main_window.cardRot,
            self.main_window.cardBraun,
            self.main_window.cardStimmung,
            self.main_window.cardGut,
            self.main_window.cardTraurig,
            self.main_window.cardSensibel,
            self.main_window.cardWuetend,
            self.main_window.cardReizbar,
            self.main_window.cardUnruhig,
            self.main_window.cardGleichweit,
            self.main_window.cardSchmerzfrei,
            self.main_window.cardKraempfe,
            self.main_window.cardBrueste,
            self.main_window.cardKopf,
            self.main_window.cardRuecken,
            self.main_window.cardGeschuetzt,
            self.main_window.cardUngeschuetzt,
            self.main_window.cardInterruptus,
            self.main_window.cardKeinSex,
            self.main_window.cardStarkLib,
            self.main_window.cardSchwachLib,
            self.main_window.cardSchmerzSex,
            self.main_window.cardKeinAusfluss,
            self.main_window.cardKlebrig,
            self.main_window.cardCremig,
            self.main_window.cardFadenziehend,
            self.main_window.cardUntypisch,
            self.main_window.cardHautOk,
            self.main_window.cardHautGut,
            self.main_window.cardPickel,
            self.main_window.cardTrocken,
            self.main_window.cardFettig,
            self.main_window.cardJuckend,
            self.main_window.cardVerdOk,
            self.main_window.cardBlaehbauch,
            self.main_window.cardBlaehungen,
            self.main_window.cardSodbrennen,
            self.main_window.cardUebel,
            self.main_window.cardErbrechen,
            self.main_window.cardStOk,
            self.main_window.cardVerstopfung,
            self.main_window.cardDurchfall,
            self.main_window.cardPosOvu,
            self.main_window.cardNegOvu,
            self.main_window.cardPosSchwanger,
            self.main_window.cardNegSchwanger,
            self.main_window.cardPilleGenommen,
            self.main_window.cardPilleVergessen,
            self.main_window.cardPilleSpat,
            self.main_window.cardPilleDoppel,
            self.main_window.cardPillenfrei,
            self.main_window.cardSpirFaden,
            self.main_window.cardSpirEingesetzt,
            self.main_window.cardSpirEntfernt,
            self.main_window.cardSpirAusgewechselt,
            self.main_window.cardSpritzVer,
            self.main_window.cardImplEingesetzt,
            self.main_window.cardImplEntfernt,
            self.main_window.cardImplAusgewechselt,
            self.main_window.cardPflAufgeklebt,
            self.main_window.cardPflEntfernt,
            self.main_window.cardPflSpatAuf,
            self.main_window.cardPflSpatEnt,
            self.main_window.cardPflAusgewechselt,
            self.main_window.cardRingEingesetzt,
            self.main_window.cardRingEntfernt,
            self.main_window.cardRingSpatEin,
            self.main_window.cardRingSpatEnt,
            self.main_window.cardRingAusgewechselt,
        ]

        # Jede Karte wird abgewählt (Häkchen entfernen).
        for karte in alle_karten:
            karte.setChecked(False)

        # Auch das Notizfeld wird geleert.
        self.main_window.txtNotiz.clear()


    # ── Slots: Allgemein ──────────────────────────────────────────────────────

    def on_personalisieren(self):
        """
        Zeigt einen Hinweis zum noch nicht vollständig
        umgesetzten Personalisierungsbereich an.
        """

        # Konsolenausgabe für Test- und Entwicklungszwecke.
        print("Personalisieren geöffnet")

        # Über die geerbte Methode des MessageMixins
        # wird eine Informationsmeldung angezeigt.
        self.zeige_information(
            "Personalisieren",
            "Hier kannst du später Kategorien anpassen."
        )

    def on_schliessen(self):
        """
            Wird aufgerufen, wenn der Schließen-Button geklickt wird.

            Öffnet wieder das Dashboard (mit derselben Benutzer-ID) und
            schließt das Eintrag-Fenster.
            """
        # Import erst hier, um einen gegenseitigen Import-Kreis zu vermeiden.
        from dashboard import DashboardWindow

        # Neues Dashboard-Fenster mit der aktuellen Benutzer-ID erstellen.
        self.dashboard = DashboardWindow(
            user_id=self.user_id
        )

        # Dashboard anzeigen und das Eintrag-Fenster schließen.
        self.dashboard.show()
        self.close()

    def on_speichern(self):
        """
            Liest alle ausgewählten Karten und die Notiz aus und speichert den
            Eintrag in der Datenbank.

            Für jede Kategorie wird geprüft, welche Karte(n) ausgewählt sind,
            und der entsprechende Wert wird übernommen. Kategorien mit nur
            einer möglichen Auswahl ergeben einen Text, Kategorien mit
            Mehrfachauswahl ergeben eine Liste. Zum Schluss wird der Eintrag
            über eintrag_speichern() gesichert.
            """

        # Hinweis zum Muster der folgenden Abschnitte:
        # Pro Kategorie wird geprüft, welche Karte ausgewählt (isChecked) ist,
        # und der zugehörige Wert in einer Variablen abgelegt. Bei Kategorien
        # mit Mehrfachauswahl werden die Werte stattdessen an eine Liste
        # angehängt.

        # Periode (nur eine Auswahl möglich)
        periode = ""
        if self.main_window.cardLeicht.isChecked():
            periode = "Leicht"
        elif self.main_window.cardMittel.isChecked():
            periode = "Mittel"
        elif self.main_window.cardStark.isChecked():
            periode = "Stark"
        elif self.main_window.cardSehrStark.isChecked():
            periode = "Sehr stark"

        # Schmierblutung (nur eine Auswahl möglich)
        schmier = ""
        if self.main_window.cardRot.isChecked():
            schmier = "Rot"
        elif self.main_window.cardBraun.isChecked():
            schmier = "Braun"

        # Gefühle (Mehrfachauswahl möglich)
        gefuehle = []
        if self.main_window.cardStimmung.isChecked():
            gefuehle.append("Stimmungsschwankungen")
        if self.main_window.cardGut.isChecked():
            gefuehle.append("Gut")
        if self.main_window.cardTraurig.isChecked():
            gefuehle.append("Traurig")
        if self.main_window.cardSensibel.isChecked():
            gefuehle.append("Sensibel")
        if self.main_window.cardWuetend.isChecked():
            gefuehle.append("Wütend")
        if self.main_window.cardReizbar.isChecked():
            gefuehle.append("Reizbar")
        if self.main_window.cardUnruhig.isChecked():
            gefuehle.append("Unruhig")
        if self.main_window.cardGleichweit.isChecked():
            gefuehle.append("Gleichmütig")

        # Schmerzen (Mehrfachauswahl möglich)
        schmerzen = []
        if self.main_window.cardSchmerzfrei.isChecked():
            schmerzen.append("Schmerzfrei")
        if self.main_window.cardKraempfe.isChecked():
            schmerzen.append("Krämpfe")
        if self.main_window.cardBrueste.isChecked():
            schmerzen.append("Sensible Brüste")
        if self.main_window.cardKopf.isChecked():
            schmerzen.append("Kopfschmerzen")
        if self.main_window.cardRuecken.isChecked():
            schmerzen.append("Rückenschmerzen")

        # Sexleben (Mehrfachauswahl möglich)
        sexleben = []
        if self.main_window.cardGeschuetzt.isChecked():
            sexleben.append("Geschützt")
        if self.main_window.cardUngeschuetzt.isChecked():
            sexleben.append("Ungeschützt")
        if self.main_window.cardInterruptus.isChecked():
            sexleben.append("Interruptus")
        if self.main_window.cardKeinSex.isChecked():
            sexleben.append("Kein Sex")
        if self.main_window.cardStarkLib.isChecked():
            sexleben.append("Starke Libido")
        if self.main_window.cardSchwachLib.isChecked():
            sexleben.append("Schwache Libido")
        if self.main_window.cardSchmerzSex.isChecked():
            sexleben.append("Schmerzhafter Sex")

        # Tägliche Notiz (Freitext aus dem Textfeld)
        notiz = self.main_window.txtNotiz.toPlainText().strip()

        # Ausfluss (Mehrfachauswahl möglich)
        ausfluss = []
        if self.main_window.cardKeinAusfluss.isChecked():
            ausfluss.append("Keinen")
        if self.main_window.cardKlebrig.isChecked():
            ausfluss.append("Klebrig")
        if self.main_window.cardCremig.isChecked():
            ausfluss.append("Cremig")
        if self.main_window.cardFadenziehend.isChecked():
            ausfluss.append("Fadenziehend")
        if self.main_window.cardUntypisch.isChecked():
            ausfluss.append("Untypisch")

        # Haut (Mehrfachauswahl möglich)
        haut = []
        if self.main_window.cardHautOk.isChecked():
            haut.append("Ok")
        if self.main_window.cardHautGut.isChecked():
            haut.append("Gut")
        if self.main_window.cardPickel.isChecked():
            haut.append("Pickel")
        if self.main_window.cardTrocken.isChecked():
            haut.append("Trocken")
        if self.main_window.cardFettig.isChecked():
            haut.append("Fettig")
        if self.main_window.cardJuckend.isChecked():
            haut.append("Juckend")

        # Verdauung (Mehrfachauswahl möglich)
        verdauung = []
        if self.main_window.cardVerdOk.isChecked():
            verdauung.append("Ok")
        if self.main_window.cardBlaehbauch.isChecked():
            verdauung.append("Aufgebläht")
        if self.main_window.cardBlaehungen.isChecked():
            verdauung.append("Blähungen")
        if self.main_window.cardSodbrennen.isChecked():
            verdauung.append("Sodbrennen")
        if self.main_window.cardUebel.isChecked():
            verdauung.append("Übel")
        if self.main_window.cardErbrechen.isChecked():
            verdauung.append("Erbrechen")

        # Stuhlgang (nur eine Auswahl möglich)
        stuhlgang = ""
        if self.main_window.cardStOk.isChecked():
            stuhlgang = "Ok"
        elif self.main_window.cardVerstopfung.isChecked():
            stuhlgang = "Verstopfung"
        elif self.main_window.cardDurchfall.isChecked():
            stuhlgang = "Durchfall"

        # Tests (Mehrfachauswahl möglich)
        tests = []
        if self.main_window.cardPosOvu.isChecked():
            tests.append("Pos. Ovulationstest")
        if self.main_window.cardNegOvu.isChecked():
            tests.append("Neg. Ovulationstest")
        if self.main_window.cardPosSchwanger.isChecked():
            tests.append("Pos. Schwangerschaftstest")
        if self.main_window.cardNegSchwanger.isChecked():
            tests.append("Neg. Schwangerschaftstest")

        # Antibabypille (nur eine Auswahl möglich)
        pille = ""
        if self.main_window.cardPilleGenommen.isChecked():
            pille = "Genommen"
        elif self.main_window.cardPilleVergessen.isChecked():
            pille = "Vergessen"
        elif self.main_window.cardPilleSpat.isChecked():
            pille = "Spät genommen"
        elif self.main_window.cardPilleDoppel.isChecked():
            pille = "Doppelte Dosis"
        elif self.main_window.cardPillenfrei.isChecked():
            pille = "Pillenfreier Tag"

        # Spirale (nur eine Auswahl möglich)
        spirale = ""
        if self.main_window.cardSpirFaden.isChecked():
            spirale = "Faden überprüft"
        elif self.main_window.cardSpirEingesetzt.isChecked():
            spirale = "Eingesetzt"
        elif self.main_window.cardSpirEntfernt.isChecked():
            spirale = "Entfernt"
        elif self.main_window.cardSpirAusgewechselt.isChecked():
            spirale = "Ausgewechselt"

        # Verhütungsspritze (Kurzschreibweise: nur verabreicht oder leer)
        spritze = "Verabreicht" if self.main_window.cardSpritzVer.isChecked() else ""

        # Hormonimplantat (nur eine Auswahl möglich)
        implantat = ""
        if self.main_window.cardImplEingesetzt.isChecked():
            implantat = "Eingesetzt"
        elif self.main_window.cardImplEntfernt.isChecked():
            implantat = "Entfernt"
        elif self.main_window.cardImplAusgewechselt.isChecked():
            implantat = "Ausgewechselt"

        # Verhütungspflaster (nur eine Auswahl möglich)
        pflaster = ""
        if self.main_window.cardPflAufgeklebt.isChecked():
            pflaster = "Aufgeklebt"
        elif self.main_window.cardPflEntfernt.isChecked():
            pflaster = "Entfernt"
        elif self.main_window.cardPflSpatAuf.isChecked():
            pflaster = "Spät aufgeklebt"
        elif self.main_window.cardPflSpatEnt.isChecked():
            pflaster = "Spät entfernt"
        elif self.main_window.cardPflAusgewechselt.isChecked():
            pflaster = "Ausgewechselt"

        # Verhütungsring (nur eine Auswahl möglich)
        ring = ""
        if self.main_window.cardRingEingesetzt.isChecked():
            ring = "Eingesetzt"
        elif self.main_window.cardRingEntfernt.isChecked():
            ring = "Entfernt"
        elif self.main_window.cardRingSpatEin.isChecked():
            ring = "Spät eingesetzt"
        elif self.main_window.cardRingSpatEnt.isChecked():
            ring = "Spät entfernt"
        elif self.main_window.cardRingAusgewechselt.isChecked():
            ring = "Ausgewechselt"

        # ── Debug-Ausgabe ─────────────────────────────────────────────────────
        # Kontroll-Ausgabe der gesammelten Werte in der Konsole.
        print("── Eintrag für " + str(self.eintrag_datum) + " ──")
        print("Periode:          " + periode)
        print("Schmierblutung:   " + schmier)
        print("Gefühle:          " + ", ".join(gefuehle))
        print("Schmerzen:        " + ", ".join(schmerzen))
        print("Sexleben:         " + ", ".join(sexleben))
        print("Notiz:            " + notiz)
        print("Ausfluss:         " + ", ".join(ausfluss))
        print("Haut:             " + ", ".join(haut))
        print("Verdauung:        " + ", ".join(verdauung))
        print("Stuhlgang:        " + stuhlgang)
        print("Tests:            " + ", ".join(tests))
        print("Pille:            " + pille)
        print("Spirale:          " + spirale)
        print("Spritze:          " + spritze)
        print("Implantat:        " + implantat)
        print("Pflaster:         " + pflaster)
        print("Ring:             " + ring)

        # Ohne angemeldeten Benutzer kann nichts gespeichert werden.
        if self.user_id is None:
            self.zeige_fehler("Kein Benutzer angemeldet.")
            return

        # Eintrag in der Datenbank speichern.
        # Die Listen werden mit ", ".join(...) zu einem Text zusammengefügt,
        # damit sie als einzelner Wert gespeichert werden können.
        eintrag_speichern(
            self.user_id,
            str(self.eintrag_datum),
            periode,
            schmier,
            ", ".join(gefuehle),
            ", ".join(schmerzen),
            ", ".join(sexleben),
            notiz,
            ", ".join(ausfluss),
            ", ".join(haut),
            ", ".join(verdauung),
            stuhlgang,
            ", ".join(tests),
            pille,
            spirale,
            spritze,
            implantat,
            pflaster,
            ring
        )

        # Über das MessageMixin wird bestätigt,
        # dass der Eintrag erfolgreich gespeichert wurde.
        self.zeige_information(
            "Gespeichert",
            "Dein Eintrag wurde gespeichert! ✅"
        )


    def gespeicherten_eintrag_laden(self):
        """
            Lädt einen bereits gespeicherten Eintrag des aktuellen Tages und
            setzt die passenden Karten wieder auf "ausgewählt".

            So sieht die Benutzerin beim erneuten Öffnen eines Tages ihre
            zuvor erfassten Daten. Ist kein Eintrag vorhanden, passiert nichts.
            """
        # Ohne Benutzer gibt es keine gespeicherten Daten.
        if self.user_id is None:
            return

        # Datum ins Speicherformat 'YYYY-MM-DD' umwandeln.
        datum = self.eintrag_datum.strftime("%Y-%m-%d")

        # Gespeicherten Eintrag aus der Datenbank laden.
        eintrag = eintrag_fuer_tag_laden(
            self.user_id,
            datum
        )

        # Wenn es für diesen Tag keinen Eintrag gibt, ist nichts zu tun.
        if eintrag is None:
            return

        # Die einzelnen Felder des Eintrags benennen.
        # Die Reihenfolge entspricht der Speicherreihenfolge in on_speichern().
        periode   = eintrag[0]
        schmier   = eintrag[1]
        gefuehle  = eintrag[2]
        schmerzen = eintrag[3]
        sexleben  = eintrag[4]
        notiz     = eintrag[5]
        ausfluss  = eintrag[6]
        haut      = eintrag[7]
        verdauung = eintrag[8]
        stuhlgang = eintrag[9]
        tests     = eintrag[10]
        pille     = eintrag[11]
        spirale   = eintrag[12]
        spritze   = eintrag[13]
        implantat = eintrag[14]
        pflaster  = eintrag[15]
        ring      = eintrag[16]

        # Hinweis zum Muster der folgenden Abschnitte:
        # Für jede Kategorie wird der gespeicherte Text geprüft und die
        # passende(n) Karte(n) wieder ausgewählt. Bei Mehrfachauswahl wird
        # mit "in" geprüft, ob der jeweilige Begriff im gespeicherten Text
        # enthalten ist.

        # Periode (Einzelauswahl)
        if periode == "Leicht":
            self.main_window.cardLeicht.setChecked(True)
        elif periode == "Mittel":
            self.main_window.cardMittel.setChecked(True)
        elif periode == "Stark":
            self.main_window.cardStark.setChecked(True)
        elif periode == "Sehr stark":
            self.main_window.cardSehrStark.setChecked(True)

        # Gefühle (Mehrfachauswahl)
        if gefuehle:
            if "Stimmungsschwankungen" in gefuehle:
                self.main_window.cardStimmung.setChecked(True)
            if "Gut" in gefuehle:
                self.main_window.cardGut.setChecked(True)
            if "Traurig" in gefuehle:
                self.main_window.cardTraurig.setChecked(True)
            if "Sensibel" in gefuehle:
                self.main_window.cardSensibel.setChecked(True)
            if "Wütend" in gefuehle:
                self.main_window.cardWuetend.setChecked(True)
            if "Reizbar" in gefuehle:
                self.main_window.cardReizbar.setChecked(True)
            if "Unruhig" in gefuehle:
                self.main_window.cardUnruhig.setChecked(True)
            if "Gleichmütig" in gefuehle:
                self.main_window.cardGleichweit.setChecked(True)

        # Schmerzen (Mehrfachauswahl)
        if schmerzen:
            if "Schmerzfrei" in schmerzen:
                self.main_window.cardSchmerzfrei.setChecked(True)
            if "Krämpfe" in schmerzen:
                self.main_window.cardKraempfe.setChecked(True)
            if "Sensible Brüste" in schmerzen:
                self.main_window.cardBrueste.setChecked(True)
            if "Kopfschmerzen" in schmerzen:
                self.main_window.cardKopf.setChecked(True)
            if "Rückenschmerzen" in schmerzen:
                self.main_window.cardRuecken.setChecked(True)

        # Sexleben (Mehrfachauswahl)
        if sexleben:
            if "Geschützt" in sexleben:
                self.main_window.cardGeschuetzt.setChecked(True)
            if "Ungeschützt" in sexleben:
                self.main_window.cardUngeschuetzt.setChecked(True)
            if "Interruptus" in sexleben:
                self.main_window.cardInterruptus.setChecked(True)
            if "Kein Sex" in sexleben:
                self.main_window.cardKeinSex.setChecked(True)
            if "Starke Libido" in sexleben:
                self.main_window.cardStarkLib.setChecked(True)
            if "Schwache Libido" in sexleben:
                self.main_window.cardSchwachLib.setChecked(True)
            if "Schmerzhafter Sex" in sexleben:
                self.main_window.cardSchmerzSex.setChecked(True)

        # Schmierblutung (Einzelauswahl, hier per "in" geprüft)
        if schmier:
            if "Rot" in schmier:
                self.main_window.cardRot.setChecked(True)
            if "Braun" in schmier:
                self.main_window.cardBraun.setChecked(True)

        # Notiz (Freitext zurück ins Textfeld schreiben)
        if notiz:
            self.main_window.txtNotiz.setPlainText(notiz)

        # Ausfluss (Mehrfachauswahl)
        if ausfluss:
            if "Keinen" in ausfluss:
                self.main_window.cardKeinAusfluss.setChecked(True)
            if "Klebrig" in ausfluss:
                self.main_window.cardKlebrig.setChecked(True)
            if "Cremig" in ausfluss:
                self.main_window.cardCremig.setChecked(True)
            if "Fadenziehend" in ausfluss:
                self.main_window.cardFadenziehend.setChecked(True)
            if "Untypisch" in ausfluss:
                self.main_window.cardUntypisch.setChecked(True)

        # Haut (Mehrfachauswahl)
        if haut:
            if "Ok" in haut:
                self.main_window.cardHautOk.setChecked(True)
            if "Gut" in haut:
                self.main_window.cardHautGut.setChecked(True)
            if "Pickel" in haut:
                self.main_window.cardPickel.setChecked(True)
            if "Trocken" in haut:
                self.main_window.cardTrocken.setChecked(True)
            if "Fettig" in haut:
                self.main_window.cardFettig.setChecked(True)
            if "Juckend" in haut:
                self.main_window.cardJuckend.setChecked(True)

        # Verdauung (Mehrfachauswahl)
        if verdauung:
            if "Ok" in verdauung:
                self.main_window.cardVerdOk.setChecked(True)
            if "Aufgebläht" in verdauung:
                self.main_window.cardBlaehbauch.setChecked(True)
            if "Blähungen" in verdauung:
                self.main_window.cardBlaehungen.setChecked(True)
            if "Sodbrennen" in verdauung:
                self.main_window.cardSodbrennen.setChecked(True)
            if "Übel" in verdauung:
                self.main_window.cardUebel.setChecked(True)
            if "Erbrechen" in verdauung:
                self.main_window.cardErbrechen.setChecked(True)

        # Stuhlgang (Einzelauswahl)
        if stuhlgang:
            if "Ok" in stuhlgang:
                self.main_window.cardStOk.setChecked(True)
            elif "Verstopfung" in stuhlgang:
                self.main_window.cardVerstopfung.setChecked(True)
            elif "Durchfall" in stuhlgang:
                self.main_window.cardDurchfall.setChecked(True)

        # Tests (Mehrfachauswahl)
        if tests:
            if "Pos. Ovulationstest" in tests:
                self.main_window.cardPosOvu.setChecked(True)
            if "Neg. Ovulationstest" in tests:
                self.main_window.cardNegOvu.setChecked(True)
            if "Pos. Schwangerschaftstest" in tests:
                self.main_window.cardPosSchwanger.setChecked(True)
            if "Neg. Schwangerschaftstest" in tests:
                self.main_window.cardNegSchwanger.setChecked(True)

        # Pille (Einzelauswahl)
        if pille:
            if "Genommen" in pille:
                self.main_window.cardPilleGenommen.setChecked(True)
            elif "Vergessen" in pille:
                self.main_window.cardPilleVergessen.setChecked(True)
            elif "Spät genommen" in pille:
                self.main_window.cardPilleSpat.setChecked(True)
            elif "Doppelte Dosis" in pille:
                self.main_window.cardPilleDoppel.setChecked(True)
            elif "Pillenfreier Tag" in pille:
                self.main_window.cardPillenfrei.setChecked(True)

        # Spirale (Einzelauswahl)
        if spirale:
            if "Faden überprüft" in spirale:
                self.main_window.cardSpirFaden.setChecked(True)
            elif "Eingesetzt" in spirale:
                self.main_window.cardSpirEingesetzt.setChecked(True)
            elif "Entfernt" in spirale:
                self.main_window.cardSpirEntfernt.setChecked(True)
            elif "Ausgewechselt" in spirale:
                self.main_window.cardSpirAusgewechselt.setChecked(True)

        # Spritze (Einzelauswahl)
        if spritze:
            if "Verabreicht" in spritze:
                self.main_window.cardSpritzVer.setChecked(True)

        # Implantat (Einzelauswahl)
        if implantat:
            if "Eingesetzt" in implantat:
                self.main_window.cardImplEingesetzt.setChecked(True)
            elif "Entfernt" in implantat:
                self.main_window.cardImplEntfernt.setChecked(True)
            elif "Ausgewechselt" in implantat:
                self.main_window.cardImplAusgewechselt.setChecked(True)

        # Pflaster (Einzelauswahl)
        if pflaster:
            if "Aufgeklebt" in pflaster:
                self.main_window.cardPflAufgeklebt.setChecked(True)
            elif "Entfernt" in pflaster:
                self.main_window.cardPflEntfernt.setChecked(True)
            elif "Spät aufgeklebt" in pflaster:
                self.main_window.cardPflSpatAuf.setChecked(True)
            elif "Spät entfernt" in pflaster:
                self.main_window.cardPflSpatEnt.setChecked(True)
            elif "Ausgewechselt" in pflaster:
                self.main_window.cardPflAusgewechselt.setChecked(True)

        # Ring (Einzelauswahl)
        if ring:
            if "Eingesetzt" in ring:
                self.main_window.cardRingEingesetzt.setChecked(True)
            elif "Entfernt" in ring:
                self.main_window.cardRingEntfernt.setChecked(True)
            elif "Spät eingesetzt" in ring:
                self.main_window.cardRingSpatEin.setChecked(True)
            elif "Spät entfernt" in ring:
                self.main_window.cardRingSpatEnt.setChecked(True)
            elif "Ausgewechselt" in ring:
                self.main_window.cardRingAusgewechselt.setChecked(True)

    def woche_start_berechnen(self, datum):
        """
            Berechnet den Montag der Woche, in der das übergebene Datum liegt.

            Parameter:
                datum (date): Ein beliebiger Tag.

            Rückgabewert:
                date: Der Montag derselben Woche.
            """
        # weekday() liefert 0 für Montag … 6 für Sonntag. Diese Anzahl Tage
        # wird abgezogen, um beim Montag zu landen.
        return datum - timedelta(days=datum.weekday())

    def woche_aktualisieren(self):
        """
            Aktualisiert die sieben Buttons des Wochenstreifens.

            Für jeden Tag der aktuellen Woche werden die Tageszahl gesetzt und
            das zugehörige Datum gespeichert. Der ausgewählte Tag wird optisch
            hervorgehoben.
            """
        # Den Montag der Woche bestimmen, in der das Eintragsdatum liegt.
        montag = self.woche_start_berechnen(self.eintrag_datum)
        # Liste, in der die Datumswerte der sieben Buttons gespeichert werden.
        self.button_daten = []

        # Stil für nicht ausgewählte Tage.
        normal_style = """
            QPushButton {
                background: transparent;
                border: none;
                color: #CBA8B5;
                font-size: 13px;
                font-weight: 500;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #FCE4EC;
            }
        """

        # Stil für den aktuell ausgewählten Tag (rosa Rahmen, hervorgehoben).
        aktiv_style = """
            QPushButton {
                background: transparent;
                border: 2px solid #E91E63;
                border-radius: 10px;
                color: #E91E63;
                font-size: 13px;
                font-weight: 700;
            }
        """

        # Für jeden der sieben Buttons das passende Datum berechnen.
        for i, button in enumerate(self.tages_buttons):
            # Tag i Tage nach Montag.
            button_datum = montag + timedelta(days=i)
            # Datum merken (wird in on_tag_gewaehlt verwendet).
            self.button_daten.append(button_datum)
            # Tageszahl auf dem Button anzeigen.
            button.setText(str(button_datum.day))
            # Den ausgewählten Tag hervorheben, alle anderen normal darstellen.
            if button_datum == self.eintrag_datum:
                button.setStyleSheet(aktiv_style)
            else:
                button.setStyleSheet(normal_style)

# ── Programm starten ──────────────────────────────────────────────────────────

# Dieser Block wird nur ausgeführt, wenn die Datei direkt gestartet wird
# (zum Testen). Beim Import aus einer anderen Datei läuft er nicht.
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EintragWindow()
    window.show()
    sys.exit(app.exec())