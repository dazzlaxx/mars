from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from forms import RegistrationForm, LoginForm, ApplicationForm
from models import db, User, Application
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("home.html")  # Изменено на home.html


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Вход выполнен успешно!", "success")
            return redirect(url_for("application_form"))
        else:
            flash("Неверный email или пароль", "danger")
    return render_template("login.html", form=form)


@app.route("/application", methods=["GET", "POST"])
@login_required
def application_form():
    form = ApplicationForm()
    if form.validate_on_submit():
        application = Application(
            user_id=current_user.id,
            education=form.education.data,
            experience=form.experience.data,
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            nationality=form.nationality.data,
            university=form.university.data,
            skills=form.skills.data,
            certifications=form.certifications.data,
            motivation=form.motivation.data,
        )
        db.session.add(application)
        db.session.commit()
        flash("Application submitted!", "success")
        return redirect(url_for("home"))
    return render_template("application_form.html", form=form)


@app.route("/simulators")
@login_required
def simulators():
    return render_template("simulators.html")


@app.route("/cabin_distribution")
@login_required
def cabin_distribution():
    return render_template("cabin_distribution.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")  # Уведомление об успешном выходе
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
