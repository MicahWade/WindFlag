document.addEventListener('DOMContentLoaded', function() {
    const challengeContainer = document.getElementById('challenge-container');
    if (!challengeContainer) {
        return;
    }
    const loading = document.getElementById('loading');
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
    const hintsList = document.getElementById('hintsList');
    const userScoreDisplay = document.getElementById('userScoreDisplay');

    const flagSubmissionSection = document.getElementById('flagSubmissionSection');
    const codeSubmissionSection = document.getElementById('codeSubmissionSection');
    const codeEditor = document.getElementById('codeEditor');
    let editor = CodeMirror.fromTextArea(codeEditor, {
        lineNumbers: true,
        mode: "text/plain",
        theme: "dracula",
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false
    });
    const modalRunCodeButton = document.getElementById('modalRunCodeButton');
    const codeResult = document.getElementById('codeResult');

    let currentChallengeId = null;
    let currentChallengeType = null;
    let currentChallengeLanguage = null;

    function initChallengeCards() {
        const challengeCards = document.querySelectorAll('.challenge-card');
        challengeCards.forEach(card => {
            card.addEventListener('click', function() {
                currentChallengeId = this.dataset.id;
                
                fetch(`/api/challenge_details/${currentChallengeId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success === false) {
                            showFlashMessage(data.message, 'danger');
                            challengeModal.classList.add('opacity-0', 'pointer-events-none');
                            modalContent.classList.add('-translate-y-full');
                            return;
                        }
    
                        modalChallengeName.textContent = data.name;
                        if (typeof marked !== 'undefined' && marked.parse) {
                            try {
                                modalChallengeDescription.innerHTML = marked.parse(data.description);
                            } catch (e) {
                                console.error('Error parsing markdown:', e);
                                modalChallengeDescription.textContent = data.description;
                            }
                        } else {
                            console.warn('Marked library not loaded, displaying raw description.');
                            modalChallengeDescription.textContent = data.description;
                        }
                        modalChallengePoints.textContent = data.points + ' pts';
    
                        const isCompleted = data.is_completed;
                        const multiFlagType = data.multi_flag_type;
                        let submittedFlagsCount = data.submitted_flags_count;
                        let totalFlags = data.total_flags;
    
                        modalChallengeStatus.classList.add('hidden');
                        modalFlagProgress.classList.add('hidden');
                        modalFlagProgress.textContent = '';
                        codeResult.classList.add('hidden');
    
                        if (data.challenge_type === 'CODING') {
                            flagSubmissionSection.classList.add('hidden');
                            codeSubmissionSection.classList.remove('hidden');
                            currentChallengeLanguage = data.language || 'python';
                            editor.setOption('mode', currentChallengeLanguage);
                            editor.setValue(data.starter_code || '');
                            if (isCompleted) {
                                editor.setOption('readOnly', true);
                                modalRunCodeButton.disabled = true;
                                modalRunCodeButton.classList.add('opacity-50', 'cursor-not-allowed');
                                modalChallengeStatus.textContent = 'You have already completed this coding challenge!';
                                modalChallengeStatus.classList.remove('hidden');
                            } else {
                                editor.setOption('readOnly', false);
                                modalRunCodeButton.disabled = false;
                                modalRunCodeButton.classList.remove('opacity-50', 'cursor-not-allowed');
                            }
                            editor.refresh();
                        } else {
                            flagSubmissionSection.classList.remove('hidden');
                            codeSubmissionSection.classList.add('hidden');
                            if (isCompleted) {
                                modalChallengeStatus.textContent = 'You have already completed this challenge!';
                                modalChallengeStatus.classList.remove('hidden');
                                flagInput.disabled = true;
                                submitButton.disabled = true;
                                submitButton.classList.add('opacity-50', 'cursor-not-allowed');
                            }
                            else {
                                flagInput.disabled = false;
                                submitButton.disabled = false;
                                submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
                                if (totalFlags > 1) {
                                    modalFlagProgress.textContent = `Flags submitted: ${submittedFlagsCount} / ${totalFlags}`;
                                    modalFlagProgress.classList.remove('hidden');
                                }
                            }
                        }
    
                        if (data.hints && data.hints.length > 0) {
                            hintsList.innerHTML = '';
                            document.getElementById('modalHintsSection').classList.remove('hidden');
                            data.hints.forEach(hint => {
                                const hintDiv = document.createElement('div');
                                hintDiv.className = 'hint-item mb-2 p-3 theme-modal-hint-item';
                                if (hint.is_revealed) {
                                    hintDiv.innerHTML = `<p>${hint.content}</p>`;
                                } else {
                                    hintDiv.className += ' flex justify-between items-center';
                                    hintDiv.innerHTML = `
                                        <span>${hint.title} (Cost: ${hint.cost} pts)</span>
                                        <button class="reveal-hint-btn theme-modal-button-primary font-bold py-1 px-3 text-xs" data-hint-id="${hint.id}" data-hint-cost="${hint.cost}">Reveal Hint</button>
                                    `;
                                }
                                hintsList.appendChild(hintDiv);
                            });
                        } else {
                            document.getElementById('modalHintsSection').classList.add('hidden');
                            hintsList.innerHTML = '';
                        }
    
                        if (data.challenge_type === 'FLAG') {
                            modalFlagForm.action = `/submit_flag/${currentChallengeId}`;
                        }
                        
                        challengeModal.classList.remove('opacity-0', 'pointer-events-none');
                        modalContent.classList.remove('-translate-y-full');
                    })
                    .catch(error => {
                        console.error('Error fetching challenge details:', error);
                        showFlashMessage('Error loading challenge details.', 'danger');
                    });
            });
        });
    }

    function initAccordion() {
        const accordionHeaders = document.querySelectorAll('.accordion-header');
        const ACCORDION_STATE_KEY = 'accordionState';
        const savedAccordionStates = JSON.parse(localStorage.getItem(ACCORDION_STATE_KEY)) || {};

        accordionHeaders.forEach(header => {
            const content = header.nextElementSibling;
            const icon = header.querySelector('.accordion-icon');
            const categoryId = header.dataset.categoryId;

            let isOpen = savedAccordionStates[categoryId] !== false;

            if (isOpen) {
                content.classList.remove('hidden');
                icon.classList.add('rotate-180');
            } else {
                content.classList.add('hidden');
                icon.classList.remove('rotate-180');
            }

            header.addEventListener('click', () => {
                content.classList.toggle('hidden');
                icon.classList.toggle('rotate-180');
                isOpen = !content.classList.contains('hidden');
                savedAccordionStates[categoryId] = isOpen;
                localStorage.setItem(ACCORDION_STATE_KEY, JSON.stringify(savedAccordionStates));
            });
        });
    }

    fetch('/api/public/challenges')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (loading) loading.style.display = 'none';
            let html = '';
            data.forEach(category => {
                let challengesHtml = '';
                let solvedCount = 0;
                category.challenges.forEach(challenge => {
                    if (challenge.solved) {
                        solvedCount++;
                    }
                    challengesHtml += `
                        <div class="theme-challenge-card theme-hover-card p-6 challenge-card cursor-pointer transform hover:scale-105 transition duration-300 ease-in-out ${challenge.solved ? 'theme-completed-challenge' : ''}"
                             data-id="${challenge.id}"
                             data-name="${challenge.name}"
                             data-description="${challenge.description}"
                             data-points="${challenge.points}"
                             data-completed="${challenge.solved}"
                             data-solves="${challenge.solves}">
                            <h5 class="theme-challenge-title text-xl font-bold mb-2">${challenge.name}</h5>
                            <p class="theme-challenge-points">${challenge.points} pts</p>
                            <p class="theme-challenge-solves text-sm">${challenge.solves} solves</p>
                        </div>
                    `;
                });

                html += `
                    <div class="accordion-item theme-accordion-item mb-6">
                        <div class="accordion-header p-4 cursor-pointer flex justify-between items-center" data-category-id="${category.name.toLowerCase().replace(/ /g, '-')}">
                            <h2 class="theme-category-title text-2xl font-semibold">${category.name}
                                <span class="theme-category-stats text-lg ml-2">(${solvedCount}/${category.challenges.length})</span>
                            </h2>
                            <svg class="w-6 h-6 transform transition-transform duration-200 accordion-icon rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                            </svg>
                        </div>
                        <div class="accordion-content p-4">
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                                ${challengesHtml}
                            </div>
                        </div>
                    </div>
                `;
            });
            challengeContainer.innerHTML = html;
            initChallengeCards();
            initAccordion();
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
            if (loading) loading.style.display = 'none';
            challengeContainer.innerHTML = '<p class="text-red-500">Could not load challenges. Please try again later.</p>';
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
                        currentCard.classList.add('theme-completed-challenge');
                        flagInput.disabled = true;
                        submitButton.disabled = true;
                        submitButton.classList.add('opacity-50', 'cursor-not-allowed');
                        modalChallengeStatus.textContent = data.message;
                        modalChallengeStatus.classList.remove('hidden');
                        modalFlagProgress.classList.add('hidden');
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

    function showFlashMessage(message, category) {
        const flashContainer = document.getElementById('flash-messages');
        if (!flashContainer) {
            console.warn('Flash message container not found. Message:', message);
            alert(message);
            return;
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = `p-3 mb-3 rounded-md text-sm ${category === 'success' ? 'theme-flash-success' : 'theme-flash-danger'}`;
        alertDiv.textContent = message;
        flashContainer.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});