from PyQt6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar, QTabWidget, 
                             QWidget, QVBoxLayout, QHBoxLayout)
from PyQt6.QtGui import QColor, QIcon, QAction
from PyQt6.QtCore import Qt, QDate, QTranslator, QLocale, QEvent
from splash_screen import SplashScreen
import qtawesome as qta
from models import Client, Inventaire, Produit, session, Commande, StatutCommande
from Clients.client import ClientsTab
from Inventaire.inventaire import InventaireTab
from Produit.produit import ProduitsTab
from Commande.commande import CommandesTab
from Accueil.accueil import AccueilTab
from Depense.depense import DepenseTab
from Perte.perte import PerteTab
import sys  # Ajoutez cette ligne

# Définition des styles
BUTTON_STYLE_BLUE = """
QPushButton {
    background-color: #007bff;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    margin: 4px 2px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #0056b3;
}
"""

BUTTON_STYLE_YELLOW = """
QPushButton {
    background-color: #ffc107;
    border: none;
    color: black;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    margin: 4px 2px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #d39e00;
}
"""

BUTTON_STYLE_RED = """
QPushButton {
    background-color: #dc3545;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    margin: 4px 2px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #bd2130;
}
"""

TABLE_STYLE = """
QTableWidget {
    background-color: #f2f2f2;
     color: balck;
    alternate-background-color: #e6e6e6;
    selection-background-color: #a6a6a6;
}
QHeaderView::section {
    background-color: #4CAF50;
    color: white;
    padding: 5px;
    border: 1px solid #ddd;
}
"""

MODAL_STYLE = """
QDialog {
    background-color: #f0f0f0;
}
QLineEdit {
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 3px;
}
"""

SPINBOX_STYLE = """
QSpinBox, QDoubleSpinBox {
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 3px;
}
"""




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Gestion du Poulailler"))
        self.setGeometry(100, 100, 1000, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Création des onglets avec des icônes
        self.accueil_tab = AccueilTab()
        self.commandes_tab = CommandesTab()
        self.clients_tab = ClientsTab()
        self.inventaire_tab = InventaireTab()
        self.produits_tab = ProduitsTab()
        self.depenses_tab = DepenseTab()
        self.perte_tab = PerteTab()

        self.tab_widget.addTab(self.accueil_tab, qta.icon('fa5s.home'), self.tr("Accueil"))
        self.tab_widget.addTab(self.commandes_tab, qta.icon('fa5s.shopping-cart'), self.tr("Commandes"))
        self.tab_widget.addTab(self.inventaire_tab, qta.icon('fa5s.warehouse'), self.tr("Inventaire"))
        self.tab_widget.addTab(self.produits_tab, qta.icon('fa5s.box'), self.tr("Produits"))
        self.tab_widget.addTab(self.clients_tab, qta.icon('fa5s.users'), self.tr("Clients"))
        self.tab_widget.addTab(self.depenses_tab, qta.icon('fa5s.money-bill-wave'), self.tr("Dépenses"))
        self.tab_widget.addTab(self.perte_tab, qta.icon('fa5s.trash-alt'), self.tr("Pertes"))

        # Style pour les onglets
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                top: -1px;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ddd;
                padding: 5px;
                min-width: 100px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #4CAF50;
                color: white;
            }
            QTabBar::tab:selected {
                border-color: #4CAF50;
                border-bottom-color: #4CAF50;
            }
        """)

        # Connecter les signaux
        self.commandes_tab.inventaire_modifie.connect(self.inventaire_tab.rafraichir_table_inventaire)
        self.commandes_tab.inventaire_modifie.connect(self.accueil_tab.refresh)

        # Rafraîchir l'onglet d'accueil lorsqu'on y accède
        self.tab_widget.currentChanged.connect(self.on_tab_change)

        # Connecter le signal de rafraîchissement de l'inventaire
        self.perte_tab.inventaire_modifie.connect(self.inventaire_tab.rafraichir_table_inventaire)

        # Créer un menu pour changer de langue
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()
        language_menu = menubar.addMenu(self.tr("Langue"))

        french_action = QAction("Français", self)
        french_action.triggered.connect(lambda: self.change_language("fr_FR"))
        language_menu.addAction(french_action)

        arabic_action = QAction("العربية", self)
        arabic_action.triggered.connect(lambda: self.change_language("ar_MA"))
        language_menu.addAction(arabic_action)

    def change_language(self, locale):
        translator = QTranslator()
        if translator.load(f"translations/{locale}"):
            QApplication.instance().installTranslator(translator)
            self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Gestion du Poulailler"))
        # Mettez à jour tous les autres textes traduits ici
        # Par exemple :
        # self.tab_widget.setTabText(0, self.tr("Accueil"))
        # self.tab_widget.setTabText(1, self.tr("Inventaire"))
        # etc.

    def on_tab_change(self, index):
        if index == 0:  # Index de l'onglet d'accueil
            self.accueil_tab.refresh()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

def main():
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    window = MainWindow()

    def on_language_selected(locale):
        window.change_language(locale)
        window.show()
        splash.close()

    splash.language_selected.connect(on_language_selected)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
