import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox, 
                             QHeaderView, QDialog, QFormLayout, QInputDialog, QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox, QListWidget, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from models import Client, Inventaire, Produit, session, Commande, StatutCommande

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


class AjouterClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un client")
        self.setModal(True)
        self.setStyleSheet(MODAL_STYLE)

        layout = QFormLayout(self)

        self.nom_input = QLineEdit()
        self.telephone_input = QLineEdit()

        layout.addRow("Nom:", self.nom_input)
        layout.addRow("Téléphone:", self.telephone_input)

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




class ClientsTab(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Bouton pour ouvrir le formulaire d'ajout de client
        self.ajouter_button = QPushButton("Ajouter un client")
        self.ajouter_button.setStyleSheet(BUTTON_STYLE_BLUE)
        self.ajouter_button.clicked.connect(self.ouvrir_formulaire_client)
        layout.addWidget(self.ajouter_button)

        # Table des clients
        self.table_clients = QTableWidget()
        self.table_clients.setStyleSheet(TABLE_STYLE)
        self.table_clients.setColumnCount(3)  # Ajout d'une colonne pour l'ID
        self.table_clients.setHorizontalHeaderLabels(["ID", "Nom", "Téléphone"])
        self.table_clients.verticalHeader().setVisible(False)
        self.table_clients.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_clients.setAlternatingRowColors(True)
        self.table_clients.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_clients.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table_clients)

        # Boutons de modification et suppression
        button_layout = QHBoxLayout()
        self.modifier_button = QPushButton("Modifier le client sélectionné")
        self.modifier_button.setStyleSheet(BUTTON_STYLE_YELLOW)
        self.modifier_button.clicked.connect(self.modifier_client)
        button_layout.addWidget(self.modifier_button)

        self.supprimer_button = QPushButton("Supprimer le client sélectionné")
        self.supprimer_button.setStyleSheet(BUTTON_STYLE_RED)
        self.supprimer_button.clicked.connect(self.supprimer_client)
        button_layout.addWidget(self.supprimer_button)

        layout.addLayout(button_layout)

        self.charger_clients()

    def charger_clients(self):
        self.table_clients.setRowCount(0)
        clients = session.query(Client).all()
        for client in clients:
            self.ajouter_client_a_table(client)

    def ouvrir_formulaire_client(self):
        dialog = AjouterClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nom = dialog.nom_input.text().strip()
            telephone = dialog.telephone_input.text().strip()
            self.ajouter_client(nom, telephone)

    def ajouter_client(self, nom, telephone):
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom du client est obligatoire.")
            return

        nouveau_client = Client(nom=nom, telephone=telephone)
        try:
            session.add(nouveau_client)
            session.commit()
            self.ajouter_client_a_table(nouveau_client)
            QMessageBox.information(self, "Succès", "Le client a été ajouté avec succès.")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter le client : {str(e)}")

    def ajouter_client_a_table(self, client):
        row_position = self.table_clients.rowCount()
        self.table_clients.insertRow(row_position)
        self.table_clients.setItem(row_position, 0, QTableWidgetItem(str(client.id)))
        self.table_clients.setItem(row_position, 1, QTableWidgetItem(client.nom))
        self.table_clients.setItem(row_position, 2, QTableWidgetItem(client.telephone))

    def modifier_client(self):
        selected_row = self.table_clients.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un client à modifier.")
            return

        client_id = int(self.table_clients.item(selected_row, 0).text())
        client = session.query(Client).get(client_id)

        if client:
            dialog = AjouterClientDialog(self)
            dialog.nom_input.setText(client.nom)
            dialog.telephone_input.setText(client.telephone)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                nouveau_nom = dialog.nom_input.text().strip()
                nouveau_telephone = dialog.telephone_input.text().strip()

                if nouveau_nom:
                    client.nom = nouveau_nom
                    client.telephone = nouveau_telephone
                    session.commit()
                    self.table_clients.setItem(selected_row, 1, QTableWidgetItem(client.nom))
                    self.table_clients.setItem(selected_row, 2, QTableWidgetItem(client.telephone))
                    QMessageBox.information(self, "Succès", "Le client a été modifié avec succès.")
                else:
                    QMessageBox.warning(self, "Erreur", "Le nom du client est obligatoire.")

    def supprimer_client(self):
        selected_row = self.table_clients.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un client à supprimer.")
            return

        client_id = int(self.table_clients.item(selected_row, 0).text())
        client = session.query(Client).get(client_id)

        if client:
            reply = QMessageBox.question(self, "Confirmation", f"Êtes-vous sûr de vouloir supprimer le client {client.nom} ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                session.delete(client)
                session.commit()
                self.table_clients.removeRow(selected_row)
                QMessageBox.information(self, "Succès", "Le client a été supprimé avec succès.")
