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

    const modalRunCodeButton = document.getElementById('modalRunCodeButton');
    const codeResult = document.getElementById('codeResult');

    let currentChallengeId = null;
    let currentChallengeType = null;
    let currentChallengeLanguage = null;
    let codeMirrorEditor = null; // Initialize CodeMirror editor here

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
                            currentChallengeType = 'CODING';

                            if (!codeMirrorEditor) {
                                codeMirrorEditor = CodeMirror.fromTextArea(codeEditor, {
                                    lineNumbers: true,
                                    mode: currentChallengeLanguage,
                                    theme: "dracula",
                                    indentUnit: 4,
                                    tabSize: 4,
                                    indentWithTabs: false,
                                    viewportMargin: Infinity,
                                    fullScreen: false // Ensure CodeMirror is NOT fullscreen by default
                                });
                                codeMirrorEditor.getWrapperElement().classList.add('codemirror-themed-input');
                                
                                // Dynamically create and append fullscreen button
                                const fullscreenButton = document.createElement('button');
                                fullscreenButton.innerHTML = `
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
                                    </svg>
                                `;
                                fullscreenButton.title = "Enter Fullscreen (F11)";
                                fullscreenButton.className = "CodeMirror-fullscreen-button-custom absolute top-2 right-2 p-1 rounded-full bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white z-10";
                                
                                fullscreenButton.addEventListener('click', (event) => {
                                    event.preventDefault();
                                    codeMirrorEditor.setOption("fullScreen", !codeMirrorEditor.getOption("fullScreen"));
                                });
                                codeMirrorEditor.getWrapperElement().appendChild(fullscreenButton);
                                
                                // Add an event listener to update the button icon when fullscreen state changes
                                codeMirrorEditor.on('optionChange', (cm, option) => {
                                    if (option === 'fullScreen') {
                                        if (cm.getOption("fullScreen")) {
                                            fullscreenButton.innerHTML = `Exit`;
                                            fullscreenButton.title = "Exit Fullscreen (Esc)";
                                            fullscreenButton.classList.add('text-lg', 'px-3'); // Make it bigger and more visible
                                        } else {
                                            fullscreenButton.innerHTML = `
                                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
                                                </svg>
                                            `;
                                            fullscreenButton.title = "Enter Fullscreen (F11)";
                                            fullscreenButton.classList.remove('text-lg', 'px-3');
                                        }
                                    }
                                });

                            } else {
                                codeMirrorEditor.setOption('mode', currentChallengeLanguage);
                                codeMirrorEditor.getWrapperElement().classList.add('codemirror-themed-input'); // Ensure class is applied on re-use
                            }
                            codeMirrorEditor.setValue(data.starter_code || '');
                            if (isCompleted) {
                                codeMirrorEditor.setOption('readOnly', true);
                                modalRunCodeButton.disabled = true;
                                modalRunCodeButton.classList.add('opacity-50', 'cursor-not-allowed');
                                modalChallengeStatus.textContent = 'You have already completed this coding challenge!';
                                modalChallengeStatus.classList.remove('hidden');
                            } else {
                                codeMirrorEditor.setOption('readOnly', false);
                                modalRunCodeButton.disabled = false;
                                modalRunCodeButton.classList.remove('opacity-50', 'cursor-not-allowed');
                            }
                            codeMirrorEditor.refresh();
                        } else {
                            flagSubmissionSection.classList.remove('hidden');
                            codeSubmissionSection.classList.add('hidden');
                            currentChallengeType = 'FLAG';

                            if (codeMirrorEditor) {
                                // If editor exists, destroy it
                                codeMirrorEditor.toTextArea(); 
                                codeMirrorEditor = null;
                            }

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

                            // --- Add Switchboard Button Logic Here ---
                            if (typeof window.enableSwitchboard !== 'undefined' && window.enableSwitchboard) {
                                let switchboardButton = document.getElementById('switchboardButton');
                                if (!switchboardButton) {
                                    switchboardButton = document.createElement('a');
                                    switchboardButton.id = 'switchboardButton';
                                    switchboardButton.textContent = 'Go to Challenge';
                                    switchboardButton.target = '_blank'; // Open in new tab
                                    switchboardButton.className = 'theme-modal-button-secondary font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-sm shadow-md ml-2';
                                    submitButton.parentNode.insertBefore(switchboardButton, submitButton.nextSibling);
                                }

                                // Ensure category_name exists in data. If not, default to an empty string to avoid errors.
                                const categoryName = data.category_name || '';
                                const challengeName = data.name || '';

                                const categoryNameFormatted = categoryName.replace(/ /g, '_');
                                const challengeNameFormatted = challengeName.replace(/ /g, '_');
                                switchboardButton.href = `${window.switchboardBaseUrl}/${categoryNameFormatted}/${challengeNameFormatted}`;
                                switchboardButton.classList.remove('hidden'); // Ensure it's visible if enabled
                            } else {
                                // If switchboard is not enabled, hide the button if it exists
                                const switchboardButton = document.getElementById('switchboardButton');
                                if (switchboardButton) {
                                    switchboardButton.classList.add('hidden');
                                }
                            }
                            // --- End Switchboard Button Logic ---
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
    
                        if (currentChallengeType === 'FLAG') {
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

    modalRunCodeButton.addEventListener('click', function() {
        if (!codeMirrorEditor) return;

        const userCode = codeMirrorEditor.getValue();
        modalRunCodeButton.disabled = true;
        modalRunCodeButton.classList.add('opacity-50', 'cursor-not-allowed');
        codeResult.classList.remove('hidden');
        codeResult.textContent = 'Running code...';

        fetch(`/api/challenges/${currentChallengeId}/submit_code`, { // Fixed URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: userCode, language: currentChallengeLanguage })
        })
        .then(async response => {
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP Error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            codeResult.textContent = data.output;
            if (data.success) {
                showFlashMessage('Code executed successfully!', 'success');
                if (data.is_correct) {
                    showFlashMessage('Challenge Solved!', 'success');
                    const currentCard = document.querySelector(`.challenge-card[data-id="${currentChallengeId}"]`);
                    if (currentCard) {
                        currentCard.dataset.completed = 'true';
                        currentCard.classList.add('theme-completed-challenge');
                        codeMirrorEditor.setOption('readOnly', true);
                        modalRunCodeButton.disabled = true;
                        modalRunCodeButton.classList.add('opacity-50', 'cursor-not-allowed');
                        modalChallengeStatus.textContent = 'You have already completed this coding challenge!';
                        modalChallengeStatus.classList.remove('hidden');
                    }
                }
            } else {
                showFlashMessage(data.message || 'Error executing code.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error running code:', error);
            codeResult.textContent = `Error: ${error.message}`;
            showFlashMessage('An error occurred during code execution.', 'danger');
        })
        .finally(() => {
            modalRunCodeButton.disabled = false;
            modalRunCodeButton.classList.remove('opacity-50', 'cursor-not-allowed');
        });
    });



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
                        <div class="theme-challenge-card theme-hover-card p-6 challenge-card cursor-pointer transform hover:scale-105 transition duration-300 ease-in-out ${challenge.solved ? 'theme-completed-challenge completed-challenge-line' : ''}"
                             data-id="${challenge.id}"
                             data-name="${challenge.name}"
                             data-description="${challenge.description}"
                             data-points="${challenge.points}"
                             data-completed="${challenge.solved}"
                             data-solves="${challenge.solves}">
                            <h5 class="theme-challenge-title text-xl font-bold mb-2">
                                ${challenge.name}
                            </h5>
                            <p class="theme-challenge-points">${challenge.points} pts</p>
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

    const challengeContent = document.getElementById('challengeContent');
    const solversContent = document.getElementById('solversContent');
    const solversList = document.getElementById('solversList');
    const solverCount = document.getElementById('solverCount');
    const viewSolversBtn = document.getElementById('viewSolversBtn');

    let showingSolvers = false;

    if (viewSolversBtn) {
        viewSolversBtn.addEventListener('click', function() {
            if (!showingSolvers) {
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
                solversContent.classList.add('hidden');
                challengeContent.classList.remove('hidden');
                viewSolversBtn.textContent = 'View Solvers';
                showingSolvers = false;
            }
        });
    }

    closeModalButtons.forEach(button => {
        button.addEventListener('click', function() {
            challengeModal.classList.add('opacity-0', 'pointer-events-none');
            modalContent.classList.add('-translate-y-full');
            showingSolvers = false; // Reset state when closing modal
            challengeContent.classList.remove('hidden'); // Ensure challenge content is visible
            solversContent.classList.add('hidden'); // Hide solvers content
            if (viewSolversBtn) {
                viewSolversBtn.textContent = 'View Solvers'; // Reset button text
            }
        });
    });

    challengeModal.addEventListener('click', function(event) {
        if (event.target === challengeModal) {
            challengeModal.classList.add('opacity-0', 'pointer-events-none');
            modalContent.classList.add('-translate-y-full');
            showingSolvers = false; // Reset state when closing modal
            challengeContent.classList.remove('hidden'); // Ensure challenge content is visible
            solversContent.classList.add('hidden'); // Hide solvers content
            if (viewSolversBtn) {
                viewSolversBtn.textContent = 'View Solvers'; // Reset button text
            }
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