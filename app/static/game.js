document.addEventListener("DOMContentLoaded", function () {
  const stocksDiv = document.getElementById("stocks");
  const atnStocksDiv = document.getElementById("atnStocks");
  const stockOptions = stocksDiv.querySelectorAll(".stock-option");
  const completeDiv = document.getElementById("complete");
  const surveyDiv = document.getElementById("survey");
  const investButton = document.getElementById("investButton");
  const surveyButton = document.getElementById("surveyButton");
  const progressDiv = document.getElementById("progress");
  const agentsDiv = document.getElementById("agents");
  const ar = agentsDiv.querySelectorAll(".agents-rec");
  const recommendationDiv = document.getElementById("recommendation-text");
  const recommendationContent = document.getElementById("recommendation-content");
  const rewardDiv = document.getElementById("reward");
  const proceedDiv = document.getElementById("proceed");
  let intendedOptionIndex = null;
  let selectedOptionIndex = null;
  let isAnimating = false; // Flag for animation state
  let totalReward = 0;
  let currentEpisode = 0;
  let selectedList = [];
  let rewardsList = [];
  investButton.classList.add("inactive-button"); // Add the inactive class initially
  const episodes = 30; // Total number of episodes
  let agents = 1;
  let intention = -1;
  let isIntention = false;
  let recommendationShown = false; // Track if recommendation is shown
  let curCase = -1;
  let expForRec = "";
  let expPostSel = "";
  let atnCheck = false;
  const completeButton = document.querySelector('#complete .button');
  const surveyAnswer = document.getElementById('strategy');
  const atnButton = document.getElementById('atnButton');
  const q1 = document.getElementById('q1');
  const q2 = document.getElementById('q2');

  surveyAnswer.addEventListener('input', function() {
    if (surveyAnswer.value.trim() !== '') {
        // If the textarea is not empty, enable the button
        surveyButton.className = "button";
    } else {
        // If the textarea is empty, disable the button
        surveyButton.className = "inactive-button";
    }
  });

  atnButton.addEventListener('click', () => {
    var selectedIndexq1 = document.querySelector('#q1 input[type="radio"]:checked') ? Array.from(document.querySelectorAll('#q1 input[type="radio"]')).indexOf(document.querySelector('#q1 input[type="radio"]:checked')) : -1;
    var selectedIndexq2 = document.querySelector('#q2 input[type="radio"]:checked') ? Array.from(document.querySelectorAll('#q2 input[type="radio"]')).indexOf(document.querySelector('#q2 input[type="radio"]:checked')) : -1;
    if (selectedIndexq1 == -1 && currentEpisode == 7) {
      return;
    }
    if (selectedIndexq2 == -1 && currentEpisode == 16) {
      return;
    }
    
    console.log(selectedIndexq1);
    if (selectedIndexq1 == 1 && currentEpisode == 7) {
      atnCheck = true;
    }
    if (selectedIndexq2 == 3 && currentEpisode == 16) {
      atnCheck = true;
    }
    fetch(`/attention_check?atn=${atnCheck}`)
      .then(response => response.json())
      .then(data => {
        if (data.redirect) {
            // If the server responded with a redirect, navigate to that page
            window.location.href = data.redirect;
        } else {
            let suc = data.success;
            if (suc == 1) {
              atnStocksDiv.style.display = 'none';
              atnStocksDiv.style.pointerEvents = "none";
              stocksDiv.style.display = 'flex';
              stocksDiv.style.pointerEvents = "auto";
              recommendationContent.innerHTML = '';
              recommendationDiv.style.display = 'none';
              atnCheck = false;
            }
        }
      });
    });

  function setIntention(opt, i){
    intention = opt;
    isIntention = true;
    stockOptions.forEach((o, index) => {
      if (o === opt){
      o.classList.add("intention");
      intendedOptionIndex = index;
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
            
            fetch(`/get_recommendation?intendedOption=${intendedOptionIndex}`)
              .then(response => response.json())
              .then(data=>{
                agents = data.agents;
                curCase = data.cases;
                expForRec = data.expForRec;
                condition = data.condition;
                ar.forEach((div, index) => {
                  stockOptions[index].style.backgroundColor = "#f0f0f0";
                  if (index === agents - 1 && !recommendationShown) {
                    const image = document.createElement("img");
                    if (condition == 2){
                      div.classList.remove(div.classList.item(0));
                      div.classList.add("warmupagents-rec");
                      const image = document.createElement("img");
                      image.src = "../static/hand_100.png";
                      image.classList.remove("still");
                      image.classList.add("slide-down");
                      div.innerHTML = "";
                      div.appendChild(image);
                      
                      stockOptions[index].style.backgroundColor = "#e6f4e6";
                      // Set the recommendationShown flag to true
                      recommendationShown = true;
                    }
                    else{
                      image.src = "../static/hand_50.png";
                      image.classList.remove("still");
                      image.classList.add("slide-down");
                      div.innerHTML = "";
                      div.appendChild(image);            
                    
                      recommendationContent.innerHTML = expForRec;
                      recommendationDiv.style.width = "";
                      recommendationDiv.style.display = "flex";
                      if (index === 0) {recommendationDiv.style.marginLeft = "-30%";}
                      else if (index === 1) {recommendationDiv.style.marginLeft = "-25%";}
                      else if (index === 2) {recommendationDiv.style.marginLeft = "-8.45%";}
                      else if (index === 3) {recommendationDiv.style.marginLeft = "8.45%";}
                      else if (index === 4) {recommendationDiv.style.marginLeft = "25%";}
                      else if (index === 5) {recommendationDiv.style.marginLeft = "30%";}
                    }
                    stockOptions[index].style.backgroundColor = "#e6f4e6";
                    //recommendationDiv.style.marginLeft = 
                    // Set the recommendationShown flag to true
                    recommendationShown = true;
                  } else if (index === agents - 1) {
                    const image = document.createElement("img");
                    image.src = "../static/hand_50.png";        
                    image.classList.remove("slide-down");          
                    image.classList.add("still");
                    div.innerHTML = "";
                    div.appendChild(image);
                    if (condition != 2){
                      const recommendationDiv = document.getElementById("recommendation-text");
                      recommendationDiv.style.display = "none";
                    }
                    
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
  
  surveyButton.addEventListener("click", () => {
    let q = 0;
    if (currentEpisode == 10) {q=1;}
    else {q = 2;}
    fetch(`/get_strategy?q=${q}&a=${surveyAnswer.value}`)
      .then(response => response.json())
      .then(data => {let suc = data.success;});

    surveyDiv.style.display = "none";
    surveyButton.style.display = "none";
    stocksDiv.style.display = 'flex';
    stocksDiv.style.pointerEvents = "auto";
    rewardDiv.style.display = "block";
    proceedDiv.style.display = "block";
    surveyAnswer.innerHTML = "";
  });

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
          const rewardText = `Reward received: ${data.reward}`;
          expPostSel = data.expPostSel;
          if (currentEpisode >= episodes) {
            const realMoney = data.money;
            console.log(realMoney);
          }
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
          if(condition != 2){
            recommendationContent.innerHTML = expPostSel;
            recommendationDiv.style.margin = "";
          }
          
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
                      recommendationContent.innerHTML = "";
                      recommendationDiv.style.display = "none";
                      updateProgressBar(selectedList);
                      if (currentEpisode == 10 || currentEpisode == 20) {
                        stocksDiv.style.display = 'none';
                        stocksDiv.style.pointerEvents = "none";
                        surveyDiv.style.display = "block";
                        surveyAnswer.value = "";
                        surveyButton.style.display = "inline";
                        surveyButton.className = "inactive-button";
                        rewardDiv.style.display = "none";
                        proceedDiv.style.display = "none";
                      }
                      if (currentEpisode == 7 || currentEpisode == 16) {
                        stocksDiv.style.display = 'none';
                        stocksDiv.style.pointerEvents = "none";
                        atnStocksDiv.style.display = 'block';
                        atnStocksDiv.style.pointerEvents = "auto";
                        if (currentEpisode == 7){
                          q1.style.display = 'block';
                          q2.style.display = 'none';
                        }
                        else {
                          q1.style.display = 'none';
                          q2.style.display = 'block';
                        }
                        recommendationDiv.style.display = "none";
                      } else {
                        stocksDiv.style.pointerEvents = "auto";
                      }
                    });
                    isAnimating = false; // Reset animation flag
                  }, 300);
                },
              });
            },
          });          
          resetIntention();
          recommendationShown = false;          
        });         
        
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
        
        agentsDiv.style.display = "none";
        surveyDiv.style.display = "none";
        completeDiv.style.display = "block";
        completeButton.className = "button"; 

        return;
      }, 2000);      
    }
    
  });
  // Initial progress bar update  
  updateProgressBar(selectedList);
});
