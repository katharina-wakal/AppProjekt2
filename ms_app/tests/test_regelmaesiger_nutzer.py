"""
Dieses Testmodul füllt die Tabelle daily_entries mit simulierten Tracking-Daten.

Die Daten werden für einen bereits vorhandenen Testnutzer erzeugt.
Dabei werden tägliche Einträge über einen Zeitraum von sechs Monaten angelegt.

Zusätzlich werden sieben Perioden simuliert, aus denen später sechs vollständige
Zykluslängen berechnet werden können.
"""
# sqlite3 wird benötigt, um auf die SQLite-Datenbank zuzugreifen.
import sqlite3

# date wird für Datumswerte verwendet.
# timedelta ermöglicht es, Tage zu einem Datum hinzuzurechnen.
from datetime import date, timedelta

# Path erleichtert das Erstellen eines betriebssystemunabhängigen Dateipfades.
from pathlib import Path

# Path erleichtert das Erstellen eines betriebssystemunabhängigen Dateipfades.
DB_PATH = (
    # __file__ bezeichnet die aktuelle Python-Datei.
    # resolve() erzeugt daraus einen vollständigen absoluten Pfad.
    # parent wechselt in den Ordner, in dem diese Datei liegt.
    # Das zweite parent wechselt noch eine Ordnerebene weiter nach oben.
    Path(__file__).resolve().parent.parent

    # Anschließend wird in den Ordner "src" gewechselt.
    / "src"

    # Danach wird in den Ordner "ms_app" gewechselt.
    / "ms_app"

    #Am Ende wird der Dateiname der Datenbank ergänzt.
    / "femhealth.db"
)

# Die Datenbank-ID des Testnutzers, für den die Testdaten erstellt werden.
TEST_USER_ID = 5

def create_connection():
    """
    Öffnet eine Verbindung zur vorhandenen FemHealth-Datenbank.

    Rückgabewert:
        Eine aktive Verbindung zur SQLite-Datenbank.
    """
    # sqlite3.connect() öffnet die angegebene Datenbank.
    # Der Path wird mit str() in eine Zeichenkette umgewandelt.
    return sqlite3.connect(str(DB_PATH))

def testdaten_einfuegen():
    """
       Fügt simulierte tägliche Tracking-Einträge für den Testnutzer ein.

       Zuerst wird geprüft, ob der Testnutzer existiert.
       Danach werden alte Testeinträge gelöscht und neue Einträge für
       sechs Monate angelegt.
       """
    # Eine Verbindung zur Datenbank wird hergestellt.
    connection = create_connection()

    # Der Cursor wird benötigt, um SQL-Befehle auszuführen.
    cursor = connection.cursor()

    # Der try-Block enthält alle Datenbankaktionen, bei denen Fehler auftreten könnten.
    try:
        # Prüfen, ob der Testnutzer mit der angegebenen ID wirklich existiert.
        cursor.execute("""
            SELECT id, first_name, last_name, email
            FROM users
            WHERE id = ?
        """,
# Das Fragezeichen im SQL-Befehl wird durch TEST_USER_ID ersetzt.
# Das Komma ist notwendig, damit Python dies als Tupel erkennt.
    (TEST_USER_ID,))

        # fetchone() liefert den ersten gefundenen Datensatz.
        # Wenn kein Nutzer gefunden wurde, ist das Ergebnis None.
        nutzer = cursor.fetchone()

        # Prüfen, ob kein Nutzer mit der angegebenen ID gefunden wurde.
        if nutzer is None:
            # Eine Fehlermeldung wird in der Konsole ausgegeben.
            print("Kein Nutzer mit der ID " + str(TEST_USER_ID) + " gefunden.")

            # Die Funktion wird beendet, da keine Testdaten eingefügt werden können.
            return

        # Ausgabe der Daten des gefundenen Testnutzers.
        # nutzer[1] enthält den Vornamen.
        # nutzer[2] enthält den Nachnamen.
        # nutzer[3] enthält die E-Mail-Adresse.
        print(
            "Testnutzer gefunden: "+ str(nutzer[1])+ " "
            + str(nutzer[2])+ " ("+ str(nutzer[3])+ ")" )

        # Bereits vorhandene Tracking-Einträge des Testnutzers werden gelöscht.
        # Dadurch entstehen bei erneutem Ausführen keine doppelten Einträge.
        cursor.execute("""
            DELETE FROM daily_entries
            WHERE user_id = ?
        """,
        # Es werden nur Einträge des angegebenen Testnutzers gelöscht.
        (TEST_USER_ID,))

        # In diesem Dictionary werden die simulierten Periodenstarts gespeichert.
        #
        # Der Schlüssel ist jeweils das Startdatum der Periode.
        # Der Wert gibt die Dauer der Periode in Tagen an.
        #
        # Aus sieben Periodenstarts können sechs vollständige Zykluslängen
        # berechnet werden, da eine Zykluslänge immer der Abstand zwischen
        # zwei aufeinanderfolgenden Periodenstarts ist.
        perioden = {
            # Erste Periode beginnt am 5. Dezember 2025 und dauert fünf Tage.
            date(2025, 12, 5): 5,
            # Zweite Periode beginnt am 2. Januar 2026 und dauert fünf Tage.
            date(2026, 1, 2): 5,
            # Dritte Periode beginnt am 31. Januar 2026 und dauert fünf Tage.
            date(2026, 1, 31): 5,
            # Vierte Periode beginnt am 28. Februar 2026 und dauert fünf Tage.
            date(2026, 2, 28): 5,
            # Fünfte Periode beginnt am 28. März 2026 und dauert fünf Tage.
            date(2026, 3, 28): 5,
            # Sechste Periode beginnt am 26. April 2026 und dauert fünf Tage.
            date(2026, 4, 26): 5,
            # Siebte Periode beginnt am 24. Mai 2026 und dauert fünf Tage.
            date(2026, 5, 24): 5
        }

        # In diesem Dictionary werden später alle einzelnen Periodentage gespeichert.
        #
        # Der Schlüssel wird das Datum des Periodentages.
        # Der Wert wird die Stärke der Blutung an diesem Tag.
        perioden_tage = {}

        # Alle Periodenstarts und die jeweils zugehörige Dauer durchlaufen.
        for periodenstart, dauer in perioden.items():

            # Für jeden einzelnen Tag der jeweiligen Periode wird die Schleife ausgeführt.
            #
            # Bei einer Dauer von fünf Tagen erzeugt range(dauer) die Werte:
            # 0, 1, 2, 3 und 4.
            for tag_nummer in range(dauer):
                # Das Datum des einzelnen Periodentages wird berechnet.
                #
                # tag_nummer 0 entspricht dem Periodenstart.
                # tag_nummer 1 entspricht dem darauffolgenden Tag usw.
                periodentag = periodenstart + timedelta(days=tag_nummer)

                # Am ersten Periodentag wird eine mittlere Blutungsstärke eingetragen.
                if tag_nummer == 0:
                    staerke = "Mittel"
                # Am zweiten Periodentag wird eine starke Blutung eingetragen.
                elif tag_nummer == 1:
                    staerke = "Stark"
                # Am dritten Periodentag wird wieder eine mittlere Blutung eingetragen.
                elif tag_nummer == 2:
                    staerke = "Mittel"
                # An allen übrigen Periodentagen wird eine leichte Blutung eingetragen.
                else:
                    staerke = "Leicht"

                # Das Datum und die zugehörige Blutungsstärke werden
                # im Dictionary gespeichert.
                perioden_tage[periodentag] = staerke

        # Das Startdatum des simulierten Tracking-Zeitraums.
        startdatum = date(2025, 12, 1)

        # Das Enddatum des simulierten Tracking-Zeitraums.
        enddatum = date(2026, 5, 31)

        # Das aktuelle Datum wird zunächst auf das Startdatum gesetzt.
        # Diese Variable wird später täglich um einen Tag erhöht.
        aktuelles_datum = startdatum
        # Zähler für die Anzahl der erzeugten täglichen Einträge
        anzahl_eintraege = 0

        # Die Schleife läuft so lange, bis einschließlich des Enddatums
        # alle täglichen Einträge erzeugt wurden.
        while aktuelles_datum <= enddatum:

            # Im Dictionary perioden_tage wird geprüft, ob das aktuelle Datum
            # ein Periodentag ist.
            #
            # Wenn es ein Periodentag ist, wird die Blutungsstärke zurückgegeben.
            # Wenn kein Eintrag vorhanden ist, liefert get() den Wert None.
            periode = perioden_tage.get(aktuelles_datum)


            schmierblutung = None # Standardwert für Schmierblutungen, none = keine schmierblutungen
            gefuehle = "Ausgeglichen" # Standardwert für die Gefühle an einem normalen Tag.
            schmerzen = None # Standardwert für Schmerzen., None = keine Schmerzen
            sexleben = None # Standardwert für Angaben zum Sexleben.
            notiz = "Simulierter Tracking-Eintrag" # Standardnotiz für einen normalen simulierten Tracking-Tag.
            ausfluss = "Normal" # Standardwert für den Ausfluss.
            haut = "Normal" # Standardwert für den Hautzustand.
            verdauung = "Normal" # Standardwert für die Verdauung.
            stuhlgang = "Normal" # Standardwert für den Stuhlgang.
            tests = None # Standardwert für eingetragene Tests.
            pille = None  # Standardwert für die Einnahme der Pille.
            spirale = None # Standardwert für die Verwendung einer Spirale.
            spritze = None # Standardwert für die Verwendung einer Verhütungsspritze.
            implantat = None # Standardwert für die Verwendung eines Verhütungsimplantats.
            pflaster = None # Standardwert für die Verwendung eines Verhütungspflasters.
            ring = None # Standardwert für die Verwendung eines Verhütungsrings.

            # Prüfen, ob das aktuelle Datum ein Periodentag ist.
            if periode is not None:
                gefuehle = "Empfindlich" # An Periodentagen wird die Stimmung als empfindlich festgelegt.
                schmerzen = "Unterleibsschmerzen"# An Periodentagen werden Unterleibsschmerzen simuliert.
                notiz = "Simulierter Periodeneintrag"# Die Standardnotiz wird durch eine Periodennotiz ersetzt.

            # Falls es kein Periodentag ist, wird geprüft, ob die Anzahl
            # der bisherigen Einträge durch 14 teilbar ist.
            #
            # Der Modulo-Operator % liefert den Rest einer Division.
            # Ist der Rest 0, wird ungefähr alle 14 Tage ein müder Tag simuliert.
            elif anzahl_eintraege % 14 == 0:
                gefuehle = "Müde" # An diesem Tag wird Müdigkeit als Gefühl eingetragen.
                schmerzen = "Kopfschmerzen" # Zusätzlich werden Kopfschmerzen simuliert.
                notiz = "Müder Tag mit Kopfschmerzen" # Die Notiz wird entsprechend angepasst.

            # Falls die vorherigen Bedingungen nicht erfüllt sind, wird geprüft,
            # ob die Anzahl der bisherigen Einträge durch 9 teilbar ist.
            #
            # Dadurch wird ungefähr alle neun Tage ein stressiger Tag simuliert.
            elif anzahl_eintraege % 9 == 0:
                gefuehle = "Gestresst" # Das Gefühl wird auf gestresst gesetzt.
                notiz = "Stressiger Tag" # Die Notiz wird entsprechend angepasst.

            # Der tägliche Tracking-Eintrag wird in die Datenbank eingefügt.
            cursor.execute("""
                INSERT INTO daily_entries (
                    user_id,
                    entry_date,
                    period_strength,
                    spotting,
                    feelings,
                    pain,
                    sex_life,
                    note,
                    discharge,
                    skin,
                    digestion,
                    stool,
                    tests,
                    pill,
                    spiral,
                    injection,
                    implant,
                    patch,
                    ring
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                # Die Werte werden in derselben Reihenfolge übergeben,
                # in der die Spalten im SQL-Befehl aufgelistet wurden.
                TEST_USER_ID,
                # Das aktuelle Datum wird in das Format YYYY-MM-DD umgewandelt.
                aktuelles_datum.isoformat(),
                periode,
                schmierblutung,
                gefuehle,
                schmerzen,
                sexleben,
                notiz,
                ausfluss,
                haut,
                verdauung,
                stuhlgang,
                tests,
                pille,
                spirale,
                spritze,
                implantat,
                pflaster,
                ring
            ))

            # Der Zähler der erzeugten Einträge wird um eins erhöht.
            anzahl_eintraege += 1
            # Das aktuelle Datum wird um einen Tag erhöht.
            # Danach beginnt der nächste Schleifendurchlauf.
            aktuelles_datum += timedelta(days=1)

        # Nach dem Erstellen aller Tracking-Einträge wird der Punktestand
        # des Testnutzers an die simulierte Nutzung angepasst.
        cursor.execute("""
            UPDATE users
            SET credit_points = ?
            WHERE id = ?
        """, (
            anzahl_eintraege,
            TEST_USER_ID
        ))

        # Alle vorgenommenen Änderungen werden dauerhaft
        # in der Datenbank gespeichert.
        connection.commit()

        # Trennlinie für eine übersichtlichere Konsolenausgabe.
        print("---------------------------------------")
        # Bestätigung, dass die Testdaten erfolgreich eingefügt wurden.
        print("Testdaten wurden erfolgreich eingefügt.")
        # Ausgabe der ID des Testnutzers.
        print("User-ID: " + str(TEST_USER_ID))
        # Ausgabe der Anzahl der erstellten täglichen Einträge.
        print("Daily Entries: " + str(anzahl_eintraege))
        # Hinweis auf die erwarteten Zykluslängen.
        print("Erwartete Zykluslängen:")
        # Ausgabe der sechs Zykluslängen.
        #
        # Diese ergeben sich aus den Abständen zwischen den sieben Periodenstarts.
        print([28, 29, 28, 28, 29, 28])
        # Abschließende Trennlinie.
        print("---------------------------------------")

    # Dieser Block wird ausgeführt, wenn während einer Datenbankaktion
    # ein SQLite-Fehler auftritt.
    except sqlite3.Error as fehler:
        # Alle Änderungen seit dem letzten commit() werden rückgängig gemacht.
        # Dadurch werden keine unvollständigen Testdaten gespeichert.
        connection.rollback()
        # Die Fehlermeldung wird zusammen mit dem konkreten Fehler ausgegeben.
        print("Fehler beim Einfügen der Testdaten:", fehler)

    # Der finally-Block wird immer ausgeführt.
    # Dabei spielt es keine Rolle, ob der Vorgang erfolgreich war
    # oder ein Fehler aufgetreten ist.
    finally:
        # Die Verbindung zur Datenbank wird ordentlich geschlossen.
        connection.close()


if __name__ == "__main__":
    testdaten_einfuegen()