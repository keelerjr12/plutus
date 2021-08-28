from uuid import UUID
from plutus.reports.balancesheet import BalanceSheetQuery
from plutus.reports.queries import GetAccountLedgerQuery
from data.transaction import SqlTransactionRepository
from data.account import SqlAccountRepository
from decimal import Decimal
from plutus.account.queries import GetAccountHierarchyByIdQuery, GetAccountMetadataByNameQuery, GetAccountQuery, GetAccountsHierarchyQuery
from plutus.reports.reports import ReportService
from plutus.account.commands import CreateAccountCommand, DeleteAccountCommand
from plutus.transaction.commands import CreateTransactionCommand, DeleteTransactionCommand
from data.database import SessionLocal
from cli.views import AccountDetailsViewModel, ConsoleTableView, AccountsViewModel, BalanceSheetView, LedgerViewModel, prompt_view, prompt_view_account
import click

session = SessionLocal()
account_repo = SqlAccountRepository(session)
trans_repo = SqlTransactionRepository(session)

class ServiceFactory():
    def report_service() -> ReportService:
        session = SessionLocal()
        account_repo = SqlAccountRepository(session)
        trans_repo = SqlTransactionRepository(session)
        return ReportService(account_repo, trans_repo, session)

@click.group()
def cli():
    pass

@click.command()
@click.argument('name')
@click.option('-t', '--type', default="Asset")
@click.option('-r', '--rate')
@click.option('-p', '--parent')
def create_account(name, type, rate, parent):
    print(f'Creating new account {name} of type {type}')

    resp = CreateAccountCommand(account_repo, session).execute(name, type, rate, parent)
    
    if resp == False:
        print(f'Account with name {name} already exists')

@click.command()
def accounts():
    accounts = GetAccountsHierarchyQuery().execute()
    view = ConsoleTableView(AccountsViewModel(accounts))
    view.show()

@click.command()
@click.argument('name')
def account(name):
    account = GetAccountHierarchyByIdQuery().execute(name)

    if account == None:
        print(f'Account {name} does not exist!')
        return

    view = ConsoleTableView(AccountDetailsViewModel(account))
    view.show()

@click.command()
@click.option('--id')
def delete_account(id: UUID):
    print(f'Deleting account {id}')

    #account = GetAccountMetadataByNameQuery().execute(id)
    account = GetAccountQuery().execute(id)

    if account == None:
        print(f'Account {id} does not exist!')
        return

    DeleteAccountCommand(account_repo, session).execute(account.id)

@click.command()
@click.argument('date')
@click.argument('debit_account_id')
@click.argument('credit_account_id')
@click.argument('desc')
@click.argument('quantity', type=Decimal)
def create_transaction(date, debit_account_id, credit_account_id, desc, quantity):
    print(f'Creating new transaction')
    # TODO: allow for different values
    value = Decimal('1.0')
    CreateTransactionCommand(trans_repo, session).execute(date, debit_account_id, credit_account_id, desc, quantity, value)

@click.command()
@click.argument('transaction_id')
def delete_transaction(transaction_id):
    print(f'Deleting transaction')
    DeleteTransactionCommand(trans_repo, session).execute(transaction_id)

# @click.command()
# @click.argument('for_account_id', type=int)
# @click.argument('file_name')
# def load_transactions(for_account_id: int, file_name: str):
#     print(f'Loading transactions')

#     #tlc = TransactionLoaderController()
#     #tlc.load(for_account_id, file_name)

#     loader = ServiceFactory.transaction_loader()
#     loader.load(for_account_id, file_name, prompt_view, prompt_view_account) #TODO: Make this class

@click.command()
@click.argument('account_name')
def ledger(account_name: str):
    account = GetAccountMetadataByNameQuery().execute(account_name)
    ledger = GetAccountLedgerQuery().execute(account.id)
    view = ConsoleTableView(LedgerViewModel(account, ledger))
    view.show()

@click.command()
def balance_sheet():
    bs = BalanceSheetQuery().execute()
    view = BalanceSheetView(bs)
    view.show()

# @click.command()
# @click.argument('account_id')
# @click.option('-y', '--years', 'years', default=20)
# def projection(account_id, years):
#     projection = ServiceFactory.report_service().get_projection(account_id, years)
#     view = ConsoleTableView(ProjectionViewModel(projection))
#     view.show()

# @click.command()
# def plan():
#     plan = ServiceFactory.report_service().get_plan()
#     view = PlanView(plan)
#     view.show()

cli.add_command(create_account)
cli.add_command(accounts)
cli.add_command(account)
cli.add_command(delete_account)
cli.add_command(create_transaction)
cli.add_command(delete_transaction)
#cli.add_command(load_transactions)
cli.add_command(ledger)
cli.add_command(balance_sheet)
#cli.add_command(projection)
#cli.add_command(plan)

cli()