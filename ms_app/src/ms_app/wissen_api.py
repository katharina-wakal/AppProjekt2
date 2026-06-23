import requests
from urllib.parse import quote

def suche_thema(thema):
    url = "https://de.wikipedia.org/api/rest_v1/page/summary/" + quote(thema)

    response = requests.get(
        url,
        timeout=10
    )

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