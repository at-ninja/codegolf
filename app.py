import datetime
import os.path
import time
import glob
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

language_choices = {
    '0': 'Python3', 
    '1': 'Python2', 
    '2': 'Node',
    '3': 'clang++',
    '4': 'Java'
}


class ProgramForm(FlaskForm):
    program = FileField(validators=[FileRequired()])
    email = EmailField(
        validators=[validators.DataRequired(), validators.Email()])
    problem = SelectField(choices=[(str(x+1), 'Problem {}'.format(x+1)) for x in range(9)],
                          validators=[validators.DataRequired()])
    language = SelectField(choices=[(x, language_choices[x]) for x in language_choices.keys()],
                           validators=[validators.DataRequired()])


class Submission(object):
    def __init__(self, email, size):
        self.email = email
        self.size = size


@app.route('/', methods=('GET', 'POST'))
def submit():
    form = ProgramForm()
    if form.problem is not None:
        print(form.problem.data)
    if form.validate_on_submit():
        timestamp = datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y:%m:%d_%H:%M:%S')
        f = form.program.data
        filename = secure_filename(f.filename)

        tmp_file = os.path.join(
            app.instance_path, 'tmp', '{0}-{1}-{2}'.format(
                timestamp, form.email.data, filename)
        )
        f.save(tmp_file)
        size = os.path.getsize(tmp_file)

        real_file = os.path.join(
            app.instance_path, 'programs', '{4}-{0}-{1}-{2}-{5}-{3}'.format(
                size, timestamp, form.email.data, filename, form.problem.data, form.language.data)
        )

        with open(tmp_file, 'r') as fp:
            with open(real_file, 'w') as fp2:
                fp2.write(fp.read())

        os.remove(tmp_file)

        return redirect(url_for('submit'))
    else:
        print(form.errors)
    return render_template('index.html', form=form)


@app.route('/problem/<problemnumber>')
def problem(problemnumber):
    if problemnumber in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        submissions = glob.glob(os.path.join(
            app.instance_path, 'programs', '{0}-*'.format(problemnumber)
        ))
        submissions = [Submission(email=x.split(
            '-')[3], size=x.split('-')[1]) for x in submissions]
        submissions.sort(key=lambda x: int(x.size))
        submissions = submissions[:5]
        return render_template('problem.html', problem=problemnumber, leaderboards=submissions)
    else:
        return redirect(url_for('submit'))


if __name__ == '__main__':
    app.run()
