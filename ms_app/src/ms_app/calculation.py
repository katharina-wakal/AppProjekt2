from datetime import date, datetime, timedelta


# Standard-Zykluslänge, solange erst ein Periodenstart vorhanden ist.
STANDARD_CYCLE_LENGTH = 28

# Für die Prognose werden höchstens die letzten sechs Zyklen verwendet.
MAX_CYCLES_USED = 6

# Der Eisprung wird ungefähr 14 Tage vor der nächsten Periode angenommen.
DAYS_BEFORE_NEXT_PERIOD_FOR_OVULATION = 14


def calculate_cycle_prediction(period_start_dates, today=None):
    """
    Berechnet Zykluswerte aus den gespeicherten Periodenstarts.

    Args:
        period_start_dates:
            Liste der Periodenstarts im Format YYYY-MM-DD.

        today:
            Optionales Vergleichsdatum für Tests.
            Wird kein Datum angegeben, wird das heutige Datum verwendet.

    Returns:
        dict:
            Enthält alle berechneten Zyklus- und Prognosewerte.
    """

    # Ohne einen gespeicherten Periodenstart ist keine Prognose möglich.
    if len(period_start_dates) == 0:
        raise ValueError(
            "Für die Prognose wird mindestens "
            "ein Periodenstart benötigt."
        )

    # In dieser Liste werden alle Periodenstarts
    # als echte Datumsobjekte gespeichert.
    dates = []

    # Alle übergebenen Periodenstarts durchlaufen.
    for date_value in period_start_dates:

        # Falls ein datetime-Objekt übergeben wurde,
        # wird nur das Datum verwendet.
        if isinstance(date_value, datetime):
            period_date = date_value.date()

        # Falls bereits ein date-Objekt übergeben wurde,
        # kann es direkt verwendet werden.
        elif isinstance(date_value, date):
            period_date = date_value

        else:
            # Den Datumstext aus der Datenbank
            # in ein date-Objekt umwandeln.
            period_date = datetime.strptime(
                date_value,
                "%Y-%m-%d"
            ).date()

        # Doppelte Periodenstarts nicht mehrfach speichern.
        if period_date not in dates:
            dates.append(period_date)

    # Die Periodenstarts chronologisch sortieren.
    dates.sort()

    # Der letzte Wert ist der letzte tatsächlich
    # eingetragene Periodenbeginn.
    last_period_start = dates[-1]

    # Falls kein eigenes Vergleichsdatum übergeben wurde,
    # wird das heutige Datum verwendet.
    if today is None:
        today = date.today()

    # Bei nur einem Periodenstart gibt es noch
    # keine gemessene Zykluslänge.
    if len(dates) == 1:

        # Es konnten noch keine Abstände berechnet werden.
        cycle_lengths = []

        # Deshalb wird zunächst der Standardwert verwendet.
        average_cycle = STANDARD_CYCLE_LENGTH
        shortest_cycle = STANDARD_CYCLE_LENGTH
        longest_cycle = STANDARD_CYCLE_LENGTH

    else:
        # Hier werden die Abstände zwischen
        # zwei Periodenstarts gespeichert.
        cycle_lengths = []

        # Ab dem zweiten Periodenstart wird jeweils
        # die Differenz zum vorherigen Start berechnet.
        for index in range(1, len(dates)):

            difference = (
                dates[index] - dates[index - 1]
            ).days

            cycle_lengths.append(difference)

        # Nur die letzten sechs gemessenen Zyklen
        # für die Prognose verwenden.
        last_cycles = cycle_lengths[-MAX_CYCLES_USED:]

        # Durchschnittliche Zykluslänge berechnen.
        average_cycle = round(
            sum(last_cycles) / len(last_cycles)
        )

        # Kürzeste Zykluslänge bestimmen.
        shortest_cycle = min(last_cycles)

        # Längste Zykluslänge bestimmen.
        longest_cycle = max(last_cycles)

    # Den wahrscheinlichsten nächsten Periodenstart berechnen.
    predicted_period_start = (
        last_period_start
        + timedelta(days=average_cycle)
    )

    # Den frühestmöglichen Periodenstart berechnen.
    earliest_period_start = (
        last_period_start
        + timedelta(days=shortest_cycle)
    )

    # Den spätestmöglichen Periodenstart berechnen.
    latest_period_start = (
        last_period_start
        + timedelta(days=longest_cycle)
    )

    # Den wahrscheinlichen Eisprung berechnen.
    # Dieser wird ungefähr 14 Tage vor der
    # nächsten Periode angenommen.
    predicted_ovulation = (
        predicted_period_start
        - timedelta(
            days=DAYS_BEFORE_NEXT_PERIOD_FOR_OVULATION
        )
    )

    # Der letzte tatsächliche Periodenstart ist Zyklustag 1.
    # Deshalb wird zur Datumsdifferenz 1 addiert.
    current_cycle_day = (
        today - last_period_start
    ).days + 1

    # Berechnen, wie viele Tage bis zur
    # prognostizierten Periode verbleiben.
    days_until_period = (
        predicted_period_start - today
    ).days

    # Ein negativer Wert bedeutet,
    # dass der prognostizierte Termin überschritten wurde.
    is_overdue = days_until_period < 0

    # Den Zyklustag des prognostizierten Eisprungs berechnen.
    ovulation_cycle_day = (
        predicted_ovulation - last_period_start
    ).days + 1

    # Standardmäßig gibt es keinen Warnhinweis.
    warning = None

    # Prüfen, ob mindestens eine gemessene Zykluslänge
    # außerhalb des Bereichs von 21 bis 35 Tagen liegt.
    if shortest_cycle < 21 or longest_cycle > 35:

        warning = (
            "Dein Zyklus liegt außerhalb des üblichen Bereichs. "
            "Falls das häufiger vorkommt oder du Beschwerden hast, "
            "solltest du ärztlichen Rat einholen."
        )

    # Alle berechneten Werte als Dictionary zurückgeben.
    #
    # Die bisherigen Schlüssel bleiben erhalten,
    # damit beispielsweise analyse.py weiterhin funktioniert.
    return {
        "cycle_lengths": cycle_lengths,
        "average_cycle": average_cycle,
        "shortest_cycle": shortest_cycle,
        "longest_cycle": longest_cycle,
        "last_period_start": last_period_start,
        "earliest_period_start": earliest_period_start,
        "predicted_period_start": predicted_period_start,
        "latest_period_start": latest_period_start,
        "predicted_ovulation": predicted_ovulation,
        "current_cycle_day": current_cycle_day,
        "days_until_period": days_until_period,
        "is_overdue": is_overdue,
        "ovulation_cycle_day": ovulation_cycle_day,
        "warning": warning
    }