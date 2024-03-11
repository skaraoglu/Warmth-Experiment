from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from app.models import User, Task, Survey
from scipy.stats import ttest_ind, f_oneway, levene

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from numpy import mean


METRIC = 'follow'
# METRIC = 'change'
mode = 'boxplot'
# mode = None
# mode = 'histogram'
mode = 'seaborn'

app = Flask(__name__)
app.config.from_object('app.configuration.DevelopmentConfig')
db = SQLAlchemy(app)

# Create an application context
app.app_context().push()
# Create a session to interact with the database
session = db.session

''' INITIAL DATA PREPROCESSING '''
# Get all users
users = session.query(User).filter_by(experiment_completed=True).all()
print("Number of users: ", len(users))

users_0 = session.query(User).filter_by(experiment_completed=True, intervention_condition=0).all()
print("Number of users in condition 0: ", len(users_0))

users_1 = session.query(User).filter_by(experiment_completed=True, intervention_condition=1).all()
# Remove user 'ATSY6K6MCCNHS' from condition 1
users_1.remove(session.query(User).filter_by(mturk_id='ATSY6K6MCCNHS').first())
print("Number of users in condition 1: ", len(users_1))

users_2 = session.query(User).filter_by(experiment_completed=True, intervention_condition=2).all()
# Remove users 'A1A9FWTXG5F5F9' and 'A3PJMDQ88WL50G' from condition 2
users_2.remove(session.query(User).filter_by(mturk_id='A1A9FWTXG5F5F9').first())
users_2.remove(session.query(User).filter_by(mturk_id='A3PJMDQ88WL50G').first())
print("Number of users in condition 2: ", len(users_2))

users_0_util = []
users_1_util = []
users_2_util = []

users_0_follow_all = []
users_1_follow_all = []
users_2_follow_all = []

users_0_follow_half = [[] for i in range(2)]
users_1_follow_half = [[] for i in range(2)]
users_2_follow_half = [[] for i in range(2)]

users_0_follow_third = [[] for i in range(3)]
users_1_follow_third = [[] for i in range(3)]
users_2_follow_third = [[] for i in range(3)]


for condition in [users_0, users_1, users_2]:
    for user in condition:
        
        score = session.query(Task).filter_by(mturk_id=user.mturk_id, task_type='task').first().score
        if condition == users_0:
            users_0_util.append(score)
        elif condition == users_1:
            users_1_util.append(score)
        elif condition == users_2:
            users_2_util.append(score)
            
        intentions = session.query(Task).filter_by(mturk_id=user.mturk_id, task_type='task').first().data['intentions']
        recommendations = session.query(Task).filter_by(mturk_id=user.mturk_id, task_type='task').first().data['recommendations']
        selections = session.query(Task).filter_by(mturk_id=user.mturk_id, task_type='task').first().data['selections']
        rewards = session.query(Task).filter_by(mturk_id=user.mturk_id, task_type='task').first().data['rewards']
        
        if METRIC == 'follow':
            
            proportion_followed = 0
            for i in range(len(intentions)):
                if recommendations[i] == selections[i]:
                    proportion_followed += 1
            proportion_followed /= len(intentions)
            
            if condition == users_0:
                users_0_follow_all.append(proportion_followed)
            elif condition == users_1:
            
                users_1_follow_all.append(proportion_followed)
            elif condition == users_2:
                users_2_follow_all.append(proportion_followed)
            
            proportion_followed = 0  
            for i in range(0, 15):
                if recommendations[i] == selections[i]:
                    proportion_followed += 1
            proportion_followed /= 15
            if condition == users_0:
                users_0_follow_half[0].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_half[0].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_half[0].append(proportion_followed)
                
            proportion_followed = 0
            for i in range(15, 30):
                if recommendations[i] == selections[i]:
                    proportion_followed += 1
            proportion_followed /= 15
            
            if condition == users_0:
                users_0_follow_half[1].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_half[1].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_half[1].append(proportion_followed)
            
            proportion_followed = 0
            for i in range(0, 10):
                if recommendations[i] == selections[i]:
                    proportion_followed += 1
            proportion_followed /= 10
            if condition == users_0:
                users_0_follow_third[0].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_third[0].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_third[0].append(proportion_followed)
                
            proportion_followed = 0
            for i in range(10, 20):
                if recommendations[i] == selections[i]:
                    proportion_followed += 1
            proportion_followed /= 10
            if condition == users_0:
                users_0_follow_third[1].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_third[1].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_third[1].append(proportion_followed)
            
            proportion_followed = 0
            for i in range(20, 30):
                if recommendations[i] == selections[i]:
                    proportion_followed += 1
            proportion_followed /= 10
            if condition == users_0:
                users_0_follow_third[2].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_third[2].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_third[2].append(proportion_followed)
        
        if METRIC == 'change':
        
            proportion_followed = 0
            for i in range(len(intentions)):
                if intentions[i] != selections[i]:
                    proportion_followed += 1
            proportion_followed /= len(intentions)
            
            if condition == users_0:
                users_0_follow_all.append(proportion_followed)
            elif condition == users_1:

                users_1_follow_all.append(proportion_followed)
            elif condition == users_2:
                users_2_follow_all.append(proportion_followed)
            
            proportion_followed = 0  
            for i in range(0, 15):
                if intentions[i] != selections[i]:
                    proportion_followed += 1
            proportion_followed /= 15
            if condition == users_0:
                users_0_follow_half[0].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_half[0].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_half[0].append(proportion_followed)
                
            proportion_followed = 0
            for i in range(15, 30):
                if intentions[i] != selections[i]:
                    proportion_followed += 1
            proportion_followed /= 15
            
            if condition == users_0:
                users_0_follow_half[1].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_half[1].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_half[1].append(proportion_followed)
            
            proportion_followed = 0
            for i in range(0, 10):
                if intentions[i] != selections[i]:
                    proportion_followed += 1
            proportion_followed /= 10
            if condition == users_0:
                users_0_follow_third[0].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_third[0].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_third[0].append(proportion_followed)
                
            proportion_followed = 0
            for i in range(10, 20):
                if intentions[i] != selections[i]:
                    proportion_followed += 1
            proportion_followed /= 10
            if condition == users_0:
                users_0_follow_third[1].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_third[1].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_third[1].append(proportion_followed)
            
            proportion_followed = 0
            for i in range(20, 30):
                if intentions[i] != selections[i]:
                    proportion_followed += 1
            proportion_followed /= 10
            if condition == users_0:
                users_0_follow_third[2].append(proportion_followed)
            elif condition == users_1:
                users_1_follow_third[2].append(proportion_followed)
            elif condition == users_2:
                users_2_follow_third[2].append(proportion_followed)

print("Average utility for condition 0: ", np.mean(users_0_util), np.std(users_0_util))
print("Average utility for condition 1: ", np.mean(users_1_util), np.std(users_1_util))
print("Average utility for condition 2: ", np.mean(users_2_util), np.std(users_2_util))

# print(users_0_follow_all)
# print(users_1_follow_all)
# print(users_2_follow_all)

# print(users_0_follow_half)
# print(users_1_follow_half)
# print(users_2_follow_half)

# print(users_0_follow_third)
# print(users_1_follow_third)
# print(users_2_follow_third)

print("Average proportion of recommendations followed for condition 0: ", np.mean(users_0_follow_all), np.std(users_0_follow_all))
print("Average proportion of recommendations followed for condition 1: ", np.mean(users_1_follow_all), np.std(users_1_follow_all))
print("Average proportion of recommendations followed for condition 2: ", np.mean(users_2_follow_all), np.std(users_2_follow_all))

print("Average proportion of recommendations followed for first half for condition 0: ", np.mean(users_0_follow_half[0]))
print("Average proportion of recommendations followed for first half for condition 1: ", np.mean(users_1_follow_half[0]))
print("Average proportion of recommendations followed for first half for condition 2: ", np.mean(users_2_follow_half[0]))

print("Average proportion of recommendations followed for second half for condition 0: ", np.mean(users_0_follow_half[1]))
print("Average proportion of recommendations followed for second half for condition 1: ", np.mean(users_1_follow_half[1]))
print("Average proportion of recommendations followed for second half for condition 2: ", np.mean(users_2_follow_half[1]))

print("Average proportion of recommendations followed for first third for condition 0: ", np.mean(users_0_follow_third[0]))
print("Average proportion of recommendations followed for first third for condition 1: ", np.mean(users_1_follow_third[0]))
print("Average proportion of recommendations followed for first third for condition 2: ", np.mean(users_2_follow_third[0]))

print("Average proportion of recommendations followed for second third for condition 0: ", np.mean(users_0_follow_third[1]))
print("Average proportion of recommendations followed for second third for condition 1: ", np.mean(users_1_follow_third[1]))
print("Average proportion of recommendations followed for second third for condition 2: ", np.mean(users_2_follow_third[1]))

print("Average proportion of recommendations followed for third third for condition 0: ", np.mean(users_0_follow_third[2]))
print("Average proportion of recommendations followed for third third for condition 1: ", np.mean(users_1_follow_third[2]))
print("Average proportion of recommendations followed for third third for condition 2: ", np.mean(users_2_follow_third[2]))


''' DATA ANALYSIS of UTILITY'''

# Combine 1 and 0
# users_1_util = users_1_util + users_0_util
      
# Check to see if means are significantly different using ANOVA
f_stat, p_val = f_oneway(users_0_util, users_1_util, users_2_util)
print("F-statistic: " + str(f_stat))
print("P-value: " + str(p_val))

      
      

# Check to see if variances are significantly different using Levene's test
levene_stat, p_val = levene(users_0_util, users_1_util, users_2_util)
print("Levene's test statistic: " + str(levene_stat))
print("P-value: " + str(p_val))
           
# Check to see if means are significantly different using t-tests
t_stat, p_val = ttest_ind(users_0_util, users_1_util)
print("Condition 0 and 1")
print("T-statistic: " + str(t_stat))
print("P-value: " + str(p_val))

t_stat, p_val = ttest_ind(users_2_util, users_0_util, alternative='less')
print("Condition 2 and 0")
print("T-statistic: " + str(t_stat))
print("P-value: " + str(p_val))

t_stat, p_val = ttest_ind(users_2_util, users_1_util, alternative='less')
print("Condition 2 and 1")
print("T-statistic: " + str(t_stat))
print("P-value: " + str(p_val))


''' DATA ANALYSIS of FOLLOWING RECOMMENDATIONS'''

print("~~~~ALL~~~~\n")
# Check to see if means are significantly different using ANOVA
f_stat, p_val = f_oneway(users_0_follow_all, users_1_follow_all, users_2_follow_all)
print("F-statistic: " + str(f_stat))
print("P-value: " + str(p_val))

# Check to see if variances are significantly different using Levene's test
levene_stat, p_val = levene(users_0_follow_all, users_1_follow_all, users_2_follow_all)
print("Levene's test statistic: " + str(levene_stat))
print("P-value: " + str(p_val))

# Check to see if means are significantly different using t-tests

t_stat, p_val = ttest_ind(users_0_follow_all, users_1_follow_all)
print("Condition 0 and 1")
print("T-statistic: " + str(t_stat))
print("P-value: " + str(p_val))

t_stat, p_val = ttest_ind(users_2_follow_all, users_0_follow_all, alternative='less')
print("Condition 2 and 0")
print("T-statistic: " + str(t_stat))
print("P-value: " + str(p_val))

t_stat, p_val = ttest_ind(users_2_follow_all, users_1_follow_all, alternative='less')
print("Condition 2 and 1")
print("T-statistic: " + str(t_stat))
print("P-value: " + str(p_val))

print("~~~~HALF~~~~\n")
for i in range(2):
    print("~~~~HALF " + str(i+1) + "~~~~\n")
    # Check to see if means are significantly different using ANOVA
    f_stat, p_val = f_oneway(users_0_follow_half[i], users_1_follow_half[i], users_2_follow_half[i])
    print("F-statistic: " + str(f_stat))
    print("P-value: " + str(p_val))

    # Check to see if variances are significantly different using Levene's test
    levene_stat, p_val = levene(users_0_follow_half[i], users_1_follow_half[i], users_2_follow_half[i])
    print("Levene's test statistic: " + str(levene_stat))
    print("P-value: " + str(p_val))

    # Check to see if means are significantly different using t-tests

    t_stat, p_val = ttest_ind(users_0_follow_half[i], users_1_follow_half[i], alternative='greater')
    print("Condition 0 and 1")
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))

    t_stat, p_val = ttest_ind(users_2_follow_half[i], users_0_follow_half[i], alternative='less')
    print("Condition 2 and 0")
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))

    t_stat, p_val = ttest_ind(users_2_follow_half[i], users_1_follow_half[i], alternative='less')
    print("Condition 2 and 1")
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))

print("~~~~THIRDS~~~~\n")
for i in range(3):
    print("~~~~THIRD " + str(i+1) + "~~~~\n")
    # Check to see if means are significantly different using ANOVA
    f_stat, p_val = f_oneway(users_0_follow_third[i], users_1_follow_third[i], users_2_follow_third[i])
    print("F-statistic: " + str(f_stat))
    print("P-value: " + str(p_val))

    # Check to see if variances are significantly different using Levene's test
    levene_stat, p_val = levene(users_0_follow_third[i], users_1_follow_third[i], users_2_follow_third[i])
    print("Levene's test statistic: " + str(levene_stat))
    print("P-value: " + str(p_val))

    # Check to see if means are significantly different using t-tests

    t_stat, p_val = ttest_ind(users_0_follow_third[i], users_1_follow_third[i], alternative='greater')
    print("Condition 0 and 1")
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))

    t_stat, p_val = ttest_ind(users_2_follow_third[i], users_0_follow_third[i], alternative='less')
    print("Condition 2 and 0")
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))

    t_stat, p_val = ttest_ind(users_2_follow_third[i], users_1_follow_third[i], alternative='less')
    print("Condition 2 and 1")
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))
    

''' PLOTTING '''


if mode == 'boxplot':
    # Plot utility
    plt.figure(dpi=400)
    plt.boxplot([users_2_util, users_1_util, users_0_util])
    plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])
    means = [np.mean(users_2_util), np.mean(users_1_util), np.mean(users_0_util)]
    plt.plot([1, 2, 3], means, marker='o', markersize=8, color='green', linestyle='None')

    plt.title('Utility Score')
    plt.xlabel('Agent Condition')
    plt.ylabel('Utility')
    
    # Save the figure to /figures
    plt.savefig('figures/utility_score.png', dpi=400)

    if METRIC == 'follow':
    # Plot proportion of recommendations followed
        plt.figure(dpi=400)
        plt.boxplot([users_2_follow_all, users_1_follow_all, users_0_follow_all])
        plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])
        
        means = [np.mean(users_2_follow_all), np.mean(users_1_follow_all), np.mean(users_0_follow_all)]
        plt.plot([1, 2, 3], means, marker='o', markersize=8, color='green', linestyle='None')

        plt.title('Recommendation Score')
        plt.xlabel('Agent Condition')
        plt.ylabel('Proportion')
        
        # Save the figure to /figures
        plt.savefig('figures/recommendation_score.png', dpi=400)

    if METRIC == 'change':
        
        plt.figure(dpi=400)
        plt.boxplot([users_2_follow_all, users_1_follow_all, users_0_follow_all])
        plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])
        
        means = [np.mean(users_2_follow_all), np.mean(users_1_follow_all), np.mean(users_0_follow_all)]
        plt.plot([1, 2, 3], means, marker='o', markersize=8, color='green', linestyle='None')
        
        plt.title('Switching Score')
        plt.xlabel('Agent Condition')
        plt.ylabel('Proportion')
        # Save the figure to /figures
        plt.savefig('figures/switching_score.png', dpi=400)
if mode == 'histogram':
    # Calculate the means
    means = [np.mean(users_2_util), np.mean(users_1_util), np.mean(users_0_util)]
    means_follow = [np.mean(users_2_follow_all), np.mean(users_1_follow_all), np.mean(users_0_follow_all)]
    
    # Plot utility
    plt.figure()
    plt.bar([1, 2, 3], means, color=['blue', 'orange', 'green'])
    plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])
    plt.title('Utility')
    plt.xlabel('Intervention Condition')
    plt.ylabel('Utility')
    plt.show()
    
    if METRIC == 'follow':
        # Plot proportion of recommendations followed
        plt.figure()
        plt.bar([1, 2, 3], means_follow, color=['blue', 'orange', 'green'])
        plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])
        plt.title('Proportion of Recommendations Followed')
        plt.xlabel('Intervention Condition')
        plt.ylabel('Proportion Followed')
        plt.show()
    if METRIC == 'change':
        # Plot proportion of intentions changed
        plt.figure()
        plt.bar([1, 2, 3], means_follow, color=['blue', 'orange', 'green'])
        plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])
        plt.title('Proportion of Intentions Changed')
        plt.xlabel('Intervention Condition')
        plt.ylabel('Proportion Changed')
        plt.show()
if mode == 'seaborn':
    #Make violin plots
    data = [users_2_util, users_1_util, users_0_util]
    labels = ['None', 'Warm', 'Cold']
    df = pd.DataFrame(data).T  # Transpose the DataFrame to align with your data
    df.columns = labels  # Set column names
    df = df.melt(var_name='Intervention Condition', value_name='Utility')
    ax = sns.violinplot(x='Intervention Condition', y='Utility', data=df)
    
    # Add the mean
    means = [np.mean(users_2_util), np.mean(users_1_util), np.mean(users_0_util)]
    ax.plot([0, 1, 2], means, marker='o', markersize=5, color='#c99342', linestyle='None')
    
    fig = ax.get_figure()
    fig.savefig('figures/utility_violin.png', dpi=400)
    
    # Clear the seaborn plot
    plt.clf()
    
    if METRIC == 'follow':
        data = [users_2_follow_all, users_1_follow_all, users_0_follow_all]
        labels = ['None', 'Warm', 'Cold']
        df = pd.DataFrame(data).T
        df.columns = labels
        df = df.melt(var_name='Intervention Condition', value_name='Proportion')
        ax = sns.violinplot(x='Intervention Condition', y='Proportion', data=df)
        
        # Add the mean
        means = [np.mean(users_2_follow_all), np.mean(users_1_follow_all), np.mean(users_0_follow_all)]
        ax.plot([0, 1, 2], means, marker='o', markersize=5, color='#c99342', linestyle='None')
        
        fig = ax.get_figure()
        fig.savefig('figures/follow_violin.png', dpi=400)
        
        plt.clf()
    
    
    if METRIC == 'change':
        data = [users_2_follow_all, users_1_follow_all, users_0_follow_all]
        labels = ['None', 'Warm', 'Cold']
        df = pd.DataFrame(data).T
        df.columns = labels
        df = df.melt(var_name='Intervention Condition', value_name='Proportion')
        ax = sns.violinplot(x='Intervention Condition', y='Proportion', data=df)
        
        # Add the mean
        means = [np.mean(users_2_follow_all), np.mean(users_1_follow_all), np.mean(users_0_follow_all)]
        ax.plot([0, 1, 2], means, marker='o', markersize=5, color='#c99342', linestyle='None')
        
        fig = ax.get_figure()
        fig.savefig('figures/change_violin.png', dpi=400)
        
        plt.clf()
    
    # Save the figure to /figures
    
''' SURVEY DATA ANALYSIS '''

users_0_survey = [[] for i in range(13)]
users_1_survey = [[] for i in range(13)]
users_2_survey = [[] for i in range(13)]

users_0_survey_means = [[] for i in range(4)]
users_1_survey_means = [[] for i in range(4)]
users_2_survey_means = [[] for i in range(4)]

for condition in [users_0, users_1, users_2]:
    for user in condition:
        survey = session.query(Survey).filter_by(mturk_id=user.mturk_id, type='evaluation').first()
        # {"consistency_1": "5", "perceived_usefulness_1": "2",
        # "perceived_usefulness_2": "4", "perceived_usefulness_3": "5",
        # "satisfaction_1": "4", "satisfaction_2": "5",
        # "satisfaction_3": "4", "warmth_1": "5", "warmth_2": "5",
        # "warmth_3": "4", "warmth_4": "4", "warmth_5": "5",
        # "consistency_2": "1", "attention-check": "5"}
        
        # Take the average of the ratings
        consistency = (int(survey.data['consistency_1']) + int(survey.data['consistency_2'])) / 2
        perceived_usefulness = (int(survey.data['perceived_usefulness_1']) + int(survey.data['perceived_usefulness_2']) + int(survey.data['perceived_usefulness_3'])) / 3
        satisfaction = (int(survey.data['satisfaction_1']) + int(survey.data['satisfaction_2']) + int(survey.data['satisfaction_3'])) / 3
        warmth = (int(survey.data['warmth_1']) + int(survey.data['warmth_2']) + int(survey.data['warmth_3']) + int(survey.data['warmth_4']) + int(survey.data['warmth_5'])) / 5
        
        if condition == users_0:
            users_0_survey_means[0].append(consistency)
            users_0_survey_means[1].append(perceived_usefulness)
            users_0_survey_means[2].append(satisfaction)
            users_0_survey_means[3].append(warmth)
        elif condition == users_1:
            users_1_survey_means[0].append(consistency)
            users_1_survey_means[1].append(perceived_usefulness)
            users_1_survey_means[2].append(satisfaction)
            users_1_survey_means[3].append(warmth)
        elif condition == users_2:
            users_2_survey_means[0].append(consistency)
            users_2_survey_means[1].append(perceived_usefulness)
            users_2_survey_means[2].append(satisfaction)
            users_2_survey_means[3].append(warmth)
        
        # Also just save each of the ratings
        
        # Convert the dict to a list
        survey_data = list(survey.data.values())
        for i in range(13):
            if condition == users_0:
                users_0_survey[i].append(int(survey_data[i]))
            elif condition == users_1:
                users_1_survey[i].append(int(survey_data[i]))
            elif condition == users_2:
                users_2_survey[i].append(int(survey_data[i]))


for i in range(4):
    # Check to see if means are significantly different using ANOVA
    f_stat, p_val = f_oneway(users_0_survey_means[i], users_1_survey_means[i], users_2_survey_means[i])
    print("F-statistic for survey mean " + str(i) + ": " + str(f_stat))
    print("P-value for survey mean " + str(i) + ": " + str(p_val))
    
    # Check to see if variances are significantly different using Levene's test
    levene_stat, p_val = levene(users_0_survey_means[i], users_1_survey_means[i], users_2_survey_means[i])
    print("Levene's test statistic for survey mean " + str(i) + ": " + str(levene_stat))
    print("P-value for survey mean " + str(i) + ": " + str(p_val))
    
    # Check to see if means are significantly different using t-tests
    t_stat, p_val = ttest_ind(users_0_survey_means[i], users_1_survey_means[i])
    print("Condition 0 and 1 for survey mean " + str(i))
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))
    
    t_stat, p_val = ttest_ind(users_2_survey_means[i], users_0_survey_means[i])
    print("Condition 2 and 0 for survey mean " + str(i))
    print("T-statistic: " + str(t_stat))
    
    t_stat, p_val = ttest_ind(users_2_survey_means[i], users_1_survey_means[i])
    print("Condition 2 and 1 for survey mean " + str(i))
    
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))
    
for i in range(13):
    
    # Check to see if means are significantly different using ANOVA
    f_stat, p_val = f_oneway(users_0_survey[i], users_1_survey[i], users_2_survey[i])
    print("F-statistic for survey " + str(i) + ": " + str(f_stat))
    print("P-value for survey " + str(i) + ": " + str(p_val))
    
    # Check to see if variances are significantly different using Levene's test
    levene_stat, p_val = levene(users_0_survey[i], users_1_survey[i], users_2_survey[i])
    print("Levene's test statistic for survey " + str(i) + ": " + str(levene_stat))
    print("P-value for survey " + str(i) + ": " + str(p_val))
    
    # Check to see if means are significantly different using t-tests
    t_stat, p_val = ttest_ind(users_0_survey[i], users_1_survey[i])
    print("Condition 0 and 1 for survey " + str(i))
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))
    
    t_stat, p_val = ttest_ind(users_2_survey[i], users_0_survey[i])
    print("Condition 2 and 0 for survey " + str(i))
    print("T-statistic: " + str(t_stat))
    
    t_stat, p_val = ttest_ind(users_2_survey[i], users_1_survey[i])
    print("Condition 2 and 1 for survey " + str(i))
    
    print("T-statistic: " + str(t_stat))
    print("P-value: " + str(p_val))
    
''' DEMOGRAPHICS '''

def demographics(users_0, users_1, users_2):
    
    # Initialize counters for gender categories
    female_count = 0
    male_count = 0
    other_count = 0
    age_18_24 = 0
    age_25_34 = 0
    age_35_44 = 0
    age_45_54 = 0
    age_55_64 = 0
    age_65 = 0
    white = 0 
    black = 0 
    asian = 0
    hispanic = 0
    native = 0 
    race_other = 0
    
    education_none = 0
    education_hs = 0
    education_some_college = 0
    education_associate = 0
    education_bachelors = 0
    education_masters = 0
    education_phd = 0
    
    # Iterate through users and parse survey demographics JSON
    for group in [users_0, users_1, users_2]:
        users_list = users_0 + users_1 + users_2
        for user in group:
            demographics = session.query(Survey).filter_by(mturk_id=user.mturk_id, type="demographics").first()
            gender = demographics.data['gender']
            
            if gender == "Female":
                female_count += 1
            elif gender == "Male":
                male_count += 1
            else:
                other_count += 1
                
            age = demographics.data['age']
            
            if age == "18-24":
                age_18_24 += 1
            elif age == "25-34":
                age_25_34 += 1
            elif age == "35-44":
                age_35_44 += 1
            elif age == "45-54":
                age_45_54 += 1
            elif age == "55-64":
                age_55_64 += 1
            else:
                age_65 += 1
                
            education = demographics.data['education']
            
            if education == "Less than high school":
                education_none += 1
            elif education == "High school":
                education_hs += 1
            elif education == "Some college, no degree":
                education_some_college += 1
            elif education == "Associate degree":
                education_associate += 1
            elif education == "Bachelor's degree":
                education_bachelors += 1
            elif education == "Master's/Graduate Degree":
                education_masters += 1
            else:
                education_phd += 1
                
            # Race
            
            race = demographics.data['ethnicity']
            
            if race == "White":
                white += 1
            elif race == "Hispanic/Latino":
                hispanic += 1
            elif race == "Black or African American":
                black += 1
            elif race == "Native or American Indian":
                native += 1
            elif race == "Asian or Pacific Islander":
                asian += 1
            else:
                race_other += 1
                
    male_count /= len(users_list)
    female_count /= len(users_list)
    other_count /= len(users_list)
    age_18_24 /= len(users_list)
    age_25_34 /= len(users_list)
    age_35_44 /= len(users_list)
    age_45_54 /= len(users_list)
    age_55_64 /= len(users_list)
    age_65 /= len(users_list)
    white /= len(users_list)
    black /= len(users_list)
    asian /= len(users_list)
    hispanic /= len(users_list)
    native /= len(users_list)
    race_other /= len(users_list)
    education_none /= len(users_list)
    education_hs /= len(users_list)
    education_some_college /= len(users_list)
    education_associate /= len(users_list)
    education_bachelors /= len(users_list)
    education_masters /= len(users_list)
    education_phd /= len(users_list)
            
            
            
    
    print("Number of female users: " + str(female_count))
    print("Number of male users: " + str(male_count))
    print("Number of users with other gender: " + str(other_count))
    
    print("Number 18-24 " + str(age_18_24))
    print("Number 25-34 " + str(age_25_34))
    print("Number 35-44 " + str(age_35_44))
    print("Number 45-54 " + str(age_45_54))
    print("Number 55-64 " + str(age_55_64))
    print("Number 65+ " + str(age_65))
    
    print("Number with no education: " + str(education_none))
    print("Number with high school education: " + str(education_hs))
    print("Number with some college education: " + str(education_some_college))
    print("Number with associate degree: " + str(education_associate))
    print("Number with bachelor's degree: " + str(education_bachelors))
    print("Number with master's degree: " + str(education_masters))
    print("Number with PhD: " + str(education_phd))
    
    print("Percent white: " + str(white))
    print("Percent black: " + str(black))
    print("Percent asian: " + str(asian))
    print("Percent hispanic: " + str(hispanic))
    print("Percent native: " + str(native))
    print("Percent other: " + str(race_other))
    
    
        
        
demographics(users_0, users_1, users_2)


