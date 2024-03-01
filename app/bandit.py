import numpy as np
import random
import math
from .recommendation import agent_recommender, agent_feedback

class Bandit:

    def __init__(self, num_arms, num_episodes, condition, beta_vals=None):
        np.random.seed(seed=62)
        self.num_arms = num_arms
        self.num_episodes = num_episodes
        if beta_vals is None:
            self.beta_vals = np.random.uniform(0, 1, num_arms)
        else:
            self.beta_vals = beta_vals
        self.x = np.zeros(num_arms) # Number of pulls for each arm
        self.y = np.zeros(num_arms) # Rewards received each round
        self.rewardPerRound = np.zeros(num_episodes) # Rewards received each round        
        self.r = np.zeros(num_episodes) # Recommendations for each round
        self.i = np.zeros(num_episodes) # Intentions for each round
        self.s = np.zeros(num_episodes) # Selections for each round
        self.t = 0

        self.l = np.zeros(num_episodes) # Likelihood that the user adopts
        #self.l[0] = 1 # Complaint - Likelihood
        self.condition = condition # Cold = 0 or Warm = 1
        self.cases = np.zeros(num_episodes) # Cases for each round

    def updateLikelihood(self, delta=.75):
        if(self.t < self.num_episodes):
            self.l[self.t] = delta * self.l[self.t-1] + (1 - delta) * (1 if self.i[self.t] == self.s[self.t] else 0)
    
    def recommend_arm(self):
        self.r[self.t] = 0
        # case 1:
        if (self.x[int(self.i[self.t])] < 1 and np.count_nonzero(self.r[:self.t] == int(self.i[self.t])) == 0):
            self.r[self.t] = self.i[self.t]
            self.cases[self.t] = 1
            return
        
        arms_to_recommend = []
        for i in range(self.num_arms):
            if self.x[i] < 1 and np.count_nonzero(self.r[:self.t] == i) < 2:
                arms_to_recommend.append(i)

        if arms_to_recommend:
            self.r[self.t] = random.choice(arms_to_recommend)
            self.cases[self.t] = 2
            return 
        
        '''
        # case 2b:
        arms_to_recommend = []
        for i in range(self.num_arms):
            # If arm pulled less than two times and recommended less than three times
            if self.x[i] < 2 and np.count_nonzero(self.r[:self.t] == i) < 3:
                arms_to_recommend.append(i)

        if arms_to_recommend:
            self.r[self.t] = random.choice(arms_to_recommend)
            self.cases[self.t] = 2
            print("Case 2b")
            return 
        '''

        # case 3: UCB
        min_weight = 0.5
        max_weight = 0.9
        weight = min_weight + self.t * (max_weight - min_weight) / self.num_episodes

        max_value = 0.0
        max_arm = 0
        for i in range(self.num_arms):
            i_value = weight * (self.y[i] / (self.x[i] if self.x[i] != 0 else 0.1))
            i_value += (1 - weight) * math.sqrt(self.num_episodes / (self.x[i] if self.x[i] != 0 else 0.1))

            if max_value < i_value:
                max_value = i_value
                max_arm = i
            
        self.cases[self.t] = 3
        self.r[self.t] = max_arm
        return
        
    def pull_arm(self, arm_index):
        reward = np.random.exponential(self.beta_vals[arm_index])
        # Upper bound for reward: 3 * beta_vals[arm_index]
        if reward > 3 * self.beta_vals[arm_index]:
            # Reward is capped at 3 * beta_vals[arm_index] and a random value between 0 and 0.2 is subtracted for noise
            reward = 3 * self.beta_vals[arm_index] - np.random.uniform(0, 0.2)
        # Lower bound for reward: 0.01
        if reward < 0.01:
            # Reward is capped at 0.01 and a random value between 0 and 0.2 is added for noise
            reward = 0.01
        return reward
    
    def reset(self):
        self.x = np.zeros(self.num_arms) # Number of pulls for each arm
        self.y = np.zeros(self.num_arms) # Rewards for each arm
        self.r = np.zeros(self.num_episodes) # Recommendations for each arm
        self.i = np.zeros(self.num_episodes) # Intentions for each round
        self.s = np.zeros(self.num_episodes) # Selections for each round
        self.t = 0
        self.l = np.zeros(self.num_episodes) # Likelihood that the user adopts
        self.l[0] = 1 # Complaint - Likelihood
        #self.condition = 0 # Cold = 0 or Warm = 1
        self.cases = np.zeros(self.num_episodes)

    def getExplanation4Recommendation(self):
        # self.condition is Condition
        # self.l is Complaint - Likelihood
        # self.i[self.t] is Intention for time t (Current)
        # self.r[self.t] is Recommendation for time t (Current)
        # self.s[self.t] is Selection for time t (Current)
        # average reward for recommendation is sum(self.y[x]) / len(self.y[x])
        # self.y[self.t] is Reward for time t (Current)
        agent = agent_recommender(self.condition, self.i[self.t], self.r[self.t], self.l[self.t])
        return agent.get_recommendation()
    
    def getExplanationPostSelection(self):
        # self.condition is Condition
        # self.l is Complaint - Likelihood
        # self.i[self.t] is Intention for time t (Current)
        # self.r[self.t] is Recommendation for time t (Current)
        # self.s[self.t] is Selection for time t (Current)
        # average reward for recommendation is sum(self.y[x]) / len(self.y[x])
        # self.y[self.t] is Reward for time t (Current)
        
        agent = agent_feedback(self.condition, self.s[self.t], self.r[self.t], self.rewardPerRound[self.t], sum(self.y) / self.num_arms)
        return agent.get_feedback() 

    def UCB(self):
        for i in range(self.num_arms):
            if self.F[i] == 0:
                return i + 1
        ucb_values = self.S + np.sqrt(2 * np.log(np.sum(self.F)) / (self.F))
        action = np.argmax(ucb_values) + 1
        return action
    
    def calculateMoney(self):        
        if np.sum(self.y) < np.median(self.beta_vals)*self.num_episodes:
            return 0
        elif np.sum(self.y) < np.max(self.beta_vals)*self.num_episodes:
            return (np.sum(self.y) - (np.median(self.beta_vals)*self.num_episodes)) * 200 / self.num_episodes
        else:
            return 200