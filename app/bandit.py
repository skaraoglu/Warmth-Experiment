# this version
# new comment
# I'm trying. Hello.

import numpy as np
from scipy.optimize import fsolve
from scipy.integrate import quad
from scipy.stats import expon
from flask import (
    url_for, redirect, render_template, flash, request, session, jsonify,
    current_app
)
from app import app

class Bandit:
    def __init__(self, num_arms, beta_vals=None):
        np.random.seed(seed=62)

        self.num_arms = num_arms
        if beta_vals is None:
            self.beta_vals = np.array([0.2, 0.3, 0.75, 0.8, 0.85, 0.9])
        else:
            self.beta_vals = beta_vals
        # Sum of the rewards for the specific arm
        self.S = np.zeros(num_arms)
        # Number of times selected for the specific arm
        self.F = np.zeros(num_arms)
        # Number of times a certain arms has been recommended
        self.recommended = np.zeros(num_arms)
        # Sequence of selected arms
        self.selections = []
        # Number of arms considered in current pass
        self.arms_to_pull = []
        # Mean rewards of each arm (mu')
        self.mean_rewards = self.S / (self.F + 0.0000000001)
        # Intention of the User
        self.intent = 0
        # Whether SOAAv can still be used
        self.use_SOAAv = True

    
    def pull_arm(self, arm_index):
        reward = np.random.normal(self.beta_vals[arm_index], 0.025, 1)
        return reward
    
    def reset(self):
        self.S = np.zeros(self.num_arms)
        self.F = np.zeros(self.num_arms)

    def UCB(self):
        for i in range(self.num_arms):
            if self.F[i] == 0:
                return i + 1
        ucb_values = self.S + np.sqrt(2 * np.log(np.sum(self.F)) / (self.F))
        action = np.argmax(ucb_values) + 1
        return action            
    
    @app.route('/get_recommendation', methods=['POST'])
    def get_recommendation(self):
        user_curr_intention = request.json['intendedOptionIndex']
        self.intent = user_curr_intention

    def HILL_UCB(self): #implement
        return -1    
    
    # If user ignores suggestion twice move on.
    def HILL_SOAAv(self, intention, factor=0):
        # see why recommendation is arm after selection
        for i in range(self.num_arms): # algorithm ignores unpulled arms when recommedning
            # if i not in self.selections: # self.F
            #     self.recommended[i] += 1
            #     return i + 1
            # elif self.recommended[i] < 2:
            #     self.recommended[i] += 1
            #     return i + 1
            if (self.F[intention] == 0):
                self.recommended[intention] += 1
                return i + 1
            elif (any(i < 2 for i in self.recommended) and (self.F[i] == 0)):
                self.recommended[i] += 1
                return i + 1

        # elif min(self.recommended) < 2:
        #     self.recommended[min(self.recommended)] += 1
        #     return min(self.recommended) + 1
        
        if self.arms_to_pull is None:
            set_selections = set(self.selections)
            average_reward = sum(self.mean_rewards) / len(set_selections)  
            for i in set_selections:
                if self.mean_rewards[i] >= (1 + factor) * average_reward:
                    self.arms_to_pull.append(i + 1)
                    print(self.arms_to_pull)
        pull = []
        for i in self.arms_to_pull:
            pull.append(self.F[i-1])
        
        # Check the number of pulls for each arm in pull[] to see whether SOAAv can still be used

        
        # Select the minimum from the arms to pull. This will be the recommended arm.
        action = min(pull)
        # Remove the arm that will be pulled from the list
        self.arms_to_pull.remove(action - 1)
        self.recommended[action] += 1
        
        return action

    def KL(self, X, Y):
        # Define the integrand function for the KL divergence
        f = lambda x: -X.pdf(x)*(Y.logpdf(x) - X.logpdf(x))
        # Compute the definite integral of the integrand from -inf to inf
        return quad(f, -np.inf, np.inf)[0]

    def solve_X(self, mu, result):
        # Create an exponential distribution object with rate mu
        X = expon(scale=1/mu)
        # Define a function to find the root of
        def f(x):
            # Create an exponential distribution object with rate x
            Y = expon(scale=1/x)
            # Compute the difference between the KL divergence and the target result (result - kl = 0)
            return self.KL(X, Y) - result
        # Use fsolve to find the root of the function f
        x = fsolve(f, mu)
        return x[0]

    def sample_theta(self, mu, n):
        # when n - 1 = 0, prevent divide by zero by setting result to 0 
        if n == 1: result = 0
        else:
            # Sample a random value y from a uniform distribution on [0, 1]
            y = np.random.uniform(0, 1)
            if y >= 0.5:
                # Compute the target result for KL(mu, x) using y (y>=1/2) and n
                result = np.log(1 / (2 * (1 - y))) / (n - 1)
            else:
                # Compute the target result for KL(mu, x) using y (y<1/2) and n
                result = np.log(1 / (2 * y)) / (n - 1)
        # Solve for x using the solve_X function
        x = self.solve_X(mu, result)
        return x
    
    def ExpTS(self):
        for i in range(self.num_arms):
            if self.F[i] == 0:
                return i + 1
        theta_values = [0.0] * self.num_arms
        for i in range(self.num_arms):
            # Compute the mean reward (mu_i) and number of pulls (n_i) for arm i
            mu_i = self.S[i] / self.F[i]
            n_i = self.F[i]
            # Sample θi(t) independently from P(̂μi(t), Ti(t))
            theta_values[i] = self.sample_theta(mu_i, n_i)
        print(theta_values)
        action = np.argmax(theta_values) + 1
        return action
    
    def calc_arms(self, factor):
        # determine number of pass - look at available arms from 
        num_pulled_arm = []
        for curr_arm in self.arms_available:
            num_pulled_arm.append(self.F(curr_arm))
        # average output of each arms - will use to find average output of all arms
        mean_reward_arm = [np.zeros(self.num_arms)]
        for i in range(self.num_arms):
            mean_reward_arm[i] = self.S[i] / self.F[i]
        mean_all_arms = 0
        mean_all_arms = sum(mean_reward_arm) / (self.num_arms)
        # arms we can consider still
        for arm in range(self.num_arms):
            if self.means[arm][self.num_pass] >= ((1 + factor) * mean_all_arms):
                self.arms_available.append[arm]

    # def SOAAv(self, num_arms, num_episodes, factor, beta=None):
    #     num_total_pulls = 1
    #     sequence_pulls = []
    #     arms_available = []
    #     total_reward = 0
    #     #pull_budget = num_episodes
    #     #count_pull = np.zeros(num_arms)
        
    #     total_arm = num_arms
    #     elimination_factor = factor
    #     reward_round = np.zeros(num_episodes)  # Initialize reward_round with zeros
    #     round_num = 0
    #     bandit = Bandit(num_arms, beta)

    #     #add which arms are available
    #     while pull_budget >= 1 and len(arms_available) > 0:
    #         numPullsInPass = 0
    #         passAverageRatio = 0

    #         for i in range(num_arms):
    #             if (i+1) in arms_available and pull_budget >= 1:
    #                 action = i
    #                 reward = bandit.pull_arm(action)
    #                 reward_round[round_num] = reward
    #                 round_num += 1
    #                 total_reward += reward
    #                 count_pull[action] += 1
    #                 mean_reward_arm[action] = ((mean_reward_arm[action]*count_pull[action]) + reward) / (count_pull[action])
    #                 sequence_pulls.append(action)
    #                 pull_budget -= 1
    #                 num_total_pulls += 1
    #                 passAverageRatio = passAverageRatio + reward
    #                 numPullsInPass += 1

    #         if numPullsInPass > 0:
    #             passAverageRatio = passAverageRatio / numPullsInPass
    #             arms_available = [i+1 for i in range(total_arm) if mean_reward_arm[i] >= (1 + elimination_factor) * passAverageRatio]

    #     return sequence_pulls, reward_round
    