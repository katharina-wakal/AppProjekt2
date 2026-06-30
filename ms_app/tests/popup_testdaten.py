"""
Erstellt Testdaten für Nutzer-ID 6.

MODUS = "periode":
Der nächste Periodenbeginn wird für heute prognostiziert.

MODUS = "ovulation":
Die Ovulation wird für heute prognostiziert.
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "ms_app"
    / "femhealth.db"
)

USER_ID = 6

# Hier zwischen "periode" und "ovulation" wechseln.
MODUS = "ovulation"


def testdaten_einfuegen():
    heute = date.today()

    if MODUS == "periode":
        # Letzter Periodenstart war vor 28 Tagen.
        # Bei einem regelmäßigen 28-Tage-Zyklus wird heute
        # als nächster Periodenbeginn prognostiziert.
        abstaende = [196, 168, 140, 112, 84, 56, 28]

    elif MODUS == "ovulation":
        # Letzter Periodenstart war vor 14 Tagen.
        # Der nächste Periodenbeginn liegt in 14 Tagen.
        # Dadurch wird die Ovulation für heute prognostiziert.
        abstaende = [182, 154, 126, 98, 70, 42, 14]

    else:
        print("Ungültiger Modus.")
        return

    periodenstarts = []

    for abstand in abstaende:
        periodenstarts.append(heute - timedelta(days=abstand))

    verbindung = sqlite3.connect(DB_PATH)
    cursor = verbindung.cursor()

    try:
        nutzer = cursor.execute(
            """
            SELECT id, first_name, last_name, email
            FROM users
            WHERE id = ?
            """,
            (USER_ID,)
        ).fetchone()

        if nutzer is None:
            print("Kein Nutzer mit der ID 6 gefunden.")
            return

        print(
            "Testnutzer gefunden:",
            nutzer[1],
            nutzer[2],
            "(" + nutzer[3] + ")"
        )

        # Alle bisherigen Tracking-Einträge von Lena löschen.
        cursor.execute(
            """
            DELETE FROM daily_entries
            WHERE user_id = ?
            """,
            (USER_ID,)
        )

        # Für jeden Periodenstart werden fünf Periodentage angelegt.
        for periodenstart in periodenstarts:
            for tag in range(5):
                eintragsdatum = periodenstart + timedelta(days=tag)

                if tag == 0:
                    staerke = "Mittel"
                elif tag == 1:
                    staerke = "Stark"
                elif tag == 2:
                    staerke = "Mittel"
                else:
                    staerke = "Leicht"

                cursor.execute(
                    """
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
                    """,
                    (
                        USER_ID,
                        eintragsdatum.isoformat(),
                        staerke,
                        0,
                        "Empfindlich",
                        "Leicht",
                        "",
                        "Testdaten für Zyklus-Popup",
                        "",
                        "",
                        "",
                        "",
                        "",
                        0,
                        0,
                        0,
                        0,
                        0,
                        0
                    )
                )

        verbindung.commit()

        print("---------------------------------------")
        print("Testdaten wurden erfolgreich eingefügt.")
        print("Modus:", MODUS)
        print("Heutiges Datum:", heute)
        print("Periodenstarts:")

        for periodenstart in periodenstarts:
            print(periodenstart)

        if MODUS == "periode":
            print("Erwartetes Ergebnis: Perioden-Popup erscheint.")
        else:
            print("Erwartetes Ergebnis: Ovulations-Popup erscheint.")

        print("---------------------------------------")

    except sqlite3.Error as fehler:
        verbindung.rollback()
        print("Fehler beim Einfügen der Testdaten:", fehler)

    finally:
        verbindung.close()


if __name__ == "__main__":
    testdaten_einfuegen()