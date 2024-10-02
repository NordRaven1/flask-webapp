from flask_wtf import FlaskForm
from wtforms import BooleanField


class DeleteArticleForm(FlaskForm):
    user_agreement = BooleanField("Удалить статью")

    def __init__(self, *args, custom_label=None, **kwargs):
        super(DeleteArticleForm, self).__init__(*args, **kwargs)
        if custom_label:
            self.user_agreement.label.text = f"Я подтверждаю, что хочу удалить статью {custom_label}"
