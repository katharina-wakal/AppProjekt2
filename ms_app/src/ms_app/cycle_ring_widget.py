# cycle_ring_widget.py
# Dieses Modul enthält ein eigenes Widget, das den Zyklus
# als kreisförmigen Ring im FemHealth-Dashboard darstellt.

import math #für mathematische Berechnungen
from PyQt6.QtWidgets import QWidget# QWidget ist die Basisklasse für unser eigenes Widget.
# Qt enthält verschiedene Einstellungen und Aufzählungen von PyQt.
# QRectF beschreibt ein Rechteck mit Fließkommazahlen.
# QPointF beschreibt einen Punkt mit x- und y-Koordinate.
from PyQt6.QtCore import Qt, QRectF, QPointF
# QPainter wird zum Zeichnen des Rings verwendet.
# QColor legt Farben fest.
# QPen beschreibt Linien und deren Eigenschaften.
# QBrush beschreibt die Füllung einer Form.
# QFont legt die Schriftart und Schriftgröße fest.v
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

# Eigene Klasse für den Zyklus-Ring.
# Sie erbt von QWidget und kann dadurch wie ein normales
# PyQt-Widget in einem Fenster verwendet werden.
class CycleRingWidget(QWidget):

    # Konstruktor der Klasse.
    # parent ist optional das übergeordnete PyQt-Widget.
    def __init__(self, parent=None):
        # Konstruktor der Elternklasse QWidget aufrufen.
        super().__init__(parent)

        # ── Zyklus-Daten ──────────────────────────────────────────────────
        self.zyklus_laenge  = 28 # Standardmäßige Länge eines Zyklus in Tagen.
        self.heute_tag      = 14 # Der aktuelle Tag innerhalb des Zyklus.
        self.periode_start  = 1 # Erster Tag der Periodenphase.
        self.periode_ende   = 5 # Letzter Tag der Periodenphase.
        self.eisprung_start = 12 # Erster Tag der angenommenen fruchtbaren Phase.
        self.eisprung_ende  = 16 # Letzter Tag der angenommenen fruchtbaren Phase.

        # Text in der Mitte (wird beim Klick geändert)
        self.mitte_zeile1 = "Tag 14" # Erste Textzeile, die in der Mitte des Rings angezeigt wird.
        self.mitte_zeile2 = "von 28" # Zweite Textzeile, die in der Mitte des Rings angezeigt wird.

        # Standardtext speichern, damit er nach einem Klick
        # wiederhergestellt werden kann.
        self.standard_zeile1 = self.mitte_zeile1
        self.standard_zeile2 = self.mitte_zeile2

        # Voraussichtlicher Eisprungtag innerhalb des Zyklus.
        self.eisprung_tag = 14

        #Det Hintergrund des Widgets wirdtransparentdargestellt.
        # Dadurch ist beispielsweise die Hintergrundfarbe des Dashboards sichtbar.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Aktiviert die Erfassung von Mausbewegungen,
        # auch wenn keine Maustaste gedrückt wird.
        self.setMouseTracking(True)

    # ── Daten von außen setzen ────────────────────────────────────────────

    # Mit dieser Methode können die angezeigten Zyklusdaten
    # von einem anderen Modul aus aktualisiert werden.
    def zyklus_setzen(
            self,
            heute,
            laenge,
            periode_start,
            periode_ende,
            eisprung_start,
            eisprung_ende,
            tage_bis_periode
    ):
        """
        Übernimmt die bereits berechneten Zyklusdaten
        aus dem Dashboard und aktualisiert den Ring.
        """

        # Den tatsächlichen aktuellen Zyklustag speichern.
        # Dieser kann bei einer überfälligen Periode
        # größer als die durchschnittliche Zykluslänge sein.
        self.aktueller_zyklustag = heute

        # Die durchschnittliche Zykluslänge speichern.
        self.zyklus_laenge = laenge

        # Der Marker muss sich innerhalb des gezeichneten Rings befinden.
        # Deshalb wird er auf den letzten dargestellten Tag begrenzt,
        # falls die Periode bereits überfällig ist.
        self.heute_tag = min(
            max(heute, 1),
            laenge
        )

        # Beginn und Ende der Periodenphase speichern.
        self.periode_start = periode_start
        self.periode_ende = periode_ende

        # Beginn und Ende der fruchtbaren Phase speichern.
        self.eisprung_start = eisprung_start
        self.eisprung_ende = eisprung_ende

        # Der genaue Eisprungtag liegt in der Mitte
        # der berechneten fruchtbaren Phase.
        self.eisprung_tag = (
                                    eisprung_start + eisprung_ende
                            ) // 2

        # Bereits berechnete Anzahl der Tage
        # bis zur nächsten Periode speichern.
        self.tage_bis_periode = tage_bis_periode

        # Prüfen, ob aktuell eine eingetragene
        # beziehungsweise erwartete Periodenphase vorliegt.
        if periode_start <= heute <= periode_ende:
            tag_in_periode = (
                    heute - periode_start + 1
            )

            self.mitte_zeile1 = (
                    "Tag " + str(tag_in_periode)
            )

            self.mitte_zeile2 = "der Periode"

        # Ein negativer Wert bedeutet,
        # dass die vorhergesagte Periode bereits überfällig ist.
        elif tage_bis_periode < 0:
            self.mitte_zeile1 = (
                    str(abs(tage_bis_periode))
                    + " Tage"
            )

            self.mitte_zeile2 = "überfällig"

        # Der vorhergesagte Periodenbeginn ist heute.
        elif tage_bis_periode == 0:
            self.mitte_zeile1 = "Heute"

            self.mitte_zeile2 = "voraussichtliche Periode"

        # Genau ein Tag verbleibt bis zur nächsten Periode.
        elif tage_bis_periode == 1:
            self.mitte_zeile1 = "1 Tag"

            self.mitte_zeile2 = "bis zur Periode"

        # Mehrere Tage verbleiben bis zur nächsten Periode.
        else:
            self.mitte_zeile1 = (
                    str(tage_bis_periode)
                    + " Tage"
            )

            self.mitte_zeile2 = "bis zur Periode"

        # Den normalen Text speichern.
        # Dieser wird wieder angezeigt, wenn der Nutzer
        # neben den Ring oder in die Ringmitte klickt.
        self.standard_zeile1 = self.mitte_zeile1
        self.standard_zeile2 = self.mitte_zeile2

        # Das Widget neu zeichnen.
        self.update()
    # ── Klick-Erkennung ───────────────────────────────────────────────────

    def mousePressEvent(self, event):
        """
        Zeigt Informationen über den angeklickten Bereich des Rings.

        Es werden hier keine neuen Zyklusprognosen berechnet.
        Die Methode verwendet nur die bereits vom Dashboard
        übergebenen Werte.
        """

        # Nur Klicks mit der linken Maustaste auswerten.
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # Die Position des Mausklicks in einen Zyklustag umwandeln.
        geklickter_tag = self.punkt_zu_tag(
            event.position().x(),
            event.position().y()
        )

        # Wurde nicht auf den Ring geklickt, wird wieder
        # die normale Prognoseanzeige dargestellt.
        if geklickter_tag is None:
            self.mitte_zeile1 = self.standard_zeile1
            self.mitte_zeile2 = self.standard_zeile2

            self.update()
            return

        # Prüfen, ob der ausgewählte Tag in der Periodenphase liegt.
        if (
                self.periode_start
                <= geklickter_tag
                <= self.periode_ende
        ):
            # Berechnen, der wievielte Tag der Periode
            # innerhalb des roten Bereichs ausgewählt wurde.
            tag_in_periode = (
                    geklickter_tag
                    - self.periode_start
                    + 1
            )

            self.mitte_zeile1 = (
                    "Tag " + str(tag_in_periode)
            )

            self.mitte_zeile2 = "der Periode"

        # Prüfen, ob genau der prognostizierte
        # Eisprungtag angeklickt wurde.
        elif geklickter_tag == self.eisprung_tag:
            self.mitte_zeile1 = "Eisprung"

            self.mitte_zeile2 = "voraussichtlich"

        # Prüfen, ob der Tag innerhalb
        # der fruchtbaren Phase liegt.
        elif (
                self.eisprung_start
                <= geklickter_tag
                <= self.eisprung_ende
        ):
            self.mitte_zeile1 = (
                    "Zyklustag "
                    + str(geklickter_tag)
            )

            self.mitte_zeile2 = "fruchtbare Phase"

        else:
            # Bei allen übrigen Tagen wird lediglich
            # der ausgewählte Zyklustag angezeigt.
            self.mitte_zeile1 = (
                    "Zyklustag "
                    + str(geklickter_tag)
            )

            self.mitte_zeile2 = "ausgewählter Tag"

        # Das Widget mit dem neuen Text neu zeichnen.
        self.update()

    # ── Hilfsmethode: Klickpunkt → Zyklustag ─────────────────────────────

    def punkt_zu_tag(self, klick_x, klick_y):
        breite  = self.width()
        hoehe   = self.height()
        mitte_x = breite / 2
        mitte_y = hoehe / 2
        radius  = min(breite, hoehe) / 2 - 18

        # Abstand vom Mittelpunkt
        dx = klick_x - mitte_x
        dy = klick_y - mitte_y
        abstand = math.sqrt(dx * dx + dy * dy)

        # Nur Klicks auf dem Ring auswerten (±20px Toleranz)
        ring_breite = 16
        toleranz    = 20
        if abstand < radius - ring_breite - toleranz:
            return None
        if abstand > radius + ring_breite + toleranz:
            return None

        # Winkel berechnen (atan2 gibt Winkel von der x-Achse)
        winkel_rad = math.atan2(dy, dx)
        winkel_grad = math.degrees(winkel_rad)

        # Umrechnen: 0° = oben, im Uhrzeigersinn
        # atan2: 0°=rechts → wir verschieben um +90°
        winkel_oben = (winkel_grad + 90) % 360

        # Winkel → Zyklustag
        tag = int(winkel_oben / 360 * self.zyklus_laenge) + 1
        if tag < 1:
            tag = 1
        if tag > self.zyklus_laenge:
            tag = self.zyklus_laenge

        return tag

    # ── paintEvent ────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        breite  = self.width()
        hoehe   = self.height()
        mitte_x = breite / 2
        mitte_y = hoehe / 2
        radius  = min(breite, hoehe) / 2 - 18
        ring_breite = 16

        ring_rect = QRectF(
            mitte_x - radius,
            mitte_y - radius,
            radius * 2,
            radius * 2
        )

        # 1. Hintergrundring
        pen = QPen(QColor(255, 255, 255, 90))
        pen.setWidth(ring_breite)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(ring_rect)

        # 2. Roter Bogen: Periode – kräftiges Rot
        self.bogen_zeichnen(
            painter, ring_rect, ring_breite,
            self.periode_start, self.periode_ende,
            self.zyklus_laenge,
            QColor(210, 30, 30)     # kräftiges Rot #D21E1E
        )

        # 3. Blauer Bogen: Eisprung/fruchtbare Phase
        self.bogen_zeichnen(
            painter, ring_rect, ring_breite,
            self.eisprung_start, self.eisprung_ende,
            self.zyklus_laenge,
            QColor(25, 118, 210)    # #1976D2 Blau
        )

        # 4. Heutiger-Tag-Marker: weißlicher transparenter Kreis
        winkel_heute = self.tag_zu_winkel(self.heute_tag, self.zyklus_laenge)
        punkt_heute  = self.punkt_auf_ring(mitte_x, mitte_y, radius, winkel_heute)
        marker_r     = ring_breite / 2 + 5

        painter.setPen(QPen(QColor(255, 255, 255, 230), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.drawEllipse(
            QRectF(
                punkt_heute.x() - marker_r,
                punkt_heute.y() - marker_r,
                marker_r * 2,
                marker_r * 2
            )
        )
        # Tag-Nummer im Marker
        painter.setPen(QPen(QColor(173, 20, 87)))
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            QRectF(
                punkt_heute.x() - marker_r,
                punkt_heute.y() - marker_r,
                marker_r * 2,
                marker_r * 2
            ),
            Qt.AlignmentFlag.AlignCenter,
            str(self.heute_tag)
        )

        # 5. Text in der Mitte (2 Zeilen)
        mitte_rect = QRectF(mitte_x - 70, mitte_y - 28, 140, 30)
        font1 = QFont("Segoe UI", 15, QFont.Weight.Bold)
        painter.setFont(font1)
        painter.setPen(QPen(QColor(173, 20, 87)))
        painter.drawText(mitte_rect, Qt.AlignmentFlag.AlignCenter, self.mitte_zeile1)

        mitte_rect2 = QRectF(mitte_x - 70, mitte_y + 4, 140, 24)
        font2 = QFont("Segoe UI", 10)
        painter.setFont(font2)
        painter.setPen(QPen(QColor(136, 14, 79)))
        painter.drawText(mitte_rect2, Qt.AlignmentFlag.AlignCenter, self.mitte_zeile2)

        painter.end()

    # ── Hilfsmethoden ────────────────────────────────────────────────────

    def tag_zu_winkel(self, tag, zyklus_laenge):
        anteil = (tag - 1) / zyklus_laenge
        return -90 + anteil * 360

    def punkt_auf_ring(self, mitte_x, mitte_y, radius, winkel_grad):
        winkel_rad = math.radians(winkel_grad)
        x = mitte_x + radius * math.cos(winkel_rad)
        y = mitte_y + radius * math.sin(winkel_rad)
        return QPointF(x, y)

    def bogen_zeichnen(self, painter, ring_rect, ring_breite,
                       tag_start, tag_ende, zyklus_laenge, farbe):
        anteil_start = (tag_start - 1) / zyklus_laenge
        anteil_ende  = tag_ende / zyklus_laenge

        start_grad = 90 - anteil_start * 360
        spann_grad = -(anteil_ende - anteil_start) * 360

        pen = QPen(farbe)
        pen.setWidth(ring_breite)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawArc(
            ring_rect,
            int(start_grad * 16),
            int(spann_grad * 16)
        )
