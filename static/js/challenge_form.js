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

    // Custom logic for prerequisite_challenge_ids_input_field (checkboxes)
    const prerequisiteChallengeCheckboxes = document.querySelectorAll('input[name="prerequisite_challenge_ids_checkbox"]');
    const prerequisiteChallengeHiddenInput = document.getElementById('prerequisite_challenge_ids_hidden');

    function updateHiddenPrerequisiteChallenges() {
        const selectedIds = Array.from(prerequisiteChallengeCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => parseInt(checkbox.value));
        prerequisiteChallengeHiddenInput.value = JSON.stringify(selectedIds);
    }

    // Add event listeners to checkboxes
    prerequisiteChallengeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateHiddenPrerequisiteChallenges);
    });

    // Initialize checkboxes based on hidden input's initial value
    if (prerequisiteChallengeHiddenInput && prerequisiteChallengeHiddenInput.value !== undefined) {
        try {
            const initialSelectedIds = JSON.parse(prerequisiteChallengeHiddenInput.value || '[]');
            if (Array.isArray(initialSelectedIds)) {
                prerequisiteChallengeCheckboxes.forEach(checkbox => {
                    if (initialSelectedIds.includes(parseInt(checkbox.value))) {
                        checkbox.checked = true;
                    }
                });
            }
        } catch (e) {
            console.error("Error parsing initial prerequisite challenge IDs:", e);
        }
    }

    // Custom logic for prerequisite_count_category_ids_input_field (checkboxes)
    const prerequisiteCountCategoryCheckboxes = document.querySelectorAll('input[name="prerequisite_count_category_ids_checkbox"]');
    const prerequisiteCountCategoryHiddenInput = document.getElementById('prerequisite_count_category_ids_hidden');

    function updateHiddenPrerequisiteCountCategories() {
        const selectedIds = Array.from(prerequisiteCountCategoryCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => parseInt(checkbox.value));
        prerequisiteCountCategoryHiddenInput.value = JSON.stringify(selectedIds);
    }

    // Add event listeners to checkboxes
    prerequisiteCountCategoryCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateHiddenPrerequisiteCountCategories);
    });

    // Initialize checkboxes based on hidden input's initial value
    if (prerequisiteCountCategoryHiddenInput && prerequisiteCountCategoryHiddenInput.value !== undefined) {
        try {
            const initialSelectedIds = JSON.parse(prerequisiteCountCategoryHiddenInput.value || '[]');
            if (Array.isArray(initialSelectedIds)) {
                prerequisiteCountCategoryCheckboxes.forEach(checkbox => {
                    if (initialSelectedIds.includes(parseInt(checkbox.value))) {
                        checkbox.checked = true;
                    }
                });
            }
        } catch (e) {
            console.error("Error parsing initial prerequisite count category IDs:", e);
        }
    }

    // Timezone field visibility on hover
    const timezoneTooltipIcon = document.getElementById('timezone_tooltip_icon');
    const timezoneField = document.getElementById('timezone_field');

    if (timezoneTooltipIcon && timezoneField) {
        timezoneTooltipIcon.addEventListener('mouseenter', function() {
            timezoneField.style.display = 'block';
        });
        timezoneField.addEventListener('mouseleave', function() {
            timezoneField.style.display = 'none';
        });
    }
});
