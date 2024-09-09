from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QColor
from sqlalchemy import func
from models import Commande, StatutCommande, Depense, session
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import qtawesome as qta

class MontantCard(QFrame):
    def __init__(self, title, icon, color):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
                padding: 20px;
                border: 1px solid #ddd;
            }}
            QLabel {{
                color: white;
            }}
        """)
        layout = QVBoxLayout()
        self.setLayout(layout)

        title_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(32, 32))
        title_layout.addWidget(icon_label)
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.montant_label = QLabel()
        self.montant_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.montant_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))

        layout.addLayout(title_layout)
        layout.addWidget(self.montant_label)

    def set_montant(self, montant):
        self.montant_label.setText(f"{montant:.2f} N-UM")

class PieChart(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                border: 1px solid #ddd;
            }
        """)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.no_data_label = QLabel("Pas de données à afficher")
        self.no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_data_label.setStyleSheet("font-size: 16px; color: #888;")
        self.no_data_label.hide()
        layout.addWidget(self.no_data_label)

    def update_chart(self, commandes, depenses):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if commandes == 0 and depenses == 0:
            self.canvas.hide()
            self.no_data_label.show()
        else:
            self.canvas.show()
            self.no_data_label.hide()
            colors = ['#4CAF50', '#FFC107']  # Vert pour les commandes, Jaune pour les dépenses
            data = [commandes, depenses]
            labels = ['Commandes', 'Dépenses']
            
            # Filtrer les valeurs nulles
            non_zero = [(label, value) for label, value in zip(labels, data) if value > 0]
            if non_zero:
                labels, data = zip(*non_zero)
                ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            else:
                ax.text(0.5, 0.5, "Pas de données à afficher", ha='center', va='center')
            
            ax.axis('equal')
        self.canvas.draw()

class AccueilTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
        """)
        layout = QVBoxLayout()
        self.setLayout(layout)

        welcome_label = QLabel("Bienvenue dans l'application de gestion du Poulailler")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #2C3E50; margin: 20px 0;")
        layout.addWidget(welcome_label)

        cards_layout = QHBoxLayout()
        self.commandes_card = MontantCard("Commandes payées", qta.icon('fa5s.shopping-cart', color='white'), "#4CAF50")
        self.depenses_card = MontantCard("Dépenses", qta.icon('fa5s.money-bill-wave', color='white'), "#FFC107")
        self.benefice_card = MontantCard("Bénéfice", qta.icon('fa5s.chart-line', color='white'), "#2196F3")
        cards_layout.addWidget(self.commandes_card)
        cards_layout.addWidget(self.depenses_card)
        cards_layout.addWidget(self.benefice_card)
        layout.addLayout(cards_layout)

        self.pie_chart = PieChart()
        layout.addWidget(self.pie_chart)

        layout.addStretch()

        self.refresh()

    def refresh(self):
        total_commandes = session.query(func.sum(Commande.prix )).filter(
            Commande.statut == StatutCommande.PAYEE
        ).scalar() or 0

        total_depenses = session.query(func.sum(Depense.montant)).scalar() or 0

        benefice = total_commandes - total_depenses

        self.commandes_card.set_montant(total_commandes)
        self.depenses_card.set_montant(total_depenses)
        self.benefice_card.set_montant(benefice)

        self.pie_chart.update_chart(total_commandes, total_depenses)
