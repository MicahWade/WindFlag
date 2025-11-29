$(document).ready(function() {
    function initializeDataTable(tableId, options = {}) {
        var table = $(tableId);
        if (table.length && !$.fn.DataTable.isDataTable(table)) {
            // Always initialize DataTables, it will handle empty tables gracefully.
            table.DataTable(options);
        }
    }

    initializeDataTable('#users-table');
    initializeDataTable('#challenges-table', {
        "columns": [
            { "orderable": true }, // ID
            { "orderable": true }, // Name
            { "orderable": true }, // Category
            { "orderable": true }, // Points
            { "orderable": true }, // Unlock
            { "orderable": false }  // Actions (typically not sortable)
        ],
        "language": {
            "emptyTable": "No challenges found. <a href='/admin/challenge/new' class='text-blue-500 hover:underline'>Create one?</a>"
        }
    });
    initializeDataTable('#categories-table');
    initializeDataTable('#award-categories-table');
    initializeDataTable('#submissions-table');
});
