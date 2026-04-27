import pathlib
from PyQt6 import uic, QtWidgets


class Contact(QtWidgets.QWidget):
    def __init__(self, s_show_social_media):
        super(Contact, self).__init__()

        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.page = uic.loadUi(working_dir + '/resources/contact.ui', self)

        # this signal is passed by the main page to show the main window.
        # when emitting, make sure to close the currently shown sub window
        self.s_show_social_media = s_show_social_media

        self.button_pressed()

    def button_pressed(self):
        """
        Listens to a button press. When the button main page is pressed, call self.change_window().
        """
        self.btnChangePage.clicked.connect(self.change_window_sm)

    def change_window_sm(self):
        """
        Closes this sub window and opens the main page again by emitting the signal.
        """
        self.s_show_social_media.emit()
        self.close()
