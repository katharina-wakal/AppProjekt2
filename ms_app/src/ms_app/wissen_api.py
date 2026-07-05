import requests                  # für HTTP-Anfragen (API-Aufrufe)
from urllib.parse import quote   # Kodiert Sonderzeichen für URLs (z. B. Leerzeichen → %20)


# sucht Infos zu einem Thema über die Wikipedia-API
def suche_thema(thema):

    # Erstellt die API-URL & kodiert den Suchbegriff für eine gültige URL
    url = "https://de.wikipedia.org/api/rest_v1/page/summary/" + quote(thema)

    # HTTP-Header mit User-Agent hinzufügen
    headers = {"User-Agent": "MeinSchulprojekt/1.0 (meine.email@beispiel.de)"}

    print("URL:", url) # Gibt die erzeugte URL zu Testzwecken in der Konsole aus

    response = requests.get(url, headers=headers, timeout=10)
    # Sendet GET-Anfrage an Wikipedia-API
    # timeout=10 beendet Anfrage nach spätestens 10 Sek.

    print("Status:", response.status_code) # Gibt HTTP-Statuscode aus (z. B. 200 = erfolgreich)

    print("Antwort:", response.text[:300]) # Gibt die ersten 300 Zeichen der API-Antwort aus (zum Debuggen)

    # Prüft, ob Anfrage erfolgreich war
    if response.status_code == 200:
        daten = response.json() # Wandelt JSON-Antwort der API in Python-Dictionary um

        return {
            "titel": daten.get("title", ""), # Liest Titel des Wikipedia-Artikels aus
            "beschreibung": daten.get("extract", "Kein Text gefunden."), # Liest Kurzbeschreibung aus
            "url": daten.get("content_urls", {}).get("desktop", {}).get("page", "") # Liest Link zur Wikipedia-Seite aus
        }

    # wenn kein Artikel gefunden wurde oder ein Fehler auftritt
    else:

        return {
            "titel": thema, # Gibt Suchbegriff als Titel zurück
            "beschreibung": "Kein Artikel gefunden.", # Fehlermeldung für Benutzer
            "url": "" # Keine URL vorhanden
        }