from abc import ABC
from uuid import UUID
from plutus.transaction.transaction import Transaction, UncategorizedTransaction

class ITransactionRepository(ABC):
    def create(self, transaction: Transaction):
        pass

    def get_all(self) -> list[Transaction]:
        pass

    def find(self, payee: str) -> list[Transaction]:
        pass

    def delete(self, transaction_id: UUID):
        pass

class IUncategorizedTransactionRepository(ABC):
    def create(self, uncat_trans: UncategorizedTransaction):
        pass
