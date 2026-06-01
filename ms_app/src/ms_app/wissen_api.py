import requests


def lade_pubmed_ids(suchbegriff):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": suchbegriff,
        "retmode": "json",
        "retmax": 5
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    return data["esearchresult"]["idlist"]


def erstelle_artikel_links(suchbegriff):
    ids = lade_pubmed_ids(suchbegriff)

    artikel = []

    for pubmed_id in ids:
        artikel.append(
            "https://pubmed.ncbi.nlm.nih.gov/" + pubmed_id + "/"
        )

    return artikel