from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from db_params import SCHEMA, DBNAME, DBUSER, DBPASSWORD, PORT, DBADDRESS

POSTGRES_DATABASE_URL = fr"postgresql://{DBUSER}:{DBPASSWORD}@{DBADDRESS}/{DBNAME}"  # NEEDS TO BE DEFINED!

engine = create_engine(
    POSTGRES_DATABASE_URL,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.schema = 'public'