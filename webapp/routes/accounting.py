from functools import partial

from flask import Blueprint, redirect, url_for, session, abort, request, render_template, flash
from flask_login import login_required, logout_user, current_user, login_user

import webapp.db.accounting_functions as db_ac
import webapp.db.courses_functions as db_crs
from exceptions import exceptions
from forms.LoginForm import LoginForm
from forms.RegistrationForm import RegistrationForm
from pagination.Paginator import Paginator

accounting_bp = Blueprint("accounting", __name__)


@accounting_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("courses.show_courses"))


@accounting_bp.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        abort(404)
    form = LoginForm()
    _render_template = partial(render_template, "login.html", form=form)
    if request.method == "GET":
        return _render_template()
    if not form.validate_on_submit():
        errors = [error for errors in form.errors.values() for error in errors]
        for error in errors:
            flash(error)
        return _render_template()
    user = db_ac.find_user_by_email(form.email.data)
    if user is not None and user.check_password(form.password.data):
        login_user(user)
        session.permanent = True
        return redirect(url_for("courses.show_courses"))
    flash("Неверная информация в полях авторизации")
    return _render_template()


@accounting_bp.route("/registration", methods=("GET", "POST"))
def registration():
    if current_user.is_authenticated:
        abort(404)
    form = RegistrationForm()
    _render_template = partial(render_template, "registration.html", form=form)
    if request.method == "GET":
        return _render_template()
    if not form.validate_on_submit():
        errors = [error for errors in form.errors.values() for error in errors]
        for error in errors:
            flash(error)
        return _render_template()
    try:
        db_ac.register_user(form.login.data, form.email.data, form.password.data)
    except exceptions.AlreadyRegisteredException:
        flash("Пользователь с таким логином или email уже зарегистрирован!")
        return _render_template()
    user = db_ac.find_user_by_login(form.login.data)
    login_user(user)
    return redirect(url_for("courses.show_courses"))


@accounting_bp.route("/profile", methods=["GET"])
@login_required
def show_profile():
    courses_per_page = 6
    page = request.args.get('page', default=1, type=int)
    courses_paginator = Paginator(page, courses_per_page, db_crs.get_count_of_fav_courses())
    offset = (page - 1) * courses_per_page
    fav_courses = db_crs.get_fav_courses_per_page(current_user.user_id, courses_per_page, offset)
    user_comments = db_crs.get_comments_left_by_user(current_user)
    return render_template("user_profile.html", fav_courses=fav_courses, page=page, comments=user_comments,
                           paginator=courses_paginator)


@accounting_bp.route("/admin_panel", methods=["GET"])
@login_required
def show_admin_panel():
    if current_user.role != 'admin':
        abort(404)
    users = db_ac.get_all_users()
    return render_template("admin_panel.html", users=users)


@accounting_bp.route("/admin_panel/<string:user_id>/to_author", methods=["GET"])
@login_required
def make_author_from_reader(user_id: str):
    if current_user.role != 'admin':
        abort(404)
    user = db_ac.find_user_by_id(user_id)
    users = db_ac.get_all_users()
    if user is None or user not in users:
        abort(404)
    db_ac.user_to_author(user_id)
    return redirect(url_for(".show_admin_panel"))


@accounting_bp.route("/admin_panel/<string:user_id>/to_reader", methods=["GET"])
@login_required
def make_reader_from_author(user_id: str):
    if current_user.role != 'admin':
        abort(404)
    user = db_ac.find_user_by_id(user_id)
    users = db_ac.get_all_users()
    if user is None or user not in users:
        abort(404)
    db_ac.user_to_reader(user_id)
    return redirect(url_for(".show_admin_panel"))
