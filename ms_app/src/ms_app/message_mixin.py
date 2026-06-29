# QMessageBox wird verwendet, um unterschiedliche
# Meldungs- und Bestätigungsfenster anzuzeigen.
from PyQt6.QtWidgets import QMessageBox


# Das MessageMixin ist eine wiederverwendbare Hilfsklasse.
#
# Es ist selbst kein sichtbares Fenster.
# Andere Fensterklassen können jedoch von diesem Mixin erben
# und dadurch dessen Methoden verwenden.
class MessageMixin:

    def _elternfenster_bestimmen(self, elternfenster):
        """
        Bestimmt, welches Fenster als Elternfenster
        für eine Meldung verwendet werden soll.

        Args:
            elternfenster:
                Optional übergebenes Elternfenster.

        Returns:
            Das übergebene Elternfenster oder das aktuelle Fensterobjekt.
        """

        # Wenn kein besonderes Elternfenster übergeben wurde,
        # wird das aktuelle Fenster verwendet.
        if elternfenster is None:
            return self

        # Andernfalls wird das ausdrücklich
        # übergebene Fenster verwendet.
        return elternfenster

    def zeige_fehler(
            self,
            nachricht,
            titel="Fehler",
            elternfenster=None
    ):
        """
        Zeigt eine einheitliche Fehlermeldung an.

        Args:
            nachricht:
                Text der Fehlermeldung.

            titel:
                Titel des Meldungsfensters.
                Standardmäßig wird „Fehler“ verwendet.

            elternfenster:
                Optionales Elternfenster der Meldung.
        """

        # Das passende Elternfenster bestimmen.
        parent = self._elternfenster_bestimmen(
            elternfenster
        )

        # Eine Warnmeldung mit dem angegebenen
        # Titel und Text anzeigen.
        QMessageBox.warning(
            parent,
            titel,
            nachricht
        )

    def zeige_information(
            self,
            titel,
            nachricht,
            elternfenster=None
    ):
        """
        Zeigt eine Informationsmeldung an.

        Args:
            titel:
                Titel des Meldungsfensters.

            nachricht:
                Text der Informationsmeldung.

            elternfenster:
                Optionales Elternfenster der Meldung.
        """

        # Das passende Elternfenster bestimmen.
        parent = self._elternfenster_bestimmen(
            elternfenster
        )

        # Die Informationsmeldung anzeigen.
        QMessageBox.information(
            parent,
            titel,
            nachricht
        )

    def zeige_warnung(
            self,
            titel,
            nachricht,
            elternfenster=None
    ):
        """
        Zeigt eine Warnmeldung ohne Auswahlmöglichkeit an.

        Args:
            titel:
                Titel der Warnmeldung.

            nachricht:
                Text der Warnmeldung.

            elternfenster:
                Optionales Elternfenster der Meldung.
        """

        # Das passende Elternfenster bestimmen.
        parent = self._elternfenster_bestimmen(
            elternfenster
        )

        # Die Warnmeldung anzeigen.
        QMessageBox.warning(
            parent,
            titel,
            nachricht
        )

    def frage_bestaetigung(
            self,
            titel,
            nachricht,
            elternfenster=None
    ):
        """
        Zeigt eine Bestätigungsfrage mit Ja und Nein an.

        Args:
            titel:
                Titel des Bestätigungsdialogs.

            nachricht:
                Frage, die angezeigt wird.

            elternfenster:
                Optionales Elternfenster des Dialogs.

        Returns:
            True, wenn Ja gewählt wurde.
            False, wenn Nein gewählt oder der Dialog geschlossen wurde.
        """

        # Das passende Elternfenster bestimmen.
        parent = self._elternfenster_bestimmen(
            elternfenster
        )

        # Einen Fragedialog mit Ja- und Nein-Schaltfläche öffnen.
        antwort = QMessageBox.question(
            parent,
            titel,
            nachricht,
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,

            # Nein wird als sichere Standardauswahl festgelegt.
            QMessageBox.StandardButton.No
        )

        # Das Ergebnis direkt als True oder False zurückgeben.
        return antwort == QMessageBox.StandardButton.Yes

    def frage_warnung(
            self,
            titel,
            nachricht,
            elternfenster=None
    ):
        """
        Zeigt eine besonders hervorgehobene Warnfrage an.

        Diese Methode eignet sich beispielsweise für das Löschen
        eines Accounts oder anderer unwiderruflicher Daten.

        Returns:
            True, wenn Ja gewählt wurde.
            False, wenn Nein gewählt oder der Dialog geschlossen wurde.
        """

        # Das passende Elternfenster bestimmen.
        parent = self._elternfenster_bestimmen(
            elternfenster
        )

        # Einen Warnungsdialog mit Ja und Nein öffnen.
        antwort = QMessageBox.warning(
            parent,
            titel,
            nachricht,
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,

            # Nein wird als sichere Standardauswahl festgelegt.
            QMessageBox.StandardButton.No
        )

        # Das Ergebnis als booleschen Wert zurückgeben.
        return antwort == QMessageBox.StandardButton.Yes