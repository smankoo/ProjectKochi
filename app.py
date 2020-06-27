from __future__ import unicode_literals
import youtube_dl
import uuid
import os
import json
import sys
import time
import shutil
from flask import Flask, render_template, request, redirect, send_from_directory

with open('config.json', 'r') as config_file:
    data=config_file.read()

config = json.loads(data)

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
        cleanup()
        return(render_template('index.html'))
    elif request.method == 'POST':

        url = request.form['url']
        if url == "":
            return(render_template('index.html'))

        download_parent = config['download_dir']
        cachedir = config['cache_dir']
        tmpdir = uuid.uuid4().hex

        downloaddir = download_parent + '/' + tmpdir

        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

        if not os.path.exists(downloaddir):
            os.mkdir(downloaddir)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'outtmpl': downloaddir + '/%(title)s.%(ext)s',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if len(os.listdir(downloaddir)) == 1:
            file_name = os.listdir(downloaddir)[0]
            return send_from_directory(downloaddir, file_name, as_attachment = True)

@app.route('/cleanup')
def cleanup():
    download_parent = config['download_dir']
    if not os.path.isdir(download_parent):
        return([])
    delete_list = []
    for file_name in os.listdir(download_parent):
        # delete directories older than 2 minutes
        d = os.path.join(download_parent, file_name)
        if file_name != config['cache_dir'] \
         and os.path.isdir(d)       \
         and os.stat(d).st_mtime < (time.time() - (2*60)):
            delete_list.append(d)
            shutil.rmtree(d)

    return(json.dumps(delete_list))


if __name__ == '__main__':
    app.run(debug=True)