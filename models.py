from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
import enum

Base = declarative_base()

# Table d'association pour la relation many-to-many entre Produit et Inventaire
produit_inventaire = Table('produit_inventaire', Base.metadata,
    Column('produit_id', Integer, ForeignKey('produits.id')),
    Column('inventaire_id', Integer, ForeignKey('inventaire.id'))
)

class StatutCommande(enum.Enum):
    EN_ATTENTE = "En attente"
    PAYEE = "Payée"
    ANNULEE = "Annulée"

class StatusInventaire(enum.Enum):
    EN_STOCK = "En stock"
    RUPTURE = "Rupture de stock"
    COMMANDE = "Commandé"

class Inventaire(Base):
    __tablename__ = 'inventaire'
    id = Column(Integer, primary_key=True)
    nom = Column(String(50), nullable=False)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    status = Column(Enum(StatusInventaire), nullable=False)
    date_mise_a_jour = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    produits = relationship("Produit", secondary="inventaire_produit", back_populates="inventaires")

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    telephone = Column(String(20))
    commandes = relationship("Commande", back_populates="client")

class Commande(Base):
    __tablename__ = 'commandes'
    id = Column(Integer, primary_key=True)
    date_commande = Column(DateTime, default=datetime.utcnow)
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship("Client", back_populates="commandes")
    statut = Column(Enum(StatutCommande), default=StatutCommande.EN_ATTENTE)
    quantite = Column(Integer, nullable=False)  # Changé de total à quantité
    prix = Column(Float, nullable=False)

    produits = relationship("Produit", secondary="commande_produit")

class Paiement(Base):
    __tablename__ = 'paiements'
    id = Column(Integer, primary_key=True)
    commande_id = Column(Integer, ForeignKey('commandes.id'))
    montant = Column(Float, nullable=False)
    date_paiement = Column(DateTime, nullable=False)
    commande = relationship("Commande")

class Produit(Base):
    __tablename__ = 'produits'
    id = Column(Integer, primary_key=True)
    nom = Column(String(50), nullable=False)
    prix = Column(Float, nullable=False)
    description = Column(String(200))
    date_creation = Column(DateTime, default=datetime.utcnow)

    commandes = relationship("Commande", secondary="commande_produit", back_populates="produits")
    pertes = relationship("Perte", back_populates="produit")
    inventaires = relationship("Inventaire", secondary="inventaire_produit", back_populates="produits")

class Depense(Base):
    __tablename__ = 'depenses'
    id = Column(Integer, primary_key=True)
    description = Column(String(200), nullable=False)
    montant = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

class Perte(Base):
    __tablename__ = 'pertes'
    id = Column(Integer, primary_key=True)
    produit_id = Column(Integer, ForeignKey('produits.id'), nullable=False)
    quantite = Column(Integer, nullable=False)
    date_perte = Column(DateTime, default=datetime.utcnow)
    raison = Column(String(200))

    produit = relationship("Produit", back_populates="pertes")

commande_produit = Table('commande_produit', Base.metadata,
    Column('commande_id', Integer, ForeignKey('commandes.id'), primary_key=True),
    Column('produit_id', Integer, ForeignKey('produits.id'), primary_key=True)
)

inventaire_produit = Table('inventaire_produit', Base.metadata,
    Column('inventaire_id', Integer, ForeignKey('inventaire.id'), primary_key=True),
    Column('produit_id', Integer, ForeignKey('produits.id'), primary_key=True)
)

# Modifiez cette ligne pour inclure le nom de la base de données dans l'URL
db_url = 'mysql://root:@localhost/poulaillerdb'
# db_url = 'mysql://root:@localhost/testdb'

# Créez le moteur
engine = create_engine(db_url)

# Vérifiez si la base de données existe, sinon créez-la
if not database_exists(engine.url):
    create_database(engine.url)
    print("Base de données créée avec succès.")

# Créez toutes les tables
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
