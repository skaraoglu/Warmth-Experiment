import json
import random
from flask import (
    url_for, redirect, render_template, flash, request, session, jsonify,
    current_app
)
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, bandit
from app.forms import LoginForm
from app.models import User, TaskCompletion
from datetime import datetime, timedelta
import numpy as np

_beta = [0.9, 0.85, 0.75, 0.8, 0.3, 0.2]
num_arms = 6  # Number of stock options
num_episodes = 0
bandit = bandit.Bandit(num_arms,beta_vals=_beta)
bandit.reset()

#Loads the user object from the database
@lm.user_loader
def load_user(mturk_id):
    return User.query.get(mturk_id)

#404 error page
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

#Utility function to clear session data and logout
@app.route('/clear_session_and_logout/')
def clear_session_and_logout():
    logout_user()
    session.clear()
    flash('You have either run out of time or have violated the terms of the experiment.')
    return redirect(url_for('login'))

def is_session_expired():
    expiry_time = session.get('expiry_time')
    if expiry_time:
        expiry_time = datetime.strptime(expiry_time, '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expiry_time:
            return True
    return False

@app.before_request
def check_session_expiry():
    if current_user.is_authenticated and is_session_expired():
        clear_session_and_logout()

#Index page
@app.route('/')
def index():
    if not current_user.is_authenticated or not session.get('login_completed'):
        return redirect(url_for('login'))
    else:
        return redirect(url_for('experiment'))

#Login page
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('experiment'))

    form = LoginForm()
    if form.validate_on_submit():
        mturk_id = form.mturk_id.data
        user = User.query.filter_by(mturk_id=mturk_id).first()

        if not user:
            new_user = User(mturk_id=mturk_id)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash('Login successful! You are now registered in the system.')

            session['mturk_id'] = mturk_id
            session['login_completed'] = True
            session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session['expiry_time'] = (datetime.now() + timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S')

            return redirect(url_for('experiment'))
        else:
            if user.experiment_completed:
                flash('Error! You have already completed the experiment.')
            else:
                flash('Error! MTurk ID already used. Contact the researchers if you believe this to be in error.')
            return redirect(url_for('login'))

    return render_template('login.html', title='Sign In', form=form)

@app.route('/experiment/')
@login_required
def experiment():
    if not current_user.is_authenticated:
        print("User not authenticated.")
        return redirect(url_for('login'))

    if session.get('exp_page_loaded'):
        print("User is reloading experiment page.")
        return redirect(url_for('clear_session_and_logout'))

    session['task_started'] = False
    print("Setting experiment page loaded.")
    session['exp_page_loaded'] = True
    t_c = is_task_completed('tutorial')
    w_c = is_task_completed('warmup')

    mturk_id = session.get('mturk_id')

    return render_template('experiment.html', mturk_id=mturk_id, tutorial_completed=t_c, warmup_completed=w_c)

def is_task_completed(task_type):
    task_completion = TaskCompletion.query.filter_by(user_id=current_user.mturk_id, task_type=task_type).first()
    if task_completion:
        return True
    else:
        return False

@app.route('/tutorial/')
@login_required
def tutorial():
    session['exp_page_loaded'] = False

    if not current_user.is_authenticated:
        print("User not authenticated.")
        return redirect(url_for('login'))

    mturk_id = session.get('mturk_id')

    #Change tutorial task to completed
    tutorial_completion = TaskCompletion.query.filter_by(user_id=current_user.mturk_id, task_type='tutorial').first()
    if not tutorial_completion:
        tutorial_completion = TaskCompletion(user_id=mturk_id, task_type='tutorial')
        db.session.add(tutorial_completion)
        db.session.commit()

    return render_template('tutorial.html', mturk_id=mturk_id)

@app.route('/warmup/')
@login_required
def warmup():
    session['exp_page_loaded'] = False

    if session.get('warmup_loaded'):
        print("User is reloading warmup page.")
        return redirect(url_for('clear_session_and_logout'))

    #Get the warmup start time
    session['warmup_start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    num_episodes = 10
    if not current_user.is_authenticated:
        print("User not authenticated.")
        return redirect(url_for('login'))

    session['warmup_started'] = True
    print("Setting experiment page loaded.")
    session['warmup_loaded'] = True

    bandit.reset()

    mturk_id = session.get('mturk_id')

    warmup_completion = TaskCompletion.query.filter_by(user_id=current_user.mturk_id, task_type='warmup').first()
    if not warmup_completion:
        warmup_completion = TaskCompletion(user_id=mturk_id, task_type='warmup')
        db.session.add(warmup_completion)
        db.session.commit()

    return render_template('warmup.html', mturk_id=mturk_id)

@app.route('/task/')
@login_required
def task():
    num_episodes = 30
    if not current_user.is_authenticated:
        print("User not authenticated.")
        return redirect(url_for('login'))

    session['task_started'] = True
    print("Setting experiment page loaded.")
    session['task_page_loaded'] = True

    bandit.reset()

    mturk_id = session.get('mturk_id')
    return render_template('task.html', mturk_id=mturk_id)

@app.route('/get_reward')
def get_reward():
    selected_option = int(request.args.get('selected_option', 0))
    reward = bandit.pull_arm(selected_option)

    # Update self.S and self.F with the received reward
    bandit.S[selected_option] += reward
    bandit.F[selected_option] += 1

    agents = int(bandit.UCB())
    #print(agents)

    if(np.sum(bandit.F)==num_episodes):
        bandit.reset()

    return jsonify({'reward': reward, 'banditS': bandit.S[selected_option], 'banditF': bandit.F[selected_option], 'agents': agents})




