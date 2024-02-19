import random

class agent_recommender:    

    # condition: warm or cold agent
    def __init__(self, condition, curr_intent, curr_recommend, likelihood, case):
        # Determine if it is exploration or not. 0 --> Exploration and 1 --> UCB
        self.case = case
        self.curr_intent = curr_intent
        self.curr_recommend = curr_recommend
        # Checks to see if intention = recommendation
        self.agreement = 0
       
        # Conditions: 1 = warm, 0 = cold
        self.condition = condition
        
        # Likelihood: >=0.5 = high, <0.5 = low
        self.likelihood = likelihood
        # If likelihood is greater than 0.5, the value will be 1, otherwise 0.
        self.likelihood_key = -1       
        
        # EXPLORATION =========================================================================
        # Warm: encouragment when I = R
        self.warm_encourage_equal = ["We’re on the same page!", "Seems like we agree!", "Great minds think alike!", "Glad we think the same!"]
        # Warm: Compliment for when I = R
        self.warm_compliment_equal = ["Nice choice!", "Clever selection!", "Good decision!"]
        # Warm: Agreement when I = R (High Level of Adoption)
        self.warm_high_equal = ["This choice is promising.😊", " I completely agree.", "This should pay off."]
        # Warm: Agreement when I = R (Low level of Adoption)
        self.warm_low_equal = ["Your choice looks promising.", "Go ahead with your selection.", "This selection looks good.", "That looks like a good decision."]    
        # Warm: Agreement when I ≠ R (Low Level of Adoption)
        self.warm_low_unequal = ["Choosing this option may benefit you in the long run.", "You could consider this option instead as it could get you a higher reward.", "This choice may give us a better outcome, as it has been good before."]
        # Warm: Agreement when I ≠ R (High Level of Adoption)
        self.warm_high_unequal = ["How about this choice since it may be promising?", "How about choosing this selection since it could lead us to success?", "Would you like to consider this option instead as it could be better?"]
        # Warm: encouragement when I ≠ R
        self.warm_encourage_unequal = ["We can do this together.", "We are better together", "Let's do this together."]
        # Warm: compliment when I ≠ R
        self.warm_compliment_unequal = ["Love your efforts!", "Your efforts are commendable.", "Nice decision!"]
        
        # Cold: Agreement when I = R (High Level of Adoption)
        self.cold_compliment_equal = ["A decent choice.", "Not bad.", "Well-made decision."]
        # Cold: Agreement when I = R (Low Level of Adoption)
        self.cold_encourage_equal = ["Agreed.", "Quite plausible.", "Logical decision."]
        # Cold: Suggestion when I != R (High Level of Adoption)
        self.cold_compliment_unequal = ["The progress so far is commendable.", "I am pleased with the teamwork.", "I see good progress so far."]
        # Cold: Suggestion when I != R (Low Level of Adoption)
        self.cold_encourage_unequal = ["There may be a better choice.", "I believe cooperation is a better strategy.", "I recommend working with me on this."]
        # Cold: 2nd Sentence Agreement when I = R (High Level of Adoption)
        self.cold_high_equal = ["I concur.", "I agree.", "I shall not disagree."]
        # Cold: 2nd Sentence Suggestion when I != R (High Level of Adoption)
        self.cold_high_unequal = ["Having considered through the options, I suggest selecting this option.", "I believe this one will be a more plausible choice based on my understanding.", "Taking previous performance into account, I suggest selecting this option.", "Based on my assessment, selecting this one is more plausible.", "Based on my evaluations, this one is more plausible."]
        # Cold: 2nd Sentence Agreement when I = R (Low Level of Adoption)
        self.cold_low_equal = ["I believe your choice for this instance is plausible.", "I concure with this selection.", "I see that a fair decision has been made."]
        # Cold: 2nd Sentence Suggestion when I != R (Low Level of Adoption)
        self.cold_low_unequal = ["If this option is not selected, it may obtain a suboptimal outcome.", "If this option is selected, there may be a less desirable outcome.", "If this option is ignored, the optimal outcome may not be attained."]
        
        
        # UCB =====================================================================
        # Warm: encouragment when I = R
        self.warm_encourage_equal_UCB = ["We’re on the same page!", "Seems like we agree!", "Great minds think alike!", "Glad we think the same!"]
        # Warm: Compliment for when I = R
        self.warm_compliment_equal = ["Nice choice!", "Clever selection!", "Good decision!"]
        # Warm: Agreement when I = R (High Level of Adoption)
        self.warm_high_equal = ["Exploring this choice is promising.😊", " I completely agree.", "Exploring this choice should pay off."]
        # Warm: Agreement when I = R (Low level of Adoption)
        self.warm_low_equal = ["Your choice looks promising.", "Go ahead with your selection.", "Exploring this selection is good.", "Exploring this choice is an ideal decision."]    
        # Warm: Agreement when I ≠ R (Low Level of Adoption)
        self.warm_low_unequal = ["Exploring this option may benefit you in the long run.", "You could consider exploring this option instead as it could get you a higher reward.",  "You could consider this option instead, as it could help you explore your options.", "This choice may give us a better outome, as it hasn't been explored yet."]
        # Warm: Agreement when I ≠ R (High Level of Adoption)
        self.warm_high_unequal = ["How about this choice since it may be promising?", "How about choosing this selection since it could lead us to success?", "Would you like to consider this option instead as it could be better?"]
        # Warm: encouragement when I ≠ R
        self.warm_encourage_unequal = ["We can do this together.", "We are better together", "Let's do this together."]
        # Warm: compliment when I ≠ R
        self.warm_compliment_unequal = ["Love your efforts!", "Your efforts are commendable.", "Nice decision!"]
        
        # Cold: Agreement when I = R (High Level of Adoption)
        self.cold_compliment_equal = ["A decent choice.", "Not bad.", "Well-made decision."]
        # Cold: Agreement when I = R (Low Level of Adoption)
        self.cold_encourage_equal = ["Agreed.", "Quite plausible.", "Logical decision."]
        # Cold: Suggestion when I != R (High Level of Adoption)
        self.cold_compliment_unequal = ["The progress so far is commendable.", "I am pleased with the teamwork.", "I see good progress so far."]
        # Cold: Suggestion when I != R (Low Level of Adoption)
        self.cold_encourage_unequal = ["There may be a better choice to explore.", "I believe cooperation is a better strategy.", "I recommend working with me on this."]
        # Cold: 2nd Sentence Agreement when I = R (High Level of Adoption)
        self.cold_high_equal = ["I concur.", "I agree.", "I shall not disagree."]
        # Cold: 2nd Sentence Suggestion when I != R (High Level of Adoption)
        self.cold_high_unequal = ["Having considered through the options, I suggest exploring this option.", "Based on my evaluations, exploring this option is more plausible.", "Taking previous performance into account, I suggest selecting this option."]
        # Cold: 2nd Sentence Agreement when I = R (Low Level of Adoption)
        self.cold_low_equal = ["I believe your choice for this instance is plausible.", "I concur with this selection.", "I see that a fair decision has been made."]
        # Cold: 2nd Sentence Suggestion when I != R (Low Level of Adoption)
        self.cold_low_unequal = ["If this option is not explored, it may lead to a suboptimal outcome.", "If this option is explored, there may be a less desirable outcome.", "If this option is ignored, the optimal outcome may not be attained."]
        

        # Contains both warm and cold sentences
        ## "#warm_or_cold#likelihood_key#agreement"
        # Exploration has "#" at the beginning.
        # UCB has 0 or 1 at the beginning.
        self.map_recommendation = {"#1#0#1":(self.warm_encourage_equal, self.warm_low_equal), "1#0#1":(self.warm_encourage_equal_UCB, self.warm_low_equal_UCB), "#1#1#1":(self.warm_compliment_equal, self.warm_high_equal), "1#1#1":(self.warm_compliment_equal_UCB, self.warm_high_equal_UCB), "#1#0#0":(self.warm_encourage_unequal, self.warm_low_unequal), "1#0#0":(self.warm_encourage_unequal_UCB, self.warm_low_unequal_UCB), "#1#1#0":(self.warm_compliment_unequal, self.warm_high_unequal), "1#1#0":(self.warm_compliment_unequal_UCB, self.warm_high_unequal_UCB), "#0#0#1":(self.cold_encourage_equal, self.cold_low_equal), "0#0#1":(self.cold_encourage_equal_UCB, self.cold_low_equal_UCB), "#0#0#0":(self.cold_encourage_unequal, self.cold_low_unequal), "0#0#0":(self.cold_encourage_unequal_UCB, self.cold_low_unequal_UCB), "#0#1#1":(self.cold_compliment_equal, self.cold_high_equal), "0#1#1":(self.cold_compliment_equal_UCB, self.cold_high_equal_UCB), "#0#1#0":(self.cold_compliment_unequal, self.cold_high_unequal), "0#1#0":(self.cold_compliment_unequal_UCB, self.cold_high_unequal_UCB)}
    # Choose randomly from the sentence to construct a sentence. 
    def form_recommendation(self, first_list:list, second_list:list):
        first_sent = random.choice(first_list)
        second_sent = random.choice(second_list)
        return first_sent + " " + second_sent
    
    # Set values for likelihood key and agreement
    def set_values(self):
        
        if self.likelihood > 0.5:
            self.likelihood_key = 1
        else:
            self.likelihood_key = 0
            
        if self.curr_intent == self.curr_recommend:
            self.agreement = 1
        else:
            self.agreement = 0
    
    # Recommendation
    def get_recommendation(self):
        self.set_values()
        if (self.case == 1):   
            key = "#" + str(self.condition) + "#" + str(self.likelihood_key) + "#" + str(self.agreement)
        else:
            key = str(self.condition) + "#" + str(self.likelihood_key) + "#" + str(self.agreement)
            
        recommendation = self.form_recommendation(self.map_recommendation[key][0], self.map_recommendation[key][1])
        return recommendation
        
class agent_feedback:
    def __init__(self, condition, curr_selection, curr_recommend, curr_reward, avg_reward):
        self.curr_selection = curr_selection
        self.curr_recommend = curr_recommend
        self.curr_reward = curr_reward
        self.avg_reward = avg_reward
        self.condition = condition
        self.good_reward = 0
        self.agreement = 0
        
        # Warm: Good reward, agreement
        self.warm_good_agree = ["Awesome, let's keep going!", "Yay, we should continue!"]
        # Warm: Good reward, disagreement
        self.warm_good_disagree = ["Nice! Let's keep working together.", "Awesome! We should keep cooperating."]
        # Warm: Bad reward, agreement
        self.warm_bad_agree = ["Bad luck happens. Let's continue!", "Oh, how unlucky! We should keep going."]
        # Warm: Bad reward, disagreement
        self.warm_bad_disagree = ["That's unfortunate. We should work together!", "Oh no! Cooperation is the best way for us."]      
        # Cold: Good reward, agreement
        self.cold_good_agree = ["I see it worked out.", "I'm liking what I see."]
        # Cold: Good reward, disagreement
        self.cold_good_disagree = ["A decent outcome. I want to agree on more decisions moving forward."]
        # Cold: Bad reward, agreement
        self.cold_bad_agree = ["I'm refining my calculations. I'll be better equipped to assist you next time."]
        # Cold: Bad reward, disagreement
        self.cold_bad_disagree = ["Don't forget. I am here to assist you.", "I recommend collaborating to maximize reward."]      
        
        # "#condition#good_reward#agreement"
        self.map_recommendation = {"#1#1#1":self.warm_good_agree, "#1#1#0":self.warm_good_disagree, "#1#0#1":self.warm_bad_agree, "#1#0#0": self.warm_bad_disagree, "#0#1#1":self.cold_good_agree, "#0#0#1":self.cold_bad_agree, "#0#1#0":self.cold_good_disagree, "#0#0#0":self.cold_bad_disagree}

    def set_values(self):
        if (self.curr_reward >= self.avg_reward):
            self.good_reward = 1
        if (self.curr_selection == self.curr_recommend):
            self.agreement = 1
    # Post-Recommendation
    def get_feedback(self):
        self.set_values()
        key = "#" + str(self.condition) + "#" + str(self.good_reward) + "#" + str(self.agreement)
        recommendation = random.choice(self.map_recommendation[key])
        return recommendation
    
    