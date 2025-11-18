document.addEventListener('DOMContentLoaded', function() {
    const challengeCards = document.querySelectorAll('.challenge-card');
    const challengeModal = document.getElementById('challengeModal');
    const modalContent = challengeModal.querySelector('div:first-child'); // Select the first child div which is the modal content
    const closeModalButtons = document.querySelectorAll('.close-modal');
    const modalChallengeName = document.getElementById('modalChallengeName');
    const modalChallengeDescription = document.getElementById('modalChallengeDescription');
    const modalChallengePoints = document.getElementById('modalChallengePoints');
    const modalChallengeStatus = document.getElementById('modalChallengeStatus');
    const modalFlagForm = document.getElementById('modalFlagForm');
    const flagInput = document.getElementById('modalFlagInput');
    const submitButton = document.getElementById('modalSubmitButton');
    let currentChallengeId = null;

    challengeCards.forEach(card => {
        card.addEventListener('click', function() {
            currentChallengeId = this.dataset.id;
            modalChallengeName.textContent = this.dataset.name;
            modalChallengeDescription.textContent = this.dataset.description;
            modalChallengePoints.textContent = this.dataset.points + ' pts';

            const isCompleted = this.dataset.completed === 'true';

            if (isCompleted) {
                modalChallengeStatus.textContent = 'You have already completed this challenge!';
                modalChallengeStatus.classList.remove('hidden');
                flagInput.disabled = true;
                submitButton.disabled = true;
                submitButton.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                modalChallengeStatus.classList.add('hidden');
                flagInput.disabled = false;
                submitButton.disabled = false;
                submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
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
            if (data.success) {
                alert(data.message); // Or display a more sophisticated success message
                // Hide modal with animation
                challengeModal.classList.add('opacity-0', 'pointer-events-none');
                modalContent.classList.add('-translate-y-full');
                // Optionally, update the challenge card's status on the main page
                const completedCard = document.querySelector(`.challenge-card[data-id="${challengeId}"]`);
                if (completedCard) {
                    completedCard.dataset.completed = 'true';
                    completedCard.classList.add('completed-challenge');
                    // Update points if necessary, though usually score is global
                }
                // Reload the page to reflect score changes and completed status
                window.location.reload();
            } else {
                alert(data.message); // Display error message
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during submission.');
        });
    });
});