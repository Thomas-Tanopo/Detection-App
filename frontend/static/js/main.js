$(document).ready(function() {
    function toggleSidebar(show) {
        $('#sidebar').toggleClass('show', show);
        $('#sidebarOverlay').toggleClass('show', show);
    }

    $('#sidebarToggle').on('click', function() {
        toggleSidebar(true);
    });

    $('#sidebarClose').on('click', function() {
        toggleSidebar(false);
    });

    $('#sidebarOverlay').on('click', function() {
        toggleSidebar(false);
    });

    $(document).on('click', function(e) {
        if ($(window).width() < 768) {
            if (!$(e.target).closest('#sidebar').length && !$(e.target).closest('#sidebarToggle').length) {
                toggleSidebar(false);
            }
        }
    });

    $(window).on('resize', function() {
        if ($(window).width() >= 768) {
            toggleSidebar(false);
        }
    });
});

function showAlert(message, type) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
    const container = document.querySelector('.container-fluid.p-3, .container-fluid.p-md-4');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}
