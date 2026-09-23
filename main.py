import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json()
    url = data.get('url') if data else None

    if not url:
        return jsonify({'error': 'Por favor ingresa una URL válida.'}), 400

    try:
        # Petición a servicio externo de extracción universal sin costo
        api_url = f"https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "vCodec": "h264"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        res_data = response.json()

        if response.status_code == 200 and "url" in res_data:
            return jsonify({
                'success': True,
                'title': 'Video listo para descargar',
                'download_url': res_data['url']
            })
        else:
            return jsonify({'error': 'No se pudo obtener el video de este enlace. Verifica que sea público.'}), 400

    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
