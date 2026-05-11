/* Halo Blog — Admin Panel JS */

let token = localStorage.getItem('admin_token');
let currentPage = 'dashboard';

// ── Init ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    if (!token) {
        document.getElementById('login-modal').classList.add('show');
    } else {
        loadPage('dashboard');
    }

    // Nav clicks
    document.querySelectorAll('.admin-nav .nav-item').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const page = link.dataset.page;
            if (page) {
                loadPage(page);
                document.querySelectorAll('.admin-nav .nav-item').forEach(n => n.classList.remove('active'));
                link.classList.add('active');
            } else {
                window.open(link.href, '_blank');
            }
        });
    });
});

// ── Auth ────────────────────────────────────────────
async function doLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-user').value;
    const password = document.getElementById('login-pass').value;

    const res = await fetch('/admin/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('admin_token', token);
        document.getElementById('login-modal').classList.remove('show');
        loadPage('dashboard');
    } else {
        alert('登录失败，请检查用户名和密码');
    }
    return false;
}

function logout() {
    token = null;
    localStorage.removeItem('admin_token');
    location.reload();
}

function authHeaders() {
    return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
}

// ── Page Router ─────────────────────────────────────
async function loadPage(page) {
    currentPage = page;
    const content = document.getElementById('admin-content');
    const title = document.getElementById('page-title');

    const titles = {
        dashboard: '仪表盘', posts: '文章管理', editor: '写文章',
        categories: '分类管理', tags: '标签管理', comments: '评论管理', links: '友链管理', profile: '个人信息',
    };
    title.textContent = titles[page] || page;
    content.innerHTML = '<div class="loading">加载中...</div>';

    switch (page) {
        case 'dashboard': await renderDashboard(content); break;
        case 'posts': await renderPosts(content); break;
        case 'editor': renderEditor(content); break;
        case 'categories': await renderCategories(content); break;
        case 'tags': await renderTags(content); break;
        case 'comments': await renderComments(content); break;
        case 'links': await renderLinks(content); break;
        case 'profile': await renderProfile(content); break;
    }
}

// ── Dashboard ───────────────────────────────────────
async function renderDashboard(el) {
    const res = await fetch('/admin/api/dashboard', { headers: authHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    const s = data.stats;

    el.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">文章总数</div><div class="stat-value">${s.posts}</div></div>
            <div class="stat-card"><div class="stat-label">已发布</div><div class="stat-value">${s.published}</div></div>
            <div class="stat-card"><div class="stat-label">评论总数</div><div class="stat-value">${s.comments}</div></div>
            <div class="stat-card"><div class="stat-label">待审评论</div><div class="stat-value" style="color:${s.pending_comments > 0 ? '#d97706' : 'inherit'}">${s.pending_comments}</div></div>
            <div class="stat-card"><div class="stat-label">分类</div><div class="stat-value">${s.categories}</div></div>
            <div class="stat-card"><div class="stat-label">标签</div><div class="stat-value">${s.tags}</div></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div class="admin-table">
                <h3 style="padding:16px;">最近文章</h3>
                <table><tbody>
                    ${data.recent_posts.map(p => `<tr><td>${p.title}</td><td><span class="badge badge-${p.status}">${p.status}</span></td></tr>`).join('')}
                </tbody></table>
            </div>
            <div class="admin-table">
                <h3 style="padding:16px;">最近评论</h3>
                <table><tbody>
                    ${data.recent_comments.map(c => `<tr><td><strong>${c.author_name}</strong>: ${c.content}</td><td><span class="badge badge-${c.is_approved ? 'approved' : 'pending'}">${c.is_approved ? '已通过' : '待审'}</span></td></tr>`).join('')}
                </tbody></table>
            </div>
        </div>
    `;
}

// ── Posts ────────────────────────────────────────────
let postsPage = 1;
async function renderPosts(el, page = 1) {
    postsPage = page;
    const res = await fetch(`/admin/api/posts?page=${page}&page_size=15`, { headers: authHeaders() });
    const data = await res.json();

    el.innerHTML = `
        <div class="toolbar">
            <div class="toolbar-left">
                <input class="search-input" placeholder="搜索文章..." onkeyup="if(event.key==='Enter')searchPosts(this.value)">
            </div>
            <button class="btn btn-primary" onclick="loadPage('editor')">✏️ 写文章</button>
        </div>
        <div class="admin-table">
            <table>
                <thead><tr>
                    <th>标题</th><th>状态</th><th>分类</th><th>标签</th><th>浏览</th><th>发布时间</th><th>操作</th>
                </tr></thead>
                <tbody>
                    ${data.items.map(p => `<tr>
                        <td><a href="/post/${p.slug}" target="_blank">${p.title}</a></td>
                        <td><span class="badge badge-${p.status}">${p.status === 'published' ? '已发布' : '草稿'}</span></td>
                        <td>${p.category ? p.category.name : '-'}</td>
                        <td>${p.tags.map(t => t.name).join(', ') || '-'}</td>
                        <td>${p.views}</td>
                        <td>${p.published_at ? formatDate(p.published_at) : '-'}</td>
                        <td class="action-btns">
                            <button class="action-btn" onclick="editPost(${p.id})">编辑</button>
                            <button class="action-btn danger" onclick="deletePost(${p.id})">删除</button>
                        </td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>
        ${data.total_pages > 1 ? `<div class="pagination" style="margin-top:16px;">
            ${page > 1 ? `<button onclick="renderPosts(document.getElementById('admin-content'),${page-1})">← 上一页</button>` : ''}
            <span>${page} / ${data.total_pages}</span>
            ${page < data.total_pages ? `<button onclick="renderPosts(document.getElementById('admin-content'),${page+1})">下一页 →</button>` : ''}
        </div>` : ''}
    `;
}

async function searchPosts(q) {
    const el = document.getElementById('admin-content');
    const res = await fetch(`/admin/api/posts?q=${encodeURIComponent(q)}`, { headers: authHeaders() });
    const data = await res.json();
    // Reuse renderPosts table logic
    renderPosts(el, 1);
}

async function editPost(id) {
    const res = await fetch(`/admin/api/posts/${id}`, { headers: authHeaders() });
    const post = await res.json();
    loadPage('editor');
    setTimeout(() => fillEditor(post), 100);
}

async function deletePost(id) {
    if (!confirm('确定删除这篇文章？')) return;
    const res = await fetch(`/admin/api/posts/${id}`, { method: 'DELETE', headers: authHeaders() });
    if (res.ok) {
        toast('文章已删除');
        renderPosts(document.getElementById('admin-content'), postsPage);
    }
}

// ── Editor ───────────────────────────────────────────
let editingPostId = null;

function renderEditor(el) {
    editingPostId = null;
    el.innerHTML = `
        <div class="toolbar">
            <div class="toolbar-left">
                <button class="btn" onclick="loadPage('posts')">← 返回列表</button>
                <button class="btn btn-primary" onclick="savePost()">💾 保存</button>
                <button class="btn" onclick="savePost('published')">📤 发布</button>
            </div>
        </div>
        <div class="form-group">
            <label>标题</label>
            <input id="ep-title" placeholder="文章标题">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Slug (URL)</label>
                <input id="ep-slug" placeholder="article-url-slug">
            </div>
            <div class="form-group">
                <label>分类</label>
                <select id="ep-category"><option value="">无分类</option></select>
            </div>
        </div>
        <div class="form-group">
            <label>摘要</label>
            <input id="ep-summary" placeholder="文章摘要（可选）">
        </div>
        <div class="form-group">
            <label>标签</label>
            <div id="ep-tags-container" style="display:flex;flex-wrap:wrap;gap:8px;padding:8px;background:var(--bg-card);border:1px solid var(--border);border-radius:8px;min-height:36px;"></div>
            <small style="color:var(--text-secondary);margin-top:4px;display:block;">点击标签选中/取消</small>
        </div>
        <div class="editor-layout">
            <div class="editor-input">
                <label style="font-weight:600;margin-bottom:8px;display:block;">Markdown 编辑器</label>
                <textarea id="ep-content" placeholder="在此输入 Markdown 内容..." oninput="updatePreview()"></textarea>
            </div>
            <div class="editor-preview markdown-body" id="ep-preview">
                <p style="color:var(--text-secondary);">预览区域</p>
            </div>
        </div>
    `;
    loadCategoriesForSelect();
    loadTagsForSelect();
}

async function loadTagsForSelect(selectedIds = []) {
    const res = await fetch('/admin/api/tags', { headers: authHeaders() });
    const tags = await res.json();
    const container = document.getElementById('ep-tags-container');
    if (!container) return;
    container.innerHTML = tags.map(t => `
        <span class="tag-chip ${selectedIds.includes(t.id) ? 'selected' : ''}" data-id="${t.id}"
            style="padding:4px 12px;border-radius:16px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;
            background:${selectedIds.includes(t.id) ? 'var(--primary)' : 'var(--bg-main)'};
            color:${selectedIds.includes(t.id) ? '#fff' : 'var(--text-primary)'};
            border:1px solid ${selectedIds.includes(t.id) ? 'var(--primary)' : 'var(--border)'};"
            onclick="this.classList.toggle('selected');this.style.background=this.classList.contains('selected')?'var(--primary)':'var(--bg-main)';this.style.color=this.classList.contains('selected')?'#fff':'var(--text-primary)';this.style.borderColor=this.classList.contains('selected')?'var(--primary)':'var(--border)';"
        >${t.name}</span>
    `).join('');
}

function getSelectedTagIds() {
    return Array.from(document.querySelectorAll('#ep-tags-container .tag-chip.selected')).map(el => parseInt(el.dataset.id));
}

function fillEditor(post) {
    editingPostId = post.id;
    document.getElementById('ep-title').value = post.title;
    document.getElementById('ep-slug').value = post.slug;
    document.getElementById('ep-summary').value = post.summary || '';
    document.getElementById('ep-content').value = post.content || '';
    if (post.category_id) document.getElementById('ep-category').value = post.category_id;
    loadTagsForSelect(post.tags ? post.tags.map(t => t.id) : []);
    updatePreview();
}

async function loadCategoriesForSelect() {
    const res = await fetch('/admin/api/categories', { headers: authHeaders() });
    const cats = await res.json();
    const select = document.getElementById('ep-category');
    cats.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.name;
        select.appendChild(opt);
    });
}

function updatePreview() {
    const content = document.getElementById('ep-content').value;
    // Simple markdown → HTML (client-side preview)
    let html = content
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    document.getElementById('ep-preview').innerHTML = html;
}

async function savePost(status) {
    const title = document.getElementById('ep-title').value.trim();
    const content = document.getElementById('ep-content').value.trim();
    if (!title) return toast('请输入标题', 'error');

    let slug = document.getElementById('ep-slug').value.trim();
    if (!slug) slug = title.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-').replace(/^-|-$/g, '');

    const data = {
        title, slug,
        summary: document.getElementById('ep-summary').value,
        content,
        status: status || 'draft',
        category_id: document.getElementById('ep-category').value || null,
        tag_ids: getSelectedTagIds(),
    };

    const url = editingPostId ? `/admin/api/posts/${editingPostId}` : '/admin/api/posts';
    const method = editingPostId ? 'PUT' : 'POST';

    const res = await fetch(url, {
        method, headers: authHeaders(),
        body: JSON.stringify(data),
    });

    if (res.ok) {
        toast(editingPostId ? '文章已更新' : '文章已保存');
        loadPage('posts');
    } else {
        const err = await res.json();
        toast(err.detail || '保存失败', 'error');
    }
}

// ── Categories ───────────────────────────────────────
async function renderCategories(el) {
    const res = await fetch('/admin/api/categories', { headers: authHeaders() });
    const cats = await res.json();

    el.innerHTML = `
        <div class="toolbar">
            <button class="btn btn-primary" onclick="showAddCategory()">➕ 新增分类</button>
        </div>
        <div class="admin-table">
            <table>
                <thead><tr><th>名称</th><th>Slug</th><th>描述</th><th>文章数</th><th>操作</th></tr></thead>
                <tbody>
                    ${cats.map(c => `<tr>
                        <td>${c.name}</td><td>${c.slug}</td><td>${c.description || '-'}</td><td>${c.post_count}</td>
                        <td class="action-btns"><button class="action-btn danger" onclick="deleteCategory(${c.id})">删除</button></td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>
        <div id="cat-form" style="display:none;margin-top:16px;" class="admin-table">
            <div style="padding:20px;">
                <h3 style="margin-bottom:12px;">新增分类</h3>
                <div class="form-row">
                    <div class="form-group"><label>名称</label><input id="cat-name" placeholder="分类名称"></div>
                    <div class="form-group"><label>Slug</label><input id="cat-slug" placeholder="category-slug"></div>
                </div>
                <div class="form-group"><label>描述</label><input id="cat-desc" placeholder="分类描述"></div>
                <button class="btn btn-primary" onclick="addCategory()">保存</button>
            </div>
        </div>
    `;
}

function showAddCategory() { document.getElementById('cat-form').style.display = 'block'; }

async function addCategory() {
    const name = document.getElementById('cat-name').value.trim();
    let slug = document.getElementById('cat-slug').value.trim();
    if (!name) { toast('请输入分类名称', 'error'); return; }
    if (!slug) {
        // 自动生成 slug：中文转拼音风格，英文小写
        slug = name.toLowerCase()
            .replace(/[\u4e00-\u9fff]+/g, m => m) // 保留中文
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-|-$/g, '') || 'category-' + Date.now();
    }

    try {
        const res = await fetch('/admin/api/categories', {
            method: 'POST', headers: authHeaders(),
            body: JSON.stringify({ name, slug, description: document.getElementById('cat-desc').value }),
        });
        if (res.ok) {
            toast('分类已创建');
            renderCategories(document.getElementById('admin-content'));
        } else {
            const err = await res.json();
            toast(err.detail || '创建失败', 'error');
        }
    } catch (e) {
        toast('网络错误，请重试', 'error');
        console.error(e);
    }
}

async function deleteCategory(id) {
    if (!confirm('确定删除此分类？')) return;
    await fetch(`/admin/api/categories/${id}`, { method: 'DELETE', headers: authHeaders() });
    toast('分类已删除');
    renderCategories(document.getElementById('admin-content'));
}

// ── Tags ─────────────────────────────────────────────
async function renderTags(el) {
    const res = await fetch('/admin/api/tags', { headers: authHeaders() });
    const tags = await res.json();

    el.innerHTML = `
        <div class="toolbar">
            <div class="toolbar-left">
                <input id="tag-name" class="search-input" placeholder="标签名称">
                <input id="tag-slug" class="search-input" placeholder="tag-slug" style="width:180px">
                <button class="btn btn-primary" onclick="addTag()">➕ 添加</button>
            </div>
        </div>
        <div class="admin-table">
            <table>
                <thead><tr><th>名称</th><th>Slug</th><th>操作</th></tr></thead>
                <tbody>
                    ${tags.map(t => `<tr>
                        <td>${t.name}</td><td>${t.slug}</td>
                        <td class="action-btns"><button class="action-btn danger" onclick="deleteTag(${t.id})">删除</button></td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function addTag() {
    const name = document.getElementById('tag-name').value.trim();
    let slug = document.getElementById('tag-slug').value.trim();
    if (!name) return toast('请输入标签名称', 'error');
    if (!slug) slug = name.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fff]+/g, '-');

    await fetch('/admin/api/tags', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ name, slug }),
    });
    toast('标签已添加');
    renderTags(document.getElementById('admin-content'));
}

async function deleteTag(id) {
    if (!confirm('确定删除此标签？')) return;
    await fetch(`/admin/api/tags/${id}`, { method: 'DELETE', headers: authHeaders() });
    toast('标签已删除');
    renderTags(document.getElementById('admin-content'));
}

// ── Comments ─────────────────────────────────────────
let commentsPage = 1;
async function renderComments(el, page = 1) {
    commentsPage = page;
    const res = await fetch(`/admin/api/comments?page=${page}`, { headers: authHeaders() });
    const data = await res.json();

    el.innerHTML = `
        <div class="admin-table">
            <table>
                <thead><tr><th>作者</th><th>内容</th><th>状态</th><th>时间</th><th>操作</th></tr></thead>
                <tbody>
                    ${data.items.map(c => `<tr>
                        <td><strong>${c.author_name}</strong><br><small>${c.author_email || ''}</small></td>
                        <td>${c.content.slice(0, 80)}${c.content.length > 80 ? '...' : ''}</td>
                        <td><span class="badge badge-${c.is_approved ? 'approved' : 'pending'}">${c.is_approved ? '已通过' : '待审核'}</span></td>
                        <td>${formatDate(c.created_at)}</td>
                        <td class="action-btns">
                            ${!c.is_approved ? `<button class="action-btn" onclick="approveComment(${c.id})">✅ 通过</button>` : ''}
                            <button class="action-btn danger" onclick="deleteComment(${c.id})">删除</button>
                        </td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function approveComment(id) {
    await fetch(`/admin/api/comments/${id}/approve`, { method: 'PUT', headers: authHeaders() });
    toast('评论已通过');
    renderComments(document.getElementById('admin-content'), commentsPage);
}

async function deleteComment(id) {
    if (!confirm('确定删除此评论？')) return;
    await fetch(`/admin/api/comments/${id}`, { method: 'DELETE', headers: authHeaders() });
    toast('评论已删除');
    renderComments(document.getElementById('admin-content'), commentsPage);
}

// ── Links ────────────────────────────────────────────
async function renderLinks(el) {
    const res = await fetch('/admin/api/links', { headers: authHeaders() });
    const links = await res.json();

    el.innerHTML = `
        <div class="toolbar">
            <button class="btn btn-primary" onclick="showAddLink()">➕ 新增友链</button>
        </div>
        <div class="admin-table">
            <table>
                <thead><tr><th>名称</th><th>URL</th><th>描述</th><th>排序</th><th>可见</th><th>操作</th></tr></thead>
                <tbody>
                    ${links.map(l => `<tr>
                        <td>${l.name}</td><td><a href="${l.url}" target="_blank">${l.url}</a></td>
                        <td>${l.description || '-'}</td><td>${l.sort_order}</td>
                        <td>${l.is_visible ? '✅' : '❌'}</td>
                        <td class="action-btns"><button class="action-btn danger" onclick="deleteLink(${l.id})">删除</button></td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>
        <div id="link-form" style="display:none;margin-top:16px;" class="admin-table">
            <div style="padding:20px;">
                <h3 style="margin-bottom:12px;">新增友链</h3>
                <div class="form-row">
                    <div class="form-group"><label>名称</label><input id="link-name" placeholder="网站名称"></div>
                    <div class="form-group"><label>URL</label><input id="link-url" placeholder="https://..."></div>
                </div>
                <div class="form-group"><label>描述</label><input id="link-desc" placeholder="简短描述"></div>
                <button class="btn btn-primary" onclick="addLink()">保存</button>
            </div>
        </div>
    `;
}

function showAddLink() { document.getElementById('link-form').style.display = 'block'; }

async function addLink() {
    const name = document.getElementById('link-name').value.trim();
    const url = document.getElementById('link-url').value.trim();
    if (!name || !url) return toast('请填写名称和URL', 'error');

    await fetch('/admin/api/links', {
        method: 'POST', headers: authHeaders(),
        body: JSON.stringify({ name, url, description: document.getElementById('link-desc').value }),
    });
    toast('友链已添加');
    renderLinks(document.getElementById('admin-content'));
}

async function deleteLink(id) {
    if (!confirm('确定删除此友链？')) return;
    await fetch(`/admin/api/links/${id}`, { method: 'DELETE', headers: authHeaders() });
    toast('友链已删除');
    renderLinks(document.getElementById('admin-content'));
}

// ── Utilities ────────────────────────────────────────
function formatDate(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function toast(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

// ── Profile ──────────────────────────────────────────
async function renderProfile(el) {
    const res = await fetch('/admin/api/profile', { headers: authHeaders() });
    if (!res.ok) { toast('加载失败', 'error'); return; }
    const user = await res.json();

    el.innerHTML = `
        <div style="max-width:600px;">
            <div class="admin-table">
                <div style="padding:24px;">
                    <h3 style="margin-bottom:20px;">👤 个人信息</h3>
                    <div class="form-group">
                        <label>用户名</label>
                        <input id="prof-username" value="${user.username}" disabled style="opacity:0.6;">
                        <small style="color:var(--text-secondary);">用户名不可修改</small>
                    </div>
                    <div class="form-group">
                        <label>显示名称</label>
                        <input id="prof-displayname" value="${user.display_name || ''}" placeholder="用于前端展示">
                    </div>
                    <div class="form-group">
                        <label>邮箱</label>
                        <input id="prof-email" type="email" value="${user.email || ''}" placeholder="your@email.com">
                    </div>
                    <div class="form-group">
                        <label>头像 URL</label>
                        <input id="prof-avatar" value="${user.avatar || ''}" placeholder="https://example.com/avatar.jpg">
                        ${user.avatar ? `<div style="margin-top:8px;"><img src="${user.avatar}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;"></div>` : ''}
                    </div>
                    <button class="btn btn-primary" onclick="saveProfile()">保存资料</button>
                </div>
            </div>

            <div class="admin-table" style="margin-top:20px;">
                <div style="padding:24px;">
                    <h3 style="margin-bottom:20px;">🔒 修改密码</h3>
                    <div class="form-group">
                        <label>当前密码</label>
                        <input id="prof-old-pass" type="password" placeholder="输入当前密码">
                    </div>
                    <div class="form-group">
                        <label>新密码</label>
                        <input id="prof-new-pass" type="password" placeholder="至少 6 位">
                    </div>
                    <div class="form-group">
                        <label>确认新密码</label>
                        <input id="prof-confirm-pass" type="password" placeholder="再次输入新密码">
                    </div>
                    <button class="btn btn-primary" onclick="changePassword()">修改密码</button>
                </div>
            </div>

            <div style="margin-top:16px;padding:16px;background:var(--bg-card);border-radius:8px;font-size:0.85rem;color:var(--text-secondary);">
                注册时间：${formatDate(user.created_at)} | 角色：${user.role}
            </div>
        </div>
    `;
}

async function saveProfile() {
    const data = {
        display_name: document.getElementById('prof-displayname').value.trim(),
        email: document.getElementById('prof-email').value.trim(),
        avatar: document.getElementById('prof-avatar').value.trim(),
    };
    try {
        const res = await fetch('/admin/api/profile', {
            method: 'PUT', headers: authHeaders(),
            body: JSON.stringify(data),
        });
        if (res.ok) { toast('资料已更新'); }
        else { const err = await res.json(); toast(err.detail || '更新失败', 'error'); }
    } catch (e) { toast('网络错误', 'error'); }
}

async function changePassword() {
    const oldPass = document.getElementById('prof-old-pass').value;
    const newPass = document.getElementById('prof-new-pass').value;
    const confirmPass = document.getElementById('prof-confirm-pass').value;
    if (!oldPass || !newPass) { toast('请填写密码', 'error'); return; }
    if (newPass !== confirmPass) { toast('两次密码不一致', 'error'); return; }
    if (newPass.length < 6) { toast('密码至少 6 位', 'error'); return; }
    try {
        const res = await fetch('/admin/api/profile/password', {
            method: 'PUT', headers: authHeaders(),
            body: JSON.stringify({ old_password: oldPass, new_password: newPass }),
        });
        if (res.ok) {
            toast('密码已修改，需重新登录');
            setTimeout(() => { localStorage.removeItem('admin_token'); location.reload(); }, 1500);
        } else { const err = await res.json(); toast(err.detail || '修改失败', 'error'); }
    } catch (e) { toast('网络错误', 'error'); }
}
