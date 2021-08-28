from decimal import Decimal
from enum import Enum
from logging import exception
from uuid import UUID

class AccountType(Enum):
    ASSET = 1
    EQUITY = 2
    EXPENSE = 3
    INCOME = 4
    LIABILITY = 5

    @staticmethod
    def from_str(label):
        if label in ('Asset', 'asset', 'ASSET'):
            return AccountType.ASSET
        elif label in ('Equity', 'equity', 'EQUITY'):
            return AccountType.EQUITY
        elif label in ('Expense', 'expense', 'EXPENSE'):
            return AccountType.EXPENSE
        elif label in ('Income', 'income', 'INCOME'):
            return AccountType.INCOME
        elif label in ('Liability', 'liability', 'LIABILITY'):
            return AccountType.LIABILITY
        else:
            raise NotImplementedError

    def __str__(self):
        return self.name.lower().capitalize()
    
class Account():

    def __init__(self, id: UUID, name: str, type: AccountType, roa_rate: Decimal = 0, children_ids: list[int] = None, transaction_ids: list[int] = None):
        self.id = id
        self.name = name
        self.type = type
        self.roa_rate = roa_rate
        self._parent_id = None
        self._children_ids = children_ids
        self._transaction_ids = transaction_ids

    @property
    def parent_id(self):
        return self._parent_id
       
    @parent_id.setter
    def parent_id(self, id):
        self._parent_id = id

    def delete(self) -> None:
        if self._has_subaccounts():
            raise exception('Cannot delete an account with subaccounts')

        if self._has_transactions():
            raise exception('Cannot delete an account with transactions')

    def _has_subaccounts(self) -> bool:
        if len(self._children_ids) > 0:
            return True
        
        return False

    def _has_transactions(self) -> bool:
        if len(self._transaction_ids) > 0:
            return True
        
        return False