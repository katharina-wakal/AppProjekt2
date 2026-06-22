import sqlite3
from datetime import datetime


DB_NAME = "femhealth.db"


def create_connection():
    connection = sqlite3.connect(DB_NAME)
    return connection


def create_tables():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            privacy_accepted INTEGER NOT NULL,
            newsletter INTEGER DEFAULT 0,
            credit_points INTEGER NOT NULL DEFAULT 0,
            advanced_analysis_unlocked INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            period_strength TEXT,
            spotting TEXT,
            feelings TEXT,
            pain TEXT,
            sex_life TEXT,
            note TEXT,
            discharge TEXT,
            skin TEXT,
            digestion TEXT,
            stool TEXT,
            tests TEXT,
            pill TEXT,
            spiral TEXT,
            injection TEXT,
            implant TEXT,
            patch TEXT,
            ring TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doctor_name TEXT NOT NULL,
            doctor_type TEXT NOT NULL,
            location TEXT,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reminder TEXT,
            notes TEXT,
            preparation TEXT,
            result TEXT,
            follow_up_needed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            face_id_enabled INTEGER DEFAULT 0,
            hide_widget_data INTEGER DEFAULT 0,
            app_lock_enabled INTEGER DEFAULT 0,
            language TEXT DEFAULT 'Deutsch',
            design_mode TEXT DEFAULT 'Hell',
            units TEXT DEFAULT 'Metrisch',
            notifications_enabled INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()

def credit_spalten_ergaenzen():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(users)")
    vorhandene_spalten = [
        spalte[1]
        for spalte in cursor.fetchall()
    ]

    if "credit_points" not in vorhandene_spalten:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN credit_points INTEGER NOT NULL DEFAULT 0
        """)

    if "advanced_analysis_unlocked" not in vorhandene_spalten:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN advanced_analysis_unlocked INTEGER NOT NULL DEFAULT 0
        """)

    connection.commit()
    connection.close()


create_tables()
credit_spalten_ergaenzen()
print("Datenbank wurde erfolgreich erstellt.")

def user_anlegen(
    vorname,
    nachname,
    geburtsdatum,
    email,
    password_hash,
    datenschutz,
    newsletter
):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (
            first_name,
            last_name,
            birth_date,
            email,
            password_hash,
            privacy_accepted,
            newsletter
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        vorname,
        nachname,
        geburtsdatum,
        email,
        password_hash,
        datenschutz,
        newsletter
    ))

    connection.commit()
    connection.close()

def login_pruefen(email, passwort_hash):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, first_name, last_name, email
        FROM users
        WHERE email = ? AND password_hash = ?
    """, (email, passwort_hash))

    user = cursor.fetchone()

    connection.close()

    return user

def eintrag_speichern(
    user_id,
    datum,
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
):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM daily_entries
        WHERE user_id = ?
        AND entry_date = ?
    """, (user_id, datum))

    vorhandener_eintrag = cursor.fetchone()

    if vorhandener_eintrag is None:
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
            user_id,
            datum,
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

        cursor.execute("""
                       UPDATE users
                       SET credit_points = credit_points + 1
                       WHERE id = ?
                       """, (user_id,))

    else:
        cursor.execute("""
            UPDATE daily_entries
            SET
                period_strength = ?,
                spotting = ?,
                feelings = ?,
                pain = ?,
                sex_life = ?,
                note = ?,
                discharge = ?,
                skin = ?,
                digestion = ?,
                stool = ?,
                tests = ?,
                pill = ?,
                spiral = ?,
                injection = ?,
                implant = ?,
                patch = ?,
                ring = ?
            WHERE user_id = ?
            AND entry_date = ?
        """, (
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
            ring,
            user_id,
            datum
        ))

    connection.commit()
    connection.close()

def periodenstarts_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT entry_date
        FROM daily_entries
        WHERE user_id = ?
        AND period_strength IS NOT NULL
        AND period_strength != ''
        ORDER BY entry_date ASC
    """, (user_id,))

    daten = cursor.fetchall()
    connection.close()

    perioden_tage = []

    for eintrag in daten:
        perioden_tage.append(eintrag[0])

    if len(perioden_tage) == 0:
        return []

    periodenstarts = []

    letzter_periodenstart = None

    for datum_text in perioden_tage:
        aktuelles_datum = datetime.strptime(datum_text, "%Y-%m-%d").date()

        if letzter_periodenstart is None:
            periodenstarts.append(datum_text)
            letzter_periodenstart = aktuelles_datum

        else:
            unterschied = (aktuelles_datum - letzter_periodenstart).days

            if unterschied >= 21:
                periodenstarts.append(datum_text)
                letzter_periodenstart = aktuelles_datum

    return periodenstarts

def arzttermin_speichern(
    user_id,
    doctor_name,
    doctor_type,
    location,
    appointment_date,
    appointment_time,
    reminder,
    notes,
    preparation,
    result,
    follow_up_needed
):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO doctor_appointments (
            user_id,
            doctor_name,
            doctor_type,
            location,
            appointment_date,
            appointment_time,
            reminder,
            notes,
            preparation,
            result,
            follow_up_needed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        doctor_name,
        doctor_type,
        location,
        appointment_date,
        appointment_time,
        reminder,
        notes,
        preparation,
        result,
        follow_up_needed
    ))

    connection.commit()
    connection.close()

def perioden_tage_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT entry_date
        FROM daily_entries
        WHERE user_id = ?
        AND period_strength IS NOT NULL
        AND period_strength != ''
    """, (user_id,))

    daten = cursor.fetchall()

    connection.close()

    tage = []

    for eintrag in daten:
        tage.append(eintrag[0])

    return tage

def eintrag_fuer_tag_laden(user_id, datum):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
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
        FROM daily_entries
        WHERE user_id = ?
        AND entry_date = ?
    """, (user_id, datum))

    eintrag = cursor.fetchone()

    connection.close()

    return eintrag

def eintrag_fuer_bearbeitung_laden(user_id, datum):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
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
        FROM daily_entries
        WHERE user_id = ?
        AND entry_date = ?
    """, (user_id, datum))

    eintrag = cursor.fetchone()

    connection.close()

    return eintrag

def zykluslaengen_laden(user_id):
    periodenstarts = periodenstarts_laden(user_id)

    zykluslaengen = []

    for i in range(1, len(periodenstarts)):
        start_vorher = datetime.strptime(
            periodenstarts[i - 1],
            "%Y-%m-%d"
        ).date()

        start_aktuell = datetime.strptime(
            periodenstarts[i],
            "%Y-%m-%d"
        ).date()

        differenz = (start_aktuell - start_vorher).days
        zykluslaengen.append(differenz)

    return zykluslaengen

def perioden_dauer_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT entry_date
        FROM daily_entries
        WHERE user_id = ?
        AND period_strength IS NOT NULL
        AND period_strength != ''
        ORDER BY entry_date ASC
    """, (user_id,))

    daten = cursor.fetchall()
    connection.close()

    if len(daten) == 0:
        return []

    tage = []

    for eintrag in daten:
        tage.append(
            datetime.strptime(eintrag[0], "%Y-%m-%d").date()
        )

    dauern = []
    aktuelle_dauer = 1

    for i in range(1, len(tage)):
        unterschied = (tage[i] - tage[i - 1]).days

        if unterschied <= 1:
            aktuelle_dauer += 1
        else:
            dauern.append(aktuelle_dauer)
            aktuelle_dauer = 1

    dauern.append(aktuelle_dauer)

    return dauern

def user_vorname_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT first_name
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()

    connection.close()

    if daten is None:
        return ""

    return daten[0]

def user_email_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT email
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()
    connection.close()

    if daten is None:
        return ""

    return daten[0]

def credit_points_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT credit_points
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()
    connection.close()

    if daten is None:
        return 0

    return daten[0]

def analysen_freigeschaltet_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT advanced_analysis_unlocked
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()
    connection.close()

    if daten is None:
        return False

    return daten[0] == 1

def erweiterte_analysen_freischalten(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT credit_points, advanced_analysis_unlocked
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()

    if daten is None:
        connection.close()
        return False

    credit_points = daten[0]
    bereits_freigeschaltet = daten[1]

    if bereits_freigeschaltet == 1:
        connection.close()
        return True

    if credit_points < 60:
        connection.close()
        return False

    cursor.execute("""
        UPDATE users
        SET
            credit_points = credit_points - 60,
            advanced_analysis_unlocked = 1
        WHERE id = ?
    """, (user_id,))

    connection.commit()
    connection.close()

    return True


def email_existiert(email, ausgenommen_user_id=None):
    connection = create_connection()
    cursor = connection.cursor()

    if ausgenommen_user_id is None:
        cursor.execute("""
            SELECT id
            FROM users
            WHERE LOWER(email) = LOWER(?)
        """, (email,))
    else:
        cursor.execute("""
            SELECT id
            FROM users
            WHERE LOWER(email) = LOWER(?)
            AND id != ?
        """, (email, ausgenommen_user_id))

    daten = cursor.fetchone()
    connection.close()

    return daten is not None


def email_aendern(user_id, neue_email):
    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE users
            SET email = ?
            WHERE id = ?
        """, (neue_email, user_id))

        connection.commit()

        # Prüfen, ob überhaupt ein Benutzer aktualisiert wurde
        erfolgreich = cursor.rowcount > 0

    except sqlite3.IntegrityError:
        erfolgreich = False

    finally:
        connection.close()

    return erfolgreich

def passwort_pruefen(user_id, passwort_hash):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM users
        WHERE id = ?
        AND password_hash = ?
    """, (user_id, passwort_hash))

    user = cursor.fetchone()
    connection.close()

    return user is not None


def passwort_aendern(user_id, neuer_passwort_hash):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET password_hash = ?
        WHERE id = ?
    """, (neuer_passwort_hash, user_id))

    connection.commit()

    erfolgreich = cursor.rowcount > 0

    connection.close()

    return erfolgreich

def account_loeschen(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Alle zum Account gehörenden Daten löschen
        cursor.execute("""
            DELETE FROM daily_entries
            WHERE user_id = ?
        """, (user_id,))

        cursor.execute("""
            DELETE FROM doctor_appointments
            WHERE user_id = ?
        """, (user_id,))

        cursor.execute("""
            DELETE FROM user_settings
            WHERE user_id = ?
        """, (user_id,))

        # Benutzer zuletzt löschen
        cursor.execute("""
            DELETE FROM users
            WHERE id = ?
        """, (user_id,))

        erfolgreich = cursor.rowcount > 0

        connection.commit()
        return erfolgreich

    except sqlite3.Error as fehler:
        connection.rollback()
        print("Fehler beim Löschen des Accounts:", fehler)
        return False

    finally:
        connection.close()

def tracking_daten_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
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
        FROM daily_entries
        WHERE user_id = ?
        ORDER BY entry_date ASC
    """, (user_id,))

    daten = cursor.fetchall()
    connection.close()

    return daten


def alle_nutzerdaten_laden(user_id):
    connection = create_connection()
    cursor = connection.cursor()

    # Accountdaten
    cursor.execute("""
        SELECT
            id,
            first_name,
            last_name,
            birth_date,
            email,
            privacy_accepted,
            newsletter,
            created_at
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()

    # Trackingdaten
    cursor.execute("""
        SELECT
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
            ring,
            created_at
        FROM daily_entries
        WHERE user_id = ?
        ORDER BY entry_date ASC
    """, (user_id,))

    tracking_daten = cursor.fetchall()

    # Arzttermine
    cursor.execute("""
        SELECT
            doctor_name,
            doctor_type,
            location,
            appointment_date,
            appointment_time,
            reminder,
            notes,
            preparation,
            result,
            follow_up_needed,
            created_at
        FROM doctor_appointments
        WHERE user_id = ?
        ORDER BY appointment_date ASC, appointment_time ASC
    """, (user_id,))

    arzttermine = cursor.fetchall()

    # App-Einstellungen
    cursor.execute("""
        SELECT
            face_id_enabled,
            hide_widget_data,
            app_lock_enabled,
            language,
            design_mode,
            units,
            notifications_enabled,
            created_at,
            updated_at
        FROM user_settings
        WHERE user_id = ?
    """, (user_id,))

    einstellungen = cursor.fetchone()

    connection.close()

    if user is None:
        return None

    user_spalten = [
        "id",
        "first_name",
        "last_name",
        "birth_date",
        "email",
        "privacy_accepted",
        "newsletter",
        "created_at"
    ]

    tracking_spalten = [
        "entry_date",
        "period_strength",
        "spotting",
        "feelings",
        "pain",
        "sex_life",
        "note",
        "discharge",
        "skin",
        "digestion",
        "stool",
        "tests",
        "pill",
        "spiral",
        "injection",
        "implant",
        "patch",
        "ring",
        "created_at"
    ]

    arzttermin_spalten = [
        "doctor_name",
        "doctor_type",
        "location",
        "appointment_date",
        "appointment_time",
        "reminder",
        "notes",
        "preparation",
        "result",
        "follow_up_needed",
        "created_at"
    ]

    einstellungen_spalten = [
        "face_id_enabled",
        "hide_widget_data",
        "app_lock_enabled",
        "language",
        "design_mode",
        "units",
        "notifications_enabled",
        "created_at",
        "updated_at"
    ]

    return {
        "account": dict(zip(user_spalten, user)),
        "daily_entries": [
            dict(zip(tracking_spalten, eintrag))
            for eintrag in tracking_daten
        ],
        "doctor_appointments": [
            dict(zip(arzttermin_spalten, termin))
            for termin in arzttermine
        ],
        "settings": (
            dict(zip(einstellungen_spalten, einstellungen))
            if einstellungen is not None
            else {}
        )
    }









