import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox, 
                             QHeaderView, QDialog, QFormLayout, QInputDialog, QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox, QListWidget, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from models import Client, Inventaire, Produit, session, Commande, StatutCommande
from sqlalchemy import desc
import qtawesome as qta

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


class AjouterProduitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un produit")
        self.setModal(True)
        self.setStyleSheet(MODAL_STYLE)

        layout = QFormLayout(self)

        self.nom_input = QLineEdit()
        self.description_input = QTextEdit()
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setMinimum(0)
        self.prix_input.setMaximum(1000000)
        self.prix_input.setDecimals(2)
        self.categorie_input = QComboBox()
        self.categorie_input.addItems(["Œufs", "Poulets", "Autres"])

        self.ingredients_list = QListWidget()
        self.ingredients_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.charger_ingredients()

        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Prix de vente:", self.prix_input)
        layout.addRow("Catégorie:", self.categorie_input)
        layout.addRow("Ingrédients:", self.ingredients_list)

        buttons = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Annuler")
        self.ok_button.setStyleSheet(BUTTON_STYLE_BLUE)
        self.cancel_button.setStyleSheet(BUTTON_STYLE_RED)
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)

        layout.addRow(buttons)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def charger_ingredients(self):
        ingredients = session.query(Inventaire).all()
        for ingredient in ingredients:
            self.ingredients_list.addItem(ingredient.nom)



import qtawesome as qta

class ProduitsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Bouton pour ajouter un produit
        self.ajouter_button = QPushButton("Ajouter un produit")
        self.ajouter_button.setIcon(qta.icon('fa5s.plus'))
        self.ajouter_button.clicked.connect(self.ouvrir_formulaire_produit)
        self.ajouter_button.setStyleSheet(BUTTON_STYLE_BLUE)
        layout.addWidget(self.ajouter_button)

        # Table des produits
        self.table_produits = QTableWidget()
        self.table_produits.setColumnCount(5)
        self.table_produits.setHorizontalHeaderLabels(["ID", "Nom", "Prix", "Description", "Date de création"])
        self.table_produits.verticalHeader().setVisible(False)
        self.table_produits.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_produits.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table_produits)

        # Boutons de modification et suppression
        button_layout = QHBoxLayout()
        self.modifier_button = QPushButton("Modifier")
        self.modifier_button.setIcon(qta.icon('fa5s.edit'))
        self.modifier_button.clicked.connect(self.modifier_produit)
        self.modifier_button.setStyleSheet(BUTTON_STYLE_YELLOW)
        button_layout.addWidget(self.modifier_button)

        self.supprimer_button = QPushButton("Supprimer")
        self.supprimer_button.setIcon(qta.icon('fa5s.trash'))
        self.supprimer_button.clicked.connect(self.supprimer_produit)
        self.supprimer_button.setStyleSheet(BUTTON_STYLE_RED)
        button_layout.addWidget(self.supprimer_button)

        layout.addLayout(button_layout)

        self.charger_produits()

    def charger_produits(self):
        self.table_produits.setRowCount(0)
        produits = session.query(Produit).order_by(desc(Produit.date_creation)).all()
        for produit in produits:
            self.ajouter_produit_a_table(produit)

    def ajouter_produit_a_table(self, produit):
        row_position = self.table_produits.rowCount()
        self.table_produits.insertRow(row_position)
        self.table_produits.setItem(row_position, 0, QTableWidgetItem(str(produit.id)))
        self.table_produits.setItem(row_position, 1, QTableWidgetItem(produit.nom))
        self.table_produits.setItem(row_position, 2, QTableWidgetItem(f"{produit.prix:.2f}"))
        self.table_produits.setItem(row_position, 3, QTableWidgetItem(produit.description))
        self.table_produits.setItem(row_position, 4, QTableWidgetItem(produit.date_creation.strftime("%Y-%m-%d")))

    def ouvrir_formulaire_produit(self):
        dialog = AjouterProduitDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nom, prix, description, date_creation = dialog.get_data()
            self.ajouter_produit(nom, prix, description, date_creation)

    def ajouter_produit(self, nom, prix, description, date_creation):
        nouveau_produit = Produit(nom=nom, prix=prix, description=description, date_creation=date_creation)
        session.add(nouveau_produit)
        session.commit()
        self.ajouter_produit_a_table(nouveau_produit)

    def modifier_produit(self):
        selected_row = self.table_produits.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit à modifier.")
            return

        produit_id = int(self.table_produits.item(selected_row, 0).text())
        produit = session.query(Produit).get(produit_id)

        dialog = AjouterProduitDialog(self, produit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nom, prix, description, date_creation = dialog.get_data()
            produit.nom = nom
            produit.prix = prix
            produit.description = description
            produit.date_creation = date_creation
            session.commit()
            self.charger_produits()

    def supprimer_produit(self):
        selected_row = self.table_produits.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit à supprimer.")
            return

        produit_id = int(self.table_produits.item(selected_row, 0).text())
        produit = session.query(Produit).get(produit_id)

        reply = QMessageBox.question(self, "Confirmation", "Êtes-vous sûr de vouloir supprimer ce produit ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            session.delete(produit)
            session.commit()
            self.table_produits.removeRow(selected_row)

class AjouterProduitDialog(QDialog):
    def __init__(self, parent=None, produit=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un produit" if produit is None else "Modifier un produit")
        self.setModal(True)
        self.setStyleSheet(MODAL_STYLE)

        layout = QFormLayout(self)

        self.nom_input = QLineEdit()
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setRange(0, 1000000)
        self.prix_input.setDecimals(2)
        self.prix_input.setStyleSheet(SPINBOX_STYLE)
        self.description_input = QTextEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Prix:", self.prix_input)
        layout.addRow("Description:", self.description_input)
        layout.addRow("Date de création:", self.date_input)

        buttons = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet(BUTTON_STYLE_BLUE)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setStyleSheet(BUTTON_STYLE_RED)
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)

        layout.addRow(buttons)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        if produit:
            self.nom_input.setText(produit.nom)
            self.prix_input.setValue(produit.prix)
            self.description_input.setText(produit.description)
            self.date_input.setDate(produit.date_creation.date())

    def get_data(self):
        return (
            self.nom_input.text(),
            self.prix_input.value(),
            self.description_input.toPlainText(),
            self.date_input.date().toPyDate()
        )

