from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import tempfile, os, uuid, subprocess, threading, time
import yt_dlp

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'imports'; OUT.mkdir(exist_ok=True)
app=Flask(__name__, static_folder=str(ROOT), static_url_path='')
ALLOWED=('youtube.com','www.youtube.com','m.youtube.com','youtu.be','www.tiktok.com','tiktok.com','vm.tiktok.com','vt.tiktok.com')

def allowed(url):
    from urllib.parse import urlparse
    h=(urlparse(url).hostname or '').lower().rstrip('.')
    return any(h==x or h.endswith('.'+x) for x in ALLOWED)

def clean_old():
    now=time.time()
    for p in OUT.glob('*'):
        try:
            if now-p.stat().st_mtime>1800:p.unlink()
        except:pass

@app.get('/')
def index(): return send_from_directory(ROOT,'index.html')

@app.post('/api/import')
def imp():
    clean_old(); data=request.get_json(silent=True) or {}; url=str(data.get('url','')).strip()
    if not url or not allowed(url): return jsonify(error='Link harus YouTube/TikTok yang didukung.'),400
    token=uuid.uuid4().hex; base=OUT/token
    try:
        opts={
          'format':'bestaudio/best','outtmpl':str(base)+'.%(ext)s','noplaylist':True,
          'quiet':True,'no_warnings':True,'restrictfilenames':True,
          'postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'wav'}],
          'socket_timeout':20,'retries':2,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info=ydl.extract_info(url,download=True)
            title=info.get('title') or 'Imported Audio'
        wav=base.with_suffix('.wav')
        if not wav.exists():
            return jsonify(error='FFmpeg tidak menghasilkan WAV. Pastikan FFmpeg terpasang.'),500
        return jsonify(title=title,url=f'/imports/{wav.name}')
    except Exception as e:
        for p in OUT.glob(token+'.*'):
            try:p.unlink()
            except:pass
        return jsonify(error='Import gagal: '+str(e)[:500]),500

@app.get('/imports/<name>')
def imported(name):
    return send_from_directory(OUT,name,as_attachment=False,max_age=0)

if __name__=='__main__':
    print('RENSTUDIO AUDIO EDITOR V4 → http://127.0.0.1:8787')
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT','8787')),threaded=True)
