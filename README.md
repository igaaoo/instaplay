# Instaplay

Sistema de detecção de gestos em tempo real para jogos multiplayer. Quando um ou mais jogadores levantam os dois braços por 2 segundos, o sistema salva automaticamente os últimos 30 segundos de vídeo com marca d'água e registra no banco de dados.

## Como funciona

1. A câmera captura o vídeo continuamente em uma thread dedicada
2. YOLOv8 detecta a pose de todas as pessoas no frame em outra thread
3. Quando alguém mantém **os dois braços levantados por 2 segundos**, o gesto é confirmado
4. O sistema toca um som, salva o clipe e registra no banco
5. A API Flask permite buscar os vídeos pelo código da partida

## Estrutura do projeto

```
instaplay/
├── app.py                      # Loop principal + orquestração das threads
├── config.py                   # Constantes (FPS, buffer, resolução, paths)
├── camera/
│   ├── camera.py               # Captura de vídeo em thread dedicada
│   ├── detector.py             # Inferência YOLOv8 em thread dedicada
│   └── pose_utils.py           # Lógica de detecção de braços levantados
├── processing/
│   ├── bufferManager.py        # Buffer circular de 30 segundos
│   └── videoSaver.py           # Exporta vídeo do buffer com marca d'água
├── server/
│   ├── server.py               # API Flask
│   ├── db/connection.py        # Conexão PostgreSQL + modelos ORM
│   └── services/
│       └── partidas_service.py # Regras de negócio (partidas e vídeos)
├── static/
│   ├── logo.png                # Marca d'água aplicada nos vídeos
│   ├── start.mp3               # Som ao iniciar a partida
│   ├── replay.mp3              # Som ao detectar o gesto
│   └── videos/                 # Vídeos gerados
├── docker-compose.yaml         # PostgreSQL
├── init.sql                    # Schema do banco
└── requirements.txt
```

## Pré-requisitos

- Python 3.10+
- Docker Desktop

## Instalação

```bash
# 1. Subir o banco de dados
docker-compose up -d

# 2. Instalar dependências Python
pip install -r requirements.txt
```

Na primeira execução o modelo YOLOv8 (~6 MB) é baixado automaticamente.

## Configuração da câmera

Em `app.py`, linha 43, altere o `source` conforme sua câmera:

| Fonte | Valor |
|---|---|
| Webcam local | `0` |
| IP Cam (DroidCam, iVCam) | `'http://192.168.x.x:4747/video'` |
| RTSP | `'rtsp://usuario:senha@192.168.x.x:554/stream'` |

## Execução

```bash
python app.py
```

O terminal exibe o código da partida ao iniciar:

```
Partida iniciada | Codigo: a3f2c1d4e5b6...
```

O mesmo código aparece na janela de preview. Para encerrar, pressione `q` na janela.

## Detecção de gesto

- Keypoints utilizados: ombros (5, 6) e pulsos (9, 10) — formato COCO
- Condição: `pulso.y < ombro.y` para **ambos** os braços simultaneamente
- Tempo mínimo sustentado: **2 segundos**
- Cooldown entre detecções: **5 segundos**

## API

Base URL: `http://localhost:5000`

### Buscar partida e vídeos

```
GET /partida/<codigo>
```

Resposta:
```json
{
  "id": "uuid",
  "codigo": "a3f2c1d4...",
  "pagamento": false,
  "data_inicio": "2025-01-01T10:00:00",
  "data_fim": null,
  "jogadas": [
    {
      "id": "uuid",
      "partida_id": "uuid",
      "path": "20250101100500-uuid.mp4",
      "thumbnail": "base64...",
      "created_at": "2025-01-01T10:05:00"
    }
  ]
}
```

### Baixar vídeo

```
GET /partida/video/<filename>
```

## Banco de dados

| Tabela | Descrição |
|---|---|
| `partida` | Sessão de jogo (código, data início/fim, pagamento) |
| `partida_videos` | Clipes gerados (path, thumbnail base64, timestamp) |

## Performance

| Técnica | Efeito |
|---|---|
| `yolov8n-pose` (nano) | Modelo mais leve da família YOLOv8 |
| Resize para 640px antes da inferência | Reduz custo ~4× vs resolução original |
| `skip_frames=2` | Inferência a cada 2 frames |
| Thread de captura separada | Câmera nunca bloqueia o loop principal |
| Fila de 1 slot no detector | Sempre processa o frame mais recente |
