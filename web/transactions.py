from datetime import date
from decimal import Decimal

from plutus.transaction.queries import GetTransactionsByAccountIdQuery, GetUncategorizedTransactionsQuery, TransactionModel
from uuid import UUID

from pydantic.main import BaseModel
from fastapi import status, APIRouter, UploadFile, File

from plutus.transaction.commands import CategorizeTransactionsCommand, CategorizedTransaction, CreateTransactionCommand, DeleteTransactionCommand, UploadTransactionFileCommand
from .dependencies import trans_repo, uncat_trans_repo, session

from dataclasses import dataclass


router = APIRouter(
    prefix="/api"
)

@dataclass
class TransactionResponse:
    id: int
    date: date
    type: str
    account: str
    description: str
    value: str
    balance: str

def transaction_to_response(tx: TransactionModel) -> TransactionResponse:
    value = "{0:.2f}".format(tx.value)
    balance = "{0:.2f}".format(tx.balance)

    resp = TransactionResponse(tx.id, tx.date, tx.type, tx.account, tx.description, value, balance)
    return resp

@router.get("/accounts/{account_id}/transactions")
async def get_transactions(account_id):
    transactions = GetTransactionsByAccountIdQuery().execute(account_id)

    resp = [transaction_to_response(tx) for tx in transactions]

    return resp

class CreateTransactionRequest(BaseModel):
    date: date
    debit_account_id: UUID
    credit_account_id: UUID
    desc: str
    quantity: Decimal

@router.post("/transactions", status_code=status.HTTP_201_CREATED)
async def create_transaction(request: CreateTransactionRequest):
    print(f'Creating new transaction')
    value = Decimal('1.0')
    CreateTransactionCommand(trans_repo, session).execute(request.date, request.debit_account_id, request.credit_account_id, request.desc, request.quantity, value)

@router.post("/accounts/{account_id}/transactions")
async def upload_transaction_file(file: UploadFile = File(...), account_id = ""):
    print(f'Uploading new transaction file')
    UploadTransactionFileCommand(trans_repo, uncat_trans_repo, session).execute(file.file, account_id)

@dataclass
class UncategorizedTransactionResponse:
    id: int
    date: date
    account: str
    description: str
    type: str
    amount: str

@router.get("/accounts/{account_id}/uncategorized")
async def get_uncategorized_transactions(account_id: UUID) -> list[UncategorizedTransactionResponse]:
    uncat_trans = GetUncategorizedTransactionsQuery().execute(account_id)
    uncat_trans_resp = [UncategorizedTransactionResponse(u.id, u.date, u.account_id, u.description, u.type, str(u.amount)) for u in uncat_trans]
    return uncat_trans_resp

class CategorizedTransactionsRequest(BaseModel):
    transactions: list[CategorizedTransaction]

@router.put("/accounts/{account_id}/uncategorized")
async def categorize_transactions(account_id: UUID, req: CategorizedTransactionsRequest) -> bool:
    CategorizeTransactionsCommand(trans_repo, uncat_trans_repo, session).execute(account_id, req.transactions)
    return True

# TODO: need to handle error cases
@router.delete("/transactions/{id}")
async def delete_account(id: UUID):
    resp = DeleteTransactionCommand(trans_repo, session).execute(id)