from datetime import date
import decimal
from plutus.account.queries import GetAccountQuery
from plutus.transaction.repository import ITransactionRepository
from plutus.account.repository import IAccountRepository
from plutus.kfinance import Projection
from pydantic import parse_obj_as

class PlanAccountDto():
    name: str
    entries: list[decimal.Decimal]

class PlanDto():

    def __init__(self):
        self.dates = []
        self.dates.append(date.today())
        self.dates.append(date.today())

        self.accts = []

        # NEW COL
        acct = PlanAccountDto()
        acct.entries = []
        acct.name = "Savings"
        acct.entries.append(decimal.Decimal('100.69'))
        acct.entries.append(decimal.Decimal('11.69'))
        self.accts.append(acct)

        # NEW COL
        acct = PlanAccountDto()
        acct.entries = []
        acct.name = "Checking"
        acct.entries.append(decimal.Decimal('-100.69'))
        acct.entries.append(decimal.Decimal('-0.69'))
        self.accts.append(acct)

        # NEW COL
        acct = PlanAccountDto()
        acct.entries = []
        acct.name = "Vanguard"
        acct.entries.append(decimal.Decimal('100400.69'))
        acct.entries.append(decimal.Decimal('20000.69'))
        self.accts.append(acct)

class ReportService:
    def __init__(self, account_repo: IAccountRepository, trans_repo: ITransactionRepository, session):
        self._account_repo = account_repo
        self._trans_repo = trans_repo  
        self._session = session

    def get_plan(self) -> PlanDto:
    # with session_scope() as session:
    #     acct_repo = crud.SqlAccountRepository(session)
    #     trans_repo = crud.SqlTransactionRepository(session)

    #     plan = FinancialPlan(acct_repo, trans_repo, 60)
    #     plan.create()
        return PlanDto()

    def get_projection(self, account_id: int, num_years: int = 20) -> list[tuple[date, decimal.Decimal]]:
        acct = GetAccountQuery(account_id).execute()
        projection = Projection(acct.name, acct.balance, acct.roa_rate, num_years)
        projection.create()

        return projection.all()
