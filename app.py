import subprocess
import time
import datetime
import os
from flask import Flask, render_template, redirect, url_for, request, send_file
from werkzeug.utils import secure_filename
from constants import VALID_EXTENSIONS, make_instance_folder, PROBLEMS, compare_rows
from program_form import ProgramForm
from leaderboard_row import LeaderboardRow


app = Flask(__name__)

make_instance_folder(app.instance_path)

# set the secret key.
app.secret_key = 'developer'

# Input / Output example files

@app.route('/winners')
def winners():

    winner_list = []

    for problemnumber in PROBLEMS[::-1]:

        dir_to_check = os.path.join(
            app.instance_path, 'programs', 'correct', str(problemnumber))
        correct_sols = [f for f in os.listdir(
            dir_to_check) if os.path.isfile(os.path.join(dir_to_check, f))]

        # convert filenames to objects
        board = []
        for f in correct_sols:
            fp = os.path.join(dir_to_check, f)

            size = os.path.getsize(fp)
            email = f.split('-')[1]
            time = f.split('-')[0]

            row = LeaderboardRow(
                size=size, email=email, time=time,
                filename=f, active=False)

            board += [row]

        board.sort(key=lambda x: x.time)  # secondary sort
        board.sort(key=lambda x: x.size)  # primary sort

        filtered_board = [x.email for x in board if x.email not in winner_list]

        winner_list += filtered_board[:1]

    return render_template('winners.html', winners=winner_list)


@app.route('/problem/inputs/input<problem>.txt')
def inputs(problem):
    if problem in [str(x) for x in PROBLEMS]:
        return send_file(os.path.join(
            'inputs', 'input_{}.txt'.format(
                problem)
        ), mimetype="text/plain")
    return redirect(url_for('submissionPage'))


@app.route('/problem/outputs/output<problem>.txt')
def outputs(problem):
    if problem in [str(x) for x in PROBLEMS]:
        return send_file(os.path.join(
            'outputs', 'output_{}.txt'.format(
                problem)
        ), mimetype="text/plain")
    return redirect(url_for('submissionPage'))


@app.route('/incorrect')
def incorrect():
    return render_template('incorrect.html')


@app.route('/leaderboards/<problemnumber>')
def leaderboards(problemnumber):
    if problemnumber in [str(x) for x in PROBLEMS]:

        highlight_result = request.args.get('e')

        dir_to_check = os.path.join(
            app.instance_path, 'programs', 'correct', str(problemnumber))
        correct_sols = [f for f in os.listdir(
            dir_to_check) if os.path.isfile(os.path.join(dir_to_check, f))]

        # convert filenames to objects
        board = []
        for f in correct_sols:
            fp = os.path.join(dir_to_check, f)

            size = os.path.getsize(fp)
            email = f.split('-')[1]
            time = f.split('-')[0]
            active = highlight_result == email

            row = LeaderboardRow(
                size=size, email=email, time=time,
                filename=f, active=active)

            board += [row]

        board.sort(key=lambda x: x.time)  # secondary sort
        board.sort(key=lambda x: x.size)  # primary sort

        return render_template('leaderboards.html', problem=problemnumber, board=board)
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
        tmp_filename = '{0}-{1}-{2}'.format(
            timestamp, form.email.data, filename)

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
                    ['python3', 'chroot_jail_script.py',
                        os.path.abspath(tmp_file)],
                    stdin=stdin)
            with open(judge_output, 'r') as output_file:
                output = output_file.read()

            # check if the output is correct
            if output == res.decode('UTF-8'):
                print('Accepted submission')

                # save the file to the accepted solutions folder
                new_filename = os.path.join(
                    app.instance_path, 'programs', 'correct', str(
                        form.problem.data), tmp_filename
                )
                with open(tmp_file, 'r') as tmp:
                    with open(new_filename, 'w') as new:
                        new.write(tmp.read())

                os.remove(tmp_file)

                return redirect(url_for('leaderboards', problemnumber=form.problem.data, e=form.email.data))
            else:
                raise Exception('Wrong answer')
        except Exception as exc:
            print('Invalid submission')

            # save the file to the incorrect solutions folder
            new_filename = '{0}-{1}'.format(form.problem.data, tmp_filename)
            new_filepath = os.path.join(
                app.instance_path, 'programs', 'incorrect', new_filename
            )
            with open(tmp_file, 'r') as tmp:
                with open(new_filepath, 'w') as new:
                    new.write(tmp.read())
            os.remove(tmp_file)

            return redirect(url_for('incorrect'))

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), threaded=True)
