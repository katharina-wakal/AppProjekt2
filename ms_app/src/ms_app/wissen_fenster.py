import webbrowser
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from wissen_api import suche_thema


class WissenFenster(QMainWindow):

    def __init__(self, titel, suchbegriff):
        super().__init__()

        self.setWindowTitle(titel)
        self.resize(500, 400)

        zentral = QWidget()
        layout = QVBoxLayout()

        ueberschrift = QLabel(titel)
        ueberschrift.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(ueberschrift)

        # API aufrufen
        ergebnis = suche_thema(suchbegriff)

        beschreibung = QLabel(ergebnis["beschreibung"])
        beschreibung.setWordWrap(True)
        beschreibung.setStyleSheet("font-size: 13px;")
        layout.addWidget(beschreibung)

        if ergebnis["url"]:
            button = QPushButton("Mehr auf Wikipedia lesen")
            button.clicked.connect(
                lambda checked, url=ergebnis["url"]: webbrowser.open(url)
            )
            layout.addWidget(button)

        zentral.setLayout(layout)
        self.setCentralWidget(zentral)