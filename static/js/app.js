$(document).ready(function() {
    let logsTable;
    let practiceIdsLoaded = false;

    // Initialize the application
    initializeApp();

    function initializeApp() {
        setDefaultDates();
        loadPracticeIds();
        initializeDataTable();
        bindEventHandlers();
        initializeSidebar();
        displayUserInfo();
    }

    function setDefaultDates() {
        const today = new Date();
        const sixMonthsAgo = new Date();
        sixMonthsAgo.setMonth(today.getMonth() - 6);

        // Format dates as YYYY-MM-DD for input[type="date"]
        const formatDate = (date) => {
            return date.toISOString().split('T')[0];
        };

        // Set default values
        $('#dateFrom').val(formatDate(sixMonthsAgo));
        $('#dateTo').val(formatDate(today));

        console.log('Default dates set:', formatDate(sixMonthsAgo), 'to', formatDate(today));
    }
    
    function loadPracticeIds() {
        // Prevent loading practice IDs multiple times
        if (practiceIdsLoaded) {
            return;
        }

        $.ajax({
            url: '/api/practice-ids',
            method: 'GET',
            success: function(data) {
                const practiceSelect = $('#practiceId');

                // Completely destroy and recreate the select element
                if (practiceSelect.hasClass('selectpicker')) {
                    practiceSelect.selectpicker('destroy');
                }

                // Remove all existing options and Bootstrap Select elements
                practiceSelect.empty();
                practiceSelect.removeClass('selectpicker');

                // Add the default option
                practiceSelect.append('<option value="">All Practices</option>');

                // Sort practice IDs numerically and add unique ones only
                data.sort((a, b) => parseInt(a.id) - parseInt(b.id));

                const uniqueIds = [...new Set(data.map(p => p.id))];
                uniqueIds.forEach(function(practiceId) {
                    practiceSelect.append(`<option value="${practiceId}">Practice ${practiceId}</option>`);
                });

                // Add selectpicker class and initialize
                practiceSelect.addClass('selectpicker');
                practiceSelect.selectpicker({
                    liveSearch: true,
                    liveSearchPlaceholder: 'Search practices...',
                    noneSelectedText: 'All Practices',
                    noneResultsText: 'No practices found',
                    size: 10,
                    style: 'btn-outline-secondary',
                    styleBase: 'form-select'
                });

                // Mark as loaded to prevent duplicate loading
                practiceIdsLoaded = true;

                console.log('Practice IDs loaded:', uniqueIds.length, 'unique practices');
            },
            error: function(xhr, status, error) {
                showError('Failed to load practice IDs: ' + error);
                console.error('Error loading practice IDs:', error);
            }
        });
    }
    
    function initializeDataTable() {
        logsTable = $('#logsTable').DataTable({
            processing: true,
            serverSide: true, // Enable server-side pagination
            responsive: true,
            scrollX: false,
            autoWidth: false,
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
            order: [[4, 'desc']],
            ajax: function(data, callback) {
                // Map DataTables params to our API
                const page = Math.floor(data.start / data.length) + 1;
                const perPage = data.length;

                const formData = new FormData($('#filterForm')[0]);
                const params = new URLSearchParams(formData);
                params.set('page', page);
                params.set('per_page', perPage);

                showLoading(true);
                hideError();

                $.ajax({
                    url: '/api/logs?' + params.toString(),
                    method: 'GET',
                    success: function(response) {
                        // Transform to DataTables expected format
                        const rows = (response.data || []).map(function(log) {
                            return [
                                log.id || '',                // ID
                                log.practiceid || '',        // Practice ID
                                log.ErrorMassage || '',      // Error Message
                                log.url || '',               // URL
                                log.ErrorTime || '',         // Error Time
                                log.stacktraces || '',       // Stack Trace
                                log.LLMSolution || '',       // LLMSolution
                                log.JiraStatus || '',        // Jira Status
                                log.insertdat || '',         // Inserted At
                                `<button class=\"btn btn-sm btn-primary me-1 btn-edit\" data-id=\"${log.id}\">\n                                    <i class=\"fas fa-edit\"></i> Edit\n                                </button>\n                                <button class=\"btn btn-sm btn-danger btn-delete\" data-id=\"${log.id}\">\n                                    <i class=\"fas fa-trash\"></i> Delete\n                                </button>`
                            ];
                        });

                        updateRecordCount(response.total || rows.length);
                        showLoading(false);

                        callback({
                            draw: data.draw,
                            recordsTotal: response.total || rows.length,
                            recordsFiltered: response.total || rows.length,
                            data: rows
                        });
                    },
                    error: function(xhr, status, error) {
                        showLoading(false);
                        let errorMessage = 'Failed to load data';
                        if (xhr.responseJSON && xhr.responseJSON.error) {
                            errorMessage += ': ' + xhr.responseJSON.error;
                        }
                        showError(errorMessage);
                        callback({ draw: data.draw, recordsTotal: 0, recordsFiltered: 0, data: [] });
                    }
                });
            },
            columnDefs: [
                {
                    targets: [0], // ID column - now visible
                    visible: false
                },
                {
                    targets: [1], // insertdat column - format as date only (no time)
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return data;
                        }
                        return data || '';
                    }
                },
                {
                    targets: [5], // Stack trace column
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return `<div class="stacktrace-multiline" title="Click to view full stack trace"
                                    style="cursor: pointer;"
                                    onclick="showStackTrace('${escapeHtml(data)}')">${escapeHtml(data)}</div>`;
                        }
                        return data || '';
                    }
                },
                {
                    targets: [6], // LLMSolution column (multiline similar to error message)
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return `<div class="error-message-multiline">${escapeHtml(data)}</div>`;
                        }
                        return data || '';
                    }
                },
                {
                    targets: [2], // Error Message column
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return `<div class="error-message-multiline">${escapeHtml(data)}</div>`;
                        }
                        return data || '';
                    }
                },
                {
                    targets: [3], // URL column
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            const truncated = data.length > 50 ? data.substring(0, 50) + '...' : data;
                            return `<span class="url-cell" title="${escapeHtml(data)}">${escapeHtml(truncated)}</span>`;
                        }
                        return data || '';
                    }
                },
                {
                    targets: [4], // ErrorTime column - show as string
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            // Just return the time string as-is
                            return escapeHtml(data);
                        }
                        return data || '';
                    }
                },
                {
                    targets: [8], // insertdat column - format as date only (no time)
                    render: function(data, type, row) {
                        if (type === 'display' && data) {
                            return formatDateOnly(data);
                        }
                        return data || '';
                    }
                },
                {
                    targets: [7], // Jira Status column - show button based on status
                    render: function(data, type, row) {
                        if (type === 'display') {
                            const status = data || 'false';
                            if (status == 'false') {
                                return `<button class="btn btn-sm btn-success" onclick="openJira(${row[0]})">
                                    <i class="fas fa-external-link-alt"></i> Open Jira
                                </button>`;
                            } else if (status == 'true') {
                                return `<button class="btn btn-sm btn-secondary" disabled>
                                    <i class="fas fa-check"></i> Jira Created
                                </button>`;
                            } else {
                                return escapeHtml(status);
                            }
                        }
                        return data || '';
                    }
                },
                {
                    targets: [9], // Actions column - disable sorting
                    orderable: false,
                    searchable: false
                }
            ],
            language: {
                emptyTable: "No console error logs found",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)",
                lengthMenu: "Show _MENU_ entries",
                loadingRecords: "Loading...",
                processing: "Processing...",
                search: "Search:",
                zeroRecords: "No matching records found"
            }
        });

        // Summary table (Common Logs)
        window.summaryTable = $('#summaryTable').DataTable({
            processing: true,
            serverSide: true,
            responsive: true,
            scrollX: false,
            autoWidth: false,
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
            order: [[4, 'desc']],
            ajax: function(data, callback) {
                const page = Math.floor(data.start / data.length) + 1;
                const perPage = data.length;

                const formData = new FormData($('#filterForm')[0]);
                const params = new URLSearchParams(formData);
                params.delete('time_from');
                params.delete('time_to');
                params.set('page', page);
                params.set('per_page', perPage);

                showLoading(true);
                hideError();

                $.ajax({
                    url: '/api/logs-summary?' + params.toString(),
                    method: 'GET',
                    success: function(response) {
                        const rows = (response.data || []).map(function(log) {
                            return [
                                log.practiceids || '',
                                log.stacktraces || '',
                                log.ErrorMassage || '',
                                log.LLMSolution || '',
                                log.ErrorCount || 0
                            ];
                        });

                        updateRecordCount(response.total || rows.length);
                        showLoading(false);

                        callback({
                            draw: data.draw,
                            recordsTotal: response.total || rows.length,
                            recordsFiltered: response.total || rows.length,
                            data: rows
                        });
                    },
                    error: function(xhr) {
                        showLoading(false);
                        let errorMessage = 'Failed to load summary data';
                        if (xhr.responseJSON && xhr.responseJSON.error) {
                            errorMessage += ': ' + xhr.responseJSON.error;
                        }
                        showError(errorMessage);
                        callback({ draw: data.draw, recordsTotal: 0, recordsFiltered: 0, data: [] });
                    }
                });
            },
            columnDefs: [
                {
                    targets: [1],
                    render: function(data, type) {
                        if (type === 'display' && data) {
                            return `<div class="stacktrace-multiline" title="Click to view full stack trace"
                                    style="cursor: pointer;"
                                    onclick="showStackTrace('${escapeHtml(data)}')">${escapeHtml(data)}</div>`;
                        }
                        return data || '';
                    }
                },
                {
                    targets: [3],
                    render: function(data, type) {
                        if (type === 'display' && data) {
                            return `<div class="error-message-multiline">${escapeHtml(data)}</div>`;
                        }
                        return data || '';
                    }
                }
            ],
            language: {
                emptyTable: 'No common logs found'
            }
        });
    }
    
    function bindEventHandlers() {
        // Filter form submission
        $('#filterForm').on('submit', function(e) {
            e.preventDefault();
            logsTable.ajax.reload();
        });
        
        // Clear filters button
        $('#clearFilters').on('click', function() {
            $('#filterForm')[0].reset();
            // Reset to default dates instead of clearing
            setDefaultDates();
            // Reset the searchable dropdown
            resetPracticeIdDropdown();
            logsTable.ajax.reload();
        });
        
        // Real-time search
        $('#searchText').on('keyup', function() {
            clearTimeout(window.searchTimeout);
            window.searchTimeout = setTimeout(function() {
                const selected = $('#logType').val();
                if (selected === 'common') {
                    summaryTable.ajax.reload();
                } else {
                    logsTable.ajax.reload();
                }
            }, 500);
        });

        // Delegate edit/delete button clicks since rows are dynamic
        $('#logsTable tbody').on('click', '.btn-edit', function() {
            const recordId = $(this).data('id');
            window.editRecord(recordId);
        });

        $('#logsTable tbody').on('click', '.btn-delete', function() {
            const recordId = $(this).data('id');
            window.deleteRecord(recordId);
        });
        // Toggle between Console and Common logs
        $('#logType').on('change', function() {
            const selected = $(this).val();
            switchView(selected);
        });
    }

    function initializeSidebar() {
        // Sidebar toggle buttons
        $('#sidebarToggleBtn').on('click', function() {
            toggleSidebar();
        });

        $('#sidebarToggle').on('click', function() {
            toggleSidebar();
        });

        // Close sidebar when clicking overlay
        $('#sidebarOverlay').on('click', function() {
            closeSidebar();
        });

        // Sidebar menu items
        $('.sidebar-menu .nav-link').on('click', function(e) {
            e.preventDefault();
            const view = $(this).data('view');
            
            // Update active menu item
            $('.sidebar-menu .nav-link').removeClass('active');
            $(this).addClass('active');
            
            // Switch view
            switchView(view);
            
            // Close sidebar on mobile
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    }

    function toggleSidebar() {
        const sidebar = $('#sidebar');
        const mainContent = $('#mainContent');
        const overlay = $('#sidebarOverlay');
        
        if (sidebar.hasClass('show')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    function openSidebar() {
        $('#sidebar').addClass('show');
        $('#mainContent').addClass('sidebar-open');
        if (window.innerWidth <= 768) {
            $('#sidebarOverlay').addClass('show');
        }
    }

    function closeSidebar() {
        $('#sidebar').removeClass('show');
        $('#mainContent').removeClass('sidebar-open');
        $('#sidebarOverlay').removeClass('show');
    }

    function switchView(view) {
        if (view === 'common') {
            $('#logsTable').hide();
            $('#summaryTable').show();
            $('#logType').val('common');
            summaryTable.ajax.reload();
        } else {
            $('#summaryTable').hide();
            $('#logsTable').show();
            $('#logType').val('console');
            logsTable.ajax.reload();
        }
    }

    function displayUserInfo() {
        // Get user info from sessionStorage (set during login)
        const user = JSON.parse(sessionStorage.getItem('user') || '{}');
        if (user.fullName) {
            $('#userDisplay').text(`Welcome, ${user.fullName}`);
        } else if (user.username) {
            $('#userDisplay').text(`Welcome, ${user.username}`);
        }
    }
    // loadData/updateTable are no longer needed with server-side DataTables
    
    function updateRecordCount(count) {
        $('#recordCount').text(count + ' records');
    }
    
    function showLoading(show) {
        if (show) {
            $('#loadingSpinner').show();
            $('.table-container').hide();
        } else {
            $('#loadingSpinner').hide();
            $('.table-container').show();
        }
    }
    
    function showError(message) {
        $('#errorMessage').text(message);
        $('#errorAlert').removeClass('d-none');
    }
    
    function hideError() {
        $('#errorAlert').addClass('d-none');
    }
    
    function formatDateTime(dateTimeString) {
        if (!dateTimeString) return '';

        try {
            const date = new Date(dateTimeString);
            return date.toLocaleString();
        } catch (e) {
            return dateTimeString;
        }
    }

    function formatDateOnly(dateTimeString) {
        if (!dateTimeString) return '';

        try {
            const date = new Date(dateTimeString);
            return date.toLocaleDateString();
        } catch (e) {
            return dateTimeString;
        }
    }
    
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    function resetPracticeIdDropdown() {
        const practiceSelect = $('#practiceId');
        if (practiceSelect.hasClass('selectpicker')) {
            practiceSelect.selectpicker('val', '');
            practiceSelect.selectpicker('refresh');
        }
    }

    // Global function to show stack trace modal
    window.showStackTrace = function(stackTrace) {
        $('#stackTraceContent').text(stackTrace);
        $('#stackTraceModal').modal('show');
    };

    // Global function to reload practice IDs (for debugging)
    window.reloadPracticeIds = function() {
        practiceIdsLoaded = false;
        loadPracticeIds();
    };

    // Edit record function
    window.editRecord = function(recordId) {
        // Find the record data from the current table data
        const tableData = logsTable.data().toArray();
        const recordData = tableData.find(row => row[0] == recordId);

        if (recordData) {
            // Populate the edit form
            $('#editRecordId').val(recordData[0]);           // ID
            $('#editPracticeId').val(recordData[1]);         // Practice ID
            $('#editErrorMessage').val(recordData[2]);       // Error Message
            $('#editUrl').val(recordData[3]);                // URL
            $('#editErrorTime').val(recordData[4]);          // Error Time
            $('#editStackTrace').val(recordData[5]);         // Stack Trace
            $('#editLLMSolution').val(recordData[6]);        // LLMSolution
            $('#editJiraStatus').val(recordData[7]);         // Jira Status
            $('#editInsertedAt').val(recordData[8]);         // Inserted At

            // Show the modal
            $('#editRecordModal').modal('show');
        } else {
            showError('Record not found');
        }
    };

    // Delete record function
    window.deleteRecord = function(recordId) {
        if (confirm('Are you sure you want to delete this record?')) {
            // Here you would typically make an AJAX call to delete the record
            // For now, just show a message
            alert('Delete functionality would be implemented here for record ID: ' + recordId);
        }
    };

    // Save record function
    window.saveRecord = function() {
        const formData = {
            id: $('#editRecordId').val(),
            practiceid: $('#editPracticeId').val(),
            errormessage: $('#editErrorMessage').val(),
            url: $('#editUrl').val(),
            errortime: $('#editErrorTime').val(),
            stacktrace: $('#editStackTrace').val(),
            jirastatus: $('#editJiraStatus').val()
        };

        // Here you would typically make an AJAX call to save the record
        // For now, just show a message and close the modal
        alert('Save functionality would be implemented here for record ID: ' + formData.id);
        $('#editRecordModal').modal('hide');
    };

    // Open Jira function
    window.openJira = function(recordId) {
        // Here you would typically make an AJAX call to create a Jira ticket
        // and then update the record's Jira status
        if (confirm('Create a new Jira ticket for this error log?')) {
            alert('Jira ticket creation would be implemented here for record ID: ' + recordId);
            // After successful Jira creation, you would:
            // 1. Update the record's JiraStatus to 1
            // 2. Reload the table to show the updated status
            // loadData();
        }
    };
});
