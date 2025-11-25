$(document).ready(function() {
    function initializeDataTable(tableId) {
        var table = $(tableId);
        if (table.length && !$.fn.DataTable.isDataTable(table)) {
            // Only initialize if the table has rows in the body
            if (table.find('tbody tr').length > 0) {
                table.DataTable();
            }
        }
    }

    initializeDataTable('#users-table');
    initializeDataTable('#challenges-table');
    initializeDataTable('#categories-table');
    initializeDataTable('#award-categories-table');
    initializeDataTable('#submissions-table');
});
