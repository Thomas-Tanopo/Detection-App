const API_BASE = localStorage.getItem('api_base') || window.API_BASE || 'http://localhost:8000';

async function apiFetch(path, options = {}) {
    const token = localStorage.getItem('token');
    const headers = { ...options.headers };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
    const res = await fetch(API_BASE + path, { ...options, headers });
    if (res.status === 401) { localStorage.removeItem('token'); localStorage.removeItem('user'); window.renderPage('login'); return null; }
    if (options.raw) return res;
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Error');
    return data;
}

const api = {
    login: (u, p) => apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify({ username: u, password: p }) }),
    register: (d) => apiFetch('/api/auth/register', { method: 'POST', body: JSON.stringify(d) }),
    me: () => apiFetch('/api/auth/me'),
    categories: {
        list: () => apiFetch('/api/categories'),
        get: (id) => apiFetch('/api/categories/' + id),
        create: (d) => apiFetch('/api/categories', { method: 'POST', body: JSON.stringify(d) }),
        update: (id, d) => apiFetch('/api/categories/' + id, { method: 'PUT', body: JSON.stringify(d) }),
        delete: (id) => apiFetch('/api/categories/' + id, { method: 'DELETE' }),
    },
    items: {
        list: () => apiFetch('/api/items'),
        get: (id) => apiFetch('/api/items/' + id),
        create: (d) => apiFetch('/api/items', { method: 'POST', body: JSON.stringify(d) }),
        update: (id, d) => apiFetch('/api/items/' + id, { method: 'PUT', body: JSON.stringify(d) }),
        delete: (id) => apiFetch('/api/items/' + id, { method: 'DELETE' }),
    },
    detection: {
        upload: (file) => { const fd = new FormData(); fd.append('file', file); return apiFetch('/api/detection/upload', { method: 'POST', body: fd }); },
        detectFrame: (image) => apiFetch('/api/detection/detect-frame', { method: 'POST', body: JSON.stringify({ image }) }),
        history: () => apiFetch('/api/detection/history'),
    },
    dashboard: {
        stats: () => apiFetch('/api/dashboard/stats'),
        trend: () => apiFetch('/api/dashboard/trend'),
        topLabels: () => apiFetch('/api/dashboard/top-labels'),
        recent: () => apiFetch('/api/dashboard/recent'),
    },
    reports: {
        list: (s, e) => apiFetch(`/api/reports?start_date=${s || ''}&end_date=${e || ''}`),
        exportExcel: async (s, e) => {
            const res = await apiFetch(`/api/reports/export/excel?start_date=${s || ''}&end_date=${e || ''}`, { raw: true });
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = 'laporan_deteksi.xlsx'; a.click();
            URL.revokeObjectURL(url);
        },
        exportPdf: async (s, e) => {
            const res = await apiFetch(`/api/reports/export/pdf?start_date=${s || ''}&end_date=${e || ''}`, { raw: true });
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = 'laporan_deteksi.pdf'; a.click();
            URL.revokeObjectURL(url);
        },
    }
};
