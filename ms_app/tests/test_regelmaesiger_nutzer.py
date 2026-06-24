"""
Füllt daily_entries für den bereits vorhandenen Testnutzer
mit sechs Monaten simulierten Tracking-Daten.
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path

# Pfad zu deiner echten femhealth.db
DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "ms_app"
    / "femhealth.db"
)


TEST_USER_ID = 5

def create_connection():
    """
    Öffnet eine Verbindung zur vorhandenen FemHealth-Datenbank.
    """
    return sqlite3.connect(str(DB_PATH))

def testdaten_einfuegen():
    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Prüfen, ob der Testnutzer wirklich existiert
        cursor.execute("""
            SELECT id, first_name, last_name, email
            FROM users
            WHERE id = ?
        """, (TEST_USER_ID,))

        nutzer = cursor.fetchone()

        if nutzer is None:
            print(f"Kein Nutzer mit der ID {TEST_USER_ID} gefunden.")
            return

        print(
            f"Testnutzer gefunden: "
            f"{nutzer[1]} {nutzer[2]} ({nutzer[3]})"
        )

        # Bereits vorhandene Tracking-Einträge dieses Nutzers löschen
        cursor.execute("""
            DELETE FROM daily_entries
            WHERE user_id = ?
        """, (TEST_USER_ID,))

        # Periodenstarts:
        # Aus sieben Periodenstarts entstehen sechs berechenbare Zyklen.
        perioden = {
            date(2025, 12, 5): 5,
            date(2026, 1, 2): 5,
            date(2026, 1, 31): 5,
            date(2026, 2, 28): 5,
            date(2026, 3, 28): 5,
            date(2026, 4, 26): 5,
            date(2026, 5, 24): 5
        }

        # Einzelne Periodentage mit passender Stärke erzeugen
        perioden_tage = {}

        for periodenstart, dauer in perioden.items():
            for tag_nummer in range(dauer):
                periodentag = periodenstart + timedelta(days=tag_nummer)

                if tag_nummer == 0:
                    staerke = "Mittel"
                elif tag_nummer == 1:
                    staerke = "Stark"
                elif tag_nummer == 2:
                    staerke = "Mittel"
                else:
                    staerke = "Leicht"

                perioden_tage[periodentag] = staerke

        # Tägliche Einträge über sechs Monate erzeugen
        startdatum = date(2025, 12, 1)
        enddatum = date(2026, 5, 31)

        aktuelles_datum = startdatum
        anzahl_eintraege = 0

        while aktuelles_datum <= enddatum:
            periode = perioden_tage.get(aktuelles_datum)

            schmierblutung = None
            gefuehle = "Ausgeglichen"
            schmerzen = None
            sexleben = None
            notiz = "Simulierter Tracking-Eintrag"
            ausfluss = "Normal"
            haut = "Normal"
            verdauung = "Normal"
            stuhlgang = "Normal"
            tests = None
            pille = None
            spirale = None
            spritze = None
            implantat = None
            pflaster = None
            ring = None

            if periode is not None:
                gefuehle = "Empfindlich"
                schmerzen = "Unterleibsschmerzen"
                notiz = "Simulierter Periodeneintrag"

            elif anzahl_eintraege % 14 == 0:
                gefuehle = "Müde"
                schmerzen = "Kopfschmerzen"
                notiz = "Müder Tag mit Kopfschmerzen"

            elif anzahl_eintraege % 9 == 0:
                gefuehle = "Gestresst"
                notiz = "Stressiger Tag"

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
                TEST_USER_ID,
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

            anzahl_eintraege += 1
            aktuelles_datum += timedelta(days=1)

        # Punktestand passend zur simulierten Nutzung setzen
        cursor.execute("""
            UPDATE users
            SET credit_points = ?
            WHERE id = ?
        """, (
            anzahl_eintraege,
            TEST_USER_ID
        ))

        connection.commit()

        print("---------------------------------------")
        print("Testdaten wurden erfolgreich eingefügt.")
        print(f"User-ID: {TEST_USER_ID}")
        print(f"Daily Entries: {anzahl_eintraege}")
        print("Erwartete Zykluslängen:")
        print([28, 29, 28, 28, 29, 28])
        print("---------------------------------------")

    except sqlite3.Error as fehler:
        connection.rollback()
        print("Fehler beim Einfügen der Testdaten:", fehler)

    finally:
        connection.close()


if __name__ == "__main__":
    testdaten_einfuegen()