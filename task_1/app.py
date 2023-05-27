from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import requests

from typing import List, Dict, Any

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@postgres:5432/db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String)
    answer_text = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    added_at = db.Column(db.DateTime, default=datetime.now)

    def serialize(self) -> dict:
        return {
            'id': self.id,
            'question_text': self.question_text,
            'answer_text': self.answer_text,
            'created_at': self.created_at
        }


@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        """
            Тело запроса должно иметь вид "{'question_num': int}"

            curl -X POST localhost:5000 -d "{'question_num': '1'}" 
            curl -X POST localhost:5000 -d "{\"question_num\": \"1\"}" - cmd в Windows
        """
        data: dict = request.get_json(force=True)
        question_num: str = data.get('question_num')

        # if "question_num" not in data or not data["question_num"].isdigit() or not data["question_num"]: 
        if not question_num or not question_num.isdigit():
            abort(400)
        
        question_num: int = int(data["question_num"])
        res: List[Dict[Any, Any]] = requests.get(f"https://jservice.io/api/random?count={question_num}").json()
        
        for question in res:
            if question_in_db(question["id"]):
                status: bool = True
                while status is True:
                    question: dict = requests.get("https://jservice.io/api/random?count=1").json()[0]
                    
                    if not question_in_db(question["id"]):
                        new_question: Question = Question(
                            id=question["id"],
                            question_text=question["question"],
                            answer_text=question["answer"],
                            created_at=question["created_at"]
                        )
                        db.session.add(new_question)
                        db.session.flush()
                        
                        status = False
            
            else:
                # Save question
                new_question: Question = Question(
                    id=question["id"],
                    question_text=question["question"],
                    answer_text=question["answer"],
                    created_at=question["created_at"]
                )
                db.session.add(new_question)
                db.session.flush()
        
        db.session.commit()
        result: Question = Question.query.order_by(Question.added_at.desc()).first()
        return jsonify(result.serialize()) if result else jsonify({})
    
    abort(405)


def question_in_db(id: int) -> bool:
    question: Question = Question.query.filter_by(id=id).first()
    
    return True if question else False


if __name__ == '__main__':
    app.run(
        debug=True,
        host="0.0.0.0", 
        port=5000
        )