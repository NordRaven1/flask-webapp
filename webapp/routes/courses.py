from functools import partial

from flask import Blueprint, request, render_template, abort, flash, redirect, url_for
from flask_login import current_user, login_required

import webapp.db.courses_functions as db_crs
from exceptions import exceptions
from forms.ArticleForm import ArticleForm
from forms.CommentsForm import CommentsForm
from forms.CourseForm import CourseForm
import webapp.images.image_functions as img_funcs
from forms.DeleteArticleForm import DeleteArticleForm
from forms.DeleteCourseForm import DeleteCourseForm
from webapp.pagination.Paginator import Paginator

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/", methods=["GET"])
def show_courses():
    courses_per_page = 6
    page = request.args.get('page', default=1, type=int)
    title_to_find = request.args.get('title', default="", type=str)
    description_to_find = request.args.get('description', default="", type=str)
    courses_paginator = Paginator(page, courses_per_page, db_crs.get_count_of_courses(title_to_find,
                                                                                      description_to_find))
    offset = (page - 1) * courses_per_page
    if current_user.is_authenticated:
        courses_on_this_page = db_crs.get_courses_per_page(current_user.user_id, courses_per_page, offset,
                                                           title_to_find, description_to_find)
        fav_courses = db_crs.get_courses_favoured_by_user(current_user)
    else:
        courses_on_this_page = db_crs.get_courses_per_page(None, courses_per_page, offset, title_to_find,
                                                           description_to_find)
        fav_courses = []
    fav_ids = {course.course_id for course in fav_courses}
    return render_template("index.html", courses=courses_on_this_page, page=page, paginator=courses_paginator,
                           fav_ids=fav_ids, title_to_find=title_to_find, description_to_find=description_to_find)


@courses_bp.route("/<string:course_id>", methods=["GET"])
@login_required
def show_course_page(course_id: str):
    articles_per_page = 3
    page = request.args.get('page', default=1, type=int)
    course = db_crs.find_course_by_id(course_id)
    if course is None:
        abort(404)
    articles_paginator = Paginator(page, articles_per_page, db_crs.get_count_of_articles_in_course(course_id))
    offset = (page - 1) * articles_per_page
    articles = db_crs.get_all_articles_at_course(course_id, articles_per_page, offset)
    images = [img_funcs.dump_image(article.image) for article in articles]
    return render_template("course.html", course=course, articles=articles, images=images, page=page,
                           paginator=articles_paginator)


@courses_bp.route("/new", methods=("GET", "POST"))
@login_required
def create_course():
    if current_user.role != 'author':
        abort(404)
    form = CourseForm()
    _render_template = partial(render_template, "new_course.html", form=form)
    if request.method == "GET":
        return _render_template()
    if not form.validate_on_submit():
        errors = [error for errors in form.errors.values() for error in errors]
        for error in errors:
            flash(error)
        return _render_template()
    try:
        db_crs.add_course(form.course_title.data, current_user, form.description.data)
    except exceptions.CourseAlreadyExists:
        flash("Курс с таким названием уже существует")
        return _render_template()
    return redirect(url_for(".show_courses"))


@courses_bp.route("/<string:course_id>/to_favourite", methods=["GET"])
@login_required
def add_course_to_favourites(course_id: str):
    course = db_crs.find_course_by_id(course_id)
    if course is None:
        abort(404)
        db_crs.add_course_to_favourites(current_user, course_id)
        return redirect(url_for(".show_courses"))


@courses_bp.route("/<string:course_id>/out_of_favourite", methods=["GET"])
@login_required
def unfavourite_course(course_id: str):
    course = db_crs.find_course_by_id(course_id)
    if course is None:
        abort(404)
    db_crs.remove_course_from_favoured(current_user, course_id)
    return redirect(url_for(".show_courses"))


@courses_bp.route("/<string:course_id>/out_of_favourite_from_profile", methods=["GET"])
@login_required
def unfavourite_course_from_profile(course_id: str):
    course = db_crs.find_course_by_id(course_id)
    if course is None:
        abort(404)
    db_crs.remove_course_from_favoured(current_user, course_id)
    return redirect(url_for("accounting.show_profile"))


@courses_bp.route("/<string:course_id>/edit", methods=("GET", "POST"))
@login_required
def edit_course(course_id: str):
    course = db_crs.find_course_by_id(course_id)
    if course is None:
        abort(404)
    if not (course.author == current_user or current_user.role == 'admin'):
        abort(404)
    form = CourseForm()
    _render_template = partial(render_template, "edit_course.html", form=form)
    if request.method == "GET":
        form.course_title.data = course.course_title
        form.description.data = course.description
        return _render_template()
    form.course_title.data = request.form.get('course_title', '')
    form.description.data = request.form.get('description', '')
    if not form.validate_on_submit():
        errors = [error for errors in form.errors.values() for error in errors]
        for error in errors:
            flash(error)
        return _render_template()
    try:
        db_crs.edit_course(form.course_title.data, form.description.data, course_id)
    except exceptions.CourseAlreadyExists:
        flash("Курс с таким названием уже существует")
        return _render_template()
    return redirect(url_for(".show_courses"))


@courses_bp.route("/<string:course_id>/delete", methods=("GET", "POST"))
@login_required
def delete_course(course_id: str):
    course = db_crs.find_course_by_id(course_id)
    if course is None:
        abort(404)
    if not (course.author == current_user or current_user.role == 'admin'):
        abort(404)
    form = DeleteCourseForm(custom_label=course.course_title)
    articles_count = db_crs.get_count_of_articles_in_course(course_id)
    _render_template = partial(render_template, "delete_course.html", form=form, course=course,
                               articles_count=articles_count)
    if request.method == "GET":
        return _render_template()
    if form.validate_on_submit():
        if form.user_agreement.data:
            db_crs.delete_course(course_id)
            return redirect(url_for(".show_courses"))
        else:
            return _render_template(check=True)


@courses_bp.route("/<string:course_id>/articles/new", methods=("GET", "POST"))
@login_required
def create_article(course_id: str):
    course = db_crs.find_course_by_id(course_id)
    if course is None:
        abort(404)
    if current_user != course.author:
        abort(404)
    form = ArticleForm()
    _render_template = partial(render_template, "new_article.html", form=form)
    if request.method == "GET":
        return _render_template()
    if not form.validate_on_submit():
        errors = [error for errors in form.errors.values() for error in errors]
        for error in errors:
            flash(error)
        return _render_template()
    try:
        image = img_funcs.load_image(form.cover_image.data)
        db_crs.add_article(form.article_title.data, course_id, form.article_text.data, current_user, image)
    except exceptions.ArticleAlreadyExists:
        flash("Статья с таким названием уже существует в данном курсе")
        return _render_template()
    return redirect(url_for(".show_course_page", course_id=course_id))


@courses_bp.route("/<string:course_id>/articles/<string:article_id>", methods=["GET"])
@login_required
def show_article_page(course_id: str, article_id: str):
    course = db_crs.find_course_by_id(course_id)
    article = db_crs.find_article_by_id(article_id)
    if course is None or article is None:
        abort(404)
    form = CommentsForm()
    comments = db_crs.get_comments_for_article(article_id)
    comments_replies_dict = {comment: db_crs.get_replies_for_comment(comment.comment_id) for comment in comments}
    image = img_funcs.dump_image(article.image)
    return render_template("article.html", article=article, image=image, course=course, form=form,
                           comments_and_replies=comments_replies_dict)


@courses_bp.route("/<string:course_id>/articles/<string:article_id>/delete", methods=("GET", "POST"))
@login_required
def delete_article(course_id: str, article_id: str):
    course = db_crs.find_course_by_id(course_id)
    article = db_crs.find_article_by_id(article_id)
    if course is None or article is None:
        abort(404)
    if not (article.author == current_user or current_user.role == 'admin'):
        abort(404)
    form = DeleteArticleForm(custom_label=article.article_title)
    _render_template = partial(render_template, "delete_article.html", form=form, article=article, course=course)
    if request.method == "GET":
        return _render_template()
    if form.validate_on_submit():
        if form.user_agreement.data:
            db_crs.delete_article(article_id)
            return redirect(url_for(".show_course_page", course_id=course_id))
        else:
            return _render_template(check=True)


@courses_bp.route("/<string:course_id>/articles/<string:article_id>/edit", methods=("GET", "POST"))
@login_required
def edit_article(course_id: str, article_id: str):
    course = db_crs.find_course_by_id(course_id)
    article = db_crs.find_article_by_id(article_id)
    if course is None or article is None:
        abort(404)
    if not (article.author == current_user or current_user.role == 'admin'):
        abort(404)
    form = ArticleForm()
    _render_template = partial(render_template, "edit_article.html", form=form)
    image = article.image.image if article.image else None
    if request.method == "GET":
        form.article_title.data = article.article_title
        form.article_text.data = article.article_text
        return _render_template()
    form.article_title.data = request.form.get('article_title', '')
    form.article_text.data = request.form.get('article_text', '')
    if not form.validate_on_submit():
        errors = [error for errors in form.errors.values() for error in errors]
        for error in errors:
            flash(error)
        return _render_template()
    try:
        if form.cover_image.data:
            image = img_funcs.load_image(form.cover_image.data)
        db_crs.edit_article(form.article_title.data, form.article_text.data, article_id, image)
    except exceptions.ArticleAlreadyExists:
        flash("Статья с таким названием уже существует в данном курсе")
        return _render_template()
    return redirect(url_for(".show_article_page", course_id=course_id, article_id=article_id, active_tab='#article'))


@courses_bp.route("/<string:course_id>/articles/<string:article_id>/add_comment", methods=("GET", "POST"))
@login_required
def add_comment(course_id: str, article_id: str):
    course = db_crs.find_course_by_id(course_id)
    article = db_crs.find_article_by_id(article_id)
    if course is None or article is None:
        abort(404)
    form = CommentsForm()
    _render_template = partial(render_template, "show_article_page", course_id=course_id, article_id=article_id,
                               form=form, active_tab='#comments')
    if not form.validate_on_submit():
        errors = [error for errors in form.errors.values() for error in errors]
        for error in errors:
            flash(error)
        return _render_template()
    db_crs.add_comment(current_user, form.comment_text.data, article_id)
    return redirect(url_for(".show_article_page", course_id=course_id, article_id=article_id,
                            active_tab='#comments'))


@courses_bp.route("/<string:course_id>/articles/<string:article_id>/comments/<string:comment_id>/reply",
                  methods=("GET", "POST"))
@login_required
def reply_to_comment(course_id: str, article_id: str, comment_id: str):
    course = db_crs.find_course_by_id(course_id)
    article = db_crs.find_article_by_id(article_id)
    comment = db_crs.find_comment_by_id(comment_id)
    if course is None or article is None or comment is None:
        abort(404)
    if not (current_user == article.author or current_user.role == 'admin' or comment.author == current_user):
        abort(404)
    form = CommentsForm()
    _render_template = partial(render_template, "show_article_page", course_id=course_id, article_id=article_id,
                               form=form, active_tab='#comments')
    if not form.validate_on_submit():
        errors = [error for errors in form.errors.values() for error in errors]
        for error in errors:
            flash(error)
        return _render_template()
    db_crs.reply_to_comment(current_user, form.comment_text.data, article_id, comment_id)
    return redirect(url_for(".show_article_page", course_id=course_id, article_id=article_id,
                            active_tab='#comments'))


@courses_bp.route("/comment-<string:comment_id>", methods=["GET"])
def link_to_comment(comment_id: str):
    comment = db_crs.find_comment_by_id(comment_id)
    if comment is None:
        abort(404)
    article = db_crs.find_article_by_comment(comment)
    if article is None:
        abort(404)
    course = db_crs.find_course_by_article(article)
    if course is None:
        abort(404)
    return redirect(url_for(".show_article_page", course_id=course.course_id, article_id=article.article_id,
                            _anchor=f"comment-{comment_id}", active_tab='#comments'))


@courses_bp.route("/<string:course_id>/articles/<string:article_id>/comments/<string:comment_id>/delete",
                  methods=["GET"])
@login_required
def delete_comment(course_id: str, article_id: str, comment_id: str):
    course = db_crs.find_course_by_id(course_id)
    article = db_crs.find_article_by_id(article_id)
    comment = db_crs.find_comment_by_id(comment_id)
    if course is None or article is None or comment is None:
        abort(404)
    if not (article.author == current_user or current_user.role == 'admin'):
        abort(404)
    db_crs.delete_comment(comment_id)
    return redirect(url_for(".show_article_page", course_id=course_id, article_id=article_id,
                            active_tab='#comments'))
