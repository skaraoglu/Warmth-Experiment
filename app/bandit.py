import numpy as np
import random
import math
from recommendation import agent_recommender, agent_feedback

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
        self.r = np.zeros(num_episodes) # Recommendations for each round
        self.i = np.zeros(num_episodes) # Intentions for each round
        self.s = np.zeros(num_episodes) # Selections for each round
        self.t = 0

        self.l = np.zeros(num_episodes) # Likelihood that the user adopts
        #self.l[0] = 1 # Complaint - Likelihood
        self.condition = 0 # Cold = 0 or Warm = 1
        self.cases = np.zeros(num_episodes) # Cases for each round

    def updateLikelihood(self, delta=.75):
        if(self.t < self.num_episodes):
            self.l[self.t] = delta * self.l[self.t-1] + (1 - delta) * (1 if self.i[self.t] == self.s[self.t] else 0)
    
    def recommend_arm(self):
        self.r[self.t] = 0
        # If arm pulled less than two times
        # fit this to our structure
        currIntention = int(self.i[self.t])

        print(self.x[currIntention])
        if self.x[int(self.i[self.t])] < 2: # Why - 1?
            self.r[self.t] = self.i[self.t]
            self.cases[self.t] = 1
            print("case1")
            return 
        
        arms_to_recommend = []
        for i in range(self.num_arms):
            # If arm pulled less than two times and recommended less than three times
            if self.x[i] < 2 and np.count_nonzero(self.r == i) < 3:
                arms_to_recommend.append(i)

        if arms_to_recommend:
            self.r[self.t] = random.choice(arms_to_recommend)
            self.cases[self.t] = 2
            print("case2")
            return 

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
        print("case3")
        return
        
    def pull_arm(self, arm_index):
        reward = np.random.exponential(self.beta_vals[arm_index])
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
        self.condition = 0 # Cold = 0 or Warm = 1
        self.cases = np.zeros(self.num_episodes)

    def getExplanation4Recommendation(self):
        # self.condition is Condition
        # self.l is Complaint - Likelihood
        # self.i[self.t] is Intention for time t (Current)
        # self.r[self.t] is Recommendation for time t (Current)
        # self.s[self.t] is Selection for time t (Current)
        # average reward for recommendation is sum(self.y[x]) / len(self.y[x])
        # self.y[self.t] is Reward for time t (Current)
        agent = agent_recommender(self.condition, self.i[self.t], self.r[self.t], self.l)
        return agent.get_recommendation()
    
    def getExplanationPostSelection(self):
        # self.condition is Condition
        # self.l is Complaint - Likelihood
        # self.i[self.t] is Intention for time t (Current)
        # self.r[self.t] is Recommendation for time t (Current)
        # self.s[self.t] is Selection for time t (Current)
        # average reward for recommendation is sum(self.y[x]) / len(self.y[x])
        # self.y[self.t] is Reward for time t (Current)
        agent = agent_feedback(self.condition, self.s[self.t], self.r[self.t], self.y[self.t], sum(self.y) / len(self.y))
        return agent.get_feedback() 

    def UCB(self):
        for i in range(self.num_arms):
            if self.F[i] == 0:
                return i + 1
        ucb_values = self.S + np.sqrt(2 * np.log(np.sum(self.F)) / (self.F))
        action = np.argmax(ucb_values) + 1
        return action            