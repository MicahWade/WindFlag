document.addEventListener('DOMContentLoaded', function() {
    const userRows = document.querySelectorAll('.user-row');
    const dropdown = document.getElementById('user-actions-dropdown');
    const toggleHiddenForm = document.getElementById('toggle-hidden-form');
    const toggleHiddenButton = document.getElementById('toggle-hidden-button');
    const toggleAdminForm = document.getElementById('toggle-admin-form');
    const toggleAdminButton = document.getElementById('toggle-admin-button');
    let currentUserId = null;

    // Pass current user's super admin status from Flask
    const isCurrentUserSuperAdmin = {{ is_current_user_super_admin | tojson }};
    const usersSuperAdminStatus = {{ users_super_admin_status | tojson }}; // New: Map of user_id to is_super_admin

    userRows.forEach(row => {
        row.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent document click from immediately closing
            currentUserId = this.dataset.userId;
            const isAdmin = this.dataset.isAdmin === 'true';
            // Get target user's super admin status from the passed map
            const isTargetUserSuperAdmin = usersSuperAdminStatus[currentUserId];
            const isHidden = this.dataset.isHidden === 'true';

            // Update hidden toggle button
            toggleHiddenForm.action = `/admin/user/${currentUserId}/toggle_hidden`;
            toggleHiddenButton.textContent = isHidden ? 'Unhide User' : 'Hide User';

            // Update admin toggle button
            toggleAdminForm.action = `/admin/user/${currentUserId}/toggle_admin`;
            toggleAdminButton.textContent = isAdmin ? 'Revoke Admin' : 'Make Admin';

            // Admin status toggle logic
            if (currentUserId == {{ current_user.id | tojson }}) { // Cannot change own admin status
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
        if (!dropdown.contains(event.target) && !event.target.closest('.user-row')) {
            dropdown.classList.add('hidden');
        }
    });
});
