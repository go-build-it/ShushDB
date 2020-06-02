"""
Provides a str->object store.

Uses LMDB and capn proto.
"""
import collections.abc
import contextlib
import platform

import lmdb


if platform.architecture()[0] == '64bit':
    DEFAULT_MAP = 1024 * 1024 * 1024 * 1024
    # 1TB "On 64-bit there is no penalty for making this huge (say 1TB)"
else:
    DEFAULT_MAP = 10 * 1024 * 1024  # 10MB


class Database(collections.abc.Mapping):
    def __init__(self, handle, txn, struct):
        self._db = handle
        self._txn = txtn
        self._struct = struct

    def __iter__(self):
        with self._txn.cursor(self._db) as cursor:
            for item, _ in cursor:
                yield item

    def __len__(self):
        return self._txn.stat(self._db)['entries']

    def __getitem__(self, key):
        default = object()
        blob = self._txn.get(key, default=default, db=self._db)
        if blob is default:
            raise KeyError(f"Could not find key {key!r}")  # TODO: Database name
        return self._struct.from_bytes(blob)

    # TODO: Cursor


class WritableDatabase(Database, collections.abc.MutableMapping):
    def __setitem__(self, key, value):
        assert isinstance(value, self._struct)
        blob = value.to_bytes()
        self._txn.replace(key, blob, db=self._db)

    def __delitem__(self, key):
        self._txn.delete(key, db=self._db)

    def prune(self):
        """
        Empty the database
        """
        self._txn.drop(self._db, delete=False)


class Transaction(collections.abc.Mapping):
    _db_class: type

    def __init__(self, txn, odb):
        self._txn = _txn
        self._db = odb

    def __iter__(self):
        yield from self._db.schema

    def __len__(self):
        return len(self._db.schema)

    def __getitem__(self, key):
        db = self._db.open_db(key, self._txn)
        return self._db_class(db, self._txn, self._db.schema[key])


class ReadingTransaction(Transaction):
    _db_class = Database


class WritingTransaction(Transaction):
    _db_class = WritingDatabase


class ObjectDB:
    """
    The root object to access a database with.

    Is a context manager for resource cleanup.

    Use the .for_reading() and .for_writing() methods to start transactions.
    """
    def __init__(self, path, schema, *, subdir=True, map_size=DEFAULT_MAP, **opts):
        """
        Takes the same arguments as lmdb.Environment, although some defaults
        have changed.

        Schema maps the name of the database to the capn proto struct that it uses
        to store data.
        """
        self.environ = lmdb.Environment(
            path, map_size=map_size, subdir=subdir, max_dbs=len(schema), **opts
        )

        self.schema = schema

        self._init_dbs()

        self.environ.reader_check()

    def _init_dbs(self):
        """
        Do initial named database creation, so we can assertively know them later.
        """
        for dbname in self.schema.keys():
            db = self.environ.open_db(dbname, create=True)
            # There isn't a call to free this opaque handle, so I guess we'll
            # just let it float off
            # (To be fair, it'll get reused)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.environ.close()

    @contextlib.contextmanager
    def for_reading(self) -> ReadingTransaction:
        # TODO: Parent transactions
        with lmdb.Transaction(self.environ) as tx:
            yield ReadingTransaction(self, tx)

    @contextlib.contextmanager
    def for_writing(self) -> WritingTransaction:
        # TODO: Parent transactions
        with lmdb.Transaction(self.environ) as tx:
            yield WritingTransaction(self, tx)
