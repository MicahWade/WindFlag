document.addEventListener('DOMContentLoaded', function () {
    const decayTypeSelect = document.getElementById('point_decay_type');
    const minimumPointsField = document.getElementById('minimum_points_field');
    const decayRateField = document.getElementById('point_decay_rate_field');
    const proactiveDecayField = document.getElementById('proactive_decay_field');
    const decayRateLabel = document.querySelector('label[for="point_decay_rate"]');
    const formulaDisplay = document.getElementById('formula_display');

    // New unlock fields
    const unlockTypeSelect = document.getElementById('unlock_type_select');
    const prerequisitePercentageValueField = document.getElementById('prerequisite_percentage_value_field');
    const prerequisiteCountValueField = document.getElementById('prerequisite_count_value_field');
    const prerequisiteCountCategoryIdsInputField = document.getElementById('prerequisite_count_category_ids_input_field'); // New field
    const prerequisiteChallengeIdsInputField = document.getElementById('prerequisite_challenge_ids_input_field');
    const unlockDateTime = document.getElementById('unlock_date_time_field');

    const formulas = {
        'STATIC': 'Challenge Value is awarded as-is',
        'LINEAR': 'Initial - (Decay * SolveCount)',
        'LOGARITHMIC': '(((Minimum - Initial) / (Decay^2)) * (SolveCount^2)) + Initial'
    };

    function updateDecayForm() {
        const selectedType = decayTypeSelect.value;

        if (selectedType === 'STATIC') {
            minimumPointsField.style.display = 'none';
            decayRateField.style.display = 'none';
            proactiveDecayField.style.display = 'none';
        } else {
            minimumPointsField.style.display = 'block';
            decayRateField.style.display = 'block';
            proactiveDecayField.style.display = 'block';
        }

        if (selectedType === 'LINEAR') {
            decayRateLabel.textContent = 'Decay';
        } else if (selectedType === 'LOGARITHMIC') {
            decayRateLabel.textContent = 'Decay';
        } else {
            decayRateLabel.textContent = 'Point Decay Rate';
        }

        formulaDisplay.textContent = formulas[selectedType] || '';
    }

    function updateUnlockForm() {
        const selectedUnlockType = unlockTypeSelect.value;

        // Hide all unlock-related fields initially
        prerequisitePercentageValueField.style.display = 'none';
        prerequisiteCountValueField.style.display = 'none';
        prerequisiteCountCategoryIdsInputField.style.display = 'none'; // New: Hide by default
        // prerequisiteChallengeIdsInputField.style.display = 'none'; // Removed: This field is now always visible
        unlockDateTime.style.display = 'none';

        // Show fields based on selected unlock type
        if (selectedUnlockType === 'PREREQUISITE_PERCENTAGE') {
            prerequisitePercentageValueField.style.display = 'block';
        } else if (selectedUnlockType === 'PREREQUISITE_COUNT') {
            prerequisiteCountValueField.style.display = 'block';
            prerequisiteCountCategoryIdsInputField.style.display = 'block'; // New: Show for PREREQUISITE_COUNT
        } else if (selectedUnlockType === 'TIMED') {
            unlockDateTime.style.display = 'block';
        } else if (selectedUnlockType === 'COMBINED') {
            prerequisitePercentageValueField.style.display = 'block'; // Assuming combined can use percentage
            prerequisiteCountValueField.style.display = 'block'; // Assuming combined can use count
            prerequisiteCountCategoryIdsInputField.style.display = 'block'; // New: Show for COMBINED
            // prerequisiteChallengeIdsInputField.style.display = 'block'; // Removed: This field is now always visible
            unlockDateTime.style.display = 'block';
        }
    }

    function updateFlagFields() {
        const multiFlagType = document.getElementById('multi_flag_type_select').value;
        const thresholdField = document.getElementById('multi_flag_threshold_field');
        const flagsInputSection = document.getElementById('flags_input_fields_section');
        const dynamicFlagApiKeySection = document.getElementById('dynamic_flag_api_key_section');

        // Hide all related fields initially
        thresholdField.style.display = 'none';
        flagsInputSection.style.display = 'block'; // Default to showing the main flags input
        dynamicFlagApiKeySection.style.display = 'none';

        if (multiFlagType === 'N_OF_M') {
            thresholdField.style.display = 'block';
        } else if (multiFlagType === 'DYNAMIC') {
            // For DYNAMIC, hide the standard flag inputs and show the API key section
            flagsInputSection.style.display = 'none';
            dynamicFlagApiKeySection.style.display = 'block';
        } else if (multiFlagType === 'HTTP') {
            flagsInputSection.style.display = 'none';
            thresholdField.style.display = 'none';
            dynamicFlagApiKeySection.style.display = 'none';
        }
        // For other types like 'STANDARD' or 'LIST', no special fields are needed, so the default state is correct.
    }
    
    function updateCategoryFields() {
        const categorySelect = document.getElementById('category_select');
        const newCategoryNameField = document.getElementById('new_category_name_field');

        if (categorySelect.value === '0') {
            newCategoryNameField.style.display = 'block';
        } else {
            newCategoryNameField.style.display = 'none';
        }
    }

    if (decayTypeSelect) {
        decayTypeSelect.addEventListener('change', updateDecayForm);
        updateDecayForm();
    }

    if (unlockTypeSelect) {
        unlockTypeSelect.addEventListener('change', updateUnlockForm);
        updateUnlockForm(); // Initial call to set correct visibility
    }

    const multiFlagTypeSelect = document.getElementById('multi_flag_type_select');
    if (multiFlagTypeSelect) {
        multiFlagTypeSelect.addEventListener('change', updateFlagFields);
        updateFlagFields(); // Initial call to set correct visibility
    }

    const categorySelect = document.getElementById('category_select');
    if (categorySelect) {
        categorySelect.addEventListener('change', updateCategoryFields);
        updateCategoryFields(); // Initial call
    }

    let isSolutionVerified = false; // Flag to track if the coding solution has been verified
    const solutionVerifiedField = document.getElementById('solution_verified');
    // Initialize verification status from hidden field (server-side memory)
    if (solutionVerifiedField && solutionVerifiedField.value === 'true') {
        isSolutionVerified = true;
    }

    const challengeSubmitButton = document.getElementById('challenge_submit_button');
    const languageSelect = document.getElementById('language');

    // CodeMirror Integration for Admin Challenge Form
    const adminCodeMirrorEditors = {}; // Object to hold CodeMirror instances

    function resetVerification() {
        isSolutionVerified = false;
        if (solutionVerifiedField) {
            solutionVerifiedField.value = 'false';
        }
        updateSubmitButtonState();
    }

    function getCodeMirrorMode(language) {
        const lowerCaseLang = language.toLowerCase();
        if (lowerCaseLang.includes('python')) return 'python';
        if (lowerCaseLang.includes('javascript') || lowerCaseLang.includes('node')) return 'javascript';
        if (lowerCaseLang.includes('php')) return 'php';
        if (lowerCaseLang.includes('shell') || lowerCaseLang.includes('bash')) return 'shell';
        if (lowerCaseLang.includes('haskell')) return 'haskell';
        if (lowerCaseLang.includes('dart')) return 'dart';
        // Add more language mappings as needed
        return null; // Default to no specific mode
    }

    function initializeAdminCodeMirrorEditor(elementId) {
        const textarea = document.getElementById(elementId);
        if (textarea && typeof CodeMirror !== 'undefined') {
            if (!adminCodeMirrorEditors[elementId]) {
                const mode = getCodeMirrorMode(languageSelect ? languageSelect.value : '');
                adminCodeMirrorEditors[elementId] = CodeMirror.fromTextArea(textarea, {
                    lineNumbers: true,
                    mode: mode,
                    theme: "dracula",
                    indentUnit: 4,
                    tabSize: 4,
                    indentWithTabs: false,
                    viewportMargin: Infinity,
                    fullScreen: false // Ensure CodeMirror is NOT fullscreen by default
                });
                adminCodeMirrorEditors[elementId].getWrapperElement().classList.add('codemirror-themed-input');
                
                // Dynamically create and append fullscreen button
                const fullscreenButton = document.createElement('button');
                fullscreenButton.innerHTML = `
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
                    </svg>
                `;
                fullscreenButton.title = "Enter Fullscreen (F11)";
                // Use a class for styling consistent with CodeMirror's own fullscreen button
                fullscreenButton.className = "CodeMirror-fullscreen-button-custom absolute top-2 right-2 p-1 rounded-full bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white z-10";
                
                fullscreenButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    adminCodeMirrorEditors[elementId].setOption("fullScreen", !adminCodeMirrorEditors[elementId].getOption("fullScreen"));
                });
                adminCodeMirrorEditors[elementId].getWrapperElement().appendChild(fullscreenButton);

                // Add change listener to reset verification
                adminCodeMirrorEditors[elementId].on('change', resetVerification);

                // Add an event listener to update the button icon when fullscreen state changes
                adminCodeMirrorEditors[elementId].on('optionChange', (cm, option) => {
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
                // If editor already exists, ensure theme and class are applied
                adminCodeMirrorEditors[elementId].getWrapperElement().classList.add('codemirror-themed-input');
            }
        }
    }

    function updateCodeEditorsMode() {
        const selectedLanguage = languageSelect ? languageSelect.value : '';
        const mode = getCodeMirrorMode(selectedLanguage);

        for (const editorId in adminCodeMirrorEditors) {
            if (adminCodeMirrorEditors.hasOwnProperty(editorId)) {
                adminCodeMirrorEditors[editorId].setOption('mode', mode);
                adminCodeMirrorEditors[editorId].refresh();
            }
        }
    }

    function updateSubmitButtonState() {
        const challengeTypeSelect = document.getElementById('challenge_type_select');
        const submitStatusMessageDiv = document.getElementById('submit_status_message');

        if (challengeSubmitButton) { // Add null check here
            if (challengeTypeSelect.value === 'CODING') {
                challengeSubmitButton.disabled = !isSolutionVerified;
                if (submitStatusMessageDiv) {
                    if (!isSolutionVerified) {
                        submitStatusMessageDiv.textContent = 'Please verify the reference solution before submitting.';
                        submitStatusMessageDiv.classList.add('text-red-500');
                    } else {
                        submitStatusMessageDiv.textContent = '';
                        submitStatusMessageDiv.classList.remove('text-red-500');
                    }
                }
            } else {
                challengeSubmitButton.disabled = false; // Always enabled for non-coding challenges
                if (submitStatusMessageDiv) {
                    submitStatusMessageDiv.textContent = '';
                    submitStatusMessageDiv.classList.remove('text-red-500');
                }
            }
        }
    }

    function updateChallengeTypeFields() {
        const challengeTypeSelect = document.getElementById('challenge_type_select');
        const flagFields = document.getElementById('flag_challenge_fields');
        const codingFields = document.getElementById('coding_challenge_fields');

        if (challengeTypeSelect) {
             if (challengeTypeSelect.value === 'CODING') {
                if (flagFields) flagFields.style.display = 'none';
                if (codingFields) codingFields.style.display = 'block';
                
                // Only reset verification if not already verified (e.g., from hidden field on load)
                if (!solutionVerifiedField || solutionVerifiedField.value !== 'true') {
                    isSolutionVerified = false; 
                } else {
                    isSolutionVerified = true;
                }

                // Initialize CodeMirror for coding fields if not already done
                initializeAdminCodeMirrorEditor('expected_output_editor');
                initializeAdminCodeMirrorEditor('test_case_input_editor');
                initializeAdminCodeMirrorEditor('setup_code_editor');
                initializeAdminCodeMirrorEditor('starter_code_editor');
                initializeAdminCodeMirrorEditor('reference_solution_editor');
                updateCodeEditorsMode(); // Set initial mode
                setupFullscreenButtons(); // Call to setup buttons after editors are initialized
                
            } else {
                if (flagFields) flagFields.style.display = 'block';
                if (codingFields) codingFields.style.display = 'none';
                isSolutionVerified = true; // Not a coding challenge, so no verification needed

                // Destroy CodeMirror instances for coding fields
                for (const editorId in adminCodeMirrorEditors) {
                    if (adminCodeMirrorEditors.hasOwnProperty(editorId)) {
                        adminCodeMirrorEditors[editorId].toTextArea();
                        delete adminCodeMirrorEditors[editorId];
                    }
                }
            }
        }
        updateSubmitButtonState(); // Update button state after changing challenge type
    }

    const challengeTypeSelect = document.getElementById('challenge_type_select');
    if (challengeTypeSelect) {
        challengeTypeSelect.addEventListener('change', updateChallengeTypeFields);
        updateChallengeTypeFields(); // Initial call
    }

    // Event listener for language select to update CodeMirror modes
    if (languageSelect) {
        languageSelect.addEventListener('change', updateCodeEditorsMode);
    }

    // Verify Solution Button Logic
    const verifySolutionButton = document.getElementById('verify_solution_button');
    if (verifySolutionButton) {
        verifySolutionButton.addEventListener('click', function () {
            const language = languageSelect.value;
            const setupCode = adminCodeMirrorEditors['setup_code_editor'] ? adminCodeMirrorEditors['setup_code_editor'].getValue() : '';
            const testCaseInput = adminCodeMirrorEditors['test_case_input_editor'] ? adminCodeMirrorEditors['test_case_input_editor'].getValue() : '';
            const referenceSolution = adminCodeMirrorEditors['reference_solution_editor'] ? adminCodeMirrorEditors['reference_solution_editor'].getValue() : '';
            const expectedOutput = adminCodeMirrorEditors['expected_output_editor'] ? adminCodeMirrorEditors['expected_output_editor'].getValue() : '';
            const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
            const statusDiv = document.getElementById('verify_solution_status');

            // Client-side validation for empty fields
            if (!language || !referenceSolution || !expectedOutput) {
                if (statusDiv) {
                    statusDiv.textContent = 'Error: Language, Reference Solution, and Expected Output cannot be empty.';
                    statusDiv.classList.add('text-red-500');
                }
                isSolutionVerified = false;
                updateSubmitButtonState();
                // Re-enable button immediately as no fetch was made
                verifySolutionButton.disabled = false;
                verifySolutionButton.textContent = originalButtonText;
                verifySolutionButton.classList.remove('opacity-50', 'cursor-not-allowed');
                return; // Stop execution
            }

            // Disable button and show loading state
            const originalButtonText = verifySolutionButton.textContent;
            verifySolutionButton.disabled = true;
            verifySolutionButton.textContent = 'Verifying...';
            verifySolutionButton.classList.add('opacity-50', 'cursor-not-allowed');
            
            // Reset status
            if (statusDiv) {
                statusDiv.textContent = '';
                statusDiv.className = 'ml-4 text-sm font-bold'; // Reset classes
            }

            fetch('/api/admin/verify_coding_challenge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    language: language,
                    setup_code: setupCode,
                    test_case_input: testCaseInput,
                    reference_solution: referenceSolution,
                    expected_output: expectedOutput
                })
            })
            .then(async response => {
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `HTTP Error: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.is_correct) {
                    isSolutionVerified = true;
                    if (solutionVerifiedField) {
                        solutionVerifiedField.value = 'true';
                    }
                    updateSubmitButtonState();
                    if (statusDiv) {
                        statusDiv.textContent = 'Success: Reference solution verified!';
                        statusDiv.classList.add('text-green-500');
                    }
                } else {
                    isSolutionVerified = false;
                    updateSubmitButtonState();
                    let errorMessage = 'Verification Failed: ';
                    if (data.message) errorMessage += data.message;
                    
                    // Log details to console
                    if (data.stderr) console.error('Verification Stderr:', data.stderr);
                    if (data.stdout) console.log('Verification Stdout:', data.stdout);

                    if (statusDiv) {
                        statusDiv.textContent = errorMessage + (data.stderr ? ' (Check console for details)' : '');
                        statusDiv.classList.add('text-red-500');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (statusDiv) {
                    statusDiv.textContent = 'An error occurred: ' + error.message;
                    statusDiv.classList.add('text-red-500');
                }
                isSolutionVerified = false;
                updateSubmitButtonState();
            })
            .finally(() => {
                // Restore button state
                verifySolutionButton.disabled = false;
                verifySolutionButton.textContent = originalButtonText;
                verifySolutionButton.classList.remove('opacity-50', 'cursor-not-allowed');
            });
        });
    }

    // Dynamic Hint Fields Logic
    const hintsContainer = document.getElementById('hints-container');
    const addHintButton = document.getElementById('add-hint-button');

    // Get the initial count of hints
    let hintCount = hintsContainer ? hintsContainer.children.length : 0;

    function addHintField(title = '', content = '', cost = 0, hintId = '') {
        const newHintEntry = document.createElement('div');
        newHintEntry.classList.add('hint-entry', 'border', 'p-4', 'rounded', 'mb-4');
        newHintEntry.innerHTML = `
            <input type="hidden" name="hints-${hintCount}-id" value="${hintId}">
            <div class="mb-4">
                <label for="hints-${hintCount}-title" class="block text-gray-300 text-sm font-bold mb-2">Hint Title</label>
                <input type="text" id="hints-${hintCount}-title" name="hints-${hintCount}-title" class="shadow appearance-none border border-gray-600 rounded w-full py-2 px-3 bg-gray-700 text-gray-200 leading-tight focus:outline-none focus:shadow-outline" value="${title}" required>
            </div>
            <div class="mb-4">
                <label for="hints-${hintCount}-content" class="block text-gray-300 text-sm font-bold mb-2">Hint Content</label>
                <textarea id="hints-${hintCount}-content" name="hints-${hintCount}-content" class="shadow appearance-none border border-gray-600 rounded w-full py-2 px-3 bg-gray-700 text-gray-200 leading-tight focus:outline-none focus:shadow-outline" required>${content}</textarea>
            </div>
            <div class="mb-4">
                <label for="hints-${hintCount}-cost" class="block text-gray-300 text-sm font-bold mb-2">Hint Cost</label>
                <input type="number" id="hints-${hintCount}-cost" name="hints-${hintCount}-cost" class="shadow appearance-none border border-gray-600 rounded w-full py-2 px-3 bg-gray-700 text-gray-200 leading-tight focus:outline-none focus:shadow-outline" value="${cost}" required min="0">
            </div>
            <button type="button" class="remove-hint-button bg-red-600 hover:bg-red-500 text-white font-bold py-1 px-2 rounded focus:outline-none focus:shadow-outline">Remove Hint</button>
        `;
        hintsContainer.appendChild(newHintEntry);
        hintCount++;
    }

    function removeHintField(event) {
        event.target.closest('.hint-entry').remove();
        // Reindex remaining hints
        reindexHints();
    }

    function reindexHints() {
        const hintEntries = hintsContainer.querySelectorAll('.hint-entry');
        hintCount = 0;
        hintEntries.forEach((entry) => {
            entry.querySelectorAll('[name^="hints-"]').forEach((input) => {
                const oldName = input.getAttribute('name');
                const newName = oldName.replace(/hints-\d+-/, `hints-${hintCount}-`);
                input.setAttribute('name', newName);
                input.setAttribute('id', newName); // Also update ID for labels
            });
            hintCount++;
        });
    }

    if (addHintButton) {
        addHintButton.addEventListener('click', () => addHintField());
    }

    // Add event listeners to existing remove buttons
    if (hintsContainer) {
        hintsContainer.addEventListener('click', (event) => {
            if (event.target.classList.contains('remove-hint-button')) {
                removeHintField(event);
            }
        });
    }

    // Scroll preservation logic
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
    }

    const savedScrollPosition = sessionStorage.getItem('scrollPosition');
    if (savedScrollPosition) {
        window.scrollTo(0, parseInt(savedScrollPosition));
        sessionStorage.removeItem('scrollPosition');
    }
});