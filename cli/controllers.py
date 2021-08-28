from plutus.account.queries import GetAccountsQuery
from ofxparse.ofxparse import OfxParser

class TransactionLoaderController:

    def load(self, for_account_id: int, file_name: str):
        transactions = []
        with open(file_name) as fileobj:
            ofx = OfxParser.parse(fileobj)
            transactions = ofx.account.statement.transactions
                
        accounts = GetAccountsQuery().execute()

        for transaction in transactions:        
            print(transaction.date, transaction.payee, transaction.type, transaction.amount)

        #transactions = self._trans_repo.find(transaction.payee)

                # possible_account_id = None
                # for trans in transactions:
                #     for split in trans.splits:
                #         if split.account_id != for_account_id:
                #             possible_account_id = split.account_id
                #             break

                # if possible_account_id != None:
                #     CreateTransactionCommand(self._trans_repo, self._session).execute(transaction.date, possible_account_id, for_account_id, transaction.payee, abs(transaction.amount))
                # else:
                #     name = prompt_view(transaction.payee)

                #     account_found = self._account_repo.find_by_name(name)

                #     if (account_found.name == name):
                #         CreateTransactionCommand(self._trans_repo, self._session).execute(transaction.date, account_found.id, for_account_id, transaction.payee, abs(transaction.amount))
                #     else:
                #         resp = prompt_view_account(account_found.name)
                #         print(resp)

                #         if resp == True:
                #             CreateTransactionCommand(self._trans_repo, self._session).execute(transaction.date, account_found.id, for_account_id, transaction.payee, abs(transaction.amount))