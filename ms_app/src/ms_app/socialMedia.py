import pathlib
from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import pyqtSignal

from ms_app.contact import Contact


class SocialMedia(QtWidgets.QWidget):

    s_show_social_media = pyqtSignal()

    def __init__(self, s_show_main_page):
        super(SocialMedia, self).__init__()

        working_dir = str(pathlib.Path(__file__).parent.resolve())
        self.page = uic.loadUi(working_dir + '/resources/social_media.ui', self)

        # signal used to go from contact window back to the social media window
        # same like the signal passed from main page to this page
        self.s_show_social_media.connect(self.show)
        self.contact_window = Contact(self.s_show_social_media)

        # this signal is passed by the main page to show the main window.
        # when emitting, make sure to close the currently shown sub window
        self.s_show_main_page = s_show_main_page

        self.button_pressed()

    def button_pressed(self):
        """
        Listens to a button press. When the button main page is pressed, call self.change_window().
        """
        self.btnChangePage.clicked.connect(self.change_window_main)
        self.btnChangePageContact.clicked.connect(self.change_window_contact)

    def change_window_main(self):
        """
        Closes this sub window and opens the main page again by emitting the signal.
        """
        self.s_show_main_page.emit()
        self.close()

    def change_window_contact(self):
        """
        Changes to the contact window via .show() command. The close() command closes the main window, otherwise
        both window would be shown.
        """
        self.contact_window.show()
        self.close()
