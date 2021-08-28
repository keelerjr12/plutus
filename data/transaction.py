from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from data.database import Base
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DECIMAL, Date, String
from plutus.transaction.repository import ITransactionRepository, IUncategorizedTransactionRepository
from plutus.transaction.transaction import Split, Transaction, UncategorizedTransaction

class SplitType(Base):
    __tablename__ = "split_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class SplitDataModel(Base):
    __tablename__ = "split"
    account_id = Column(UUID(as_uuid=True), ForeignKey('account.id'), primary_key=True, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey('transaction.id'), primary_key=True, index=True)
    
    type_id = Column(Integer, ForeignKey('split_type.id'))
    split_type = relationship(SplitType, lazy='joined')

    description = Column(String)

    quantity = Column(DECIMAL)
    value = Column(DECIMAL)

class TransactionDataModel(Base):
    __tablename__ = "transaction"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    date = Column(Date)

    splits = relationship(SplitDataModel, lazy='joined')

class SqlTransactionRepository(ITransactionRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, transaction: Transaction) -> None:
        trans = TransactionDataModel(id = transaction.id, date = transaction.date)
        self.db.add(trans)

        split = SplitDataModel(account_id = transaction.splits[0].account_id, \
            transaction_id=trans.id, \
            type_id=transaction.splits[0].type.value, \
            description=transaction.splits[0].description, \
            quantity=transaction.splits[0].quantity, \
            value=transaction.splits[0].value) 
        self.db.add(split)

        split = SplitDataModel(account_id = transaction.splits[1].account_id, \
            transaction_id=trans.id, \
            type_id=transaction.splits[1].type.value, \
            description=transaction.splits[1].description, \
            quantity=transaction.splits[1].quantity, \
            value=transaction.splits[1].value)
        self.db.add(split)

    def get_all(self) -> list[Transaction]:
        db_transactions = self.db.query(TransactionDataModel)\
        .order_by(TransactionDataModel.date)\
        .all()

        transactions = []
        for t in db_transactions:
            splits = [Split(s.account_id, s.transaction_id, s.description, s.split_type, s.amount) for s in t.splits]
            transactions.append(Transaction(t.id, t.date, splits))
        
        return transactions

    def find(self, payee: str) -> list[Transaction]:
        db_transactions = self.db.query(TransactionDataModel).filter(TransactionDataModel.splits.any(SplitDataModel.description == payee)).all()
        
        transactions = []
        for t in db_transactions:
            splits = []

            for s in t.splits:
                split = Split(s.account_id, s.transaction_id, s.description, s.type, s.amount)
                splits.append(split)
            
            trans = Transaction(t.date, t.id, splits)
            transactions.append(trans)

        return transactions


    def delete(self, transaction_id: UUID) -> None:
        self.db.query(SplitDataModel).filter(SplitDataModel.transaction_id == transaction_id).delete()
        self.db.query(TransactionDataModel).filter(TransactionDataModel.id == transaction_id).delete()

class UncategorizedTransactionDataModel(Base):
    __tablename__ = "uncategorized_transaction"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    account_id = Column(UUID(as_uuid=True), ForeignKey('account.id'))
    
    type_id = Column(Integer, ForeignKey('split_type.id'))
    split_type = relationship(SplitType, lazy='joined')

    description = Column(String)
    quantity = Column(DECIMAL)
    value = Column(DECIMAL)

class SqlUncategorizedTransactionRepository(IUncategorizedTransactionRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, uncat_trans: UncategorizedTransaction):
        uncat_trans = UncategorizedTransactionDataModel(
            date = uncat_trans.date,
            account_id = uncat_trans.account_id,
            type_id = uncat_trans.type.value,
            description = uncat_trans.description,
            quantity = uncat_trans.amount,
            value = Decimal('1.0'))

        self.db.add(uncat_trans)