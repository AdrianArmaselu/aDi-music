from __future__ import print_function # In python 2.7
import os, sys
from flask import Flask, request, redirect, url_for, json
from flask import send_from_directory
from flask import render_template
from werkzeug import secure_filename

UPLOAD_FOLDER_PREFIX = 'static/files/{}'
ALLOWED_EXTENSIONS = set(['mid'])

app = Flask(__name__)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():

    # create a dir based on user ip address, so each user has his own dir for his music
    #get user ip address
    trusted_proxies = {'127.0.0.1'}  # define your own set
    route = request.access_route + [request.remote_addr]
    remote_addr = next((addr for addr in reversed(route) if addr not in trusted_proxies), request.remote_addr)
    upload_folder = UPLOAD_FOLDER_PREFIX.format(remote_addr)
    if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

    songs = os.listdir(upload_folder)
    if request.method == 'POST':
        upload_files = request.files.getlist("file[]")
        for f in upload_files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                destination = os.path.join(upload_folder, filename)
                print(upload_folder)
                print(destination)
                f.save(destination)
        return redirect(url_for('upload_file'))
    return render_template("index.html",
                        title = 'Sebastian Music', songs=songs, upload_folder=upload_folder)


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
