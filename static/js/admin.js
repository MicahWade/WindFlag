document.addEventListener('DOMContentLoaded', function() {
    const userRows = document.querySelectorAll('.user-row');
    const dropdown = document.getElementById('user-actions-dropdown');
    const toggleHiddenForm = document.getElementById('toggle-hidden-form');
    const toggleHiddenButton = document.getElementById('toggle-hidden-button');
    const toggleAdminForm = document.getElementById('toggle-admin-form');
    const toggleAdminButton = document.getElementById('toggle-admin-button');
    const toggleBanForm = document.getElementById('toggle-ban-form'); // New
    const toggleBanButton = document.getElementById('toggle-ban-button'); // New
    let currentUserId = null;

    // Pass current user's super admin status from Flask
    // These variables are now defined globally in the HTML template
    // const isCurrentUserSuperAdmin = {{ is_current_user_super_admin | tojson }};
    // const usersSuperAdminStatus = {{ users_super_admin_status | tojson }};
    // const currentLoggedInUserId = {{ current_user.id | tojson }};

    userRows.forEach(row => {
        row.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent document click from immediately closing
            currentUserId = this.dataset.userId;
            const isAdmin = this.dataset.isAdmin === 'true';
            // Get target user's super admin status from the passed map
            const isTargetUserSuperAdmin = usersSuperAdminStatus[currentUserId];
            const isHidden = this.dataset.isHidden === 'true';
            const isBanned = this.dataset.isBanned === 'true'; // New

            // Update hidden toggle button
            toggleHiddenForm.action = `/admin/user/${currentUserId}/toggle_hidden`;
            toggleHiddenButton.textContent = isHidden ? 'Unhide User' : 'Hide User';

            // Update ban toggle button
            toggleBanForm.action = `/admin/user/${currentUserId}/toggle_ban`;
            toggleBanButton.textContent = isBanned ? 'Unban User' : 'Ban User';
            
            if (currentUserId == currentLoggedInUserId) { // Cannot ban/unban self
                toggleBanButton.disabled = true;
                toggleBanButton.classList.add('opacity-50', 'cursor-not-allowed');
            } else if (!isCurrentUserSuperAdmin) { // Only super admins can ban/unban
                toggleBanButton.disabled = true;
                toggleBanButton.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                toggleBanButton.disabled = false;
                toggleBanButton.classList.remove('opacity-50', 'cursor-not-allowed');
            }

            // Update admin toggle button
            toggleAdminForm.action = `/admin/user/${currentUserId}/toggle_admin`;
            toggleAdminButton.textContent = isAdmin ? 'Revoke Admin' : 'Make Admin';

            // Admin status toggle logic
            if (currentUserId == currentLoggedInUserId) { // Cannot change own admin status
                toggleAdminButton.disabled = true;
                toggleAdminButton.classList.add('opacity-50', 'cursor-not-allowed');
            } else if (!isCurrentUserSuperAdmin) { // Only super admins can toggle admin status
                toggleAdminButton.disabled = true;
                toggleAdminButton.classList.add('opacity-50', 'cursor-not-allowed');
            } else if (isTargetUserSuperAdmin && isAdmin) { // Super admin cannot revoke admin status from another super admin via UI
                toggleAdminButton.disabled = true;
                toggleAdminButton.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                toggleAdminButton.disabled = false;
                toggleAdminButton.classList.remove('opacity-50', 'cursor-not-allowed');
            }

            // Position and show dropdown
            const rect = this.getBoundingClientRect();
            dropdown.style.top = `${rect.bottom + window.scrollY}px`;
            dropdown.style.left = `${rect.left + window.scrollX}px`;
            dropdown.classList.remove('hidden');
        });
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (dropdown && !dropdown.contains(event.target) && !event.target.closest('.user-row')) {
            dropdown.classList.add('hidden');
        }
    });

    // New JavaScript for challenge form dynamic flag logic
    const multiFlagTypeSelect = document.getElementById('multi_flag_type_select');
    const flagsAndThresholdSection = document.getElementById('flags_and_threshold_section');
    const dynamicFlagApiKeySection = document.getElementById('dynamic_flag_api_key_section');
    const hasDynamicFlagCheckbox = document.getElementById('has_dynamic_flag_checkbox');
    const challengeId = document.querySelector('input[name="challenge_id"]')?.value; // Get challenge_id if available

    function toggleFlagFields() {
        if (!multiFlagTypeSelect) return; // Exit if elements are not present (e.g., on other admin pages)

        if (multiFlagTypeSelect.value === 'DYNAMIC') {
            if (flagsAndThresholdSection) flagsAndThresholdSection.style.display = 'none';
            if (dynamicFlagApiKeySection) dynamicFlagApiKeySection.style.display = 'block';
            if (hasDynamicFlagCheckbox) hasDynamicFlagCheckbox.checked = true;
        } else {
            if (flagsAndThresholdSection) flagsAndThresholdSection.style.display = 'block';
            if (dynamicFlagApiKeySection) dynamicFlagApiKeySection.style.display = 'none';
            if (hasDynamicFlagCheckbox) hasDynamicFlagCheckbox.checked = false;
        }
    }

    // Initial call to set visibility based on current selection
    toggleFlagFields();

    // Add event listener for changes
    if (multiFlagTypeSelect) {
        multiFlagTypeSelect.addEventListener('change', toggleFlagFields);
    }

    // Also, if the hasDynamicFlagCheckbox is manually changed, update the multi-flag type
    if (hasDynamicFlagCheckbox) {
        hasDynamicFlagCheckbox.addEventListener('change', function() {
            if (this.checked) {
                multiFlagTypeSelect.value = 'DYNAMIC';
            } else {
                // Revert to SINGLE if unchecked, or logic to pick a default non-dynamic type
                if (multiFlagTypeSelect.value === 'DYNAMIC') {
                    multiFlagTypeSelect.value = 'SINGLE'; // Default to SINGLE when unchecking dynamic
                }
            }
            toggleFlagFields();
        });
    }
});
