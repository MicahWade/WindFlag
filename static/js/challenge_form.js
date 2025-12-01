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
    const challengeSubmitButton = document.getElementById('challenge_submit_button');
    const languageSelect = document.getElementById('language');

    // CodeMirror Integration for Admin Challenge Form
    const adminCodeMirrorEditors = {}; // Object to hold CodeMirror instances

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
                    indentWithTabs: false
                });
                adminCodeMirrorEditors[elementId].getWrapperElement().classList.add('codemirror-themed-input');
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
        if (challengeSubmitButton) { // Add null check here
            if (challengeTypeSelect.value === 'CODING') {
                challengeSubmitButton.disabled = !isSolutionVerified;
            } else {
                challengeSubmitButton.disabled = false; // Always enabled for non-coding challenges
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
                isSolutionVerified = false; // Reset verification status for coding challenges

                // Initialize CodeMirror for coding fields if not already done
                initializeAdminCodeMirrorEditor('expected_output_editor');
                initializeAdminCodeMirrorEditor('test_case_input_editor');
                initializeAdminCodeMirrorEditor('setup_code_editor');
                initializeAdminCodeMirrorEditor('starter_code_editor');
                initializeAdminCodeMirrorEditor('reference_solution_editor');
                updateCodeEditorsMode(); // Set initial mode
                
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
});