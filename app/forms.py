from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=12)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=64)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')