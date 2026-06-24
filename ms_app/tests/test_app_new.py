"""
Tests für die FemHealth-App.

Getestete Module:
  - calculation.py  → calculate_cycle_prediction()
  - user_db.py      → account_exists(), register_user(), verify_login(), get_user()

Ausführen (aus dem ms_app-Ordner):
    python tests/ms_app.py
  oder direkt:
    pytest tests/ -vv
"""

import sys
import pathlib
import pytest

# Pfad zum Quellcode hinzufügen, damit die Imports funktionieren
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src" / "ms_app"))

from calculation import calculate_cycle_prediction, STANDARD_CYCLE_LENGTH
import user_db


# =============================================================================
# HILFSFUNKTION
# =============================================================================

@pytest.fixture(autouse=True)
def reset_user_db():
    """Setzt die In-Memory-Nutzerdatenbank vor jedem Test zurück."""
    user_db._users.clear()
    yield
    user_db._users.clear()


# =============================================================================
# TESTS: calculation.py – calculate_cycle_prediction()
# =============================================================================

class TestCalculateCyclePrediction:
    """Tests für die Zyklusvorhersage-Berechnung."""

    # ── Einzelner Eintrag (Standardwert) ─────────────────────────────────────

    def test_ein_datum_verwendet_standardwert(self):
        """Bei nur einem Datum wird der Standardzyklus von 28 Tagen genutzt."""
        result = calculate_cycle_prediction(["2024-01-01"])
        assert result["average_cycle"] == STANDARD_CYCLE_LENGTH

    def test_ein_datum_vorhergesagter_start_korrekt(self):
        """Nächste Periode = letzter Start + 28 Tage."""
        from datetime import date
        result = calculate_cycle_prediction(["2024-01-01"])
        assert result["predicted_period_start"] == date(2024, 1, 29)

    def test_ein_datum_keine_zykluslaengen(self):
        """Mit nur einem Datum gibt es noch keine berechneten Zykluslängen."""
        result = calculate_cycle_prediction(["2024-01-01"])
        assert result["cycle_lengths"] == []

    def test_ein_datum_keine_warnung(self):
        """Standardwert 28 liegt im Normalbereich – keine Warnung."""
        result = calculate_cycle_prediction(["2024-01-01"])
        assert result["warning"] is None

    # ── Zwei Einträge ─────────────────────────────────────────────────────────

    def test_zwei_daten_durchschnitt_korrekt(self):
        """Mit zwei Einträgen wird ein echter Durchschnitt berechnet."""
        result = calculate_cycle_prediction(["2024-01-01", "2024-01-29"])
        assert result["average_cycle"] == 28

    def test_zwei_daten_zykluslaenge_gespeichert(self):
        """Die berechnete Zykluslänge wird in der Liste gespeichert."""
        result = calculate_cycle_prediction(["2024-01-01", "2024-01-29"])
        assert result["cycle_lengths"] == [28]

    def test_zwei_daten_prognose_berechnet(self):
        """Nächste Periode = letzter Start + Durchschnitt."""
        from datetime import date
        result = calculate_cycle_prediction(["2024-01-01", "2024-01-29"])
        assert result["predicted_period_start"] == date(2024, 2, 26)

    # ── Mehrere Einträge ──────────────────────────────────────────────────────

    def test_mehrere_daten_durchschnitt_korrekt(self):
        """Durchschnitt aus drei Zyklen korrekt gerundet."""
        # Zykluslängen: 30, 27, 29 → Durchschnitt 28.67 → gerundet 29
        daten = ["2024-01-01", "2024-01-31", "2024-02-27", "2024-03-27"]
        result = calculate_cycle_prediction(daten)
        assert result["average_cycle"] == 29

    def test_reihenfolge_egal(self):
        """Die Funktion sortiert Daten selbst – Reihenfolge spielt keine Rolle."""
        result_sortiert = calculate_cycle_prediction(["2024-01-01", "2024-01-29"])
        result_unsortiert = calculate_cycle_prediction(["2024-01-29", "2024-01-01"])
        assert result_sortiert["average_cycle"] == result_unsortiert["average_cycle"]
        assert result_sortiert["predicted_period_start"] == result_unsortiert["predicted_period_start"]

    # ── Ovulation ─────────────────────────────────────────────────────────────

    def test_ovulation_14_tage_vor_periode(self):
        """Ovulation = 14 Tage vor der vorhergesagten Periode."""
        from datetime import timedelta
        result = calculate_cycle_prediction(["2024-01-01"])
        erwartet = result["predicted_period_start"] - timedelta(days=14)
        assert result["predicted_ovulation"] == erwartet

    # ── Warnung bei ungewöhnlichem Zyklus ────────────────────────────────────

    def test_warnung_bei_kurzem_zyklus(self):
        """Zyklus unter 21 Tagen löst eine Warnung aus."""
        daten = ["2024-01-01", "2024-01-19"]  # 18 Tage
        result = calculate_cycle_prediction(daten)
        assert result["warning"] is not None

    def test_warnung_bei_langem_zyklus(self):
        """Zyklus über 35 Tagen löst eine Warnung aus."""
        daten = ["2024-01-01", "2024-02-10"]  # 40 Tage
        result = calculate_cycle_prediction(daten)
        assert result["warning"] is not None

    def test_keine_warnung_bei_normalem_zyklus(self):
        """Zyklus zwischen 21 und 35 Tagen erzeugt keine Warnung."""
        daten = ["2024-01-01", "2024-01-29"]  # 28 Tage
        result = calculate_cycle_prediction(daten)
        assert result["warning"] is None

    # ── Maximal 6 Zyklen werden berücksichtigt ────────────────────────────────

    def test_alle_zykluslaengen_werden_gespeichert(self):
        """Alle Zykluslängen werden gespeichert, auch wenn >6."""
        daten = [
            "2024-01-01", "2024-01-29", "2024-02-26", "2024-03-25",
            "2024-04-22", "2024-05-20", "2024-06-17", "2024-07-15"
        ]
        result = calculate_cycle_prediction(daten)
        assert len(result["cycle_lengths"]) == 7  # 8 Starts = 7 Zyklen


# =============================================================================
# TESTS: user_db.py
# =============================================================================

class TestUserDb:
    """Tests für die In-Memory-Nutzerdatenbank."""

    # ── account_exists() ──────────────────────────────────────────────────────

    def test_account_exists_nicht_vorhanden(self):
        """Nicht registrierter Account wird als nicht vorhanden erkannt."""
        assert user_db.account_exists("test@example.com") is False

    def test_account_exists_nach_registrierung(self):
        """Nach Registrierung wird der Account gefunden."""
        user_db.register_user("test@example.com", "pw", "Anna", "Müller", "2000-01-01", False)
        assert user_db.account_exists("test@example.com") is True

    def test_account_exists_case_insensitive(self):
        """E-Mail-Vergleich ist case-insensitiv."""
        user_db.register_user("Test@Example.com", "pw", "Anna", "Müller", "2000-01-01", False)
        assert user_db.account_exists("test@example.com") is True
        assert user_db.account_exists("TEST@EXAMPLE.COM") is True

    # ── register_user() ───────────────────────────────────────────────────────

    def test_register_user_speichert_alle_daten(self):
        """Alle Nutzerdaten werden korrekt gespeichert."""
        user_db.register_user("anna@test.de", "geheim", "Anna", "Müller", "2000-05-15", True)
        user = user_db.get_user("anna@test.de")
        assert user is not None
        assert user["vorname"] == "Anna"
        assert user["nachname"] == "Müller"
        assert user["geburtsdatum"] == "2000-05-15"
        assert user["newsletter"] is True

    def test_register_user_passwort_gespeichert(self):
        """Das Passwort wird korrekt gespeichert."""
        user_db.register_user("anna@test.de", "meinPasswort", "Anna", "Müller", "2000-01-01", False)
        user = user_db.get_user("anna@test.de")
        assert user["passwort"] == "meinPasswort"

    def test_register_mehrere_nutzer(self):
        """Mehrere Nutzer können unabhängig registriert werden."""
        user_db.register_user("anna@test.de", "pw1", "Anna", "Müller", "2000-01-01", False)
        user_db.register_user("ben@test.de", "pw2", "Ben", "Schmidt", "1995-03-20", True)
        assert user_db.account_exists("anna@test.de") is True
        assert user_db.account_exists("ben@test.de") is True

    # ── verify_login() ────────────────────────────────────────────────────────

    def test_verify_login_korrekte_daten(self):
        """Login mit korrekten Daten ist erfolgreich."""
        user_db.register_user("anna@test.de", "richtig", "Anna", "Müller", "2000-01-01", False)
        assert user_db.verify_login("anna@test.de", "richtig") is True

    def test_verify_login_falsches_passwort(self):
        """Login mit falschem Passwort schlägt fehl."""
        user_db.register_user("anna@test.de", "richtig", "Anna", "Müller", "2000-01-01", False)
        assert user_db.verify_login("anna@test.de", "falsch") is False

    def test_verify_login_nicht_registriert(self):
        """Login für unbekannten Account schlägt fehl."""
        assert user_db.verify_login("unbekannt@test.de", "passwort") is False

    def test_verify_login_email_case_insensitive(self):
        """Login-E-Mail ist case-insensitiv."""
        user_db.register_user("Anna@Test.de", "pw", "Anna", "Müller", "2000-01-01", False)
        assert user_db.verify_login("anna@test.de", "pw") is True

    # ── get_user() ────────────────────────────────────────────────────────────

    def test_get_user_vorhanden(self):
        """Registrierter Nutzer wird zurückgegeben."""
        user_db.register_user("anna@test.de", "pw", "Anna", "Müller", "2000-01-01", False)
        user = user_db.get_user("anna@test.de")
        assert user is not None

    def test_get_user_nicht_vorhanden(self):
        """Nicht registrierter Nutzer gibt None zurück."""
        assert user_db.get_user("niemand@test.de") is None
