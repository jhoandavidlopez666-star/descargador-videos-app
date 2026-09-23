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
        # Resolver redirecciones de links cortos (vt.tiktok.com, etc.)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        session = requests.Session()
        res_redirect = session.get(url, headers=headers, allow_redirects=True, timeout=8)
        clean_url = res_redirect.url if res_redirect.url else url

        # Petición a la API pública de extracción
        cobalt_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        payload = {
            "url": clean_url,
            "vCodec": "h264"
        }

        response = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=cobalt_headers)
        res_data = response.json()

        if response.status_code == 200 and "url" in res_data:
            return jsonify({
                'success': True,
                'title': '¡Video listo!',
                'download_url': res_data['url']
            })
        elif "picker" in res_data and len(res_data["picker"]) > 0:
            return jsonify({
                'success': True,
                'title': '¡Video listo!',
                'download_url': res_data["picker"][0]["url"]
            })
        else:
            return jsonify({'error': 'No se pudo obtener el enlace. Asegúrate de que el video sea público.'}), 400

    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
