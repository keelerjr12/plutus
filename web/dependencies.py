from data.transaction import SqlTransactionRepository, SqlUncategorizedTransactionRepository
from data.account import SqlAccountRepository
from data.database import SessionLocal

session = SessionLocal()
account_repo = SqlAccountRepository(session)
trans_repo = SqlTransactionRepository(session)
uncat_trans_repo = SqlUncategorizedTransactionRepository(session)