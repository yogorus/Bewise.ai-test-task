from flask import Flask, request, abort, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pydub import AudioSegment
from typing import BinaryIO
from mimetypes import guess_type, add_type
from io import BytesIO

import uuid
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@postgres:5432/db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.errorhandler(400)
def handle_bad_request(error):
    response = jsonify({'error': 'Bad request'})
    response.status_code = 400
    return response

@app.errorhandler(405)
def handle_method_not_allowed(error):
    response = jsonify({'error': 'Method not allowed'})
    response.status_code = 405
    return response

@app.errorhandler(409)
def handle_conflict(error):
    response = jsonify({'error': 'Conflict'})
    response.status_code = 409
    return response

add_type('audio/wav', '.wav') # В линукс контейнере выдает "audio/x-wav" и проверка возвращает False, потому добавил MIME тип вручную.

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String)
    uuid_token = db.Column(db.String, default=uuid.uuid4().hex)

class Record(db.Model):
    id = db.Column(db.String, default=uuid.uuid4().hex, primary_key=True)
    filename = db.Column(db.String, unique=False)
    data = db.Column(db.LargeBinary, unique=False)


@app.route('/', methods=["POST"])
def index():
    if request.method == "POST":
        """
            curl -X POST localhost:5000 -d "{\"username\": \"foo\"}"
        """
        data: dict = request.get_json(force=True)

        if "username" not in data or not data["username"]:
            abort(400)
        
        username: str = data["username"]
        user: User = User.query.filter_by(username = username).first()
        
        if user:
            abort(409)
        
        # Create user
        user: User = User(username=username)
        db.session.add(user)
        db.session.commit()
        
        return {"id": user.id, "uuid_token": user.uuid_token}, 201
    
    abort(405)


@app.route('/upload', methods=["POST"])
def upload():
    if request.method == "POST":
        r"""
        curl -X POST -H "Content-Type: multipart/form-data" \ 
            -F "file=@C:\Users\Yogorus\Desktop\projects\bewise\task_2\BabyElephantWalk60.wav" \ 
            -F "user_id=1" \
            -F "uuid_token=token" \
            http://localhost:5000/upload
        curl -X POST -H "Content-Type: multipart/form-data" -F "file=@C:\Users\Yogorus\Desktop\projects\bewise\task_2\BabyElephantWalk60.wav" -F "user_id=6" -F "uuid_token=e30e02a9712e4d0fa9f21c215bba4eb6" http://localhost:5000/upload
        curl -X POST -H "Content-Type: multipart/form-data" -F "file=@C:\Users\Yogorus\Desktop\projects\bewise\task_2\CantinaBand3.wav" -F "user_id=6" -F "uuid_token=e30e02a9712e4d0fa9f21c215bba4eb6" http://localhost:5000/upload
        C:\Users\Yogorus\Desktop\projects\bewise\task_2\CantinaBand3.wav
        """
        fields: tuple = ("user_id", "uuid_token")
        
        if all(field in request.form for field in fields) and 'file' in request.files:

            id: int = request.form["user_id"]
            token: str = request.form["uuid_token"]
            file: BinaryIO = request.files['file']
            
            if upload_is_correct(file) and user_is_correct(id=id, token=token):

                # Get sound
                sound: AudioSegment = AudioSegment.from_wav(file)
                
                # If we don't care about audio duration, this can be removed
                sound = sound.set_frame_rate(44100)
                
                buffer: BinaryIO = BytesIO()
                sound.export(buffer, format="mp3")

                mp3_data = buffer.getvalue()

                # Add .mp3 to filename
                base: str = os.path.splitext(file.filename)[0]
                new_filename: str = f"{base}.mp3"

                try:
                    record: Record = Record(filename=new_filename, data=mp3_data)
                    db.session.add(record)
                    db.session.commit()
                
                    return {"url": f"http://localhost:5000/record?id={record.id}&user={id}"}, 201
                
                except:
                    pass
                
            
            abort(400)  
            
        abort(400)
    
    abort(405)


@app.route('/record', methods=["GET"])
def record():
    if request.method == "GET":
        
        record_id: str = request.args.get('id')
        user_id: str = request.args.get('user')
        
        if record_id and user_id and record_id.isalnum() and user_id.isdigit():
            user_id : int = int(user_id)
            record: Record = Record.query.filter_by(id=record_id).first()
    
            if record:
                return send_file(BytesIO(record.data), download_name=record.filename, as_attachment=True)
        
            else:
                return {'message': 'something went wrong'}
        
        abort(400)
    
    abort(405)


def upload_is_correct(file: BinaryIO) -> bool:
    filename: str = file.filename
    mimetype: str = guess_type(filename)[0]
    
    return True if mimetype == "audio/wav" else False
    

def user_is_correct(token: str, id: str) -> bool:

    if not id.isdigit():
        return False
    
    id: int = int(id)

    user: User = User.query.filter_by(id=id).first()
    
    if not user:
        return False
    
    return True if user.uuid_token == token else False


if __name__ == '__main__':
    app.run(
        debug=True,
        host="0.0.0.0", 
        port=5000
        )