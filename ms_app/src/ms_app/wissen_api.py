import requests
from urllib.parse import quote


def suche_thema(thema):
    url = "https://de.wikipedia.org/api/rest_v1/page/summary/" + quote(thema)

    # User-Agent Header hinzufügen
    headers = {
        "User-Agent": "MeinSchulprojekt/1.0 (meine.email@beispiel.de)"
    }

    print("URL:", url)

    response = requests.get(url, headers=headers, timeout=10)

    print("Status:", response.status_code)
    print("Antwort:", response.text[:300])

    if response.status_code == 200:
        daten = response.json()
        return {
            "titel": daten.get("title", ""),
            "beschreibung": daten.get("extract", "Kein Text gefunden."),
            "url": daten.get("content_urls", {}).get("desktop", {}).get("page", "")
        }
    else:
        return {
            "titel": thema,
            "beschreibung": "Kein Artikel gefunden.",
            "url": ""
        }