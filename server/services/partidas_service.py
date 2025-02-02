from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from server.db.connection import Partida, PartidaVideos, get_db_session

def criar_partida(codigo, pagamento, data_inicio, data_fim=None):
    with get_db_session() as session:
        nova_partida = Partida(
            codigo=codigo,
            pagamento=pagamento,
            data_inicio=data_inicio,
            data_fim=data_fim,
            quadra=1,
            ativa=True
        )
        session.add(nova_partida)
        session.commit()  
        return nova_partida.id

def adicionar_video(partida_id, path, thumbnail, created_at=None):
    created_at = created_at or datetime.now()
    with get_db_session() as session:
        novo_video = PartidaVideos(
            partida_id=partida_id,
            path=path,
            thumbnail=thumbnail,
            created_at=created_at
        )
        session.add(novo_video)
        session.commit()

def finalizar_partida(partida_id, data_fim=None):
    data_fim = data_fim or datetime.now()
    with get_db_session() as session:
        partida = session.query(Partida).filter_by(id=partida_id).first()
        if partida:
            partida.data_fim = data_fim
            partida.ativa = False
            session.commit()
        else:
            raise ValueError("Partida não encontrada.")

def salvar_partida(partida):
    with get_db_session():
        nova_partida_id = criar_partida(
            codigo=partida["codigo"],
            pagamento=partida["pagamento"],
            data_inicio=partida["data_inicio"],
            data_fim=partida.get("data_fim")
        )
        return nova_partida_id
    
def salvar_video(partida_id, path, thumbnail, created_at):
    with get_db_session() as session:
        novo_video = PartidaVideos(
            partida_id=partida_id,
            path=path,
            thumbnail=thumbnail,
            created_at=created_at,
            pagamento=False
        )
        session.add(novo_video)
        session.commit()
    
def pegar_partida(codigo):
    with get_db_session() as session:
        partida = session.query(Partida).filter_by(codigo=codigo).first()
        
        if partida:
            return partida
        
        raise ValueError("Partida não encontrada com o código fornecido.")
    

def pegar_jogadas_por_partida(partida_id):
    with get_db_session() as session:
        partida = session.query(Partida).filter_by(id=partida_id).first()
        if not partida:
            raise ValueError("Partida não encontrada.")
        
        if not partida.pagamento:
            raise ValueError("Pagamento não realizado para esta partida.")
        
        videos = session.query(PartidaVideos).filter_by(partida_id=partida_id).all()
        if videos:
            return [
                {
                    'id': video.id,
                    'partida_id': video.partida_id,
                    'path': video.path,
                    'created_at': video.created_at,
                    'thumbnail': video.thumbnail,
                    'pagamento': video.pagamento
                } for video in videos
            ]
        else:
            raise ValueError("Jogadas para a partida não encontradas.")