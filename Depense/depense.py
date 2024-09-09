from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from models import Depense, session
from sqlalchemy import desc, func
from models import Commande, StatutCommande

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

class DepenseTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Bouton pour ajouter une dépense
        self.ajouter_button = QPushButton("Ajouter une dépense")
        self.ajouter_button.clicked.connect(self.ouvrir_formulaire_depense)
        self.ajouter_button.setStyleSheet(BUTTON_STYLE_BLUE)
        layout.addWidget(self.ajouter_button)

        # Table des dépenses
        self.table_depenses = QTableWidget()
        self.table_depenses.setColumnCount(4)
        self.table_depenses.setHorizontalHeaderLabels(["ID", "Description", "Montant", "Date"])
        self.table_depenses.verticalHeader().setVisible(False)
        self.table_depenses.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_depenses.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table_depenses)

        # Boutons de modification et suppression
        button_layout = QHBoxLayout()
        self.modifier_button = QPushButton("Modifier")
        self.modifier_button.clicked.connect(self.modifier_depense)
        self.modifier_button.setStyleSheet(BUTTON_STYLE_YELLOW)
        button_layout.addWidget(self.modifier_button)

        self.supprimer_button = QPushButton("Supprimer")
        self.supprimer_button.clicked.connect(self.supprimer_depense)
        self.supprimer_button.setStyleSheet(BUTTON_STYLE_RED)
        button_layout.addWidget(self.supprimer_button)

        layout.addLayout(button_layout)

        self.charger_depenses()

    def charger_depenses(self):
        self.table_depenses.setRowCount(0)
        depenses = session.query(Depense).order_by(desc(Depense.date)).all()
        for depense in depenses:
            self.ajouter_depense_a_table(depense)

    def ajouter_depense_a_table(self, depense):
        row_position = self.table_depenses.rowCount()
        self.table_depenses.insertRow(row_position)
        self.table_depenses.setItem(row_position, 0, QTableWidgetItem(str(depense.id)))
        self.table_depenses.setItem(row_position, 1, QTableWidgetItem(depense.description))
        self.table_depenses.setItem(row_position, 2, QTableWidgetItem(f"{depense.montant:.2f}"))
        self.table_depenses.setItem(row_position, 3, QTableWidgetItem(depense.date.strftime("%Y-%m-%d")))

    def ouvrir_formulaire_depense(self):
        dialog = AjouterDepenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            description, montant, date = dialog.get_data()
            if self.verifier_montant_depense(montant):
                self.ajouter_depense(description, montant, date)
            else:
                QMessageBox.warning(self, "Erreur", "Le montant de la dépense est supérieur au montant total des commandes payées.")

    def verifier_montant_depense(self, montant):
        total_commandes_payees = session.query(func.sum(Commande.prix)).filter(Commande.statut == StatutCommande.PAYEE).scalar() or 0
        return montant <= total_commandes_payees

    def ajouter_depense(self, description, montant, date):
        nouvelle_depense = Depense(description=description, montant=montant, date=date)
        session.add(nouvelle_depense)
        session.commit()
        self.ajouter_depense_a_table(nouvelle_depense)

    def modifier_depense(self):
        selected_row = self.table_depenses.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une dépense à modifier.")
            return

        depense_id = int(self.table_depenses.item(selected_row, 0).text())
        depense = session.query(Depense).get(depense_id)

        dialog = AjouterDepenseDialog(self, depense)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            description, montant, date = dialog.get_data()
            depense.description = description
            depense.montant = montant
            depense.date = date
            session.commit()
            self.charger_depenses()

    def supprimer_depense(self):
        selected_row = self.table_depenses.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une dépense à supprimer.")
            return

        depense_id = int(self.table_depenses.item(selected_row, 0).text())
        depense = session.query(Depense).get(depense_id)

        reply = QMessageBox.question(self, "Confirmation", "Êtes-vous sûr de vouloir supprimer cette dépense ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            session.delete(depense)
            session.commit()
            self.table_depenses.removeRow(selected_row)

class AjouterDepenseDialog(QDialog):
    def __init__(self, parent=None, depense=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une dépense" if depense is None else "Modifier une dépense")
        self.setModal(True)
        self.setStyleSheet(MODAL_STYLE)

        layout = QFormLayout(self)

        self.description_input = QLineEdit()
        self.montant_input = QDoubleSpinBox()
        self.montant_input.setRange(0, 1000000)
        self.montant_input.setDecimals(2)
        self.montant_input.setStyleSheet(SPINBOX_STYLE)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        layout.addRow("Description:", self.description_input)
        layout.addRow("Montant:", self.montant_input)
        layout.addRow("Date:", self.date_input)

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

        if depense:
            self.description_input.setText(depense.description)
            self.montant_input.setValue(depense.montant)
            self.date_input.setDate(depense.date.date())

    def get_data(self):
        return (
            self.description_input.text(),
            self.montant_input.value(),
            self.date_input.date().toPyDate()
        )

    def accept(self):
        if self.parent().verifier_montant_depense(self.montant_input.value()):
            super().accept()
        else:
            QMessageBox.warning(self, "Erreur", "Le montant de la dépense est supérieur au montant total des commandes payées.")