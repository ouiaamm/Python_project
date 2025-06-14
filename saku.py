from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QHBoxLayout, QProgressBar, QCheckBox, QScrollArea, QLabel, QDateEdit
)
from PySide6.QtCore import Qt, QUrl, QTimer, QTime, QDate
from PySide6.QtGui import QIcon, QPixmap 
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from database import save_task, update_task_details, delete_task, get_user_tasks
from datetime import datetime

WINDOW_WIDTH = 736
WINDOW_HEIGHT = 413
ICON_PATH = "saku.jpg"
DEFAULT_THEME = "theme0"

class ClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.update_clock()
        
        self.clock_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #5A7EC9;
                text-align: center;
            }
        """)
        
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        self.layout.addWidget(self.clock_label)
        self.setLayout(self.layout)

    def update_clock(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.clock_label.setText(current_time)

class MainWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        self.setWindowTitle("SakuDo")
        self.setGeometry(400, 200, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowIcon(QIcon(ICON_PATH))

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setSource(QUrl.fromLocalFile("m0.mp3"))
        self.music_playing = False
        self.media_player.mediaStatusChanged.connect(self.loop_music)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.init_ui()
        self.apply_theme(DEFAULT_THEME)
        self.load_user_tasks()

    def init_ui(self):
        self.init_left_section()
        self.init_right_section()

    def init_left_section(self):
        self.left_section = QWidget()
        self.left_section.setStyleSheet("background: transparent;")
        self.left_layout = QVBoxLayout(self.left_section)

        self.init_theme_buttons()
        self.init_task_input()
        self.init_task_list()
        self.init_progress_bar()

        self.main_layout.addWidget(self.left_section)

    def init_theme_buttons(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)

        for i in range(4):
            btn = QPushButton(str(i), self)
            btn.setStyleSheet(self.button_style())
            btn.clicked.connect(lambda _, theme=f"theme{i}": self.apply_theme(theme))
            layout.addWidget(btn)

        self.left_layout.addLayout(layout)

    def init_task_input(self):
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Enter a new task")
        self.task_input.setStyleSheet("""
        QLineEdit {
            background-color: white;
            border-radius: 5px;
            min-width: 200px;
            padding: 5px;
            border: 2px solid #5A7EC9;
        }
    """)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        
        self.date_input.setStyleSheet("""
        QDateEdit {
            background-color: white;
            border: 1px solid #5A7EC9;
            border-radius: 5px;
            padding: 2px;
            min-width: 90px;
            max-width: 100px;
            font-size: 12px;
        }
        QDateEdit::drop-down {
            width: 16px;
        }
    """)
        self.date_input.setStyleSheet(self.date_input_style())
        self.date_input.setFixedHeight(28)  # Match height with tas
        
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.date_input)

        self.add_task_button = QPushButton("Add task", self)
        self.add_task_button.setStyleSheet(self.add_button_style())
        self.add_task_button.clicked.connect(self.add_task_from_input)

        self.left_layout.addLayout(input_layout)
        self.left_layout.addWidget(self.add_task_button)

    def init_task_list(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(10)

        self.scroll_area.setWidget(self.scroll_widget)
        self.left_layout.addWidget(self.scroll_area)

    def init_progress_bar(self):
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet(self.progress_bar_style())
        self.progress_bar.setValue(0)
        self.left_layout.addWidget(self.progress_bar)

    def init_right_section(self):
        self.right_section = QWidget()
        self.right_section.setStyleSheet("background: transparent;")
        self.right_layout = QVBoxLayout(self.right_section)

        self.clock_widget = ClockWidget()
        self.clock_widget.setFixedSize(150, 50)
        self.right_layout.addWidget(self.clock_widget, alignment=Qt.AlignTop | Qt.AlignRight)

        self.music_button = QPushButton(self)
        self.music_button.setIcon(QIcon("off.jpg"))
        self.music_button.setIconSize(QPixmap("off.jpg").size())
        self.music_button.setFixedSize(80, 80)
        self.music_button.setStyleSheet("border: none; background-color: transparent;")
        self.music_button.clicked.connect(self.toggle_music)

        self.right_layout.addWidget(self.music_button, alignment=Qt.AlignBottom | Qt.AlignRight)
        self.main_layout.addWidget(self.right_section)

    def button_style(self):
        return """
            QPushButton {
                background-color: #5A7EC9;
                color: white;
                border-radius: 15px;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F7E0E3;
            }
        """


    def add_button_style(self):
        return """
            QPushButton {
                background-color: #5A7EC9;
                color: white;
                border-radius: 5px;
                min-width: 60px;
                max-width: 60px;
                min-height: 20px;
                max-height: 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F7E0E3;
            }
        """

    def progress_bar_style(self):
        return """
            QProgressBar {
                min-width: 200px;
                max-width: 200px;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #5A7EC9;
            }
        """

    def toggle_music(self):
        if self.music_playing:
            self.media_player.stop()
            self.music_button.setIcon(QIcon("off.jpg"))
        else:
            self.media_player.play()
            self.music_button.setIcon(QIcon("on.jpg"))
        self.music_playing = not self.music_playing

    def loop_music(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0) 
            self.media_player.play()

    def change_music(self, music_file):
        self.media_player.stop()
        self.media_player.setSource(QUrl.fromLocalFile(music_file))
        if self.music_playing:
            self.media_player.play()

    def apply_theme(self, theme):
        
        theme_files = {
            "theme0": ("images/theme0.jpg", "music/m0.mp3"),
            "theme1": ("images/theme1.jpg", "music/m1.mp3"),
            "theme2": ("images/theme2.jpg", "music/m2.mp3"),
            "theme3": ("images/theme3.jpg", "music/m3.mp3")
        }
        
        if theme in theme_files:
            bg_image, music_file = theme_files[theme]
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-image: url({bg_image});
                    background-repeat: no-repeat;
                    background-position: center;
                }}
            """)
            self.change_music(music_file)

    def add_task_from_input(self):
        task_text = self.task_input.text()
        due_date = self.date_input.date().toString("yyyy-MM-dd")
        if task_text:
            self.add_task(task_text, due_date)
            self.task_input.clear()

    def parse_date(self, date_value):
        """Handle different date formats from database"""
        if isinstance(date_value, str):
            try:
                return QDate.fromString(date_value, "yyyy-MM-dd")
            except:
                try:
                    return QDate.fromString(date_value, Qt.ISODate)
                except:
                    return QDate.currentDate()
        elif hasattr(date_value, 'year'):
            return QDate(date_value.year, date_value.month, date_value.day)
        return QDate.currentDate()

    def update_task_style(self, task_widget, due_date):
        current_date = QDate.currentDate()
        days_remaining = current_date.daysTo(due_date)
        
        if hasattr(task_widget, 'checkbox') and task_widget.checkbox.isChecked():
            task_widget.setStyleSheet("""
                background: rgba(144, 238, 144, 0.7);
                border-radius: 5px;
                padding: 5px;
                border: 1px solid rgba(50, 200, 50, 0.9);
            """)
        elif days_remaining < 0:
            task_widget.setStyleSheet("""
                background: rgba(255, 50, 50, 150);
                border-radius: 5px;
                padding: 5px;
                border: 1px solid rgba(255, 0, 0, 200);
            """)
        elif days_remaining == 0:
            task_widget.setStyleSheet("""
                background: rgba(255, 165, 0, 100);
                border-radius: 5px;
                padding: 5px;
                border: 1px solid rgba(255, 140, 0, 150);
            """)
        elif days_remaining <= 7:
            task_widget.setStyleSheet("""
                background: rgba(255, 215, 0, 80);
                border-radius: 5px;
                padding: 5px;
                border: 1px solid rgba(255, 215, 0, 120);
            """)
        else:
            task_widget.setStyleSheet("""
                background: rgba(173, 216, 230, 0.3);
                border-radius: 5px;
                padding: 5px;
            """)

    def add_task(self, task_text, due_date):
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)
        task_layout.setContentsMargins(5, 5, 5, 5)

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(lambda state: [
            self.update_task_style(task_widget, date_input.date()),
            self.update_task_in_db(task_widget),
            self.update_progress()
        ])
        task_layout.addWidget(checkbox)

        task_edit = QLineEdit(task_text)
        task_edit.setStyleSheet("border: none; background: transparent; color: black;")
        task_edit.textChanged.connect(lambda: self.update_task_in_db(task_widget))
        task_layout.addWidget(task_edit)

        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        date_input.setDate(self.parse_date(due_date))
        date_input.setStyleSheet(self.date_input_style())
        date_input.dateChanged.connect(lambda date: [
            self.update_task_style(task_widget, date),
            self.update_task_in_db(task_widget)
        ])
        task_layout.addWidget(date_input)

        delete_button = QPushButton("🗑️")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: black;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_task(task_widget))
        task_layout.addWidget(delete_button)

        task_id = save_task(self.user_id, task_text, due_date, 0)

        task_widget.task_id = task_id
        task_widget.checkbox = checkbox
        task_widget.task_edit = task_edit
        task_widget.date_input = date_input

        self.update_task_style(task_widget, date_input.date())
        self.scroll_layout.addWidget(task_widget)
        self.update_progress()

    def load_user_tasks(self):
        tasks = get_user_tasks(self.user_id)
        
        for task in tasks:
            task_widget = QWidget()
            task_layout = QHBoxLayout(task_widget)
            task_layout.setContentsMargins(5, 5, 5, 5)

            checkbox = QCheckBox()
            checkbox.setChecked(bool(task['is_completed']))
            
            date_input = QDateEdit()
            date_input.setCalendarPopup(True)
            date_input.setDate(self.parse_date(task['due_date']))
            date_input.setStyleSheet(self.date_input_style())
            
            checkbox.stateChanged.connect(lambda state, tw=task_widget, di=date_input: [
                self.update_task_style(tw, di.date()),
                self.update_task_in_db(tw),
                self.update_progress()
            ])
            task_layout.addWidget(checkbox)

            task_edit = QLineEdit(task['task_text'])
            task_edit.setStyleSheet("border: none; background: transparent; color: black;")
            task_edit.textChanged.connect(lambda: self.update_task_in_db(task_widget))
            task_layout.addWidget(task_edit)

            date_input.dateChanged.connect(lambda date, tw=task_widget: [
                self.update_task_style(tw, date),
                self.update_task_in_db(tw)
            ])
            task_layout.addWidget(date_input)

            delete_button = QPushButton("🗑️")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                    color: black;
                }
            """)
            delete_button.clicked.connect(lambda: self.delete_task(task_widget))
            task_layout.addWidget(delete_button)

            task_widget.task_id = task['task_id']
            task_widget.checkbox = checkbox
            task_widget.task_edit = task_edit
            task_widget.date_input = date_input

            self.update_task_style(task_widget, date_input.date())
            self.scroll_layout.addWidget(task_widget)
        
        self.update_progress()

    def update_task_in_db(self, task_widget):
        is_checked = 1 if task_widget.checkbox.isChecked() else 0
        update_task_details(
            task_id=task_widget.task_id,
            new_text=task_widget.task_edit.text(),
            due_date=task_widget.date_input.date().toString("yyyy-MM-dd"),
            is_completed=is_checked
        )

    def delete_task(self, task_widget):
        delete_task(task_widget.task_id)
        task_widget.deleteLater()
        self.update_progress()

    def update_progress(self):
        total_tasks = self.scroll_layout.count()
        if total_tasks == 0:
            self.progress_bar.setValue(0)
            return

        completed_tasks = 0
        for i in range(total_tasks):
            task_widget = self.scroll_layout.itemAt(i).widget()
            if task_widget and task_widget.checkbox.isChecked():
                completed_tasks += 1

        progress = int((completed_tasks / total_tasks) * 100)
        self.progress_bar.setValue(progress)

    def date_input_style(self):
        return """
            QDateEdit {
                background-color: white;
                border: 1px solid #5A7EC9;
                border-radius: 5px;
                padding: 2px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #5A7EC9;
            }
            QDateEdit::down-arrow {
                color: gray;
                width: 16px;
                height: 16px;
            }
            QCalendarWidget {
                background-color: white;
                color: black;
            }
            QCalendarWidget QToolButton {
                background-color: #5A7EC9;
                color: white;
                border-radius: 5px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: black;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #5A7EC9;
                color: white;
            }
            QCalendarWidget QAbstractItemView {
                background-color: white;
                color: black;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: gray;
            }
        """