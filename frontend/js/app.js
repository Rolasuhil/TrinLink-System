const API_BASE = '/api';

function getToken() {
    return localStorage.getItem('trainlink_token');
}

function getUser() {
    const u = localStorage.getItem('trainlink_user');
    return u ? JSON.parse(u) : null;
}

function setAuth(token, user) {
    localStorage.setItem('trainlink_token', token);
    localStorage.setItem('trainlink_user', JSON.stringify(user));
}

function logout() {
    localStorage.removeItem('trainlink_token');
    localStorage.removeItem('trainlink_user');
    window.location.href = '../public/02-login.html';
}

function authHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
    };
}

async function apiGet(url) {
    const res = await fetch(`${API_BASE}${url}`, { headers: authHeaders() });
    if (res.status === 401) { logout(); return null; }
    return await res.json();
}

async function apiPost(url, data) {
    const res = await fetch(`${API_BASE}${url}`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(data)
    });
    if (res.status === 401) { logout(); return null; }
    return await res.json();
}

async function apiPatch(url, data) {
    const res = await fetch(`${API_BASE}${url}`, {
        method: 'PATCH',
        headers: authHeaders(),
        body: JSON.stringify(data)
    });
    if (res.status === 401) { logout(); return null; }
    return await res.json();
}

async function apiDelete(url, data) {
    const res = await fetch(`${API_BASE}${url}`, {
        method: 'DELETE',
        headers: authHeaders(),
        body: data ? JSON.stringify(data) : undefined
    });
    if (res.status === 401) { logout(); return null; }
    return await res.json();
}

function showAlert(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `alert alert-${type}`;
    el.innerHTML = `<i class="ti ti-alert-circle"></i> ${msg}`;
    document.querySelector('.page-body')?.prepend(el);
    setTimeout(() => el.remove(), 5000);
}

function formatDate(d) {
    if (!d) return '';
    const date = new Date(d);
    return date.toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric' });
}

function getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2);
}

function requireAuth(types = []) {
    const user = getUser();
    if (!user) { window.location.href = '../public/02-login.html'; return false; }
    if (types.length > 0 && !types.includes(user.person_type)) {
        window.location.href = '../public/02-login.html';
        return false;
    }
    return true;
}

function renderSidebar(user) {
    const links = {
        trainee: [
            { section: 'الرئيسية', items: [
                { href: '08-trainee-dashboard.html', icon: 'ti-layout-dashboard', text: 'لوحة التحكم' },
            ]},
            { section: 'التدريب', items: [
                { href: '09-search.html', icon: 'ti-search', text: 'البحث والفرص' },
                { href: '11-my-applications.html', icon: 'ti-file-text', text: 'طلباتي' },
                { href: '17-attendance.html', icon: 'ti-calendar-check', text: 'الحضور والتقارير' },
            ]},
            { section: 'الأدوات', items: [
                { href: '13-ai-assistant.html', icon: 'ti-sparkles', text: 'المساعد الذكي' },
                { href: '14-community.html', icon: 'ti-users', text: 'المجتمع' },
                { href: '15-chat.html', icon: 'ti-message', text: 'الدردشة' },
            ]},
            { section: 'الحساب', items: [
                { href: '12-my-profile.html', icon: 'ti-user', text: 'الملف الشخصي' },
                { href: '16-notifications.html', icon: 'ti-bell', text: 'الإشعارات' },
            ]},
        ],
        company: [
            { section: 'الرئيسية', items: [
                { href: '18-company-dashboard.html', icon: 'ti-layout-dashboard', text: 'لوحة التحكم' },
            ]},
            { section: 'الفرص', items: [
                { href: '19-post-internship.html', icon: 'ti-plus', text: 'نشر فرصة' },
                { href: '20-manage-applications.html', icon: 'ti-file-text', text: 'إدارة الطلبات' },
                { href: '21-trainees-progress.html', icon: 'ti-chart-line', text: 'متابعة المتدربيين' },
            ]},
            { section: 'التواصل', items: [
                { href: '23-chat.html', icon: 'ti-message', text: 'الدردشة' },
            ]},
            { section: 'الحساب', items: [
                { href: '22-company-profile.html', icon: 'ti-building', text: 'ملف الشركة' },
                { href: '16-notifications.html', icon: 'ti-bell', text: 'الإشعارات' },
            ]},
        ],
        supervisor: [
            { section: 'الرئيسية', items: [
                { href: '24-supervisor-dashboard.html', icon: 'ti-layout-dashboard', text: 'لوحة التحكم' },
            ]},
            { section: 'المتابعة', items: [
                { href: '25-my-trainees.html', icon: 'ti-users', text: 'المتدربون' },
                { href: '26-progress-reports.html', icon: 'ti-chart-bar', text: 'التقارير' },
            ]},
            { section: 'التواصل', items: [
                { href: '27-chat.html', icon: 'ti-message', text: 'الدردشة' },
            ]},
        ],
        admin: [
            { section: 'الرئيسية', items: [
                { href: '28-admin-dashboard.html', icon: 'ti-layout-dashboard', text: 'لوحة التحكم' },
            ]},
            { section: 'الإدارة', items: [
                { href: '29-manage-users.html', icon: 'ti-users', text: 'المستخدمون' },
                { href: '30-manage-content.html', icon: 'ti-file-text', text: 'المحتوى' },
                { href: '31-reports-statistics.html', icon: 'ti-chart-bar', text: 'التقارير' },
                { href: '32-assign-trainee.html', icon: 'ti-link', text: 'ربط المتدربين' },
            ]},
        ],
    };

    const sections = links[user.person_type] || [];
    const pageName = window.location.pathname.split('/').pop();

    let html = `
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon"><i class="ti ti-briefcase"></i></div>
            <span class="sidebar-logo-text">TrainLink</span>
        </div>
        <div class="sidebar-nav">
    `;

    sections.forEach(s => {
        html += `<div class="sidebar-section"><div class="sidebar-section-title">${s.section}</div>`;
        s.items.forEach(item => {
            const active = pageName === item.href ? 'active' : '';
            html += `<a href="${item.href}" class="sidebar-link ${active}"><i class="${item.icon}"></i>${item.text}</a>`;
        });
        html += '</div>';
    });

    html += `
        </div>
        <div class="sidebar-user">
            <div class="sidebar-user-avatar">${getInitials(user.full_name)}</div>
            <div class="sidebar-user-info">
                <div class="sidebar-user-name">${user.full_name}</div>
                <div class="sidebar-user-type">${user.person_type === 'trainee' ? 'متدرب' : user.person_type === 'company' ? 'شركة' : user.person_type === 'supervisor' ? 'مشرف' : 'أدمن'}</div>
            </div>
            <button class="btn-icon btn-ghost" onclick="logout()" title="تسجيل الخروج"><i class="ti ti-logout"></i></button>
        </div>
    `;
    return html;
}

function initLayout(user) {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) sidebar.innerHTML = renderSidebar(user);
}
