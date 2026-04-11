DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BOS-ETMALL 訂單後台</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f6f9fc;
    color: #061b31;
    min-height: 100vh;
    display: flex;
    font-weight: 300;
  }

  /* ── Sidebar ── */
  .sidebar {
    width: 220px;
    min-height: 100vh;
    background: #ffffff;
    border-right: 1px solid #e5edf5;
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0; left: 0;
    z-index: 200;
    box-shadow: none;
  }

  .sidebar-logo {
    padding: 20px 18px 16px;
    border-bottom: 1px solid #e5edf5;
    display: flex; align-items: center; gap: 10px;
  }

  .logo-mark {
    width: 28px; height: 28px; background: #533afd;
    border-radius: 6px; display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .logo-mark svg { width: 15px; height: 15px; fill: white; }

  .logo-text {
    font-size: 13px; font-weight: 600; color: #061b31;
    letter-spacing: -0.3px; line-height: 1.2;
  }
  .logo-sub { font-size: 10px; color: #64748d; font-weight: 400; margin-top: 1px; }

  /* Nav */
  .nav-section {
    padding: 12px 10px 6px;
  }
  .nav-label {
    font-size: 10px; font-weight: 500; color: #64748d;
    text-transform: uppercase; letter-spacing: 0.8px;
    padding: 0 8px; margin-bottom: 4px;
  }

  .nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 10px;
    border-radius: 5px;
    font-size: 13px; font-weight: 400; color: #273951;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.15s;
    margin-bottom: 1px;
  }
  .nav-item:hover { background: #f6f9fc; color: #533afd; }
  .nav-item.active {
    background: rgba(83,58,253,0.08);
    color: #533afd;
    font-weight: 500;
  }
  .nav-icon {
    width: 16px; height: 16px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    opacity: 0.7;
  }
  .nav-item.active .nav-icon { opacity: 1; }

  .sidebar-footer {
    margin-top: auto;
    padding: 16px 18px;
    border-top: 1px solid #e5edf5;
  }
  .status-pill {
    display: flex; align-items: center; gap: 7px;
    padding: 7px 10px;
    border-radius: 5px;
    background: rgba(21,190,83,0.08);
    border: 1px solid rgba(21,190,83,0.25);
    font-size: 12px; color: #108c3d; font-weight: 400;
  }
  .status-pill.offline { background: rgba(234,34,97,0.08); border-color: rgba(234,34,97,0.25); color: #c41e5a; }
  .status-dot { width: 6px; height: 6px; border-radius: 50%; background: #15be53; flex-shrink: 0; animation: blink 2s infinite; }
  .status-pill.offline .status-dot { background: #ea2261; animation: none; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }
  .status-info { flex: 1; }
  .status-label { font-size: 11px; color: #64748d; margin-top: 1px; }

  /* ── Main ── */
  .main {
    margin-left: 220px;
    flex: 1;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .topbar {
    background: #ffffff;
    border-bottom: 1px solid #e5edf5;
    padding: 0 28px;
    height: 52px;
    display: flex; align-items: center; justify-content: space-between;
    
  }
  .topbar-title { font-size: 14px; font-weight: 500; color: #061b31; letter-spacing: -0.2px; }
  .topbar-right { display: flex; align-items: center; gap: 16px; }
  .last-update { font-size: 12px; color: #64748d; }
  .refresh-btn {
    background: transparent; border: 1px solid #e5edf5;
    color: #64748d; padding: 5px 12px; border-radius: 4px;
    font-size: 12px; font-family: inherit; font-weight: 400;
    cursor: pointer; transition: all 0.15s;
  }
  .refresh-btn:hover { border-color: #533afd; color: #533afd; background: rgba(83,58,253,0.04); }

  .content { padding: 28px; }

  /* Stats */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 24px;
  }

  .stat-card {
    background: #ffffff;
    border: 1px solid #e5edf5;
    border-radius: 6px;
    padding: 18px 20px;
  }
  .stat-label { font-size: 11px; font-weight: 500; color: #64748d; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
  .stat-value { font-size: 28px; font-weight: 300; color: #061b31; letter-spacing: -0.8px; font-variant-numeric: tabular-nums; line-height: 1; margin-bottom: 5px; }
  .stat-sub { font-size: 12px; color: #64748d; }
  .stat-card.accent .stat-value { color: #533afd; }
  .stat-card.success .stat-value { color: #108c3d; }

  /* Panels */
  .panel {
    background: #ffffff;
    border: 1px solid #e5edf5;
    border-radius: 6px;
    margin-bottom: 20px;
    overflow: hidden;
  }
  .panel-header {
    padding: 14px 20px;
    border-bottom: 1px solid #e5edf5;
    display: flex; justify-content: space-between; align-items: center;
    background: #fafcff;
  }
  .panel-title { font-size: 13px; font-weight: 500; color: #061b31; }

  /* Table */
  table { width: 100%; border-collapse: collapse; }
  th {
    padding: 9px 14px;
    text-align: left;
    font-size: 11px; font-weight: 500; color: #64748d;
    text-transform: uppercase; letter-spacing: 0.6px;
    border-bottom: 1px solid #e5edf5;
    background: #f8fafc;
  }
  td {
    padding: 11px 14px;
    font-size: 13px; color: #273951;
    border-bottom: 1px solid #f0f5fa;
    font-weight: 400;
  }
  tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: #f8fafc; }

  .amount { font-weight: 500; color: #061b31; font-variant-numeric: tabular-nums; letter-spacing: -0.2px; }
  .order-id { font-family: 'SFMono-Regular', monospace; font-size: 11px; color: #533afd; }

  .badge { display: inline-flex; align-items: center; padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 400; }
  .badge-success { background: rgba(21,190,83,0.12); color: #108c3d; border: 1px solid rgba(21,190,83,0.3); }
  .badge-neutral { background: #f6f9fc; color: #64748d; border: 1px solid #e5edf5; }

  .empty { text-align: center; padding: 48px; color: #64748d; font-size: 13px; }

  /* Stores */
  .stores-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
    padding: 18px;
  }
  .store-card {
    background: #f8fafc; border: 1px solid #e5edf5; border-radius: 5px;
    padding: 12px 14px; text-align: center; transition: all 0.15s;
  }
  .store-card:hover { background: #fff; }
  .store-name { font-size: 12px; color: #64748d; margin-bottom: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .store-count { font-size: 20px; font-weight: 300; color: #533afd; font-variant-numeric: tabular-nums; letter-spacing: -0.4px; }
  .store-amount { font-size: 11px; color: #64748d; margin-top: 2px; }

  /* Settings & Health view */
  .settings-view, .health-view { padding: 28px; display: none; }
  .settings-card, .health-card {
    background: #fff; border: 1px solid #e5edf5; border-radius: 6px;
    padding: 28px;
    max-width: 560px;
  }
  .health-status { font-size: 36px; font-weight: 300; color: #108c3d; margin-bottom: 8px; }
  .health-time { font-size: 13px; color: #64748d; }
  .health-url { font-family: monospace; font-size: 12px; color: #533afd; margin-top: 16px; display: block; }

  @media (max-width: 900px) {
    .sidebar { width: 60px; }
    .logo-text, .logo-sub, .nav-label, .nav-item span, .status-info { display: none; }
    .sidebar-logo { justify-content: center; padding: 16px; }
    .nav-item { justify-content: center; }
    .sidebar-footer { padding: 12px; }
    .main { margin-left: 60px; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
  }
</style>
</head>
<body>

<!-- Sidebar -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-mark">
      <svg viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
    </div>
    <div>
      <div class="logo-text">BOS-ETMALL</div>
      <div class="logo-sub">訂單管理後台</div>
    </div>
  </div>

  <nav style="flex:1;padding-top:8px;">
    <div class="nav-section">
      <div class="nav-label">主選單</div>
      <a class="nav-item active" onclick="showView('dashboard')">
        <span class="nav-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
        </span>
        <span>監控儀表板</span>
      </a>
      <a class="nav-item" onclick="showView('health')">
        <span class="nav-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </span>
        <span>健康檢查</span>
      </a>
      <a class="nav-item" onclick="showView('settings')">
        <span class="nav-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </span>
        <span>設定</span>
      </a>
    </div>
    <div class="nav-section">
      <div class="nav-label">開發者</div>
      <a class="nav-item" href="/docs" target="_blank">
        <span class="nav-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
        </span>
        <span>API 文件</span>
      </a>
    </div>
  </nav>

  <div class="sidebar-footer">
    <div class="status-pill" id="sidebarStatus">
      <div class="status-dot" id="sidebarDot"></div>
      <div class="status-info">
        <div id="sidebarStatusText">連線中</div>
        <div class="status-label" id="sidebarTime"></div>
      </div>
    </div>
  </div>
</aside>

<!-- Main content -->
<div class="main">
  <div class="topbar">
    <span class="topbar-title" id="pageTitle">監控儀表板</span>
    <div class="topbar-right">
      <span class="last-update" id="lastUpdate"></span>
      <button class="refresh-btn" onclick="loadData()">重新整理</button>
    </div>
  </div>

  <!-- Dashboard view -->
  <div id="dashboardView" class="content">
    <div class="stats-grid">
      <div class="stat-card success">
        <div class="stat-label">今日訂單</div>
        <div class="stat-value" id="todayCount">—</div>
        <div class="stat-sub" id="todayAmount">NT$ —</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">本月訂單</div>
        <div class="stat-value" id="monthCount">—</div>
        <div class="stat-sub" id="monthAmount">NT$ —</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">累計訂單</div>
        <div class="stat-value" id="totalCount">—</div>
        <div class="stat-sub" id="totalAmount">NT$ —</div>
      </div>
      <div class="stat-card accent">
        <div class="stat-label">已同步 Sheet</div>
        <div class="stat-value" id="syncedCount">—</div>
        <div class="stat-sub">筆已寫入</div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">最新訂單</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>訂單編號</th><th>店家</th><th>消費者</th>
            <th>手機</th><th>金額</th><th>狀態</th><th>訂單時間</th><th>Sheet</th>
          </tr>
        </thead>
        <tbody id="ordersBody">
          <tr><td colspan="8" class="empty">載入中...</td></tr>
        </tbody>
      </table>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">店家分布</span>
      </div>
      <div class="stores-grid" id="storesGrid">
        <div style="padding:16px;color:#64748d;font-size:13px;">載入中...</div>
      </div>
    </div>
  </div>

  <!-- Settings view -->
  <div id="settingsView" class="settings-view">
    <div class="settings-card">
      <div class="panel-title" style="font-size:15px;margin-bottom:6px;">Email 報表設定</div>
      <p style="font-size:13px;color:#64748d;margin-bottom:24px;">每天早上 09:00 自動發送前一天訂單報表給以下收件人。</p>

      <div style="margin-bottom:20px;">
        <label style="font-size:12px;font-weight:500;color:#273951;display:block;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px;">Email 報表欄位（可多選）</label>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;" id="fieldCheckboxes">
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="order_id" style="accent-color:#533afd;"> 訂單編號
          </label>
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="store_name" style="accent-color:#533afd;"> 店家名稱
          </label>
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="store_id" style="accent-color:#533afd;"> 店家編號
          </label>
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="consumer_name" style="accent-color:#533afd;"> 消費者姓名
          </label>
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="consumer_phone" style="accent-color:#533afd;"> 消費者手機
          </label>
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="amount" style="accent-color:#533afd;"> 消費金額
          </label>
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="order_status" style="accent-color:#533afd;"> 訂單狀態
          </label>
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="order_time" style="accent-color:#533afd;"> 訂單時間
          </label>
          <label style="display:flex;align-items:center;gap:7px;font-size:13px;color:#273951;cursor:pointer;padding:8px 10px;border:1px solid #e5edf5;border-radius:4px;">
            <input type="checkbox" value="received_at" style="accent-color:#533afd;"> 接收時間
          </label>
        </div>
      </div>

      <div style="margin-bottom:16px;">
        <label style="font-size:12px;font-weight:500;color:#273951;display:block;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px;">收件人（每行一個 Email）</label>
        <textarea id="recipientsInput"
          style="width:100%;height:120px;border:1px solid #e5edf5;border-radius:4px;padding:10px 12px;font-family:inherit;font-size:13px;color:#061b31;resize:vertical;outline:none;line-height:1.6;"
          placeholder="jason@example.com&#10;partner@example.com"
          onfocus="this.style.borderColor='#533afd'"
          onblur="this.style.borderColor='#e5edf5'"></textarea>
        <div style="font-size:11px;color:#64748d;margin-top:5px;">每行輸入一個 Email，儲存後立即生效</div>
      </div>

      <div style="display:flex;gap:10px;align-items:center;">
        <button onclick="saveSettings()"
          style="background:#533afd;color:#fff;border:none;padding:8px 18px;border-radius:4px;font-size:13px;font-family:inherit;font-weight:500;cursor:pointer;">
          儲存設定
        </button>
        <button onclick="sendTodayReport()"
          style="background:transparent;color:#533afd;border:1px solid #b9b9f9;padding:8px 18px;border-radius:4px;font-size:13px;font-family:inherit;cursor:pointer;">
          立即發送今日正式報表
        </button>
        <button onclick="sendTestReport()"
          style="background:transparent;color:#64748d;border:1px solid #e5edf5;padding:8px 18px;border-radius:4px;font-size:13px;font-family:inherit;cursor:pointer;">
          發送測試信
        </button>
        <span id="settingsMsg" style="font-size:12px;color:#108c3d;display:none;">已儲存</span>
      </div>
    </div>
  </div>

  <!-- Health view -->
  <div id="healthView" class="health-view">
    <div class="health-card">
      <div class="panel-title" style="margin-bottom:20px;font-size:15px;">系統健康狀態</div>
      <div class="health-status" id="healthStatus">—</div>
      <div class="health-time" id="healthTime">—</div>
      <code class="health-url">GET /health</code>
    </div>
  </div>
</div>

<script>
const fmt = n => new Intl.NumberFormat('zh-TW').format(n);
const fmtDate = s => s ? new Date(s).toLocaleString('zh-TW',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}) : '—';

function showView(view) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.getElementById('dashboardView').style.display = view === 'dashboard' ? 'block' : 'none';
  document.getElementById('healthView').style.display = view === 'health' ? 'block' : 'none';
  document.getElementById('settingsView').style.display = view === 'settings' ? 'block' : 'none';

  event.currentTarget.classList.add('active');

  const titles = { dashboard: '監控儀表板', health: '健康檢查', settings: '設定' };
  document.getElementById('pageTitle').textContent = titles[view] || view;

  if (view === 'health') loadHealth();
  if (view === 'settings') loadSettings();
}

const DEFAULT_FIELDS = 'order_id,store_name,consumer_name,consumer_phone,amount,order_status,order_time';

async function loadSettings() {
  try {
    const s = await fetch('/admin/settings').then(r => r.json());
    const recipients = (s.email_recipients || '').split(',').map(e => e.trim()).filter(Boolean).join('\\n');
    document.getElementById('recipientsInput').value = recipients;

    const fields = (s.email_fields || DEFAULT_FIELDS).split(',');
    document.querySelectorAll('#fieldCheckboxes input[type=checkbox]').forEach(cb => {
      cb.checked = fields.includes(cb.value);
    });
  } catch(e) {}
}

async function saveSettings() {
  const raw = document.getElementById('recipientsInput').value;
  const recipients = raw.split('\\n').map(e => e.trim()).filter(Boolean).join(',');

  const fields = [...document.querySelectorAll('#fieldCheckboxes input[type=checkbox]:checked')]
    .map(cb => cb.value).join(',');

  if (!fields) { alert('請至少選擇一個欄位'); return; }

  try {
    await fetch('/admin/settings', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ email_recipients: recipients, email_fields: fields })
    });
    const msg = document.getElementById('settingsMsg');
    msg.style.display = 'inline';
    setTimeout(() => msg.style.display = 'none', 2500);
  } catch(e) { alert('儲存失敗'); }
}

async function sendTodayReport() {
  if (!confirm('確定要立即發送今日正式報表？')) return;
  try {
    const r = await fetch('/admin/send-today-report', { method: 'POST' });
    const d = await r.json();
    if (r.ok) alert('今日報表已發送！共 ' + (d.message || ''));
    else alert('發送失敗：' + (d.detail || JSON.stringify(d)));
  } catch(e) { alert('發送失敗'); }
}

async function sendTestReport() {
  if (!confirm('確定要發送測試信？')) return;
  try {
    const r = await fetch('/admin/test-email', { method: 'POST' });
    const d = await r.json();
    if (r.ok) alert('測試信已發送！收件人：' + (d.recipients || []).join(', '));
    else alert('發送失敗：' + (d.detail || JSON.stringify(d)));
  } catch(e) { alert('發送失敗'); }
}

async function loadHealth() {
  try {
    const h = await fetch('/health').then(r => r.json());
    document.getElementById('healthStatus').textContent = h.status === 'ok' ? '✓  正常運作' : '✗  異常';
    document.getElementById('healthStatus').style.color = h.status === 'ok' ? '#108c3d' : '#ea2261';
    document.getElementById('healthTime').textContent = '伺服器時間：' + new Date(h.time).toLocaleString('zh-TW');
  } catch(e) {
    document.getElementById('healthStatus').textContent = '✗  無法連線';
    document.getElementById('healthStatus').style.color = '#ea2261';
  }
}

async function loadData() {
  try {
    const [health, orders] = await Promise.all([
      fetch('/health').then(r => r.json()),
      fetch('/orders?limit=200').then(r => r.json())
    ]);

    const sp = document.getElementById('sidebarStatus');
    sp.className = 'status-pill';
    document.getElementById('sidebarStatusText').textContent = 'API 正常';
    const now = new Date().toLocaleTimeString('zh-TW', {hour:'2-digit',minute:'2-digit'});
    document.getElementById('sidebarTime').textContent = '更新 ' + now;
    document.getElementById('lastUpdate').textContent = '最後更新：' + now;

    const today_ = new Date();
    const today = orders.filter(o => new Date(o.received_at).toDateString() === today_.toDateString());
    const month = orders.filter(o => {
      const d = new Date(o.received_at);
      return d.getFullYear() === today_.getFullYear() && d.getMonth() === today_.getMonth();
    });
    const synced = orders.filter(o => o.synced_to_sheet);

    document.getElementById('todayCount').textContent = today.length;
    document.getElementById('todayAmount').textContent = 'NT$ ' + fmt(today.reduce((s,o)=>s+o.amount,0));
    document.getElementById('monthCount').textContent = month.length;
    document.getElementById('monthAmount').textContent = 'NT$ ' + fmt(month.reduce((s,o)=>s+o.amount,0));
    document.getElementById('totalCount').textContent = orders.length;
    document.getElementById('totalAmount').textContent = 'NT$ ' + fmt(orders.reduce((s,o)=>s+o.amount,0));
    document.getElementById('syncedCount').textContent = synced.length;

    const tbody = document.getElementById('ordersBody');
    if (orders.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="empty">尚無訂單資料</td></tr>';
    } else {
      tbody.innerHTML = orders.slice(0,50).map(o => `
        <tr>
          <td><span class="order-id">${o.order_id}</span></td>
          <td>${o.store_name || o.store_id}</td>
          <td>${o.consumer_name || '—'}</td>
          <td>${o.consumer_phone}</td>
          <td class="amount">NT$ ${fmt(o.amount)}</td>
          <td><span class="badge badge-success">${o.order_status}</span></td>
          <td style="font-size:12px;color:#64748d;">${fmtDate(o.order_time)}</td>
          <td>${o.synced_to_sheet
            ? '<span class="badge badge-success">✓ 已同步</span>'
            : '<span class="badge badge-neutral">—</span>'}</td>
        </tr>`).join('');
    }

    const storeMap = {};
    orders.forEach(o => {
      const k = o.store_name || o.store_id;
      if (!storeMap[k]) storeMap[k] = { count: 0, amount: 0 };
      storeMap[k].count++;
      storeMap[k].amount += o.amount;
    });
    const grid = document.getElementById('storesGrid');
    if (Object.keys(storeMap).length === 0) {
      grid.innerHTML = '<div style="padding:16px;color:#64748d;font-size:13px;">尚無資料</div>';
    } else {
      grid.innerHTML = Object.entries(storeMap)
        .sort((a,b) => b[1].count - a[1].count)
        .map(([name, d]) => `
          <div class="store-card">
            <div class="store-name" title="${name}">${name}</div>
            <div class="store-count">${d.count}</div>
            <div class="store-amount">NT$ ${fmt(d.amount)}</div>
          </div>`).join('');
    }

  } catch(e) {
    const sp = document.getElementById('sidebarStatus');
    sp.className = 'status-pill offline';
    document.getElementById('sidebarStatusText').textContent = 'API 離線';
  }
}

loadData();
setInterval(loadData, 30000);
</script>
</body>
</html>"""
