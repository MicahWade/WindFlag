document.addEventListener('DOMContentLoaded', function () {
    const decayTypeSelect = document.getElementById('point_decay_type');
    const minimumPointsField = document.getElementById('minimum_points_field');
    const decayRateField = document.getElementById('point_decay_rate_field');
    const proactiveDecayField = document.getElementById('proactive_decay_field');
    const decayRateLabel = document.querySelector('label[for="point_decay_rate"]');
    const formulaDisplay = document.getElementById('formula_display');

    const formulas = {
        'STATIC': 'Challenge Value is awarded as-is',
        'LINEAR': 'Initial - (Decay * SolveCount)',
        'LOGARITHMIC': '(((Minimum - Initial) / (Decay^2)) * (SolveCount^2)) + Initial'
    };

    function updateForm() {
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

    if (decayTypeSelect) {
        decayTypeSelect.addEventListener('change', updateForm);
        updateForm();
    }
});
