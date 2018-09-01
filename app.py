import subprocess
import time
import datetime
import os
from flask import Flask, render_template, redirect, url_for
from program_form import ProgramForm
from werkzeug.utils import secure_filename
from constants import VALID_EXTENSIONS, make_instance_folder, PROBLEMS

app = Flask(__name__)

make_instance_folder(app.instance_path)

# set the secret key.
app.secret_key = 'developer'


@app.route('/incorrect')
def incorrect():
    return render_template('incorrect.html')


@app.route('/leaderboards/<problemnumber>')
def leaderboards(problemnumber):
    if problemnumber in [str(x) for x in PROBLEMS]:
        return render_template('leaderboards.html', problem=problemnumber)
    else:
        return redirect(url_for('submissionPage'))


@app.route('/problem/<problemnumber>')
def problem(problemnumber):
    if problemnumber in [str(x) for x in PROBLEMS]:
        return render_template('problem.html', problem=problemnumber)
    else:
        return redirect(url_for('submissionPage'))


@app.route('/', methods=('GET', 'POST'))
def submissionPage():
    form = ProgramForm()
    if form.validate_on_submit():
        # If the form is valid, we want to save it, run it, and store data about it
        filename = secure_filename(form.program.data.filename)
        filetype = filename.split('.')[-1]

        print('---------------')
        print('New submission')
        print(form.email.data, filename)

        timestamp = datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y:%m:%d_%H:%M:%S')

        # save untested to disk (tmp)
        tmp_filename = '{3}-{0}-{1}-{2}'.format(
            timestamp, form.email.data, filename, form.problem.data)

        tmp_file = os.path.join(app.instance_path, 'tmp', tmp_filename)

        form.program.data.save(tmp_file)

        judge_input = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'judge_inputs', 'input{}.txt'.format(form.problem.data))
        judge_output = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'judge_outputs', 'output{}.txt'.format(form.problem.data))

        # test it
        try:
            print('Testing...')
            with open(judge_input, 'r') as stdin:
                res = subprocess.check_output(
                    VALID_EXTENSIONS[filetype](os.path.abspath(tmp_file)),
                    stdin=stdin)
            with open(judge_output, 'r') as output_file:
                output = output_file.read()

            # check if the output is correct
            if output == res.decode('UTF-8'):
                print('Accepted submission')

                # get size of file
                filesize = os.path.getsize(tmp_file)

                filename_with_size = '{0}-{1}'.format(filesize, tmp_filename)

                # save the file to the accepted solutions folder
                new_filename = os.path.join(
                    app.instance_path, 'programs', 'correct', str(
                        form.problem.data), filename_with_size
                )
                with open(tmp_file, 'r') as tmp:
                    with open(new_filename, 'w') as new:
                        new.write(tmp.read())

                os.remove(tmp_file)

                return redirect(url_for('leaderboards', problemnumber=form.problem.data))
            else:
                raise Exception('Wrong answer')
        except Exception as exc:
            print('Invalid submission')

            # save the file to the incorrect solutions folder
            new_filename = os.path.join(
                app.instance_path, 'programs', 'incorrect', tmp_filename
            )
            with open(tmp_file, 'r') as tmp:
                with open(new_filename, 'w') as new:
                    new.write(tmp.read())
            os.remove(tmp_file)

            return redirect(url_for('incorrect'))

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run()
