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

    # Diese Methode wandelt die Koordinaten eines Mausklicks
    # in einen Zyklustag um.
    def punkt_zu_tag(self, klick_x, klick_y):
        breite  = self.width() # Aktuelle Breite des Widgets abfragen.
        hoehe   = self.height() # Aktuelle Höhe des Widgets abfragen.
        mitte_x = breite / 2 # Horizontale Position des Mittelpunkts berechnen.
        mitte_y = hoehe / 2 # Vertikale Position des Mittelpunkts berechnen.
        # Radius des Rings berechnen.
        # Es werden 18 Pixel Abstand zum Rand des Widgets gelassen.
        radius  = min(breite, hoehe) / 2 - 18

        # Abstand vom Mittelpunkt
        dx = klick_x - mitte_x # Horizontalen Abstand des Klicks vom Mittelpunkt berechnen.
        dy = klick_y - mitte_y # Vertikalen Abstand des Klicks vom Mittelpunkt berechnen.
        # Direkten Abstand des Klickpunkts vom Mittelpunkt berechnen.
        # Grundlage ist der Satz des Pythagoras.
        abstand = math.sqrt(dx * dx + dy * dy)

        # Nur Klicks auf dem Ring auswerten (±20px Toleranz)
        ring_breite = 16 # Breite der gezeichneten Ringlinie in Pixeln.
        # Zusätzliche Toleranz, damit der Ring leichter
        # mit der Maus angeklickt werden kann.
        toleranz    = 20

        # Prüfen, ob der Klick zu weit innerhalb des Rings liegt.
        if abstand < radius - ring_breite - toleranz:
            # Der Klick wird nicht als Klick auf den Ring gewertet.
            return None

        # Prüfen, ob der Klick zu weit außerhalb des Rings liegt.
        if abstand > radius + ring_breite + toleranz:
            # Der Klick wird nicht als Klick auf den Ring gewertet.
            return None

        # Den Winkel des Klickpunkts zum Mittelpunkt berechnen.
        # atan2 berücksichtigt sowohl die x- als auch die y-Koordinate.
        # Das Ergebnis wird zunächst im Bogenmaß zurückgegeben.
        winkel_rad = math.atan2(dy, dx)
        # Den Winkel vom Bogenmaß in Grad umwandeln.
        winkel_grad = math.degrees(winkel_rad)

        # atan2 verwendet die rechte Seite des Kreises als 0°.
        # Für unseren Zyklus soll jedoch die obere Seite 0° sein.
        # Deshalb wird der Winkel um 90° verschoben.
        #
        # Durch % 360 bleibt das Ergebnis immer zwischen
        # 0 und 359 Grad.
        winkel_oben = (winkel_grad + 90) % 360

        # Den berechneten Winkel in einen Zyklustag umwandeln.
        #
        # Beispiel bei 28 Tagen:
        # 0° entspricht Tag 1.
        # 180° entspricht ungefähr Tag 15.
        tag = int(winkel_oben / 360 * self.zyklus_laenge) + 1

        # Sicherheitsprüfung:
        # Der Zyklustag darf nicht kleiner als 1 sein.
        if tag < 1:
            tag = 1

        # Sicherheitsprüfung:
        # Der Zyklustag darf nicht größer als
        # die gesamte Zykluslänge sein.
        if tag > self.zyklus_laenge:
            tag = self.zyklus_laenge

        # Den berechneten Zyklustag zurückgeben.
        return tag

    # ── paintEvent ────────────────────────────────────────────────────────

    # Diese Methode wird von PyQt automatisch aufgerufen,
    # wenn das Widget gezeichnet oder aktualisiert werden muss.
    def paintEvent(self, event):

        # Ein QPainter-Objekt für dieses Widget erstellen.
        painter = QPainter(self)

        # Kantenglättung aktivieren.
        # Dadurch werden Kreise und Bögen glatter dargestellt.
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        breite  = self.width() # Aktuelle Breite des Widgets abfragen.
        hoehe   = self.height() # Aktuelle Höhe des Widgets abfragen.
        mitte_x = breite / 2 # Horizontale Mitte des Widgets berechnen.
        mitte_y = hoehe / 2  # Vertikale Mitte des Widgets berechnen.
        radius  = min(breite, hoehe) / 2 - 18 # Radius des Zyklusrings berechnen.
        ring_breite = 16 # Breite der Ringlinie festlegen.

        # Ein Rechteck erzeugen, in das der Kreis gezeichnet wird.
        # Da Breite und Höhe gleich groß sind, entsteht ein Kreis.
        ring_rect = QRectF(
            mitte_x - radius,
            mitte_y - radius,
            radius * 2,
            radius * 2
        )

        # 1. Hintergrundring

        # Einen halbtransparenten weißen Stift für den Hintergrundring
        # erstellen.
        pen = QPen(QColor(255, 255, 255, 90))
        pen.setWidth(ring_breite) # Breite der Linie festlegen.
        pen.setCapStyle(Qt.PenCapStyle.FlatCap) # Die Enden der Linie werden gerade dargestellt.
        painter.setPen(pen)# Den erstellten Stift für den Painter festlegen.
        painter.setBrush(Qt.BrushStyle.NoBrush) # Keine Füllung verwenden, da nur der Rand gezeichnet wird.
        painter.drawEllipse(ring_rect) # Den vollständigen Hintergrundkreis zeichnen.

        # 2. Roter Bogen: Periode – kräftiges Rot

        # Die Hilfsmethode bogen_zeichnen aufrufen.
        self.bogen_zeichnen(
            painter,  # Painter zum Zeichnen
            ring_rect,  # Bereich, in dem gezeichnet wird
            ring_breite,  # Breite der Linie
            self.periode_start,  # Erster Periodentag
            self.periode_ende,  # Letzter Periodentag
            self.zyklus_laenge,  # Gesamte Zykluslänge
            QColor(210, 30, 30)  # Kräftiges Rot: #D21E1E
        )

        # 3. Blauer Bogen: Eisprung/fruchtbare Phase

        # Einen blauen Bogen für die Eisprung- beziehungsweise
        # fruchtbare Phase zeichnen.
        self.bogen_zeichnen(
            painter,  # Painter zum Zeichnen
            ring_rect,  # Bereich des Rings
            ring_breite,  # Breite der Linie
            self.eisprung_start,  # Erster Tag der Phase
            self.eisprung_ende,  # Letzter Tag der Phase
            self.zyklus_laenge,  # Gesamte Zykluslänge
            QColor(25, 118, 210)  # Blau: #1976D2
        )

        # 4. Heutiger-Tag-Marker: weißlicher transparenter Kreis
        # Den heutigen Zyklustag in einen Winkel umwandeln.
        winkel_heute = self.tag_zu_winkel(self.heute_tag, self.zyklus_laenge)
        # Den Punkt auf dem Ring berechnen, der dem heutigen Tag entspricht.
        punkt_heute  = self.punkt_auf_ring(mitte_x, mitte_y, radius, winkel_heute)
        # Radius des kreisförmigen Markers berechnen.
        marker_r     = ring_breite / 2 + 5

        # Rand des Markers festlegen.
        # Der Rand ist fast vollständig weiß und 2 Pixel breit.
        painter.setPen(QPen(QColor(255, 255, 255, 230), 2))
        # Füllfarbe des Markers festlegen.
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        # Den kreisförmigen Marker zeichnen.
        painter.drawEllipse(
            QRectF(
                punkt_heute.x() - marker_r,
                punkt_heute.y() - marker_r,
                marker_r * 2,
                marker_r * 2
            )
        )
        # Farbe für die Zahl innerhalb des Markers festlegen.
        painter.setPen(QPen(QColor(173, 20, 87)))
        # Schriftart, Schriftgröße und Fettdruck festlegen.
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        # Die Schrift für den Painter übernehmen.
        painter.setFont(font)
        # Die Nummer des heutigen Zyklustags
        # mittig in den Marker schreiben.
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

        # Rechteck für die erste Textzeile festlegen.
        mitte_rect = QRectF(mitte_x - 70, mitte_y - 28, 140, 30)
        # Schrift für die erste Textzeile festlegen.
        font1 = QFont("Segoe UI", 15, QFont.Weight.Bold)
        painter.setFont(font1) # Schrift übernehmen.
        painter.setPen(QPen(QColor(173, 20, 87)))# Textfarbe festlegen
        # Erste Textzeile zentriert zeichnen.
        painter.drawText(mitte_rect, Qt.AlignmentFlag.AlignCenter, self.mitte_zeile1)

        # Rechteck für die zweite Textzeile festlegen
        mitte_rect2 = QRectF(mitte_x - 70, mitte_y + 4, 140, 24)
        font2 = QFont("Segoe UI", 10) # Kleinere Schrift für die zweite Textzeile erstellen.
        painter.setFont(font2) # Schrift übernehmen.
        painter.setPen(QPen(QColor(136, 14, 79))) # Etwas dunklere Textfarbe festlegen.
        # Zweite Textzeile zentriert zeichnen.
        painter.drawText(mitte_rect2, Qt.AlignmentFlag.AlignCenter, self.mitte_zeile2)

        # Zeichenvorgang beenden.
        painter.end()

    # ── Hilfsmethoden ────────────────────────────────────────────────────

    # Diese Methode wandelt einen Zyklustag in einen Winkel um.
    def tag_zu_winkel(self, tag, zyklus_laenge):
        # Berechnen, welcher Anteil des gesamten Zyklus
        # vor dem angegebenen Tag liegt.
        #
        # Bei Tag 1 ist der Anteil 0.
        anteil = (tag - 1) / zyklus_laenge

        # Den Anteil in einen Winkel umrechnen.
        #
        # -90° entspricht der oberen Position des Kreises.
        # Danach wird im Uhrzeigersinn über 360° weitergerechnet.
        return -90 + anteil * 360

    # Diese Methode berechnet die x- und y-Koordinaten
    # eines Punkts auf dem Kreis.
    def punkt_auf_ring(self, mitte_x, mitte_y, radius, winkel_grad):
        # Den Winkel von Grad in Bogenmaß umwandeln,
        # da sin und cos mit Bogenmaß arbeiten.
        winkel_rad = math.radians(winkel_grad)
        # Die x-Koordinate des Punkts auf dem Kreis berechnen.
        x = mitte_x + radius * math.cos(winkel_rad)
        # Die y-Koordinate des Punkts auf dem Kreis berechnen.
        y = mitte_y + radius * math.sin(winkel_rad)

        # Den berechneten Punkt als QPointF zurückgeben.
        return QPointF(x, y)

    # Diese Methode zeichnet einen farbigen Abschnitt des Zyklusrings.
    def bogen_zeichnen(self, painter, ring_rect, ring_breite,
                       tag_start, tag_ende, zyklus_laenge, farbe):

        # Berechnen, an welcher relativen Position des Zyklus
        # der farbige Abschnitt beginnt.
        anteil_start = (tag_start - 1) / zyklus_laenge
        # Berechnen, an welcher relativen Position des Zyklus
        # der farbige Abschnitt endet.
        anteil_ende  = tag_ende / zyklus_laenge

        # Den Startpunkt des Bogens in Grad berechnen.
        #
        # QPainter verwendet eine andere Winkelorientierung
        # als die zuvor verwendeten mathematischen Funktionen.
        start_grad = 90 - anteil_start * 360

        # Berechnen, über wie viele Grad sich der Bogen erstreckt.
        #
        # Der negative Wert sorgt dafür, dass der Bogen
        # im Uhrzeigersinn gezeichnet wird.
        spann_grad = -(anteil_ende - anteil_start) * 360

        pen = QPen(farbe) # Einen Zeichenstift mit der übergebenen Farbe erstellen.
        pen.setWidth(ring_breite) # Breite des Bogens festlegen.
        pen.setCapStyle(Qt.PenCapStyle.RoundCap) # Die Enden des Bogens werden abgerundet dargestellt.
        painter.setPen(pen) # Den Zeichenstift für den Painter übernehmen.
        painter.setBrush(Qt.BrushStyle.NoBrush) # Keine Füllung verwenden, da nur der Bogen gezeichnet wird.

        # Den Bogen zeichnen.
        #
        # QPainter erwartet Winkelwerte nicht direkt in Grad,
        # sondern in Sechzehntelgraden.
        # Deshalb werden die Werte jeweils mit 16 multipliziert.
        painter.drawArc(
            ring_rect,
            int(start_grad * 16),
            int(spann_grad * 16)
        )
