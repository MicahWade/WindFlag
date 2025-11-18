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
    let currentChallengeId = null;

    // Function to get a color based on percentage
    function getColorForPercentage(percentage) {
        // Define color stops (e.g., red for 0%, yellow for 50%, green for 100%)
        // Using Tailwind CSS color classes
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

    challengeCards.forEach(card => {
        const completionPercentage = parseInt(card.dataset.completionPercentage);
        const isCompleted = card.dataset.completed === 'true';

        // Apply initial background color based on completion percentage
        if (!isCompleted) {
            card.classList.remove('bg-gray-800'); // Remove default background
            card.classList.add(getColorForPercentage(completionPercentage));
        }

        card.addEventListener('click', function() {
            currentChallengeId = this.dataset.id;
            modalChallengeName.textContent = this.dataset.name;
            modalChallengeDescription.textContent = this.dataset.description;
            modalChallengePoints.textContent = this.dataset.points + ' pts';

            const isCompleted = this.dataset.completed === 'true';
            const multiFlagType = this.dataset.multiFlagType;
            let submittedFlagsCount = parseInt(this.dataset.submittedFlagsCount);
            let totalFlags = parseInt(this.dataset.totalFlags);

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

                // Display flag progress for multi-flag challenges that are not yet completed
                // Changed condition to totalFlags > 1
                if (totalFlags > 1) {
                    modalFlagProgress.textContent = `Flags submitted: ${submittedFlagsCount} / ${totalFlags}`;
                    modalFlagProgress.classList.remove('hidden');
                }
            }

            // Update form action for submission
            modalFlagForm.action = `/submit_flag/${currentChallengeId}`;
            
            // Show modal with animation
            challengeModal.classList.remove('opacity-0', 'pointer-events-none');
            modalContent.classList.remove('-translate-y-full');
        });
    });

    closeModalButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Hide modal with animation
            challengeModal.classList.add('opacity-0', 'pointer-events-none');
            modalContent.classList.add('-translate-y-full');
        });
    });

    // Close modal when clicking outside of it
    challengeModal.addEventListener('click', function(event) {
        if (event.target === challengeModal) {
            // Hide modal with animation
            challengeModal.classList.add('opacity-0', 'pointer-events-none');
            modalContent.classList.add('-translate-y-full');
        }
    });

    const challengeContent = document.getElementById('challengeContent');
    const solversContent = document.getElementById('solversContent');
    const backToChallenge = document.getElementById('backToChallenge');
    const solversList = document.getElementById('solversList');
    const solverCount = document.getElementById('solverCount');
    const viewSolversBtn = document.getElementById('viewSolversBtn');

    viewSolversBtn.addEventListener('click', function() {
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
            })
            .catch(error => console.error('Error fetching solvers:', error));
    });

    backToChallenge.addEventListener('click', function() {
        solversContent.classList.add('hidden');
        challengeContent.classList.remove('hidden');
    });

    // Handle AJAX form submission
    modalFlagForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(modalFlagForm);
        const challengeId = currentChallengeId; // Use the stored currentChallengeId

        fetch(`/submit_flag/${challengeId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json()) // Assuming the server responds with JSON
        .then(data => {
            alert(data.message); // Display message from server

            if (data.success) {
                // Update the challenge card on the main page
                const currentCard = document.querySelector(`.challenge-card[data-id="${challengeId}"]`);
                if (currentCard) {
                    // If challenge is fully solved
                    if (data.message.includes('Challenge Solved!')) {
                        currentCard.dataset.completed = 'true';
                        currentCard.classList.add('completed-challenge');
                        // Update card color to green
                        currentCard.classList.remove(getColorForPercentage(parseInt(currentCard.dataset.completionPercentage)));
                        currentCard.classList.add(getColorForPercentage(100));

                        // Disable modal inputs
                        flagInput.disabled = true;
                        submitButton.disabled = true;
                        submitButton.classList.add('opacity-50', 'cursor-not-allowed');
                        modalChallengeStatus.textContent = data.message; // Changed this line
                        modalChallengeStatus.classList.remove('hidden');
                        modalFlagProgress.classList.add('hidden'); // Hide progress if solved
                    } else {
                        // Partial submission success, update flag count
                        const submittedCountMatch = data.message.match(/submitted (\d+) of (\d+) flags/);
                        if (submittedCountMatch) {
                            const newSubmittedCount = parseInt(submittedCountMatch[1]);
                            const totalCount = parseInt(submittedCountMatch[2]);
                            currentCard.dataset.submittedFlagsCount = newSubmittedCount;
                            
                            // Recalculate and update completion percentage
                            const newCompletionPercentage = (newSubmittedCount / totalCount * 100);
                            currentCard.dataset.completionPercentage = newCompletionPercentage;

                            // Update card color
                            currentCard.classList.remove(getColorForPercentage(parseInt(currentCard.dataset.completionPercentage))); // Remove old color
                            currentCard.classList.add(getColorForPercentage(newCompletionPercentage)); // Add new color

                            // Update the displayed progress in the card
                            const cardFlagProgress = currentCard.querySelector('p:last-child');
                            if (cardFlagProgress) {
                                cardFlagProgress.textContent = `Flags: ${newSubmittedCount} / ${totalCount}`;
                            }
                            // Update modal progress
                            // Changed condition to totalFlags > 1
                            if (totalCount > 1) {
                                modalFlagProgress.textContent = `Flags submitted: ${newSubmittedCount} / ${totalCount}`;
                                modalFlagProgress.classList.remove('hidden');
                            } else {
                                modalFlagProgress.classList.add('hidden');
                            }
                        }
                    }
                }
                flagInput.value = ''; // Clear flag input
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during submission.');
        });
    });
});