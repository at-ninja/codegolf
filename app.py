import datetime
import os.path
import time
import psycopg2
from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import validators
from wtforms.fields.html5 import EmailField
from wtforms.fields import SelectField

app = Flask(__name__)

# set the secret key.
app.secret_key = 'developer'

DATABASE_URL = os.environ['DATABASE_URL']


class ProgramForm(FlaskForm):
    program = FileField(validators=[FileRequired()])
    email = EmailField(
        validators=[validators.DataRequired(), validators.Email()])
    language = SelectField(choices=[('0', 'Python3'), ('1', 'Python2'), ('2', 'Node'), ('3', 'C/C++'), ('4', 'Java')],
                           validators=[validators.DataRequired()])


@app.route('/', methods=('GET', 'POST'))
def submit():
    form = ProgramForm()
    if form.validate_on_submit():
        f = form.program.data
        filename = secure_filename(f.filename)
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('INSERT INTO programs (email, filename, file_bin) VALUES \
                        (%s, %s, %s)',
                    (form.email.data, filename, form.program.data))
        # f.save(os.path.join(
        #     app.instance_path,
        #     'programs',
        #     '{0}-{1}-{2}'.format(
        #         datetime.datetime.fromtimestamp(
        #             time.time()).strftime('%Y-%m-%d_%H:%M:%S'),
        #         form.email.data,
        #         filename)
        # ))
        return redirect(url_for('submit'))
    else:
        print(form.errors)
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run()
