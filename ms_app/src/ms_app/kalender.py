# ---------------------------------------------------------------------------
# Kalender-Seite der FemHealth-App – Monatsübersicht mit Zyklus-Markierungen
# ---------------------------------------------------------------------------
#
# In dieser Datei wird das Kalender-Fenster verwaltet.
# Der Kalender zeigt mehrere Monate untereinander an und markiert
# besondere Tage farblich: Perioden-Tage (rot), die Eisprung-Zone (blau)
# und gespeicherte Arzttermine (lila).
#
# Klickt die Benutzerin auf einen Tag, werden im unteren Detail-Bereich
# der Zyklustag, die Zyklusphase und die getrackten Daten dieses Tages
# angezeigt.

# sys wird benötigt, um die PyQt-Anwendung zu starten (nur beim direkten
# Ausführen dieser Datei) und beim Beenden einen Rückgabewert zu übergeben.
import sys
# pathlib wird verwendet, um den Pfad zur kalender.ui-Datei zu bestimmen.
import pathlib
# date und timedelta werden für die Datums- und Zyklusberechnungen genutzt.
from datetime import date, timedelta, datetime
# uic lädt die im Qt Designer erstellte Benutzeroberfläche.
from PyQt6 import uic
# Benötigte PyQt6-Widgets: Fenster, Labels, Buttons, Layouts

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QGridLayout, QVBoxLayout
)
# Qt liefert u. a. Ausrichtungs-Konstanten, QTimer erlaubt verzögerte Aufrufe.
from PyQt6.QtCore import Qt, QTimer
# Datenbankfunktionen zum Laden von Perioden-Tagen, Tageseinträgen
# und Arztterminen.
from database import perioden_tage_laden, eintrag_fuer_tag_laden, arzttermine_laden, arzttermin_fuer_tag_laden
# datetime wird verwendet, um gespeicherte Datums-Texte in echte Datumsobjekte
# umzuwandeln.
# Das MessageMixin stellt wiederverwendbare Methoden
# für Fehler- und Informationsmeldungen bereit.
from message_mixin import MessageMixin




# ---------------------------------------------------------------------------
# Klasse für das Kalender-Fenster
# ---------------------------------------------------------------------------
# KalenderWindow erbt gleichzeitig von zwei Klassen:
#
# QMainWindow stellt die Funktionen eines PyQt-Hauptfensters bereit.
# MessageMixin ergänzt wiederverwendbare Methoden für Meldungsfenster.
#
# Da KalenderWindow von zwei Elternklassen erbt,
# handelt es sich um Mehrfachvererbung.
class KalenderWindow(QMainWindow, MessageMixin):
    """
        Verwaltet das Kalender-Fenster der FemHealth-App.

        Die Klasse lädt die Benutzeroberfläche, baut den Mehrmonats-Kalender
        auf, markiert besondere Tage farblich und zeigt im Detail-Bereich
        die Zyklus- und Tagesinformationen zum ausgewählten Tag an.
        """

    def __init__(self, user_id=None):
        """
            Initialisiert das Kalender-Fenster.

            Dabei wird die UI-Datei geladen, die Perioden-Tage und Arzttermine
            des Benutzers werden aus der Datenbank geladen, die Buttons werden
            verbunden und der Kalender wird aufgebaut.

            Parameter:
                user_id: Die ID des angemeldeten Benutzers. Wird sie nicht
                    übergeben (None), werden keine persönlichen Daten geladen.
            """
        # Der Konstruktor der übergeordneten Klasse QMainWindow wird ausgeführt.
        super().__init__()
        # Die übergebene Benutzer-ID wird gespeichert, damit sie später
        # in allen Methoden zur Verfügung steht.
        self.user_id = user_id

        # .ui-Datei laden – genau wie in VL 4 gezeigt
        # Der Ordner dieser Datei wird bestimmt, damit die kalender.ui
        # zuverlässig gefunden wird.
        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.main_window = uic.loadUi(working_dir + "/kalender.ui", self)

        # Liste der Tage, an denen die Periode war (wird farblich markiert).
        self.perioden_tage = []
        self.arzttermin_tage = []  # Liste mit Daten gespeicherter Arzttermine

        # Persönliche Daten werden nur geladen, wenn ein Benutzer angemeldet ist.
        if self.user_id is not None:

            # Perioden-Tage als Text-Liste aus der Datenbank laden.
            perioden_daten = perioden_tage_laden(self.user_id)

            # Jeden Datums-Text in ein echtes date-Objekt umwandeln
            # und der Liste hinzufügen.
            for datum_text in perioden_daten:
                datum = datetime.strptime(
                    datum_text,
                    "%Y-%m-%d"
                ).date()

                self.perioden_tage.append(datum)

            # Arzttermine aus der Datenbank laden
            # Das Datum ist im Format 'dd.MM.yyyy' gespeichert (siehe arzttermin.py)
            termin_daten = arzttermine_laden(self.user_id)

            for datum_text in termin_daten:
                try:
                    # Datums-Text ins date-Objekt umwandeln und speichern.
                    datum = datetime.strptime(datum_text, "%d.%m.%Y").date()
                    self.arzttermin_tage.append(datum)  # Datum zur Liste hinzufügen
                except ValueError:
                    pass  # Ungültiges Datumsformat wird übersprungen

        # Fest definierte Eisprung-Zone (zur Demonstration / Markierung).
        self.eisprung_zone = [
            date(2026, 5, 14),
            date(2026, 5, 15),
            date(2026, 5, 16),
            date(2026, 5, 17),
        ]

        # Zyklusbeginn für Zyklustag-Berechnung
        self.zyklus_start  = date(2026, 5, 5)
        # Angenommene Länge eines Zyklus in Tagen.
        self.zyklus_laenge = 28

        # Aktuell ausgewählter Tag (beim Start: heute).
        self.ausgewaehlter_tag = date.today()

        # Buttons mit Funktionen verbinden
        self.main_window.btnBack.clicked.connect(self.on_zurueck)
        self.main_window.btnTracken.clicked.connect(self.on_tracken)
        self.main_window.btnMehrErfahren.clicked.connect(self.on_mehr_erfahren)

        # Kalender aufbauen und Sheet befüllen
        self.kalender_aufbauen()
        # Den Detail-Bereich mit den Daten von heute füllen.
        self.detail_sheet_befuellen(date.today())

    # ── Kalender aufbauen ─────────────────────────────────────────────────────

    def kalender_aufbauen(self):
        """
            Baut den Mehrmonats-Kalender auf.

            Es werden 6 Monate in die Vergangenheit bis 6 Monate in die
            Zukunft (insgesamt 13 Monate) untereinander angezeigt.
            Anschließend wird automatisch ungefähr zum aktuellen Monat
            gescrollt.
            """
        # Platzhalter-Label verstecken
        self.main_window.lblPlaceholderInfo.setVisible(False)

        # Haupt-Layout für calContents anlegen
        # In dieses senkrechte Layout werden alle Monate eingehängt.
        haupt_layout = QVBoxLayout()
        haupt_layout.setContentsMargins(8, 4, 8, 4)
        haupt_layout.setSpacing(0)

        # Aktuellen und nächsten Monat anzeigen
        # Mehrere Monate anzeigen: 6 Monate zurück bis 6 Monate voraus
        heute = date.today()
        # Mit dem ersten Tag des aktuellen Monats beginnen.
        start_monat = heute.replace(day=1)

        # 6 Monate zurückgehen
        # Trick: einen Tag vor den Monatsanfang springen (= letzter Tag des
        # Vormonats) und dann wieder auf Tag 1 setzen.
        for i in range(6):
            start_monat = (start_monat - timedelta(days=1)).replace(day=1)

        # Ab diesem Monat wird aufgebaut.
        aktueller_monat = start_monat

        # 13 Monate nacheinander einfügen.
        for i in range(13):
            self.monat_hinzufuegen(
                haupt_layout,
                aktueller_monat.year,
                aktueller_monat.month
            )

            # Zum nächsten Monat springen: auf Tag 28 setzen, ein paar Tage
            # addieren (sicher im Folgemonat) und dann auf Tag 1 setzen.
            aktueller_monat = (
                    aktueller_monat.replace(day=28) + timedelta(days=4)
            ).replace(day=1)

        # Am Ende einen dehnbaren Bereich anhängen, damit oben kein Leerraum bleibt.
        haupt_layout.addStretch()
        # Das fertige Layout dem Inhaltsbereich des Kalenders zuweisen.
        self.main_window.calContents.setLayout(haupt_layout)

        # Nach dem Aufbau automatisch zum aktuellen Monat scrollen
        # Nach dem Anzeigen automatisch ungefähr zum aktuellen Monat scrollen
        # QTimer.singleShot wartet kurz, bis das Layout fertig gezeichnet ist.
        QTimer.singleShot(100, self.zum_aktuellen_monat_scrollen)

    def zum_aktuellen_monat_scrollen(self):
        """
            Scrollt im Kalender ungefähr in die Mitte, sodass der aktuelle
            Monat sichtbar ist.
            """
        # Die senkrechte Scrollleiste des Scrollbereichs holen.
        scrollbar = self.main_window.calScrollArea.verticalScrollBar()
        # Auf die Hälfte des maximalen Scrollwerts setzen (= ungefähr Mitte).
        scrollbar.setValue(scrollbar.maximum() // 2)

    def monat_hinzufuegen(self, eltern_layout, jahr, monat):
        """
            Fügt einen einzelnen Monat zum Kalender hinzu.

            Zuerst wird der Monatsname als Überschrift eingefügt, danach wird
            ein Raster (Grid) mit einem Button pro Tag erzeugt. Jeder Tag wird
            farblich passend gestaltet und mit einem Klick-Handler verbunden.

            Parameter:
                eltern_layout: Das Layout, in das der Monat eingehängt wird.
                jahr (int): Das Jahr des Monats.
                monat (int): Die Monatszahl (1 = Januar … 12 = Dezember).
            """
        # Monatsname als Label
        # Index 0 bleibt leer, damit monat (1–12) direkt als Index passt.
        monatsnamen = [
            "", "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        # Überschrift "Monat Jahr" erstellen und zentrieren.
        monat_label = QLabel(monatsnamen[monat] + "  " + str(jahr))
        monat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        monat_label.setStyleSheet(
            "color:#880E4F; font-size:14px; font-weight:bold; background:transparent; padding:8px 0 4px;"
        )
        eltern_layout.addWidget(monat_label)

        # Grid für die Tages-Buttons
        grid = QGridLayout()
        grid.setSpacing(1)

        # Erster Tag des Monats → Wochentag bestimmen (0=Montag, 6=Sonntag)
        # Dadurch weiß der Kalender, in welcher Spalte der 1. Tag startet.
        erster_tag   = date(jahr, monat, 1)
        start_spalte = erster_tag.weekday()

        # Anzahl Tage im Monat bestimmen
        # Im Dezember muss ins nächste Jahr gewechselt werden.
        if monat == 12:
            tage_im_monat = (date(jahr + 1, 1, 1) - timedelta(days=1)).day
        else:
            # Sonst: erster Tag des Folgemonats minus ein Tag = letzter Tag.
            tage_im_monat = (date(jahr, monat + 1, 1) - timedelta(days=1)).day

        # Tages-Buttons einfügen
        # zelle zählt fortlaufend die Position im Raster (inkl. Leerstellen
        # am Monatsanfang).
        zelle = start_spalte
        for tag_nr in range(1, tage_im_monat + 1):
            aktuelles_datum = date(jahr, monat, tag_nr)
            # Aus der laufenden Zellennummer Zeile und Spalte berechnen.
            zeile  = (zelle // 7) + 1
            spalte = zelle % 7

            # Button mit der Tageszahl erzeugen und Höhe festlegen.
            btn = QPushButton(str(tag_nr))
            btn.setMinimumHeight(38)
            btn.setMaximumHeight(38)
            # Den passenden Stil (Farbe je nach Tagestyp) setzen.
            btn.setStyleSheet(self.tag_stil_bestimmen(aktuelles_datum))

            # Klick-Handler verbinden – Lambda mit Default-Argument!
            # d=aktuelles_datum speichert das Datum pro Button fest,
            # sonst würden alle Buttons das letzte Datum verwenden.
            btn.clicked.connect(
                lambda checked, d=aktuelles_datum: self.on_tag_geklickt(d)
            )

            # Button an der berechneten Position ins Raster setzen.
            grid.addWidget(btn, zeile, spalte)
            zelle += 1

        # Das fertige Tages-Raster ins übergeordnete Layout einhängen.
        eltern_layout.addLayout(grid)

    def tag_stil_bestimmen(self, datum):
        """
            Bestimmt das Aussehen (CSS-Stylesheet) eines einzelnen Tages-Buttons.

            Je nach Tagestyp wird eine andere Farbe gewählt:
            Arzttermin (lila), Periode (rot), Eisprung-Zone (blau),
            heutiger Tag (rosa Rahmen), zukünftige Tage (grau) und
            vergangene Tage (dunkel).

            Parameter:
                datum (date): Der Tag, dessen Stil bestimmt werden soll.

            Rückgabewert:
                str: Das fertige Stylesheet als Text.
            """
        # Grundstil für alle Tage
        basis = (
            "border:none; border-radius:10px; font-size:13px; "
            "font-weight:500; min-height:38px; max-height:38px;"
        )

        # Arzttermin-Tag (lila)
        if datum in self.arzttermin_tage:
            return basis + "background:#7B1FA2; color:#fff; border-radius:10px;"

        # Perioden-Tag (rot)
        # Bei zusammenhängenden Tagen werden die Ecken am Anfang/Ende
        # abgerundet, damit der Block wie ein Balken aussieht.
        if datum in self.perioden_tage:
            index = self.perioden_tage.index(datum)
            if index == 0:
                return basis + "background:#E91E63; color:#fff; border-radius:10px 2px 2px 10px;"
            if index == len(self.perioden_tage) - 1:
                return basis + "background:#E91E63; color:#fff; border-radius:2px 10px 10px 2px;"
            return basis + "background:#E91E63; color:#fff; border-radius:2px;"

        # Eisprung-Zone (hellblau)
        if datum in self.eisprung_zone:
            index = self.eisprung_zone.index(datum)
            if index == 0:
                return basis + "background:#E3F2FD; color:#1565C0; border-radius:10px 2px 2px 10px;"
            if index == len(self.eisprung_zone) - 1:
                return basis + "background:#E3F2FD; color:#1565C0; border-radius:2px 10px 10px 2px;"
            return basis + "background:#E3F2FD; color:#1565C0; border-radius:2px;"

        # Heutiger Tag (rosa Rahmen)
        if datum == date.today():
            return basis + "color:#E91E63; font-weight:700; border:2px solid #E91E63;"

        # Zukünftige Tage (ausgegraut)
        if datum > date.today():
            return basis + "color:#CBA8B5;"

        # Vergangene normale Tage
        return basis + "color:#4A0010;"

    # ── Detail-Sheet befüllen ─────────────────────────────────────────────────

    def detail_sheet_befuellen(self, datum):
        """
            Füllt den unteren Detail-Bereich mit den Informationen zu einem Tag.

            Angezeigt werden das Datum, der Zyklustag und die Zyklusphase.
            Außerdem wird geprüft, ob für diesen Tag ein Arzttermin oder ein
            getrackter Eintrag gespeichert ist, und der entsprechende Inhalt
            wird angezeigt.

            Parameter:
                datum (date): Der Tag, dessen Details angezeigt werden sollen.
            """
        # Datum formatieren: "26. Mai"
        monatsnamen = [
            "", "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        datum_text = str(datum.day) + ". " + monatsnamen[datum.month]

        # Zyklustag berechnen
        # Abstand in Tagen seit Zyklusbeginn berechnen.
        delta      = (datum - self.zyklus_start).days
        # Mit Modulo auf die Zykluslänge umrechnen (+1, damit bei 1 begonnen wird).
        zyklus_tag = (delta % self.zyklus_laenge) + 1

        # Zyklusphase bestimmen
        phase = self.phase_berechnen(zyklus_tag)

        # Labels aktualisieren
        self.main_window.sheetDate.setText("Getrackt am " + datum_text)
        self.main_window.sheetCycleDay.setText("Zyklustag " + str(zyklus_tag))
        self.main_window.sheetPhase.setText(phase)

        # ── Tagesdaten laden ─────────────────────────────

        # Nur laden, wenn ein Benutzer angemeldet ist.
        if self.user_id is not None:

            # Prüfen ob ein Arzttermin für diesen Tag gespeichert ist
            # Das Datum wird ins Format 'dd.MM.yyyy' umgewandelt, so wie es gespeichert wird
            datum_arzt = datum.strftime("%d.%m.%Y")
            termin = arzttermin_fuer_tag_laden(self.user_id, datum_arzt)

            # Fall 1: Für diesen Tag existiert ein Arzttermin.
            if termin is not None:

                # Arzttermin-Felder mit lesbaren Labels zusammenstellen
                arzt_labels = [
                    ("🩺 Arzt / Ärztin", termin[0]),
                    ("🏥 Fachrichtung", termin[1]),
                    ("📍 Ort", termin[2]),
                    ("🕐 Uhrzeit", termin[3]),
                    ("📝 Notiz", termin[4]),
                ]

                # Aus den ausgefüllten Feldern einen Text aufbauen.
                text = ""

                for name, wert in arzt_labels:
                    if wert:
                        text += name + ": " + wert + "\n"

                # Den zusammengebauten Text anzeigen, sonst einen Hinweis.
                if text:
                    self.main_window.sheetEmpty.setText(text.strip())
                else:
                    self.main_window.sheetEmpty.setText("Keine Arzttermin-Details vorhanden")

            # Fall 2: Kein Arzttermin – stattdessen nach einem Tageseintrag suchen.
            else:

                eintrag = eintrag_fuer_tag_laden(
                    self.user_id,
                    datum.strftime("%Y-%m-%d")
                )

                # Wenn ein getrackter Eintrag existiert, dessen Felder anzeigen.
                if eintrag is not None:

                    # Jedes Feld bekommt ein lesbares Label mit Symbol.
                    # Die Reihenfolge entspricht der Speicherreihenfolge.
                    labels = [
                        ("🩸 Periode", eintrag[0]),
                        ("🔴 Schmierblutung", eintrag[1]),
                        ("💭 Gefühle", eintrag[2]),
                        ("🤕 Schmerzen", eintrag[3]),
                        ("❤️ Sexleben", eintrag[4]),
                        ("📝 Notiz", eintrag[5]),
                        ("💧 Ausfluss", eintrag[6]),
                        ("✨ Haut", eintrag[7]),
                        ("🍽 Verdauung", eintrag[8]),
                        ("🚽 Stuhlgang", eintrag[9]),
                        ("🧪 Tests", eintrag[10]),
                        ("💊 Pille", eintrag[11]),
                        ("🔵 Spirale", eintrag[12]),
                        ("💉 Spritze", eintrag[13]),
                        ("🌱 Implantat", eintrag[14]),
                        ("🩹 Pflaster", eintrag[15]),
                        ("⭕ Ring", eintrag[16]),
                    ]

                    # Nur ausgefüllte Felder in den Text aufnehmen.
                    text = ""

                    for name, wert in labels:
                        if wert:
                            text += name + ": " + wert + "\n"

                    if text:
                        self.main_window.sheetEmpty.setText(text.strip())
                    else:
                        self.main_window.sheetEmpty.setText("Keine getrackten Erfahrungen")

                # Weder Arzttermin noch Eintrag vorhanden.
                else:
                    self.main_window.sheetEmpty.setText("Keine getrackten Erfahrungen")

        # Kein Benutzer angemeldet → keine Daten anzeigbar.
        else:
            self.main_window.sheetEmpty.setText("Keine getrackten Erfahrungen")

        # Kontroll-Ausgabe in der Konsole.
        print("Sheet: " + datum_text + " – Zyklustag " + str(zyklus_tag) + " – " + phase)

    def phase_berechnen(self, zyklus_tag):
        """
            Bestimmt die Zyklusphase anhand des Zyklustags.

            Die Einteilung gilt für einen typischen 28-Tage-Zyklus.

            Parameter:
                zyklus_tag (int): Der aktuelle Tag im Zyklus (beginnend bei 1).

            Rückgabewert:
                str: Der Name der Zyklusphase.
            """
        # Zyklusphase für 28-Tage-Zyklus bestimmen
        if zyklus_tag <= 5:
            return "Menstruation"
        elif zyklus_tag <= 13:
            return "Follikelphase"
        elif zyklus_tag <= 16:
            return "Ovulationsphase"
        elif zyklus_tag <= 22:
            return "Frühe Lutealphase"
        elif zyklus_tag <= 25:
            return "Mittlere Lutealphase"
        else:
            return "Späte Lutealphase"

    # ── Slots ─────────────────────────────────────────────────────────────────

    def on_tag_geklickt(self, datum):
        """
            Wird aufgerufen, wenn ein Tag im Kalender angeklickt wird.

            Der gewählte Tag wird gespeichert und der Detail-Bereich wird
            mit den Informationen dieses Tages aktualisiert.

            Parameter:
                datum (date): Der angeklickte Tag.
            """
        # Ausgewählten Tag speichern und Sheet aktualisieren
        self.ausgewaehlter_tag = datum
        self.detail_sheet_befuellen(datum)

    def on_tracken(self):
        """
        Zeigt momentan eine Platzhaltermeldung für das Tracken
        am ausgewählten Kalendertag an.

        Das direkte Öffnen des Eintragfensters ist an dieser Stelle
        noch nicht umgesetzt.
        """

        # Das ausgewählte Datum für Test- und Entwicklungszwecke ausgeben.
        print(
            "Tracken für: "
            + str(self.ausgewaehlter_tag)
        )

        # Über das MessageMixin eine Informationsmeldung anzeigen.
        self.zeige_information(
            "Tracken",
            "Eintrag für "
            + str(self.ausgewaehlter_tag)
            + " kommt noch!"
        )

    def on_mehr_erfahren(self):
        """
        Zeigt momentan eine Platzhaltermeldung
        für zusätzliche Informationen zur Zyklusphase an.
        """

        # Konsolenausgabe für Test- und Entwicklungszwecke.
        print("Mehr erfahren geöffnet")

        # Über das MessageMixin eine Informationsmeldung anzeigen.
        self.zeige_information(
            "Mehr erfahren",
            "Infos zur Zyklusphase kommen noch!"
        )

    def on_zurueck(self):
        """
            Wird aufgerufen, wenn der Zurück-Button geklickt wird.

            Öffnet wieder das Dashboard (mit derselben Benutzer-ID) und
            schließt das Kalender-Fenster.
            """
        # Zurück zum Dashboard
        print("Zurück zum Dashboard")

        # Import erst hier, um einen gegenseitigen Import-Kreis
        # (dashboard ↔ kalender) zu vermeiden.
        from dashboard import DashboardWindow

        # Neues Dashboard-Fenster mit der aktuellen Benutzer-ID erstellen.
        self.dashboard = DashboardWindow(
            user_id=self.user_id
        )

        # Dashboard anzeigen und das Kalender-Fenster schließen.
        self.dashboard.show()
        self.close()

# ── Programm starten ──────────────────────────────────────────────────────────

# Dieser Block wird nur ausgeführt, wenn die Datei direkt gestartet wird
# (zum Testen). Beim Import aus einer anderen Datei läuft er nicht.
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KalenderWindow()
    window.show()
    sys.exit(app.exec())