import webbrowser
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton



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

        beschreibung = QLabel("Aktuelle Artikel aus PubMed:")
        layout.addWidget(beschreibung)

        artikel_links = erstelle_artikel_links(suchbegriff)

        for link in artikel_links:
            button = QPushButton(link)
            button.clicked.connect(lambda checked, url=link: webbrowser.open(url))
            layout.addWidget(button)

        zentral.setLayout(layout)
        self.setCentralWidget(zentral)