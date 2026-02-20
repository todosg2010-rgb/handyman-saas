from datetime import datetime
from extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # 🔥 future monetization
    plan = db.Column(db.String(20), default="free")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔥 relationship
    jobs = db.relationship(
        "Job",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    # 🚨 NOT nullable anymore
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    description = db.Column(db.Text, nullable=False)

    hours = db.Column(db.Float, nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    profit_percent = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)

    total_cost = db.Column(db.Float, nullable=False)
    profit_amount = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=False)

    client_message = db.Column(db.Text, nullable=False)
    engine_version = db.Column(db.String(20), default="v1.4")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔥 relationship
    materials = db.relationship(
        "JobMaterial",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan"
    )


class JobMaterial(db.Model):
    __tablename__ = "job_materials"

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )

    name = db.Column(db.String(255), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
