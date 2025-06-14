import sys
from PySide6.QtWidgets import QApplication
from auth_form import LoginWindow
from saku import MainWindow

def main():
    app = QApplication(sys.argv)
    
    login_window = LoginWindow()
    main_window = None
    
    def handle_login(user_id):
        login_window.close()
        nonlocal main_window
        main_window = MainWindow(user_id)
        main_window.show()
    
    login_window.success_callback = handle_login
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()