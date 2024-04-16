// Utility Functions
const generateSessionId = () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
});

const getSessionId = () => {
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
        sessionId = generateSessionId();
        sessionStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
};
achievements = [
    {
        id: 1,
        name: "The Direwolf Pact",
        description: "Ensure Sansa's direwolf, Lady, is not executed.",
        accomplished: false
    },
    {
        id: 2,
        name: "Crowned Stag",
        description: "Prevent the death of King Robert Baratheon.",
        accomplished: false
    },
    {
        id: 3,
        name: "Honor Preserved",
        description: "Save Ned Stark from being arrested.",
        accomplished: false
    },
    {
        id: 4,
        name: "Wolf and Lion Dance",
        description: "Forge an unlikely alliance between House Stark and House Lannister.",
        accomplished: false
    },
    {
        id: 5,
        name: "Keeper of Secrets",
        description: "Learn all the secrets Jon Arryn uncovered before his death.",
        accomplished: false
    },
    {
        id: 6,
        name: "Quantum Leap",
        description: "Make a decision that drastically alters the timeline of events from the book.",
        accomplished: false
    },
    {
        id: 7,
        name: "A Song Unchanged",
        description: "Complete the game without causing any major deviations from the book's main plotline.",
        accomplished: false
    }
];
// Achievement Management
const populateAchievements = achievements => {
    const list = document.getElementById('achievementsList');
    list.innerHTML = ''; // Clear list
    achievements.forEach(({name, description, accomplished}) => {
        const iconName = name.replace(/\s+/g, '_') + (accomplished ? "" : "-modified") + ".png";
        const item = document.createElement('li');
        item.innerHTML = `
            <img src="icons/${iconName}" alt="${name}" style="width: 100px; height: 100px; vertical-align: middle;">
            ${name} - ${description} ${accomplished ? '✅' : '❌'}
        `;
        list.appendChild(item);
    });

};

// Game Initialization and Control
const initializeIntroduction = () => {
    document.getElementById('cliOutput').textContent = "Welcome to the ASOIAF Adventure. Your mission is to save Ned Stark. Click 'Start' to begin.";
    document.getElementById('userInput').disabled = true;
    const submitButton = document.querySelector('button[type="submit"]');
    submitButton.textContent = "Start";
    document.getElementById('cliForm').addEventListener('submit', handleGameStart, {once: true});
};

const handleGameStart = event => {
    event.preventDefault();
    document.getElementById('userInput').disabled = false;
    document.querySelector('button[type="submit"]').textContent = "Submit";
    document.getElementById('cliOutput').textContent = "";
    const bgMusic = document.getElementById('bgMusic');
    bgMusic.play()
    fetchInitialText();
    setUpFormSubmission();
};

const fetchInitialText = async () => {
    const sessionId = getSessionId();
    const submitButton = document.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    try {
        const response = await fetch(`/api/initial_text?session_id=${sessionId}`);
        const data = await response.json();
        document.getElementById('cliOutput').textContent = data.text;
        fetchAndUpdateProgressBar();
    } catch (error) {
        console.error('Error fetching initial text:', error);
    } finally {
        submitButton.disabled = false;
    }
};

const setUpFormSubmission = () => {
    document.getElementById('cliForm').addEventListener('submit', async event => {
        event.preventDefault();
        const userInput = document.getElementById('userInput').value;
        const submitButton = document.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            const sessionId = getSessionId();
            const response = await fetch('/api/submit_input', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({userInput, sessionId}),
            });
            const resultData = await response.json();
            document.getElementById('cliOutput').textContent = resultData.finalText;
            populateConversationHistory();
            fetchAndUpdateProgressBar();
            const achievementsResponse = await fetch(`/api/achievements?session_id=${sessionId}`);
            const achievementsData = await achievementsResponse.json();
            populateAchievements(achievementsData.achievements);
            populateIconsAndButton(achievementsData.achievements);
            setupAchievementsModal()
            fetchNewAchievements(sessionId);
            const end_gameResponse = await fetch(`/api/end_game?session_id=${sessionId}`);
            const end_gameData = await end_gameResponse.json();
            if (end_gameData.end_game) {
                document.getElementById('userInput').disabled = true;
                submitButton.textContent = "Game Over";
                submitButton.disabled = true;
            }
        } catch (error) {
            console.error('Error during fetch operation:', error);
        } finally {
            document.getElementById('userInput').value = '';
            submitButton.disabled = false;
        }
    });
};

// Modal and Achievements UI
const setupAchievementsModal = () => {
    const achievementsModal = document.getElementById('achievementsModal');
    document.getElementById('achievementsButton').onclick = () => {
        populateAchievements(achievements); // Assuming 'achievements' is globally accessible
        achievementsModal.style.display = 'block';
    };
    document.getElementsByClassName('close')[0].onclick = () => achievementsModal.style.display = 'none';
    window.onclick = event => {
        if (event.target === achievementsModal) achievementsModal.style.display = 'none';
    };
};

// Main
document.addEventListener("DOMContentLoaded", () => {
    const bgMusic = document.getElementById('bgMusic');

    // Attempt to play music when the document is fully loaded
    const playPromise = bgMusic.play();
    if (playPromise !== undefined) {
        playPromise.then(_ => {
            console.log("Autoplay started successfully.");
        }).catch(error => {
            console.log("Autoplay was prevented:", error);
            // Here you might add a user interface indication that autoplay failed
        });
    }
    initializeIntroduction();
    populateIconsAndButton(achievements);
    setupAchievementsModal();
});

const populateIconsAndButton = (achievements) => {
    const container = document.getElementById('iconsAndAchievementContainer');
    container.innerHTML = ''; // Clear container

    // Add the first three achievements as icons
    achievements.slice(0, 3).forEach(achievement => {
        const iconFileName = achievement.name.replace(/\s+/g, '_') + (achievement.accomplished ? "" : "-modified") + ".png";
        const iconElement = document.createElement('img');
        iconElement.src = `icons/${iconFileName}`; // Update the path accordingly
        iconElement.alt = achievement.description;
        iconElement.className = 'icon'; // Use this class for styling
        container.appendChild(iconElement);
    });

    // Create and add the Achievement button
    const button = document.createElement('button');
    button.id = 'achievementsButton';
    button.textContent = 'Achievements';
    button.className = 'achievement-button'; // Use this class for styling if needed
    container.appendChild(button);
};

const populateConversationHistory = async () => {
    const historyContainer = document.getElementById('conversationHistory');
    historyContainer.innerHTML = ''; // Clear previous content

    try {
        const sessionId = getSessionId(); // Assuming getSessionId() retrieves the current session
        const response = await fetch(`/api/conversation_history?session_id=${sessionId}`);
        const data = await response.json(); // Assuming the endpoint returns a JSON list of strings

        // Append each message as a paragraph to the history container
        data.forEach(message => {
            const p = document.createElement('p');
            p.textContent = message;
            historyContainer.appendChild(p);
        });
    } catch (error) {
        console.error('Error fetching conversation history:', error);
    }
};

function fetchAndUpdateProgressBar() {
    fetch(`/api/current_progress?session_id=${getSessionId()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const currentProgress = data.progress[0];
            const totalEvents = data.progress[1];
            const percentage = ((currentProgress / totalEvents) * 100).toFixed(2);

            document.getElementById("progressBar").style.width = percentage + '%';
            document.getElementById("progressText").innerText = `percentage: ${percentage}%`;
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}

const showAchievementPopup = (achievement) => {
  const container = document.getElementById('achievementPopupContainer');
  const popup = document.createElement('div');
  popup.className = 'achievement-popup';
  popup.innerHTML = `
    <h4>New Achievement Unlocked!</h4>
    <strong>${achievement.name}</strong>
    <p>${achievement.description}</p>
  `;

  container.appendChild(popup);

  // Automatically remove the popup after a delay (e.g., 5 seconds)
  setTimeout(() => {
    popup.style.opacity = '0';
    setTimeout(() => popup.remove(), 500); // Wait for fade out to remove
  }, 5000);
};

async function fetchNewAchievements(sessionId) {
    if (Math.random() >= 0.25) {
        // If the random number is not below 0.25, end the function early
        console.log('Skipping fetchNewAchievements due to probability check.');
        return;
    }
    const response = await fetch(`/api/new_achievements?session_id=${sessionId}`);
    if (response.ok) {
        const data = await response.json();
        const newAchievement = data.new_achievements;
        showAchievementPopup(newAchievement);
    } else {
        console.error('Failed to fetch new achievements');
    }
}


function toggleMute() {
    const music = document.getElementById('bgMusic');
    music.muted = !music.muted;
    console.log("Mute toggled. Current state: " + (music.muted ? "Muted" : "Unmuted"));
    if (!music.muted) {
        music.play().catch(error => {
            console.log("Failed to play after unmuting:", error);
        });
    }
}

// You can expose toggleMute if it needs to be globally accessible
window.toggleMute = toggleMute;

// Log when the audio starts playing
document.getElementById("bgMusic").oncanplaythrough = function() {
    console.log("Audio is loaded and can play through.");
};

document.getElementById("bgMusic").onplay = function() {
    console.log("Audio is now playing.");
};

// Check if the music plays automatically or is blocked by browser policies
document.getElementById("bgMusic").autoplay = true;
document.getElementById("bgMusic").play().catch(error => {
    console.log("Audio failed to play automatically. Error: " + error.message);
});