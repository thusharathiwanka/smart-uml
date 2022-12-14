from datetime import datetime
from config.database import db


class Diagram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    class_diagram_path = db.Column(db.String(80))
    usecase_diagram_path = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(), default=datetime.now())

    def __repr__(self) -> str:
        return 'Diagram>>> {self.content}'
