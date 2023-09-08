import numpy as np
from scipy.optimize import fsolve
from scipy.integrate import quad
from scipy.stats import expon
class Bandit:
    def __init__(self, num_arms, beta_vals=None):
        np.random.seed(seed=62)
        self.num_arms = num_arms
        if beta_vals is None:
            self.beta_vals = np.random.uniform(0, 1, num_arms)
        else:
            self.beta_vals = beta_vals
        self.S = np.zeros(num_arms)
        self.F = np.zeros(num_arms)
    
    def pull_arm(self, arm_index):
        reward = np.random.exponential(self.beta_vals[arm_index])
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
    
def SOAAv(num_arms, num_episodes, factor, beta=None):
    num_total_pulls = 1
    sequence_pulls = []
    total_reward = 0
    pull_budget = num_episodes
    count_pull = np.zeros(num_arms)
    mean_reward_arm = np.zeros(num_arms)
    arms_available = np.arange(1, num_arms+1)
    total_arm = num_arms
    elimination_factor = factor
    reward_round = np.zeros(num_episodes)  # Initialize reward_round with zeros
    round_num = 0
    bandit = Bandit(num_arms, beta)

    while pull_budget >= 1 and len(arms_available) > 0:
        numPullsInPass = 0
        passAverageRatio = 0

        for i in range(num_arms):
            if (i+1) in arms_available and pull_budget >= 1:
                action = i
                reward = bandit.pull_arm(action)
                reward_round[round_num] = reward
                round_num += 1
                total_reward += reward
                count_pull[action] += 1
                mean_reward_arm[action] = ((mean_reward_arm[action]*count_pull[action]) + reward) / (count_pull[action])
                sequence_pulls.append(action)
                pull_budget -= 1
                num_total_pulls += 1
                passAverageRatio = passAverageRatio + reward
                numPullsInPass += 1

        if numPullsInPass > 0:
            passAverageRatio = passAverageRatio / numPullsInPass
            arms_available = [i+1 for i in range(total_arm) if mean_reward_arm[i] >= (1 + elimination_factor) * passAverageRatio]

    return sequence_pulls, reward_round