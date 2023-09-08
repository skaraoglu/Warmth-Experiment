from app import db
from sqlalchemy import JSON

class User(db.Model):
    mturk_id = db.Column(db.String(20), primary_key = True, unique=True)
    experiment_completed = db.Column(db.Boolean, default=False)
    #consent = db.Column(db.Boolean, default=False)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.mturk_id)

    def __repr__(self):
        return '<User MTURK ID: %r>' % (self.mturk_id)
    
class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mturk_id = db.Column(db.String(20), db.ForeignKey('user.mturk_id'))
    type = db.Column(db.String(20))
    data = db.Column(JSON)
    timestamp = db.Column(db.DateTime)  # Record when the survey was completed
    
class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mturk_id = db.Column(db.String(20), db.ForeignKey('user.mturk_id'))
    day_number = db.Column(db.Integer) # 1, 2, or 3
    agent_present = db.Column(db.Boolean, default=False)
    task_selections = db.relationship('Task', backref='day', lazy=True) # selected tasks for the day, should be 5
    completed = db.Column(db.Boolean, default=False)  # Mark day as completed
    timestamp = db.Column(db.DateTime)  # Record when the day was completed

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mturk_id = db.Column(db.String(20), db.ForeignKey('user.mturk_id'))
    task_type = db.Column(db.String(50))
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'))
    task_instance = db.Column(db.Integer)
    score = db.Column(db.Integer)  # Or a more appropriate data type
    completed = db.Column(db.Boolean, default=False)  # Mark task as completed
    timestamp = db.Column(db.DateTime)  # Record when the task was completed

class TaskCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('user.mturk_id'))
    task_type = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)