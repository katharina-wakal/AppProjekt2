# cycle_ring_widget.py
# Zyklus-Ring Widget für FemHealth Dashboard

import math
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class CycleRingWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Zyklus-Daten ──────────────────────────────────────────────────
        self.zyklus_laenge  = 28
        self.heute_tag      = 14
        self.periode_start  = 1
        self.periode_ende   = 5
        self.eisprung_start = 12
        self.eisprung_ende  = 16

        # Text in der Mitte (wird beim Klick geändert)
        self.mitte_zeile1 = "Tag 14"
        self.mitte_zeile2 = "von 28"

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

    # ── Daten von außen setzen ────────────────────────────────────────────

    def zyklus_setzen(self, heute, laenge, periode_start, periode_ende,
                      eisprung_start, eisprung_ende):
        self.heute_tag      = heute
        self.zyklus_laenge  = laenge
        self.periode_start  = periode_start
        self.periode_ende   = periode_ende
        self.eisprung_start = eisprung_start
        self.eisprung_ende  = eisprung_ende

        # Standardanzeige: wie viele Tage bis zur nächsten Periode
        tage_bis_periode = laenge - heute + periode_start
        if heute >= periode_start and heute <= periode_ende:
            self.mitte_zeile1 = "Tag " + str(heute - periode_start + 1)
            self.mitte_zeile2 = "der Periode"
        else:
            self.mitte_zeile1 = str(tage_bis_periode) + " Tage"
            self.mitte_zeile2 = "bis zur Periode"

        self.update()

    # ── Klick-Erkennung ───────────────────────────────────────────────────

    def mousePressEvent(self, event):
        # Welchen Tag hat der Nutzer angeklickt?
        geklickter_tag = self.punkt_zu_tag(event.position().x(), event.position().y())

        if geklickter_tag is None:
            return

        # Prüfen welcher Bereich geklickt wurde
        if self.periode_start <= geklickter_tag <= self.periode_ende:
            # Roter Bereich: Periodenphase
            tag_in_periode = geklickter_tag - self.periode_start + 1
            self.mitte_zeile1 = "Tag " + str(tag_in_periode)
            self.mitte_zeile2 = "der Periode"

        elif self.eisprung_start <= geklickter_tag <= self.eisprung_ende:
            # Blauer Bereich: Eisprung-/fruchtbare Phase
            tage_bis = self.eisprung_start - geklickter_tag
            if tage_bis <= 0:
                self.mitte_zeile1 = "Eisprung"
                self.mitte_zeile2 = "Tag " + str(geklickter_tag - self.eisprung_start + 1)
            else:
                self.mitte_zeile1 = str(tage_bis) + " Tage bis"
                self.mitte_zeile2 = "zum Eisprung"

        else:
            # Grauer Bereich: normaler Zyklustag → Tage bis zur Periode
            if geklickter_tag <= self.heute_tag:
                tage_bis = self.zyklus_laenge - self.heute_tag + geklickter_tag
            else:
                tage_bis = geklickter_tag - self.heute_tag

            # Tage bis nächste Periode vom geklickten Tag aus
            tage_bis_periode = self.zyklus_laenge - geklickter_tag + self.periode_start
            if tage_bis_periode > self.zyklus_laenge:
                tage_bis_periode = tage_bis_periode - self.zyklus_laenge

            self.mitte_zeile1 = str(tage_bis_periode) + " Tage"
            self.mitte_zeile2 = "bis zur Periode"

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
