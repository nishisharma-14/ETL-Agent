// High-density Industrial Console Client
// Zero emojis, strict data state management

let allProducts = [];
let filteredProducts = [];
let currentPage = 1;
const pageSize = 20;

// DOM Elements
const tableBody = document.getElementById('table-body');
const recordsCounter = document.getElementById('records-counter');
const pageIndicator = document.getElementById('page-indicator');
const prevPageBtn = document.getElementById('prev-page-btn');
const nextPageBtn = document.getElementById('next-page-btn');
const searchInput = document.getElementById('search-input');
const categoryFilter = document.getElementById('category-filter');
const minPriceFilter = document.getElementById('min-price-filter');
const maxPriceFilter = document.getElementById('max-price-filter');
const applyFiltersBtn = document.getElementById('apply-filters-btn');
const resetFiltersBtn = document.getElementById('reset-filters-btn');
const triggerBtn = document.getElementById('trigger-pipeline-btn');
const btnSpinner = document.getElementById('btn-spinner');
const consoleStream = document.getElementById('console-stream');
const logStatus = document.getElementById('log-status');

// Metrics Elements
const metricTotal = document.getElementById('metric-total');
const metricInserted = document.getElementById('metric-inserted');
const metricUpdated = document.getElementById('metric-updated');
const metricUnchanged = document.getElementById('metric-unchanged');

function addLog(message, isHighlight = false) {
  const line = document.createElement('div');
  line.className = 'log-line' + (isHighlight ? ' log-highlight' : '');
  const ts = new Date().toISOString().substring(11, 19);
  line.innerHTML = `<span class="log-ts">[${ts}]</span> ${message}`;
  consoleStream.appendChild(line);
  consoleStream.scrollTop = consoleStream.scrollHeight;
}

// Fetch products from FastAPI
async function loadProducts() {
  try {
    addLog("Querying database records from /products API...");
    const res = await fetch('/products?limit=200');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    allProducts = data;
    filteredProducts = [...allProducts];

    populateCategories(allProducts);
    updateMetrics(allProducts.length);
    renderTable();
    addLog(`Ingested ${allProducts.length} active database records.`);
  } catch (err) {
    addLog(`Failed to fetch records: ${err.message}`, true);
    tableBody.innerHTML = `<tr><td colspan="8" class="empty-state">Unable to load records. Ensure API backend is running.</td></tr>`;
  }
}

function updateMetrics(total, inserted = 0, updated = 0, unchanged = total) {
  metricTotal.textContent = total;
  metricInserted.textContent = inserted;
  metricUpdated.textContent = updated;
  metricUnchanged.textContent = unchanged;
}

function populateCategories(items) {
  const categories = [...new Set(items.map(p => p.category))].sort();
  categoryFilter.innerHTML = '<option value="">All Categories</option>';
  categories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat.toUpperCase();
    categoryFilter.appendChild(opt);
  });
}

function applyFilters() {
  const searchTerm = searchInput.value.trim().toLowerCase();
  const selectedCategory = categoryFilter.value.toLowerCase();
  const minPrice = parseFloat(minPriceFilter.value) || 0;
  const maxPrice = parseFloat(maxPriceFilter.value) || Infinity;

  filteredProducts = allProducts.filter(p => {
    const matchesSearch =
      !searchTerm ||
      p.title.toLowerCase().includes(searchTerm) ||
      (p.brand && p.brand.toLowerCase().includes(searchTerm)) ||
      String(p.product_id).includes(searchTerm);

    const matchesCategory = !selectedCategory || p.category.toLowerCase() === selectedCategory;
    const matchesPrice = p.price >= minPrice && p.price <= maxPrice;

    return matchesSearch && matchesCategory && matchesPrice;
  });

  currentPage = 1;
  renderTable();
  addLog(`Filter applied: ${filteredProducts.length} records matching criteria.`);
}

function resetFilters() {
  searchInput.value = '';
  categoryFilter.value = '';
  minPriceFilter.value = '';
  maxPriceFilter.value = '';
  filteredProducts = [...allProducts];
  currentPage = 1;
  renderTable();
  addLog("Filters reset to default.");
}

function renderTable() {
  const total = filteredProducts.length;
  recordsCounter.textContent = `Showing ${total} records`;

  if (total === 0) {
    tableBody.innerHTML = `<tr><td colspan="8" class="empty-state">No matching records found.</td></tr>`;
    pageIndicator.textContent = "Page 0 of 0";
    prevPageBtn.disabled = true;
    nextPageBtn.disabled = true;
    return;
  }

  const maxPage = Math.ceil(total / pageSize);
  currentPage = Math.min(currentPage, maxPage);

  const startIdx = (currentPage - 1) * pageSize;
  const endIdx = Math.min(startIdx + pageSize, total);
  const pageItems = filteredProducts.slice(startIdx, endIdx);

  tableBody.innerHTML = '';
  pageItems.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="mono-cell">${p.product_id}</td>
      <td><strong>${escapeHtml(p.title)}</strong></td>
      <td><span class="badge-tag">${escapeHtml(p.category.toUpperCase())}</span></td>
      <td>${escapeHtml(p.brand || 'GENERIC')}</td>
      <td class="align-right price-cell">$${p.price.toFixed(2)}</td>
      <td class="align-right mono-cell">${p.rating.toFixed(2)}</td>
      <td class="align-right mono-cell">${p.stock}</td>
      <td class="mono-cell" style="font-size: 11px; color: var(--text-muted);">${formatTimestamp(p.updated_at)}</td>
    `;
    tableBody.appendChild(tr);
  });

  pageIndicator.textContent = `Page ${currentPage} of ${maxPage} (${startIdx + 1}-${endIdx} of ${total})`;
  prevPageBtn.disabled = currentPage <= 1;
  nextPageBtn.disabled = currentPage >= maxPage;
}

function formatTimestamp(isoStr) {
  if (!isoStr) return 'N/A';
  return isoStr.replace('T', ' ').substring(0, 19) + ' UTC';
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// Trigger Pipeline Run
async function triggerPipelineRun() {
  triggerBtn.disabled = true;
  btnSpinner.style.display = 'inline-block';
  logStatus.textContent = 'EXECUTING PIPELINE...';
  addLog("Initiating on-demand ETL pipeline run via POST /pipeline/run...", true);

  try {
    const res = await fetch('/pipeline/run', { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const summary = await res.json();

    addLog(`Pipeline Execution Successful: Extracted=${summary.total_extracted}, Transformed=${summary.total_transformed}`, true);
    addLog(`Incremental Load Result: Inserted=${summary.inserted}, Updated=${summary.updated}, Unchanged=${summary.unchanged}`, true);

    updateMetrics(summary.total_transformed, summary.inserted, summary.updated, summary.unchanged);
    await loadProducts();
  } catch (err) {
    addLog(`Pipeline execution failed: ${err.message}`, true);
  } finally {
    triggerBtn.disabled = false;
    btnSpinner.style.display = 'none';
    logStatus.textContent = 'READY';
  }
}

// Event Listeners
triggerBtn.addEventListener('click', triggerPipelineRun);
applyFiltersBtn.addEventListener('click', applyFilters);
resetFiltersBtn.addEventListener('click', resetFilters);

searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') applyFilters();
});

prevPageBtn.addEventListener('click', () => {
  if (currentPage > 1) {
    currentPage--;
    renderTable();
  }
});

nextPageBtn.addEventListener('click', () => {
  const maxPage = Math.ceil(filteredProducts.length / pageSize);
  if (currentPage < maxPage) {
    currentPage++;
    renderTable();
  }
});

// Initial boot
loadProducts();
