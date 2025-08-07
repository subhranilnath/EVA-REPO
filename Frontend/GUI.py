
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel
from PyQt5.QtGui import QIcon, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values  # For loading environment variables
import sys
import os

# Load environment variables from .env file
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")

# Define paths to resource directories
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

# Write 'False' to Mic.data file - indicates mic is OFF initially
def MicButtonInitialed():
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write("False")

# Write 'True' to Mic.data file - indicates mic is ON
def MicButtonClosed():
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write("True")

# Returns full path of a graphics file
def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'

# Returns full path of a temp file
def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'

# Writes a message to the Responses.data file for display
def ShowTextToScreen(Text):
    with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
        file.write(Text)

# Set microphone status by writing to Mic.data
def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)

# Get microphone status by reading from Mic.data
def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

# Set assistant status by writing to Status.data
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# Get assistant status by reading from Status.data
def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status


# ---------------- CHAT SECTION WIDGET ---------------- #
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)

        # Chat display box (Read-only)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("background-color: white; color: black; font-family: 'Segoe UI';")
        self.chat_text_edit.setFont(QFont("Segoe UI", 13))
        layout.addWidget(self.chat_text_edit)

        # GIF animation at the bottom-right corner
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Eva.gif'))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()

        # Live speech status text (shown on bottom)
        self.label = QLabel("")
        self.label.setStyleSheet("color: #213555; font-size:16px; font-family:'Segoe UI'; margin-right: 195px; border: none; margin-top: -30px")
        self.label.setAlignment(Qt.AlignRight)

        layout.addWidget(self.label)
        layout.addWidget(self.gif_label)

        self.old_chat_message = ""  # Keeps track of previously shown messages

        # Timer triggers loading and updating messages every 100ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    # Reads from Responses.data and displays new messages
    def loadMessages(self):
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                if messages and messages != self.old_chat_message:
                    print("Displaying message:", messages)
                    self.addMessages(messages, color="black")
                    self.old_chat_message = messages
        except Exception as e:
            print("Error reading Responses.data:", e)

    # Reads speech recognition status and updates label
    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                self.label.setText(file.read())
        except Exception as e:
            print("Error reading Status.data:", e)

    # Adds new chat messages with formatting
    def addMessages(self, messages, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(messages + '\n')
        self.chat_text_edit.setTextCursor(cursor)

# ---------------- INITIAL HOME SCREEN ---------------- #
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 150)

        # Fullscreen GIF background
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Eva.gif'))
        movie.setScaledSize(QSize(screen_width, int(screen_width / 16 * 9)))
        gif_label.setMovie(movie)
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        # Icon in center
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)

        icon_wrapper = QHBoxLayout()
        icon_wrapper.addStretch()
        icon_wrapper.addWidget(self.icon_label)
        icon_wrapper.addStretch()

        # Live speech status label
        self.label = QLabel("")
        self.label.setStyleSheet("color:#213555; font-size:16px; font-family:'Segoe UI'; margin-bottom:0;")
        self.label.setAlignment(Qt.AlignCenter)

        # Mic toggle state
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon  # Clicking toggles mic

        # Add elements to layout
        content_layout.addWidget(gif_label)
        content_layout.addLayout(icon_wrapper)
        content_layout.addWidget(self.label)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: white;")

        # Periodically update speech status
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    # Display live speech recognition text
    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                self.label.setText(file.read())
        except Exception as e:
            print("Error reading Status.data:", e)

    # Load and scale icon image
    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    # Toggle mic on/off icon and update Mic.data
    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

# ---------------- CHAT SCREEN (used in page 2) ---------------- #
class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(""))  # Spacer label
        layout.addWidget(ChatSection())  # Embed the ChatSection
        self.setLayout(layout)
        self.setStyleSheet("background-color: white;")

# ---------------- CUSTOM TOP NAVIGATION BAR ---------------- #
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 0, 10, 0)

        # Left: App title
        left_layout = QHBoxLayout()
        title_label = QLabel(f"{str(Assistantname).capitalize()} AI")
        title_label.setStyleSheet("color: #3D74B6; font-weight: bolder; font-size: 35px; font-family:'Segoe UI'; background-color:white")
        left_layout.addWidget(title_label)

        # Center: Navigation buttons
        center_layout = QHBoxLayout()
        home_button = QPushButton()
        home_button.setIcon(QIcon(GraphicsDirectoryPath("Home.png")))
        home_button.setText(" Home")
        home_button.setStyleSheet("background-color:white; color:#3D74B6; font-family:'Segoe UI';")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))  # Go to InitialScreen

        message_button = QPushButton()
        message_button.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")))
        message_button.setText(" Chat")
        message_button.setStyleSheet("background-color:white; color:#3D74B6; font-family:'Segoe UI';")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))  # Go to MessageScreen

        center_layout.addWidget(home_button)
        center_layout.addSpacing(10)
        center_layout.addWidget(message_button)

        # Right: Window control buttons
        right_layout = QHBoxLayout()
        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath("Minimize2.png")))
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath("Close.png")))
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        right_layout.addWidget(minimize_button)
        right_layout.addWidget(self.maximize_button)
        right_layout.addWidget(close_button)

        # Combine all layouts
        main_layout.addLayout(left_layout)
        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    # Minimize window
    def minimizeWindow(self):
        self.parent().showMinimized()

    # Maximize/restore window
    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    # Close window
    def closeWindow(self):
        self.parent().close()

# ---------------- MAIN APPLICATION WINDOW ---------------- #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove default title bar
        self.initUI()

    def initUI(self):
        # Get screen size for fullscreen layout
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # Stack of two screens: Initial and Chat
        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(MessageScreen())

        # Custom title bar
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)

        # Window setup
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color:white;")
        self.setCentralWidget(stacked_widget)

# ---------------- RUN THE APP ---------------- #
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# Entry point
if __name__ == "__main__":
    GraphicalUserInterface()