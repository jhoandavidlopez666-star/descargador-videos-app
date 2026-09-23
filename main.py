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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # 1. Si es TikTok (acepta enlaces cortos vt.tiktok.com y enlaces completos)
        if "tiktok.com" in url:
            tikwm_url = f"https://www.tikwm.com/api/?url={url}"
            res = requests.get(tikwm_url, headers=headers, timeout=10)
            res_json = res.json()

            if res_json.get("code") == 0 and "data" in res_json:
                # Video sin marca de agua
                video_url = res_json["data"].get("play")
                if video_url and not video_url.startswith("http"):
                    video_url = "https://www.tikwm.com" + video_url

                return jsonify({
                    'success': True,
                    'title': res_json["data"].get("title", "Video de TikTok"),
                    'download_url': video_url
                })

        # 2. Respaldo multi-plataforma (Cobalt con headers de API v10)
        cobalt_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        payload = {
            "url": url,
            "vCodec": "h264"
        }

        res_cobalt = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=cobalt_headers, timeout=12)
        
        if res_cobalt.status_code == 200:
            c_data = res_cobalt.json()
            download_link = c_data.get("url") or (c_data.get("picker")[0]["url"] if c_data.get("picker") else None)
            
            if download_link:
                return jsonify({
                    'success': True,
                    'title': 'Video listo para descargar',
                    'download_url': download_link
                })

        return jsonify({'error': 'No se pudo obtener el enlace. Asegúrate de que el video sea público.'}), 400

    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
