import json
import random
from flask import (
    url_for, redirect, render_template, flash, request, session, jsonify,
    current_app
)
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, bandit
from app.forms import LoginForm
from app.models import Survey, User, TaskCompletion, Task
from datetime import datetime, timedelta
import numpy as np

attentionChecks = []
_beta = [0.9, 0.85, 0.75, 0.8, 0.3, 0.2]
num_arms = 6  # Number of stock options
num_episodes = 30
bandit = bandit.Bandit(num_arms,num_episodes,beta_vals=_beta,condition=1)
bandit.reset()

@app.before_request
def create_tables():
    db.create_all()

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

            return redirect(url_for('consent'))
        else:
            if user.experiment_completed:
                flash('Error! You have already completed the experiment.')
            else:
                flash('Error! MTurk ID already used. Contact the researchers if you believe this to be in error.')
            return redirect(url_for('login'))

    return render_template('login.html', title='Sign In', form=form)

@app.route('/consent/', methods=['GET', 'POST'])
def consent():
    if not current_user.is_authenticated or session.get('consent') == True:
        clear_session_and_logout()

    return render_template('consent.html')

@app.route('/consent/submit/', methods=['POST'])
def consent_submit():
    if not current_user.is_authenticated or session.get('consent') == True:
        print("Not authenticated or consent already given")
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form.get('consent') == 'True':
            current_user.consent = True
            session['consent'] = True
            db.session.commit()
                            
            return redirect(url_for('demographics_survey'))
        else:
            print("Consent not given")
            return clear_session_and_logout()
        
@app.route('/demographics_survey/', methods=['GET', 'POST'])
def demographics_survey():
    if not current_user.is_authenticated or not session.get('consent'):
        return redirect(url_for('clear_session_and_logout'))
    #elif Survey.query.filter_by(mturk_id=session['mturk_id'], type='demographics').first():
        #return redirect(url_for('clear_session_and_logout'))
    else:
        session['survey_page_loaded'] = True
        return render_template('demographics_survey.html')
    
@app.route('/demographics_survey/submit/', methods=['POST'])
def demographics_survey_submit():
    print("Demographics survey submit")
    if not current_user.is_authenticated or not session.get('consent'):
        return redirect(url_for('clear_session_and_logout'))
    
    # Check if the form was already submitted
    #if Survey.query.filter_by(mturk_id=session['mturk_id'], type='demographics').first():
        #return redirect(url_for('clear_session_and_logout'))
    
    if request.method == 'POST':
        
        # Get data from the form as a dictionary
        demographics = {}
        demographics['age'] = request.form.get('q1')
        demographics['gender'] = request.form.get('q2')
        demographics['ethnicity'] = request.form.get('q3')
        demographics['education'] = request.form.get('q4')
        demographics['attention-check'] = request.form.get('q5')
        
        failed_attention_checks = 0
        if demographics['attention-check'] != '4' or demographics['attention-check'] != '5':
            failed_attention_checks += 1
        session['failed_attention_checks'] = failed_attention_checks
        print("Failed attention checks: " + str(failed_attention_checks))
        
        # Save survey to database
        survey = Survey(
            mturk_id = session['mturk_id'],
            type = 'demographics',
            data = demographics,
            timestamp = datetime.now()
        )
        
        db.session.add(survey)
        db.session.commit()
      
    return redirect(url_for('experiment'))

@app.route('/survey/', methods=['GET', 'POST'])
def survey():
    if not current_user.is_authenticated or not session.get('consent'):
        return redirect(url_for('clear_session_and_logout'))
    #elif Survey.query.filter_by(mturk_id=session['mturk_id'], type='demographics').first():
        #return redirect(url_for('clear_session_and_logout'))
    else:
        session['survey_page_loaded'] = True
        return render_template('survey.html')
    
@app.route('/survey/submit/', methods=['POST'])
def survey_submit():
    print("survey submit")
    if not current_user.is_authenticated or not session.get('consent'):
        return redirect(url_for('clear_session_and_logout'))
    
    # Check if the form was already submitted
    #if Survey.query.filter_by(mturk_id=session['mturk_id'], type='demographics').first():
        #return redirect(url_for('clear_session_and_logout'))
    
    if request.method == 'POST':
        
        # Get data from the form as a dictionary
        evaluation = {}
        evaluation['consistency_1'] = request.form.get('q1')
        evaluation['perceived_usefulness_1'] = request.form.get('q2')
        evaluation['perceived_usefulness_2'] = request.form.get('q3')
        evaluation['perceived_usefulness_3'] = request.form.get('q4')
        evaluation['satisfaction_1'] = request.form.get('q5')
        evaluation['satisfaction_2'] = request.form.get('q6')
        evaluation['satisfaction_3'] = request.form.get('q7')
        evaluation['warmth_1'] = request.form.get('q8')
        evaluation['warmth_2'] = request.form.get('q9')
        evaluation['warmth_3'] = request.form.get('q10')
        evaluation['warmth_4'] = request.form.get('q11')
        evaluation['warmth_5'] = request.form.get('q12')
        evaluation['consistency_2'] = request.form.get('q13')
        evaluation['attention-check'] = request.form.get('q14')
        
        
        failed_attention_checks = 0
        if evaluation['attention-check'] != '4' or evaluation['attention-check'] != '5':
            failed_attention_checks += 1
        session['failed_attention_checks'] = failed_attention_checks
        print("Failed attention checks: " + str(failed_attention_checks))
        
        # Save survey to database
        survey = Survey(
            mturk_id = session['mturk_id'],
            type = 'evaluation',
            data = evaluation,
            timestamp = datetime.now()
        )
        
        db.session.add(survey)
        db.session.commit()
      
    return redirect(url_for('experiment'))
    
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

    # Set experiment length
    bandit.num_episodes = 10
    if not current_user.is_authenticated:
        print("User not authenticated.")
        return redirect(url_for('login'))

    session['warmup_started'] = True
    print("Setting experiment page loaded.")
    session['warmup_loaded'] = True

    bandit.reset()

    mturk_id = session.get('mturk_id')

    return render_template('warmup.html', mturk_id=mturk_id)

@app.route('/warmup/submit/', methods=['POST'])
@login_required
def warmupcomplete():
    print("warmup submit")
    if not current_user.is_authenticated or not session.get('consent'):
        return redirect(url_for('clear_session_and_logout'))
    
    # Check if the form was already submitted
    #if Survey.query.filter_by(mturk_id=session['mturk_id'], type='demographics').first():
        #return redirect(url_for('clear_session_and_logout'))
    
    if request.method == 'POST':
    
        bandit.reset()

        mturk_id = session.get('mturk_id')

        warmup_completion = TaskCompletion.query.filter_by(user_id=current_user.mturk_id, task_type='warmup').first()
        if not warmup_completion:
            warmup_completion = TaskCompletion(user_id=mturk_id, task_type='warmup')
            db.session.add(warmup_completion)
            db.session.commit()
        
        warmup_results = {}
        warmup_results['intentions'] = bandit.i.tolist()
        warmup_results['recommendations'] = bandit.r.tolist()
        warmup_results['selections'] = bandit.s.tolist()
        warmup_results['rewards'] = bandit.rewardPerRound.tolist()
        warmup_results['strategy'] = request.form.get('strategy')

        warmup = Task(
            mturk_id = mturk_id,
            task_type = 'warmup',
            task_instance = 1,
            data = warmup_results,
            score = sum(bandit.rewardPerRound),
            completed = True,
            timestamp = datetime.now()        
        )

        db.session.add(warmup)
        db.session.commit()

    return redirect(url_for('experiment'))

@app.route('/task/')
@login_required
def task():
    # Set experiment length
    bandit.num_episodes = 30
    if not current_user.is_authenticated:
        print("User not authenticated.")
        return redirect(url_for('login'))

    session['task_started'] = True
    print("Setting experiment page loaded.")
    session['task_page_loaded'] = True

    bandit.reset()

    mturk_id = session.get('mturk_id')
    return render_template('task.html', mturk_id=mturk_id)

@app.route('/task/submit/', methods=['POST'])
@login_required
def taskcomplete():
    print("task submit")
    if not current_user.is_authenticated or not session.get('consent'):
        return redirect(url_for('clear_session_and_logout'))
    
    # Check if the form was already submitted
    #if Survey.query.filter_by(mturk_id=session['mturk_id'], type='demographics').first():
        #return redirect(url_for('clear_session_and_logout'))
    
    if request.method == 'POST':
    
        bandit.reset()

        mturk_id = session.get('mturk_id')

        task_completion = TaskCompletion.query.filter_by(user_id=current_user.mturk_id, task_type='task').first()
        if not task_completion:
            task_completion = TaskCompletion(user_id=mturk_id, task_type='task')
            db.session.add(task_completion)
            db.session.commit()
        
        task_results = {}
        task_results['intentions'] = bandit.i.tolist()
        task_results['recommendations'] = bandit.r.tolist()
        task_results['selections'] = bandit.s.tolist()
        task_results['rewards'] = bandit.rewardPerRound.tolist()
        #task_results['strategy'] = request.form.get('strategy')

        task = Task(
            mturk_id = mturk_id,
            task_type = 'task',
            task_instance = 1,
            data = task_results,
            score = sum(bandit.rewardPerRound),
            completed = True,
            timestamp = datetime.now()        
        )

        db.session.add(task)
        db.session.commit()

    return redirect(url_for('survey'))

@app.route('/gamecomplete/')
@login_required
def gamecomplete():
    mturk_id = session.get('mturk_id')
    return render_template('gamecomplete.html', mturk_id=mturk_id)

@app.route('/attention_check')
def attention_check():
    atnCheck = request.args.get('atn')
    attentionChecks.append(atnCheck)
    if (atnCheck == 'false') : failed_attention_checks += 1

    return jsonify({'success' : 1})

@app.route('/get_strategy')
def get_strategy():
    q = request.args.get('q', 0)
    a = request.args.get('a', 0)

    return jsonify({'success' : 1})

@app.route('/get_recommendation')
def get_recommendation():
    # get user intention
    user_curr_intention = int(request.args.get('intendedOption', 10))
    # update the intention
    bandit.i[bandit.t] = int(user_curr_intention) 
    # get recommendation
    bandit.recommend_arm()
    # get explanation for recommendation
    expForRec = bandit.getExplanation4Recommendation()
    
    return jsonify({'agents' : bandit.r[bandit.t] + 1, 'cases' : bandit.cases[bandit.t], 'expForRec': expForRec})

@app.route('/get_reward')
def get_reward():
    # get user selection
    selected_option = int(request.args.get('selected_option', 0))
    # get reward
    reward = bandit.pull_arm(selected_option)

    # Update bandit
    bandit.rewardPerRound[bandit.t] = reward;
    bandit.s[bandit.t] = selected_option 
    bandit.y[selected_option] += reward
    bandit.x[selected_option] += 1
    
    expPostSel = bandit.getExplanationPostSelection()

    bandit.t += 1
    bandit.updateLikelihood()

    if(np.sum(bandit.x)==bandit.num_episodes):
        bandit.reset()

    return jsonify({'reward': reward, 'banditY': bandit.y[selected_option], 'banditX': bandit.x[selected_option], 'expPostSel': expPostSel})




