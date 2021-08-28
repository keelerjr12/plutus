from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from plutus.account.account import Account, AccountType
from sqlalchemy.orm.session import Session
from plutus.account.repository import IAccountRepository

class CreateAccountCommand:
    def __init__(self, account_repo: IAccountRepository, session: Session):
        self._account_repo = account_repo
        self._session = session

    def execute(self, name: str, account_type: str, roa_rate: Decimal, parent_id: Optional[UUID] = None) -> bool:
        account_found = self._account_repo.get_by_name(name)

        if account_found != None:
            return False

        id = uuid4()
        acct = Account(id, name, AccountType.from_str(account_type), roa_rate)

        if parent_id != None:
            parent = self._account_repo.get_by_id(parent_id)

            if parent == None:
                return False

            acct.parent_id = parent.id

        self._account_repo.create(acct)
        self._session.commit()

class DeleteAccountCommand:

    def __init__(self, accountRepo: IAccountRepository, session: Session):
        self._accountRepo = accountRepo
        self._session = session

    def execute(self, id: int) -> bool:
        acct = self._accountRepo.get_by_id(id)

        if acct == None:
            return False

        acct.delete()
        self._accountRepo.delete(acct)

        self._session.commit()