from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic.types import UUID4
from plutus.account.account import AccountType
from pydantic import BaseModel, constr
from sqlalchemy.sql.expression import text
from data.database import engine

class AccountMetadataDto(BaseModel):
    id: UUID
    name: constr(max_length=63)
    type: AccountType
    roa_rate: Decimal = 0

    class Config:  
        use_enum_values = True

class GetAccountMetadataByNameQuery:

    def execute(self, name: str) -> AccountMetadataDto:                
        with engine.connect() as con:
            d = {'name': name}
            statement = text("""SELECT account.id, account.name, account_type.name AS type, roa_rate 
            FROM account 
            INNER JOIN account_type ON account.type_id = account_type.id
            WHERE account.name = :name;""")

            rs = con.execute(statement, d)
            row = rs.fetchone()
            
            if row == None:
                return None

            id = row['id']
            name = row['name']
            type = row['type']
            rate = row['roa_rate']

            dto = AccountMetadataDto(id = id, name = name, type= AccountType.from_str(type), roa_rate = rate)

        return dto

class GetAccountQuery:

    # def execute(self, id: int) -> AccountMetadataDto:
                
    #     with engine.connect() as con:
                        
    #         d = {'account_id': id, 'type': 'Credit'}
    #         statement = text("""SELECT account_id, type, SUM(amount) FROM split WHERE account_id = :account_id AND type = :type GROUP BY account_id, type""")
    #         rs = con.execute(statement, d)
            
    #         credits = Decimal('0')
    #         row = rs.first()
    #         if row != None:
    #             credits = Decimal(row[2])


    #         d = {'account_id': id, 'type': 'Debit'}
    #         statement = text("""SELECT account_id, type, SUM(amount) FROM split WHERE account_id = :account_id AND type = :type GROUP BY account_id, type""")
    #         rs = con.execute(statement, d)
            
    #         debits = Decimal('0')
    #         row = rs.first()
    #         if row != None:
    #             debits = Decimal(row[2])

    #         statement = text("""SELECT * FROM account WHERE id = :account_id;""")

    #         rs = con.execute(statement, d)
    #         for row in rs:
    #             id = row[0]
    #             name = row[1]
    #             type = row[2]
    #             rate = row[3]

    #     bal = credits - debits
    #     dto = AccountMetadataDto(id = id, name = name, type=type, roa_rate = rate, balance = bal )

    #     return dto

    def execute(self, id: UUID) -> AccountMetadataDto:                
        with engine.connect() as con:
            d = {'id': id}
            statement = text("""SELECT account.id, account.name, account_type.name AS type, roa_rate 
            FROM account 
            INNER JOIN account_type ON account.type_id = account_type.id
            WHERE account.id = :id;""")

            rs = con.execute(statement, d)
            row = rs.fetchone()
            
            if row == None:
                return None

            id = row['id']
            name = row['name']
            type = row['type']
            rate = row['roa_rate']

            dto = AccountMetadataDto(id = id, name = name, type= AccountType.from_str(type), roa_rate = rate)

        return dto

class GetAccountsQuery:
    def execute(self) -> list[AccountMetadataDto]:
        with engine.connect() as con:
            statement = text("""SELECT * FROM account;""")

            rs = con.execute(statement)
            ids = []

            for row in rs:
                ids.append(row[0])
            
        acct_dtos = [GetAccountQuery().execute(id) for id in ids]
        return acct_dtos

@dataclass
class HierarchicalAccountDto:
    id: UUID
    name: str
    type: AccountType
    roa_rate: Decimal
    balance: Decimal
    parent_id: Optional[UUID]

    children: list = field(default_factory=list) 

class GetAccountHierarchyByIdQuery:

    def execute(self, id: UUID) -> HierarchicalAccountDto:
                
        account_hier = {}

        with engine.connect() as con:
        
            d = {'id': id,}
            statement = text("""
                WITH RECURSIVE cte AS (
                    SELECT id, name, type_id, roa_rate, parent_id FROM account WHERE id = :id
                    UNION ALL
                    SELECT a.id, a.name, a.type_id, a.roa_rate, a.parent_id FROM cte c
                    JOIN account a ON a.parent_id = c.id
                ) SELECT cte.id, cte.name, at.name, roa_rate, parent_id FROM cte
                LEFT JOIN account_type at ON at.id = cte.type_id
                ORDER BY cte.name;""")

            rs = con.execute(statement, d)

            rows = rs.fetchall()
            if len(rows) < 1:
                raise Exception(f'Account with id {id} does not exist')

            for acct in rows:
                acct_id = acct[0]
                
                d = {'account_id': acct_id, 'type': 'Credit'}
                statement = text("""SELECT account_id, type_id, SUM(quantity * value) 
                FROM split
                INNER JOIN split_type ON split.type_id = split_type.id
                WHERE account_id = :account_id AND split_type.name = :type 
                GROUP BY account_id, split.type_id""")
                rs = con.execute(statement, d)
                
                credits = Decimal('0')
                row = rs.first()

                if row != None:
                    credits = Decimal(row[2])

                d = {'account_id': acct_id, 'type': 'Debit'}
                statement = text("""SELECT account_id, type_id, SUM(quantity * value)
                FROM split
                INNER JOIN split_type ON split.type_id = split_type.id
                WHERE account_id = :account_id AND split_type.name = :type 
                GROUP BY account_id, split.type_id""")
                rs = con.execute(statement, d)
                
                debits = Decimal('0')
                row = rs.first()

                if row != None:
                    # TODO: Allow the use of 'quantity' and 'value'
                    debits = Decimal(row[2])

                acct_type = AccountType.from_str(acct[2])
                if acct_type == AccountType.ASSET or acct_type == AccountType.EXPENSE:
                    curr_bal = debits - credits
                else:
                    curr_bal = credits - debits

                acct_dto = HierarchicalAccountDto(acct_id, acct[1], acct_type, acct[3], curr_bal, acct[4])
                account_hier[acct_dto.id] = acct_dto

        for acct in account_hier.values():
            if acct.parent_id is None or acct.parent_id not in account_hier.keys():
                root = acct
            else:
                account_hier[acct.parent_id].children.append(acct)

                parent_id = acct.parent_id
                while parent_id in account_hier.keys():
                    account_hier[parent_id].balance += acct.balance
                    parent_id = account_hier[parent_id].parent_id

        return root

class GetAccountsHierarchyQuery:
    def execute(self) -> list[HierarchicalAccountDto]:
        with engine.connect() as con:

            statement = text("""SELECT id, name, parent_id 
            FROM account 
            WHERE parent_id IS NULL 
            ORDER BY name;""")

            rs = con.execute(statement)
            
            root_level: list[HierarchicalAccountDto] = []

            for acct in rs:
                id = acct[0]

                acct_dto = GetAccountHierarchyByIdQuery().execute(id)
                root_level.append(acct_dto)
                
            return root_level

class GetAccountsHierarchyByTypeQuery:
    def execute(self, type: str) -> list[HierarchicalAccountDto]:
        with engine.connect() as con:

            d = {'type': type}
            statement = text("""SELECT account.id, account.name, parent_id 
            FROM account 
            JOIN account_type ON account_type.id = account.type_id
            WHERE parent_id IS NULL AND account_type.name = :type
            ORDER BY name;""")

            rs = con.execute(statement, d)
            
            root_level: list[HierarchicalAccountDto] = []

            for acct in rs:
                name = acct[1]

                #acct_dto = GetAccountHierarchyByNameQuery().execute(name)
                #root_level.append(acct_dto)
                
            return root_level
