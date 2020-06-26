from __future__ import unicode_literals
import youtube_dl

from flask import Flask, render_template, request, redirect


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'GET':
        return(render_template('index.html'))
    elif request.method == 'POST':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])

        return(request.form['url'])
    

if __name__ == '__main__':
    app.run(debug=True)