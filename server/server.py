from flask import Flask, jsonify, send_file

from services.partidas_service import pegar_jogadas_por_partida, pegar_partida

app = Flask(__name__)

@app.route('/jogada')
def download_video():
    return "send_file(VIDEO_PATH, as_attachment=True)"

@app.route('/partida/<codigo>', methods=['GET'])
def obter_partida(codigo):
    try:
        partida = pegar_partida(codigo)
        if partida:
            return jsonify({
                'id': partida.id,
                'codigo': partida.codigo,
                'pagamento': partida.pagamento,
                'data_inicio': partida.data_inicio,
                'data_fim': partida.data_fim
            }), 200
        else:
            return jsonify({'message': 'Partida não encontrada'}), 404
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

@app.route('/partida/<partida_id>/jogadas', methods=['GET'])
def obter_jogadas_por_partida(partida_id):
    try:
        jogadas = pegar_jogadas_por_partida(partida_id)
        if jogadas:
            return jsonify(jogadas), 200
        else:
            return jsonify({'message': 'Jogadas para a partida não encontradas'}), 404
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
