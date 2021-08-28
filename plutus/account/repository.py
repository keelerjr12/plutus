from abc import ABC
from plutus.account.account import Account


class IAccountRepository(ABC):
    def create(account: Account):
        pass
        
    def get_all(account_type = '') -> list[Account]:
        pass

    def get_by_id(self, id: int) -> Account:
        pass

    def get_by_name(self, name: str) -> Account:
        pass

    def delete(self, acct: Account) -> None:
        pass