import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login – FemHealth")
        self.setFixedSize(450, 650)
        self.setStyleSheet("QMainWindow { background-color: #FDF6F0; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── HEADER ──────────────────────────────────────────────────────────
        header_frame = QFrame()
        header_frame.setMinimumHeight(200)
        header_frame.setMaximumHeight(200)
        header_frame.setStyleSheet("""
            QFrame#headerFrame {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0   #FCE4EC,
                    stop:0.5 #F8BBD9,
                    stop:1   #F48FB1
                );
                border-bottom-left-radius: 32px;
                border-bottom-right-radius: 32px;
            }
        """)
        header_frame.setObjectName("headerFrame")

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 32, 20, 28)
        header_layout.setSpacing(8)

        header_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        logo_icon_label = QLabel("🌺")
        logo_icon_label.setAlignment(Qt.AlignCenter)
        logo_icon_label.setStyleSheet("QLabel { font-size: 36px; background: transparent; }")
        header_layout.addWidget(logo_icon_label)

        logo_label = QLabel("FemHealth")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 32px;
                font-weight: bold;
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
            }
        """)
        header_layout.addWidget(logo_label)

        subtitle_label = QLabel("Deine Gesundheit. Dein Zyklus. Deine App.")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 220);
                font-size: 13px;
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
            }
        """)
        header_layout.addWidget(subtitle_label)

        header_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        main_layout.addWidget(header_frame)

        # ── CONTENT ─────────────────────────────────────────────────────────
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame.setStyleSheet("QFrame#contentFrame { background-color: #FDF6F0; }")

        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(40, 28, 40, 28)
        content_layout.setSpacing(0)

        # Welcome
        welcome_label = QLabel("Willkommen zurück")
        welcome_label.setStyleSheet("""
            QLabel {
                color: #AD1457;
                font-size: 22px;
                font-weight: bold;
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
                margin-bottom: 4px;
            }
        """)
        content_layout.addWidget(welcome_label)

        info_label = QLabel("Bitte melde dich an, um fortzufahren")
        info_label.setStyleSheet("""
            QLabel {
                color: #9E9E9E;
                font-size: 13px;
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
                margin-bottom: 18px;
            }
        """)
        content_layout.addWidget(info_label)

        # E-Mail
        email_label = QLabel("E-MAIL")
        email_label.setStyleSheet("""
            QLabel {
                color: #880E4F;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
                margin-top: 4px;
                margin-bottom: 5px;
            }
        """)
        content_layout.addWidget(email_label)

        self.email_line_edit = QLineEdit()
        self.email_line_edit.setMinimumHeight(48)
        self.email_line_edit.setPlaceholderText("deine@email.de")
        self.email_line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #FFF5F8;
                border: 2px solid #F8BBD9;
                border-radius: 12px;
                padding-left: 16px;
                padding-right: 16px;
                color: #4A0010;
                font-size: 14px;
                font-family: "Segoe UI", Arial, sans-serif;
                margin-bottom: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #E91E63;
                background-color: #FFFFFF;
            }
            QLineEdit:hover {
                border: 2px solid #F48FB1;
            }
        """)
        content_layout.addWidget(self.email_line_edit)

        # Passwort
        password_label = QLabel("PASSWORT")
        password_label.setStyleSheet("""
            QLabel {
                color: #880E4F;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
                margin-top: 4px;
                margin-bottom: 5px;
            }
        """)
        content_layout.addWidget(password_label)

        self.password_line_edit = QLineEdit()
        self.password_line_edit.setMinimumHeight(48)
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        self.password_line_edit.setPlaceholderText("Passwort eingeben")
        self.password_line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #FFF5F8;
                border: 2px solid #F8BBD9;
                border-radius: 12px;
                padding-left: 16px;
                padding-right: 16px;
                color: #4A0010;
                font-size: 14px;
                font-family: "Segoe UI", Arial, sans-serif;
                margin-bottom: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #E91E63;
                background-color: #FFFFFF;
            }
            QLineEdit:hover {
                border: 2px solid #F48FB1;
            }
        """)
        content_layout.addWidget(self.password_line_edit)

        # Options row (Remember me + Forgot password)
        options_layout = QHBoxLayout()
        options_layout.setSpacing(8)

        self.remember_checkbox = QCheckBox("Angemeldet bleiben")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #757575;
                font-size: 12px;
                font-family: "Segoe UI", Arial, sans-serif;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 17px;
                height: 17px;
                border-radius: 5px;
                border: 2px solid #F48FB1;
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #E91E63;
                border: 2px solid #E91E63;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #E91E63;
            }
        """)
        options_layout.addWidget(self.remember_checkbox)

        options_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        forgot_password_button = QPushButton("Passwort vergessen?")
        forgot_password_button.setFlat(True)
        forgot_password_button.setCursor(Qt.PointingHandCursor)
        forgot_password_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #F48FB1;
                border: none;
                font-size: 12px;
                font-family: "Segoe UI", Arial, sans-serif;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #AD1457;
            }
        """)
        forgot_password_button.clicked.connect(self.on_forgot_password)
        options_layout.addWidget(forgot_password_button)

        content_layout.addLayout(options_layout)

        content_layout.addSpacerItem(QSpacerItem(20, 14, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Login Button
        login_button = QPushButton("ANMELDEN")
        login_button.setMinimumHeight(52)
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F48FB1,
                    stop:1 #E91E63
                );
                color: #FFFFFF;
                border: none;
                border-radius: 14px;
                font-size: 15px;
                font-weight: bold;
                font-family: "Segoe UI", Arial, sans-serif;
                letter-spacing: 1px;
                margin-bottom: 16px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F06292,
                    stop:1 #C2185B
                );
            }
            QPushButton:pressed {
                background-color: #AD1457;
            }
        """)
        login_button.clicked.connect(self.on_login)
        content_layout.addWidget(login_button)

        # Divider "oder"
        divider_layout = QHBoxLayout()
        divider_layout.setSpacing(10)

        div_line1 = QFrame()
        div_line1.setFrameShape(QFrame.HLine)
        div_line1.setFrameShadow(QFrame.Plain)
        div_line1.setStyleSheet("color: #F8BBD9;")
        divider_layout.addWidget(div_line1)

        div_label = QLabel("oder")
        div_label.setStyleSheet("""
            QLabel {
                color: #C2A0AD;
                font-size: 12px;
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
            }
        """)
        divider_layout.addWidget(div_label)

        div_line2 = QFrame()
        div_line2.setFrameShape(QFrame.HLine)
        div_line2.setFrameShadow(QFrame.Plain)
        div_line2.setStyleSheet("color: #F8BBD9;")
        divider_layout.addWidget(div_line2)

        content_layout.addLayout(divider_layout)

        content_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Register row
        register_layout = QHBoxLayout()
        register_layout.setSpacing(6)

        register_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        no_account_label = QLabel("Noch kein Konto?")
        no_account_label.setStyleSheet("""
            QLabel {
                color: #9E9E9E;
                font-size: 13px;
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
            }
        """)
        register_layout.addWidget(no_account_label)

        register_button = QPushButton("Jetzt registrieren")
        register_button.setFlat(True)
        register_button.setCursor(Qt.PointingHandCursor)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #E91E63;
                border: none;
                font-size: 13px;
                font-weight: bold;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QPushButton:hover {
                color: #AD1457;
            }
        """)
        register_button.clicked.connect(self.on_register)
        register_layout.addWidget(register_button)

        register_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        content_layout.addLayout(register_layout)

        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        main_layout.addWidget(content_frame)

    # ── Slots ────────────────────────────────────────────────────────────────
    def on_login(self):
        email = self.email_line_edit.text().strip()
        password = self.password_line_edit.text()
        remember = self.remember_checkbox.isChecked()
        print(f"[Login] E-Mail: {email} | Passwort: {'*' * len(password)} | Angemeldet bleiben: {remember}")
        # TODO: Authentifizierungslogik hier einfügen

    def on_forgot_password(self):
        print("[Login] Passwort vergessen geklickt")
        # TODO: Passwort-Reset-Dialog öffnen

    def on_register(self):
        print("[Login] Registrieren geklickt")
        # TODO: Registrierungsfenster öffnen


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
