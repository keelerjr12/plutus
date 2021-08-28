from dataclasses import dataclass
from decimal import Decimal
from plutus.account.queries import GetAccountsHierarchyByTypeQuery

@dataclass
class BalanceSheetAccount:
    name: str
    balance: Decimal

@dataclass
class BalanceSheetQueryResponse:
    assets: list[BalanceSheetAccount]
    total_asset_balance: Decimal
    liabilities: list[BalanceSheetAccount]
    total_liability_balance: Decimal

class BalanceSheetQuery:

    def execute(self) -> BalanceSheetQueryResponse:
        assets = GetAccountsHierarchyByTypeQuery().execute('Asset')
        liabilities = GetAccountsHierarchyByTypeQuery().execute('Liability')

        asset_dtos = [BalanceSheetAccount(asset.name, asset.balance) for asset in assets]
        total_asset_balance = sum([asset_dto.balance for asset_dto in asset_dtos])

        liability_dtos = [BalanceSheetAccount(liability.name, liability.balance) for liability in liabilities]
        total_liability_balance = sum([liability_dto.balance for liability_dto in liability_dtos])

        resp = BalanceSheetQueryResponse(asset_dtos, total_asset_balance, liability_dtos, total_liability_balance)

        return resp