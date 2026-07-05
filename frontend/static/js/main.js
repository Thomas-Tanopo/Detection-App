function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = 'login.html';
  }
}

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem('user'));
  } catch { return null; }
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = 'login.html';
}

function showAlert(msg, type) {
  type = type || 'success';
  const container = document.getElementById('alertContainer') || document.body;
  const div = document.createElement('div');
  div.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
  div.style.zIndex = 9999;
  div.innerHTML = `${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  container.appendChild(div);
  setTimeout(() => div.remove(), 4000);
}

function showModal(id) {
  const el = document.getElementById(id);
  if (el) { const m = bootstrap.Modal.getOrCreateInstance(el); m.show(); }
}

function hideModal(id) {
  const el = document.getElementById(id);
  if (el) { const m = bootstrap.Modal.getInstance(el); m.hide(); }
}

function formatDate(d) {
  if (!d) return '-';
  const dt = new Date(d);
  return dt.toLocaleDateString('id-ID', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function getDateStr(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function highlightActiveLink() {
  const page = window.location.pathname.split('/').pop() || 'dashboard.html';
  document.querySelectorAll('.nav-link').forEach(a => {
    const href = a.getAttribute('href');
    if (href === page) a.classList.add('active');
  });
}

function getBaseUrl() {
  return window.location.origin + window.location.pathname.replace(/[^/]*$/, '');
}

function handleApiError(err) {
  console.error(err);
  showAlert(err.message || 'Terjadi kesalahan', 'danger');
}

const DataTableIndo = {
  processing: 'Memproses...',
  search: 'Cari:',
  lengthMenu: 'Tampilkan _MENU_ data',
  info: 'Menampilkan _START_ sampai _END_ dari _TOTAL_ data',
  infoEmpty: 'Tidak ada data',
  infoFiltered: '(difilter dari _MAX_ total data)',
  infoPostFix: '',
  loadingRecords: 'Memuat...',
  zeroRecords: 'Tidak ditemukan data yang cocok',
  emptyTable: 'Tidak ada data',
  paginate: {
    first: 'Pertama',
    previous: 'Sebelumnya',
    next: 'Selanjutnya',
    last: 'Terakhir'
  },
  aria: { sortAscending: ': aktifkan untuk mengurutkan ascending', sortDescending: ': aktifkan untuk mengurutkan descending' }
};

function initDataTable(selector, opts) {
  opts = opts || {};
  opts.language = DataTableIndo;
  opts.responsive = true;
  if (!opts.pageLength) opts.pageLength = 10;
  return $(selector).DataTable(opts);
}

document.addEventListener('DOMContentLoaded', function() {
  highlightActiveLink();
});
