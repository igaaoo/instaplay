from flask import Flask, send_file
from config import VIDEO_PATH

app = Flask(__name__)

@app.route('/jogada')
def download_video():
    return send_file(VIDEO_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
