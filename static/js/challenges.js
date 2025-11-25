document.addEventListener('DOMContentLoaded', function() {
    // The challengeContainer and loading elements are from the remote branch, but they are not present in the current HTML.
    // I will comment them out for now, or ensure the HTML is updated. For now, commenting out.
    // const challengeContainer = document.getElementById('challenge-container');
    // if (!challengeContainer) {
    //     return;
    // }
    // const loading = document.getElementById('loading');

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
    const modalFullscreenCodeButton = document.getElementById('modalFullscreenCodeButton'); // Get fullscreen button

    let currentChallengeId = null;
    let currentChallengeType = null;
    let currentChallengeLanguage = null;
    let codeMirrorEditor = null; // Initialize CodeMirror editor here

    // Function to toggle fullscreen mode for the modal
    function toggleFullscreen() {
        challengeModal.classList.toggle('fullscreen');
        if (challengeModal.classList.contains('fullscreen')) {
            document.documentElement.requestFullscreen();
            modalFullscreenCodeButton.textContent = 'Exit Fullscreen';
        } else {
            document.exitFullscreen();
            modalFullscreenCodeButton.textContent = 'Fullscreen';
        }
        if (codeMirrorEditor) { // Ensure editor exists before refreshing
            codeMirrorEditor.refresh(); // Important: Refresh CodeMirror to adjust to new dimensions
        }
    }

    // Add event listener for the fullscreen button
    if (modalFullscreenCodeButton) {
        modalFullscreenCodeButton.addEventListener('click', toggleFullscreen);
    }

    // Listen for fullscreen change events to update button text if user exits fullscreen manually
    document.addEventListener('fullscreenchange', () => {
        if (!document.fullscreenElement) {
            challengeModal.classList.remove('fullscreen');
            if (modalFullscreenCodeButton) {
                modalFullscreenCodeButton.textContent = 'Fullscreen';
            }
            if (codeMirrorEditor) {
                codeMirrorEditor.refresh();
            }
        }
    });

    // Language-specific blacklists for client-side static code analysis
    // These are patterns or keywords that indicate potentially dangerous operations
    // Less strict than server-side, for immediate user feedback.
    const LANGUAGE_BLACKLISTS_JS = {
        'python': {
            'forbidden_keywords': [
                'import os', 'import subprocess', 'import sys', 'import socket', 'import shutil',
                'eval(', 'exec(', 'open(', 'system(', 'popen(', '__import__('
            ],
            'forbidden_regex': [
                /while\s*True:/, // Python infinite loop
                /subprocess\.(run|call|check_call|check_output)/,
                /os\.(system|popen|fork|kill|rmdir|remove|unlink|mkdir|makedirs)/,
                /sys\.exit/, /sys\.modules/,
                /\bfile\s*\(/ 
            ]
        },
        'javascript': { // Corresponds to 'nodejs' on backend
            'forbidden_keywords': [
                'require(', 'import(', 'child_process', 'fs.', 'net.', 'http.', 'https.',
                'eval(', 'new Function(', 'process.exit('
            ],
            'forbidden_regex': [
                /while\s*\(\s*true\s*\)/, /for\s*\(\s*;\s*;\s*\)/, // JS infinite loops
                /require\s*\[\'getcwd\'\]\)/,
                /import\s+[\'getcwd\']/, 
                /process\.stdout/, /process\.stderr/, // Corrected JS regex patterns
                /fs\.[a-zA-Z]+Sync/, // Synchronous file system operations
                /child_process\.(spawn|exec|fork)/,
                /new\s+Function\s*\(/ // Dynamic code execution
            ]
        },
        'php': {
            'forbidden_keywords': [
                'exec(', 'shell_exec(', 'system(', 'passthru(', 'proc_open(', 'popen(',
                'eval(', 'assert(', 'include(', 'require(', 'file_get_contents(',
                'file_put_contents(', 'unlink(', 'rmdir(', 'mkdir(', 'chmod(', 'chown(',
                'curl_exec(', 'phpinfo(', 'die(', 'exit('
            ],
            'forbidden_regex': [
                /while\s*\(\s*true\s*\)/, /for\s*\(\s*;\s*;\s*\)/, // PHP infinite loops
                /include\s+[\'getcwd\']/, 
                /require\s+[\'getcwd\']/, 
                /\$_GET/, /\$_POST/, /\$_REQUEST/, /\$_FILES/, /\$_SERVER/ // External input access
            ]
        },
        'bash': {
            'forbidden_keywords': [
                'rm ', 'sudo ', 'chown ', 'chmod ', 'ssh ', 'scp ', 'wget ', 'curl ',
                'nc ', 'netcat ', 'nmap ', 'apt-get ', 'yum ', 'kill ', 'pkill ',
                'halt ', 'reboot ', 'shutdown ', 'dd ', 'mkfs ', 'fdisk ', 'parted ',
                'while true', 'for ((;;))' // Bash infinite loops
            ],
            'forbidden_regex': [
                /`.*`/, /\$\(\)/, // Command substitution
                /&&\s*/, /\|\|\s*/, /;\s*/, // Command chaining
                /\bcat\s+\/etc\/(passwd|shadow)\b/, // Specific file access
                /\/\w+\/\w+/ // Absolute paths
            ]
        },
        'dart': {
            'forbidden_keywords': [
                'dart:io', 'dart:cli', 'dart:developer', 'dart:ffi', 'dart:isolate',
                'Process.run(', 'Process.start(', 'File(', 'Directory(', 'Socket(', 'HttpServer(', 'exit('
            ],
            'forbidden_regex': [
                /while\s*\(\s*true\s*\)/, /for\s*\(\s*;\s*;\s*\)/, // Dart infinite loops
                /import\s+['"]dart:io['"]/,
                /import\s+['"]package:.*['"]/,
                /new\s+File\s*\(/ 
            ]
        },
        'haskell': {
            'forbidden_keywords': [
                'System.IO', 'System.Process', 'Network.Socket', 'System.Directory',
                'unsafePerformIO', 'System.cmd', 'System.rawSystem', 'System.process',
                'openFile', 'readFile', 'writeFile', 'exitWith'
            ],
            'forbidden_regex': [
                /import\s+System\./,
                /import\s+Network\./,
                /import\s+Foreign\./,
                /import\s+GHC\./
            ]
        }
    };

    function _staticCodeAnalysisJS(language, code) {
        const blacklist = LANGUAGE_BLACKLISTS_JS[language];
        if (!blacklist) {
            return {is_safe: true, message: "OK"};
        }

        const codeLower = code.toLowerCase(); // For case-insensitive keyword checking

        // Check for forbidden keywords (case-insensitive)
        for (const keyword of blacklist.forbidden_keywords || []) {
            if (codeLower.includes(keyword.toLowerCase())) {
                return {is_safe: false, message: `Detected disallowed keyword: "${keyword}". Please remove it.`};
            }
        }

        // Check for forbidden regex patterns
        for (const regexPattern of blacklist.forbidden_regex || []) {
            if (regexPattern.test(code)) {
                return {is_safe: false, message: `Detected disallowed code pattern: "${regexPattern.source}". Please remove it.`};
            }
        }

        return {is_safe: true, message: "OK"};
    }

    // Function to get a color based on percentage
    function getColorForPercentage(percentage) {
        if (percentage === 100) {
            return 'theme-status-completed'; // Completed
        } else if (percentage >= 75) {
            return 'theme-status-high-progress';
        } else if (percentage >= 50) {
            return 'theme-status-medium-progress';
        } else if (percentage >= 25) {
            return 'theme-status-low-progress';
        } else if (percentage > 0) {
            return 'theme-status-very-low-progress';
        } else {
            return 'theme-status-no-progress'; // Default for 0% or not started
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
        alertDiv.className = `p-3 mb-3 rounded-md text-sm ${category === 'success' ? 'theme-flash-success' : 'theme-flash-danger'}`;
        alertDiv.textContent = message;
        flashContainer.appendChild(alertDiv);

        // Automatically remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
    
    function initChallengeCards() {
        const challengeCards = document.querySelectorAll('.challenge-card');
        challengeCards.forEach(card => {
            const completionPercentage = parseInt(card.dataset.completionPercentage);
            const isCompleted = card.dataset.completed === 'true';
            const isLocked = card.classList.contains('locked-challenge'); // Check if the card is locked
    
            // Get the computed value of --card-border from the body (or any element where it's defined)
            const computedStyle = getComputedStyle(document.body);
            const cardBorder = computedStyle.getPropertyValue('--card-border');
            const cardRadius = computedStyle.getPropertyValue('--radius'); // New: Get --radius
    
            // Apply border and border-radius to the card
            if (cardBorder) {
                card.style.border = cardBorder;
            }
            if (cardRadius) { // New: Apply border-radius
                card.style.borderRadius = cardRadius;
            }
    
            // Apply initial background color based on completion percentage for unlocked challenges
            if (!isCompleted && !isLocked) {
                card.classList.add(getColorForPercentage(completionPercentage));
            }

            card.addEventListener('click', function() {
                if (isLocked) {
                    // If the challenge is locked, do not open the modal.
                    // The unlock information is already displayed on the card itself.
                    return; 
                }

                currentChallengeId = this.dataset.id;
                currentChallengeType = this.dataset.challengeType; // Get challenge type
                
                // Fetch challenge details including hints
                fetch(`/api/challenge_details/${currentChallengeId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success === false) { // Handle server-side errors
                            showFlashMessage(data.message, 'danger');
                            challengeModal.classList.add('opacity-0', 'pointer-events-none');
                            modalContent.classList.add('-translate-y-full');
                            return;
                        }

                        modalChallengeName.textContent = data.name;
                        // Safely parse markdown description using marked, with fallback
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

                        // Reset modal status and progress
                        modalChallengeStatus.classList.add('hidden');
                        modalFlagProgress.classList.add('hidden');
                        modalFlagProgress.textContent = '';
                        codeResult.classList.add('hidden'); // Hide code result on modal open

                        // Conditional display of forms
                        if (currentChallengeType === 'CODING') {
                            flagSubmissionSection.classList.add('hidden');
                            codeSubmissionSection.classList.remove('hidden');
                            currentChallengeLanguage = data.language || 'python'; // Set currentChallengeLanguage
                            if (!codeMirrorEditor) {
                                codeMirrorEditor = CodeMirror.fromTextArea(codeEditor, {
                                    lineNumbers: true,
                                    mode: currentChallengeLanguage, // Set CodeMirror mode
                                    theme: "dracula",
                                    indentUnit: 4, // 4 spaces for indentation
                                    tabSize: 4, // 4 spaces for tab
                                    indentWithTabs: false // Use spaces instead of tabs
                                });
                            } else {
                                codeMirrorEditor.setOption('mode', currentChallengeLanguage); // Set CodeMirror mode
                            }
                            codeMirrorEditor.setValue(data.starter_code || ''); // Load starter code into CodeMirror
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
                            codeMirrorEditor.refresh(); // Important to refresh after setting value and options when editor might have been hidden
                        } else { // FLAG challenge type
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
                            // Clean up CodeMirror if it was initialized for a previous coding challenge
                            if (codeMirrorEditor) {
                                codeMirrorEditor.toTextArea(); // Convert back to textarea to clean up CodeMirror instance
                                codeMirrorEditor = null;
                            }
                        }

                        // Populate hints section (common to all challenge types)
                        if (data.hints && data.hints.length > 0) {
                            hintsList.innerHTML = ''; // Clear previous hints
                            document.getElementById('modalHintsSection').classList.remove('hidden'); // Show the section
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
                            document.getElementById('modalHintsSection').classList.add('hidden'); // Hide the section
                            hintsList.innerHTML = ''; // Ensure it's empty
                        }

                        // Update form action for submission (only for FLAG challenges)
                        if (currentChallengeType === 'FLAG') {
                            modalFlagForm.action = `/submit_flag/${currentChallengeId}`;
                        }
                        
                        // Show modal with animation
                        challengeModal.classList.remove('opacity-0', 'pointer-events-none');
                        modalContent.classList.remove('-translate-y-full');
                        // No explicit refresh/focus here, rely on autofocus option.
                        // If issues persist, might need a small delay after modal fully visible.
                    })
                    .catch(error => {
                        console.error('Error fetching challenge details:', error);
                        showFlashMessage('Error loading challenge details.', 'danger');
                    });
            });
        });
    }

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

            if (!confirm('Are you sure you want to reveal this hint for ' + hintCost + ' points?')) {
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
            showingSolvers = false; // Reset state when closing modal
            challengeContent.classList.remove('hidden'); // Ensure challenge content is visible
            solversContent.classList.add('hidden'); // Hide solvers content
            viewSolversBtn.textContent = 'View Solvers'; // Reset button text

            // CodeMirror Cleanup
            if (codeMirrorEditor) {
                codeMirrorEditor.setValue(''); // Clear content
                codeMirrorEditor.setOption('readOnly', false); // Ensure it's editable for next challenge
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
            viewSolversBtn.textContent = 'View Solvers'; // Reset button text
        }
    });

    const challengeContent = document.getElementById('challengeContent');
    const solversContent = document.getElementById('solversContent');
    const solversList = document.getElementById('solversList');
    const solverCount = document.getElementById('solverCount');
    const viewSolversBtn = document.getElementById('viewSolversBtn');

    let showingSolvers = false; // State to track what is currently shown

    if (viewSolversBtn) {
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
    }

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
                    } else {
                        // Handle multi-flag progress update
                        const submittedCountMatch = data.message.match(/submitted (\d+) of (\d+) flags/);
                        if (submittedCountMatch) {
                            const newSubmittedCount = parseInt(submittedCountMatch[1]);
                            const totalCount = parseInt(submittedCountMatch[2]);
                            currentCard.dataset.submittedFlagsCount = newSubmittedCount;
                            
                            // Re-calculate completion percentage and apply color
                            const newCompletionPercentage = (newSubmittedCount / totalCount * 100);
                            currentCard.dataset.completionPercentage = newCompletionPercentage;
                            
                            // Remove previous percentage class and add new one
                            const oldPercentageClass = Array.from(currentCard.classList).find(cls => cls.startsWith('theme-status-'));
                            if (oldPercentageClass) {
                                currentCard.classList.remove(oldPercentageClass);
                            }
                            currentCard.classList.add(getColorForPercentage(newCompletionPercentage));
    
                            // Update modal progress display
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

    // Handle code submission
    modalRunCodeButton.addEventListener('click', function() {
        if (!codeMirrorEditor) return; // Should not happen if button is visible for coding challenges

        const code = codeMirrorEditor.getValue(); // Get code from CodeMirror instance
        const challengeId = currentChallengeId;

        // Perform client-side static analysis
        const {is_safe, message} = _staticCodeAnalysisJS(currentChallengeLanguage, code);
        if (!is_safe) {
            showFlashMessage(`Client-side security check failed: ${message}`, 'danger');
            codeResult.classList.remove('hidden');
            codeResult.classList.add('theme-code-result-error');
            codeResult.textContent = `Security Error: ${message}`;
            return; // Prevent submission
        }

        codeResult.classList.add('hidden'); // Hide previous result
        codeResult.textContent = '';
        modalRunCodeButton.disabled = true; // Disable button to prevent multiple submissions
        modalRunCodeButton.classList.add('opacity-50', 'cursor-not-allowed');

        fetch(`/api/challenges/${challengeId}/submit_code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code })
        })
        .then(response => response.json())
        .then(data => {
            modalRunCodeButton.disabled = false; // Re-enable button
            modalRunCodeButton.classList.remove('opacity-50', 'cursor-not-allowed');

            codeResult.classList.remove('hidden');
            if (data.correct) {
                showFlashMessage(data.message, 'success');
                codeResult.classList.remove('bg-gray-900', 'text-gray-100', 'text-red-400'); // Remove previous states
                codeResult.classList.add('theme-code-result-success');
                codeResult.textContent = 'Correct! Challenge Solved.';
                
                // Update challenge card status
                const currentCard = document.querySelector(`.challenge-card[data-id="${challengeId}"]`);
                if (currentCard) {
                    currentCard.dataset.completed = 'true';
                    currentCard.classList.remove(getColorForPercentage(parseInt(currentCard.dataset.completionPercentage)));
                    currentCard.classList.add(getColorForPercentage(100));
                    codeMirrorEditor.setOption('readOnly', true);
                    modalRunCodeButton.disabled = true;
                    modalRunCodeButton.classList.add('opacity-50', 'cursor-not-allowed');
                }
                modalChallengeStatus.textContent = data.message;
                modalChallengeStatus.classList.remove('hidden');

            } else {
                showFlashMessage(data.message, 'danger');
                codeResult.classList.remove('bg-gray-900', 'text-gray-100', 'bg-green-800'); // Remove previous states
                codeResult.classList.add('theme-code-result-error');
                let output = '';
                if (data.stdout) output += `STDOUT:\n${data.stdout}\n\n`;
                if (data.stderr) output += `STDERR:\n${data.stderr}\n\n`;
                if (data.error_message) output += `Error: ${data.error_message}`;
                codeResult.textContent = output || 'Execution failed with no output.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showFlashMessage('An error occurred during code submission.', 'danger');
            modalRunCodeButton.disabled = false; // Re-enable button on error
            modalRunCodeButton.classList.remove('opacity-50', 'cursor-not-allowed');
            codeResult.classList.remove('hidden');
            codeResult.classList.add('text-red-400');
            codeResult.textContent = `Network error or unexpected response: ${error}`;
        });
    });

    // Accordion functionality
    function initAccordion() {
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
    }

    // Initialize challenge cards and accordion after DOM is fully loaded
    initChallengeCards();
    initAccordion();
});
