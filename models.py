from datetime import datetime

from sqlalchemy import Integer, create_engine, Column, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///impurity_db.db", echo=True, future=True)
Session = sessionmaker(engine)
Base = declarative_base()


class Impurity(Base):
    __tablename__ = 'impurity'

    id = Column(Integer, primary_key=True)
    reference = Column(Text, nullable=True)
    version = Column(Text, nullable=True)
    api_name = Column(Text, nullable=True)
    impurity_name = Column(Text, nullable=True)
    raw_chemical_name = Column(Text, nullable=True)
    chemical_name = Column(Text, nullable=True)
    synonyms = Column(Text, nullable=True)
    smiles = Column(Text, nullable=True)
    modified_at = Column(DateTime, nullable=True, default=datetime.now)
    created_at = Column(DateTime, nullable=True, default=datetime.now, server_default='CURRENT_TIMESTAMP')


if __name__ == '__main__':
    Base.metadata.create_all(engine)
