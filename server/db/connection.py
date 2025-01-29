from sqlalchemy import create_engine, Column, String, UUID, TIMESTAMP, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

# Configuração do banco de dados
DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{db}".format(
    user="teste",
    password="teste%40123",
    host="localhost",
    port="5432",
    db="instaplay"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={'options': '-c client_encoding=utf8'}
)

# Criando a engine e a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Partida(Base):
    __tablename__ = 'partida'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(50), nullable=False)
    pagamento = Column(Boolean)
    data_inicio = Column(TIMESTAMP, nullable=False)
    data_fim = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class PartidaVideos(Base):
    __tablename__ = 'partida_videos'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partida_id = Column(UUID(as_uuid=True), nullable=False)
    path = Column(String(255), nullable=False)
    thumbnail = Column(String, nullable=True)  # Nova coluna para armazenar a imagem em Base64
    created_at = Column(TIMESTAMP, server_default=func.now())

# Base.metadata.create_all(bind=engine)

def get_db_session():
    db = SessionLocal()
    return db
