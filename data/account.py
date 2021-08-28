from sqlalchemy.dialects.postgresql import UUID
from data.transaction import SplitDataModel
from plutus.account.account import Account
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DECIMAL, Date, String
from sqlalchemy import Column, Integer
from data.database import Base
from plutus.account.repository import IAccountRepository
from sqlalchemy.orm import Session

class AccountType(Base):
    __tablename__ = "account_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class AccountDataModel(Base):
    __tablename__ = "account"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String)

    type_id = Column(Integer, ForeignKey('account_type.id'))
    account_type = relationship(AccountType, lazy='joined')

    roa_rate = Column(DECIMAL)

    parent_id = Column(UUID(as_uuid=True), ForeignKey('account.id'))
    #parent = relationship('AccountDataModel', remote_side=[id])

    subaccounts = relationship('AccountDataModel')

    splits = relationship(SplitDataModel, lazy='joined')

account_types = {'Asset': 1, 'Expense': 2, 'Income': 3, 'Liability': 4}

class SqlAccountRepository(IAccountRepository):

    def __init__(self, db: Session):
        self._db = db

    def create(self, account: Account):
        acct = AccountDataModel(id = account.id, name = account.name, type_id = account.type.value, roa_rate = account.roa_rate, parent_id = account.parent_id)

        self._db.add(acct)
        self._db.commit()

    def get_all(self, account_type = '') -> list[AccountDataModel]:
        query = self._db.query(AccountDataModel)

        if (account_type != ''):
            query = query.filter(AccountDataModel.account_type.has(AccountType.name == account_type))
            
        sqlAccounts = query.all()

        accounts = [self._map_account(acct_dto) for acct_dto in sqlAccounts]

        return accounts

    def get_by_id(self, id: int) -> AccountDataModel:
        acct_dto = self._db.query(AccountDataModel).get(id)
        account = self._map_account(acct_dto)
        return account

    def get_by_name(self, name: str) -> AccountDataModel:
        account = self._db.query(AccountDataModel).filter(AccountDataModel.name == name).first()
        if (account == None):
            return None

        account = self._map_account(account)

        return account

    def delete(self, acct: Account) -> None:
        self._db.query(AccountDataModel).filter(AccountDataModel.id == acct.id).delete()

    # TODO: Can separate from class
    def _map_account(self, acct: AccountDataModel) -> Account:
            children_ids = [child.id for child in acct.subaccounts]
            transaction_ids = [split.transaction_id for split in acct.splits]
            acct = Account(acct.id, acct.name, acct.account_type, acct.roa_rate, children_ids, transaction_ids)

            return acct