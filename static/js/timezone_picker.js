document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('timezone_search_input');
    const dropdownList = document.getElementById('timezone_dropdown_list');
    const hiddenSelect = document.getElementById('timezone_select_hidden');

    // Get all options from the hidden select
    const options = Array.from(hiddenSelect.options).map(option => ({
        value: option.value,
        text: option.textContent
    }));

    // Function to filter and display options
    function filterOptions() {
        const searchTerm = searchInput.value.toLowerCase();
        dropdownList.innerHTML = ''; // Clear previous results

        const filtered = options.filter(option =>
            option.text.toLowerCase().includes(searchTerm)
        );

        if (filtered.length > 0) {
            filtered.forEach(option => {
                const div = document.createElement('div');
                div.classList.add('p-2', 'cursor-pointer', 'theme-dropdown-item');
                div.textContent = option.text;
                div.dataset.value = option.value;
                div.addEventListener('click', function() {
                    searchInput.value = option.text;
                    hiddenSelect.value = option.value;
                    dropdownList.classList.add('hidden');
                });
                dropdownList.appendChild(div);
            });
            dropdownList.classList.remove('hidden');
        } else {
            dropdownList.classList.add('hidden');
        }
    }

    // Event listener for search input
    searchInput.addEventListener('input', filterOptions);

    // Event listener to show dropdown when input is focused
    searchInput.addEventListener('focus', function() {
        filterOptions(); // Show all options or filtered if there's text
    });

    // Event listener to hide dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) && !dropdownList.contains(event.target)) {
            dropdownList.classList.add('hidden');
        }
    });

    // Initialize search input with the currently selected value
    const selectedOption = hiddenSelect.options[hiddenSelect.selectedIndex];
    if (selectedOption) {
        searchInput.value = selectedOption.textContent;
    }
});
