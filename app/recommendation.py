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
        
        # UCB =========================================================================
        # Use after exploration phase is over
        # Warm: encouragment when I = R: 5
        self.warm_encourage_equal_UCB = ["We're on the same page!", "Seems like we agree!", "Great minds think alike!", "Glad we think the same!", "Awesome, we agree!"]
        # Warm: Compliment for when I = R: 5
        self.warm_compliment_equal_UCB = ["Nice choice!", "Clever selection!", "Good decision!", "Great choice!", "Good thinking!"]
        # Warm: Agreement when I = R (High Level of Adoption): 5
        self.warm_high_equal_UCB = ["This choice is promising. 😊", "We completely agree.", "This should pay off. 😁", "Let's see what we receive.", "We can continue with this choice. 😊"]
        # Warm: Agreement when I = R (Low level of Adoption): 5
        self.warm_low_equal_UCB = ["Your choice looks promising.", "Go ahead with your selection. 🙂", "This selection looks good.", "That looks like a good decision. 😌", "You have made a nice choice."]    
        # Warm: Agreement when I ≠ R (Low Level of Adoption): 5
        self.warm_low_unequal_UCB = ["Choosing this option may benefit you in the long run.", "You could consider this option instead as it could get you a higher reward. 🙂", "This choice may give us a better outcome, as it has been good before.", "You may want to choose this option instead, it could be the better one. 🙂", "This option may be the better choice for you to pick, as it could give a higher reward."]
        # Warm: Agreement when I ≠ R (High Level of Adoption): 5
        self.warm_high_unequal_UCB = ["How about this choice since it may be promising? 😊", "How about choosing this selection since it could lead us to success?", "Would you like to consider this option instead as it could be better? 😊", "Maybe we could pick this instead, since it's done well before?", "How about we pick this one, since it could give us a higher reward? 😁"]
        # Warm: encouragement when I ≠ R: 5
        self.warm_encourage_unequal_UCB = ["We can do this together.", "We are better together", "Let's do this together.", "Let's work together.", "Teamwork is the key."]
        # Warm: compliment when I ≠ R: 5
        self.warm_compliment_unequal_UCB = ["Love your efforts!", "Your efforts are commendable.", "Nice decision!", "That's a reasonable choice!", "Oh, interesting!"]
        
        # Cold: Agreement when I = R (High Level of Adoption): 5
        self.cold_compliment_equal_UCB = ["A decent choice.", "Not bad.", "Well-made decision.", "Quite a fair decision.", "Very acceptable choice."]
        # Cold: Agreement when I = R (Low Level of Adoption): 5
        self.cold_encourage_equal_UCB = ["Agreed.", "Quite plausible.", "Logical decision.", "A satisfactory choice.", "A reasonable selection."]
        # Cold: Suggestion when I != R (High Level of Adoption): 5
        self.cold_compliment_unequal_UCB = ["I am optimistic about working together.", "I am pleased with the teamwork.", "I see good progress so far.", "I see an interesting decision has been made.", "I understand the choice."]
        # Cold: Suggestion when I != R (Low Level of Adoption): 5
        self.cold_encourage_unequal_UCB = ["There may be a better choice.", "I believe cooperation is a better strategy.", "I recommend working with me on this.", "I have a different suggestion.", "I recommend this instead."]
        # Cold: 2nd Sentence Agreement when I = R (High Level of Adoption): 5
        self.cold_high_equal_UCB = ["I concur.", "I agree.", "I shall not disagree.", "I like this choice.", "I am in accord."]
        # Cold: 2nd Sentence Suggestion when I != R (High Level of Adoption): 5
        self.cold_high_unequal_UCB = ["Having considered through the options, I suggest selecting this option.", "I believe this one will be a more plausible choice based on my understanding.", "Taking previous performance into account, I suggest selecting this option.", "Based on my assessment, selecting this one is more plausible.", "Based on my evaluations, this one is more plausible."]
        # Cold: 2nd Sentence Agreement when I = R (Low Level of Adoption): 5
        self.cold_low_equal_UCB = ["I believe your choice for this instance is plausible.", "I concur with this selection.", "I see that a fair decision has been made.", "I support this choice.", "I am pleased by this selection."]
        # Cold: 2nd Sentence Suggestion when I != R (Low Level of Adoption): 5
        self.cold_low_unequal_UCB = ["If this option is not selected, it may obtain a suboptimal outcome.", "If this option is selected, there may be a less desirable outcome.", "If this option is ignored, the optimal outcome may not be attained.", "If this option is selected, it could avoid a suboptimal outcome.", "Choosing this option may result in a more positive outcome."]
        
        
        # EXPLORATION =====================================================================
        # Use during initial exploration phase
        # Warm: encouragment when I = R: 5
        self.warm_encourage_equal = ["We're on the same page!", "Seems like we agree!", "Great minds think alike!", "Glad we think the same!", "Good to see we agree!"]
        # Warm: Compliment for when I = R: 5
        self.warm_compliment_equal = ["Nice choice!", "Clever selection!", "Good decision!", "Wow, great choice!", "Good thinking!"]
        # Warm: Agreement when I = R (High Level of Adoption): 5
        self.warm_high_equal = ["Exploring this choice is promising.😊", "We completely agree, we should explore this.", "Exploring this choice sounds good. 😄", "Let's see what we receive.", "We can continue with this choice. 😊"]
        # Warm: Agreement when I = R (Low level of Adoption): 5
        self.warm_low_equal = ["Checking out this choice looks promising. 😀", "Go ahead with this selection.", "Exploring this selection is good.", "Exploring this choice is a great decision.🙂", "Your choice will help us learn."]    
        # Warm: Agreement when I ≠ R (Low Level of Adoption): 5
        self.warm_low_unequal = ["Exploring this option may benefit you in the long run.😊", "You could consider exploring this option instead as it could get you a higher reward.",  "You could consider this option instead, as it could help you explore your options.🙂", "This choice may give us a better outome, as it hasn't been explored yet.", "You could try this one instead, as it has not been explored much."]
        # Warm: Agreement when I ≠ R (High Level of Adoption): 5
        self.warm_high_unequal = ["How about this choice since it could be explored more?🙂", "How about checking out this one, since we could still learn more?", "Would you like to explore this option instead as it's not as well tested?", "Maybe you'd like to consider this option, since we could learn more about it? 😀", "What if we look at this one instead, since we could explore it more?"]
        # Warm: encouragement when I ≠ R: 5
        self.warm_encourage_unequal = ["We can do this together.", "We are better together.", "Let's do this together.", "We're a team.", "Let's keep going together."]
        # Warm: compliment when I ≠ R: 5
        self.warm_compliment_unequal = ["Love your efforts!", "Your efforts are commendable.", "Nice decision!", "Great effort!", "Nicely done!"]
        
        # Cold: Agreement when I = R (High Level of Adoption): 5
        self.cold_compliment_equal = ["A decent choice.", "Not bad.", "Well-made decision.", "Quite a fair decision.", "Very acceptable choice."]
        # Cold: Agreement when I = R (Low Level of Adoption): 5
        self.cold_encourage_equal = ["Agreed.", "Quite plausible.", "Logical decision.", "A satisfactory choice.", "A reasonable selection."]
        # Cold: Suggestion when I != R (High Level of Adoption): 5
        self.cold_compliment_unequal = ["I am optimistic about working together.", "I am pleased with the teamwork.", "I like the progress so far.", "I see an interesting selection has been made.", "I understand the choice."]
        # Cold: Suggestion when I != R (Low Level of Adoption): 5
        self.cold_encourage_unequal = ["There may be a better choice to explore.", "I believe cooperation is a better strategy.", "I recommend working with me on this.", "I believe there is a better option.", "I would like to work together on this."]
        # Cold: 2nd Sentence Agreement when I = R (High Level of Adoption): 5
        self.cold_high_equal = ["I concur.", "I agree.", "I shall not disagree.", "Nice choice.", "I see no issues with this choice."]
        # Cold: 2nd Sentence Suggestion when I != R (High Level of Adoption): 5
        self.cold_high_unequal = ["Having considered through the options, I suggest exploring this one.", "Based on my evaluations, exploring this option is more plausible.", "Taking my calculations into account, I suggest selecting this option.", "After computing the possibilities, I recommend this choice instead.", "Based on my computations, I believe exploring this choice is more reasonable."]
        # Cold: 2nd Sentence Agreement when I = R (Low Level of Adoption): 5
        self.cold_low_equal = ["I believe your choice for this instance is plausible.", "I concur with exploring this selection.", "I see that a fair decision has been made.", "I support exploring this option.", "I recommend proceeding with this choice."]
        # Cold: 2nd Sentence Suggestion when I != R (Low Level of Adoption): 5
        self.cold_low_unequal = ["If this option is not explored, it may lead to less accurate learning.", "If this option is selected, there may be some that are less fairly explored.", "If this option is not explored, the calculations for it may not be as accurate.", "If this option is selected instead, I can use the data to learn more accurately.", "If this option is not chosen, I may not be able to compute recommendations as accurately."]
        

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
        if (self.case == 3):   
            key = str(self.condition) + "#" + str(self.likelihood_key) + "#" + str(self.agreement)
        else:
            key = "#" + str(self.condition) + "#" + str(self.likelihood_key) + "#" + str(self.agreement)
            
        recommendation = self.form_recommendation(self.map_recommendation[key][0], self.map_recommendation[key][1])
        return recommendation
        
class agent_feedback:
    def __init__(self, condition, curr_selection, curr_recommend, curr_reward, avg_reward, case):
        self.curr_selection = curr_selection
        self.curr_recommend = curr_recommend
        self.curr_reward = curr_reward
        self.avg_reward = avg_reward
        self.condition = condition
        self.good_reward = 0
        self.agreement = 0
        self.case = case
        
        # UCB
        # Warm: Good reward, agreement
        self.warm_good_agree_UCB = ["Awesome, let's keep going!", "Yay, we should continue!", "Amazing, let's keep it up! 😎", "Sweet, we got this! 😊", "Fantastic, let's move onward!", "Wooo!😀 We're doing great!"]
        # Warm: Good reward, disagreement
        self.warm_good_disagree_UCB = ["Nice! Let's try to work together.", "Awesome! We should try to cooperate.", "Neat! Let's make decisions together.😊", "Exceptional! Let's try our best to work together. 😊"]
        # Warm: Bad reward, agreement
        self.warm_bad_agree_UCB = ["Bad luck happens.🥲 Let's continue to work together!", "Oh, how unlucky! We can always learn.", "Mistakes happen. We can improve together.", "Oh no!😅 We shall learn from our mistakes."]
        # Warm: Bad reward, disagreement
        self.warm_bad_disagree_UCB = ["That's unfortunate.🙁 We should work together!", "Oh no! Cooperation is the best way for us to succeed.", "Undesirable outcomes happen. We can always work together!😊"]      
        # Cold: Good reward, agreement
        self.cold_good_agree_UCB = ["I see it worked out.", "I'm liking what I see.", "I am quite pleased with the outcome.", "I see that the selection was successful."]
        # Cold: Good reward, disagreement
        self.cold_good_disagree_UCB = ["A decent outcome. I want to agree on more decisions moving forward.", "Quite fortunate result. I would like to see more cooperations in the next rounds."]
        # Cold: Bad reward, agreement
        self.cold_bad_agree_UCB = ["I'm refining my calculations. I'll be better equipped to provide assistance next time.", "I see that the results veered from the expected. I shall further improve my computation."]
        # Cold: Bad reward, disagreement
        self.cold_bad_disagree_UCB = ["Don't forget. I am here to provide assistance.", "I recommend collaborating to maximize reward.", "I suggest that more collaboration be made.", "I would advise that more combined effors be made."]

        # Exploration
        # Warm: Good reward, agreement
        self.warm_good_agree = ["Awesome, our exploring paid off!😃", "Yay, let's keep exploring!🙂", "Wow, we should keep learning!", "Fantastic! Exploring options has its benefits."]
        # Warm: Good reward, disagreement
        self.warm_good_disagree = ["Nice! Let's try to explore together. 😊", "Awesome! We can always cooperate while exploring our choices.", "Impressive! Let's always remember that we can work as a team.😊", "Sweet! Working together is always an option."]
        # Warm: Bad reward, agreement
        self.warm_bad_agree = ["Our exploration was unlucky. 😔 Let's keep going.", "Oh, how unlucky! We are learning by trial.", "Bad luck happens while exploring. We can improve together."]
        # Warm: Bad reward, disagreement
        self.warm_bad_disagree = ["That was unfortunate. 😞 We should learn together!", "Oh no! Cooperation is the best way for us to learn.", "How unlucky! 😣 Let's try to explore together.", "Unfavorable outcomes happen. Let's not forget to explore together!"]      
        # Cold: Good reward, agreement
        self.cold_good_agree = ["I see the exploration was a success.", "I'm liking what I see.", "I am pleased with the exploration outcome.", "It is pleasing to me to see a good outcome.", "It is satisfying to see the benefits that come from exploring."]
        # Cold: Good reward, disagreement
        self.cold_good_disagree = ["A decent outcome. I want to agree on more decisions moving forward.", "Quite neat. I recommend that more exploration be made together.", "Nice. Exploring together is something I would highly recommend.", "Satisfactory work. Investigating different options together is something I would suggest."]
        # Cold: Bad reward, agreement
        self.cold_bad_agree = ["I'm refining my calculations. I'll be better equipped to assist you next time.", "An unfortunate result. I have learned from this exploration.", "As results show, mistakes can occur. I will calculate ways for better performance."]
        # Cold: Bad reward, disagreement
        self.cold_bad_disagree = ["I highly suggest that we explore more options together.", "Don't forget. I am here to assist you in exploring.", "I recommend collaborating to explore more thoroughly.", "I suggest for more exploration to be made together to help better performance."]      
        
        # "#condition#good_reward#agreement"
        self.map_recommendation = {"#1#1#1":self.warm_good_agree_UCB, "#1#1#0":self.warm_good_disagree_UCB, "#1#0#1":self.warm_bad_agree_UCB, "#1#0#0": self.warm_bad_disagree_UCB, "#0#1#1":self.cold_good_agree_UCB, "#0#0#1":self.cold_bad_agree_UCB, "#0#1#0":self.cold_good_disagree_UCB, "#0#0#0":self.cold_bad_disagree_UCB, "1#1#1":self.warm_good_agree, "1#1#0":self.warm_good_disagree, "1#0#1":self.warm_bad_agree, "1#0#0": self.warm_bad_disagree, "0#1#1":self.cold_good_agree, "0#0#1":self.cold_bad_agree, "0#1#0":self.cold_good_disagree, "0#0#0":self.cold_bad_disagree}

    def set_values(self):
        if (self.curr_reward >= self.avg_reward):
            self.good_reward = 1
        if (self.curr_selection == self.curr_recommend):
            self.agreement = 1
    # Post-Recommendation
    def get_feedback(self):
        self.set_values()
        if (self.case == 3):
            key = "#" + str(self.condition) + "#" + str(self.good_reward) + "#" + str(self.agreement)
        else:
            key = str(self.condition) + "#" + str(self.good_reward) + "#" + str(self.agreement)
        recommendation = random.choice(self.map_recommendation[key])
        return recommendation
    
    
