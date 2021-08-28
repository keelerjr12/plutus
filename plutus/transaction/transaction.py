from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

class SplitType(Enum):
    CREDIT = 1
    DEBIT = 2

class Split:
    def __init__(self, account_id: UUID, transaction_id: UUID, desc: str, type: SplitType, quantity: Decimal, value: Decimal):
        if quantity < 0:
            raise Exception('Quantity cannot be less than 0!')
        if quantity < 0:
            raise Exception('Value cannot be less than 0!')
        
        self.account_id = account_id
        self.transaction_id = transaction_id
        self.description = desc
        self.type: SplitType = type
        self.quantity = quantity
        self.value = value

    def is_credit(self) -> bool:
        return self.type == "Credit"
    
    def is_debit(self) -> bool:
        return self.type == "Debit"

class Transaction:    
    def __init__(self, id: UUID, date: date, splits: list[Split]):
        self.id = id
        self.date = date
        self.splits = splits

        self._validate_splits()

    def _validate_splits(self) -> None:
        credits = sum([split.amount for split in self.splits if split.is_credit()])
        debits = sum([split.amount for split in self.splits if split.is_debit()])

        if credits != debits:
            raise Exception('Transaction is imbalanced')

@dataclass
class UncategorizedTransaction:
    id: int
    date: date
    account_id: UUID
    description: str
    type: str
    amount: str