import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # Permite peticiones desde la web de Vercel

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json()
    url = data.get('url') if data else None

    if not url:
        return jsonify({'error': 'URL no proporcionada'}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'Video sin titulo')

            return jsonify({
                'success': True,
                'title': title,
                'download_url': video_url
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
