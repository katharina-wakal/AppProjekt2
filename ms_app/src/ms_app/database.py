"""
Datenbankmodul der FemHealth-App.

Diese Datei bildet die zentrale Verbindung zwischen der grafischen Oberfläche
und der SQLite-Datenbank 'femhealth.db'. Alle anderen Programmteile rufen
die hier definierten Funktionen auf, um Daten zu speichern, zu laden, zu
ändern oder zu löschen.

Die Datei ist bewusst als Funktionsmodul aufgebaut. Eine eigene Datenbankklasse
ist für die aktuelle Projektgröße nicht zwingend notwendig, weil jede Funktion
nur kurz eine Verbindung öffnet, ihre Abfrage ausführt und die Verbindung danach
wieder schließt.
"""
import sqlite3
from pathlib import Path

from datetime import datetime

# Ordner, in dem sich diese database.py-Datei befindet
BASE_DIR = Path(__file__).resolve().parent

# Vollständiger Pfad zur Datenbankdatei
DB_PATH = BASE_DIR / "femhealth.db"

# =============================================================================
# 1. DATENBANKVERBINDUNG UND TABELLENSTRUKTUR
# =============================================================================
def create_connection():
    """
        Öffnet eine neue Verbindung zur SQLite-Datenbank.

        Jede Datenbankfunktion ruft diese Hilfsfunktion auf. Dadurch muss der
        Verbindungsaufbau nicht an vielen Stellen unterschiedlich geschrieben
        werden.

        Returns:
            sqlite3.Connection: Eine geöffnete Verbindung zu ''femhealth.db''.
        """
    # sqlite3.connect öffnet die vorhandene Datenbankdatei. Existiert sie noch
    # nicht, legt SQLite automatisch eine neue Datei mit diesem Namen an.
    connection = sqlite3.connect(str(DB_PATH))

    # Die geöffnete Verbindung wird an die aufrufende Funktion zurückgegeben.
    return connection


def create_tables():
    """
        Erstellt alle Tabellen, die von der FemHealth-App benötigt werden.

        Durch ``CREATE TABLE IF NOT EXISTS`` werden die Tabellen nur dann neu
        angelegt, wenn sie noch nicht vorhanden sind. Bereits gespeicherte Daten
        werden deshalb beim nächsten Programmstart nicht überschrieben.

        Erstellt werden:
            - ''users'' für Benutzerkonten,
            - ''daily_entries'' für tägliche Tracking-Einträge,
            - ''doctor_appointments'' für Arzttermine,
            - ''user_settings'' für persönliche App-Einstellungen.
        """
    # Eine Verbindung zur Datenbank wird geöffnet.
    connection = create_connection()

    # Der Cursor führt die SQL-Befehle innerhalb der Verbindung aus.
    cursor = connection.cursor()

    # Die Tabelle users speichert alle Informationen eines Benutzerkontos.
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

    # Die Tabelle daily_entries speichert sämtliche Angaben, die ein Benutzer
    # für einen bestimmten Kalendertag im Tracking-Bereich auswählt.
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

    # Die Tabelle doctor_appointments enthält gespeicherte Arzttermine und die
    # dazugehörigen Informationen wie Erinnerung, Notizen und Nachsorge.
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

    # Die Tabelle user_settings speichert individuelle Einstellungen eines
    # Benutzers. Durch UNIQUE darf es pro Benutzer nur einen Datensatz geben.
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
    # commit bestätigt alle zuvor ausgeführten Änderungen dauerhaft.
    connection.commit()

    # Die Verbindung wird geschlossen, weil sie nicht mehr benötigt wird.
    connection.close()

def credit_spalten_ergaenzen():
    """
        Ergänzt ältere users-Tabellen um die Spalten für das Punktesystem.

        Diese Funktion ist eine kleine Datenbankmigration. Sie ist notwendig, wenn
        die Datenbank bereits existierte, bevor 'credit_points' und
        'advanced_analysis_unlocked' in 'create_tables' ergänzt wurden.
        """
    # Eine neue Datenbankverbindung wird geöffnet.
    connection = create_connection()

    # Ein Cursor wird zum Ausführen der SQL-Befehle erzeugt.
    cursor = connection.cursor()

    # PRAGMA table_info(users) liefert Informationen über alle vorhandenen
    # Spalten der Tabelle users.
    cursor.execute("PRAGMA table_info(users)")

    # Aus jedem zurückgegebenen Spalten-Datensatz wird der Spaltenname an
    # Position 1 ausgelesen und in einer Liste gesammelt.
    vorhandene_spalten = [
        spalte[1]
        for spalte in cursor.fetchall()
    ]
    # Nur wenn credit_points noch nicht existiert, wird die Spalte ergänzt.
    if "credit_points" not in vorhandene_spalten:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN credit_points INTEGER NOT NULL DEFAULT 0
        """)

    # Auch die Freischaltungs-Spalte wird nur bei Bedarf hinzugefügt.
    if "advanced_analysis_unlocked" not in vorhandene_spalten:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN advanced_analysis_unlocked INTEGER NOT NULL DEFAULT 0
        """)
    # Die Änderungen an der Tabellenstruktur werden gespeichert.
    connection.commit()
    # Anschließend wird die Verbindung geschlossen.
    connection.close()

# Beim Import dieser Datei werden zunächst alle benötigten Tabellen angelegt.
create_tables()
# Danach werden ältere Datenbanken bei Bedarf um die Credit-Spalten ergänzt.
credit_spalten_ergaenzen()
# Diese Konsolenausgabe bestätigt, dass die Initialisierung ausgeführt wurde.
print("Datenbank wurde erfolgreich erstellt.")

# =============================================================================
# 2. BENUTZERKONTO UND ANMELDUNG
# =============================================================================

def user_anlegen(
    vorname,nachname,geburtsdatum,email,
    password_hash,datenschutz,newsletter):
    """
    Legt ein neues Benutzerkonto in der Tabelle users an.

    Args:
        vorname (str): Vorname des neuen Benutzers.
        nachname (str): Nachname des neuen Benutzers.
        geburtsdatum (str): Geburtsdatum als Text.
        email (str): E-Mail-Adresse; sie muss in der Tabelle eindeutig sein.
        password_hash (str): Gehashte und nicht im Klartext gespeicherte Version
            des Passworts.
        datenschutz (int | bool): Gibt an, ob die Datenschutzerklärung
            akzeptiert wurde.
        newsletter (int | bool): Gibt an, ob der Newsletter gewünscht ist.

    Returns:
        None

    Möglicher Fehler:
        sqlite3.IntegrityError: Kann beispielsweise entstehen, wenn dieselbe
            E-Mail-Adresse bereits gespeichert ist.
    """
    connection = create_connection()# Die Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Der Cursor wird für den INSERT-Befehl benötigt.

    # Der neue Benutzer wird mit Platzhaltern eingefügt. Die Fragezeichen
    # verhindern, dass Eingaben direkt in den SQL-Text eingesetzt werden.
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

    connection.commit()# Der neue Datensatz wird dauerhaft gespeichert.
    connection.close()# Nach dem Speichern wird die Datenbankverbindung geschlossen.

def login_pruefen(email, passwort_hash):
    """
        Prüft, ob E-Mail-Adresse und Passwort-Hash zu einem Benutzer gehören.

        Args:
            email (str): Die beim Login eingegebene E-Mail-Adresse.
            passwort_hash (str): Der Hash des eingegebenen Passworts.

        Returns:
            tuple | None: Bei erfolgreichem Login werden Benutzer-ID, Vorname,
            Nachname und E-Mail als Tupel zurückgegeben. Bei falschen Zugangsdaten
            wird 'None' zurückgegeben.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird hergestellt.
    cursor = connection.cursor()# Über den Cursor wird die SELECT-Abfrage ausgeführt.

    # Es wird nach einem Benutzer gesucht, bei dem sowohl die E-Mail-Adresse
    # als auch der gespeicherte Passwort-Hash übereinstimmen.
    cursor.execute("""
        SELECT id, first_name, last_name, email
        FROM users
        WHERE email = ? AND password_hash = ?
    """, (email, passwort_hash))

    # fetchone liefert den ersten Treffer oder None, wenn kein Treffer vorliegt.
    user = cursor.fetchone()
    connection.close()# Die Verbindung wird nach der Abfrage geschlossen.

    # Das gefundene Benutzer-Tupel beziehungsweise None wird zurückgegeben.
    return user

# =============================================================================
# 3. TÄGLICHE TRACKING-EINTRÄGE
# =============================================================================

def eintrag_speichern(
    user_id,datum,periode,schmierblutung,gefuehle,schmerzen,sexleben,
    notiz,ausfluss,haut,verdauung,stuhlgang,tests,pille,spirale,
    spritze,implantat,pflaster,ring):
    """
        Speichert oder aktualisiert den Tracking-Eintrag eines bestimmten Tages.

        Zuerst wird geprüft, ob für den Benutzer und das Datum bereits ein Eintrag
        existiert. Existiert noch keiner, wird ein neuer Datensatz angelegt und der
        Benutzer erhält einen Credit-Punkt. Existiert bereits ein Datensatz, werden
        dessen Werte aktualisiert; dafür wird kein weiterer Punkt vergeben.

        Args:
            user_id (int): ID des angemeldeten Benutzers.
            datum (str): Datum des Eintrags im Format ``YYYY-MM-DD``.
            periode (str | None): Ausgewählte Stärke der Periode.
            schmierblutung (str | None): Angabe zu Schmierblutungen.
            gefuehle (str | None): Ausgewählte Gefühle oder Stimmung.
            schmerzen (str | None): Ausgewählte Schmerzen.
            sexleben (str | None): Angaben zum Sexualleben.
            notiz (str | None): Freie persönliche Notiz.
            ausfluss (str | None): Angabe zum Ausfluss.
            haut (str | None): Angabe zum Hautzustand.
            verdauung (str | None): Angabe zur Verdauung.
            stuhlgang (str | None): Angabe zum Stuhlgang.
            tests (str | None): Eingetragene Tests.
            pille (str | None): Angabe zur Pille.
            spirale (str | None): Angabe zur Spirale.
            spritze (str | None): Angabe zur Verhütungsspritze.
            implantat (str | None): Angabe zum Implantat.
            pflaster (str | None): Angabe zum Verhütungspflaster.
            ring (str | None): Angabe zum Verhütungsring.
        """
    connection = create_connection()# Eine neue Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für die folgenden SQL-Abfragen erstellt.

    # Zuerst wird geprüft, ob für diesen Benutzer an diesem Datum bereits ein
    # Tracking-Datensatz vorhanden ist.
    cursor.execute("""
        SELECT id
        FROM daily_entries
        WHERE user_id = ?
        AND entry_date = ?
    """, (user_id, datum))

    # Der vorhandene Datensatz wird geladen; ohne Treffer ist der Wert None.
    vorhandener_eintrag = cursor.fetchone()

    # Nur wenn noch kein Datensatz existiert, wird ein neuer Eintrag angelegt.
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
            user_id,datum,periode,schmierblutung,gefuehle,
            schmerzen,sexleben,notiz,ausfluss,haut,verdauung,
            stuhlgang,tests,pille,spirale,spritze,implantat,
            pflaster,ring))

        # Für einen wirklich neuen Tages-Eintrag wird der Punktestand des
        # Benutzers um genau einen Credit-Punkt erhöht.
        cursor.execute("""
                       UPDATE users
                       SET credit_points = credit_points + 1
                       WHERE id = ?
                       """, (user_id,))

    # Wenn bereits ein Eintrag vorhanden ist, wird dieser aktualisiert.
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

    connection.commit()# Unabhängig von INSERT oder UPDATE werden die Änderungen gespeichert.
    connection.close()# Danach wird die Datenbankverbindung geschlossen.

def perioden_tage_laden(user_id):
    """
        Lädt alle Kalendertage, an denen eine Periodenstärke eingetragen wurde.

        Args:
            user_id (int): ID des Benutzers, dessen Periodentage geladen werden.

        Returns:
            list[str]: Liste aller gespeicherten Periodentage als Datumstexte.
        """
    connection = create_connection()# Die Verbindung zur SQLite-Datenbank wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für die SELECT-Abfrage erstellt.

    # Es werden nur Einträge berücksichtigt, deren period_strength weder NULL
    # noch ein leerer Text ist.
    cursor.execute("""
        SELECT entry_date
        FROM daily_entries
        WHERE user_id = ?
        AND period_strength IS NOT NULL
        AND period_strength != ''
        ORDER BY entry_date ASC
    """, (user_id,))

    # fetchall liefert alle passenden Datensätze als Liste von Tupeln.
    daten = cursor.fetchall()

    connection.close()# Die Datenbankverbindung wird nach dem Laden geschlossen.

    # In dieser Liste werden später nur die Datumswerte gesammelt.
    tage = []

    # Jeder Datenbanktreffer besteht hier aus einem Tupel mit einem Datum.
    for eintrag in daten:
        # Der erste Wert des Tupels ist entry_date und wird angehängt.
        tage.append(eintrag[0])

    # Die fertige Liste aller Periodentage wird zurückgegeben.
    return tage

def eintrag_fuer_tag_laden(user_id, datum):
    """
        Lädt sämtliche Tracking-Angaben eines Benutzers für ein bestimmtes Datum.

        Diese Funktion wird beispielsweise benötigt, um einen gespeicherten Tag im
        Kalender oder in einer Detailansicht darzustellen.

        Args:
            user_id (int): ID des angemeldeten Benutzers.
            datum (str): Gesuchtes Datum im Format ``YYYY-MM-DD``.

        Returns:
            tuple | None: Die 17 gespeicherten Tracking-Felder oder ``None``, wenn
            für diesen Tag kein Eintrag existiert.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Über diesen Cursor wird die SELECT-Abfrage ausgeführt.

    # Alle in der Benutzeroberfläche benötigten Tracking-Felder werden für den
    # ausgewählten Benutzer und Tag geladen.
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

    # Da es pro Benutzer und Datum nur einen relevanten Eintrag geben soll,
    # wird lediglich der erste Treffer geladen.
    eintrag = cursor.fetchone()

    connection.close()# Die Verbindung wird nach der Abfrage geschlossen.

    return eintrag# Der Datensatz oder None wird an die aufrufende Datei zurückgegeben.

def eintrag_fuer_bearbeitung_laden(user_id, datum):
    """
        Lädt einen Tracking-Eintrag, damit er im Eingabefenster bearbeitet wird.

        Inhaltlich führt diese Funktion aktuell dieselbe Abfrage wie
        'eintrag_fuer_tag_laden' aus. Der eigene Name macht jedoch deutlich, dass
        der Datensatz in diesem Fall für die Bearbeitungsansicht benötigt wird.

        Args:
            user_id (int): ID des angemeldeten Benutzers.
            datum (str): Zu bearbeitendes Datum im Format 'YYYY-MM-DD'

        Returns:
            tuple | None: Die gespeicherten Tracking-Werte oder 'None'
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird hergestellt.
    cursor = connection.cursor()# Der Cursor führt die folgende SQL-Abfrage aus.

    # Es werden dieselben 17 Tracking-Felder wie in der Tagesansicht geladen.
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

    # fetchone liefert den passenden Tagesdatensatz oder None.
    eintrag = cursor.fetchone()

    connection.close()# Nach der Abfrage wird die Verbindung geschlossen.
    return eintrag# Der geladene Datensatz wird zurückgegeben.

def tracking_daten_laden(user_id):
    """
        Lädt die vollständige Tracking-Historie eines Benutzers.

        Die Daten werden chronologisch nach dem Eintragsdatum sortiert. Diese
        Funktion eignet sich insbesondere für den Export oder umfangreiche
        Auswertungen.

        Args:
            user_id (int): ID des Benutzers.

        Returns:
            list[tuple]: Liste aller Tracking-Datensätze des Benutzers.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Der Cursor wird für die SELECT-Abfrage benötigt.

    # Es werden das Datum und alle 17 Tracking-Felder geladen.
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

    daten = cursor.fetchall()# Alle passenden Datensätze werden gleichzeitig geladen.
    connection.close()# Die Verbindung wird danach geschlossen.

    return daten# Die Liste der Tupel wird an die aufrufende Funktion zurückgegeben.
# =============================================================================
# 4. ZYKLUSBERECHNUNGEN UND ANALYSE
# =============================================================================

def periodenstarts_laden(user_id):
    """
        Ermittelt aus allen Periodentagen die einzelnen Periodenstarts.

        Mehrere aufeinanderfolgende Periodentage gehören zur gleichen Periode. Ein
        Datum wird daher nur als neuer Periodenstart gewertet, wenn mindestens
        21 Tage seit dem zuletzt erkannten Start vergangen sind.

        Args:
            user_id (int): ID des Benutzers.

        Returns:
            list[str]: Erkannte Periodenstarts im Format 'YYYY-MM-DD'.
        """
    # Alle gespeicherten Periodentage über die vorhandene Funktion laden.
    perioden_tage = perioden_tage_laden(user_id)

    # Wenn überhaupt keine Periodentage gespeichert sind, gibt es auch keine
    # Periodenstarts; die Funktion endet sofort mit einer leeren Liste.
    if len(perioden_tage) == 0:
        return []

    periodenstarts = []# Diese Liste enthält am Ende nur den ersten Tag jedes erkannten Zyklus.

    letzter_periodenstart = None# Zu Beginn wurde noch kein vorheriger Periodenstart verarbeitet.

    # Alle gespeicherten Periodentage werden chronologisch durchlaufen.
    for datum_text in perioden_tage:
        # Der Datumstext wird in ein echtes date-Objekt umgewandelt, damit
        # Zeitabstände in Tagen berechnet werden können.
        aktuelles_datum = datetime.strptime(datum_text, "%Y-%m-%d").date()

        # Das erste vorhandene Periodendatum ist automatisch ein Periodenstart.
        if letzter_periodenstart is None:
            # Der ursprüngliche Datumstext wird in die Ergebnisliste übernommen.
            periodenstarts.append(datum_text)

            # Dieses Datum dient ab jetzt als Vergleichswert.
            letzter_periodenstart = aktuelles_datum

        # Für alle weiteren Periodentage wird der Abstand geprüft.
        else:
            # Die Differenz zum zuletzt erkannten Periodenstart wird berechnet.
            unterschied = (aktuelles_datum - letzter_periodenstart).days

            # Erst ab einem Abstand von 21 Tagen wird ein neuer Zyklus erkannt.
            if unterschied >= 21:
                # Der aktuelle Tag wird als neuer Periodenstart gespeichert.
                periodenstarts.append(datum_text)

                # Der Vergleichswert wird auf den neuen Start gesetzt.
                letzter_periodenstart = aktuelles_datum

    return periodenstarts # Die Liste aller erkannten Periodenstarts wird zurückgegeben.

def zykluslaengen_laden(user_id):
    """
        Berechnet die Zykluslängen aus den erkannten Periodenstarts.

        Die Zykluslänge entspricht dem Abstand zwischen zwei aufeinanderfolgenden
        Periodenstarts.

        Args:
            user_id (int): ID des Benutzers.

        Returns:
            list[int]: Zykluslängen in ganzen Tagen.
        """
    # Zuerst werden alle erkannten Periodenstarts des Benutzers geladen.
    periodenstarts = periodenstarts_laden(user_id)

    zykluslaengen = []# In dieser Liste werden die berechneten Abstände gespeichert.

    # Die Schleife beginnt bei Index 1, weil immer ein aktueller und ein direkt
    # davorliegender Periodenstart miteinander verglichen werden müssen.
    for i in range(1, len(periodenstarts)):
        # Der vorherige Periodenstart wird vom Text in ein date-Objekt umgewandelt.
        start_vorher = datetime.strptime(
            periodenstarts[i - 1],
            "%Y-%m-%d").date()

        # Auch der aktuelle Periodenstart wird in ein date-Objekt umgewandelt.
        start_aktuell = datetime.strptime(
            periodenstarts[i],
            "%Y-%m-%d").date()

        # Durch Subtraktion wird die Anzahl der Tage zwischen beiden Starts ermittelt.
        differenz = (start_aktuell - start_vorher).days
        # Die berechnete Zykluslänge wird der Ergebnisliste hinzugefügt.
        zykluslaengen.append(differenz)

    return zykluslaengen# Alle berechneten Zykluslängen werden zurückgegeben.

def perioden_dauer_laden(user_id):
    """
        Berechnet die Dauer jeder gespeicherten Menstruation.

        Aufeinanderfolgende Kalendertage mit eingetragener Periodenstärke werden zu
        einer Periode zusammengefasst. Sobald zwischen zwei Einträgen mehr als ein
        Tag liegt, beginnt eine neue Periode.

        Args:
            user_id (int): ID des Benutzers.

        Returns:
            list[int]: Dauer jeder erkannten Periode in Tagen.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Der Cursor wird für die folgende SELECT-Abfrage erzeugt.

    # Alle Periodentage werden in aufsteigender Datumsreihenfolge geladen.
    cursor.execute("""
        SELECT entry_date
        FROM daily_entries
        WHERE user_id = ?
        AND period_strength IS NOT NULL
        AND period_strength != ''
        ORDER BY entry_date ASC
    """, (user_id,))

    daten = cursor.fetchall()# Alle passenden Datumstupel werden geladen.
    connection.close()# Die Verbindung wird geschlossen, da keine weitere Abfrage folgt.

    # Ohne gespeicherte Periodentage können keine Periodendauern berechnet werden.
    if len(daten) == 0:
        return []

    # In dieser Liste werden die Datumstexte als date-Objekte gespeichert.
    tage = []

    # Jeder geladene Datenbankeintrag wird umgewandelt.
    for eintrag in daten:
        tage.append(
            datetime.strptime(eintrag[0], "%Y-%m-%d").date()
        )

    # Diese Liste nimmt die abgeschlossenen Periodendauern auf.
    dauern = []
    # Der erste gefundene Periodentag zählt bereits als ein Tag Dauer.
    aktuelle_dauer = 1

    # Ab dem zweiten Datum wird jeder Tag mit seinem Vorgänger verglichen.
    for i in range(1, len(tage)):
        # Der Abstand zwischen dem aktuellen und dem vorherigen Tag wird berechnet.
        unterschied = (tage[i] - tage[i - 1]).days

        # Bei gleichem oder direkt folgendem Tag gehört der Eintrag zur gleichen Periode.
        if unterschied <= 1:
            aktuelle_dauer += 1

        # Bei einem größeren Abstand ist die vorherige Periode beendet.
        else:
            # Die abgeschlossene Dauer wird in der Ergebnisliste gespeichert.
            dauern.append(aktuelle_dauer)
            # Für die neue Periode beginnt die Dauer wieder bei einem Tag.
            aktuelle_dauer = 1

    # Nach Ende der Schleife muss auch die zuletzt laufende Periode gespeichert werden.
    dauern.append(aktuelle_dauer)

    return dauern# Die Liste aller Periodendauern wird zurückgegeben.

# =============================================================================
# 5. ARZTTERMINE
# =============================================================================

def arzttermin_speichern(
    user_id, doctor_name,doctor_type,location,appointment_date,
    appointment_time,reminder,notes,preparation,result,follow_up_needed):
    """
        Speichert einen neuen Arzttermin für einen Benutzer.

        Args:
            user_id (int): ID des Benutzers, dem der Termin gehört.
            doctor_name (str): Name der Ärztin oder des Arztes.
            doctor_type (str): Fachrichtung oder Art der Praxis.
            location (str | None): Ort des Termins.
            appointment_date (str): Datum des Termins.
            appointment_time (str): Uhrzeit des Termins.
            reminder (str | None): Gewählte Erinnerung.
            notes (str | None): Freie Notizen zum Termin.
            preparation (str | None): Hinweise zur Vorbereitung.
            result (str | None): Ergebnis oder Nachtrag zum Termin.
            follow_up_needed (int | bool): Gibt an, ob eine Nachsorge nötig ist.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Der Cursor wird für den INSERT-Befehl erzeugt.

    # Alle übergebenen Termindaten werden in doctor_appointments eingefügt.
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
        user_id,doctor_name,doctor_type,location,appointment_date,
        appointment_time,reminder,notes,preparation,result,follow_up_needed))

    connection.commit()# Der neue Arzttermin wird dauerhaft gespeichert.
    connection.close()# Die Verbindung wird anschließend geschlossen.

# =============================================================================
# 6. BENUTZERDATEN UND CREDIT-SYSTEM
# =============================================================================

def user_vorname_laden(user_id):
    """
        Lädt den Vornamen eines Benutzers.

        Args:
            user_id (int): ID des gesuchten Benutzers.

        Returns:
            str: Vorname des Benutzers oder ein leerer Text, wenn keine passende ID
            gefunden wurde.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird aufgebaut.
    cursor = connection.cursor()# Ein Cursor wird für die SELECT-Abfrage erstellt.

    # Der Vorname des Benutzers mit der angegebenen ID wird geladen.
    cursor.execute("""
        SELECT first_name
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()# fetchone liefert ein Tupel mit dem Vornamen oder None.
    connection.close()# Nach der Abfrage wird die Verbindung geschlossen.

    # Wenn keine Benutzer-ID gefunden wurde, wird ein leerer Text zurückgegeben.
    if daten is None:
        return ""

    return daten[0]# Der Vorname befindet sich an Position 0 des Ergebnis-Tupels.

def user_email_laden(user_id):
    """
        Lädt die E-Mail-Adresse eines Benutzers.

        Args:
            user_id (int): ID des gesuchten Benutzers.

        Returns:
            str: E-Mail-Adresse oder ein leerer Text, wenn der Benutzer nicht
            gefunden wurde.
        """
    connection = create_connection()# Eine Datenbankverbindung wird geöffnet.
    cursor = connection.cursor()# Der Cursor führt die Abfrage aus.

    # Die E-Mail-Adresse des Benutzers wird anhand seiner ID gesucht.
    cursor.execute("""
        SELECT email
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()# Der erste Treffer wird geladen.
    connection.close()# Danach wird die Verbindung geschlossen.

    # Ohne Treffer wird ein leerer Text geliefert.
    if daten is None:
        return ""

    return daten[0]# Die E-Mail befindet sich an Position 0 des Tupels.

def credit_points_laden(user_id):
    """
        Lädt den aktuellen Credit-Punktestand eines Benutzers.

        Args:
            user_id (int): ID des Benutzers.

        Returns:
            int: Gespeicherter Punktestand oder 0, wenn der Benutzer nicht existiert.
        """
    connection = create_connection()# Die Datenbankverbindung wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für die Abfrage erzeugt.

    # Der Wert der Spalte credit_points wird geladen.
    cursor.execute("""
        SELECT credit_points
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()# Der passende Datensatz wird abgefragt.
    connection.close()# Die Verbindung wird geschlossen.

    # Falls kein Benutzer gefunden wurde, wird ein neutraler Punktestand geliefert.
    if daten is None:
        return 0

    return daten[0]# Der eigentliche Integer-Wert steht an Position 0.

def analysen_freigeschaltet_laden(user_id):
    """
        Prüft, ob die erweiterten Analysen eines Benutzers freigeschaltet sind.

        Args:
            user_id (int): ID des Benutzers.

        Returns:
            bool: 'True' bei Freischaltung, andernfalls 'False'.
        """
    connection = create_connection()# Die Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für die SELECT-Abfrage erstellt.

    # Der gespeicherte Freischaltungswert wird aus der users-Tabelle geladen.
    cursor.execute("""
        SELECT advanced_analysis_unlocked
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()# Das Ergebnis wird als Tupel oder None geladen.
    connection.close()# Die Verbindung wird nach der Abfrage geschlossen.

    # Existiert der Benutzer nicht, gelten die Analysen als nicht freigeschaltet.
    if daten is None:
        return False

    # SQLite speichert den booleschen Zustand als 0 oder 1.
    return daten[0] == 1

def erweiterte_analysen_freischalten(user_id):
    """
        Schaltet die erweiterten Analysen gegen 60 Credit-Punkte frei.

        Bereits freigeschaltete Benutzer behalten den Zugriff, ohne erneut Punkte zu
        verlieren. Bei weniger als 60 Punkten wird keine Änderung vorgenommen.

        Args:
            user_id (int): ID des Benutzers.

        Returns:
            bool: 'True', wenn die Analyse bereits freigeschaltet war oder jetzt
            erfolgreich freigeschaltet wurde. Andernfalls ``False``.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für die Abfragen erstellt.

    # Punktestand und bisheriger Freischaltungsstatus werden gemeinsam geladen.
    cursor.execute("""
        SELECT credit_points, advanced_analysis_unlocked
        FROM users
        WHERE id = ?
    """, (user_id,))

    daten = cursor.fetchone()# Der Datensatz des Benutzers wird abgerufen.

    # Wenn kein Benutzer existiert, wird die Verbindung geschlossen und False geliefert.
    if daten is None:
        connection.close()
        return False

    # Der Punktestand befindet sich an der ersten Position des Tupels.
    credit_points = daten[0]
    # Der Freischaltungsstatus befindet sich an der zweiten Position.
    bereits_freigeschaltet = daten[1]

    # Bei bestehender Freischaltung sind keine weiteren Änderungen notwendig.
    if bereits_freigeschaltet == 1:
        connection.close()
        return True

    # Reichen die Punkte nicht aus, wird ebenfalls nichts verändert.
    if credit_points < 60:
        connection.close()
        return False

    # Bei ausreichendem Punktestand werden 60 Punkte abgezogen und die Analyse
    # gleichzeitig als freigeschaltet markiert.
    cursor.execute("""
        UPDATE users
        SET
            credit_points = credit_points - 60,
            advanced_analysis_unlocked = 1
        WHERE id = ?
    """, (user_id,))

    connection.commit()# Die Änderung wird dauerhaft gespeichert.
    connection.close()# Danach wird die Verbindung geschlossen.

    return True# True signalisiert die erfolgreiche Freischaltung.

# =============================================================================
# 7. E-MAIL, PASSWORT UND ACCOUNTVERWALTUNG
# =============================================================================

def email_existiert(email, ausgenommen_user_id=None):
    """
        Prüft unabhängig von Groß- und Kleinschreibung, ob eine E-Mail existiert.

        Beim Ändern einer E-Mail kann die ID des aktuell angemeldeten Benutzers
        ausgenommen werden. Dadurch gilt dessen bisherige eigene Adresse nicht als
        unerlaubtes Duplikat.

        Args:
            email (str): Zu prüfende E-Mail-Adresse.
            ausgenommen_user_id (int | None): Benutzer-ID, die bei der Suche nicht
                berücksichtigt werden soll.

        Returns:
            bool: 'True', wenn ein anderer passender Datensatz gefunden wurde.
        """
    connection = create_connection()# Eine Datenbankverbindung wird geöffnet.
    cursor = connection.cursor() #Der Cursor wird für die bedingte SELECT-Abfrage erstellt.

    # Ohne Ausnahme wird in allen Benutzerkonten gesucht.
    if ausgenommen_user_id is None:
        cursor.execute("""
            SELECT id
            FROM users
            WHERE LOWER(email) = LOWER(?)
        """, (email,))

    # Mit Ausnahme wird die angegebene Benutzer-ID aus der Suche ausgeschlossen.
    else:
        cursor.execute("""
            SELECT id
            FROM users
            WHERE LOWER(email) = LOWER(?)
            AND id != ?
        """, (email, ausgenommen_user_id))

    daten = cursor.fetchone()# Der erste passende Benutzer wird geladen.
    connection.close()# Die Datenbankverbindung wird geschlossen.

    return daten is not None # Ein vorhandener Datensatz ergibt True, None ergibt False.


def email_aendern(user_id, neue_email):
    """
        Ändert die E-Mail-Adresse eines Benutzerkontos.

        Ein möglicher UNIQUE-Konflikt wird abgefangen. Dadurch stürzt die App nicht
        ab, wenn die neue E-Mail-Adresse bereits zu einem anderen Konto gehört.

        Args:
            user_id (int): ID des zu ändernden Benutzers.
            neue_email (str): Neue E-Mail-Adresse.

        Returns:
            bool: 'True' bei erfolgreicher Änderung, sonst 'False'
        """
    connection = create_connection()# Die Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Der Cursor wird für das UPDATE benötigt.

    # Der potenziell fehlerhafte Datenbankvorgang wird überwacht.
    try:
        # Die E-Mail-Adresse des angegebenen Benutzers wird aktualisiert.
        cursor.execute("""
            UPDATE users
            SET email = ?
            WHERE id = ?
        """, (neue_email, user_id))

        connection.commit()# Die Änderung wird dauerhaft gespeichert.

        # Prüfen, ob überhaupt ein Benutzer aktualisiert wurde
        # rowcount ist größer als 0, wenn tatsächlich ein Benutzer geändert wurde.
        erfolgreich = cursor.rowcount > 0

    # Ein IntegrityError entsteht insbesondere bei einer bereits verwendeten E-Mail.
    except sqlite3.IntegrityError:
        erfolgreich = False

    # Der finally-Block wird sowohl bei Erfolg als auch bei einem Fehler ausgeführt.
    finally:
        connection.close()# Die Verbindung wird deshalb garantiert geschlossen.

    return erfolgreich# Das Ergebnis der Änderung wird an die aufrufende Datei zurückgegeben.

def passwort_pruefen(user_id, passwort_hash):
    """
        Prüft, ob ein Passwort-Hash zum angegebenen Benutzer gehört.

        Diese Funktion wird beispielsweise vor einer Passwortänderung verwendet,
        um das bisherige Passwort zu bestätigen.

        Args:
            user_id (int): ID des Benutzers.
            passwort_hash (str): Zu prüfender Passwort-Hash.

        Returns:
            bool: 'True' bei Übereinstimmung, sonst 'False'.
        """
    connection = create_connection()# Die Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für die Abfrage erstellt.

    # Gesucht wird ein Datensatz, bei dem ID und Passwort-Hash übereinstimmen.
    cursor.execute("""
        SELECT id
        FROM users
        WHERE id = ?
        AND password_hash = ?
    """, (user_id, passwort_hash))

    user = cursor.fetchone()# Der erste passende Benutzer wird geladen.
    connection.close()# Die Verbindung wird geschlossen.

    # Ein vorhandener Datensatz bedeutet, dass das Passwort korrekt ist.
    return user is not None


def passwort_aendern(user_id, neuer_passwort_hash):
    """
        Ersetzt den gespeicherten Passwort-Hash eines Benutzers.

        Args:
            user_id (int): ID des Benutzers.
            neuer_passwort_hash (str): Hash des neuen Passworts.

        Returns:
            bool: 'True', wenn ein Benutzer aktualisiert wurde, sonst 'False'.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für das UPDATE erzeugt.

    # Der bisherige Passwort-Hash wird durch den neuen Hash ersetzt.
    cursor.execute("""
        UPDATE users
        SET password_hash = ?
        WHERE id = ?
    """, (neuer_passwort_hash, user_id))

    connection.commit()# Die Änderung wird gespeichert.

    # rowcount zeigt, ob mindestens eine Tabellenzeile geändert wurde.
    erfolgreich = cursor.rowcount > 0

    connection.close()# Die Datenbankverbindung wird geschlossen.

    return erfolgreich# Der Erfolgsstatus wird zurückgegeben.

def account_loeschen(user_id):
    """
        Löscht ein Benutzerkonto einschließlich aller zugehörigen Daten.

        Die verknüpften Trackingdaten, Arzttermine und Einstellungen werden zuerst
        gelöscht. Anschließend wird der Benutzer selbst entfernt. Tritt ein Fehler
        auf, werden mit ``rollback`` alle Änderungen dieses Vorgangs rückgängig
        gemacht.

        Args:
            user_id (int): ID des vollständig zu löschenden Benutzers.

        Returns:
            bool: 'True', wenn das Benutzerkonto gelöscht wurde, sonst 'False'.
        """
    connection = create_connection()# Eine Datenbankverbindung wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für mehrere DELETE-Befehle erstellt.

    # Der gesamte Löschvorgang wird abgesichert, damit bei einem Fehler keine
    # teilweise gelöschten Kontodaten zurückbleiben.
    try:
        # Zuerst werden alle täglichen Tracking-Einträge des Benutzers gelöscht.
        cursor.execute("""
            DELETE FROM daily_entries
            WHERE user_id = ?
        """, (user_id,))

        # Danach werden alle gespeicherten Arzttermine des Benutzers entfernt.
        cursor.execute("""
            DELETE FROM doctor_appointments
            WHERE user_id = ?
        """, (user_id,))

        # Anschließend werden die App-Einstellungen des Benutzers gelöscht.
        cursor.execute("""
            DELETE FROM user_settings
            WHERE user_id = ?
        """, (user_id,))

        # Der Benutzer selbst wird zuletzt gelöscht, nachdem abhängige Daten weg sind.
        cursor.execute("""
            DELETE FROM users
            WHERE id = ?
        """, (user_id,))

        # rowcount bezieht sich hier auf den letzten DELETE-Befehl für users.
        erfolgreich = cursor.rowcount > 0

        connection.commit()# Alle Löschungen werden gemeinsam dauerhaft bestätigt.
        return erfolgreich# Der Erfolgsstatus wird direkt zurückgegeben.

    # Sämtliche SQLite-Fehler während des Löschvorgangs werden abgefangen.
    except sqlite3.Error as fehler:
        # rollback macht alle seit dem letzten commit erfolgten Änderungen rückgängig.
        connection.rollback()
        # Die Fehlermeldung wird zur Fehlersuche in der Konsole ausgegeben.
        print("Fehler beim Löschen des Accounts:", fehler)
        # False signalisiert, dass der Account nicht vollständig gelöscht wurde.
        return False
    # Der finally-Block läuft unabhängig von Erfolg, Fehler oder return-Anweisung.
    finally:
        connection.close()# Dadurch wird die Datenbankverbindung in jedem Fall geschlossen.

# =============================================================================
# 8. VOLLSTÄNDIGER DATENEXPORT
# =============================================================================

def alle_nutzerdaten_laden(user_id):
    """
        Lädt sämtliche gespeicherten Daten eines Benutzers für einen Datenexport.

        Die Ergebnisse aus mehreren Tabellen werden in ein verschachteltes
        Dictionary umgewandelt. Dadurch können sie beispielsweise leichter als
        JSON-Datei exportiert werden.

        Args:
            user_id (int): ID des Benutzers, dessen Daten exportiert werden sollen.

        Returns:
            dict | None: Dictionary mit Account, täglichen Einträgen, Arztterminen
            und Einstellungen. Wenn kein Benutzer existiert, wird 'None' geliefert.
        """
    connection = create_connection()# Eine Verbindung zur Datenbank wird geöffnet.
    cursor = connection.cursor()# Ein Cursor wird für mehrere SELECT-Abfragen erstellt.

     # Accountdaten laden
    # Aus Datenschutzgründen wird der Passwort-Hash nicht für den Export geladen.
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

    user = cursor.fetchone()# Für eine Benutzer-ID kann höchstens ein Account-Datensatz existieren.

    # Sämtliche Tracking-Einträge werden chronologisch geladen.
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

    tracking_daten = cursor.fetchall()# Alle Tracking-Datensätze werden als Liste von Tupeln gespeichert.

    # Arzttermine laden
    # Alle Arzttermine werden nach Datum und Uhrzeit sortiert geladen.
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

    arzttermine = cursor.fetchall()# Die gefundenen Termine werden als Liste von Tupeln gespeichert.

    # App-Einstellungen laden
    # Da user_id in user_settings UNIQUE ist, kann höchstens ein Datensatz existieren.
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

    einstellungen = cursor.fetchone() # Der Einstellungsdatensatz oder None wird geladen.

    connection.close()# Nach Abschluss aller Abfragen wird die Verbindung geschlossen.

    # Wenn der Account selbst nicht existiert, kann kein Export erstellt werden.
    if user is None:
        return None

    # Diese Namen entsprechen exakt der Reihenfolge der zuvor ausgewählten
    # Account-Spalten und werden später als Dictionary-Schlüssel verwendet.
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

    # Diese Schlüsselnamen entsprechen der Reihenfolge jedes Tracking-Tupels.
    tracking_spalten = [
        "entry_date", "period_strength", "spotting", "feelings","pain",
        "sex_life","note","discharge","skin","digestion","stool",
        "tests","pill","spiral","injection","implant","patch","ring","created_at"]

    # Diese Namen werden mit den Werten jedes Arzttermin-Tupels verknüpft.
    arzttermin_spalten = [
        "doctor_name","doctor_type","location","appointment_date",
        "appointment_time","reminder","notes","preparation",
        "result","follow_up_needed","created_at"]

    # Diese Namen entsprechen den geladenen Einstellungswerten.
    einstellungen_spalten = [
        "face_id_enabled","hide_widget_data","app_lock_enabled",
        "language","design_mode","units","notifications_enabled",
        "created_at", "updated_at"]

    # Das verschachtelte Ergebnis-Dictionary wird aufgebaut und zurückgegeben.
    return {
        # zip verbindet jeden Spaltennamen mit dem passenden Wert des User-Tupels.
        "account": dict(zip(user_spalten, user)),

        # Für jeden Tracking-Datensatz wird ebenfalls ein eigenes Dictionary erzeugt.
        "daily_entries": [
            dict(zip(tracking_spalten, eintrag))
            for eintrag in tracking_daten
        ],
        # Dasselbe Verfahren wird auf alle gespeicherten Arzttermine angewendet.
        "doctor_appointments": [
            dict(zip(arzttermin_spalten, termin))
            for termin in arzttermine
        ],
        # Wenn Einstellungen existieren, werden sie als Dictionary ausgegeben.
        # Ohne Einstellungsdatensatz wird stattdessen ein leeres Dictionary genutzt.
        "settings": (
            dict(zip(einstellungen_spalten, einstellungen))
            if einstellungen is not None
            else {}
        )
    }









