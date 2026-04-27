import pathlib
from PyQt6 import uic, QtWidgets


class Settings(QtWidgets.QWidget):
    def __init__(self, s_show_main_page):
        super(Settings, self).__init__()

        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.page = uic.loadUi(working_dir + '/resources/settings.ui', self)

        # this signal is passed by the main page to show the main window.
        # when emitting, make sure to close the currently shown sub window
        self.s_show_main_page = s_show_main_page

        self.button_pressed()

    def button_pressed(self):
        """
        Listens to a button press. When the button main page is pressed, call self.change_window().
        """
        self.btnChangePage.clicked.connect(self.change_window_main)

    def change_window_main(self):
        """
        Closes this sub window and opens the main page again by emitting the signal.
        """
        self.s_show_main_page.emit()
        self.close()