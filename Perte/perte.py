from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QFormLayout, QLineEdit, QSpinBox, QDateEdit, QComboBox)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTranslator, QCoreApplication
from models import Perte, Produit, Inventaire, session
from sqlalchemy import desc
import qtawesome as qta

# Styles
BUTTON_STYLE = """
QPushButton {
    background-color: #4CAF50;
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
    background-color: #45a049;
}
"""

TABLE_STYLE = """
QTableWidget {
    background-color: #f2f2f2;
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

DIALOG_STYLE = """
QDialog {
    background-color: #f0f0f0;
}
QLineEdit, QSpinBox, QDateEdit, QComboBox {
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 3px;
}
"""

class PerteTab(QWidget):
    inventaire_modifie = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.ajouter_button = QPushButton(self.tr("Ajouter une perte"))
        self.ajouter_button.setIcon(qta.icon('fa5s.plus'))
        self.ajouter_button.clicked.connect(self.ouvrir_formulaire_perte)
        self.ajouter_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.ajouter_button)

        self.table_pertes = QTableWidget()
        self.table_pertes.setColumnCount(5)
        self.table_pertes.setHorizontalHeaderLabels([
            self.tr("ID"), self.tr("Produit"), self.tr("Quantité"),
            self.tr("Date de perte"), self.tr("Raison")
        ])
        self.table_pertes.verticalHeader().setVisible(False)
        self.table_pertes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_pertes.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table_pertes)

        button_layout = QHBoxLayout()
        self.modifier_button = QPushButton(self.tr("Modifier"))
        self.modifier_button.setIcon(qta.icon('fa5s.edit'))
        self.modifier_button.clicked.connect(self.modifier_perte)
        self.modifier_button.setStyleSheet(BUTTON_STYLE)
        button_layout.addWidget(self.modifier_button)

        self.supprimer_button = QPushButton(self.tr("Supprimer"))
        self.supprimer_button.setIcon(qta.icon('fa5s.trash'))
        self.supprimer_button.clicked.connect(self.supprimer_perte)
        self.supprimer_button.setStyleSheet(BUTTON_STYLE)
        button_layout.addWidget(self.supprimer_button)

        layout.addLayout(button_layout)

        self.charger_pertes()

    def charger_pertes(self):
        self.table_pertes.setRowCount(0)
        pertes = session.query(Perte).order_by(desc(Perte.date_perte)).all()
        for perte in pertes:
            self.ajouter_perte_a_table(perte)

    def ajouter_perte_a_table(self, perte):
        row_position = self.table_pertes.rowCount()
        self.table_pertes.insertRow(row_position)
        self.table_pertes.setItem(row_position, 0, QTableWidgetItem(str(perte.id)))
        self.table_pertes.setItem(row_position, 1, QTableWidgetItem(perte.produit.nom))
        self.table_pertes.setItem(row_position, 2, QTableWidgetItem(str(perte.quantite)))
        self.table_pertes.setItem(row_position, 3, QTableWidgetItem(perte.date_perte.strftime("%Y-%m-%d")))
        self.table_pertes.setItem(row_position, 4, QTableWidgetItem(perte.raison))

    def ouvrir_formulaire_perte(self, perte=None):
        dialog = AjouterPerteDialog(self, perte)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            produit_id, quantite, date_perte, raison = dialog.get_data()
            if perte:
                self.modifier_perte_existante(perte.id, produit_id, quantite, date_perte, raison)
            else:
                self.ajouter_perte(produit_id, quantite, date_perte, raison)

    def ajouter_perte(self, produit_id, quantite, date_perte, raison):
        nouvelle_perte = Perte(produit_id=produit_id, quantite=quantite, date_perte=date_perte, raison=raison)
        session.add(nouvelle_perte)
        self.mettre_a_jour_inventaire(produit_id, -quantite)
        session.commit()
        self.ajouter_perte_a_table(nouvelle_perte)
        self.inventaire_modifie.emit()

    def modifier_perte(self):
        selected_rows = self.table_pertes.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("Erreur"), self.tr("Veuillez sélectionner une perte à modifier."))
            return
        perte_id = int(self.table_pertes.item(selected_rows[0].row(), 0).text())
        perte = session.query(Perte).get(perte_id)
        if perte:
            self.ouvrir_formulaire_perte(perte)

    def modifier_perte_existante(self, perte_id, produit_id, quantite, date_perte, raison):
        perte = session.query(Perte).get(perte_id)
        if perte:
            ancienne_quantite = perte.quantite
            ancien_produit_id = perte.produit_id
            
            perte.produit_id = produit_id
            perte.quantite = quantite
            perte.date_perte = date_perte
            perte.raison = raison
            
            # Mettre à jour l'inventaire
            if ancien_produit_id == produit_id:
                self.mettre_a_jour_inventaire(produit_id, ancienne_quantite - quantite)
            else:
                self.mettre_a_jour_inventaire(ancien_produit_id, ancienne_quantite)
                self.mettre_a_jour_inventaire(produit_id, -quantite)
            
            session.commit()
            self.charger_pertes()
            self.inventaire_modifie.emit()

    def supprimer_perte(self):
        selected_rows = self.table_pertes.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, self.tr("Erreur"), self.tr("Veuillez sélectionner une perte à supprimer."))
            return
        perte_id = int(self.table_pertes.item(selected_rows[0].row(), 0).text())
        perte = session.query(Perte).get(perte_id)
        if perte:
            reply = QMessageBox.question(self, self.tr("Confirmation"),
                                         self.tr("Êtes-vous sûr de vouloir supprimer cette perte ?"),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.mettre_a_jour_inventaire(perte.produit_id, perte.quantite)
                session.delete(perte)
                session.commit()
                self.charger_pertes()
                self.inventaire_modifie.emit()

    def mettre_a_jour_inventaire(self, produit_id, quantite):
        produit = session.query(Produit).get(produit_id)
        if produit:
            inventaire = session.query(Inventaire).filter(Inventaire.produits.contains(produit)).first()
            if inventaire:
                inventaire.quantite += quantite

class AjouterPerteDialog(QDialog):
    def __init__(self, parent=None, perte=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Ajouter une perte") if perte is None else self.tr("Modifier une perte"))
        self.setModal(True)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QFormLayout(self)

        self.produit_combo = QComboBox()
        self.charger_produits()
        self.quantite_input = QSpinBox()
        self.quantite_input.setRange(1, 1000000)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.raison_input = QLineEdit()

        layout.addRow(self.tr("Produit:"), self.produit_combo)
        layout.addRow(self.tr("Quantité:"), self.quantite_input)
        layout.addRow(self.tr("Date de perte:"), self.date_input)
        layout.addRow(self.tr("Raison:"), self.raison_input)

        buttons = QHBoxLayout()
        self.ok_button = QPushButton(self.tr("OK"))
        self.cancel_button = QPushButton(self.tr("Annuler"))
        self.ok_button.setStyleSheet(BUTTON_STYLE)
        self.cancel_button.setStyleSheet(BUTTON_STYLE)
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)

        layout.addRow(buttons)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        if perte:
            self.produit_combo.setCurrentText(perte.produit.nom)
            self.quantite_input.setValue(perte.quantite)
            self.date_input.setDate(perte.date_perte)
            self.raison_input.setText(perte.raison)

    def charger_produits(self):
        produits = session.query(Produit).all()
        for produit in produits:
            self.produit_combo.addItem(produit.nom, produit.id)

    def get_data(self):
        return (
            self.produit_combo.currentData(),
            self.quantite_input.value(),
            self.date_input.date().toPyDate(),
            self.raison_input.text()
        )
