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
        cur.execute('INSERT INTO programs_tmp (id, email, filename, timestamp, file_bin) VALUES \
                        (DEFAULT, %s, %s, DEFAULT, %s);',
                    (form.email.data, filename, f.read()))
        conn.commit()
        # cur.close()
        conn.close()
        return redirect(url_for('submit'))
    else:
        print(form.errors)
    return render_template('index.html', form=form)


if __name__ == '__main__':
    create_table_string = 'create table if not exists programs (id serial primary key, timestamp timestamp default current_timestamp, email varchar(200) not null, problem varchar(200) not null, filename varchar(200) not null, language varchar(50) not null, file_blob bytea);'
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute(create_table_string)
    conn.commit()
    # cur.close()
    conn.close()
    app.run()
