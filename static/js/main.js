/**
 * Distribution Group Management - Main JavaScript
 * Provides enhanced interactivity and user experience
 */

(function($) {
    'use strict';

    // Global application object
    window.GroupManagement = {
        init: function() {
            this.initDataTables();
            this.initFormValidation();
            this.initModals();
            this.initSearchFunctionality();
            this.initUserSearch();
            this.initTooltips();
            this.initConfirmations();
            this.bindEvents();
        },

        // Initialize DataTables for better table management
        initDataTables: function() {
            // Groups table
            if ($('#groupsTable').length) {
                $('#groupsTable').DataTable({
                    "pageLength": 15,
                    "searching": true,
                    "lengthChange": true,
                    "info": true,
                    "paging": true,
                    "order": [[0, "asc"]],
                    "language": {
                        "search": "Search groups:",
                        "lengthMenu": "Show _MENU_ groups per page",
                        "info": "Showing _START_ to _END_ of _TOTAL_ groups",
                        "emptyTable": "No groups found",
                        "zeroRecords": "No matching groups found"
                    },
                    "columnDefs": [
                        { "orderable": false, "targets": -1 } // Disable sorting on Actions column
                    ]
                });
            }

            // Users table
            if ($('#usersTable').length) {
                $('#usersTable').DataTable({
                    "pageLength": 15,
                    "searching": true,
                    "lengthChange": true,
                    "info": true,
                    "paging": true,
                    "order": [[0, "asc"]],
                    "language": {
                        "search": "Search users:",
                        "lengthMenu": "Show _MENU_ users per page",
                        "info": "Showing _START_ to _END_ of _TOTAL_ users",
                        "emptyTable": "No users found",
                        "zeroRecords": "No matching users found"
                    },
                    "columnDefs": [
                        { "orderable": false, "targets": -1 } // Disable sorting on Actions column
                    ]
                });
            }

            // Group members table
            if ($('#groupMembersTable').length) {
                $('#groupMembersTable').DataTable({
                    "pageLength": 10,
                    "searching": true,
                    "lengthChange": false,
                    "info": true,
                    "paging": true,
                    "order": [[0, "asc"]],
                    "language": {
                        "search": "Search members:",
                        "info": "Showing _START_ to _END_ of _TOTAL_ members",
                        "emptyTable": "No members in this group",
                        "zeroRecords": "No matching members found"
                    }
                });
            }
        },

        // Form validation enhancements
        initFormValidation: function() {
            // Generic form validation
            $('.needs-validation').on('submit', function(e) {
                if (!this.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                $(this).addClass('was-validated');
            });

            // Real-time email validation
            $('input[type="email"]').on('blur', function() {
                const email = $(this).val();
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                
                if (email && !emailRegex.test(email)) {
                    $(this).addClass('is-invalid');
                    this.setCustomValidity('Please enter a valid email address');
                } else {
                    $(this).removeClass('is-invalid').addClass('is-valid');
                    this.setCustomValidity('');
                }
            });

            // Group name validation (no special characters except spaces and hyphens)
            $('input[name="name"]').on('input', function() {
                const value = $(this).val();
                const nameRegex = /^[a-zA-Z0-9\s\-_]+$/;
                
                if (value && !nameRegex.test(value)) {
                    $(this).addClass('is-invalid');
                    this.setCustomValidity('Group name can only contain letters, numbers, spaces, hyphens, and underscores');
                } else {
                    $(this).removeClass('is-invalid').addClass('is-valid');
                    this.setCustomValidity('');
                }
            });
        },

        // Modal management
        initModals: function() {
            // Clear form data when modals are closed
            $('.modal').on('hidden.bs.modal', function() {
                const form = $(this).find('form')[0];
                if (form) {
                    form.reset();
                    $(form).removeClass('was-validated');
                    $(form).find('.is-invalid, .is-valid').removeClass('is-invalid is-valid');
                }
            });

            // Focus first input when modals open
            $('.modal').on('shown.bs.modal', function() {
                $(this).find('input:first').focus();
            });

            // Handle form submissions in modals
            $('.modal form').on('submit', function(e) {
                const $form = $(this);
                const $submitBtn = $form.find('button[type="submit"]');
                
                // Add loading state
                $submitBtn.prop('disabled', true);
                $submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Processing...');
                
                // Form will submit normally, loading state will be cleared on page reload/redirect
            });
        },

        // Enhanced search functionality
        initSearchFunctionality: function() {
            // Debounced search for better performance
            let searchTimeout;
            $('.search-input').on('input', function() {
                clearTimeout(searchTimeout);
                const $input = $(this);
                
                searchTimeout = setTimeout(function() {
                    // Trigger search after 300ms of no typing
                    const searchTerm = $input.val();
                    if (searchTerm.length >= 2 || searchTerm.length === 0) {
                        // In a real implementation, this could trigger AJAX search
                        console.log('Search for:', searchTerm);
                    }
                }, 300);
            });

            // Clear search functionality
            $('.clear-search').on('click', function() {
                const $searchInput = $(this).closest('.input-group').find('input');
                $searchInput.val('').focus();
                
                // Submit form to clear search results
                $searchInput.closest('form').submit();
            });
        },

        // User search for adding members to groups
        initUserSearch: function() {
            const $userSearchInput = $('#userSearch');
            const $userSearchResults = $('#userSearchResults');
            let searchTimeout;

            if ($userSearchInput.length) {
                $userSearchInput.on('input', function() {
                    clearTimeout(searchTimeout);
                    const query = $(this).val().trim();
                    
                    if (query.length < 2) {
                        $userSearchResults.empty().hide();
                        return;
                    }

                    searchTimeout = setTimeout(function() {
                        // In a real implementation, this would make an AJAX call
                        // For now, we'll simulate the search functionality
                        $userSearchResults.html(
                            '<div class="list-group-item">Search functionality would appear here</div>'
                        ).show();
                    }, 300);
                });

                // Hide results when clicking outside
                $(document).on('click', function(e) {
                    if (!$(e.target).closest('#userSearch, #userSearchResults').length) {
                        $userSearchResults.hide();
                    }
                });
            }
        },

        // Initialize tooltips for better UX
        initTooltips: function() {
            // Initialize Bootstrap tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });

            // Add tooltips to common elements
            $('.btn[disabled]').attr('data-bs-toggle', 'tooltip')
                               .attr('title', 'You do not have permission for this action');
        },

        // Confirmation dialogs for destructive actions
        initConfirmations: function() {
            // Confirm before removing users from groups
            $('.confirm-remove').on('click', function(e) {
                e.preventDefault();
                const userName = $(this).data('user-name') || 'this user';
                const groupName = $(this).data('group-name') || 'the group';
                
                if (confirm(`Are you sure you want to remove ${userName} from ${groupName}?`)) {
                    // Submit the form
                    $(this).closest('form').submit();
                }
            });

            // Confirm before deleting groups (if implemented)
            $('.confirm-delete').on('click', function(e) {
                e.preventDefault();
                const itemName = $(this).data('item-name') || 'this item';
                
                if (confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                    $(this).closest('form').submit();
                }
            });
        },

        // Bind various event handlers
        bindEvents: function() {
            // Smooth scrolling for anchor links
            $('a[href^="#"]').on('click', function(e) {
                const target = $(this.getAttribute('href'));
                if (target.length) {
                    e.preventDefault();
                    $('html, body').stop().animate({
                        scrollTop: target.offset().top - 20
                    }, 1000);
                }
            });

            // Auto-dismiss alerts after 5 seconds
            $('.alert:not(.alert-danger)').delay(5000).fadeOut();

            // Handle card hover effects
            $('.stat-card, .card').on('mouseenter', function() {
                $(this).addClass('shadow-sm');
            }).on('mouseleave', function() {
                $(this).removeClass('shadow-sm');
            });

            // Print functionality
            $('.print-btn').on('click', function() {
                window.print();
            });

            // Copy to clipboard functionality
            $('.copy-btn').on('click', function() {
                const textToCopy = $(this).data('copy-text') || $(this).prev().text();
                
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(textToCopy).then(function() {
                        GroupManagement.showToast('Copied to clipboard!', 'success');
                    });
                } else {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = textToCopy;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    GroupManagement.showToast('Copied to clipboard!', 'success');
                }
            });

            // Toggle password visibility (if any password fields exist)
            $('.toggle-password').on('click', function() {
                const $passwordInput = $($(this).data('target'));
                const type = $passwordInput.attr('type') === 'password' ? 'text' : 'password';
                $passwordInput.attr('type', type);
                $(this).find('i').toggleClass('bi-eye bi-eye-slash');
            });

            // Auto-resize textareas
            $('textarea').on('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        },

        // Utility function to show toast notifications
        showToast: function(message, type = 'info') {
            // Create toast HTML
            const toastHtml = `
                <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : 'primary'} border-0" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;

            // Add to toast container or create one
            let $toastContainer = $('#toast-container');
            if (!$toastContainer.length) {
                $toastContainer = $('<div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3"></div>');
                $('body').append($toastContainer);
            }

            const $toast = $(toastHtml);
            $toastContainer.append($toast);

            // Initialize and show toast
            const toast = new bootstrap.Toast($toast[0], {
                autohide: true,
                delay: 3000
            });
            toast.show();

            // Remove toast element after it's hidden
            $toast.on('hidden.bs.toast', function() {
                $(this).remove();
            });
        },

        // Loading state management
        setLoadingState: function($element, loading = true) {
            if (loading) {
                $element.prop('disabled', true);
                const originalText = $element.text();
                $element.data('original-text', originalText);
                $element.html('<span class="spinner-border spinner-border-sm me-2"></span>Loading...');
            } else {
                $element.prop('disabled', false);
                const originalText = $element.data('original-text');
                if (originalText) {
                    $element.text(originalText);
                }
            }
        },

        // Format phone numbers as user types
        formatPhoneNumber: function(input) {
            // Remove all non-digit characters
            const cleaned = input.replace(/\D/g, '');
            
            // Format as (XXX) XXX-XXXX
            const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
            if (match) {
                return '(' + match[1] + ') ' + match[2] + '-' + match[3];
            }
            
            return input;
        }
    };

    // Report generation functionality
    window.ReportGenerator = {
        generateGroupReport: function(groupId, format = 'pdf') {
            const url = `/reports/group_membership?group_id=${groupId}&format=${format}`;
            window.open(url, '_blank');
        },

        generateCustomReport: function(options) {
            // This would be implemented to handle custom report generation
            console.log('Generating custom report with options:', options);
            GroupManagement.showToast('Custom report generation started...', 'info');
        }
    };

    // Initialize everything when document is ready
    $(document).ready(function() {
        GroupManagement.init();

        // Phone number formatting
        $('input[type="tel"], input[name*="phone"]').on('input', function() {
            const formatted = GroupManagement.formatPhoneNumber($(this).val());
            $(this).val(formatted);
        });

        // Auto-save draft functionality for long forms
        const $longForms = $('form textarea, form input[type="text"]').filter(function() {
            return $(this).closest('form').find('textarea, input[type="text"]').length > 3;
        });

        if ($longForms.length) {
            let saveTimeout;
            $longForms.on('input', function() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(function() {
                    // In a real implementation, this would save draft to localStorage or server
                    console.log('Auto-saving draft...');
                }, 2000);
            });
        }

        // Keyboard shortcuts
        $(document).on('keydown', function(e) {
            // Ctrl+S to save (prevent default browser save)
            if (e.ctrlKey && e.which === 83) {
                e.preventDefault();
                const $visibleForm = $('form:visible').first();
                if ($visibleForm.length) {
                    $visibleForm.submit();
                }
            }

            // Escape key to close modals
            if (e.which === 27) {
                $('.modal.show').modal('hide');
            }
        });

        // Add loading states to external links
        $('a[href^="http"]').on('click', function() {
            const $link = $(this);
            if (!$link.hasClass('no-loading')) {
                $link.append(' <span class="spinner-border spinner-border-sm ms-2"></span>');
            }
        });

        // Enhance accessibility
        $('button, a').on('focus', function() {
            $(this).addClass('focused');
        }).on('blur', function() {
            $(this).removeClass('focused');
        });

        // Handle responsive sidebar toggle (for mobile)
        $('#sidebarToggle').on('click', function() {
            $('.sidebar').toggleClass('show');
        });

        // Close sidebar when clicking overlay on mobile
        $('.sidebar-overlay').on('click', function() {
            $('.sidebar').removeClass('show');
        });
    });

})(jQuery);

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GroupManagement, ReportGenerator };
}
