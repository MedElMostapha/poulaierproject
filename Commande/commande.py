import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox, 
                             QHeaderView, QDialog, QFormLayout, QInputDialog, QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox, QListWidget, QDateEdit)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor
from models import Client, Inventaire, Produit, session, Commande, StatutCommande,inventaire_produit
from sqlalchemy import desc, func

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

class StatusBadge(QLabel):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.setStatus(status)

    def setStatus(self, status):
        self.setText(status.value)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self.getStyleForStatus(status))

    def getStyleForStatus(self, status):
        base_style = """
            border-radius: 10px;
            font-weight: bold;
            color: white;
        """
        if status == StatutCommande.EN_ATTENTE:
            return base_style + "background-color: #FFA500;"  # Orange
        elif status == StatutCommande.PAYEE:
            return base_style + "background-color: #4CAF50;"  # Vert
        elif status == StatutCommande.ANNULEE:
            return base_style + "background-color: #F44336;"  # Rouge
        else:
            return base_style + "background-color: #9E9E9E;"  # Gris

class AjouterCommandeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une commande")
        self.setModal(True)
        self.setStyleSheet(MODAL_STYLE)

        layout = QFormLayout(self)

        self.date_commande = QDateEdit()
        self.date_commande.setDate(QDate.currentDate())
        self.client_combo = QComboBox()
        self.charger_clients()
        self.produits_list = QListWidget()
        self.produits_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.charger_produits()
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setMinimum(0)
        self.prix_input.setMaximum(1000000)
        self.prix_input.setDecimals(2)
        self.quantite_input = QSpinBox()
        self.quantite_input.setMinimum(1)
        self.quantite_input.setMaximum(1000)
        self.statut_combo = QComboBox()
        self.statut_combo.addItems([statut.value for statut in StatutCommande])

        layout.addRow("Date de commande:", self.date_commande)
        layout.addRow("Client:", self.client_combo)
        layout.addRow("Produits:", self.produits_list)
        layout.addRow("Prix:", self.prix_input)
        layout.addRow("Quantité:", self.quantite_input)
        layout.addRow("Statut:", self.statut_combo)

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

    def charger_clients(self):
        clients = session.query(Client).all()
        for client in clients:
            self.client_combo.addItem(client.nom, client.id)

    def charger_produits(self):
        produits = session.query(Produit).all()
        for produit in produits:
            self.produits_list.addItem(produit.nom)

class CommandesTab(QWidget):
    inventaire_modifie = pyqtSignal()  # Nouveau signal

    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Bouton pour ouvrir le formulaire d'ajout de commande
        self.ajouter_button = QPushButton("Ajouter une commande")
        self.ajouter_button.setStyleSheet(BUTTON_STYLE_BLUE)
        self.ajouter_button.clicked.connect(self.ouvrir_formulaire_commande)
        layout.addWidget(self.ajouter_button)

        # Table des commandes
        self.table_commandes = QTableWidget()
        self.table_commandes.setStyleSheet(TABLE_STYLE)
        self.table_commandes.setColumnCount(7)  # Augmenter le nombre de colonnes
        self.table_commandes.setHorizontalHeaderLabels(["ID", "Date", "Client", "Produits", "Prix", "Quantité", "Statut"])
        self.table_commandes.verticalHeader().setVisible(False)
        self.table_commandes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_commandes.setAlternatingRowColors(True)
        self.table_commandes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_commandes.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table_commandes)

        # Boutons de modification et suppression
        button_layout = QHBoxLayout()
        self.modifier_button = QPushButton("Modifier la commande sélectionnée")
        self.modifier_button.setStyleSheet(BUTTON_STYLE_YELLOW)
        self.modifier_button.clicked.connect(self.modifier_commande)
        button_layout.addWidget(self.modifier_button)

        self.supprimer_button = QPushButton("Supprimer la commande sélectionnée")
        self.supprimer_button.setStyleSheet(BUTTON_STYLE_RED)
        self.supprimer_button.clicked.connect(self.supprimer_commande)
        button_layout.addWidget(self.supprimer_button)

        layout.addLayout(button_layout)

        self.charger_commandes()

    def charger_commandes(self):
        self.table_commandes.setRowCount(0)
        commandes = session.query(Commande).order_by(desc(Commande.date_commande)).all()
        for commande in commandes:
            self.ajouter_commande_a_table(commande)

    def ajouter_commande_a_table(self, commande):
        row_position = self.table_commandes.rowCount()
        self.table_commandes.insertRow(row_position)
        self.table_commandes.setItem(row_position, 0, QTableWidgetItem(str(commande.id)))
        self.table_commandes.setItem(row_position, 1, QTableWidgetItem(commande.date_commande.strftime("%Y-%m-%d")))
        self.table_commandes.setItem(row_position, 2, QTableWidgetItem(commande.client.nom))
        self.table_commandes.setItem(row_position, 3, QTableWidgetItem(", ".join([p.nom for p in commande.produits])))
        self.table_commandes.setItem(row_position, 4, QTableWidgetItem(f"{commande.prix:.2f} N-UM"))  # Nouvelle colonne Prix
        self.table_commandes.setItem(row_position, 5, QTableWidgetItem(str(commande.quantite)))
        
        # Créer et ajouter le badge de statut
        status_badge = StatusBadge(commande.statut)
        self.table_commandes.setCellWidget(row_position, 6, status_badge)

    def ouvrir_formulaire_commande(self):
        dialog = AjouterCommandeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            date_commande = dialog.date_commande.date().toPyDate()
            client_id = dialog.client_combo.currentData()
            produits_selectionnes = [item.text() for item in dialog.produits_list.selectedItems()]
            prix = dialog.prix_input.value()  # Nouveau champ
            quantite = dialog.quantite_input.value()
            statut = StatutCommande(dialog.statut_combo.currentText())
            self.ajouter_commande(date_commande, client_id, produits_selectionnes, prix, quantite, statut)

    def ajouter_commande(self, date_commande, client_id, produits_noms, prix, quantite, statut):
        client = session.query(Client).get(client_id)
        if not client:
            QMessageBox.warning(self, "Erreur", "Client non trouvé.")
            return

        nouvelle_commande = Commande(date_commande=date_commande, client=client, prix=prix, quantite=quantite, statut=statut)
        
        for produit_nom in produits_noms:
            produit = session.query(Produit).filter_by(nom=produit_nom).first()
            if produit:
                nouvelle_commande.produits.append(produit)

        try:
            session.add(nouvelle_commande)
            session.commit()
            self.ajouter_commande_a_table(nouvelle_commande)
            QMessageBox.information(self, "Succès", "La commande a été ajoutée avec succès.")
            if statut == StatutCommande.PAYEE:
                self.retirer_de_inventaire(nouvelle_commande)
            self.inventaire_modifie.emit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Impossible d'ajouter la commande : {str(e)}")

    def modifier_commande(self):
        selected_row = self.table_commandes.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une commande à modifier.")
            return

        commande_id = int(self.table_commandes.item(selected_row, 0).text())
        commande = session.query(Commande).get(commande_id)

        if commande:
            dialog = AjouterCommandeDialog(self)
            dialog.date_commande.setDate(commande.date_commande)
            dialog.client_combo.setCurrentIndex(dialog.client_combo.findData(commande.client.id))
            for i in range(dialog.produits_list.count()):
                item = dialog.produits_list.item(i)
                if item.text() in [p.nom for p in commande.produits]:
                    item.setSelected(True)
            dialog.prix_input.setValue(commande.prix)  # Nouveau champ
            dialog.quantite_input.setValue(commande.quantite)
            dialog.statut_combo.setCurrentText(commande.statut.value)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                ancien_statut = commande.statut
                commande.date_commande = dialog.date_commande.date().toPyDate()
                commande.client_id = dialog.client_combo.currentData()
                commande.produits = []
                for item in dialog.produits_list.selectedItems():
                    produit = session.query(Produit).filter_by(nom=item.text()).first()
                    if produit:
                        commande.produits.append(produit)
                commande.prix = dialog.prix_input.value()  # Nouveau champ
                commande.quantite = dialog.quantite_input.value()
                nouveau_statut = StatutCommande(dialog.statut_combo.currentText())

                try:
                    self.mettre_a_jour_inventaire(commande, ancien_statut, nouveau_statut)
                    commande.statut = nouveau_statut
                    session.commit()
                    self.charger_commandes()
                    QMessageBox.information(self, "Succès", "La commande a été modifiée avec succès.")
                    self.inventaire_modifie.emit()
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Erreur", f"Impossible de modifier la commande : {str(e)}")
                    print(f"Erreur détaillée : {e}")  # Pour le débogage

    def mettre_a_jour_inventaire(self, commande, ancien_statut, nouveau_statut):
        if ancien_statut == nouveau_statut:
            return  # Pas de changement de statut, pas besoin de mettre à jour l'inventaire

        for produit in commande.produits:
            # Trouver l'entrée inventaire_produit correspondante
            inv_prod = session.query(inventaire_produit).filter_by(produit_id=produit.id).first()
            if not inv_prod:
                raise ValueError(f"Aucune entrée d'inventaire trouvée pour le produit {produit.nom}")

            inventaire = session.query(Inventaire).get(inv_prod.inventaire_id)
            if not inventaire:
                raise ValueError(f"Inventaire non trouvé pour le produit {produit.nom}")

            quantite_a_ajuster = commande.quantite  # Utilisez la quantité de la commande

            if ancien_statut != StatutCommande.PAYEE and nouveau_statut == StatutCommande.PAYEE:
                # La commande vient d'être payée, on retire du stock
                inventaire.quantite -= quantite_a_ajuster
            elif ancien_statut == StatutCommande.PAYEE and nouveau_statut != StatutCommande.PAYEE:
                # La commande n'est plus payée, on remet en stock
                inventaire.quantite += quantite_a_ajuster

            if inventaire.quantite < 0:
                raise ValueError(f"Stock insuffisant pour le produit {produit.nom}")

    def supprimer_commande(self):
        selected_row = self.table_commandes.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une commande à supprimer.")
            return

        commande_id = int(self.table_commandes.item(selected_row, 0).text())
        commande = session.query(Commande).get(commande_id)

        if commande:
            reply = QMessageBox.question(self, "Confirmation", f"Êtes-vous sûr de vouloir supprimer la commande {commande.id} ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    session.delete(commande)
                    session.commit()
                    self.table_commandes.removeRow(selected_row)
                    QMessageBox.information(self, "Succès", "La commande a été supprimée avec succès.")
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Erreur", f"Impossible de supprimer la commande : {str(e)}")

    def retirer_de_inventaire(self, commande):
        if commande.statut != StatutCommande.PAYEE:
            return  # Ne rien faire si la commande n'est pas payée

            
        
        commandes=session.query(Commande).filter_by(id=commande.id).first()
   
        produits=commandes.produits

        for produit in produits:
            produitId=produit.id
            quantite_a_retirer = commandes.quantite  # Par défaut, on retire 1 unité
            # Vous pouvez ajuster cette logique selon vos besoins, par exemple :
            # quantite_a_retirer = produit.quantite_ingredient(ingredient)

            inventaire = session.query(Inventaire).filter_by(id=produitId).first()
            if inventaire:
                inventaire.quantite -= quantite_a_retirer
                if inventaire.quantite < 0:
                    inventaire.quantite = 0
                    QMessageBox.warning(self, "Attention", f"Le stock de {produit.nom} est épuisé.")

        try:
            session.commit()
            QMessageBox.information(self, "Succès", "L'inventaire a été mis à jour.")
            self.inventaire_modifie.emit()  # Émet le signal
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Erreur", f"Impossible de mettre à jour l'inventaire : {str(e)}")


       

