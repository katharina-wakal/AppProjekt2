import requests

def suche_thema(thema):

    url = "https://wsearch.nlm.nih.gov/ws/query"

    params = {
        "db": "healthTopics",
        "term": thema
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    return response.text