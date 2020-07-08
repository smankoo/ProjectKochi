from __future__ import unicode_literals
import youtube_dl
import uuid
import os
import json
import sys
import time
import shutil
import datetime

from flask import Flask, render_template, request, redirect, send_from_directory, url_for, Response, jsonify

import time
import atexit
from slugify import slugify


my_path = os.path.abspath(os.path.dirname(__file__))
config_loc = os.path.join(my_path, "../config.json")

with open(config_loc, 'r') as config_file:
    data = config_file.read()

config = json.loads(data)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/', methods=['POST', 'GET'])
    def index():
        return(render_template('index.html'))

    @app.route('/test')
    def test():
        return render_template('test.html')

    @app.route('/_download/<string:req_type>', methods=['GET', 'POST'])
    def download(req_type="single"):
        download_parent = config['download_dir']
        cachedir = config['cache_dir']
        downloadid = uuid.uuid4().hex


        downloaddir = download_parent + '/' + downloadid

        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

        if not os.path.exists(downloaddir):
            os.makedirs(downloaddir)

        if request.method == 'GET':
            
            if req_type.lower() == "single":
                url = request.args.get('url')

                if url is None or url == "":
                    return jsonify({"error":"empty URL passed"})

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
                    ydl_info = ydl.extract_info(url, download=False)

                if len(os.listdir(downloaddir)) == 1:
                    return jsonify({"downloadid": downloadid, "ydl_info": ydl_info})
                else:
                    raise "Invalid number of files in downloaddir"

        elif request.method == 'POST':
            if req_type.lower() == "list":
                # data = json.loads(request.data)
                # data = data['{"list_name":"Raavan","list_items":["https://www.youtube.com/watch?v']
                data = request.json
                list_name = data['list_name']
                list_items = data['list_items']

                list_name = slugify(list_name, separator=' ', lowercase=False) # make name file system and URL safe
                

                list_download_dir = os.path.join(downloaddir, list_name)

                if not os.path.exists(list_download_dir):
                    os.makedirs(list_download_dir)

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                    'logger': MyLogger(),
                    'progress_hooks': [my_hook],
                    'outtmpl': list_download_dir + '/%(title)s.%(ext)s',
                }

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download(list_items)

                # if len(os.listdir(downloaddir)) == 1:
                #     return jsonify({"downloadid": downloadid, "ydl_info": ydl_info})


                zip_file_name = slugify(list_name) + ".zip"
                zip_file_path = os.path.join(downloaddir, zip_file_name)
                # shutil.make_archive(zip_file_path, 'zip', downloaddir, zip_file_name)
                
                make_archive(list_download_dir, zip_file_path)
                shutil.rmtree(list_download_dir)
                

                return jsonify({"downloadid": downloadid, "filename": zip_file_name})

            else:
                print("Bad type : " + req_type)
                
                return jsonify({"error":"something went wrong!"})


    @app.route('/getfile')
    def get_file():
        downloadid = request.args.get('downloadid')
        downloaddir = os.path.join(config['download_dir'], downloadid)
        if len(os.listdir(downloaddir)) == 1:
            file_name = os.listdir(downloaddir)[0]
            return send_from_directory(downloaddir, file_name, as_attachment=True)

    def my_hook(d):
        # download_perc = round(d['downloaded_bytes']*100 / d['total_bytes'])
        # if download_perc > 30:
        #     print("download_perc:" + download_perc)
        pass

    @app.route('/_getprogress')
    def progress():
        download_perc = 0
        data = "perc:" + str(download_perc) + "\n\n"
        print(data)

        # return Response(data, mimetype= 'text/event-stream')
        return jsonify({"perc": download_perc})

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
                    and os.stat(d).st_mtime < (time.time() - (30*60)):
                delete_list.append(d)
                shutil.rmtree(d)

        return(json.dumps(delete_list))

    @app.route('/_getplaylistitems', methods=['POST', 'GET'])
    def get_playlist_items():
        # url = "https://music.youtube.com/playlist?list=OLAK5uy_m_Kjhx3wck_RmcJuPf0kLR60t4hpP65Pc"
        url = request.args.get('url')

        print("Received Playlist URL is: " + url)

        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl_info = ydl.extract_info(url, download=False)

        return ydl_info
        # return render_template('index.html', ydl_info=ydl_info)

    @app.template_filter('sec_to_time')
    def sec_to_time(sec):
        return str(datetime.timedelta(seconds=sec))

    return app


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

def make_archive(source, destination):
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        print(source, destination, archive_from, archive_to)
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s'%(name,format), destination)