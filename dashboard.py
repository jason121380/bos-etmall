DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="BOS-ETMALL">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon-192.png">
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

  /* Settings & Health & Docs view */
  .settings-view, .health-view, .docs-view { padding: 0; display: none; }
  .docs-view { height: calc(100vh - 52px); }
  .docs-view iframe { width: 100%; height: 100%; border: none; }
  @media (max-width: 768px) {
    .docs-view { height: calc(100vh - 52px - 56px - env(safe-area-inset-bottom)); }
  }
  .settings-card, .health-card {
    background: #fff; border: 1px solid #e5edf5; border-radius: 6px;
    padding: 28px;
    max-width: 560px;
  }
  .health-status { font-size: 36px; font-weight: 300; color: #108c3d; margin-bottom: 8px; }
  .health-time { font-size: 13px; color: #64748d; }
  .health-url { font-family: monospace; font-size: 12px; color: #533afd; margin-top: 16px; display: block; }

  /* ── Bottom Nav (mobile only) ── */
  .bottom-nav {
    display: none;
    position: fixed; bottom: 0; left: 0; right: 0;
    background: #ffffff; border-top: 1px solid #e5edf5;
    z-index: 300;
    padding-bottom: env(safe-area-inset-bottom);
  }
  .bottom-nav-inner {
    display: flex; justify-content: space-around; align-items: stretch;
    height: 56px;
  }
  .bottom-tab {
    flex: 1; display: flex; flex-direction: column; align-items: center;
    justify-content: center; gap: 3px;
    font-size: 10px; color: #64748d; cursor: pointer;
    transition: color 0.15s; text-decoration: none;
    -webkit-tap-highlight-color: transparent;
    padding: 4px 0;
  }
  .bottom-tab.active { color: #533afd; }
  .bottom-tab svg { width: 20px; height: 20px; }

  /* ── Sidebar overlay (mobile) ── */
  .sidebar-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,0.3); z-index: 190;
  }
  .sidebar-overlay.open { display: block; }

  /* ── Table scroll ── */
  .table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }

  @media (max-width: 768px) {
    body { flex-direction: column; }
    .sidebar { transform: translateX(-100%); transition: transform 0.25s; width: 220px; }
    .sidebar.open { transform: translateX(0); }
    .main { margin-left: 0; }
    .topbar { padding: 0 16px; }
    .hamburger { display: none !important; }
    .content { padding: 16px; padding-bottom: 80px; }
    .settings-view, .health-view { padding: 16px; padding-bottom: 80px; }
    .settings-card { max-width: 100%; padding: 20px 16px; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .stat-value { font-size: 22px; }
    .bottom-nav { display: block; }
    #fieldCheckboxes { grid-template-columns: repeat(2, 1fr); }
  }

  @media (max-width: 400px) {
    .stats-grid { grid-template-columns: 1fr 1fr; gap: 8px; }
    .stat-card { padding: 14px 12px; }
    #fieldCheckboxes { grid-template-columns: 1fr 1fr; }
  }

  .hamburger { display: none; }
</style>
</head>
<body>

<!-- Sidebar overlay -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="closeSidebar()"></div>

<!-- Sidebar -->
<aside class="sidebar" id="sidebar">
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
      <a class="nav-item" onclick="showView('docs')">
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
    <div style="display:flex;align-items:center;gap:10px;">
      <button class="hamburger" onclick="toggleSidebar()" aria-label="選單">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
      <span class="topbar-title" id="pageTitle">監控儀表板</span>
    </div>
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
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>接收時間</th><th>店家</th><th>消費者</th>
              <th>手機</th><th>金額</th><th>狀態</th><th>訂單時間</th><th>Sheet</th><th>訂單編號</th>
            </tr>
          </thead>
          <tbody id="ordersBody">
            <tr><td colspan="9" class="empty">載入中...</td></tr>
          </tbody>
        </table>
      </div>
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

      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:20px;">
        <button onclick="saveSettings()"
          style="background:#533afd;color:#fff;border:none;padding:8px 18px;border-radius:4px;font-size:13px;font-family:inherit;font-weight:500;cursor:pointer;">
          儲存設定
        </button>
        <span id="settingsMsg" style="font-size:12px;color:#108c3d;display:none;">已儲存</span>
      </div>

      <div style="border-top:1px solid #e5edf5;padding-top:20px;margin-bottom:20px;">
        <label style="font-size:12px;font-weight:500;color:#273951;display:block;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px;">手動發送報表</label>
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px;">
          <div>
            <div style="font-size:11px;color:#64748d;margin-bottom:4px;">開始日期</div>
            <input type="date" id="dateFrom"
              style="border:1px solid #e5edf5;border-radius:4px;padding:7px 10px;font-family:inherit;font-size:13px;color:#061b31;outline:none;"
              onfocus="this.style.borderColor='#533afd'" onblur="this.style.borderColor='#e5edf5'">
          </div>
          <div>
            <div style="font-size:11px;color:#64748d;margin-bottom:4px;">結束日期</div>
            <input type="date" id="dateTo"
              style="border:1px solid #e5edf5;border-radius:4px;padding:7px 10px;font-family:inherit;font-size:13px;color:#061b31;outline:none;"
              onfocus="this.style.borderColor='#533afd'" onblur="this.style.borderColor='#e5edf5'">
          </div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <button onclick="sendDateReport()"
            style="background:#533afd;color:#fff;border:none;padding:8px 18px;border-radius:4px;font-size:13px;font-family:inherit;font-weight:500;cursor:pointer;">
            發送指定區間報表
          </button>
          <button onclick="sendTodayReport()"
            style="background:transparent;color:#533afd;border:1px solid #b9b9f9;padding:8px 18px;border-radius:4px;font-size:13px;font-family:inherit;cursor:pointer;">
            發送今日報表
          </button>
          <button onclick="sendTestReport()"
            style="background:transparent;color:#64748d;border:1px solid #e5edf5;padding:8px 18px;border-radius:4px;font-size:13px;font-family:inherit;cursor:pointer;">
            發送測試信
          </button>
        </div>
      </div>

      <div style="border-top:1px solid #e5edf5;padding-top:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <label style="font-size:12px;font-weight:500;color:#273951;text-transform:uppercase;letter-spacing:0.5px;">Email 發送紀錄</label>
          <button onclick="loadEmailLogs()"
            style="background:transparent;color:#64748d;border:1px solid #e5edf5;padding:4px 12px;border-radius:4px;font-size:12px;font-family:inherit;cursor:pointer;">重新整理</button>
        </div>
        <div style="overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;font-size:12px;" id="emailLogTable">
            <thead>
              <tr style="background:#f6f9fc;">
                <th style="text-align:left;padding:8px 10px;color:#64748d;font-weight:500;border-bottom:1px solid #e5edf5;">時間</th>
                <th style="text-align:left;padding:8px 10px;color:#64748d;font-weight:500;border-bottom:1px solid #e5edf5;">類型</th>
                <th style="text-align:left;padding:8px 10px;color:#64748d;font-weight:500;border-bottom:1px solid #e5edf5;">日期區間</th>
                <th style="text-align:center;padding:8px 10px;color:#64748d;font-weight:500;border-bottom:1px solid #e5edf5;">筆數</th>
                <th style="text-align:center;padding:8px 10px;color:#64748d;font-weight:500;border-bottom:1px solid #e5edf5;">狀態</th>
              </tr>
            </thead>
            <tbody id="emailLogBody">
              <tr><td colspan="5" style="text-align:center;padding:16px;color:#94a3b8;">載入中…</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- Docs view -->
  <div id="docsView" class="docs-view">
    <iframe id="docsFrame" src="about:blank"></iframe>
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

function showView(view, evt) {
  if (evt !== undefined && evt !== null) closeSidebar();
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.getElementById('dashboardView').style.display = view === 'dashboard' ? 'block' : 'none';
  document.getElementById('healthView').style.display = view === 'health' ? 'block' : 'none';
  document.getElementById('settingsView').style.display = view === 'settings' ? 'block' : 'none';
  document.getElementById('docsView').style.display = view === 'docs' ? 'block' : 'none';
  if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
  else if (typeof event !== 'undefined' && event && event.currentTarget) event.currentTarget.classList.add('active');
  const titles = { dashboard: '監控儀表板', health: '健康檢查', settings: '設定', docs: 'API 文件' };
  document.getElementById('pageTitle').textContent = titles[view] || view;
  if (view === 'health') loadHealth();
  if (view === 'settings') { loadSettings(); loadEmailLogs(); }
  if (view === 'docs') { document.getElementById('docsFrame').src = '/docs'; }
}

const DEFAULT_FIELDS = 'store_name,consumer_phone,order_time';

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

async function sendDateReport() {
  const from = document.getElementById('dateFrom').value;
  const to = document.getElementById('dateTo').value;
  if (!from) { alert('請選擇開始日期'); return; }
  const toDate = to || from;
  if (!confirm(`確定要發送 ${from} 至 ${toDate} 的報表？`)) return;
  try {
    const r = await fetch(`/admin/send-date-report?start_date=${from}&end_date=${toDate}`, { method: 'POST' });
    const d = await r.json();
    if (r.ok) alert(d.message || '報表已發送！');
    else alert('發送失敗：' + (d.detail || JSON.stringify(d)));
  } catch(e) { alert('發送失敗'); }
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

const TRIGGER_LABELS = {
  schedule: '排程（自動）', manual_today: '今日報表', manual_date: '指定區間', test: '測試信'
};

async function loadEmailLogs() {
  try {
    const logs = await fetch('/admin/email-logs?limit=20').then(r => r.json());
    const body = document.getElementById('emailLogBody');
    if (!logs.length) {
      body.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:16px;color:#94a3b8;">尚無發送紀錄</td></tr>';
      return;
    }
    body.innerHTML = logs.map(l => {
      const t = l.sent_at ? new Date(l.sent_at).toLocaleString('zh-TW',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}) : '—';
      const statusBadge = l.status === 'ok'
        ? '<span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:10px;font-size:11px;">成功</span>'
        : '<span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:10px;font-size:11px;" title="' + (l.error||'') + '">失敗</span>';
      return `<tr style="border-bottom:1px solid #f1f5f9;">
        <td style="padding:8px 10px;color:#273951;">${t}</td>
        <td style="padding:8px 10px;color:#273951;">${TRIGGER_LABELS[l.trigger] || l.trigger}</td>
        <td style="padding:8px 10px;color:#273951;">${l.date_range || '—'}</td>
        <td style="padding:8px 10px;text-align:center;color:#273951;">${l.order_count}</td>
        <td style="padding:8px 10px;text-align:center;">${statusBadge}</td>
      </tr>`;
    }).join('');
  } catch(e) {
    document.getElementById('emailLogBody').innerHTML =
      '<tr><td colspan="5" style="text-align:center;padding:16px;color:#94a3b8;">載入失敗</td></tr>';
  }
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
      tbody.innerHTML = '<tr><td colspan="9" class="empty">尚無訂單資料</td></tr>';
    } else {
      tbody.innerHTML = orders.slice(0,50).map(o => `
        <tr>
          <td style="font-size:12px;color:#64748d;">${fmtDate(o.received_at)}</td>
          <td>${o.store_name || o.store_id}</td>
          <td>${o.consumer_name || '—'}</td>
          <td>${o.consumer_phone}</td>
          <td class="amount">NT$ ${fmt(o.amount)}</td>
          <td><span class="badge badge-success">${o.order_status}</span></td>
          <td style="font-size:12px;color:#64748d;">${fmtDate(o.order_time)}</td>
          <td>${o.synced_to_sheet
            ? '<span class="badge badge-success">✓ 已同步</span>'
            : '<span class="badge badge-neutral">—</span>'}</td>
          <td><span class="order-id">${o.order_id}</span></td>
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

// ── Sidebar mobile toggle ──
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebarOverlay').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').classList.remove('open');
}

// ── Bottom nav ──
function showTab(view, el) {
  closeSidebar();
  document.querySelectorAll('.bottom-tab').forEach(t => t.classList.remove('active'));
  if (el) el.classList.add('active');
  showView(view, null);
}

// ── Service Worker ──
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}
</script>

<!-- Bottom navigation bar -->
<nav class="bottom-nav">
  <div class="bottom-nav-inner">
    <div class="bottom-tab active" onclick="showTab('dashboard', this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
      </svg>
      儀表板
    </div>
    <div class="bottom-tab" onclick="showTab('health', this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
      健康
    </div>
    <div class="bottom-tab" onclick="showTab('settings', this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
      設定
    </div>
    <div class="bottom-tab" onclick="showTab('docs', this)">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>
      文件
    </div>
  </div>
</nav>
</body>
</html>"""
