import os
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from flask import render_template
from werkzeug import secure_filename

UPLOAD_FOLDER = 'songs'
ALLOWED_EXTENSIONS = set(['mid'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        for f_name in ['file', 'file2']:
            f = request.files[f_name]
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload_file'))
    return render_template("upload.html",
                        title = 'Upload 2 MIDI Files')

@app.route('/songs')
def index():
    music_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('mid')]
    music_files_number = len(music_files)
    return render_template("songs.html",
                        title = 'Songs Available',
                        music_files_number = music_files_number,
                        music_files = music_files)

# @app.route('/songs/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
