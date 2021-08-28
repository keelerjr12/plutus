from datetime import date
from decimal import Decimal

from plutus.split import Split
from plutus.account import Account, AccountType
from plutus.transaction import Transaction
import pytest

######### ACCOUNT #########

def test_empty_account_has_zero_balance():
    account = Account(1, "test", AccountType.ASSET)

    balance = account.balance()

    assert balance == 0

def test_debit_asset_account_with_single_split_has_balance_equal_split():
    split = Split(1, 1, 'TestSplit', 'Debit', Decimal('1.69'))
    splits = [split]
    account = Account(id=1, name='test', type = AccountType.ASSET, splits=splits)

    balance = account.balance()

    assert balance == Decimal('1.69')

def test_debit_asset_account_with_multiple_splits_has_balance_equal_splits():
    split_1 = Split(1, 1, 'TestSplit1', 'Debit', Decimal('1.69'))
    split_2 = Split(1, 2, 'TestSplit2', 'Debit', Decimal('3.69'))
    splits = [split_1, split_2]
    account = Account(id=1, name='test', type = AccountType.ASSET, splits=splits)

    balance = account.balance()

    assert balance == Decimal('5.38')

def test_credit_asset_account_with_single_split_has_balance_equal_opposite_split():
    split = Split(1, 1, 'TestSplit', 'Credit', Decimal('1.69'))
    splits = [split]
    account = Account(id=1, name='test', type = AccountType.ASSET, splits=splits)

    balance = account.balance()

    assert balance == Decimal('-1.69')

def test_debit_liability_account_with_single_split_has_balance_equal_opposite_split():
    split = Split(1, 1, 'TestSplit', 'Debit', Decimal('1.69'))
    splits = [split]
    account = Account(id=1, name='test', type = AccountType.LIABILITY, splits=splits)

    balance = account.balance()

    assert balance == Decimal('-1.69')

def test_credit_liability_account_with_single_split_has_balance_equal_split():
    split = Split(1, 1, 'TestSplit', 'Credit', Decimal('1.69'))
    splits = [split]
    account = Account(id=1, name='test', type = AccountType.LIABILITY, splits=splits)

    balance = account.balance()

    assert balance == Decimal('1.69')

######### TRANSACTION #########

def test_transaction_imbalanced_with_two_credits_raises_exception():
    split_1 = Split(1, 1, 'Split1', 'Credit', Decimal('10'))
    split_2 = Split(1, 1, 'Split2', 'Credit', Decimal('10'))

    with pytest.raises(Exception):
        transaction = Transaction(1, date.today(), [split_1, split_2])

def test_transaction_imbalanced_with_two_different_amounts_raises_exception():
    split_1 = Split(1, 1, 'Split1', 'Credit', Decimal('10'))
    split_2 = Split(1, 1, 'Split2', 'Debit', Decimal('1'))

    with pytest.raises(Exception):
        transaction = Transaction(1, date.today(), [split_1, split_2])

def test_transaction_balanced_does_not_raise_exception():
    split_1 = Split(1, 1, 'Split1', 'Credit', Decimal('10'))
    split_2 = Split(1, 1, 'Split2', 'Debit', Decimal('10'))

    transaction = Transaction(1, date.today(), [split_1, split_2])