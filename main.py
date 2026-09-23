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
        # Resolver redirecciones para enlaces cortos como vt.tiktok.com o youtu.be
        session = requests.Session()
        res_redirect = session.head(url, allow_redirects=True, timeout=5)
        final_url = res_redirect.url if res_redirect.url else url

        # Petición a la API de Cobalt
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": final_url,
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
        elif "picker" in res_data:
            # En caso de que sea un carrusel de imágenes o varias opciones
            first_media = res_data["picker"][0]["url"]
            return jsonify({
                'success': True,
                'title': 'Contenido listo para descargar',
                'download_url': first_media
            })
        else:
            return jsonify({'error': 'No se pudo obtener el video de este enlace. Verifica que sea público.'}), 400

    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
