from datetime import datetime, timedelta  # Importiert Funktionen für Datumsberechnung


STANDARD_CYCLE_LENGTH = 28  # Standardwert für Zykluslänge bei nur einem Eintrag
MAX_CYCLES_USED = 6  # Maximale Anzahl vergangener Zyklen für die Berechnung


def calculate_cycle_prediction(period_start_dates):  # Hauptfunktion zur Berechnung
    dates = []  # Leere Liste für umgewandelte Datumsobjekte

    for date_text in period_start_dates:  # Geht jedes Datum in der Liste durch
        date = datetime.strptime(date_text, "%Y-%m-%d").date()  # Wandelt Text in echtes Datum um
        dates.append(date)  # Fügt Datum zur Liste hinzu

    dates.sort()  # Sortiert alle Daten chronologisch

    last_period_start = dates[-1]  # Nimmt den letzten Periodenstart

    if len(dates) == 1:  # Prüft ob nur ein Eintrag vorhanden ist
        cycle_lengths = []  # Noch keine echten Zykluslängen vorhanden
        average_cycle = STANDARD_CYCLE_LENGTH  # Verwendet Standardwert 28
        shortest_cycle = STANDARD_CYCLE_LENGTH  # Frühester möglicher Zyklus = 28
        longest_cycle = STANDARD_CYCLE_LENGTH  # Spätester möglicher Zyklus = 28

    else:  # Falls mehr als ein Eintrag vorhanden ist
        cycle_lengths = []  # Leere Liste für berechnete Zykluslängen

        for i in range(1, len(dates)):  # Geht alle Periodenstarts durch
            difference = (dates[i] - dates[i - 1]).days  # Berechnet Abstand zwischen zwei Perioden
            cycle_lengths.append(difference)  # Speichert Zykluslänge

        last_cycles = cycle_lengths[-MAX_CYCLES_USED:]  # Nutzt nur die letzten 6 Zyklen

        average_cycle = round(sum(last_cycles) / len(last_cycles))  # Berechnet Durchschnitt
        shortest_cycle = min(last_cycles)  # Kürzester Zyklus
        longest_cycle = max(last_cycles)  # Längster Zyklus

    predicted_period_start = last_period_start + timedelta(days=average_cycle)  # Berechnet wahrscheinlichsten Start
    earliest_period_start = last_period_start + timedelta(days=shortest_cycle)  # Berechnet frühesten Start
    latest_period_start = last_period_start + timedelta(days=longest_cycle)  # Berechnet spätesten Start

    predicted_ovulation = predicted_period_start - timedelta(days=14)  # Ovulation = 14 Tage vor Periode

    warning = None  # Standardmäßig keine Warnung

    if shortest_cycle < 21 or longest_cycle > 35:  # Prüft auf ungewöhnliche Zyklen
        warning = (  # Erstellt Warnhinweis
            "Dein Zyklus liegt außerhalb des üblichen Bereichs. "
            "Falls das häufiger vorkommt oder du Beschwerden hast, "
            "solltest du ärztlichen Rat einholen."
        )

    return {  # Gibt alle berechneten Werte zurück
        "cycle_lengths": cycle_lengths,  # Liste aller berechneten Zykluslängen
        "average_cycle": average_cycle,  # Durchschnittliche Zykluslänge
        "earliest_period_start": earliest_period_start,  # Frühester möglicher Start
        "predicted_period_start": predicted_period_start,  # Wahrscheinlichster Start
        "latest_period_start": latest_period_start,  # Spätester möglicher Start
        "predicted_ovulation": predicted_ovulation,  # Wahrscheinliche Ovulation
        "warning": warning  # Warnung falls vorhanden
    }


