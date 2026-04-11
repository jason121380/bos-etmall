DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BOS-ETMALL 訂單監控</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
  .header { background: #1e293b; border-bottom: 1px solid #334155; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
  .header h1 { font-size: 18px; font-weight: 700; color: #f1f5f9; }
  .status-dot { width: 10px; height: 10px; border-radius: 50%; background: #22c55e; display: inline-block; margin-right: 8px; animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
  .status-text { font-size: 13px; color: #94a3b8; }
  .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
  .stat-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; }
  .stat-label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
  .stat-value { font-size: 32px; font-weight: 700; color: #f1f5f9; }
  .stat-sub { font-size: 12px; color: #94a3b8; margin-top: 4px; }
  .stat-card.green .stat-value { color: #22c55e; }
  .stat-card.blue .stat-value { color: #60a5fa; }
  .stat-card.purple .stat-value { color: #a78bfa; }
  .stat-card.orange .stat-value { color: #fb923c; }
  .section { background: #1e293b; border: 1px solid #334155; border-radius: 12px; overflow: hidden; margin-bottom: 24px; }
  .section-header { padding: 16px 20px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
  .section-title { font-size: 14px; font-weight: 600; color: #f1f5f9; }
  .refresh-btn { background: #334155; border: none; color: #94a3b8; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; }
  .refresh-btn:hover { background: #475569; color: #f1f5f9; }
  table { width: 100%; border-collapse: collapse; }
  th { padding: 10px 16px; text-align: left; font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #334155; }
  td { padding: 12px 16px; font-size: 13px; color: #cbd5e1; border-bottom: 1px solid #1e293b; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #0f172a; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .badge-green { background: #14532d; color: #4ade80; }
  .badge-blue { background: #1e3a5f; color: #60a5fa; }
  .amount { font-weight: 600; color: #f1f5f9; }
  .empty { text-align: center; padding: 40px; color: #475569; font-size: 14px; }
  .last-update { font-size: 11px; color: #475569; }
  .stores-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; padding: 16px; }
  .store-card { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 12px; text-align: center; }
  .store-name { font-size: 13px; color: #94a3b8; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .store-count { font-size: 24px; font-weight: 700; color: #60a5fa; }
  .store-amount { font-size: 11px; color: #64748b; margin-top: 2px; }
</style>
</head>
<body>
<div class="header">
  <h1>BOS-ETMALL 訂單監控</h1>
  <div>
    <span class="status-dot" id="statusDot"></span>
    <span class="status-text" id="statusText">連線中...</span>
    <span class="last-update" id="lastUpdate" style="margin-left:16px;"></span>
  </div>
</div>

<div class="container">
  <div class="stats-grid">
    <div class="stat-card green">
      <div class="stat-label">今日訂單</div>
      <div class="stat-value" id="todayCount">—</div>
      <div class="stat-sub" id="todayAmount">NT$ —</div>
    </div>
    <div class="stat-card blue">
      <div class="stat-label">本月訂單</div>
      <div class="stat-value" id="monthCount">—</div>
      <div class="stat-sub" id="monthAmount">NT$ —</div>
    </div>
    <div class="stat-card purple">
      <div class="stat-label">累計訂單</div>
      <div class="stat-value" id="totalCount">—</div>
      <div class="stat-sub" id="totalAmount">NT$ —</div>
    </div>
    <div class="stat-card orange">
      <div class="stat-label">已同步 Sheet</div>
      <div class="stat-value" id="syncedCount">—</div>
      <div class="stat-sub">筆已寫入</div>
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <span class="section-title">最新訂單</span>
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

  <div class="section">
    <div class="section-header">
      <span class="section-title">店家分布</span>
    </div>
    <div class="stores-grid" id="storesGrid">
      <div style="padding:20px;color:#475569;font-size:14px;">載入中...</div>
    </div>
  </div>
</div>

<script>
const fmt = (n) => new Intl.NumberFormat('zh-TW').format(n);
const fmtDate = (s) => s ? new Date(s).toLocaleString('zh-TW', {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}) : '—';

async function loadData() {
  try {
    const [health, orders] = await Promise.all([
      fetch('/health').then(r => r.json()),
      fetch('/orders?limit=200').then(r => r.json())
    ]);

    // Health
    document.getElementById('statusDot').style.background = '#22c55e';
    document.getElementById('statusText').textContent = 'API 正常';
    document.getElementById('lastUpdate').textContent = '更新：' + new Date().toLocaleTimeString('zh-TW');

    // Stats
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

    // Orders table
    const tbody = document.getElementById('ordersBody');
    if (orders.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="empty">尚無訂單</td></tr>';
    } else {
      tbody.innerHTML = orders.slice(0,50).map(o => `
        <tr>
          <td style="font-family:monospace;font-size:12px;">${o.order_id}</td>
          <td>${o.store_name || o.store_id}</td>
          <td>${o.consumer_name || '—'}</td>
          <td>${o.consumer_phone}</td>
          <td class="amount">NT$ ${fmt(o.amount)}</td>
          <td><span class="badge badge-green">${o.order_status}</span></td>
          <td style="font-size:12px;">${fmtDate(o.order_time)}</td>
          <td>${o.synced_to_sheet ? '<span class="badge badge-green">✓</span>' : '<span class="badge" style="background:#1e293b;color:#475569;">—</span>'}</td>
        </tr>`).join('');
    }

    // Stores
    const storeMap = {};
    orders.forEach(o => {
      const k = o.store_name || o.store_id;
      if (!storeMap[k]) storeMap[k] = { count: 0, amount: 0 };
      storeMap[k].count++;
      storeMap[k].amount += o.amount;
    });
    const storesGrid = document.getElementById('storesGrid');
    if (Object.keys(storeMap).length === 0) {
      storesGrid.innerHTML = '<div style="padding:20px;color:#475569;font-size:14px;">尚無資料</div>';
    } else {
      storesGrid.innerHTML = Object.entries(storeMap)
        .sort((a,b) => b[1].count - a[1].count)
        .map(([name, data]) => `
          <div class="store-card">
            <div class="store-name" title="${name}">${name}</div>
            <div class="store-count">${data.count}</div>
            <div class="store-amount">NT$ ${fmt(data.amount)}</div>
          </div>`).join('');
    }
  } catch(e) {
    document.getElementById('statusDot').style.background = '#ef4444';
    document.getElementById('statusText').textContent = 'API 離線';
  }
}

loadData();
setInterval(loadData, 30000); // 每 30 秒自動刷新
</script>
</body>
</html>"""
