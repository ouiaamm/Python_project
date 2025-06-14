from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLineEdit, QLabel
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QTimer
from database import add_user, verify_user  
import bcrypt

# Styles
WELCOME_BUTTON_STYLE = """
    QPushButton {
        background: rgba(173, 216, 230, 0.99);
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        border: none;
        min-width: 100px;
    }
    QPushButton:hover {
        background-color: #F7E0E3;
    }
"""

FORM_BUTTON_STYLE = """
    QPushButton {
        background-color: #5A7EC9;
        color: white;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        border: none;
        min-width: 80px;
        max-width: 100px;
    }
    QPushButton:hover {
        background-color: #F7E0E3;
    }
"""

INPUT_FIELD_STYLE = """
    QLineEdit {
        padding: 6px;
        border-radius: 6px;
        font-size: 13px;
        border: 1px solid #ccc;
        background: white;
    }
"""

ERROR_LABEL_STYLE = "color: red; font-size: 11px;"
SUCCESS_LABEL_STYLE = "color: green; font-size: 11px;"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SakuDo")
        self.setGeometry(400, 200, 736, 413)
        self.setFixedSize(736, 413)
        self.setWindowIcon(QIcon("saku.jpg"))
        
        self.user_id = None
        self.success_callback = lambda user_id: None
     
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("images/theme0.jpg"))
        self.background.setScaledContents(True)
        self.background.setGeometry(0, 0, 736, 413)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background: transparent;")

        self.welcome_screen = WelcomeScreen(self.stacked_widget, self.handle_success)
        self.login_screen = LoginScreen(self.stacked_widget, self.handle_success)
        self.signup_screen = SignUpScreen(self.stacked_widget, self.handle_success)
        
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.signup_screen)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def handle_success(self, user_id=None):
        self.user_id = user_id
        if self.success_callback and user_id:
            self.success_callback(user_id)

class WelcomeScreen(QWidget):
    def __init__(self, stacked_widget, success_callback):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.success_callback = success_callback
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        
        welcome_label = QLabel("WELCOME TO SAKUDO")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                color: #5A7EC9; 
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 20px;
            }
            QLabel:hover {
                color: #F7E0E3;   
            }
        """)
        
        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(15)
        
        login_button = QPushButton("Login")
        login_button.setStyleSheet(WELCOME_BUTTON_STYLE)
        login_button.clicked.connect(self.go_to_login)
        
        signup_button = QPushButton("Sign Up")
        signup_button.setStyleSheet(WELCOME_BUTTON_STYLE)
        signup_button.clicked.connect(self.go_to_signup)
        
        button_layout.addWidget(login_button)
        button_layout.addWidget(signup_button)
        
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(button_container)
        self.setLayout(main_layout)

    def go_to_login(self):
        self.stacked_widget.setCurrentIndex(1)

    def go_to_signup(self):
        self.stacked_widget.setCurrentIndex(2)

class SignUpScreen(QWidget):
    def __init__(self, stacked_widget, success_callback):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.success_callback = success_callback
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

        form_container = QWidget()
        form_container.setStyleSheet("""
            background: rgba(173, 216, 230, 0.3); 
            border-radius: 10px; 
            padding: 20px;
        """)
        form_container.setFixedWidth(300)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(12)

        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(INPUT_FIELD_STYLE)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)

        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(INPUT_FIELD_STYLE)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("Confirm:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet(INPUT_FIELD_STYLE)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(ERROR_LABEL_STYLE)
        self.error_label.setAlignment(Qt.AlignCenter)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        signup_button = QPushButton("Sign Up")
        signup_button.setStyleSheet(FORM_BUTTON_STYLE)
        signup_button.clicked.connect(self.create_account)

        back_button = QPushButton("Back")
        back_button.setStyleSheet(FORM_BUTTON_STYLE)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        buttons_layout.addWidget(signup_button)
        buttons_layout.addWidget(back_button)

        form_layout.addLayout(username_layout)
        form_layout.addLayout(password_layout)
        form_layout.addLayout(confirm_layout)
        form_layout.addWidget(self.error_label)
        form_layout.addLayout(buttons_layout)

        main_layout.addWidget(form_container)

    def create_account(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not username or not password or not confirm:
            self.error_label.setText("Please fill in all fields!")
            return

        if password != confirm:
            self.error_label.setText("Passwords don't match!")
            return

        if len(password) < 6:
            self.error_label.setText("Password must be 6+ characters")
            return

        success = add_user(username, password)
        if success:
            self.error_label.setText("Account created successfully!")
            self.error_label.setStyleSheet(SUCCESS_LABEL_STYLE)
            QTimer.singleShot(1000, lambda: self.login_after_signup(username, password))
        else:
            self.error_label.setText("Username already exists!")

    def login_after_signup(self, username, password):
        user_id = verify_user(username, password)
        if user_id:
            self.success_callback(user_id)

class LoginScreen(QWidget):
    def __init__(self, stacked_widget, success_callback):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.success_callback = success_callback
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

        form_container = QWidget()
        form_container.setStyleSheet("""
            background: rgba(173, 216, 230, 0.3);
            border-radius: 10px; 
            padding: 20px;
        """)
        form_container.setFixedWidth(300)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(12)

        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(INPUT_FIELD_STYLE)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)

        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(INPUT_FIELD_STYLE)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(ERROR_LABEL_STYLE)
        self.error_label.setAlignment(Qt.AlignCenter)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        login_button = QPushButton("Login")
        login_button.setStyleSheet(FORM_BUTTON_STYLE)
        login_button.clicked.connect(self.check_credentials)

        back_button = QPushButton("Back")
        back_button.setStyleSheet(FORM_BUTTON_STYLE)
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        buttons_layout.addWidget(login_button)
        buttons_layout.addWidget(back_button)

        form_layout.addLayout(username_layout)
        form_layout.addLayout(password_layout)
        form_layout.addWidget(self.error_label)
        form_layout.addLayout(buttons_layout)

        main_layout.addWidget(form_container)

    def check_credentials(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_label.setText("Please fill in all fields!")
            return

        user_id = verify_user(username, password)
        
        if user_id:
            self.error_label.setText("Login successful!")
            self.error_label.setStyleSheet(SUCCESS_LABEL_STYLE)
            QTimer.singleShot(1000, lambda: self.success_callback(user_id))
        else:
            self.error_label.setText("Invalid username or password!")