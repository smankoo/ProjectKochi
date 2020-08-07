import os
import shutil
from slugify import slugify
import youtube_dl
from kochi.utils_aws import save_download_to_bucket


def _youtubedl(download_id, list_name, list_items, config):

    download_parent = config['download_dir']
    cachedir = config['cache_dir']

    downloaddir = download_parent + '/' + download_id

    if not os.path.exists(cachedir):
        os.makedirs(cachedir)

    if not os.path.exists(downloaddir):
        os.makedirs(downloaddir)

    # make name file system and URL safe
    list_name = slugify(list_name, separator=' ', lowercase=False)

    list_download_dir = os.path.join(downloaddir, list_name)

    if not os.path.exists(list_download_dir):
        os.makedirs(list_download_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            },
            {'key': 'FFmpegMetadata'},
        ],
        'logger': MyLogger(),
        'progress_hooks': [_youtubedl_progress_hook],
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

    save_download_to_bucket(download_id)

    retdata = {"download_id": download_id, "filename": zip_file_name}

    return retdata


def _youtubedl_progress_hook(d):
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
    shutil.move('%s.%s' % (name, format), destination)


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
