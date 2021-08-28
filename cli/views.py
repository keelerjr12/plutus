from abc import ABC
from datetime import date
from plutus.reports.queries import LedgerEntryModel
from plutus.account.queries import AccountMetadataDto, HierarchicalAccountDto
from cli.components import TableComponentModel, TableComponentView
from plutus.reports.reports import PlanDto
from prettytable.prettytable import PrettyTable

class ConsoleTableViewModel(ABC):
    def __init__(self):
        self.title = ""

        self.header = ""

        self.rows = []

class ConsoleTableView():
    def __init__(self, table_vm: ConsoleTableViewModel):
        self._table_vm = table_vm

    def show(self):
        print(self._table_vm.title)

        model = TableComponentModel(self._table_vm.header, self._table_vm.rows)
        view = TableComponentView(model)

        view.show()

class HierarchicalAccountViewModel:
    def __init__(self, acct_dto: HierarchicalAccountDto, level: int = 0):
        self.acct_dto = acct_dto
        self.level = level

class AccountsViewModel(ConsoleTableViewModel):
    def __init__(self, accounts: list[HierarchicalAccountDto]):
        self.title = 'Account List'

        self.header = ['Id', 'Name', 'Type', 'Balance']
                
        self.rows = []
        stack = []

        for acct in accounts:
            stack.append(HierarchicalAccountViewModel(acct))

        while len(stack) > 0:
            acct_vm = stack.pop(0)
            acct = acct_vm.acct_dto

            self.rows.append([acct.id, str("+" * acct_vm.level) + acct.name, acct.type, acct.balance])

            stack[0:0] = [HierarchicalAccountViewModel(acct, acct_vm.level + 1) for acct in acct.children]

class AccountDetailsViewModel(ConsoleTableViewModel):
    def __init__(self, account: AccountMetadataDto):
        self.title = f'{account.name} Account Details'

        self.header = ['Id', 'Name', 'Type', 'Rate', 'Balance']

        self.rows = [[account.id, account.name, account.type, account.roa_rate, account.balance]]

class LedgerViewModel(ConsoleTableViewModel):
    def __init__(self, account: AccountMetadataDto, ledger: list[LedgerEntryModel]):
        self.title = f'Ledger for account {account.name}'

        self.header = ['Tx_Id', 'Date', 'Account', 'Desc', 'Amount', 'Balance']

        rows = []
        for entry in ledger:
            #val = entry.value if (entry.type == 'Credit') else -1 * entry.value
            d = entry.date if (entry.date <= date.today()) else f'**{entry.date}**'
            rows.append([entry.id, d, entry.account, entry.description, entry.value, entry.balance])
        
        self.rows = rows

class BalanceSheetView():
    def __init__(self, bs):
        self._bs = bs

    def show(self):
        table = PrettyTable()
        table.field_names = ['Asset', 'Balance']
        for asset in self._bs.assets:
            table.add_row([asset.name, asset.balance])
            
        print(table)
        print(f"Total Assets: ${self._bs.total_asset_balance}\n")

        table = PrettyTable()
        table.field_names = ['Liability', 'Balance']
        for liability in self._bs.liabilities:
            table.add_row([liability.name, liability.balance])
            
        print(table)
        print(f"Total Liabilities: ${self._bs.total_liability_balance}\n")

        #print(f"Total Networth: ${self._bs['Balance']}")

class ProjectionViewModel(ConsoleTableViewModel):
    def __init__(self, projection):
        self.title = "Projection"

        self.header = ['Date', 'Balance']

        self.rows = []
        for row in projection:
            self.rows.append([row.date, row.balance])

class PlanView():
    def __init__(self, plan: PlanDto):
        self._plan = plan

    def show(self):
        table = PrettyTable()

        table.add_column('Dates', self._plan.dates)

        for acct in self._plan.accts:
            table.add_column(acct.name, acct.entries)

        print(table)

def prompt_view(payee: str) -> str:
    print(f'Which account for payee {payee}?')
    acct = input()

    return acct

def prompt_view_account(account: str) -> bool:
    print(f'Did you mean {account}?')
    resp = input()

    return True if resp == 'Y' or resp == 'y' else False
