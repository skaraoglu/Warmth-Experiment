import numpy as np
import random
import math
from scipy.optimize import fsolve
from scipy.integrate import quad
from scipy.stats import expon
class Bandit:
    def __init__(self, num_arms, num_episodes, beta_vals=None):
        np.random.seed(seed=62)
        self.num_arms = num_arms
        self.num_episodes = num_episodes
        if beta_vals is None:
            self.beta_vals = np.random.uniform(0, 1, num_arms)
        else:
            self.beta_vals = beta_vals
        self.x = np.zeros(num_arms) # Number of pulls for each arm
        self.y = np.zeros(num_arms) # Rewards for each arm
        self.r = np.zeros(num_arms) # Recommendations for each arm
        self.i = np.zeros(num_episodes) # Intentions for each round
        self.s = np.zeros(num_episodes) # Selections for each round
        self.t = np.count_nonzero(self.x)

        self.l = np.zeros(num_episodes) # Likelihood that the user adopts
        self.l[0] = 1 # Complaint - Likelihood
        self.condition = 0 # Cold = 0 or Warm = 1
        self.cases = np.zeros(num_episodes) # Cases for each round

    def updateLikelihood(self, delta=.75):
        self.l[self.t] = delta * self.l[self.t-1] + (1 - delta) * (1 if self.i[self.t] == self.s[self.t] else 0)
         
    # What is curr_pull?
    def recommend_arm(self, curr_pull):
        action = 0
        # If arm pulled less than two times
        if self.x[self.i - 1] < 2: # Why - 1?
            action = self.i
            self.cases[self.t] = 1
            return action
        
        arms_to_recommend = []
        for i in range(self.num_arms):
            # If arm pulled less than two times and recommended less than three times
            if self.x[i] < 2 and self.r[i] < 3:
                arms_to_recommend.append(i + 1)

        if arms_to_recommend:
            action = random.choice(arms_to_recommend)
            self.cases[self.t] = 2
            return action

        min_weight = 0.5
        max_weight = 0.9
        weight = min_weight + curr_pull * (max_weight - min_weight) / self.num_episodes

        max_value = 0.0

        for i in range(self.num_arms):
            i_value = weight * (self.y[i] / (self.x[i] if self.x[i] != 0 else 0.1))
            i_value += (1 - weight) * math.sqrt(math.log(30) / (self.x[i] if self.x[i] != 0 else 0.1))

            if max_value < i_value:
                max_value = i_value
                action = i + 1
            
        self.cases[self.t] = 3

        return action
        
    def pull_arm(self, arm_index):
        reward = np.random.exponential(self.beta_vals[arm_index])
        return reward
    
    def reset(self):
        self.S = np.zeros(self.num_arms)
        self.F = np.zeros(self.num_arms)

    def getExplanation4Recommendation(currentRecommendation):
        # self.condition is Condition
        # self.l is Complaint - Likelihood
        # self.i[self.t] is Intention for time t (Current)
        # self.s[self.t] is Selection for time t (Current)
        # average reward for recommendation is sum(self.y[x]) / len(self.y[x])
        # self.y[self.t] is Reward for time t (Current)
        return
    def getExplanationPostSelection(currentRecommendation):
        # self.condition is Condition
        # self.l is Complaint - Likelihood
        # self.i[self.t] is Intention for time t (Current)
        # self.s[self.t] is Selection for time t (Current)
        # average reward for recommendation is sum(self.y[x]) / len(self.y[x])
        # self.y[self.t] is Reward for time t (Current)
        return
    

    '''
    def UCB(self):
        for i in range(self.num_arms):
            if self.F[i] == 0:
                return i + 1
        ucb_values = self.S + np.sqrt(2 * np.log(np.sum(self.F)) / (self.F))
        action = np.argmax(ucb_values) + 1
        return action            
    '''