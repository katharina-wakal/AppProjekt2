"""
FemHealth – Kalender Widget
Erzeuge den Kalender dynamisch mit PyQt6.

Voraussetzung:
    pip install PyQt6

Starten:
    python kalender_widget.py
"""

import sys
from datetime import date, timedelta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QFrame, QLabel,
    QPushButton, QScrollArea, QGridLayout, QVBoxLayout,
    QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont


# ──────────────────────────────────────────────
#  Beispieldaten – durch echte DB-Daten ersetzen
# ──────────────────────────────────────────────

PERIOD_DATA = [
    (date(2026, 5, 4),  date(2026, 5, 8)),
    (date(2026, 4, 6),  date(2026, 4, 10)),
    (date(2026, 3, 9),  date(2026, 3, 13)),
    (date(2026, 2, 10), date(2026, 2, 14)),
    (date(2026, 1, 13), date(2026, 1, 17)),
]

OVULATION_DATA = [
    # (zone_start, zone_end, peak_day)
    (date(2026, 5, 16), date(2026, 5, 20), date(2026, 5, 18)),
    (date(2026, 4, 18), date(2026, 4, 22), date(2026, 4, 20)),
    (date(2026, 3, 21), date(2026, 3, 25), date(2026, 3, 23)),
    (date(2026, 2, 22), date(2026, 2, 26), date(2026, 2, 24)),
    (date(2026, 1, 25), date(2026, 1, 29), date(2026, 1, 27)),
    (date(2026, 5, 30), date(2026, 6,  3), date(2026, 6,  1)),
]

# key: date-Objekt  value: dict mit Eintragsdaten
LOGS = {
    date(2026, 5, 4):  {"period": True, "intensity": 4,
                        "symptoms": ["Krämpfe", "Rückenschmerzen"],
                        "mood": "😔", "note": "Starker erster Tag"},
    date(2026, 5, 5):  {"period": True, "intensity": 3,
                        "symptoms": ["Krämpfe", "Müdigkeit"],
                        "mood": "😐", "note": ""},
    date(2026, 5, 6):  {"period": True, "intensity": 2,
                        "symptoms": ["Müdigkeit"], "mood": "😐", "note": ""},
    date(2026, 5, 7):  {"period": True, "intensity": 1,
                        "symptoms": [], "mood": "🙂", "note": "Besser heute"},
    date(2026, 5, 8):  {"period": True, "intensity": 1,
                        "symptoms": [], "mood": "🙂", "note": ""},
    date(2026, 4, 6):  {"period": True, "intensity": 3,
                        "symptoms": ["Krämpfe", "Kopfschmerzen"],
                        "mood": "😔", "note": ""},
    date(2026, 4, 20): {"symptoms": ["Ausfluss", "Zervixschleim"],
                        "mood": "🌸", "note": "Eisprung-Symptome"},
    date(2026, 5, 12): {"symptoms": ["Ausfluss"],
                        "mood": "🌸", "note": "Fühlte mich energiegeladen"},
}

TODAY = date.today()


# ──────────────────────────────────────────────
#  Hilfsfunktionen
# ──────────────────────────────────────────────

def is_period(d):
    """Gibt (start, end) zurück falls d in einer Periode liegt, sonst None."""
    for s, e in PERIOD_DATA:
        if s <= d <= e:
            return s, e
    return None

def is_ovulation(d):
    """Gibt (in_zone, is_peak) zurück."""
    for s, e, peak in OVULATION_DATA:
        if s <= d <= e:
            return True, (d == peak)
    return False, False

def get_cycle_day(d):
    """Zyklustag relativ zum letzten Periodenanfang."""
    closest = None
    for s, _ in PERIOD_DATA:
        if s <= d:
            diff = (d - s).days + 1
            if closest is None or diff < closest:
                closest = diff
    return closest


# ──────────────────────────────────────────────
#  Stylesheet (identisch zum Dashboard-Design)
# ──────────────────────────────────────────────

STYLESHEET = """
QWidget {
    background-color: #FDF6F0;
    font-family: "Segoe UI", Arial, sans-serif;
}
QFrame#headerFrame {
    background-color: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 #FCE4EC, stop:0.55 #F8BBD9, stop:1 #F48FB1
    );
}
QPushButton#btnBack {
    background-color: rgba(255,255,255,0.35);
    border: none;
    border-radius: 18px;
    color: #880E4F;
    font-size: 20px;
    font-weight: bold;
}
QPushButton#btnBack:hover { background-color: rgba(255,255,255,0.55); }

QLabel#lblTitle {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: bold;
    background: transparent;
}
QLabel#lblMonthName {
    color: #880E4F;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
}
QLabel#weekday {
    color: #C2A0AD;
    font-size: 10px;
    font-weight: bold;
    background: transparent;
}

/* ── Tage ── */
QPushButton.dayBtn {
    background: transparent;
    border: none;
    border-radius: 10px;
    font-size: 13px;
    color: #4A0010;
}
QPushButton.dayBtn:hover { background: #FCE4EC; }

QPushButton.dayToday {
    color: #E91E63;
    font-weight: bold;
    border-bottom: 3px solid #E91E63;
}
QPushButton.dayPeriod      { background: #E91E63; color: #fff; border-radius: 2px; }
QPushButton.dayPeriodStart { background: #E91E63; color: #fff;
                              border-top-left-radius: 10px;
                              border-bottom-left-radius: 10px;
                              border-top-right-radius: 2px;
                              border-bottom-right-radius: 2px; }
QPushButton.dayPeriodEnd   { background: #E91E63; color: #fff;
                              border-top-right-radius: 10px;
                              border-bottom-right-radius: 10px;
                              border-top-left-radius: 2px;
                              border-bottom-left-radius: 2px; }
QPushButton.dayPeriod:hover      { background: #C2185B; }
QPushButton.dayPeriodStart:hover { background: #C2185B; }
QPushButton.dayPeriodEnd:hover   { background: #C2185B; }

QPushButton.dayOvZone      { background: #E3F2FD; color: #1565C0; border-radius: 2px; }
QPushButton.dayOvZoneStart { background: #E3F2FD; color: #1565C0;
                              border-top-left-radius: 10px;
                              border-bottom-left-radius: 10px;
                              border-top-right-radius: 2px;
                              border-bottom-right-radius: 2px; }
QPushButton.dayOvZoneEnd   { background: #E3F2FD; color: #1565C0;
                              border-top-right-radius: 10px;
                              border-bottom-right-radius: 10px;
                              border-top-left-radius: 2px;
                              border-bottom-left-radius: 2px; }
QPushButton.dayOvPeak      { background: #BBDEFB; color: #0D47A1;
                              font-weight: bold; border-radius: 10px; }

QPushButton.dayFuture      { color: #CBA8B5; }
QPushButton.dayFuture:hover { background: transparent; }

/* ── Detail Sheet ── */
QFrame#sheetFrame {
    background-color: #FFFFFF;
    border-top: 1.5px solid #F8BBD9;
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
}
QLabel#sheetDate     { color: #880E4F; font-size: 14px; font-weight: bold; background: transparent; }
QLabel#sheetCycleDay { color: #F48FB1; font-size: 11px; font-weight: bold; background: transparent; }
QLabel#sheetSection  { color: #BDBDBD; font-size: 10px; font-weight: bold; background: transparent; }
QLabel#sheetNote     {
    color: #9E9E9E; font-size: 12px; font-style: italic;
    background: #FFF5F8; border-radius: 8px; padding: 8px;
    border-left: 3px solid #F48FB1;
}
QPushButton#btnAddEntry {
    background: #FFF5F8; color: #AD1457;
    border: 1.5px solid #F48FB1; border-radius: 12px;
    font-size: 13px; font-weight: bold; min-height: 40px;
}
QPushButton#btnAddEntry:hover { background: #FCE4EC; }

QPushButton.intDot {
    border: 2px solid #F8BBD9; border-radius: 11px;
    background: #FFFFFF; color: #9E9E9E;
    font-size: 10px; min-width: 22px; max-width: 22px;
    min-height: 22px; max-height: 22px;
}
QPushButton.intDotFilled {
    background: #E91E63; border: 2px solid #E91E63;
    color: #FFFFFF; border-radius: 11px;
    font-size: 10px; min-width: 22px; max-width: 22px;
    min-height: 22px; max-height: 22px;
}
QPushButton.tagRed {
    background: #FCE4EC; color: #AD1457;
    border: none; border-radius: 12px;
    padding: 4px 10px; font-size: 11px; font-weight: bold;
}
QPushButton.tagGray {
    background: #F5F5F5; color: #757575;
    border: none; border-radius: 12px;
    padding: 4px 10px; font-size: 13px;
}
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical {
    width: 4px; background: #F8EEF2; border-radius: 2px;
}
QScrollBar::handle:vertical {
    background: #F48FB1; border-radius: 2px; min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

MONTH_NAMES = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]
WEEKDAY_NAMES = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


# ──────────────────────────────────────────────
#  Kalender Widget
# ──────────────────────────────────────────────

class KalenderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(390, 844)
        self.setStyleSheet(STYLESHEET)
        self._selected_date = None
        self._sheet_open = False
        self._build_ui()
        self._populate_calendar(start_month=1, start_year=2026, num_months=8)

    # ── UI Aufbau ──────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame(objectName="headerFrame")
        header.setFixedHeight(90)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 44, 12, 8)
        btn_back = QPushButton("‹", objectName="btnBack")
        btn_back.setFixedSize(36, 36)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self._on_back)
        title = QLabel("Kalender", objectName="lblTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spacer_right = QWidget(); spacer_right.setFixedSize(36, 36)
        hl.addWidget(btn_back)
        hl.addWidget(title, 1)
        hl.addWidget(spacer_right)
        root.addWidget(header)

        # Legende
        legend = self._build_legend()
        root.addWidget(legend)

        # Scroll Area für Kalender
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        cal_content = QWidget()
        self._cal_layout = QVBoxLayout(cal_content)
        self._cal_layout.setContentsMargins(14, 8, 14, 8)
        self._cal_layout.setSpacing(4)
        self._scroll.setWidget(cal_content)
        root.addWidget(self._scroll, 1)

        # Detail Sheet
        self._sheet = self._build_sheet()
        self._sheet.setFixedHeight(0)        # startet eingeklappt
        root.addWidget(self._sheet)

    def _build_legend(self):
        frame = QFrame()
        frame.setFixedHeight(28)
        hl = QHBoxLayout(frame)
        hl.setContentsMargins(14, 4, 14, 4)
        hl.setSpacing(12)

        def leg(color_style, text, text_color="#9E9E9E"):
            box = QLabel()
            box.setFixedSize(12, 12)
            box.setStyleSheet(f"background:{color_style};border-radius:3px;")
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color:{text_color};font-size:10px;background:transparent;")
            hl.addWidget(box)
            hl.addWidget(lbl)

        leg("#E91E63", "Periode")
        dot = QLabel(); dot.setFixedSize(8, 8)
        dot.setStyleSheet("background:#1976D2;border-radius:4px;")
        hl.addWidget(dot)
        lbl_ov = QLabel("Eisprung")
        lbl_ov.setStyleSheet("color:#1565C0;font-size:10px;background:transparent;")
        hl.addWidget(lbl_ov)
        leg("#BBDEFB;border:1px solid #90CAF9", "Prognose", "#1565C0")
        hl.addStretch()
        return frame

    def _build_sheet(self):
        frame = QFrame(objectName="sheetFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 16)
        layout.setSpacing(4)

        # Handle
        handle = QWidget()
        handle.setFixedSize(36, 4)
        handle.setStyleSheet("background:#F8BBD9;border-radius:2px;")
        hw = QHBoxLayout(); hw.addStretch(); hw.addWidget(handle); hw.addStretch()
        hw_w = QWidget(); hw_w.setLayout(hw)
        layout.addWidget(hw_w)

        self._sheet_date_lbl = QLabel(objectName="sheetDate")
        self._sheet_cycle_lbl = QLabel(objectName="sheetCycleDay")
        layout.addWidget(self._sheet_date_lbl)
        layout.addWidget(self._sheet_cycle_lbl)

        # Intensität
        self._sheet_int_section = QLabel("STÄRKE DER BLUTUNG", objectName="sheetSection")
        layout.addWidget(self._sheet_int_section)
        int_row = QHBoxLayout(); int_row.setSpacing(6)
        self._int_dots = []
        for i in range(1, 6):
            b = QPushButton(str(i))
            b.setFixedSize(22, 22)
            b.setProperty("class", "intDot")
            int_row.addWidget(b)
            self._int_dots.append(b)
        int_row.addStretch()
        int_w = QWidget(); int_w.setLayout(int_row)
        layout.addWidget(int_w)

        # Beschwerden
        self._sheet_sym_section = QLabel("BESCHWERDEN", objectName="sheetSection")
        layout.addWidget(self._sheet_sym_section)
        self._tags_row = QHBoxLayout(); self._tags_row.setSpacing(6)
        self._tags_row.addStretch()
        tags_w = QWidget(); tags_w.setLayout(self._tags_row)
        layout.addWidget(tags_w)

        # Stimmung
        self._sheet_mood_section = QLabel("STIMMUNG", objectName="sheetSection")
        layout.addWidget(self._sheet_mood_section)
        self._mood_lbl = QPushButton()
        self._mood_lbl.setFixedHeight(26)
        self._mood_lbl.setProperty("class", "tagGray")
        layout.addWidget(self._mood_lbl)

        # Notiz
        self._note_lbl = QLabel(objectName="sheetNote")
        self._note_lbl.setWordWrap(True)
        layout.addWidget(self._note_lbl)

        # Button
        self._btn_add = QPushButton("+ Eintrag hinzufügen", objectName="btnAddEntry")
        self._btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_add.clicked.connect(self._on_add_entry)
        layout.addWidget(self._btn_add)

        self._sheet_empty_lbl = QLabel("Kein Eintrag für diesen Tag")
        self._sheet_empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sheet_empty_lbl.setStyleSheet("color:#BDBDBD;font-size:13px;background:transparent;")
        layout.addWidget(self._sheet_empty_lbl)

        return frame

    # ── Kalender befüllen ──────────────────────

    def _populate_calendar(self, start_month, start_year, num_months):
        """Generiert Monatsblöcke und hängt sie in _cal_layout."""
        for i in range(num_months):
            month = (start_month - 1 + i) % 12 + 1
            year  = start_year + ((start_month - 1 + i) // 12)
            block = self._build_month(year, month)
            self._cal_layout.addWidget(block)
        self._cal_layout.addStretch()

        # Scroll zu aktuellem Monat (ca. Monat 4 = Mai bei Start Januar)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum() // 3
        ))

    def _build_month(self, year, month):
        """Erstellt einen Monatsblock (Label + Wochentage + Tages-Grid)."""
        container = QWidget()
        vl = QVBoxLayout(container)
        vl.setContentsMargins(0, 8, 0, 4)
        vl.setSpacing(4)

        # Monatsname
        month_lbl = QLabel(f"{MONTH_NAMES[month]} {year}", objectName="lblMonthName")
        vl.addWidget(month_lbl)

        # Wochentage
        wd_grid = QGridLayout()
        wd_grid.setSpacing(2)
        for col, name in enumerate(WEEKDAY_NAMES):
            lbl = QLabel(name, objectName="weekday")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wd_grid.addWidget(lbl, 0, col)
        vl.addLayout(wd_grid)

        # Tages-Grid
        day_grid = QGridLayout()
        day_grid.setSpacing(3)

        import calendar
        first_weekday = date(year, month, 1).weekday()   # 0=Mo … 6=So
        days_in_month = calendar.monthrange(year, month)[1]

        # Leere Zellen am Anfang
        col = first_weekday
        row = 0

        # Ovulations-Zonen für diesen Monat vorberechnen
        ov_zone = {}  # day -> ("start"|"mid"|"end"|"peak")
        for s, e, peak in OVULATION_DATA:
            if s.year == year and s.month == month or \
               e.year == year and e.month == month or \
               (s < date(year, month, 1) and e > date(year, month, days_in_month)):
                cur = s
                while cur <= e:
                    if cur.year == year and cur.month == month:
                        if cur == peak:
                            ov_zone[cur.day] = "peak"
                        elif cur == s:
                            ov_zone[cur.day] = "start"
                        elif cur == e:
                            ov_zone[cur.day] = "end"
                        else:
                            ov_zone[cur.day] = "mid"
                    cur += timedelta(days=1)

        for day in range(1, days_in_month + 1):
            d = date(year, month, day)
            btn = self._make_day_button(d, ov_zone)
            day_grid.addWidget(btn, row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1

        vl.addLayout(day_grid)
        return container

    def _make_day_button(self, d, ov_zone):
        """Erstellt einen Tag-Button mit dem richtigen Styling."""
        btn = QPushButton(str(d.day))
        btn.setFixedHeight(40)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        is_future = d > TODAY
        per = is_period(d)
        ov  = ov_zone.get(d.day)
        log = LOGS.get(d)

        css_class = "dayBtn"

        if per:
            s, e = per
            if d == s:
                css_class = "dayPeriodStart"
            elif d == e:
                css_class = "dayPeriodEnd"
            else:
                css_class = "dayPeriod"
        elif ov:
            if ov == "peak":
                css_class = "dayOvPeak"
            elif ov == "start":
                css_class = "dayOvZoneStart"
            elif ov == "end":
                css_class = "dayOvZoneEnd"
            else:
                css_class = "dayOvZone"

        if d == TODAY:
            css_class += " dayToday"
        if is_future:
            css_class += " dayFuture"
            btn.setEnabled(False)

        btn.setProperty("class", css_class)

        # Ovulation-Peak → kleinen blauen Punkt als Overlay
        if ov == "peak" and not per:
            self._add_peak_dot(btn)

        # Hat Eintrag → rosa Punkt unten
        if log and not is_future:
            self._add_log_dot(btn, per is not None)

        if not is_future:
            btn.clicked.connect(lambda _, day=d: self._on_day_clicked(day))

        # Wichtig: Stylesheet neu anwenden damit Klassen greifen
        btn.style().unpolish(btn)
        btn.style().polish(btn)

        return btn

    def _add_peak_dot(self, btn):
        """Blauer Punkt oben rechts auf dem Eisprung-Tag."""
        dot = QLabel(btn)
        dot.setFixedSize(7, 7)
        dot.setStyleSheet("background:#1976D2;border-radius:3px;border:1px solid #fff;")
        dot.move(btn.width() - 10, 4) if btn.width() > 0 else None
        btn.resizeEvent = lambda e, d=dot, b=btn: d.move(b.width() - 10, 4)

    def _add_log_dot(self, btn, is_period_day):
        """Rosa oder weißer Punkt unten Mitte bei vorhandenem Eintrag."""
        dot = QLabel(btn)
        dot.setFixedSize(4, 4)
        color = "rgba(255,255,255,0.7)" if is_period_day else "#F48FB1"
        dot.setStyleSheet(f"background:{color};border-radius:2px;")
        btn.resizeEvent = lambda e, d=dot, b=btn: d.move(
            (b.width() - 4) // 2, b.height() - 7)

    # ── Detail Sheet ──────────────────────────

    def _on_day_clicked(self, d: date):
        self._selected_date = d
        self._update_sheet(d)
        if not self._sheet_open:
            self._animate_sheet(open_=True)

    def _update_sheet(self, d: date):
        """Befüllt den Detail Sheet mit Daten für den angeklickten Tag."""
        WDAYS = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
        self._sheet_date_lbl.setText(
            f"{WDAYS[d.weekday()]}, {d.day}. {MONTH_NAMES[d.month]} {d.year}")

        cd = get_cycle_day(d)
        cycle_txt = f"Zyklustag {cd}" if cd else ""
        per = is_period(d)
        ov_check, is_peak = is_ovulation(d)
        if per:
            cycle_txt += " · Periode"
        elif is_peak:
            cycle_txt += " · Eisprung-Tag"
        elif ov_check:
            cycle_txt += " · Fruchtbare Phase"
        self._sheet_cycle_lbl.setText(cycle_txt)

        log = LOGS.get(d)
        has_log = log is not None

        # Intensität
        show_intensity = has_log and log.get("period") and log.get("intensity")
        self._sheet_int_section.setVisible(show_intensity)
        for widget in self._int_dots:
            widget.setVisible(False)
        if show_intensity:
            intensity = log["intensity"]
            for i, btn in enumerate(self._int_dots):
                btn.setVisible(True)
                filled = i < intensity
                btn.setProperty("class", "intDotFilled" if filled else "intDot")
                btn.style().unpolish(btn); btn.style().polish(btn)

        # Symptom Tags leeren
        self._sheet_sym_section.setVisible(False)
        while self._tags_row.count() > 1:     # letztes ist addStretch
            item = self._tags_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if has_log and log.get("symptoms"):
            self._sheet_sym_section.setVisible(True)
            for sym in log["symptoms"]:
                tag = QPushButton(sym)
                tag.setProperty("class", "tagRed")
                tag.setFixedHeight(24)
                tag.style().unpolish(tag); tag.style().polish(tag)
                self._tags_row.insertWidget(self._tags_row.count() - 1, tag)

        # Stimmung
        mood = log.get("mood", "") if has_log else ""
        self._sheet_mood_section.setVisible(bool(mood))
        self._mood_lbl.setVisible(bool(mood))
        self._mood_lbl.setText(mood)

        # Notiz
        note = log.get("note", "") if has_log else ""
        self._note_lbl.setVisible(bool(note))
        self._note_lbl.setText(note)

        # Kein Eintrag / Button
        self._sheet_empty_lbl.setVisible(not has_log)
        self._btn_add.setVisible(not has_log and d <= TODAY)

    def _animate_sheet(self, open_: bool):
        """Klappt den Sheet auf/zu mit Animation."""
        target_height = 300 if open_ else 0
        self._anim = QPropertyAnimation(self._sheet, b"maximumHeight")
        self._anim.setDuration(300)
        self._anim.setStartValue(self._sheet.height())
        self._anim.setEndValue(target_height)
        self._anim.setEasingCurve(
            QEasingCurve.Type.OutCubic if open_ else QEasingCurve.Type.InCubic)
        self._anim.start()
        self._sheet_open = open_

    # ── Slots ────────────────────────────────

    def _on_back(self):
        """Zurück zum Dashboard – hier eigene Navigation einhängen."""
        if self._sheet_open:
            self._animate_sheet(open_=False)
        else:
            print("Zurück zum Dashboard")   # eigene Logik hier

    def _on_add_entry(self):
        """Eintrag-Dialog öffnen – hier eigene Logik einhängen."""
        print(f"Eintrag hinzufügen für {self._selected_date}")


# ──────────────────────────────────────────────
#  App starten
# ──────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setWindowTitle("FemHealth – Kalender")
    widget = KalenderWidget()
    win.setCentralWidget(widget)
    win.setFixedSize(390, 844)
    win.show()
    sys.exit(app.exec())
