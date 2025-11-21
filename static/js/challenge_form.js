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

    // New point reduction fields
    const unlockPointReductionTypeSelect = document.getElementById('unlock_point_reduction_type_select');
    const unlockPointReductionValueField = document.getElementById('unlock_point_reduction_value_field');
    const unlockPointReductionTargetDateField = document.getElementById('unlock_point_reduction_target_date_field');

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
        const selectedReductionType = unlockPointReductionTypeSelect.value;

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

        // Hide all point reduction-related fields initially
        unlockPointReductionValueField.style.display = 'none';
        unlockPointReductionTargetDateField.style.display = 'none';

        // Show fields based on selected point reduction type
        if (selectedReductionType === 'FIXED' || selectedReductionType === 'PERCENTAGE') {
            unlockPointReductionValueField.style.display = 'block';
        } else if (selectedReductionType === 'TIME_DECAY_TO_ZERO') {
            unlockPointReductionTargetDateField.style.display = 'block';
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

    if (unlockPointReductionTypeSelect) {
        unlockPointReductionTypeSelect.addEventListener('change', updateUnlockForm);
        updateUnlockForm(); // Initial call to set correct visibility
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
