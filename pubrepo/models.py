# -*- coding: utf-8 -*-
import hashlib
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=False)
    content = Column(Integer)

    def __init__(self, title, content):
        self.title = title
        self.content = content


class Resource(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=False)
    data = Column(LargeBinary)
    hash = Column(String, nullable=False)
    mimetype = Column(String)

    module_id = Column(Integer, ForeignKey('modules.id'))
    module = relationship("Module", backref="resources")

    def __init__(self, filename, data, module_or_module_id):
        self.filename = filename
        try:
            self.data = data.read()
        except AttributeError:
            self.data = data
        self.hash = hashlib.sha1(self.data).hexdigest()
        # TODO Do mimetype discovery.
        if isinstance(module_or_module_id, Module):
            self.module_id = module_or_module_id.id
        else:
            self.module_id = module_or_module_id
