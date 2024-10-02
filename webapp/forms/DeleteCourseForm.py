from flask_wtf import FlaskForm
from wtforms import BooleanField


class DeleteCourseForm(FlaskForm):
    user_agreement = BooleanField("Удалить курс")

    def __init__(self, *args, custom_label=None, **kwargs):
        super(DeleteCourseForm, self).__init__(*args, **kwargs)
        if custom_label:
            self.user_agreement.label.text = f"Я подтверждаю, что хочу удалить курс {custom_label}"
