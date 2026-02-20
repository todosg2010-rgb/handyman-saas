import os
from datetime import datetime

from flask import Flask, request, jsonify, redirect, render_template
from flask_migrate import Migrate
from sqlalchemy import func

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)

import bcrypt

from pricing_engine import изчисли_оферта
from extensions import db


# =========================
# BULLETPROOF DB PATH
# =========================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)
DB_PATH = os.path.join(INSTANCE_DIR, "local.db")


# =========================
# APP SETUP
# =========================

app = Flask(__name__)
app.json.ensure_ascii = False

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-this")

# 🔥 PRODUCTION DATABASE SUPPORT (Render PostgreSQL)
database_url = os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)


# IMPORTANT: import models AFTER db.init_app
import models
from models import User, Job, JobMaterial


# =========================
# LOGIN MANAGER
# =========================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =========================
# PAGE ROUTES
# =========================

@app.route("/")
def landing():
    return render_template("index.html")


@app.route("/kak-raboti")
@app.route("/how-it-works")
def how_it_works():
    return render_template("how-it-works.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/demo")
@login_required
def demo():
    return render_template("demo.html")


@app.route("/analytics")
@login_required
def analytics_page():
    return render_template("analytics.html")


# =========================
# AUTH ROUTES
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.checkpw(
            password.encode(),
            user.password_hash.encode()
        ):
            return render_template(
                "login.html",
                error="Невалиден имейл или парола"
            )

        login_user(user)
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            return render_template(
                "signup.html",
                error="Този акаунт вече съществува"
            )

        hashed_password = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        new_user = User(
            email=email,
            password_hash=hashed_password,
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect("/dashboard")

    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# =========================
# API: CALCULATE OFFER
# =========================

@app.route("/api/izchisli", methods=["POST"])
@login_required
def izchisli():
    data = request.get_json()
    try:
        result = изчисли_оферта(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# API: SAVE OFFER / JOB
# =========================

@app.route("/api/jobs", methods=["POST"])
@login_required
def save_job():
    data = request.get_json()

    try:
        hours = data.get("hours", data.get("часове"))
        hourly_rate = data.get("hourly_rate", data.get("часова_ставка"))
        profit_percent = data.get("profit_percent", data.get("процент_печалба"))
        distance = data.get("distance", data.get("разстояние", 0))

        if hours is None:
            raise KeyError("hours")

        job = Job(
            user_id=current_user.id,
            description=data.get("description", data.get("описание", "")),
            hours=float(hours),
            hourly_rate=float(hourly_rate),
            profit_percent=float(profit_percent),
            distance=float(distance),

            total_cost=float(data.get("total_cost", data.get("себестойност"))),
            profit_amount=float(data.get("profit_amount", data.get("печалба"))),
            final_price=float(data.get("final_price", data.get("препоръчителна_цена"))),

            client_message=data.get("client_message", data.get("съобщение")),
            engine_version=data.get("engine_version", "v3.0"),
        )

        db.session.add(job)
        db.session.flush()

        for m in data.get("materials", data.get("материали", [])):
            db.session.add(
                JobMaterial(
                    job_id=job.id,
                    name=m.get("name", m.get("име")),
                    unit_price=float(m.get("unit_price", m.get("единична_цена"))),
                    quantity=float(m.get("quantity", m.get("количество"))),
                    total_price=float(m.get("total_price", m.get("стойност"))),
                )
            )

        db.session.commit()
        return jsonify({"status": "saved", "job_id": job.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# =========================
# API: ANALYTICS
# =========================

@app.route("/api/analytics")
@login_required
def analytics():

    total_profit = db.session.query(
        func.coalesce(func.sum(Job.profit_amount), 0)
    ).filter(Job.user_id == current_user.id).scalar()

    total_revenue = db.session.query(
        func.coalesce(func.sum(Job.final_price), 0)
    ).filter(Job.user_id == current_user.id).scalar()

    total_jobs = db.session.query(
        func.count(Job.id)
    ).filter(Job.user_id == current_user.id).scalar()

    total_materials = db.session.query(
        func.coalesce(func.sum(JobMaterial.total_price), 0)
    ).join(Job).filter(Job.user_id == current_user.id).scalar()

    avg_margin = (
        (total_profit / total_revenue) * 100
        if total_revenue > 0 else 0
    )

    if avg_margin < 25:
        health_status = "low"
    elif avg_margin < 30:
        health_status = "warning"
    else:
        health_status = "healthy"

    return jsonify({
        "profit": round(total_profit, 2),
        "revenue": round(total_revenue, 2),
        "materials": round(total_materials, 2),
        "jobs": total_jobs,
        "avg_margin": round(avg_margin, 2),
        "health": health_status,
        "totals": {
            "profit": round(total_profit, 2),
            "revenue": round(total_revenue, 2),
            "materials": round(total_materials, 2),
            "jobs": total_jobs
        }
    })


# =========================
# API: RECENT JOBS
# =========================

@app.route("/api/jobs/recent")
@login_required
def recent_jobs():
    jobs = (
        Job.query
        .filter_by(user_id=current_user.id)
        .order_by(Job.created_at.desc())
        .limit(10)
        .all()
    )

    return jsonify([
        {
            "id": j.id,
            "description": j.description,
            "final_price": round(j.final_price, 2),
            "profit": round(j.profit_amount, 2),
            "margin": round((j.profit_amount / j.final_price) * 100, 2)
            if j.final_price else 0
        }
        for j in jobs
    ])


# =========================
# API: DELETE JOB
# =========================

@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
@login_required
def delete_job(job_id):

    job = Job.query.filter_by(
        id=job_id,
        user_id=current_user.id
    ).first_or_404()

    JobMaterial.query.filter_by(job_id=job.id).delete()
    db.session.delete(job)
    db.session.commit()

    return jsonify({"status": "deleted"})


# =========================
# RUN LOCAL
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
