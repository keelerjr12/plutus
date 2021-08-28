from uuid import UUID
from decimal import Decimal
from plutus.account.commands import CreateAccountCommand, DeleteAccountCommand
from typing import Optional
from plutus.account.queries import GetAccountHierarchyByIdQuery, GetAccountsHierarchyQuery
from fastapi import status, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel
from .dependencies import account_repo, session

router = APIRouter(
    prefix="/api/accounts"
)

class AccountResponse(BaseModel):

    id: UUID = None
    name: str = None
    type: str = None
    roa_rate: str = None
    balance: str = None
    parent_id: Optional[UUID] = None
    children: list = None

def account_to_response(acct):
    resp = AccountResponse()
    resp.id = acct.id
    resp.name = acct.name
    resp.type = acct.type.__str__()
    resp.roa_rate = '{0:.2f}'.format(acct.roa_rate * 100)
    resp.balance = '{0:.2f}'.format(acct.balance)
    resp.parent_id =  acct.parent_id
    resp.children = acct.children

    return resp

def accounts_to_response(accounts):
    acct_resps = [account_to_response(acct) for acct in accounts]

    queue = acct_resps.copy()

    for acct in queue:
        child_resps = [account_to_response(child) for child in acct.children]
        acct.children = child_resps

        queue += child_resps

    return acct_resps

@router.get("", response_model=list[AccountResponse], response_model_exclude_none=True)
async def get_accounts():
    accounts = GetAccountsHierarchyQuery().execute()

    accts_resp = accounts_to_response(accounts)
    
    return accts_resp

@router.get("/{id}", response_model=AccountResponse, response_model_exclude_none=True)
async def get_accounts(id: UUID):
    try:
        account = GetAccountHierarchyByIdQuery().execute(id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    resp = account_to_response(account)

    return resp

class CreateAccountRequest(BaseModel):
    name: str
    account_type: str
    roa_rate: str
    parent: Optional[UUID] = None

# TODO: need to handle duplicate names and error cases
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_account(request: CreateAccountRequest):
    rate = Decimal(request.roa_rate) / Decimal('100')
    resp = CreateAccountCommand(account_repo, session).execute(request.name, request.account_type, rate, request.parent)

# TODO: need to handle error cases
@router.delete("/{id}")
async def delete_account(id: int):
    resp = DeleteAccountCommand(account_repo, session).execute(id)