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

attentionChecks = []
_beta = [0.9, 0.85, 0.75, 0.8, 0.3, 0.2]
num_arms = 6  # Number of stock options
num_episodes = 30
money = 0
coldCondition = 0
warmCondition = 1
noExpCondition = 2

def assign_condition():
    
    '''SELECT INTERVENTION CONDITION'''
    users0 = User.query.filter_by(intervention_condition=0, experiment_completed = True).filter(User.mturk_id.like('A%')).all()
    users1 = User.query.filter_by(intervention_condition=1, experiment_completed = True).filter(User.mturk_id.like('A%')).all()
    users2 = User.query.filter_by(intervention_condition=2, experiment_completed = True).filter(User.mturk_id.like('A%')).all()
    # Select the intervention condition with the fewest users
    min_users = min(len(users0), len(users1), len(users2))
    if len(users1) == min_users:
        cond = 1
    elif len(users0) == min_users:
        cond = 0
    elif len(users2) == min_users:
        cond = 2
        
    # Add to user model
    user = User.query.filter_by(mturk_id=session['mturk_id']).first()
    user.intervention_condition = cond
    db.session.commit()
    return cond

    # # Read the condition counts from the file
    # try:
    #     with open('cond_counts.txt', 'r') as f:
    #         condition_counts = list(map(int, f.read().split()))
    #         if not condition_counts:
    #             condition_counts = [0, 0, 0]
    # except FileNotFoundError:
    #     # If the file doesn't exist, initialize the condition counts
    #     condition_counts = [0, 0, 0]

    # # Find the condition with the minimum count
    # condition = condition_counts.index(min(condition_counts))

    # # Increment the count for the assigned condition
    # condition_counts[condition] += 1
    # print(condition_counts)
    # # Write the updated condition counts back to the file
    # with open('cond_counts.txt', 'w') as f:
    #     f.write(' '.join(map(str, condition_counts)))

    # return condition

def get_bandit():
    # Get the bandit object from the session
    b = session['bandit']
    from app.bandit import Bandit
    return Bandit.from_json(b)

def log_experiment(message):
    path = 'logs/'
    filename = f'experiment_{current_user.mturk_id}.txt'
    timestamp = datetime.now().strftime('%m-%d %H:%M:%S')
    with open(path + filename, 'a', encoding='utf-8') as f:
        f.write(f'{message} - {timestamp}\n')

def attention_check_fail():
    fails = session.get('failed_attention_checks')
    if fails > 1:
        log_experiment(f'{current_user.mturk_id} has failed attention checks {fails} times. Logging out user.')
        clear_session_and_logout()
    else:
        return

#Utility function to clear session data and logout
@app.route('/clear_session_and_logout/')
def clear_session_and_logout():
    logout_user()
    session.clear()
    flash('You have either run out of time or have violated the terms of the experiment.')
    return redirect(url_for('login'))

@app.route('/attention_failed/')
def attention_failed():
    logout_user()
    session.clear()
    flash('You have failed 2 attention checks.')
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
        log_experiment(f'{current_user.mturk_id} is authenticated.')
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
            log_experiment(f'{mturk_id} is registered in the system.')
            session['mturk_id'] = mturk_id
            session['login_completed'] = True
            session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session['expiry_time'] = (datetime.now() + timedelta(minutes=45)).strftime('%Y-%m-%d %H:%M:%S')
            session['failed_attention_checks'] = 0

            return redirect(url_for('consent'))
        else:
            if user.experiment_completed:
                log_experiment(f'{mturk_id} has already completed the experiment.')
                flash('Error! You have already completed the experiment.')
            else:
                log_experiment(f'{mturk_id} is already registered in the system.')
                flash('Error! MTurk ID already used. Contact the researchers if you believe this to be in error.')
            return redirect(url_for('login'))

    return render_template('login.html', title='Sign In', form=form)

@app.route('/consent/', methods=['GET', 'POST'])
def consent():
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent already given. Step: consent.')
        clear_session_and_logout()

    return render_template('consent.html')

@app.route('/consent/submit/', methods=['POST'])
def consent_submit():
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent already given. Step: consent_submit.')
        print("Not authenticated or consent already given")
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form.get('consent') == 'True':
            current_user.consent = True
            session['consent'] = True
            db.session.commit()
            from app import bandit
            cond = assign_condition()
            
            # # Save condition to User model
            # user = User.query.filter_by(mturk_id=session['mturk_id']).first()
            # user.intervention_condition = cond
            # db.session.commit()
            
            bandit = bandit.Bandit(num_arms,
                                   num_episodes,
                                   beta_vals=_beta,
                                   x = np.zeros(num_arms),
                                   y = np.zeros(num_arms),
                                   rewardPerRound = np.zeros(num_episodes),
                                   r = np.zeros(num_episodes),
                                   i = np.zeros(num_episodes),
                                   s = np.zeros(num_episodes),
                                   t = 0,
                                   l = np.zeros(num_episodes),
                                   condition=cond,
                                   cases = np.zeros(num_episodes),
            )
                                   
            session['bandit'] = bandit.to_json()
        
            log_experiment(f'{current_user.mturk_id} is given consent.')
                            
            return redirect(url_for('demographics_survey'))
        else:
            print("Consent not given")
            log_experiment(f'{current_user.mturk_id} is not given consent.')
            return clear_session_and_logout()
        
@app.route('/demographics_survey/', methods=['GET', 'POST'])
def demographics_survey():
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent not given. Step: demographics_survey.')
        return redirect(url_for('clear_session_and_logout'))
    #elif Survey.query.filter_by(mturk_id=session['mturk_id'], type='demographics').first():
        #return redirect(url_for('clear_session_and_logout'))
    else:
        session['survey_page_loaded'] = True
        log_experiment(f'{current_user.mturk_id} is on demographics survey page.')
        return render_template('demographics_survey.html')
    
@app.route('/demographics_survey/submit/', methods=['POST'])
def demographics_survey_submit():
    print("Demographics survey submit")
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent not given. Step: demographics_survey_submit.')
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
        
        if demographics['attention-check'] == '1' or demographics['attention-check'] == '2' or demographics['attention-check'] == '3':
            fails = session.get('failed_attention_checks') + 1
            session['failed_attention_checks'] = fails
            print("Failed attention checks: " + str(session.get('failed_attention_checks')))     
        
        # Save survey to database
        survey = Survey(
            mturk_id = session['mturk_id'],
            type = 'demographics',
            data = demographics,
            timestamp = datetime.now()
        )
        
        db.session.add(survey)
        db.session.commit()
        log_experiment(f'{current_user.mturk_id} has submitted demographics survey.')
        log_experiment('Demographics: ' + str(demographics))
      
    return redirect(url_for('experiment'))

@app.route('/survey/', methods=['GET', 'POST'])
def survey():
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent not given. Step: survey.')
        return redirect(url_for('clear_session_and_logout'))
    #elif Survey.query.filter_by(mturk_id=session['mturk_id'], type='demographics').first():
        #return redirect(url_for('clear_session_and_logout'))
    else:
        session['survey_page_loaded'] = True
        log_experiment(f'{current_user.mturk_id} is on survey page.')
        return render_template('survey.html')
    
@app.route('/survey/submit/', methods=['POST'])
def survey_submit():
    print("survey submit")
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent not given. Step: survey_submit.')
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
        
        
        if evaluation['attention-check'] == '1' or evaluation['attention-check'] == '2' or evaluation['attention-check'] == '3':
            fails = session.get('failed_attention_checks') + 1
            session['failed_attention_checks'] = fails
            print("Failed attention checks: " + str(session.get('failed_attention_checks')))
        
        # Save survey to database
        survey = Survey(
            mturk_id = session['mturk_id'],
            type = 'evaluation',
            data = evaluation,
            timestamp = datetime.now()
        )
                
        db.session.add(survey)
        db.session.commit()
        log_experiment(f'{current_user.mturk_id} has submitted survey.')
        log_experiment('Evaluation: ' + str(evaluation))
      
    return redirect(url_for('gamecomplete'))
    
@app.route('/experiment/')
@login_required
def experiment():
    if not current_user.is_authenticated:
        print("User not authenticated.")
        log_experiment(f'{current_user.mturk_id} is not authenticated. Step: experiment.')
        return redirect(url_for('login'))

    if session.get('exp_page_loaded'):
        print("User is reloading experiment page.")
        log_experiment(f'{current_user.mturk_id} is reloading experiment page.')
        return redirect(url_for('clear_session_and_logout'))

    session['task_started'] = False
    session['endgame_loaded'] = False
    print("Setting experiment page loaded.")
    session['exp_page_loaded'] = True
    t_c = is_task_completed('tutorial')
    w_c = is_task_completed('warmup')

    mturk_id = session.get('mturk_id')
    log_experiment(f'{current_user.mturk_id} is on experiment page. Tutorial completed: {t_c}, Warmup completed: {w_c}. Step: experiment.')

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
        log_experiment(f'{current_user.mturk_id} is not authenticated. Step: tutorial.')
        return redirect(url_for('login'))

    mturk_id = session.get('mturk_id')

    #Change tutorial task to completed
    tutorial_completion = TaskCompletion.query.filter_by(user_id=current_user.mturk_id, task_type='tutorial').first()
    if not tutorial_completion:
        tutorial_completion = TaskCompletion(user_id=mturk_id, task_type='tutorial')
        db.session.add(tutorial_completion)
        db.session.commit()

    log_experiment(f'{current_user.mturk_id} is on tutorial page. Step: tutorial.')

    return render_template('tutorial.html', mturk_id=mturk_id)

@app.route('/warmup/')
@login_required
def warmup():
    if session.get('warmup_loaded'):
        print("User is reloading warmup page.")
        log_experiment(f'{current_user.mturk_id} is reloading warmup page. Step: warmup.')
        return redirect(url_for('clear_session_and_logout'))

    #Get the warmup start time
    session['warmup_start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Set experiment length
    
    bandit = get_bandit()
    bandit.num_episodes = 10
    warmup_beta = [0.75, 0.8, 0.2, 0.85, 0.3, 0.9]
    bandit.beta_vals = warmup_beta
    # bandit.reset()
    if not current_user.is_authenticated:
        print("User not authenticated.")
        return redirect(url_for('login'))

    session['warmup_started'] = True
    print("Setting experiment page loaded.")
    session['warmup_loaded'] = True

    mturk_id = session.get('mturk_id')
    log_experiment(f'{current_user.mturk_id} is on warmup page. Step: warmup.')

    # Save bandit
    session['bandit'] = bandit.to_json()
    return render_template('warmup.html', mturk_id=mturk_id)

@app.route('/warmup/submit/', methods=['POST'])
@login_required
def warmupcomplete():
    print("warmup submit")
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent not given. Step: warmupcomplete.')
        return redirect(url_for('clear_session_and_logout'))
    
    # Check if the form was already submitted
    if is_task_completed('warmup'):
        log_experiment(f'{current_user.mturk_id} has already submitted warmup. Step: warmupcomplete.')
        return redirect(url_for('clear_session_and_logout'))
    
    if request.method == 'POST':
        mturk_id = session.get('mturk_id')

        warmup_completion = TaskCompletion.query.filter_by(user_id=current_user.mturk_id, task_type='warmup').first()
        if not warmup_completion:
            warmup_completion = TaskCompletion(user_id=mturk_id, task_type='warmup')
            db.session.add(warmup_completion)
            db.session.commit()
        
        bandit = get_bandit()
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
        log_experiment(f'{current_user.mturk_id} has submitted warmup. Step: warmupcomplete.')
        log_experiment('Warmup: ' + str(warmup_results))

        # bandit.reset()
        session['bandit'] = bandit.to_json()

    session['exp_page_loaded'] = False

    return redirect(url_for('experiment'))

@app.route('/task/')
@login_required
def task():
    # Set experiment length
    bandit = get_bandit()
    bandit.num_episodes = 30
    bandit.beta_vals = _beta
    bandit.reset()
    session['bandit'] = bandit.to_json()
    if not current_user.is_authenticated:
        print("User not authenticated.")
        log_experiment(f'{current_user.mturk_id} is not authenticated. Step: task.')
        return redirect(url_for('login'))
    
    if session.get('task_page_loaded'):
        print("User is reloading experiment page.")
        log_experiment(f'{current_user.mturk_id} is reloading experiment page. Step: task.')
        return redirect(url_for('clear_session_and_logout'))

    session['task_started'] = True
    print("Setting experiment page loaded.")
    session['task_page_loaded'] = True

    mturk_id = session.get('mturk_id')
    log_experiment(f'{current_user.mturk_id} is on task page. Step: task.')

    return render_template('task.html', mturk_id=mturk_id)

@app.route('/task/submit/', methods=['POST'])
@login_required
def taskcomplete():
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent not given. Step: taskcomplete.')
        return redirect(url_for('clear_session_and_logout'))
    
    # Check if the form was already submitted
    if is_task_completed('task'):
        log_experiment(f'{current_user.mturk_id} has already submitted task. Step: taskcomplete.')
        return redirect(url_for('clear_session_and_logout'))
    
    if request.method == 'POST':
        mturk_id = session.get('mturk_id')
        bandit = get_bandit()
        money = bandit.calculateMoney()

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
        task_results['money'] = money
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
        session['bandit'] = bandit.to_json()
        log_experiment(f'{current_user.mturk_id} has submitted task. Step: taskcomplete.')
        log_experiment('Task: ' + str(task_results))

    return redirect(url_for('survey'))

@app.route('/gamecomplete/')
@login_required
def gamecomplete():
    
    
    print(session.get('endgame_loaded'))
    mturk_id = session.get('mturk_id')
    bandit = get_bandit()
    money = bandit.calculateMoney()
    rewardC = rewardCode()
    log_experiment(f'{current_user.mturk_id} is on game complete page. Step: gamecomplete.')
    log_experiment('Reward code: ' + str(rewardC))
    log_experiment('Money earned: ' + str(money))
    #bandit.reset()
    session['bandit'] = bandit.to_json()
    user = User.query.filter_by(mturk_id=mturk_id).first()
    user.experiment_completed = True
    db.session.commit()

    return render_template('gamecomplete.html', mturk_id=mturk_id, money_earned=money, rewardC=rewardC)

@app.route('/gamecomplete/submit/', methods=['POST'])
@login_required
def expcomplete():
    if not current_user.is_authenticated:
        log_experiment(f'{current_user.mturk_id} is not authenticated or consent not given. Step: taskcomplete.')
        return redirect(url_for('clear_session_and_logout'))
    
    if request.method == 'POST':
        
        feedback = {}
        feedback['feedback'] = request.form.get('feedback')        
        # Save survey to database
        survey = Survey(
            mturk_id = session['mturk_id'],
            type = 'feedback',
            data = feedback,
            timestamp = datetime.now()
        )
        
        db.session.add(survey)
        db.session.commit()
        log_experiment(f'{current_user.mturk_id} has submitted feedback survey.')
        log_experiment('Feedback: ' + str(feedback))
     
    return render_template('thankyou.html')

def rewardCode():
    return ''.join(random.choice('1234567890') for i in range(10))

@app.route('/attention_check')
def attention_check():
    atnCheck = request.args.get('atn')
    if (atnCheck == 'false') : 
        fails = session.get('failed_attention_checks') + 1
        session['failed_attention_checks'] = fails
        print("Failed attention checks: " + str(session.get('failed_attention_checks')))
        if fails > 1:
            log_experiment(f'{current_user.mturk_id} has failed attention checks {fails} times. Logging out user.')
            return jsonify({'redirect': url_for('attention_failed')})

    log_experiment(f'Attention check: {atnCheck}')

    return jsonify({'success' : 1})

@app.route('/get_strategy')
def get_strategy():
    q = request.args.get('q', 0)
    a = request.args.get('a', 0)
    strategy = {}
    strategy['question'] = q
    strategy['strategy'] = a    
    # Save survey to database
    survey = Survey(
        mturk_id = session['mturk_id'],
        type = 'strategy',
        data = strategy,
        timestamp = datetime.now()
    )
    
    db.session.add(survey)
    db.session.commit()
    log_experiment(f'Strategy: {q} - {a}')

    return jsonify({'success' : 1})

@app.route('/get_recommendation')
def get_recommendation():
    # get user intention
    user_curr_intention = int(request.args.get('intendedOption', 10))
    # update the intention
    bandit = get_bandit()
    bandit.i[bandit.t] = int(user_curr_intention) 
    # get recommendation
    bandit.recommend_arm()
    # get explanation for recommendation
    if(bandit.condition == noExpCondition):
        expForRec = "No explanation"
    else:
        expForRec = bandit.getExplanation4Recommendation()
    log_experiment(f'Step: {bandit.t}, Intention: {bandit.i[bandit.t]}, Recommendation: {bandit.r[bandit.t]}, Explanation for Recommendation: {expForRec}, Condition: {bandit.condition}')
    session['bandit'] = bandit.to_json()
    return jsonify({'agents' : bandit.r[bandit.t] + 1, 'cases' : bandit.cases[bandit.t], 'expForRec': expForRec, 'condition': bandit.condition})

@app.route('/get_reward')
def get_reward():
    # get user selection
    selected_option = int(request.args.get('selected_option', 0))
    # get reward
    bandit = get_bandit()
    reward = bandit.pull_arm(selected_option)

    # Update bandit
    bandit.rewardPerRound[bandit.t] = reward;
    bandit.s[bandit.t] = selected_option 
    bandit.y[selected_option] += reward
    bandit.x[selected_option] += 1
    
    if(bandit.condition == noExpCondition):
        expPostSel = "No explanation"
    else:
        expPostSel = bandit.getExplanationPostSelection()

    bandit.updateLikelihood()
    log_experiment(f'Step: {bandit.t}, Selection: {bandit.s[bandit.t]}, Reward: {reward}, Likelihood: {bandit.l[bandit.t]}, Explanation Post Selection: {expPostSel}')
    bandit.t += 1
    print("bandit.t in get reward: " + str(bandit.t))
    session['bandit'] = bandit.to_json()
    return jsonify({'reward': reward, 'banditY': bandit.y[selected_option], 'banditX': bandit.x[selected_option], 'expPostSel': expPostSel, 'money': bandit.calculateMoney()})




