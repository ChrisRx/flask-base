import datetime

from flask_sqlalchemy import BaseQuery as _BaseQuery

from .ext import db
from .utils import tokenizer

class BaseQuery(_BaseQuery):
    """
    Using this proxy to add default methods to BaseQuery. This allows
    for each model using query_class to have the following partial
    string search implmentation.
    """
    def search(self, query):
        tokens = tokenizer(query)
        search_vectors = [search_column.like("%{0}%".format(token)) for \
            search_column in self._mapper_zero().class_.search_columns() for \
            token in tokens]
        return self.filter(db.or_(*search_vectors)).all()

    def json(self):
        return [item.json for item in self.all()]


class Model(db.Model):
    """
    Abstract extension of Flask-SQLAlchemy declarative base providing
    additional methods
    """

    __abstract__ = True

    # Define fields searchable via query.search()
    __searchable__ = []

    query_class = BaseQuery

    @classmethod
    def search_columns(cls):
        """
        Lists searchable columns declared in __searchable__
        """
        if not getattr(cls, '__searchable__'):
            return []
        return [getattr(cls, column_name) for column_name in \
            cls.__searchable__]

    @property
    def json(self):
        convert = {}
        d = {}
        for c in self.__class__.__table__.columns:
            v = getattr(self, c.name)
            # Fixes bug with serialization of datetime.date
            if isinstance(v, datetime.date):
                v = datetime.datetime.combine(v, datetime.datetime.min.time())
            if c.type in convert.keys() and v is not None:
                try:
                    d[c.name] = convert[c.type](v)
                except:
                    d[c.name] = "Error:  Failed to covert using {0}".format(str(convert[c.type]))
            elif v is None:
                d[c.name] = str()
            else:
                d[c.name] = v
        return d

    def __repr__(self):
        return "<{0}>".format(self.__class__.__name__)
