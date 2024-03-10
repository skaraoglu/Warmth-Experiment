from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from app.models import User, Task, Survey
from scipy.stats import ttest_ind, f_oneway, levene

import matplotlib.pyplot as plt


METRIC = 'follow'
# METRIC = 'change'
# mode = 'boxplot'
mode = None
# mode = 'histogram'

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

print("Average utility for condition 0: ", np.mean(users_0_util))
print("Average utility for condition 1: ", np.mean(users_1_util))
print("Average utility for condition 2: ", np.mean(users_2_util))

# print(users_0_follow_all)
# print(users_1_follow_all)
# print(users_2_follow_all)

# print(users_0_follow_half)
# print(users_1_follow_half)
# print(users_2_follow_half)

# print(users_0_follow_third)
# print(users_1_follow_third)
# print(users_2_follow_third)

print("Average proportion of recommendations followed for condition 0: ", np.mean(users_0_follow_all))
print("Average proportion of recommendations followed for condition 1: ", np.mean(users_1_follow_all))
print("Average proportion of recommendations followed for condition 2: ", np.mean(users_2_follow_all))

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
t_stat, p_val = ttest_ind(users_0_util, users_1_util, alternative='greater')
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

t_stat, p_val = ttest_ind(users_0_follow_all, users_1_follow_all, alternative='greater')
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
    plt.figure()
    plt.boxplot([users_2_util, users_1_util, users_0_util])
    plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])

    plt.title('Utility')
    plt.xlabel('Intervention Condition')
    plt.ylabel('Utility')
    plt.show()

    if METRIC == 'follow':
    # Plot proportion of recommendations followed
        plt.figure()
        plt.boxplot([users_2_follow_all, users_1_follow_all, users_0_follow_all])
        plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])

        plt.title('Proportion of Recommendations Followed')
        plt.xlabel('Intervention Condition')
        plt.ylabel('Proportion Followed')
        plt.show()

    if METRIC == 'change':
        
        plt.figure()
        plt.boxplot([users_2_follow_all, users_1_follow_all, users_0_follow_all])
        plt.xticks([1, 2, 3], ['None', 'Warm', 'Cold'])
        
        plt.title('Proportion of Intentions Changed')
        plt.xlabel('Intervention Condition')
        plt.ylabel('Proportion Changed')
        plt.show()
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
    

        
        



