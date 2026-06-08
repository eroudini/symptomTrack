from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    logs = db.relationship("SymptomLog", backref="user", lazy="dynamic")
    reports = db.relationship("AIReport", backref="user", lazy="dynamic")
    

class SymptomLog(db.Model):
    __tablename__ = "symptom_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    date = db.Column(db.Date, nullable=False)

    pain_level = db.Column(db.Integer, nullable=False)
    fatigue_level = db.Column(db.Integer, nullable=False)
    mood_level = db.Column(db.Integer, nullable=False)

    medications = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "pain_level": self.pain_level,
            "fatigue_level": self.fatigue_level,
            "mood_level": self.mood_level,
            "medications": self.medications,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }
    
class AIReport(db.Model):
    __tablename__ = "ai_reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    period_start = db.Column(db.Date, nullable=False)
    period_start = db.Column(db.Date, nullable=False)

    content = db.Column(db.Text, nullable=False)

    generated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "content": self.content,
            "generated_at": self.generated_at.isoformat()
        }