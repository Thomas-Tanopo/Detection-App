let currentUser = JSON.parse(localStorage.getItem('user') || 'null');
let detectionChart = null, topChart = null;
const MONTHS = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];

function showAlert(msg, type = 'success') {
    const el = document.getElementById('alertBox');
    if (el) el.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show">${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

function requireAuth() { if (!localStorage.getItem('token')) { renderPage('login'); return false; } return true; }

function renderPage(page) {
    const app = document.getElementById('app');
    if (page === 'login' || page === 'register') renderAuthPage(page, app);
    else if (requireAuth()) renderAppPage(page, app);
}

function renderAuthPage(page, app) {
    const isLogin = page === 'login';
    app.innerHTML = `
    <div class="auth-wrapper">
      <div class="auth-card">
        <div class="text-center mb-4">
          <div class="auth-icon mb-3"><i class="bi bi-camera-fill"></i></div>
          <h4 class="fw-bold">${isLogin ? 'Masuk' : 'Daftar'}</h4>
          <p class="text-muted small">${isLogin ? 'Silakan masuk ke akun Anda' : 'Buat akun baru untuk memulai'}</p>
        </div>
        <div id="alertBox"></div>
        <form id="authForm">
          ${isLogin ? '' : `<div class="mb-3"><label class="form-label small fw-semibold">Nama Lengkap</label><input class="form-control" id="fullName" required></div>`}
          <div class="mb-3"><label class="form-label small fw-semibold">Username</label><input class="form-control" id="username" required></div>
          ${isLogin ? '' : `<div class="mb-3"><label class="form-label small fw-semibold">Email</label><input type="email" class="form-control" id="email" required></div>`}
          <div class="mb-3"><label class="form-label small fw-semibold">Password</label><input type="password" class="form-control" id="password" required></div>
          <button class="btn btn-primary w-100 py-2">${isLogin ? 'Masuk' : 'Daftar'}</button>
        </form>
        <p class="text-center mt-3 small">${isLogin ? 'Belum punya akun?' : 'Sudah punya akun?'} <a href="#" onclick="renderPage('${isLogin ? 'register' : 'login'}')">${isLogin ? 'Daftar' : 'Masuk'}</a></p>
      </div>
    </div>`;
    document.getElementById('authForm').onsubmit = async (e) => {
        e.preventDefault();
        const data = isLogin ? { username: e.target.username.value, password: e.target.password.value }
            : { username: e.target.username.value, email: document.getElementById('email').value, password: e.target.password.value, full_name: document.getElementById('fullName').value };
        try {
            const res = isLogin ? await api.login(data.username, data.password) : await api.register(data);
            localStorage.setItem('token', res.access_token);
            localStorage.setItem('user', JSON.stringify(res.user));
            currentUser = res.user;
            renderPage('dashboard');
        } catch (err) { showAlert(err.message, 'danger'); }
    };
}

function renderAppPage(page, app) {
    const menu = [
        { id: 'dashboard', icon: 'speedometer2', label: 'Dashboard' },
        { id: 'categories', icon: 'tags', label: 'Kategori' },
        { id: 'items', icon: 'box', label: 'Objek' },
        { id: 'upload', icon: 'upload', label: 'Upload Gambar' },
        { id: 'camera', icon: 'camera', label: 'Kamera' },
        { id: 'history', icon: 'clock-history', label: 'Riwayat Deteksi' },
        { id: 'reports', icon: 'file-earmark-bar-graph', label: 'Reports' },
    ];
    app.innerHTML = `
    <div class="d-flex" id="wrapper">
      <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar(false)"></div>
      <div class="sidebar d-flex flex-column flex-shrink-0 p-3" id="sidebar">
        <div class="d-flex align-items-center justify-content-between mb-4">
          <a href="#" class="sidebar-brand d-flex align-items-center text-decoration-none" onclick="renderPage('dashboard')">
            <i class="bi bi-camera-fill me-2"></i><span class="fw-bold">Detect App</span>
          </a>
          <button class="btn btn-link text-white d-md-none p-0" onclick="toggleSidebar(false)"><i class="bi bi-x-lg fs-5"></i></button>
        </div>
        <hr>
        <ul class="nav nav-pills flex-column mb-auto">${menu.map(m => `
          <li class="nav-item"><a href="#" class="nav-link ${page===m.id?'active':''}" onclick="renderPage('${m.id}')"><i class="bi bi-${m.icon} me-2"></i>${m.label}</a></li>
        `).join('')}</ul>
        <hr>
        <div class="dropdown">
          <a href="#" class="d-flex align-items-center text-white text-decoration-none dropdown-toggle" data-bs-toggle="dropdown">
            <i class="bi bi-person-circle me-2 fs-5"></i><strong class="text-truncate">${currentUser?.full_name || currentUser?.username}</strong>
          </a>
          <ul class="dropdown-menu dropdown-menu-dark text-small shadow">
            <li><a class="dropdown-item" href="#" onclick="logout()"><i class="bi bi-box-arrow-right me-2"></i>Logout</a></li>
          </ul>
        </div>
      </div>
      <div class="content-wrapper">
        <nav class="navbar navbar-expand navbar-light bg-white shadow-sm px-3 px-md-4">
          <div class="container-fluid">
            <button class="btn btn-outline-secondary d-md-none" onclick="toggleSidebar(true)"><i class="bi bi-list fs-5"></i></button>
            <span class="navbar-text ms-2" id="pageTitle">${page.charAt(0).toUpperCase()+page.slice(1)}</span>
            <div class="ms-auto d-flex align-items-center">
              <span class="badge bg-primary bg-opacity-10 text-primary d-none d-sm-inline me-3"><i class="bi bi-person me-1"></i>${currentUser?.full_name || currentUser?.username}</span>
              <span class="badge bg-primary bg-opacity-10 text-primary d-sm-none me-2"><i class="bi bi-person"></i></span>
            </div>
          </div>
        </nav>
        <div class="container-fluid p-3 p-md-4"><div id="alertBox"></div><div id="pageContent"></div></div>
      </div>
    </div>`;
    loadPage(page);
}

function toggleSidebar(show) {
    document.getElementById('sidebar')?.classList.toggle('show', show);
    document.getElementById('sidebarOverlay')?.classList.toggle('show', show);
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    currentUser = null;
    renderPage('login');
}

function loadPage(page) {
    const titles = { dashboard:'Dashboard', categories:'Kategori', items:'Objek', upload:'Upload Gambar', camera:'Kamera', history:'Riwayat Deteksi', reports:'Reports' };
    document.getElementById('pageTitle').textContent = titles[page] || page;
    const content = document.getElementById('pageContent');
    if (page === 'dashboard') renderDashboard(content);
    else if (page === 'categories') renderCategories(content);
    else if (page === 'items') renderItems(content);
    else if (page === 'upload') renderUpload(content);
    else if (page === 'camera') renderCamera(content);
    else if (page === 'history') renderHistory(content);
    else if (page === 'reports') renderReports(content);
}

// ========== DASHBOARD ==========
async function renderDashboard(el) {
    el.innerHTML = `<div class="text-center py-5"><div class="spinner-border"></div></div>`;
    const [stats, trend, topLabels, recent] = await Promise.all([
        api.dashboard.stats(), api.dashboard.trend(), api.dashboard.topLabels(), api.dashboard.recent()
    ]);
    const tp = stats.trend_pct;
    el.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div><h5 class="mb-1 fw-bold">Selamat datang, ${currentUser?.full_name||currentUser?.username}!</h5><p class="text-muted mb-0 d-none d-sm-block">Ringkasan aktivitas deteksi hari ini.</p></div>
      <span class="d-none d-md-block badge bg-light text-muted px-3 py-2"><i class="bi bi-calendar3 me-1"></i>${new Date().getDate()} ${MONTHS[new Date().getMonth()]} ${new Date().getFullYear()}</span>
    </div>
    <div class="row g-4 mb-4">${[
      {v:stats.today_detections,l:'Deteksi Hari Ini',i:'camera-fill',c:'#667eea #764ba2',s:`<i class="bi bi-arrow-${tp>0?'up':tp<0?'down':'dash'}-short"></i> ${tp>0?'+':''}${tp}% vs kemarin`},
      {v:stats.total_detections,l:'Total Deteksi',i:'bar-chart-fill',c:'#f093fb #f5576c',s:'<i class="bi bi-clock"></i> Semua waktu'},
      {v:stats.total_items,l:'Master Objek',i:'box-fill',c:'#4facfe #00f2fe',s:`<i class="bi bi-tags"></i> ${stats.total_categories} Kategori`},
      {v:stats.total_users,l:'Pengguna',i:'people-fill',c:'#43e97b #38f9d7',s:'<i class="bi bi-person"></i> Terdaftar'}
    ].map(c => `
      <div class="col-md-6 col-xl-3"><div class="card border-0 shadow-sm h-100" style="background:linear-gradient(135deg,${c.c})">
        <div class="card-body position-relative">
          <div class="d-flex justify-content-between align-items-start"><div class="z-1"><p class="text-white opacity-75 mb-1 small">${c.l}</p><h2 class="text-white mb-0 fw-bold">${c.v}</h2><small class="text-white opacity-75">${c.s}</small></div><div class="z-1"><div class="bg-white bg-opacity-25 rounded-circle p-3 d-inline-flex"><i class="bi bi-${c.i} fs-4 text-white"></i></div></div></div>
          <div class="position-absolute top-0 end-0 bottom-0 opacity-10 d-flex align-items-center pe-3"><i class="bi bi-${c.i}" style="font-size:6rem"></i></div>
        </div></div></div>
    `).join('')}</div>
    <div class="row g-4 mb-4">
      <div class="col-xl-8"><div class="card border-0 shadow-sm"><div class="card-header bg-white d-flex justify-content-between align-items-center py-3"><h6 class="mb-0 fw-bold"><i class="bi bi-graph-up me-2 text-primary"></i>Tren Deteksi (14 Hari)</h6></div><div class="card-body"><canvas id="detectionChart" height="200"></canvas></div></div></div>
      <div class="col-xl-4"><div class="card border-0 shadow-sm h-100"><div class="card-header bg-white py-3"><h6 class="mb-0 fw-bold"><i class="bi bi-pie-chart me-2 text-info"></i>Top Objek</h6></div><div class="card-body"><canvas id="topObjectsChart" height="250"></canvas></div></div></div>
    </div>
    <div class="row g-4">
      <div class="col-12"><div class="card border-0 shadow-sm"><div class="card-header bg-white d-flex justify-content-between align-items-center py-3"><h6 class="mb-0 fw-bold"><i class="bi bi-clock-history me-2 text-warning"></i>Aktivitas Terbaru</h6></div><div class="card-body p-0${recent.length?'':' text-center py-5'}" id="recentContent">${recent.length?renderRecentTable(recent):'<i class="bi bi-inbox fs-1 text-muted d-block mb-2"></i><p class="text-muted mb-0">Belum ada aktivitas</p>'}</div></div></div>
    </div>`;
    if (trend.labels.length) {
        detectionChart = new Chart(document.getElementById('detectionChart'), { type:'line', data:{ labels:trend.labels, datasets:[{ label:'Deteksi', data:trend.data, borderColor:'#667eea', backgroundColor:'rgba(102,126,234,0.1)', fill:true, tension:0.4, pointBackgroundColor:'#667eea', pointBorderColor:'#fff', pointBorderWidth:2, pointRadius:4, borderWidth:3 }] }, options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:false } }, scales:{ y:{ beginAtZero:true, ticks:{ stepSize:1, maxTicksLimit:6 } }, x:{ grid:{ display:false } } } } });
    }
    if (topLabels.names.length) {
        topChart = new Chart(document.getElementById('topObjectsChart'), { type:'doughnut', data:{ labels:topLabels.names, datasets:[{ data:topLabels.counts, backgroundColor:['#667eea','#f5576c','#4facfe','#43e97b','#fa8231','#a55eea','#2bcbba','#fd9644'], borderWidth:0 }] }, options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ position:'bottom', labels:{ boxWidth:12, padding:8, font:{ size:11 } } } }, cutout:'60%' } });
    }
}

function renderRecentTable(data) {
    let html = `<div class="table-responsive"><table class="table table-hover mb-0"><thead class="table-light"><tr><th class="ps-4">#ID</th><th>Gambar</th><th>Objek</th><th>Jumlah</th><th class="d-none d-sm-table-cell text-end pe-4">Waktu</th></tr></thead><tbody>`;
    data.forEach(d => {
        html += `<tr><td class="ps-4 fw-semibold">#${d.id}</td><td>${d.image_url?`<img src="${API_BASE}${d.image_url}" class="rounded" style="width:50px;height:50px;object-fit:cover" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2250%22 height=%2250%22><rect fill=%22%23eee%22 width=%2250%22 height=%2250%22/><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22central%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2210%22>N/A</text></svg>'">`:'<span class="text-muted">-</span>'}</td><td>${d.objects.slice(0,3).map(o=>`<span class="badge bg-primary bg-opacity-10 text-primary me-1">${o.label}</span>`).join('')}${d.objects.length>3?`<span class="badge bg-secondary">+${d.objects.length-3}</span>`:''}</td><td><span class="badge bg-secondary bg-opacity-10 text-secondary">${d.total_objects} objek</span></td><td class="d-none d-sm-table-cell text-end pe-4 text-muted small">${new Date(d.created_at).toLocaleString('id-ID')}</td></tr>`;
    });
    html += '</tbody></table></div>';
    return html;
}

// ========== CATEGORIES ==========
async function renderCategories(el) {
    el.innerHTML = `<div class="text-center py-5"><div class="spinner-border"></div></div>`;
    const cats = await api.categories.list();
    el.innerHTML = `
    <div class="card shadow-sm border-0"><div class="card-header bg-white d-flex justify-content-between align-items-center py-3"><h6 class="mb-0 fw-bold">Daftar Kategori</h6><button class="btn btn-primary" onclick="showCatModal()"><i class="bi bi-plus-lg me-1"></i>Tambah</button></div>
      <div class="card-body"><div class="table-responsive"><table class="table table-hover datatable" id="catTable"><thead class="table-light"><tr><th style="width:40px">No</th><th>Nama</th><th class="d-none d-md-table-cell">Deskripsi</th><th class="d-none d-sm-table-cell">Dibuat</th><th style="width:100px">Aksi</th></tr></thead><tbody>${cats.map((c,i)=>`
        <tr><td>${i+1}</td><td><span class="badge bg-secondary bg-opacity-10 text-secondary fs-6 px-3 py-2">${c.name}</span></td><td class="d-none d-md-table-cell">${c.description||'-'}</td><td class="d-none d-sm-table-cell">${new Date(c.created_at).toLocaleString('id-ID')}</td>
        <td><div class="d-flex gap-1 justify-content-center">
          <button class="btn btn-warning btn-sm" onclick="showCatModal(${c.id},'${c.name}','${(c.description||'').replace(/'/g,"\\'")}')"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-danger btn-sm" onclick="deleteCat(${c.id},'${c.name}')"><i class="bi bi-trash"></i></button>
        </div></td></tr>
      `).join('')}</tbody></table></div></div></div>`;
    if (cats.length) initDT('catTable', 3);
}

let catModalCallback;
function showCatModal(id, name, description) {
    const isEdit = !!id;
    const m = new bootstrap.Modal(Object.assign(document.createElement('div'), { className:'modal fade', innerHTML:`<div class="modal-dialog"><div class="modal-content">
      <div class="modal-header"><h6 class="modal-title fw-bold">${isEdit?'Edit':'Tambah'} Kategori</h6><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
      <div class="modal-body"><form id="catForm"><div class="mb-3"><label class="form-label">Nama Kategori</label><input class="form-control" id="catName" value="${name||''}" required></div><div class="mb-3"><label class="form-label">Deskripsi</label><textarea class="form-control" id="catDesc" rows="2">${description||''}</textarea></div></form></div>
      <div class="modal-footer"><button class="btn btn-secondary" data-bs-dismiss="modal">Batal</button><button class="btn btn-primary" id="catSaveBtn">Simpan</button></div></div></div>`}));
    m.show();
    document.getElementById('catSaveBtn').onclick = async () => {
        const data = { name: document.getElementById('catName').value, description: document.getElementById('catDesc').value };
        try { isEdit ? await api.categories.update(id, data) : await api.categories.create(data); m.hide(); renderCategories(document.getElementById('pageContent')); showAlert('Berhasil!'); } catch (e) { showAlert(e.message, 'danger'); }
    };
}

async function deleteCat(id, name) {
    if (!confirm(`Yakin hapus ${name}?`)) return;
    try { await api.categories.delete(id); renderCategories(document.getElementById('pageContent')); showAlert('Berhasil dihapus!'); } catch (e) { showAlert(e.message, 'danger'); }
}

// ========== ITEMS ==========
async function renderItems(el) {
    el.innerHTML = `<div class="text-center py-5"><div class="spinner-border"></div></div>`;
    const [items, cats] = await Promise.all([api.items.list(), api.categories.list()]);
    el.innerHTML = `
    <div class="card shadow-sm border-0"><div class="card-header bg-white d-flex justify-content-between align-items-center py-3"><h6 class="mb-0 fw-bold">Daftar Objek</h6><button class="btn btn-primary" onclick="showItemModal(${JSON.stringify(cats).replace(/"/g,'&quot;')})"><i class="bi bi-plus-lg me-1"></i>Tambah</button></div>
      <div class="card-body"><div class="table-responsive"><table class="table table-hover datatable" id="itemTable"><thead class="table-light"><tr><th style="width:40px">No</th><th>Nama</th><th class="d-none d-sm-table-cell">Kategori</th><th class="d-none d-md-table-cell">Deskripsi</th><th class="d-none d-sm-table-cell">Dibuat</th><th style="width:100px">Aksi</th></tr></thead><tbody>${items.map((c,i)=>`
        <tr><td>${i+1}</td><td class="fw-semibold">${c.name}</td><td class="d-none d-sm-table-cell">${c.category_name?`<span class="badge bg-info bg-opacity-10 text-info">${c.category_name}</span>`:'-'}</td><td class="d-none d-md-table-cell">${c.description||'-'}</td><td class="d-none d-sm-table-cell">${new Date(c.created_at).toLocaleString('id-ID')}</td>
        <td><div class="d-flex gap-1 justify-content-center">
          <button class="btn btn-warning btn-sm" onclick="showItemModal(${JSON.stringify(cats).replace(/"/g,'&quot;')},${c.id},'${c.name.replace(/'/g,"\\'")}','${(c.description||'').replace(/'/g,"\\'")}',${c.category_id||0})"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-danger btn-sm" onclick="deleteItem(${c.id},'${c.name.replace(/'/g,"\\'")}')"><i class="bi bi-trash"></i></button>
        </div></td></tr>
      `).join('')}</tbody></table></div></div></div>`;
    if (items.length) initDT('itemTable', 4);
}

function showItemModal(cats, id, name, description, category_id) {
    const isEdit = !!id;
    const m = new bootstrap.Modal(Object.assign(document.createElement('div'), { className:'modal fade', innerHTML:`<div class="modal-dialog"><div class="modal-content">
      <div class="modal-header"><h6 class="modal-title fw-bold">${isEdit?'Edit':'Tambah'} Objek</h6><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
      <div class="modal-body"><form id="itemForm">
        <div class="mb-3"><label class="form-label">Nama Objek</label><input class="form-control" id="itemName" value="${name||''}" required></div>
        <div class="mb-3"><label class="form-label">Kategori</label><select class="form-select" id="itemCat"><option value="">Pilih Kategori</option>${cats.map(c=>`<option value="${c.id}" ${category_id==c.id?'selected':''}>${c.name}</option>`).join('')}</select></div>
        <div class="mb-3"><label class="form-label">Deskripsi</label><textarea class="form-control" id="itemDesc" rows="2">${description||''}</textarea></div>
      </form></div>
      <div class="modal-footer"><button class="btn btn-secondary" data-bs-dismiss="modal">Batal</button><button class="btn btn-primary" id="itemSaveBtn">Simpan</button></div></div></div>`}));
    m.show();
    document.getElementById('itemSaveBtn').onclick = async () => {
        const data = { name: document.getElementById('itemName').value, description: document.getElementById('itemDesc').value, category_id: parseInt(document.getElementById('itemCat').value) || 0 };
        try { isEdit ? await api.items.update(id, data) : await api.items.create(data); m.hide(); renderItems(document.getElementById('pageContent')); showAlert('Berhasil!'); } catch (e) { showAlert(e.message, 'danger'); }
    };
}

async function deleteItem(id, name) {
    if (!confirm(`Yakin hapus ${name}?`)) return;
    try { await api.items.delete(id); renderItems(document.getElementById('pageContent')); showAlert('Berhasil dihapus!'); } catch (e) { showAlert(e.message, 'danger'); }
}

// ========== UPLOAD ==========
function renderUpload(el) {
    el.innerHTML = `
    <div class="row justify-content-center"><div class="col-md-8">
      <div class="card shadow-sm border-0"><div class="card-body text-center p-4 p-md-5">
        <form id="uploadForm">
          <div class="drop-zone" id="dropZone">
            <i class="bi bi-cloud-arrow-up-fill fs-1 text-primary"></i>
            <h5 class="mt-3">Drag & Drop gambar di sini</h5>
            <p class="text-muted mb-3">atau klik untuk memilih file</p>
            <input type="file" name="image" id="imageInput" accept="image/*" class="d-none" required>
            <button type="button" class="btn btn-outline-primary btn-lg" id="selectBtn"><i class="bi bi-folder2-open me-1"></i>Pilih Gambar</button>
          </div>
          <div id="previewArea" class="mt-4 d-none">
            <div class="position-relative d-inline-block">
              <img id="preview" class="img-fluid rounded shadow-sm" style="max-height:400px">
              <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 m-2" id="removeBtn"><i class="bi bi-x"></i></button>
            </div>
            <div class="mt-3"><button type="submit" class="btn btn-primary btn-lg w-100 w-sm-auto" id="detectBtn"><i class="bi bi-search me-2"></i>Deteksi Objek</button></div>
          </div>
        </form>
      </div></div>
      <div id="uploadResult" class="mt-4 d-none"></div>
    </div></div>`;
    const dz = document.getElementById('dropZone'), inp = document.getElementById('imageInput'), pa = document.getElementById('previewArea'), prev = document.getElementById('preview');
    document.getElementById('selectBtn').onclick = () => inp.click();
    inp.onchange = (e) => { if (e.target.files[0]) { const r = new FileReader(); r.onload = (ev) => { prev.src = ev.target.result; dz.classList.add('d-none'); pa.classList.remove('d-none'); }; r.readAsDataURL(e.target.files[0]); } };
    dz.ondragover = (e) => { e.preventDefault(); dz.classList.add('drop-zone-active'); };
    dz.ondragleave = () => dz.classList.remove('drop-zone-active');
    dz.ondrop = (e) => { e.preventDefault(); dz.classList.remove('drop-zone-active'); const f = e.dataTransfer.files[0]; if (f && f.type.startsWith('image/')) { inp.files = e.dataTransfer.files; const r = new FileReader(); r.onload = (ev) => { prev.src = ev.target.result; dz.classList.add('d-none'); pa.classList.remove('d-none'); }; r.readAsDataURL(f); } };
    document.getElementById('removeBtn').onclick = () => { inp.value = ''; prev.src = ''; pa.classList.add('d-none'); dz.classList.remove('d-none'); };
    document.getElementById('uploadForm').onsubmit = async (e) => {
        e.preventDefault();
        const btn = document.getElementById('detectBtn'); btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Mendeteksi...';
        try {
            const res = await api.detection.upload(document.getElementById('imageInput').files[0]);
            document.getElementById('uploadResult').innerHTML = renderResult(res);
            document.getElementById('uploadResult').classList.remove('d-none');
        } catch (err) { showAlert(err.message, 'danger'); }
        btn.disabled = false; btn.innerHTML = '<i class="bi bi-search me-2"></i>Deteksi Objek';
    };
}

// ========== CAMERA ==========
let cameraStream = null;
function renderCamera(el) {
    el.innerHTML = `
    <div class="row justify-content-center"><div class="col-md-8">
      <div class="card shadow-sm border-0"><div class="card-body text-center p-4">
        <div class="camera-container position-relative">
          <video id="video" class="img-fluid rounded shadow-sm bg-dark" autoplay playsinline style="max-height:50vh;width:100%"></video>
          <canvas id="canvas" class="d-none"></canvas>
          <div id="cameraOverlay" class="d-flex align-items-center justify-content-center" style="position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);border-radius:.375rem">
            <div class="text-center text-white"><i class="bi bi-camera-video-off fs-1 d-block mb-2"></i><p class="mb-0">Kamera tidak aktif</p></div>
          </div>
        </div>
        <div class="mt-3 d-flex justify-content-center gap-2">
          <button class="btn btn-success" id="startCamera"><i class="bi bi-camera-video me-1"></i>Mulai Kamera</button>
          <button class="btn btn-danger d-none" id="captureBtn"><i class="bi bi-camera me-1"></i>Ambil Foto</button>
          <button class="btn btn-secondary d-none" id="stopCamera"><i class="bi bi-stop me-1"></i>Stop</button>
        </div>
      </div></div>
      <div id="cameraResult" class="mt-4 d-none"></div>
    </div></div>`;
    const video = document.getElementById('video'), canvas = document.getElementById('canvas'), overlay = document.getElementById('cameraOverlay');
    document.getElementById('startCamera').onclick = async () => {
        try { cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }); video.srcObject = cameraStream; overlay.classList.add('d-none'); document.getElementById('startCamera').classList.add('d-none'); document.getElementById('captureBtn').classList.remove('d-none'); document.getElementById('stopCamera').classList.remove('d-none'); } catch (e) { showAlert('Kamera tidak bisa diakses: '+e.message, 'danger'); }
    };
    document.getElementById('stopCamera').onclick = () => { if (cameraStream) cameraStream.getTracks().forEach(t => t.stop()); cameraStream = null; video.srcObject = null; overlay.classList.remove('d-none'); document.getElementById('startCamera').classList.remove('d-none'); document.getElementById('captureBtn').classList.add('d-none'); document.getElementById('stopCamera').classList.add('d-none'); };
    document.getElementById('captureBtn').onclick = async () => {
        canvas.width = video.videoWidth; canvas.height = video.videoHeight; canvas.getContext('2d').drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg');
        const btn = document.getElementById('captureBtn'); btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Memproses...';
        try {
            const res = await api.detection.detectFrame(imageData);
            document.getElementById('cameraResult').innerHTML = renderResult(res);
            document.getElementById('cameraResult').classList.remove('d-none');
            showAlert('Foto berhasil disimpan ke riwayat!');
        } catch (err) { showAlert(err.message, 'danger'); }
        btn.disabled = false; btn.innerHTML = '<i class="bi bi-camera me-1"></i>Ambil Foto';
    };
}

function renderResult(data) {
    return `<div class="card shadow-sm border-0"><div class="card-header bg-white d-flex justify-content-between align-items-center"><h6 class="mb-0 fw-bold"><i class="bi bi-search me-2"></i>Hasil Deteksi</h6></div>
      <div class="card-body text-center"><img src="${API_BASE}${data.image_url}" class="img-fluid rounded shadow-sm" style="max-height:400px">
      ${data.detected_objects?.length ? `<div class="mt-3 d-flex flex-wrap gap-2 justify-content-center">${data.detected_objects.map(o => `<span class="badge bg-primary fs-6 px-3 py-2">${o.label} <span class="bg-white bg-opacity-25 rounded px-1 ms-1">${(o.confidence*100).toFixed(1)}%</span></span>`).join('')}</div>` : '<div class="alert alert-info mt-3">Tidak ada objek terdeteksi</div>'}
      <div class="mt-3 d-flex flex-wrap justify-content-center gap-2">
        <button class="btn btn-primary" onclick="renderPage('history')"><i class="bi bi-clock-history me-1"></i>Lihat Riwayat</button>
        <button class="btn btn-outline-secondary" onclick="renderPage('${data.image_url?.includes('camera')?'camera':'upload'}')"><i class="bi bi-camera me-1"></i>Deteksi Lagi</button>
      </div></div></div>`;
}

// ========== HISTORY ==========
async function renderHistory(el) {
    el.innerHTML = `<div class="text-center py-5"><div class="spinner-border"></div></div>`;
    const dets = await api.detection.history();
    el.innerHTML = `
    <div class="card shadow-sm border-0"><div class="card-header bg-white d-flex justify-content-between align-items-center py-3"><h6 class="mb-0 fw-bold">Riwayat Deteksi</h6><span class="badge bg-primary">${dets.length} data</span></div>
      <div class="card-body"><div class="table-responsive"><table class="table table-hover datatable" id="historyTable"><thead class="table-light"><tr><th style="width:50px">ID</th><th>Gambar</th><th>Objek</th><th class="d-none d-sm-table-cell">Tanggal</th><th style="width:80px">Detail</th></tr></thead><tbody>${dets.map(d => `
        <tr><td class="fw-semibold" data-order="${d.id}">#${d.id}</td><td>${d.image_url?`<img src="${API_BASE}${d.image_url}" class="rounded" style="width:60px;height:60px;object-fit:cover;cursor:pointer" onclick="showHistoryModal(${JSON.stringify(d).replace(/"/g,'&quot;')})" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2260%22 height=%2260%22><rect fill=%22%23eee%22 width=%2260%22 height=%2260%22/><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22central%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2212%22>N/A</text></svg>'">`:'<span class="text-muted">-</span>'}</td>
        <td>${d.detected_objects.slice(0,3).map(o=>`<span class="badge bg-primary bg-opacity-10 text-primary me-1">${o.label}</span>`).join('')}${d.detected_objects.length>3?`<span class="badge bg-secondary">+${d.detected_objects.length-3}</span>`:''}</td>
        <td class="d-none d-sm-table-cell">${new Date(d.created_at).toLocaleString('id-ID')}</td>
        <td class="text-center"><button class="btn btn-outline-primary" onclick="showHistoryModal(${JSON.stringify(d).replace(/"/g,'&quot;')})"><i class="bi bi-eye"></i></button></td></tr>
      `).join('')}</tbody></table></div></div></div>`;
    if (dets.length) initDT('historyTable', 0);
}

function showHistoryModal(d) {
    const el = Object.assign(document.createElement('div'), { className:'modal fade', innerHTML:`<div class="modal-dialog modal-lg modal-dialog-centered"><div class="modal-content">
      <div class="modal-header"><h6 class="modal-title fw-bold"><i class="bi bi-image me-2"></i>Detail Deteksi #${d.id}</h6><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
      <div class="modal-body text-center"><img src="${API_BASE}${d.image_url}" class="img-fluid rounded" style="max-height:500px" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22><rect fill=%22%23eee%22 width=%22400%22 height=%22300%22/><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22central%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2216%22>N/A</text></svg>'">
        ${d.detected_objects?.length?`<div class="mt-3 text-start"><h6 class="fw-semibold">Objek Terdeteksi:</h6><div class="table-responsive"><table class="table table-sm table-bordered"><thead class="table-light"><tr><th>#</th><th>Label</th><th>Confidence</th></tr></thead><tbody>${d.detected_objects.map((o,i)=>`<tr><td>${i+1}</td><td><span class="badge bg-primary">${o.label}</span></td><td>${(o.confidence*100).toFixed(1)}%</td></tr>`).join('')}</tbody></table></div></div>`:'<div class="alert alert-info mt-3">Tidak ada objek terdeteksi</div>'}
      </div></div></div>` });
    el.addEventListener('hidden.bs.modal', () => el.remove());
    document.body.appendChild(el);
    bootstrap.Modal.getOrCreateInstance(el).show();
}

// ========== REPORTS ==========
async function renderReports(el) {
    el.innerHTML = `<div class="text-center py-5"><div class="spinner-border"></div></div>`;
    const dets = await api.reports.list();
    el.innerHTML = `
    <div class="card shadow-sm border-0"><div class="card-header bg-white d-flex justify-content-between align-items-center py-3"><h6 class="mb-0 fw-bold"><i class="bi bi-table me-2 text-primary"></i>Riwayat Deteksi</h6><div class="d-flex gap-2">
      <button class="btn btn-success" onclick="api.reports.exportExcel(document.getElementById('fStart').value,document.getElementById('fEnd').value)" title="Export Excel"><i class="bi bi-file-earmark-excel"></i><span class="d-none d-sm-inline ms-1">Excel</span></button>
      <button class="btn btn-danger" onclick="api.reports.exportPdf(document.getElementById('fStart').value,document.getElementById('fEnd').value)" title="Export PDF"><i class="bi bi-file-earmark-pdf"></i><span class="d-none d-sm-inline ms-1">PDF</span></button>
    </div></div>
      <div class="card-body">
        <div class="row mb-3 g-2"><div class="col-md-4"><label class="form-label small fw-semibold">Tanggal Mulai</label><input type="date" class="form-control form-control-sm" id="fStart"></div>
          <div class="col-md-4"><label class="form-label small fw-semibold">Tanggal Akhir</label><input type="date" class="form-control form-control-sm" id="fEnd"></div>
          <div class="col-md-4 d-flex align-items-end gap-2"><button class="btn btn-outline-primary btn-sm flex-fill" onclick="filterReports()"><i class="bi bi-funnel me-1"></i>Filter</button><button class="btn btn-outline-secondary btn-sm" onclick="resetFilter()"><i class="bi bi-arrow-counterclockwise me-1"></i>Reset</button></div>
        </div>
        <div class="table-responsive"><table class="table table-hover datatable" id="reportTable"><thead class="table-light"><tr><th style="width:50px">ID</th><th>Gambar</th><th>Objek</th><th class="d-none d-sm-table-cell">User</th><th>Tanggal</th></tr></thead><tbody>${dets.map(d => `
          <tr><td class="fw-semibold" data-order="${d.id}">#${d.id}</td><td>${d.image_url?`<img src="${API_BASE}${d.image_url}" class="rounded" style="width:50px;height:50px;object-fit:cover" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2250%22 height=%2250%22><rect fill=%22%23eee%22 width=%2250%22 height=%2250%22/><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22central%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2210%22>N/A</text></svg>'">`:'<span class="text-muted">-</span>'}</td>
          <td>${d.detected_objects.slice(0,3).map(o=>`<span class="badge bg-primary bg-opacity-10 text-primary me-1">${o.label}</span>`).join('')}${d.detected_objects.length>3?`<span class="badge bg-secondary">+${d.detected_objects.length-3}</span>`:''}</td>
          <td class="d-none d-sm-table-cell">${d.user||'-'}</td>
          <td>${new Date(d.created_at).toLocaleString('id-ID')}</td></tr>
        `).join('')}</tbody></table></div>
      </div></div>`;
    let dt;
    if (dets.length) dt = initDT('reportTable', 0);
    window.filterReports = () => {
        const start = document.getElementById('fStart').value, end = document.getElementById('fEnd').value;
        api.reports.list(start, end).then(data => {
            const tbody = document.querySelector('#reportTable tbody');
            tbody.innerHTML = data.map(d => `<tr><td class="fw-semibold" data-order="${d.id}">#${d.id}</td><td>${d.image_url?`<img src="${API_BASE}${d.image_url}" class="rounded" style="width:50px;height:50px;object-fit:cover">`:'<span class="text-muted">-</span>'}</td><td>${d.detected_objects.slice(0,3).map(o=>`<span class="badge bg-primary bg-opacity-10 text-primary me-1">${o.label}</span>`).join('')}${d.detected_objects.length>3?`<span class="badge bg-secondary">+${d.detected_objects.length-3}</span>`:''}</td><td class="d-none d-sm-table-cell">${d.user||'-'}</td><td>${new Date(d.created_at).toLocaleString('id-ID')}</td></tr>`).join('');
            if (dt) { dt.destroy(); dt = initDT('reportTable', 0); }
        });
    };
    window.resetFilter = () => { document.getElementById('fStart').value = ''; document.getElementById('fEnd').value = ''; window.filterReports(); };
}

function initDT(id, orderIdx) {
    return $('#'+id).DataTable({
        responsive: true,
        columnDefs: [{ responsivePriority: 1, targets: [0, id==='historyTable'?4:id==='reportTable'?2:1] }],
        language: { url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/id.json' },
        order: [[orderIdx, 'desc']]
    });
}

// INIT
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    renderPage(token ? 'dashboard' : 'login');
});
