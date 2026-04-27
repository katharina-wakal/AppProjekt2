"""
My first application
"""
import pathlib
from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import pyqtSignal
import sys

from ms_app.settings import Settings
from ms_app.socialMedia import SocialMedia


"""
This is toga code. Use this instead of PyQt6 if you want to develop for iOS or Android.
"""
# import toga
# from toga.style import Pack
# from toga.style.pack import COLUMN, ROW
#
#
# class MSApplikation(toga.App):
#     def startup(self):
#         """Construct and show the Toga application.
#
#         Usually, you would add your application to a main content box.
#         We then create a main window (with a name matching the app), and
#         show the main window.
#         """
#         main_box = toga.Box()
#
#         self.main_window = toga.MainWindow(title=self.formal_name)
#         self.main_window.content = main_box
#         self.main_window.show()


class MainPage(QtWidgets.QMainWindow):

    s_show_main_page = pyqtSignal()

    def __init__(self):
        super(MainPage, self).__init__()

        working_dir = str(pathlib.Path(__file__).parent.resolve())
        # creating the main window
        self.main_window = uic.loadUi(working_dir + '/resources/main_window.ui', self)

        # this signal can be called by the sub windows to show the main page again.
        # Don't forget to close the sub window when emitting this signal
        self.s_show_main_page.connect(self.show)

        # creating the other windows by creating an object of their class
        # the passed signal is important!
        self.social_media_window = SocialMedia(self.s_show_main_page)
        self.settings_window = Settings(self.s_show_main_page)

        self.button_pressed()
        self.show()

    def button_pressed(self):
        """
        Listens to a button press. Depending on the button pressed, a sub window is created.
        """
        self.btnChangePageSM.clicked.connect(self.change_window_sm)
        self.btnChangePageSettings.clicked.connect(self.change_window_settings)

    def change_window_sm(self):
        """
        Changes to the social media window via .show() command. The close() command closes the main window, otherwise
        both window would be shown.
        """
        self.social_media_window.show()
        self.close()

    def change_window_settings(self):
        """
        Changes to the settings window via .show() command. The close() command closes the main window, otherwise
        both window would be shown.
        """
        self.settings_window.show()
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainPage()
    sys.exit(app.exec())
