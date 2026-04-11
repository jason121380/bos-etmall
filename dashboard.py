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
    font-weight: 300;
  }

  /* Header */
  .header {
    background: #ffffff;
    border-bottom: 1px solid #e5edf5;
    padding: 0 32px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: rgba(0,55,112,0.08) 0px 2px 8px;
  }

  .header-left { display: flex; align-items: center; gap: 12px; }

  .logo-mark {
    width: 28px; height: 28px; background: #533afd;
    border-radius: 6px; display: flex; align-items: center; justify-content: center;
  }
  .logo-mark svg { width: 16px; height: 16px; fill: white; }

  .header h1 {
    font-size: 15px; font-weight: 500; color: #061b31;
    letter-spacing: -0.2px;
  }

  .header-right { display: flex; align-items: center; gap: 20px; }

  .status-badge {
    display: flex; align-items: center; gap: 6px;
    background: rgba(21,190,83,0.1);
    border: 1px solid rgba(21,190,83,0.3);
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px; font-weight: 400; color: #108c3d;
  }
  .status-badge.offline { background: rgba(234,34,97,0.08); border-color: rgba(234,34,97,0.25); color: #c41e5a; }

  .status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #15be53;
    animation: pulse 2s infinite;
  }
  .status-badge.offline .status-dot { background: #ea2261; animation: none; }

  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .last-update { font-size: 12px; color: #64748d; }

  /* Container */
  .container { max-width: 1120px; margin: 0 auto; padding: 32px 24px; }

  /* Section label */
  .section-eyebrow {
    font-size: 11px; font-weight: 500; color: #533afd;
    text-transform: uppercase; letter-spacing: 0.8px;
    margin-bottom: 6px;
  }

  /* Stats grid */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
  }

  .stat-card {
    background: #ffffff;
    border: 1px solid #e5edf5;
    border-radius: 6px;
    padding: 20px 22px;
    box-shadow: rgba(50,50,93,0.25) 0px 6px 12px -6px, rgba(0,0,0,0.06) 0px 4px 8px -4px;
    transition: box-shadow 0.2s;
  }
  .stat-card:hover {
    box-shadow: rgba(50,50,93,0.25) 0px 13px 27px -12px, rgba(0,0,0,0.1) 0px 8px 16px -8px;
  }

  .stat-label {
    font-size: 12px; font-weight: 400; color: #64748d;
    margin-bottom: 10px;
  }

  .stat-value {
    font-size: 30px; font-weight: 300; color: #061b31;
    letter-spacing: -0.8px;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    margin-bottom: 6px;
  }

  .stat-sub { font-size: 12px; color: #64748d; font-weight: 400; }

  .stat-card.accent .stat-value { color: #533afd; }
  .stat-card.success .stat-value { color: #108c3d; }

  /* Panels */
  .panel {
    background: #ffffff;
    border: 1px solid #e5edf5;
    border-radius: 6px;
    margin-bottom: 24px;
    box-shadow: rgba(50,50,93,0.25) 0px 6px 12px -6px, rgba(0,0,0,0.06) 0px 4px 8px -4px;
    overflow: hidden;
  }

  .panel-header {
    padding: 16px 22px;
    border-bottom: 1px solid #e5edf5;
    display: flex; justify-content: space-between; align-items: center;
  }

  .panel-title {
    font-size: 13px; font-weight: 500; color: #061b31;
    letter-spacing: -0.1px;
  }

  .refresh-btn {
    background: transparent;
    border: 1px solid #e5edf5;
    color: #64748d;
    padding: 5px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-family: inherit;
    font-weight: 400;
    cursor: pointer;
    transition: all 0.15s;
  }
  .refresh-btn:hover {
    border-color: #533afd;
    color: #533afd;
    background: rgba(83,58,253,0.04);
  }

  /* Table */
  table { width: 100%; border-collapse: collapse; }

  th {
    padding: 10px 16px;
    text-align: left;
    font-size: 11px; font-weight: 500;
    color: #64748d;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    border-bottom: 1px solid #e5edf5;
    background: #f8fafc;
  }

  td {
    padding: 13px 16px;
    font-size: 13px;
    color: #273951;
    border-bottom: 1px solid #f0f5fa;
    font-weight: 400;
  }

  tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: #f8fafc; }

  .amount {
    font-weight: 500;
    color: #061b31;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.2px;
  }

  .order-id {
    font-family: 'SFMono-Regular', 'Consolas', monospace;
    font-size: 12px;
    color: #533afd;
  }

  .badge {
    display: inline-flex; align-items: center;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 11px; font-weight: 400;
  }
  .badge-success {
    background: rgba(21,190,83,0.15);
    color: #108c3d;
    border: 1px solid rgba(21,190,83,0.35);
  }
  .badge-neutral {
    background: #f6f9fc;
    color: #64748d;
    border: 1px solid #e5edf5;
  }

  .empty {
    text-align: center; padding: 48px;
    color: #64748d; font-size: 14px; font-weight: 300;
  }

  /* Stores grid */
  .stores-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
    padding: 20px;
  }

  .store-card {
    background: #f8fafc;
    border: 1px solid #e5edf5;
    border-radius: 5px;
    padding: 14px 16px;
    text-align: center;
    transition: box-shadow 0.15s;
  }
  .store-card:hover {
    box-shadow: rgba(50,50,93,0.15) 0px 6px 12px -6px;
    background: #ffffff;
  }

  .store-name {
    font-size: 12px; color: #64748d; font-weight: 400;
    margin-bottom: 6px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .store-count {
    font-size: 22px; font-weight: 300; color: #533afd;
    letter-spacing: -0.5px;
    font-variant-numeric: tabular-nums;
  }
  .store-amount { font-size: 11px; color: #64748d; margin-top: 3px; }

  @media (max-width: 768px) {
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .header { padding: 0 16px; }
    .container { padding: 20px 16px; }
  }
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <div class="logo-mark">
      <svg viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
    </div>
    <h1>BOS-ETMALL 訂單後台</h1>
  </div>
  <div class="header-right">
    <div class="status-badge" id="statusBadge">
      <div class="status-dot" id="statusDot"></div>
      <span id="statusText">連線中</span>
    </div>
    <span class="last-update" id="lastUpdate"></span>
  </div>
</div>

<div class="container">

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
      <button class="refresh-btn" onclick="loadData()">重新整理</button>
    </div>
    <table>
      <thead>
        <tr>
          <th>訂單編號</th>
          <th>店家</th>
          <th>消費者</th>
          <th>手機</th>
          <th>金額</th>
          <th>狀態</th>
          <th>訂單時間</th>
          <th>Sheet</th>
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
      <div style="padding:20px;color:#64748d;font-size:13px;">載入中...</div>
    </div>
  </div>

</div>

<script>
const fmt = n => new Intl.NumberFormat('zh-TW').format(n);
const fmtDate = s => s ? new Date(s).toLocaleString('zh-TW', {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}) : '—';

async function loadData() {
  try {
    const [health, orders] = await Promise.all([
      fetch('/health').then(r => r.json()),
      fetch('/orders?limit=200').then(r => r.json())
    ]);

    const badge = document.getElementById('statusBadge');
    badge.className = 'status-badge';
    document.getElementById('statusText').textContent = 'API 正常';
    document.getElementById('lastUpdate').textContent = '更新：' + new Date().toLocaleTimeString('zh-TW');

    const now = new Date();
    const today = orders.filter(o => new Date(o.received_at).toDateString() === now.toDateString());
    const month = orders.filter(o => {
      const d = new Date(o.received_at);
      return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
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
      grid.innerHTML = '<div style="padding:20px;color:#64748d;font-size:13px;">尚無資料</div>';
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
    const badge = document.getElementById('statusBadge');
    badge.className = 'status-badge offline';
    document.getElementById('statusText').textContent = 'API 離線';
  }
}

loadData();
setInterval(loadData, 30000);
</script>
</body>
</html>"""
