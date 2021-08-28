from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from plutus.transaction.transaction import UncategorizedTransaction
from uuid import UUID

from sqlalchemy.sql.expression import text
from data.database import engine


@dataclass
class TransactionModel:
    id: int
    date: date
    type: str
    account: str
    description: str
    value: Decimal
    balance: Decimal = 0

class GetTransactionsByAccountIdQuery:

    def execute(self, account_id: int)-> list[TransactionModel]:
        entry_dtos = []

        with engine.connect() as con:

            d = {'account_id': account_id}

            statement = text("""SELECT account_type.name FROM account
            JOIN account_type ON account.type_id = account_type.id
            WHERE account.id = :account_id;
            """)

            rs = con.execute(statement, d)
            row = rs.fetchone()

            account_type = row['name']

            statement = text("""
                SELECT tx_id, date, account.name AS acct_name, split_type.name AS split_type_name, description, quantity, value FROM
                    (SELECT split.account_id AS split_acct_id, split.type_id AS split_type_id, id AS tx_id, date, split.account_id FROM transaction 
                    JOIN split ON split.transaction_id = transaction.id
                    WHERE split.account_id = :account_id) AS t
                JOIN split ON split.transaction_id = t.tx_id
                JOIN account ON account.id = split.account_id
                JOIN split_type ON split_type.id = split_type_id
                WHERE split.account_id != :account_id
                ORDER BY date;
            """)
        
            running_bal = Decimal('0')
            rs = con.execute(statement, d)

            for row in rs:
                quantity = Decimal(row['quantity'])
                value = Decimal(row['value'])
                
                if account_type == 'Liability' or account_type == 'Income':
                    if row['split_type_name'] == 'Debit':
                        quantity = -1 * quantity
                else:
                    if row['split_type_name'] == 'Credit':
                        quantity = -1 * quantity

                bal = quantity * value
                running_bal += bal
                
                # TODO: this needs to change to allow quantities and values
                entry_dtos.append(
                    TransactionModel(
                        id = row['tx_id'],
                        date = row['date'],
                        type = row['split_type_name'],
                        account = row['acct_name'],
                        description = row['description'],
                        value = quantity,
                        balance = running_bal
                    )
                )
        
        return entry_dtos

class GetUncategorizedTransactionsQuery:
    def execute(self, account_id: UUID) -> list[UncategorizedTransaction]:
        uncat_transactions = []

        with engine.connect() as con:

            d = {'account_id': account_id}
                        
            statement = text("""SELECT uncategorized_transaction.id AS id, date, account_id, description, split_type.name as split_name, quantity FROM uncategorized_transaction
            JOIN split_type ON type_id = split_type.id
            WHERE account_id = :account_id;
            """)

            rs = con.execute(statement, d)

            for row in rs:
                uncat_tx = UncategorizedTransaction(row['id'], row['date'], row['account_id'], row['description'], row['split_name'], row['quantity'])
                print(row)
                uncat_transactions.append(uncat_tx)

        return uncat_transactions