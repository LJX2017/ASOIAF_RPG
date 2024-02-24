// Generates a pseudo-random UUID.
function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Retrieves or creates a new session ID and stores it in sessionStorage.
function getSessionId() {
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
        sessionId = generateSessionId();
        sessionStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
}
document.addEventListener("DOMContentLoaded", function() {

    // Example achievements data
    const achievements = [
        { id: 1, name: 'First Step', description: 'Complete the first challenge.', accomplished: true},
        { id: 2, name: 'Master Strategist', description: 'Make a pivotal decision.', accomplished: false},
        // Add more achievements as needed
    ];

    const achievementsButton = document.getElementById('achievementsButton');
    const achievementsModal = document.getElementById('achievementsModal');
    const closeSpan = document.getElementsByClassName('close')[0];

    achievementsButton.onclick = function() {
        populateAchievements(achievements);
        achievementsModal.style.display = 'block';
    }

    closeSpan.onclick = function() {
        achievementsModal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target === achievementsModal) {
            achievementsModal.style.display = 'none';
        }
    }
    initializeIntroduction();
});
function populateAchievements(achievements) {
    const list = document.getElementById('achievementsList');
    list.innerHTML = ''; // Clear existing achievements

    achievements.forEach(achievement => {
        const item = document.createElement('li');
        item.innerHTML = `
            <img src="icons/img.png" alt="${achievement.name}" style="width: 24px; height: 24px; vertical-align: middle;">
            ${achievement.name} - ${achievement.description} ${achievement.accomplished ? '✅' : '❌'}
        `;
        list.appendChild(item);
    });
}
function initializeIntroduction() {
    // Display the introductory text in the text box (or another element if preferred)
    const cliOutput = document.getElementById('cliOutput');
    cliOutput.textContent = "Welcome to the ASOIAF Adventure. Your mission is to save Ned Stark. Click 'Start' to begin.";

    // Change the button text to "Start"
    const submitButton = document.querySelector('button[type="submit"]');
    submitButton.textContent = "Start";

    // Listen for the first submit to start the game
    const form = document.getElementById('cliForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission
        startGame(); // Call the function to start the game
    }, { once: true }); // Ensure the listener only fires once
}

function startGame() {
    // Reset the button text for game use
    const submitButton = document.querySelector('button[type="submit"]');
    submitButton.textContent = "Submit";

    // Clear the introductory text and prepare for game input
    const cliOutput = document.getElementById('cliOutput');
    cliOutput.textContent = "";

    // Now the form submission should handle game inputs
    setUpFormSubmission();

    // You might also want to fetch the initial game state or text here
    fetchInitialText();
}
// Fetches initial text for the session and updates the UI.
async function fetchInitialText() {
    const sessionId = getSessionId();
    const submitButton = document.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    try {
        const response = await fetch(`/api/initial_text?session_id=${sessionId}`);
        const data = await response.json();
        document.getElementById('cliOutput').textContent = data.text;
    } catch (error) {
        console.error('Error fetching initial text:', error);
    } finally {
        submitButton.disabled = false;
    }
}

// Sets up the form submission handler to send user input to the server.
function setUpFormSubmission() {
    document.getElementById('cliForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const userInput = document.getElementById('userInput').value;
        const submitButton = document.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const sessionId = getSessionId();
        try {
            const response = await fetch('/api/submit_input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userInput, sessionId }),
            });
            const resultData = await response.json();
            document.getElementById('cliOutput').textContent = resultData.finalText;
        } catch (error) {
            console.error('Error during fetch operation:', error);
        } finally {
            submitButton.disabled = false;
        }
    });
}

// Initializes the app once the DOM is fully loaded.
// document.addEventListener("DOMContentLoaded", function() {
//     console.log("DOMContentLoaded event fired");
//     fetchInitialText();
//     setUpFormSubmission();
// });
