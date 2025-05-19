import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from dotenv import load_dotenv
from msprbloc4.client.models.models import Base


load_dotenv()

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def init_db():
    Base.metadata.create_all(bind=engine)