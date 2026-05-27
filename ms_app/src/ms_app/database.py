import sqlite3


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


create_tables()
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

    periodenstarts = []

    for eintrag in daten:
        periodenstarts.append(eintrag[0])

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








