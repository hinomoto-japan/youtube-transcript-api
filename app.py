from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re, os

app = Flask(__name__)

@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.json
    url = data.get('url', '')

    match = re.search(r'(?:v=|youtu\.be/)([^&\n?#]+)', url)
    if not match:
                return jsonify({'error': 'URLが無効です'}), 400

    video_id = match.group(1)

    try:
                ytt_api = YouTubeTranscriptApi()
                transcript_list = ytt_api.fetch(video_id, languages=['ja', 'ja-Hant', 'en'])
                text = ' '.join([entry.text for entry in transcript_list])
                return jsonify({'transcript': text, 'video_id': video_id})
    except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
