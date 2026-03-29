// RecuraOps — Dashboard JS

function showToast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span style="font-weight:700">${type==='success'?'✓':'✕'}</span> ${msg}`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.animation='toast-in .3s ease reverse'; setTimeout(()=>toast.remove(),300); }, 4000);
}
window.showToast = showToast;

function initDonut() {
  const canvas = document.getElementById('savings-donut');
  if (!canvas) return;
  const labels = JSON.parse(canvas.dataset.labels || '[]');
  const values = JSON.parse(canvas.dataset.values || '[]');
  new Chart(canvas, {
    type: 'doughnut',
    data: { labels, datasets: [{ data: values,
      backgroundColor: ['#D6EAF5','#D4EDE1','#E8E3F5'],
      borderColor: ['#A0C8E0','#A8D8BD','#C4BCE8'], borderWidth: 2, hoverOffset: 6 }] },
    options: { cutout: '72%',
      plugins: { legend: {display:false},
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ₹${ctx.parsed.toLocaleString('en-IN')}` } } },
      animation: { animateRotate: true, duration: 800 } }
  });
}

function initScanButton() {
  const btn = document.getElementById('scan-btn');
  if (!btn) return;
  btn.addEventListener('click', async () => {
    btn.classList.add('loading');
    try {
      const res = await fetch('/api/run-scan', { method: 'POST' });
      const data = await res.json();
      showToast(data.success ? 'Scan triggered! Agents running in background.' : 'Scan failed: ' + data.error, data.success ? 'success' : 'error');
    } catch (e) { showToast('Network error.', 'error'); }
    finally { setTimeout(() => btn.classList.remove('loading'), 1500); }
  });
}

function showConfirmModal(aprId, title, impact) {
  const modal = document.getElementById('confirm-modal');
  if (!modal) return;
  document.getElementById('modal-title-text').textContent = title;
  document.getElementById('modal-impact-text').textContent = impact;
  modal.classList.add('open');
  const confirmBtn = document.getElementById('modal-confirm');
  confirmBtn.disabled = false;
  confirmBtn.textContent = 'Confirm & Execute';
  confirmBtn.onclick = async () => {
    confirmBtn.disabled = true; confirmBtn.textContent = 'Executing…';
    try {
      const res = await fetch(`/approvals/${aprId}/approve`, { method: 'POST' });
      const data = await res.json();
      modal.classList.remove('open');
      if (data.success) { showToast('✓ Action approved and executed!'); setTimeout(()=>location.reload(),1500); }
      else { showToast(data.error || 'Execution failed', 'error'); confirmBtn.disabled=false; confirmBtn.textContent='Confirm & Execute'; }
    } catch { showToast('Network error.', 'error'); modal.classList.remove('open'); }
  };
  document.getElementById('modal-cancel').onclick = () => modal.classList.remove('open');
  modal.addEventListener('click', e => { if (e.target===modal) modal.classList.remove('open'); }, {once:true});
}

function initApprovalButtons() {
  document.querySelectorAll('.approve-btn').forEach(btn => {
    btn.addEventListener('click', () => showConfirmModal(btn.dataset.id, btn.dataset.title, btn.dataset.impact));
  });
  document.querySelectorAll('.reject-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      try {
        const res = await fetch(`/approvals/${btn.dataset.id}/reject`, {method:'POST'});
        const data = await res.json();
        if (data.success) { showToast('Action rejected.'); setTimeout(()=>location.reload(),1200); }
        else { showToast(data.error,'error'); btn.disabled=false; }
      } catch { showToast('Network error.','error'); btn.disabled=false; }
    });
  });
}

function initApprovalCards() {
  document.querySelectorAll('.approval-card[data-id]').forEach(card => {
    card.addEventListener('click', e => {
      if (e.target.closest('button')) return;
      document.querySelectorAll('.approval-card').forEach(c=>c.classList.remove('selected'));
      card.classList.add('selected');
      document.querySelectorAll('.detail-pane').forEach(p=>p.style.display='none');
      const d = document.getElementById(`detail-${card.dataset.id}`);
      if (d) d.style.display='block';
      const ph = document.getElementById('panel-placeholder');
      if (ph) ph.style.display='none';
    });
  });
  const first = document.querySelector('.approval-card[data-id]');
  if (first) first.click();
}

function initExpandableRows() {
  document.querySelectorAll('.row-expandable').forEach(row => {
    row.addEventListener('click', () => {
      const target = document.getElementById(row.dataset.expand);
      if (!target) return;
      const isOpen = target.style.display !== 'none';
      target.style.display = isOpen ? 'none' : 'table-row';
      const icon = row.querySelector('.expand-icon');
      if (icon) icon.style.transform = isOpen ? '' : 'rotate(90deg)';
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  initDonut();
  initScanButton();
  initApprovalButtons();
  initApprovalCards();
  initExpandableRows();
});
