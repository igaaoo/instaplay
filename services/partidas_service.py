from datetime import datetime

from db.connection import Partida, PartidaVideos, get_db_session

def criar_partida(codigo, pagamento, data_inicio, data_fim=None):
    with get_db_session() as session:
        nova_partida = Partida(
            codigo=codigo,
            pagamento=pagamento,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        session.add(nova_partida)
        session.commit()  # Salva a partida para gerar o ID
        return nova_partida.id

def adicionar_video(partida_id, path, created_at=None):
    created_at = created_at or datetime.now()
    with get_db_session() as session:
        novo_video = PartidaVideos(
            partida_id=partida_id,
            path=path,
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
            session.commit()
        else:
            raise ValueError("Partida não encontrada.")

def salvar_partida_com_videos(partida):
    with get_db_session():
        nova_partida_id = criar_partida(
            codigo=partida["codigo"],
            pagamento=partida["pagamento"],
            data_inicio=partida["data_inicio"],
            data_fim=partida.get("data_fim")
        )

        for video in partida["videos"]:
            adicionar_video(
                partida_id=nova_partida_id,
                path=video["path"],
                created_at=video["created_at"]
            )

        return nova_partida_id