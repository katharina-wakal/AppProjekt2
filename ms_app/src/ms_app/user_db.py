# user_db.py – Gemeinsame In-Memory-Nutzerdatenbank für FemHealth
# In einem echten Projekt würde hier eine Datenbankanbindung stehen.

_users: dict[str, dict] = {}  # { "email": { "passwort": "...", "vorname": "...", ... } }


def account_exists(email: str) -> bool:
    return email.lower() in _users


def register_user(email: str, passwort: str, vorname: str, nachname: str,
                  geburtsdatum: str, newsletter: bool) -> None:
    _users[email.lower()] = {
        "passwort": passwort,
        "vorname": vorname,
        "nachname": nachname,
        "geburtsdatum": geburtsdatum,
        "newsletter": newsletter,
    }


def verify_login(email: str, passwort: str) -> bool:
    user = _users.get(email.lower())
    return user is not None and user["passwort"] == passwort


def get_user(email: str) -> dict | None:
    return _users.get(email.lower())
