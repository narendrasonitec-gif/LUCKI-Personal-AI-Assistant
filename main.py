import sys
import threading

from pathlib import Path
import os

# Load .env from the same folder as main.py BEFORE importing ai/brain modules.
# This works even when VS Code's current working directory is a different folder.
PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=ENV_FILE, override=False)
except ImportError:
    # Small fallback parser so python-dotenv is not mandatory.
    if ENV_FILE.is_file():
        for raw_line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key and key not in os.environ:
                os.environ[key] = value

# Do not print or expose the secret itself.
if not os.getenv("GEMINI_API_KEY", "").strip():
    print(f"[LUCKI] Gemini API key missing. Expected GEMINI_API_KEY in: {ENV_FILE}")
else:
    print(f"[LUCKI] Gemini API key detected. Model: {os.getenv('GEMINI_MODEL', 'default')}")


from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QInputDialog,
    QFileDialog,
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import (
    Qt,
    Signal,
    QObject,
    QTimer,
    QPropertyAnimation,
    QSettings,
    QEasingCurve,
)

from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QFont,
)

from ai import ask_ai
from brain import process_command
from computer_control import screenshot

from memory import (
    add_note,
    add_task,
    delete_note,
    delete_task,
    notes,
    profile,
    remember,
    tasks,
    toggle_task,
)

from orb import AnimatedOrb
from phone_monitor import PhoneCallMonitor
from screen_vision import analyze_screen
from styles import STYLE

from user_profile import (
    first_greeting,
    get_user_name,
    set_user_name,
)

from voice import (
    get_voice,
    set_voice,
    speak,
    voice_label,
    listen,
)

from wake_word import wait_for_wake_word
from startup_manager import enable_startup


# =============================================================
# SIGNALS
# =============================================================

class Signals(QObject):

    status = Signal(str)
    user = Signal(str)
    reply = Signal(str)
    student = Signal(str)
    phone_call = Signal(str)
    show_window = Signal()
    hide_window = Signal()


# =============================================================
# STARTUP SCREEN
# =============================================================

class StartupScreen(QWidget):
    """Full-screen, one-time-per-launch Lucki brand animation."""

    def __init__(self):
        super().__init__()
        self.project_dir = Path(__file__).resolve().parent
        self.setWindowTitle("LUCKI AI")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QWidget { background: #03060b; color: white; }
            #LuckiWord { color: white; font-family: 'Segoe UI'; font-size: 104px; font-weight: 800; letter-spacing: 14px; }
            #FromBrand { color: #8b9cff; font-family: 'Segoe UI'; font-size: 24px; font-weight: 500; letter-spacing: 2px; }
            #Line { color: #39d9ff; font-size: 11px; letter-spacing: 6px; }
        """)

        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        else:
            self.showFullScreen()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(0)

        self.line = QLabel("L U C K I   A I")
        self.line.setObjectName("Line")
        self.line.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.line)

        layout.addSpacing(24)
        self.word = QLabel("LUCKI AI")
        self.word.setObjectName("LuckiWord")
        self.word.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.word)

        layout.addSpacing(26)
        self.from_brand = QLabel("SSK")
        self.from_brand.setObjectName("FromBrand")
        self.from_brand.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.from_brand)

        # Initial hidden state for a clean fade-in.
        self.word_effect = QGraphicsOpacityEffect(self.word)
        self.word.setGraphicsEffect(self.word_effect)
        self.word_effect.setOpacity(0.0)
        self.brand_effect = QGraphicsOpacityEffect(self.from_brand)
        self.from_brand.setGraphicsEffect(self.brand_effect)
        self.brand_effect.setOpacity(0.0)
        self.line_effect = QGraphicsOpacityEffect(self.line)
        self.line.setGraphicsEffect(self.line_effect)
        self.line_effect.setOpacity(0.0)

        self._animations = []
        self._fade(self.line_effect, 550, 0.0)
        self._fade(self.word_effect, 950, 0.25)
        self._fade(self.brand_effect, 800, 1.15)

    def _fade(self, effect, duration, delay):
        def go():
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
            self._animations.append(anim)
        QTimer.singleShot(int(delay * 1000), go)


class FirstRunSetup(QDialog):
    """One-time professional setup/consent screen."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set up LUCKI AI")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.setStyleSheet("""
            QDialog { background:#080c14; color:white; }
            QLabel { color:white; }
            QCheckBox { color:#e2e8f0; padding:8px 0; }
            QPushButton { background:#111827; color:white; border:1px solid #334155; border-radius:10px; padding:11px; }
            QPushButton:hover { background:#172033; }
            QLineEdit { background:#0b1220; color:white; border:1px solid #334155; border-radius:9px; padding:10px; }
        """)
        lay=QVBoxLayout(self); lay.setContentsMargins(30,26,30,24); lay.setSpacing(10)
        title=QLabel("Welcome to LUCKI AI"); title.setStyleSheet("font-size:28px;font-weight:700;")
        lay.addWidget(title)
        sub=QLabel("Let's set up your assistant. You stay in control of every permission."); sub.setWordWrap(True); sub.setStyleSheet("color:#94a3b8;font-size:14px;")
        lay.addWidget(sub)
        lay.addSpacing(8)
        self.name=QLineEdit(); self.name.setPlaceholderText("What should Lucki call you?")
        lay.addWidget(self.name)
        self.mic=QCheckBox("🎙 Microphone — listen for voice commands and wake words")
        self.screen=QCheckBox("👁 Screen analysis — only when you ask Lucki to analyze the screen")
        self.pc=QCheckBox("💻 Computer control — open apps, websites and supported actions")
        self.phone=QCheckBox("📱 Phone integration — optional Windows Phone Link features")
        self.mic.setChecked(True); self.screen.setChecked(True); self.pc.setChecked(True)
        for w in (self.mic,self.screen,self.pc,self.phone): lay.addWidget(w)
        note=QLabel("Lucki does not silently bypass Windows permissions. Screen analysis is captured when requested, not continuously recorded.")
        note.setWordWrap(True); note.setStyleSheet("color:#64748b;font-size:12px;")
        lay.addWidget(note)
        self.startup=QCheckBox("Start Lucki automatically with Windows"); self.startup.setChecked(True); lay.addWidget(self.startup)
        self.allow=QPushButton("Allow & Continue"); self.allow.clicked.connect(self.accept); lay.addWidget(self.allow)
        self.cancel=QPushButton("Exit"); self.cancel.clicked.connect(self.reject); lay.addWidget(self.cancel)

    def values(self):
        return {
            "name": self.name.text().strip() or "User",
            "mic": self.mic.isChecked(), "screen": self.screen.isChecked(),
            "pc": self.pc.isChecked(), "phone": self.phone.isChecked(),
            "startup": self.startup.isChecked(),
        }


# =============================================================
# MAIN LUCKI WINDOW
# =============================================================

class LuckiAI(QMainWindow):

    def __init__(self):

        super().__init__()

        self.running = True

        # Wake word system works automatically
        self.listening = True

        self.wake_enabled = True

        self.phone_monitor_enabled = False

        self.project_dir = (
            Path(__file__).resolve().parent
        )

        # -----------------------------------------------------
        # ASSETS
        # -----------------------------------------------------

        self.icon_path = (
            self.project_dir
            / "assets"
            / "lucki_icon.ico"
        )

        self.logo_path = (
            self.project_dir
            / "assets"
            / "lucki_logo.png"
        )

        # -----------------------------------------------------
        # WINDOW
        # -----------------------------------------------------

        self.setWindowTitle(
            "LUCKI AI — Narendra Soni"
        )

        if self.icon_path.exists():

            self.setWindowIcon(
                QIcon(
                    str(self.icon_path)
                )
            )

        self.resize(
            1250,
            780
        )

        self.setStyleSheet(
            STYLE
        )

        # -----------------------------------------------------
        # SIGNALS
        # -----------------------------------------------------

        self.signals = Signals()

        self.signals.status.connect(
            self.update_status
        )

        self.signals.user.connect(
            self.add_user_message
        )

        self.signals.reply.connect(
            self.add_lucki_message
        )

        self.signals.student.connect(
            self.show_student_result
        )

        self.signals.phone_call.connect(
            self.handle_phone_call
        )
        self.signals.show_window.connect(self._show_from_signal)
        self.signals.hide_window.connect(self._hide_from_signal)

        # -----------------------------------------------------
        # PHONE MONITOR
        # -----------------------------------------------------

        self.phone_monitor = (
            PhoneCallMonitor(
                self.signals.phone_call.emit
            )
        )

        # -----------------------------------------------------
        # PROFILE
        # -----------------------------------------------------

        self.ensure_user_profile()

        # -----------------------------------------------------
        # VOICE
        # -----------------------------------------------------

        self.load_voice_preference()

        # -----------------------------------------------------
        # UI
        # -----------------------------------------------------

        self.build_ui()

        # -----------------------------------------------------
        # WELCOME MESSAGE
        # -----------------------------------------------------

        welcome_message = (
            f"Welcome to LUCKI AI, "
            f"{self.user_name}! "
            f"SSK."
        )

        self.chat_output.append(
            f"<b>LUCKI:</b> {welcome_message}"
        )

        # -----------------------------------------------------
        # START VOICE
        # -----------------------------------------------------

        self.start_voice_loop()

    # =========================================================
    # USER PROFILE
    # =========================================================

    def ensure_user_profile(self):

        # This is a private, single-owner installation for Narendra Soni.
        name = "Narendra Soni"
        set_user_name(name)
        self.user_name = name

    # =========================================================
    # VOICE PREFERENCE
    # =========================================================

    def load_voice_preference(self):

        saved_voice = get_voice()

        if saved_voice not in [
            "maple",
            "jarvis"
        ]:

            saved_voice = "jarvis"

            set_voice(
                saved_voice
            )

        self.current_voice = (
            saved_voice
        )

    def save_voice_preference(
        self,
        name
    ):

        if name not in [
            "maple",
            "jarvis"
        ]:

            return

        set_voice(
            name
        )

        self.current_voice = name

        remember(
            "voice",
            name
        )

        if hasattr(
            self,
            "voice_status"
        ):

            self.voice_status.setText(
                f"Voice: "
                f"{self.get_display_voice_name(name)}"
            )

    def get_display_voice_name(
        self,
        voice_name
    ):

        if voice_name == "maple":

            return "Chanchu • Female"

        if voice_name == "jarvis":

            return "Lucki • Male"

        return voice_name

    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QHBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # =====================================================
        # SIDEBAR
        # =====================================================

        sidebar = QFrame()

        sidebar.setObjectName(
            "Sidebar"
        )

        sidebar.setFixedWidth(
            270
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        sidebar_layout.setSpacing(
            12
        )

        # -----------------------------------------------------
        # LOGO
        # -----------------------------------------------------

        if self.logo_path.exists():

            logo = QLabel()

            pixmap = QPixmap(
                str(self.logo_path)
            )

            pixmap = pixmap.scaled(
                220,
                120,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            logo.setPixmap(
                pixmap
            )

            logo.setAlignment(
                Qt.AlignCenter
            )

            sidebar_layout.addWidget(
                logo
            )

        else:

            logo_text = QLabel(
                "LUCKI AI"
            )

            logo_text.setAlignment(
                Qt.AlignCenter
            )

            logo_text.setObjectName(
                "LogoText"
            )

            sidebar_layout.addWidget(
                logo_text
            )

        # -----------------------------------------------------
        # BRAND
        # -----------------------------------------------------

        brand_label = QLabel(
            "SSK"
        )

        brand_label.setAlignment(
            Qt.AlignCenter
        )

        brand_label.setWordWrap(
            True
        )

        brand_label.setObjectName(
            "SideInfo"
        )

        sidebar_layout.addWidget(
            brand_label
        )

        # -----------------------------------------------------
        # USER
        # -----------------------------------------------------

        self.user_status = QLabel(
            f"Owner: {self.user_name}"
        )

        self.user_status.setObjectName(
            "SideInfo"
        )

        sidebar_layout.addWidget(
            self.user_status
        )

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        self.status_label = QLabel(
            "Status: Waiting for wake word"
        )

        self.status_label.setObjectName(
            "SideInfo"
        )

        sidebar_layout.addWidget(
            self.status_label
        )

        # -----------------------------------------------------
        # VOICE STATUS
        # -----------------------------------------------------

        self.voice_status = QLabel(
            f"Voice: "
            f"{self.get_display_voice_name(get_voice())}"
        )

        self.voice_status.setObjectName(
            "SideInfo"
        )

        sidebar_layout.addWidget(
            self.voice_status
        )

        # -----------------------------------------------------
        # START / STOP LISTENING
        # -----------------------------------------------------

        self.listen_button = QPushButton(
            "🛑 Stop Listening"
        )

        self.listen_button.clicked.connect(
            self.toggle_listening
        )

        sidebar_layout.addWidget(
            self.listen_button
        )

        # -----------------------------------------------------
        # WAKE WORD
        # -----------------------------------------------------

        self.wake_checkbox = QCheckBox(
            "Wake Words: Lucki / Lucky / Hello / Namaste"
        )

        self.wake_checkbox.setChecked(
            True
        )

        self.wake_checkbox.stateChanged.connect(
            self.toggle_wake_word
        )

        sidebar_layout.addWidget(
            self.wake_checkbox
        )

        # -----------------------------------------------------
        # VOICE SELECT
        # -----------------------------------------------------

        voice_title = QLabel(
            "Voice"
        )

        voice_title.setObjectName(
            "SectionTitle"
        )

        sidebar_layout.addWidget(
            voice_title
        )

        self.voice_combo = QComboBox()

        self.voice_combo.addItem(
            "Chanchu • Female",
            "maple"
        )

        self.voice_combo.addItem(
            "Lucki • Male",
            "jarvis"
        )

        current_voice = get_voice()

        if current_voice == "maple":

            self.voice_combo.setCurrentIndex(
                0
            )

        else:

            self.voice_combo.setCurrentIndex(
                1
            )

        self.voice_combo.currentIndexChanged.connect(
            lambda _:
            self.save_voice_preference(
                self.voice_combo.currentData()
            )
        )

        sidebar_layout.addWidget(
            self.voice_combo
        )

        # -----------------------------------------------------
        # PHONE MONITOR
        # -----------------------------------------------------

        self.phone_checkbox = QCheckBox(
            "📱 Phone Call Monitor"
        )

        self.phone_checkbox.stateChanged.connect(
            self.toggle_phone_monitor
        )

        sidebar_layout.addWidget(
            self.phone_checkbox
        )

        # -----------------------------------------------------
        # SCREEN ANALYSIS
        # -----------------------------------------------------

        screen_button = QPushButton(
            "👁 Analyze Screen"
        )

        screen_button.clicked.connect(
            self.analyze_current_screen
        )

        sidebar_layout.addWidget(
            screen_button
        )

        # -----------------------------------------------------
        # CLEAR CHAT
        # -----------------------------------------------------

        clear_chat_button = QPushButton(
            "🗑 Clear Chat"
        )

        clear_chat_button.clicked.connect(
            self.clear_chat
        )

        sidebar_layout.addWidget(
            clear_chat_button
        )

        sidebar_layout.addStretch()

        # -----------------------------------------------------
        # FOUNDER
        # -----------------------------------------------------

        founder = QLabel(
            "Founder & Developer : Narendra Soni"
        )

        founder.setAlignment(
            Qt.AlignCenter
        )

        founder.setWordWrap(
            True
        )

        founder.setObjectName(
            "Founder"
        )

        sidebar_layout.addWidget(
            founder
        )

        # -----------------------------------------------------
        # EXIT
        # -----------------------------------------------------

        exit_button = QPushButton(
            "Exit Lucki"
        )

        exit_button.clicked.connect(
            self.close
        )

        sidebar_layout.addWidget(
            exit_button
        )

        main_layout.addWidget(
            sidebar
        )

        # =====================================================
        # MAIN CONTENT
        # =====================================================

        content = QWidget()

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            24,
            20,
            24,
            20
        )

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        title = QLabel(
            "LUCKI AI"
        )

        title.setObjectName(
            "MainTitle"
        )

        content_layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Your Smart AI Assistant"
        )

        subtitle.setObjectName(
            "Subtitle"
        )

        content_layout.addWidget(
            subtitle
        )

        brand_subtitle = QLabel(
            "SSK"
        )

        brand_subtitle.setObjectName(
            "Subtitle"
        )

        content_layout.addWidget(
            brand_subtitle
        )

        # -----------------------------------------------------
        # TABS
        # -----------------------------------------------------

        self.tabs = QTabWidget()

        content_layout.addWidget(
            self.tabs
        )

        self.build_home()

        self.build_student()

        self.build_notes()

        self.build_tasks()

        main_layout.addWidget(
            content
        )

    # =========================================================
    # HOME
    # =========================================================

    def build_home(self):

        home = QWidget()

        layout = QVBoxLayout(
            home
        )

        # -----------------------------------------------------
        # ORB
        # -----------------------------------------------------

        try:

            self.orb = AnimatedOrb()

            layout.addWidget(
                self.orb,
                alignment=Qt.AlignCenter
            )

        except Exception:

            self.orb = None

        # -----------------------------------------------------
        # CHAT
        # -----------------------------------------------------

        self.chat_output = QTextEdit()

        self.chat_output.setReadOnly(
            True
        )

        layout.addWidget(
            self.chat_output
        )

        # -----------------------------------------------------
        # INPUT
        # -----------------------------------------------------

        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()

        self.chat_input.setPlaceholderText(
            "Ask Lucki anything..."
        )

        self.chat_input.returnPressed.connect(
            self.send_text
        )

        input_layout.addWidget(
            self.chat_input
        )

        send_button = QPushButton(
            "Send"
        )

        send_button.clicked.connect(
            self.send_text
        )

        input_layout.addWidget(
            send_button
        )

        attach_button = QPushButton("Attach…")
        attach_button.setToolTip("Attach a text or PDF file")
        attach_button.clicked.connect(self.attach_file)
        input_layout.addWidget(attach_button)

        copy_button = QPushButton("Copy Chat")
        copy_button.setToolTip("Copy all visible chat text")
        copy_button.clicked.connect(self.copy_chat)
        input_layout.addWidget(copy_button)

        history_button = QPushButton("History")
        history_button.clicked.connect(self.show_history)
        input_layout.addWidget(history_button)

        compact_button = QPushButton("Small Window")
        compact_button.clicked.connect(self.toggle_compact_window)
        input_layout.addWidget(compact_button)

        layout.addLayout(
            input_layout
        )

        self.tabs.addTab(
            home,
            "Home"
        )

    # =========================================================
    # STUDENT
    # =========================================================

    def build_student(self):

        student = QWidget()

        layout = QVBoxLayout(
            student
        )

        title = QLabel(
            "Student Workspace"
        )

        title.setObjectName(
            "TabTitle"
        )

        layout.addWidget(
            title
        )

        self.student_input = QTextEdit()

        self.student_input.setPlaceholderText(
            "Ask a question, explain a topic, "
            "solve an exercise, write code..."
        )

        layout.addWidget(
            self.student_input
        )

        buttons_layout = QHBoxLayout()

        modes = [
            ("Explain", "explain"),
            ("Solve", "solve"),
            ("Code", "code"),
            ("Summarize", "summarize"),
        ]

        for text, mode in modes:

            button = QPushButton(
                text
            )

            button.clicked.connect(
                lambda _, m=mode:
                self.run_student_mode(m)
            )

            buttons_layout.addWidget(
                button
            )

        layout.addLayout(
            buttons_layout
        )

        self.student_output = QTextEdit()

        self.student_output.setReadOnly(
            True
        )

        layout.addWidget(
            self.student_output
        )

        self.tabs.addTab(
            student,
            "Student"
        )

    # =========================================================
    # NOTES
    # =========================================================

    def build_notes(self):

        notes_tab = QWidget()

        layout = QVBoxLayout(
            notes_tab
        )

        title = QLabel(
            "Notes"
        )

        title.setObjectName(
            "TabTitle"
        )

        layout.addWidget(
            title
        )

        self.notes_list = QListWidget()

        layout.addWidget(
            self.notes_list
        )

        button_layout = QHBoxLayout()

        add_button = QPushButton(
            "Add Note"
        )

        add_button.clicked.connect(
            self.add_new_note
        )

        delete_button = QPushButton(
            "Delete Note"
        )

        delete_button.clicked.connect(
            self.delete_selected_note
        )

        button_layout.addWidget(
            add_button
        )

        button_layout.addWidget(
            delete_button
        )

        layout.addLayout(
            button_layout
        )

        self.refresh_notes()

        self.tabs.addTab(
            notes_tab,
            "Notes"
        )

    # =========================================================
    # TASKS
    # =========================================================

    def build_tasks(self):

        tasks_tab = QWidget()

        layout = QVBoxLayout(
            tasks_tab
        )

        title = QLabel(
            "Tasks"
        )

        title.setObjectName(
            "TabTitle"
        )

        layout.addWidget(
            title
        )

        self.tasks_list = QListWidget()

        layout.addWidget(
            self.tasks_list
        )

        button_layout = QHBoxLayout()

        add_button = QPushButton(
            "Add Task"
        )

        add_button.clicked.connect(
            self.add_new_task
        )

        toggle_button = QPushButton(
            "Complete / Undo"
        )

        toggle_button.clicked.connect(
            self.toggle_selected_task
        )

        delete_button = QPushButton(
            "Delete Task"
        )

        delete_button.clicked.connect(
            self.delete_selected_task
        )

        button_layout.addWidget(
            add_button
        )

        button_layout.addWidget(
            toggle_button
        )

        button_layout.addWidget(
            delete_button
        )

        layout.addLayout(
            button_layout
        )

        self.refresh_tasks()

        self.tabs.addTab(
            tasks_tab,
            "Tasks"
        )

    # =========================================================
    # STATUS
    # =========================================================

    def update_status(
        self,
        text
    ):

        self.status_label.setText(
            f"Status: {text}"
        )

    # =========================================================
    # PHONE MONITOR TOGGLE
    # =========================================================

    def toggle_phone_monitor(self, state):
        """Start or stop the optional Phone Link call monitor."""
        try:
            enabled = bool(state)
            if enabled:
                self.phone_monitor.start()
                self.update_status("Phone call monitor enabled")
                self.add_lucki_message(
                    "Phone call monitor enabled. Keep Phone Link open; Windows permissions and visible call alerts are required."
                )
            else:
                self.phone_monitor.stop()
                self.update_status("Ready")
                self.add_lucki_message("Phone call monitor disabled.")
        except Exception as exc:
            message = f"Could not change phone monitor state: {exc}"
            print(message)
            try:
                self.add_lucki_message(message)
                self.update_status("Ready")
            except Exception:
                pass

    # =========================================================
    # SCREEN ANALYSIS
    # =========================================================

    def analyze_current_screen(self):
        """Analyze the visible Windows screen and show the result in chat."""
        try:
            self.update_status("Analyzing screen...")
            self.add_lucki_message("Analyzing your current screen...")
            result = analyze_screen()
            self.add_lucki_message(str(result))
            self.update_status("Ready")
            try:
                speak(str(result))
            except Exception as exc:
                print("Screen analysis speech error:", exc)
        except Exception as exc:
            message = f"Screen analysis failed: {exc}"
            print(message)
            try:
                self.add_lucki_message(message)
                self.update_status("Ready")
            except Exception:
                pass

    # =========================================================
    # PHONE CALL EVENT
    # =========================================================

    def handle_phone_call(self, event):
        """Show a Phone Link call notification in the UI and announce it."""
        message = f"Phone call alert: {str(event).strip() or 'Incoming call'}"
        try:
            self.update_status("Incoming phone call")
        except Exception:
            pass
        try:
            self.add_lucki_message(message)
        except Exception:
            print("LUCKI:", message)
        try:
            speak(message)
        except Exception as exc:
            print("Phone call announcement error:", exc)

    # =========================================================
    # CHAT
    # =========================================================

    def add_user_message(
        self,
        text
    ):

        self.chat_output.append(
            f"<b>You:</b> {text}"
        )

    def add_lucki_message(
        self,
        text
    ):

        self.chat_output.append(
            f"<b>LUCKI:</b> {text}"
        )

    # =========================================================
    # EXTRA CHAT TOOLS (additive; keeps existing Home/Student/Notes/Tasks)
    # =========================================================

    def copy_chat(self):
        """Copy the visible conversation as plain text."""
        try:
            QApplication.clipboard().setText(self.chat_output.toPlainText())
            self.status_label.setText("Status: Chat copied to clipboard")
        except Exception as exc:
            QMessageBox.warning(self, "Copy failed", str(exc))

    def show_history(self):
        """Show saved conversation messages from Lucki's local memory file."""
        try:
            from memory import data
            dialog = QDialog(self)
            dialog.setWindowTitle("Lucki — Chat History")
            dialog.resize(620, 500)
            layout = QVBoxLayout(dialog)
            history = QTextEdit()
            history.setReadOnly(True)
            for item in data.get("conversation", []):
                role = str(item.get("role", "Unknown"))
                message = str(item.get("message", ""))
                history.append(f"<b>{role}:</b> {message}")
            layout.addWidget(history)
            row = QHBoxLayout()
            copy_btn = QPushButton("Copy History")
            copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(history.toPlainText()))
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            row.addWidget(copy_btn); row.addWidget(close_btn)
            layout.addLayout(row)
            dialog.exec()
        except Exception as exc:
            QMessageBox.warning(self, "History unavailable", str(exc))

    def toggle_compact_window(self):
        """Switch between a compact floating assistant and the normal window."""
        if getattr(self, "_compact_mode", False):
            self._compact_mode = False
            self.resize(1250, 780)
            self.showNormal()
            self.setWindowTitle("LUCKI AI — Narendra Soni")
        else:
            self._compact_mode = True
            self.resize(520, 360)
            self.setWindowTitle("LUCKI AI — Compact Mode")
            self.showNormal()
        self.raise_(); self.activateWindow()

    def attach_file(self):
        """Attach text/PDF context to the next prompt. Images are selected and noted, but vision needs a configured multimodal backend."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Attach a file", str(self.project_dir),
            "Supported files (*.txt *.md *.csv *.pdf *.png *.jpg *.jpeg *.webp);;All files (*.*)"
        )
        if not path:
            return
        p = Path(path)
        try:
            if p.suffix.lower() in {".txt", ".md", ".csv"}:
                content = p.read_text(encoding="utf-8", errors="replace")[:16000]
                self.chat_input.setText(f"Please analyze this attached file: {p.name}\n\n{content}\n\nMy question: ")
            elif p.suffix.lower() == ".pdf":
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(str(p))
                    content = "\n".join((page.extract_text() or "") for page in reader.pages)[:16000]
                    if not content.strip():
                        content = "No selectable text was found in this PDF; it may be scanned. File path: " + str(p)
                    self.chat_input.setText(f"Please analyze this PDF: {p.name}\n\n{content}\n\nMy question: ")
                except ImportError:
                    QMessageBox.information(self, "PDF support", "Install PDF text support with: python -m pip install pypdf")
            else:
                self.chat_input.setText(f"I attached image file {p.name} at {str(p)}. Please tell me how to enable image understanding for this file.")
                QMessageBox.information(self, "Image selected", "Image selected. This build does not yet send image bytes to Gemini; it can only pass text context to the model.")
            self.chat_input.setFocus()
        except Exception as exc:
            QMessageBox.warning(self, "Attachment failed", str(exc))

    # =========================================================
    # TEXT CHAT
    # =========================================================

    def send_text(self):

        text = (
            self.chat_input
            .text()
            .strip()
        )

        if not text:

            return

        self.chat_input.clear()

        self.add_user_message(
            text
        )

        thread = threading.Thread(
            target=self.process_text_command,
            args=(text,),
            daemon=True
        )

        thread.start()

    def process_text_command(
        self,
        text
    ):

        try:

            self.signals.status.emit(
                "Thinking..."
            )

            reply = process_command(
                text
            )

            if not reply:

                reply = (
                    "Sorry, mujhe samajh nahi aaya."
                )

            self.signals.reply.emit(
                reply
            )

            self.signals.status.emit(
                "Ready"
            )

        except Exception as e:

            self.signals.reply.emit(
                f"Error: {e}"
            )

            self.signals.status.emit(
                "Error"
            )

    # =========================================================
    # LISTENING BUTTON
    # =========================================================

    def toggle_listening(self):

        self.listening = (
            not self.listening
        )

        if self.listening:

            self.listen_button.setText(
                "🛑 Stop Listening"
            )

            self.signals.status.emit(
                "Waiting for wake word..."
            )

        else:

            self.listen_button.setText(
                "🎙 Start Listening"
            )

            self.signals.status.emit(
                "Voice listening stopped"
            )

    # =========================================================
    # WAKE WORD
    # =========================================================

    def toggle_wake_word(
        self,
        state
    ):

        self.wake_enabled = (
            state == Qt.Checked
        )

        if self.wake_enabled:

            self.signals.status.emit(
                "Wake word enabled"
            )

        else:

            self.signals.status.emit(
                "Wake word disabled"
            )

    # =========================================================
    # VOICE LOOP
    # =========================================================

    def _show_from_signal(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _hide_from_signal(self):
        self.hide()

    def start_voice_loop(self):
        thread = threading.Thread(target=self.voice_loop, daemon=True)
        thread.start()

    def _handle_voice_text(self, text):
        normalized = text.lower().strip()
        if normalized in {"exit lucki", "lucki exit", "close lucki", "lucki close"}:
            self.signals.hide_window.emit()
            self.signals.status.emit("Lucki is running in background")
            speak("Okay. Main background mein ready hoon. Bolo Hey Lucki jab chaho.")
            return "control"
        if normalized in {"stop listening", "stop listening lucki", "pause listening", "lucki pause"}:
            self.listening = False
            self.signals.status.emit("Voice listening paused")
            speak("Okay. Listening pause kar diya. Bolo Hey Lucki jab wapas baat karni ho.")
            return "control"
        self.signals.user.emit(text)
        self.signals.status.emit("Thinking...")
        reply = process_command(text) or "Sorry, mujhe samajh nahi aaya."
        self.signals.reply.emit(reply)
        self.signals.status.emit("Speaking...")
        speak(reply)
        return "answered"

    def voice_loop(self):
        conversation_active = False
        while self.running:
            try:
                if not self.listening:
                    threading.Event().wait(0.2)
                    continue
                if not conversation_active:
                    self.signals.status.emit("Waiting for wake word...")
                    detected = wait_for_wake_word(lambda: self.running and self.listening)
                    if not detected:
                        continue
                    conversation_active = True
                    self.signals.show_window.emit()
                    self.signals.status.emit("Wake detected — listening...")
                    if isinstance(detected, str):
                        # A phrase like 'Hey Lucki, open Chrome' already contains the command.
                        text = detected
                    else:
                        speak("Haan Narendra, bolo.")
                        text = ""
                else:
                    text = ""
                # If the wake phrase had no command, listen for the next sentence.
                if not text:
                    self.signals.status.emit("Listening...")
                    text = listen(timeout=8, phrase_time_limit=20)
                if not text:
                    # Keep the conversation session active through silence/timeouts.
                    # Only the Stop Listening control should end continuous listening.
                    if self.listening and self.running:
                        self.signals.status.emit("Still listening — speak anytime...")
                    continue
                result = self._handle_voice_text(text)
                if result == "control" and not self.listening:
                    conversation_active = False
                elif result == "control":
                    conversation_active = False
                else:
                    # stay in active conversation; next question can be spoken without wake word
                    conversation_active = True
            except Exception as e:
                self.signals.status.emit(f"Voice Error: {e}")
                threading.Event().wait(0.5)

    # =========================================================
    # STUDENT WORKSPACE
    # =========================================================

    def run_student_mode(
        self,
        mode
    ):

        text = (
            self.student_input
            .toPlainText()
            .strip()
        )

        if not text:

            return

        thread = threading.Thread(
            target=self.student_worker,
            args=(text, mode),
            daemon=True
        )

        thread.start()

    def student_worker(
        self,
        text,
        mode
    ):

        try:

            self.signals.status.emit(
                f"Student mode: {mode}"
            )

            result = ask_ai(
                text,
                mode
            )

            self.signals.student.emit(
                result
            )

            self.signals.status.emit(
                "Ready"
            )

        except Exception as e:

            self.signals.student.emit(
                f"Error: {e}"
            )

            self.signals.status.emit(
                "Error"
            )

    def show_student_result(
        self,
        text
    ):

        self.student_output.setPlainText(
            text
        )

    # =========================================================
    # NOTES
    # =========================================================

    def refresh_notes(self):

        self.notes_list.clear()

        try:

            data = notes()

            if isinstance(
                data,
                dict
            ):

                data = list(
                    data.values()
                )

            for note in data:

                self.notes_list.addItem(
                    str(note)
                )

        except Exception:

            pass

    def add_new_note(self):

        text, ok = QInputDialog.getMultiLineText(
            self,
            "Add Note",
            "Note:"
        )

        if ok and text.strip():

            add_note(
                text.strip()
            )

            self.refresh_notes()

    def delete_selected_note(self):

        row = (
            self.notes_list.currentRow()
        )

        if row < 0:

            return

        try:

            delete_note(
                row
            )

        except Exception:

            pass

        self.refresh_notes()

    # =========================================================
    # TASKS
    # =========================================================

    def refresh_tasks(self):

        self.tasks_list.clear()

        try:

            data = tasks()

            if isinstance(
                data,
                dict
            ):

                data = list(
                    data.values()
                )

            for task in data:

                if isinstance(
                    task,
                    dict
                ):

                    text = task.get(
                        "text",
                        str(task)
                    )

                    done = task.get(
                        "done",
                        False
                    )

                    prefix = (
                        "✅ "
                        if done
                        else "⬜ "
                    )

                    self.tasks_list.addItem(
                        prefix + text
                    )

                else:

                    self.tasks_list.addItem(
                        str(task)
                    )

        except Exception:

            pass

    def add_new_task(self):

        text, ok = QInputDialog.getText(
            self,
            "Add Task",
            "Task:"
        )

        if ok and text.strip():

            add_task(
                text.strip()
            )

            self.refresh_tasks()

    def toggle_selected_task(self):

        row = (
            self.tasks_list.currentRow()
        )

        if row < 0:

            return

        try:

            toggle_task(
                row
            )

        except Exception:

            pass

        self.refresh_tasks()

    def delete_selected_task(self):

        row = (
            self.tasks_list.currentRow()
        )

        if row < 0:

            return

        try:

            delete_task(
                row
            )

        except Exception:

            pass

        self.refresh_tasks()

    # =========================================================
    # USER NAME
    # =========================================================

    def change_user_name(self):

        name, ok = QInputDialog.getText(
            self,
            "Change User Name",
            "New name:",
            text=self.user_name
        )

        if ok and name.strip():

            self.user_name = (
                name.strip()
            )

            set_user_name(
                self.user_name
            )

            self.user_status.setText(
                f"Owner: {self.user_name}"
            )

            self.chat_output.append(
                f"<b>LUCKI:</b> Okay, main tumhe "
                f"{self.user_name} bulaunga."
            )

    # =========================================================
    # CLEAR CHAT
    # =========================================================

    def clear_chat(self):

        self.chat_output.clear()

    # =========================================================
    # CLOSE
    # =========================================================

    def closeEvent(self, event):
        # Fully stop Lucki when the window is closed, so files can be replaced/deleted.
        self.running = False
        self.listening = False
        try:
            if hasattr(self, "phone_monitor") and self.phone_monitor:
                self.phone_monitor.stop()
        except Exception as exc:
            print("Phone monitor shutdown warning:", exc)
        event.accept()


# =============================================================
# APPLICATION START
# =============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    project_dir = Path(__file__).resolve().parent
    icon_path = project_dir / "assets" / "lucki_icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Automatically register Lucki to launch with Windows for this Windows user.
    try:
        enable_startup()
    except Exception as exc:
        print("Windows startup registration skipped:", exc)

    window = LuckiAI()
    background_start = "--background" in sys.argv
    if background_start:
        window.hide()
        QTimer.singleShot(1800, lambda: speak("Namaste Narendra. Lucki background mein ready hai. Boliye Lucki."))
    else:
        window.show()
        window.raise_()
        window.activateWindow()
        QTimer.singleShot(650, lambda: speak(f"Namaste Narendra. Main Lucki hoon. Aapka assistant ready hai."))
    sys.exit(app.exec())
