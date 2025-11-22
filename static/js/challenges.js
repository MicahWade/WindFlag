document.addEventListener('DOMContentLoaded', function() {
    const challengeCards = document.querySelectorAll('.challenge-card');
    const challengeModal = document.getElementById('challengeModal');
    const modalContent = challengeModal.querySelector('div:first-child');
    const closeModalButtons = document.querySelectorAll('.close-modal');
    const modalChallengeName = document.getElementById('modalChallengeName');
    const modalChallengeDescription = document.getElementById('modalChallengeDescription');
    const modalChallengePoints = document.getElementById('modalChallengePoints');
    const modalChallengeStatus = document.getElementById('modalChallengeStatus');
    const modalFlagProgress = document.getElementById('modalFlagProgress');
    const modalFlagForm = document.getElementById('modalFlagForm');
    const flagInput = document.getElementById('modalFlagInput');
    const submitButton = document.getElementById('modalSubmitButton');
    const hintsList = document.getElementById('hintsList'); // New: Get hints list container
    const userScoreDisplay = document.getElementById('userScoreDisplay'); // Assuming you have a score display element

    let currentChallengeId = null;

    // Function to get a color based on percentage
    function getColorForPercentage(percentage) {
        if (percentage === 100) {
            return 'bg-green-600'; // Completed
        } else if (percentage >= 75) {
            return 'bg-lime-600';
        } else if (percentage >= 50) {
            return 'bg-yellow-500';
        } else if (percentage >= 25) {
            return 'bg-orange-500';
        } else if (percentage > 0) {
            return 'bg-red-600';
        } else {
            return 'bg-gray-800'; // Default for 0% or not started
        }
    }

    // Function to display flash messages
    function showFlashMessage(message, category) {
        const flashContainer = document.getElementById('flash-messages'); // Assuming a container for flash messages
        if (!flashContainer) {
            console.warn('Flash message container not found. Message:', message);
            alert(message); // Fallback to alert
            return;
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = `p-3 mb-3 rounded-md text-sm ${category === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`;
        alertDiv.textContent = message;
        flashContainer.appendChild(alertDiv);

        // Automatically remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    challengeCards.forEach(card => {
        const completionPercentage = parseInt(card.dataset.completionPercentage);
        const isCompleted = card.dataset.completed === 'true';
        const isLocked = card.classList.contains('locked-challenge'); // Check if the card is locked

        // Apply initial background color based on completion percentage for unlocked challenges
        if (!isCompleted && !isLocked) {
            card.classList.remove('bg-gray-800'); // Remove default background
            card.classList.add(getColorForPercentage(completionPercentage));
        }

        card.addEventListener('click', function() {
            if (isLocked) {
                // If the challenge is locked, do not open the modal.
                // The unlock information is already displayed on the card itself.
                return; 
            }

            currentChallengeId = this.dataset.id;
            
            // Fetch challenge details including hints
            fetch(`/api/challenge_details/${currentChallengeId}`)
                .then(response => response.json())
                .then(data => {
                    modalChallengeName.textContent = data.name;
                    try {
                        modalChallengeDescription.innerHTML = marked.parse(data.description);
                    } catch (e) {
                        console.error('Error parsing markdown:', e);
                        modalChallengeDescription.textContent = data.description;
                    }
                    modalChallengePoints.textContent = data.points + ' pts';

                    const isCompleted = data.is_completed;
                    const multiFlagType = data.multi_flag_type;
                    let submittedFlagsCount = data.submitted_flags_count;
                    let totalFlags = data.total_flags;

                    // Reset modal status and progress
                    modalChallengeStatus.classList.add('hidden');
                    modalFlagProgress.classList.add('hidden');
                    modalFlagProgress.textContent = '';

                    if (isCompleted) {
                        modalChallengeStatus.textContent = 'You have already completed this challenge!';
                        modalChallengeStatus.classList.remove('hidden');
                        flagInput.disabled = true;
                        submitButton.disabled = true;
                        submitButton.classList.add('opacity-50', 'cursor-not-allowed');
                    } else {
                        flagInput.disabled = false;
                        submitButton.disabled = false;
                        submitButton.classList.remove('opacity-50', 'cursor-not-allowed');

                        if (totalFlags > 1) {
                            modalFlagProgress.textContent = `Flags submitted: ${submittedFlagsCount} / ${totalFlags}`;
                            modalFlagProgress.classList.remove('hidden');
                        }
                    }

                    // Populate hints section
                    if (data.hints && data.hints.length > 0) {
                        hintsList.innerHTML = ''; // Clear previous hints
                        document.getElementById('modalHintsSection').classList.remove('hidden'); // Show the section
                        data.hints.forEach(hint => {
                            const hintDiv = document.createElement('div');
                            hintDiv.className = 'hint-item mb-2 p-3 bg-gray-700 rounded-md';
                            if (hint.is_revealed) {
                                hintDiv.innerHTML = `<p class="text-gray-300">${hint.content}</p>`;
                            } else {
                                hintDiv.className += ' flex justify-between items-center';
                                hintDiv.innerHTML = `
                                    <span class="text-gray-300">${hint.title} (Cost: ${hint.cost} pts)</span>
                                    <button class="reveal-hint-btn bg-yellow-600 hover:bg-yellow-500 text-white font-bold py-1 px-3 rounded text-xs" data-hint-id="${hint.id}" data-hint-cost="${hint.cost}">Reveal Hint</button>
                                `;
                            }
                            hintsList.appendChild(hintDiv);
                        });
                    } else {
                        document.getElementById('modalHintsSection').classList.add('hidden'); // Hide the section
                        hintsList.innerHTML = ''; // Ensure it's empty
                    }

                    // Update form action for submission
                    modalFlagForm.action = `/submit_flag/${currentChallengeId}`;
                    
                    // Show modal with animation
                    challengeModal.classList.remove('opacity-0', 'pointer-events-none');
                    modalContent.classList.remove('-translate-y-full');
                })
                .catch(error => {
                    console.error('Error fetching challenge details:', error);
                    showFlashMessage('Error loading challenge details.', 'danger');
                });
        });
    });

    // Event delegation for reveal hint buttons
    hintsList.addEventListener('click', function(event) {
        const revealBtn = event.target.closest('.reveal-hint-btn');
        if (revealBtn) {
            const hintId = revealBtn.dataset.hintId;
            const hintCost = parseInt(revealBtn.dataset.hintCost);
            const currentUserScore = parseInt(userScoreDisplay ? userScoreDisplay.textContent : '0'); // Get current score from display

            if (currentUserScore < hintCost) {
                showFlashMessage('You do not have enough points to reveal this hint.', 'danger');
                return;
            }

            if (!confirm(`Are you sure you want to reveal this hint for ${hintCost} points?`)) {
                return;
            }

            fetch(`/reveal_hint/${hintId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // If CSRF token is needed, add it here
                },
                body: JSON.stringify({}) // Send empty body for POST request
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showFlashMessage(data.message, 'success');
                    // Update the hint display
                    const hintDiv = revealBtn.closest('.hint-item');
                    if (hintDiv) {
                        hintDiv.innerHTML = `<p class="text-gray-300">${data.hint_content}</p>`;
                        hintDiv.classList.remove('flex', 'justify-between', 'items-center');
                    }
                    // Update user score display
                    if (userScoreDisplay) {
                        userScoreDisplay.textContent = data.new_score;
                    }
                } else {
                    showFlashMessage(data.message, 'danger');
                    // If hint was already revealed, update its content
                    if (data.message.includes('already revealed') && data.hint_content) {
                        const hintDiv = revealBtn.closest('.hint-item');
                        if (hintDiv) {
                            hintDiv.innerHTML = `<p class="text-gray-300">${data.hint_content}</p>`;
                            hintDiv.classList.remove('flex', 'justify-between', 'items-center');
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error revealing hint:', error);
                showFlashMessage('An error occurred while revealing the hint.', 'danger');
            });
        }
    });

    closeModalButtons.forEach(button => {
        button.addEventListener('click', function() {
            challengeModal.classList.add('opacity-0', 'pointer-events-none');
            modalContent.classList.add('-translate-y-full');
        });
    });

    challengeModal.addEventListener('click', function(event) {
        if (event.target === challengeModal) {
            challengeModal.classList.add('opacity-0', 'pointer-events-none');
            modalContent.classList.add('-translate-y-full');
        }
    });

    const challengeContent = document.getElementById('challengeContent');
    const solversContent = document.getElementById('solversContent');
    const solversList = document.getElementById('solversList');
    const solverCount = document.getElementById('solverCount');
    const viewSolversBtn = document.getElementById('viewSolversBtn');

    let showingSolvers = false; // State to track what is currently shown

    viewSolversBtn.addEventListener('click', function() {
        if (!showingSolvers) {
            // Currently showing challenge content, switch to solvers
            fetch(`/api/challenge/${currentChallengeId}/solvers`)
                .then(response => response.json())
                .then(data => {
                    solversList.innerHTML = '';
                    if (data.solvers.length > 0) {
                        data.solvers.forEach(solver => {
                            const li = document.createElement('li');
                            li.textContent = solver;
                            solversList.appendChild(li);
                        });
                    } else {
                        const li = document.createElement('li');
                            li.textContent = 'No solvers yet.';
                        solversList.appendChild(li);
                    }
                    solverCount.textContent = data.solver_count;
                    challengeContent.classList.add('hidden');
                    solversContent.classList.remove('hidden');
                    viewSolversBtn.textContent = 'View Challenge';
                    showingSolvers = true;
                })
                .catch(error => console.error('Error fetching solvers:', error));
        } else {
            // Currently showing solvers content, switch back to challenge
            solversContent.classList.add('hidden');
            challengeContent.classList.remove('hidden');
            viewSolversBtn.textContent = 'View Solvers';
            showingSolvers = false;
        }
    });

    modalFlagForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(modalFlagForm);
        const challengeId = currentChallengeId;

        fetch(`/submit_flag/${challengeId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showFlashMessage(data.message, data.success ? 'success' : 'danger');

            if (data.success) {
                const currentCard = document.querySelector(`.challenge-card[data-id="${challengeId}"]`);
                if (currentCard) {
                    if (data.message.includes('Challenge Solved!')) {
                        currentCard.dataset.completed = 'true';
                        currentCard.classList.add('completed-challenge');
                        currentCard.classList.remove(getColorForPercentage(parseInt(currentCard.dataset.completionPercentage)));
                        currentCard.classList.add(getColorForPercentage(100));

                        flagInput.disabled = true;
                        submitButton.disabled = true;
                        submitButton.classList.add('opacity-50', 'cursor-not-allowed');
                        modalChallengeStatus.textContent = data.message;
                        modalChallengeStatus.classList.remove('hidden');
                        modalFlagProgress.classList.add('hidden');
                    } else {
                        const submittedCountMatch = data.message.match(/submitted (\d+) of (\d+) flags/);
                        if (submittedCountMatch) {
                            const newSubmittedCount = parseInt(submittedCountMatch[1]);
                            const totalCount = parseInt(submittedCountMatch[2]);
                            currentCard.dataset.submittedFlagsCount = newSubmittedCount;
                            
                            const newCompletionPercentage = (newSubmittedCount / totalCount * 100);
                            currentCard.dataset.completionPercentage = newCompletionPercentage;

                            currentCard.classList.remove(getColorForPercentage(parseInt(currentCard.dataset.completionPercentage)));
                            currentCard.classList.add(getColorForPercentage(newCompletionPercentage));

                            const cardFlagProgress = currentCard.querySelector('p:last-child');
                            if (cardFlagProgress) {
                                cardFlagProgress.textContent = `Flags: ${newSubmittedCount} / ${totalCount}`;
                            }
                            if (totalCount > 1) {
                                modalFlagProgress.textContent = `Flags submitted: ${newSubmittedCount} / ${totalCount}`;
                                modalFlagProgress.classList.remove('hidden');
                            } else {
                                modalFlagProgress.classList.add('hidden');
                            }
                        }
                    }
                }
                flagInput.value = '';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showFlashMessage('An error occurred during submission.', 'danger');
        });
    });

    // Accordion functionality
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    const ACCORDION_STATE_KEY = 'accordionState'; // Key for localStorage

    // Load accordion states from localStorage on page load
    const savedAccordionStates = JSON.parse(localStorage.getItem(ACCORDION_STATE_KEY)) || {};

    accordionHeaders.forEach(header => {
        const content = header.nextElementSibling;
        const icon = header.querySelector('.accordion-icon');
        const categoryId = header.dataset.categoryId; // Get the category ID

        // Initialize state based on localStorage or default to open
        let isOpen = savedAccordionStates[categoryId] !== false; // Default to true if not in storage or is true

        if (isOpen) {
            content.classList.remove('hidden');
            icon.classList.add('rotate-180');
        } else {
            content.classList.add('hidden');
            icon.classList.remove('rotate-180');
        }

        header.addEventListener('click', () => {
            // Toggle the 'hidden' class on the content
            content.classList.toggle('hidden');
            // Toggle the 'rotate-180' class on the icon
            icon.classList.toggle('rotate-180');

            // Update state and save to localStorage
            isOpen = !content.classList.contains('hidden');
            savedAccordionStates[categoryId] = isOpen;
            localStorage.setItem(ACCORDION_STATE_KEY, JSON.stringify(savedAccordionStates));
        });
    });
});