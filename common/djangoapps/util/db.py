"""
Utility functions related to databases.
"""
from functools import wraps
import random

from django.db import DEFAULT_DB_ALIAS, DatabaseError, Error, transaction


MYSQL_MAX_INT = (2 ** 31) - 1


class CommitOnSuccessManager(object):

    ENABLED = True

    def __init__(self, using, read_committed=False):
        self.using = using
        self.read_committed = read_committed

    def __enter__(self):

        if not self.ENABLED:
            return

        connection = transaction.get_connection(self.using)

        if connection.in_atomic_block:
            raise transaction.TransactionManagementError('Cannot be inside an atomic block.')

        if getattr(connection, 'commit_on_success_block_level', 0) == 0:
            connection.commit_on_success_block_level = 1

            # This will set the transaction isolation level to READ COMMITTED for the next transaction.
            if self.read_committed is True:
                if connection.vendor == 'mysql':
                    cursor = connection.cursor()
                    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")

            # We aren't in a transaction yet; create one.
            # The usual way to start a transaction is to turn autocommit off.
            # However, some database adapters (namely sqlite3) don't handle
            # transactions and savepoints properly when autocommit is off.
            # In such cases, start an explicit transaction instead, which has
            # the side-effect of disabling autocommit.
            if connection.features.autocommits_when_autocommit_is_off:
                connection._start_transaction_under_autocommit()
                connection.autocommit = False
            else:
                connection.set_autocommit(False)
        else:
            connection.commit_on_success_block_level += 1

    def __exit__(self, exc_type, exc_value, traceback):

        if not self.ENABLED:
            return

        connection = transaction.get_connection(self.using)

        try:
            if exc_type is None:
                # Commit transaction
                try:
                    connection.commit()
                except DatabaseError:
                    try:
                        connection.rollback()
                    except Error:
                        # An error during rollback means that something
                        # went wrong with the connection. Drop it.
                        connection.close()
                    raise
            else:
                # Roll back transaction
                try:
                    connection.rollback()
                except Error:
                    # An error during rollback means that something
                    # went wrong with the connection. Drop it.
                    connection.close()

        finally:
            connection.commit_on_success_block_level -= 1

            # Outermost block exit when autocommit was enabled.
            if connection.commit_on_success_block_level == 0:
                if connection.features.autocommits_when_autocommit_is_off:
                    connection.autocommit = True
                else:
                    connection.set_autocommit(True)

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwds):
            with self:
                return func(*args, **kwds)
        return decorated


def commit_on_success(using=None, read_committed=False):
    """
    Decorator which executes the decorated function inside a transaction with isolation level set to READ COMMITTED.

    If the function returns a response the transaction is committed and if the function raises an exception the
    transaction is rolled back.

    Raises TransactionManagementError if there is already a transaction open.

    Note: This only works on MySQL.
    """
    if callable(using):
        return CommitOnSuccessManager(DEFAULT_DB_ALIAS, read_committed)(using)
    # Decorator: @commit_on_success(...) or context manager: with commit_on_success(...): ...
    else:
        return CommitOnSuccessManager(using, read_committed)

def commit_on_success_with_read_committed(using):
    return commit_on_success(using, True)


def generate_int_id(minimum=0, maximum=MYSQL_MAX_INT, used_ids=None):
    """
    Return a unique integer in the range [minimum, maximum], inclusive.
    """
    if used_ids is None:
        used_ids = []

    cid = random.randint(minimum, maximum)

    while cid in used_ids:
        cid = random.randint(minimum, maximum)

    return cid
