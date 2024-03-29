document.addEventListener("DOMContentLoaded", function () {
    const stocksDiv = document.getElementById("stocks");
    const stockOptions = stocksDiv.querySelectorAll(".stock-option");
    const investButton = document.getElementById("investButton");
    const surveyDiv = document.getElementById("survey");
    const progressDiv = document.getElementById("warmupprogress");
    const agentsDiv = document.getElementById("warmupagents");
    const ar = agentsDiv.querySelectorAll(".warmupagents-rec");
    let intendedOptionIndex = null;
    let selectedOptionIndex = null;
    let isAnimating = false; // Flag for animation state
    let totalReward = 0;
    let currentEpisode = 0;
    let selectedList = [];
    let rewardsList = [];
    investButton.classList.add("inactive-button"); // Add the inactive class initially
    const episodes = 10; // Total number of episodes
    let agents = -1;
    let intention = -1;
    let isIntention = false;
    let recommendationShown = false; // Track if recommendation is shown
    const completeButton = document.querySelector('#complete .button');
    const surveyAnswer = document.getElementById('strategy');
  
    surveyAnswer.addEventListener('input', function() {
      if (surveyAnswer.value.trim() !== '') {
          // If the textarea is not empty, enable the button
          completeButton.className = "button";
      } else {
          // If the textarea is empty, disable the button
          completeButton.className = "inactive-button";
      }
    });

    function setIntention(opt, i){
      intention = opt;
      isIntention = true;
      stockOptions.forEach((o, index) => {
        if (o === opt){
        o.classList.add("intention");
        intendedOptionIndex = index;
        //(intendedOptionIndex);
      }})      
    }
  
    function resetIntention(){
      intention = -1;
      isIntention = false;
      intendedOptionIndex = null;
      stockOptions.forEach((opt, index) => {
        opt.classList.remove("intention");})
    }
  
    // Initialize the progress bar
    for (let i = 0; i < episodes; i++) {
      const episodeSquare = document.createElement("div");
      episodeSquare.className = "episode-square";
      progressDiv.appendChild(episodeSquare);
    }
    
    // Function to update the progress bar based on the current episode and selected options
    function updateProgressBar(selectedList) {
      const episodeSquares = progressDiv.querySelectorAll(".episode-square");
      const episodeNumbersDiv = document.getElementById("episode-numbers"); 
      // Clear existing episode numbers
      episodeNumbersDiv.innerHTML = "";
      episodeSquares.forEach((square, index) => {
        square.classList.remove("current", "previous", "upcoming");
        // Create a span element to display the episode number
        const episodeNumber = document.createElement("span");
        episodeNumber.className = "episode-number";
        episodeNumber.textContent = index + 1;
        if (index === currentEpisode) {
          square.classList.add("current");
          episodeNumber.style.color = "#007bff";
        } else if (index < currentEpisode) {
          square.classList.add("previous");
          episodeNumber.style.color = "#44ff55";
          if (selectedList[index] !== undefined) {
            square.textContent = (selectedList[index] + 1); // Display selected option index
          } else { 
            square.textContent = ""; // Clear the square if no option selected
          }
        } else {
          square.classList.add("upcoming");
          episodeNumber.style.color = "#ddd";
          square.textContent = ""; // Clear the square for upcoming episodes
        }
        // Append the episode number span to the episode numbers div
        episodeNumbersDiv.appendChild(episodeNumber);
      });
    }  
  
    stocksDiv.addEventListener("click", (event) => {
      if (isAnimating) return; // Prevent interaction during animation
      const clickedOption = event.target.closest(".stock-option");
      if (!clickedOption) return;
      //stocksDiv.style.pointerEvents = "none";
      if (intention == -1){
        isAnimating = true;
        stocksDiv.style.pointerEvents = "none";
        setIntention(clickedOption);        
        setTimeout(() => {        
          stockOptions.forEach((opt, index) => {
            opt.classList.remove("selected");
            opt.classList.remove("intention");
            if (opt === clickedOption) {
              opt.classList.add("intention");
              
              intendedOptionIndex = index;
              //console.log("intention: " + intendedOptionIndex);
  
              fetch(`/get_recommendation?intendedOption=${intendedOptionIndex}`)
                .then(response => response.json())
                .then(data=>{
                  agents = data.agents
                  curCase = data.cases;
                  expForRec = data.expForRec;
                  condition = data.condition;
                  //console.log("recommendation: " + agents)
                  ar.forEach((div, index) => {
                    stockOptions[index].style.backgroundColor = "#f0f0f0";
                    //console.log("agent: " + agents);
                    if (index === agents - 1 && !recommendationShown) {
                      const image = document.createElement("img");
                      image.src = "../static/hand_100.png";
                      image.classList.remove("still");
                      image.classList.add("slide-down");
                      div.innerHTML = "";
                      div.appendChild(image);            
                     
                      stockOptions[index].style.backgroundColor = "#e6f4e6";
                      // Set the recommendationShown flag to true
                      recommendationShown = true;
                    } else if (index === agents - 1) {
                      const image = document.createElement("img");
                      image.src = "../static/hand_50.png";        
                      image.classList.remove("slide-down");          
                      image.classList.add("still");
                      div.innerHTML = "";
                      div.appendChild(image);
                      stockOptions[index].style.backgroundColor = "#e6f4e6";
                    } else {
                      div.innerHTML = "";
                      stockOptions[index].style.backgroundColor = "#f0f0f0";
                    }
                  
                  });
                })
              const optionLabel = opt.querySelector(".option-label");
              const stockTitle = opt.querySelector(".stock-title");
              optionLabel.style.color = "#007bff";
              stockTitle.style.color = "#007bff";
              
            } else {
              // Reset the color for other options
              const optionLabel = opt.querySelector(".option-label");
              const stockTitle = opt.querySelector(".stock-title");
              optionLabel.style.color = "#222";
              stockTitle.style.color = "#222";
            }          
            isAnimating = false;          
          });
        },100)
        stocksDiv.style.pointerEvents = "auto";
      }
      else {
        if(isAnimating){return;};
        stockOptions.forEach((opt, index) => {
          opt.classList.remove("selected");
          if (opt === clickedOption) {
            if (index === intendedOptionIndex){
              opt.classList.remove("intention");
              opt.classList.add("selected");
              selectedOptionIndex = intendedOptionIndex;
            }else {
              opt.classList.add("selected");
              selectedOptionIndex = index;
              stockOptions[intendedOptionIndex].classList.add("intention");
            }          
            // Activate the invest button when an option is selected
            investButton.classList.remove("inactive-button");
            investButton.innerText = "Invest";
            // Change the color of the span element within the selected option
            const optionLabel = opt.querySelector(".option-label");
            const stockTitle = opt.querySelector(".stock-title");
            optionLabel.style.color = "#007bff";
            stockTitle.style.color = "#007bff";
             
          } else {
            // Reset the color for other options
            const optionLabel = opt.querySelector(".option-label");
            const stockTitle = opt.querySelector(".stock-title");
            optionLabel.style.color = "#222";
            stockTitle.style.color = "#222";
          }        
        });
      };      
    });
  
    const rollingNumber = document.querySelector(".rolling-number");
    rollingNumber.textContent = "";
  
    investButton.addEventListener("click", () => {
      if (isAnimating) return; // Prevent interaction during animation
      if (intendedOptionIndex !== null) {
        for (let i = 0; i < 6; i++) {stockOptions[i].style.backgroundColor = "#f0f0f0";}        
        isAnimating = true;
        stocksDiv.style.pointerEvents = "none";
        ar.forEach((div, index) => {div.textContent = ""});
        investButton.classList.add("inactive-button");
        investButton.innerText = "Select Stock";
        // Reset the color of all option labels
        
        currentEpisode++;
        selectedList.push(selectedOptionIndex);
        
        fetch(`/get_reward?selected_option=${selectedOptionIndex}`)
          .then(response => response.json())
          .then(data => {
            totalReward += data.reward;
            const rewardDiv = document.getElementById("reward");
            const rewardText = `Reward received: ${data.reward}`;
            expPostSel = data.expPostSel;
            // agents = data.agents;
            //console.log(selectedOptionIndex);
            // Update times invested and average reward values using data attributes
            const selectedOption = stockOptions[selectedOptionIndex];
            const timesInvestedElement = selectedOption.querySelector(".times-invested");
            const averageRewardElement = selectedOption.querySelector(".average-reward");
            
            if (timesInvestedElement && averageRewardElement) {
              const timesInvestedValue = data.banditX;
              const averageRewardValue = timesInvestedValue === 0 ? 0 : data.banditY / timesInvestedValue;
  
              timesInvestedElement.textContent = `${timesInvestedValue}`;
              averageRewardElement.textContent = `${averageRewardValue.toFixed(2)}`;
            }                        
            // Update the reward value for the rolling numbers
            const rewardContainer = document.querySelector(".reward-container");
            // Toggle the rolling class on the reward frame
            const rewardFrame = document.querySelector(".reward-frame");
            rewardFrame.classList.add("rolling");
  
            // Create a rolling animation using GSAP
            const tl = gsap.timeline();
            tl.to(rollingNumber, {
              y: -40, // Adjust the distance based on your design
              duration: 0.15, // Animation duration
              onComplete: () => {
                // Update the rolling number with the new reward
                rollingNumber.textContent = data.reward.toFixed(2);
  
                // Complete the animation
                gsap.to(rollingNumber, {
                  y: 0, // Reset to original position
                  duration: 0.15, // Animation duration
                  delay: 0.05, // Delay before resetting
                  onComplete: () => {
                    // Clear the reward after the animation completes
                    setTimeout(() => {
                      rollingNumber.textContent = "";
                      // Remove the rolling class after the animation completes
                      rewardFrame.classList.remove("rolling");
                      // Clear selection from stock options
                      stockOptions.forEach(opt => opt.classList.remove("selected"));
                      stockOptions.forEach((opt) => {
                        const optionLabel = opt.querySelector(".option-label");
                        const stockTitle = opt.querySelector(".stock-title");
                        optionLabel.style.color = "#222";
                        stockTitle.style.color = "#222";
                      });
                      isAnimating = false; // Reset animation flag
                    }, 3000);
                  },
                });
              },
            });          
            resetIntention();
            recommendationShown = false;
            updateProgressBar(selectedList);          
          });   
      stocksDiv.style.pointerEvents = "auto";      
      }
      if (currentEpisode >= episodes) {
        investButton.style.display = "none";
        setTimeout(function(){
          // Hide stock options and invest button
          const rtitle = document.getElementById("rtitle");
          rtitle.textContent = "Total Reward:";
          stockOptions.forEach(opt => opt.style.display = "none");
          
          //rtitle.textContent = "Total Reward:";
          const totalRewardFrame = document.createElement("div");
          totalRewardFrame.className = "reward-frame";
          const totalRewardText = document.createElement("div");
          totalRewardText.textContent = totalReward.toFixed(2);
          totalRewardFrame.appendChild(totalRewardText);      
  
          const rewardDiv = document.getElementById("reward");
          rewardDiv.innerHTML = "";
          rewardDiv.appendChild(rtitle);
          rewardDiv.appendChild(totalRewardFrame);
          const completeDiv = document.getElementById("complete");
          agentsDiv.style.display = "none";
          surveyDiv.style.display = "block";
          completeDiv.style.display = "block";
          completeButton.className = "inactive-button";

  
          return;
        }, 2000);      
      }
      
    });
    // Initial progress bar update  
    updateProgressBar(selectedList);
  });
  