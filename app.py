import datetime
import os.path
import time
# import codejail
# import urllib.parse as urlparse
# import psycopg2
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

descriptions = {
    '1': 'This is an example question. I\'m trying to see if inline <b>HTML</b> works'
}

class ProgramForm(FlaskForm):
    program = FileField(validators=[FileRequired()])
    email = EmailField(
        validators=[validators.DataRequired(), validators.Email()])
    problem = SelectField(choices=[(str(x), 'Problem {}'.format(x+1)) for x in range(9)],
                           validators=[validators.DataRequired()])
    language = SelectField(choices=[('0', 'Python3'), ('1', 'Python2'), ('2', 'Node'), ('3', 'C/C++'), ('4', 'Java')],
                           validators=[validators.DataRequired()])


@app.route('/', methods=('GET', 'POST'))
def submit():
    form = ProgramForm()
    if form.problem is not None:
        print(form.problem.data)
    if form.validate_on_submit():
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        f = form.program.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.instance_path, 'tmp', '{0}-{1}-{2}'.format(timestamp, form.email.data, filename)
        ))
        size = os.path.getsize(os.path.join(
            app.instance_path, 'tmp', '{0}-{1}-{2}'.format(timestamp, form.email.data, filename)
        ))
        os.remove(os.path.join(
            app.instance_path, 'tmp', '{0}-{1}-{2}'.format(timestamp, form.email.data, filename)
        ))
        f.save(os.path.join(
            app.instance_path, 'programs', '{4}-{0}-{1}-{2}-{3}'.format(size, timestamp, form.email.data, filename, form.problem.data)
        ))
        return redirect(url_for('submit'))
    else:
        print(form.errors)
    return render_template('index.html', form=form)

@app.route('/problem/<problemnumber>')
def problem(problemnumber):
    if problemnumber in ['1','2','3','4','5','6','7','8','9']:
        return render_template('problem.html', problem=problemnumber)
    else:
        return redirect(url_for('submit'))


if __name__ == '__main__':
    app.run()
