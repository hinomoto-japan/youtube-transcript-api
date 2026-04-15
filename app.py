from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re, os, tempfile, base64

app = Flask(__name__)

@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.json
    url = data.get('url', '')
    match = re.search(r'(?:v=|youtu\.be/)([^&\n?#]+)', url)
    if not match:
        return jsonify({'error': 'URLが無効です'}), 400
    video_id = match.group(1)
    cookies_path = None
    try:
        cookies_b64 = os.environ.get('YOUTUBE_COOKIES_B64')
        if cookies_b64:
            cookies_content = base64.b64decode(cookies_b64).decode('utf-8')
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(cookies_content)
                cookies_path = f.name
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookies_path)
        else:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['ja', 'ja-Hant', 'en'])
        fetched = transcript.fetch()
        text = ' '.join([entry['text'] for entry in fetched])
        return jsonify({'transcript': text, 'video_id': video_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cookies_path and os.path.exists(cookies_path):
            os.unlink(cookies_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
