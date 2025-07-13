from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QDialog

from models.users import User, create_or_update_user, get_all_users
from views.message_box_view import show_message


def normalize(text):
    return text.strip().lower() if text else ""


class Account(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/account_view.ui", self)
        self.setWindowIcon(QIcon('assets/Logo.ico'))
        self.setWindowTitle("Accounts")
        self.settings = QSettings("Griin", "GriinPower")

        self.selected_user = User()
        self.username_field.setFocus()
        self.users_list.clicked.connect(self.user_selected)
        self.clear_form_btn.clicked.connect(self.clear_form)
        self.save_user_btn.clicked.connect(self.save_user)

        self.all_users = []
        self.refresh_page()
        self.clear_form(refresh=False)

        self.users_list.setAlternatingRowColors(True)
        self.show()

    def refresh_page(self):
        success, users_or_msg = get_all_users()
        if not success:
            show_message(users_or_msg, "Error")
            return

        self.all_users = users_or_msg
        filtered_users = [user for user in self.all_users if user.username.lower() != "system"]

        model = QStandardItemModel()
        for user in filtered_users:
            item = QStandardItem(f"{user.first_name} {user.last_name}".title())
            item.setData(user)
            model.appendRow(item)
        self.users_list.setModel(model)

    def user_selected(self, index):
        item = self.users_list.model().itemFromIndex(index)
        if item is None or item.data() is None:
            return

        self.selected_user = item.data()

        user_id_name = f"User ID: {self.selected_user.id}\n\n" + f"{self.selected_user.first_name} {self.selected_user.last_name}".title()
        self.user_id_name_filed.setText(user_id_name)

        self.username_field.setText(self.selected_user.username)
        self.firstname_field.setText(self.selected_user.first_name)
        self.lastname_field.setText(self.selected_user.last_name)
        self.phone_field.setText(self.selected_user.phone)
        self.email_field.setText(self.selected_user.email)
        self.role_field.setCurrentText(self.selected_user.role)

    def clear_form(self, refresh=True):
        self.selected_user = User()
        self.user_id_name_filed.setText("User ID: -\n\n")
        self.username_field.clear()
        self.firstname_field.clear()
        self.lastname_field.clear()
        self.phone_field.clear()
        self.email_field.clear()
        self.password_field.clear()
        self.role_field.setCurrentIndex(-1)
        self.username_field.setFocus()
        self.users_list.clearSelection()

        if refresh:
            self.refresh_page()

    def save_user(self):
        self.selected_user.username = normalize(self.username_field.text())
        self.selected_user.first_name = normalize(self.firstname_field.text())
        self.selected_user.last_name = normalize(self.lastname_field.text())
        self.selected_user.phone = normalize(self.phone_field.text())
        self.selected_user.email = normalize(self.email_field.text())
        self.selected_user.role = normalize(self.role_field.currentText())

        if not all([self.selected_user.username, self.selected_user.first_name, self.selected_user.last_name,
                    self.selected_user.role]):
            show_message("Username, first name, last name, and role are required.", "Error")
            return

        # Prompt for new password if creating a new user
        if not self.selected_user.id:
            password = self.password_field.text().strip()
            if not password:
                show_message("Password is required for new users.", "Error")
                self.password_field.setFocus()
                return
            self.selected_user.password = password
        else:
            password = self.password_field.text().strip()
            if password:
                self.selected_user.password = password  # Only update if provided

        success, message = create_or_update_user(self.selected_user)
        if success:
            self.clear_form()
        else:
            show_message(message, "Error")
