import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox, 
                             QHeaderView, QDialog, QFormLayout, QInputDialog, QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox, QListWidget, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from models import Client, Inventaire, Produit, session, Commande, StatutCommande,StatusInventaire
from sqlalchemy import desc

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


class AjouterArticleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un article")
        self.setModal(True)
        self.setStyleSheet(MODAL_STYLE)

        layout = QFormLayout(self)

        self.nom_input = QLineEdit()
        self.quantite_input = QSpinBox()
        self.quantite_input.setMinimum(0)
        self.quantite_input.setMaximum(1000000)
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setMinimum(0)
        self.prix_input.setMaximum(1000000)
        self.prix_input.setDecimals(2)

        self.produits_list = QListWidget()
        self.produits_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.charger_produits()

        self.status_combo = QComboBox()
        self.status_combo.addItems([status.value for status in StatusInventaire])

        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Quantité:", self.quantite_input)
        layout.addRow("Prix unitaire:", self.prix_input)
        layout.addRow("Produits associés:", self.produits_list)
        layout.addRow("Status:", self.status_combo)

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

    def charger_produits(self):
        produits = session.query(Produit).all()
        for produit in produits:
            self.produits_list.addItem(produit.nom)

    def get_data(self):
        nom = self.nom_input.text()
        quantite = self.quantite_input.value()
        prix_unitaire = self.prix_input.value()
        status = StatusInventaire(self.status_combo.currentText())
        produits_selectionnes = [item.text() for item in self.produits_list.selectedItems()]
        return nom, quantite, prix_unitaire, status, produits_selectionnes



class InventaireTab(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Bouton pour ouvrir le formulaire d'ajout d'article
        self.ajouter_button = QPushButton("Ajouter un article")
        self.ajouter_button.setStyleSheet(BUTTON_STYLE_BLUE)
        self.ajouter_button.clicked.connect(self.ouvrir_formulaire_article)
        layout.addWidget(self.ajouter_button)

        # Table de l'inventaire
        self.table_inventaire = QTableWidget()
        self.table_inventaire.setStyleSheet(TABLE_STYLE)
        self.table_inventaire.setColumnCount(6)  # Augmenter le nombre de colonnes
        self.table_inventaire.setHorizontalHeaderLabels(["ID", "Nom", "Quantité", "Prix unitaire", "Status", "Produits associés"])
        self.table_inventaire.verticalHeader().setVisible(False)
        self.table_inventaire.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_inventaire.setAlternatingRowColors(True)
        self.table_inventaire.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_inventaire.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table_inventaire)

        # Boutons de modification et suppression
        button_layout = QHBoxLayout()
        self.modifier_button = QPushButton("Modifier l'article sélectionné")
        self.modifier_button.setStyleSheet(BUTTON_STYLE_YELLOW)
        self.modifier_button.clicked.connect(self.modifier_article)
        button_layout.addWidget(self.modifier_button)

        self.supprimer_button = QPushButton("Supprimer l'article sélectionné")
        self.supprimer_button.setStyleSheet(BUTTON_STYLE_RED)
        self.supprimer_button.clicked.connect(self.supprimer_article)
        button_layout.addWidget(self.supprimer_button)

        layout.addLayout(button_layout)

        self.charger_inventaire()

    def rafraichir_table_inventaire(self):
        self.table_inventaire.setRowCount(0)  # Efface toutes les lignes existantes
        inventaire = session.query(Inventaire).all()
        for article in inventaire:
            self.ajouter_article_a_table(article)

    def charger_inventaire(self):
        self.table_inventaire.setRowCount(0)
        articles = session.query(Inventaire).order_by(desc(Inventaire.id)).all()
        for article in articles:
            self.ajouter_article_a_table(article)

    def ajouter_article_a_table(self, article):
        row_position = self.table_inventaire.rowCount()
        self.table_inventaire.insertRow(row_position)
        self.table_inventaire.setItem(row_position, 0, QTableWidgetItem(str(article.id)))
        self.table_inventaire.setItem(row_position, 1, QTableWidgetItem(article.nom))
        self.table_inventaire.setItem(row_position, 2, QTableWidgetItem(str(article.quantite)))
        self.table_inventaire.setItem(row_position, 3, QTableWidgetItem(f"{article.prix_unitaire:.2f}"))
        self.table_inventaire.setItem(row_position, 4, QTableWidgetItem(article.status.value))
        self.table_inventaire.setItem(row_position, 5, QTableWidgetItem(", ".join([p.nom for p in article.produits])))

    def ouvrir_formulaire_article(self):
        dialog = AjouterArticleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nom, quantite, prix_unitaire, status, produits_selectionnes = dialog.get_data()
            self.ajouter_article(nom, quantite, prix_unitaire, status, produits_selectionnes)

    def ajouter_article(self, nom, quantite, prix_unitaire, status, produits_noms):
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de l'article est obligatoire.")
            return

        nouvel_article = Inventaire(
            nom=nom, 
            quantite=quantite, 
            prix_unitaire=prix_unitaire,
            status=StatusInventaire(status)
        )
        
        for produit_nom in produits_noms:
            produit = session.query(Produit).filter_by(nom=produit_nom).first()
            if produit:
                nouvel_article.produits.append(produit)

        try:
            session.add(nouvel_article)
            session.commit()
            self.ajouter_article_a_table(nouvel_article)
            QMessageBox.information(self, "Succès", "L'article a été ajouté avec succès.")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter l'article : {str(e)}")

    def modifier_article(self):
        selected_row = self.table_inventaire.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un article à modifier.")
            return

        article_id = int(self.table_inventaire.item(selected_row, 0).text())
        article = session.query(Inventaire).get(article_id)

        if article:
            dialog = AjouterArticleDialog(self)
            dialog.nom_input.setText(article.nom)
            dialog.quantite_input.setValue(article.quantite)
            dialog.prix_input.setValue(article.prix_unitaire)
            for i in range(dialog.produits_list.count()):
                item = dialog.produits_list.item(i)
                if item.text() in [p.nom for p in article.produits]:
                    item.setSelected(True)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                article.nom = dialog.nom_input.text().strip()
                article.quantite = dialog.quantite_input.value()
                article.prix_unitaire = dialog.prix_input.value()
                article.status = StatusInventaire(dialog.status_combo.currentText())
                
                try:
                    session.commit()
                    self.charger_inventaire()
                    QMessageBox.information(self, "Succès", "L'article a été modifié avec succès.")
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Erreur", f"Impossible de modifier l'article : {str(e)}")

    def supprimer_article(self):
        selected_row = self.table_inventaire.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un article à supprimer.")
            return

        article_id = int(self.table_inventaire.item(selected_row, 0).text())
        article = session.query(Inventaire).get(article_id)

        if article:
            reply = QMessageBox.question(self, "Confirmation", f"Êtes-vous sûr de vouloir supprimer l'article {article.nom} ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    session.delete(article)
                    session.commit()
                    self.table_inventaire.removeRow(selected_row)
                    QMessageBox.information(self, "Succès", "L'article a été supprimé avec succès.")
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Erreur", f"Impossible de supprimer l'article : {str(e)}")
