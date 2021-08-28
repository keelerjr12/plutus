from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4
from ofxparse.ofxparse import OfxParser
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.sqltypes import Date
from plutus.transaction.repository import ITransactionRepository, IUncategorizedTransactionRepository
from plutus.transaction.transaction import Split, SplitType, Transaction, UncategorizedTransaction


class CreateTransactionCommand:

    def __init__(self, transRepo: ITransactionRepository, session: Session):
        self._transRepo = transRepo
        self._session = session    

    def execute(self, date: date, debit_account_id: UUID, credit_account_id: UUID, desc: str, quantity: Decimal, value: Decimal):
        if value < 0:
            raise Exception('Value cannot be less than 0!')
        
        id = uuid4()

        splits = []
        split = Split(credit_account_id, id, desc, SplitType.CREDIT, quantity, value)
        splits.append(split)
        split = Split(debit_account_id, id, desc, SplitType.DEBIT, quantity, value)
        splits.append(split)

        transaction = Transaction(id, date, splits)

        self._transRepo.create(transaction)
        self._session.commit()

class DeleteTransactionCommand:

    def __init__(self, transRepo: ITransactionRepository, session: Session):
        self._transRepo = transRepo
        self._session = session    

    def execute(self, transaction_id: UUID):
        self._transRepo.delete(transaction_id)
        self._session.commit()

class UploadTransactionFileCommand:

    def __init__(self, trans_repo: ITransactionRepository, uncat_trans_repo: IUncategorizedTransactionRepository, session):
        self._trans_repo = trans_repo
        self._uncat_trans_repo = uncat_trans_repo
        self._session = session

    def execute(self, file, for_account_id: UUID):
        ofx = OfxParser.parse(file)
        transactions = ofx.account.statement.transactions

        for transaction in transactions:
            print(transaction.date, transaction.payee, transaction.type, transaction.amount)

            found_transactions = self._trans_repo.find(transaction.payee)

            possible_account_id = None
            for trans in found_transactions:
                for split in trans.splits:
                    if split.account_id != for_account_id:
                        possible_account_id = split.account_id
                        break

            if possible_account_id != None:
                # TODO: This will not work and needs to be refactored!
                CreateTransactionCommand(self._trans_repo, self._session).execute(transaction.date, possible_account_id, for_account_id, transaction.payee, abs(transaction.amount))
            else:
                print(f'Could not add {transaction.payee}')
                
                # TODO: This absolutely must be moved!
                type = SplitType.CREDIT
                if transaction.type == "debit":
                    type = SplitType.DEBIT

                uncat_trans = UncategorizedTransaction(
                    id = "",
                    date = transaction.date,
                    account_id = for_account_id, 
                    description = transaction.payee,
                    type = type,
                    amount = str(abs(transaction.amount)))
                self._uncat_trans_repo.create(uncat_trans)

        self._session.commit()

@dataclass
class CategorizedTransaction:
    id: int
    accountId: UUID

class CategorizeTransactionsCommand:

    def __init__(self, trans_repo: ITransactionRepository, uncat_trans_repo: IUncategorizedTransactionRepository, session):
        self._trans_repo = trans_repo
        self._uncat_trans_repo = uncat_trans_repo
        self._session = session

    def execute(self, for_account_id: UUID, categorized_txs: list[CategorizedTransaction]):
        print('you are here')
        print(for_account_id)
        print(categorized_txs)