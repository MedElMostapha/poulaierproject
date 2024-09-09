from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTranslator, QCoreApplication
from PyQt6.QtGui import QFont

class SplashScreen(QWidget):
    language_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Bienvenue / Welcome / مرحبا"))
        self.setFixedSize(600, 300)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.welcome_label = QLabel(self.tr("Bienvenue dans l'application de Gestion du Poulailler"))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(self.welcome_label)  # Adding first label

        self.developper = QLabel(self.tr("Développé par Mohamed Lemine El Mostapha"))
        self.developper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.developper.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(self.developper)  # Adding second label

        # Now both labels are in the same layout.



        

        self.language_combo = QComboBox()
        self.language_combo.addItem("Français", "fr_FR")
        self.language_combo.addItem("العربية", "ar_MA")
        layout.addWidget(self.language_combo)

        self.start_button = QPushButton(self.tr("Démarrer l'application"))
        self.start_button.clicked.connect(self.start_app)
        layout.addWidget(self.start_button)

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #333;
            }
            QComboBox, QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def start_app(self):
        selected_language = self.language_combo.currentData()
        self.language_selected.emit(selected_language)
        self.close()

    def changeEvent(self, event):
        if event.type() == event.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Bienvenue / Welcome / مرحبا"))
        self.welcome_label.setText(self.tr("Bienvenue dans l'application de Gestion du Poulailler"))
        self.start_button.setText(self.tr("Démarrer l'application"))