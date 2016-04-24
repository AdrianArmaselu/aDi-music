from __future__ import print_function  # In python 2.7
import os, sys
from flask import Flask, request, redirect, url_for, json, make_response, request
from flask import send_from_directory
from flask import render_template
from werkzeug import secure_filename
import random, string
import Generator

UPLOAD_FOLDER_PREFIX = 'static/files/{}'
ALLOWED_EXTENSIONS = set(['mid'])

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    folder_name = request.cookies.get('foldername')
    if not folder_name:
        print("no foldername")
        folder_name = get_foldername()
        folder_path = os.makedirs(UPLOAD_FOLDER_PREFIX.format(folder_name))
        print(folder_path)

    # folder_name = request.cookies.get('foldername')
    upload_folder = UPLOAD_FOLDER_PREFIX.format(folder_name)

    if request.method == 'POST':
        upload_files = request.files.getlist("file[]")
        for f in upload_files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                destination = os.path.join(upload_folder, filename)
                f.save(destination)
                Generator.generate(filename, 3000, upload_folder)
        return redirect(url_for('upload_file'))

    songs = os.listdir(upload_folder)
    resp = make_response(render_template("index.html",
                                         title='Sebastian Music', songs=songs, upload_folder=upload_folder))
    resp.set_cookie('foldername', folder_name)

    return resp


def get_foldername():
    STRING_LENGTH = 20
    folder_name = ''.join(random.choice(string.lowercase) for i in range(STRING_LENGTH))
    while os.path.exists(folder_name):
        folder_name = ''.join(random.choice(string.lowercase) for i in range(STRING_LENGTH))
    return folder_name


@app.route('/delete_song', methods=['POST'])
def delete_song():
    song = request.form['song']
    os.remove(song)
    return redirect(url_for('upload_file'))


# @app.route('/songs')
# def index():
#     music_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('mid')]
#     music_files_number = len(music_files)
#     return render_template("songs.html",
#                         title = 'Songs Available',
#                         music_files_number = music_files_number,
#                         music_files = music_files)

@app.route('/songs/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
