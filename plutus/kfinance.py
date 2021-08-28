from datetime import date
from decimal import Decimal
from plutus.account.account import Account
from plutus.account.repository import IAccountRepository
from plutus.transaction.repository import ITransactionRepository
from plutus.transaction.transaction import Transaction
from dataclasses import dataclass

@dataclass
class ProjectionRow():
    date: date
    balance: Decimal

class Projection():
    def __init__(self, account_name: str, recent_balance: Decimal, roa_rate: Decimal, num_years: int):
        self.account_name = account_name
        self._init_balance = recent_balance
        self._roa_rate = roa_rate
        self._num_years = num_years
        self._projections = []

    def create(self):
        bal = self._init_balance
        dateVar = date(2021, 1, 1) # TODO: FIX!!!!

        for yr in range(self._num_years):
            for mth in range(1, 13):
                dateVar = date(2021 + yr, mth, 1)

                bal = bal * (1 + self._roa_rate / 12)
                self._projections.append(ProjectionRow(dateVar, bal))

    def all(self) -> list[ProjectionRow]:
        return self._projections

    def by_date(self, year: int, month: int) -> ProjectionRow:
        return [proj for proj in self._projections if proj.date == date(year, month, 1)][0]

class FinancialPlan():
    def __init__(self, acct_repo: IAccountRepository,  trans_repo: ITransactionRepository, num_years: int):
        self._acct_repo = acct_repo
        self._trans_repo = trans_repo
        self._num_years = num_years

    def create(self):
        accts = self._acct_repo.get_all()

        projections = []

        for acct in accts:
            projection = Projection(acct.name, acct.balance, acct.roa_rate, self._num_years)
            projection.create()
            projections.append(projection)
    
        year = 2021
        month = 1

        for year in range(year, year + self._num_years):
            for month in range(1, 13):
                d = date(year, month, 1)
                print(d)

                for proj in projections:
                    print(proj.account_name)
                    row = proj.by_date(year, month)
                    print(row.balance)

        #print(projections)