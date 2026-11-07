const API = '/api';

const data = { books: [], orders: [], machines: [], times: [] };
const $ = id => document.getElementById(id);
const euro = n => Number(n).toFixed(2) + ' €';
const hours = n => Number(n).toFixed(2) + ' h';
const bookName = id => (data.books.find(b => b.id === id) || { name: '?' }).name;

function safe(text) {
  const p = document.createElement('p');
  p.textContent = text;
  return p.innerHTML;
}

let messageTimer;
function showMessage(text, isError) {
  $('message').textContent = text;
  $('message').className = isError ? 'error' : '';
  clearTimeout(messageTimer);
  messageTimer = setTimeout(() => { $('message').textContent = ''; }, 4000);
}

async function request(method, url, body) {
  const response = await fetch(API + url, {
    method: method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined
  }).catch(() => { throw new Error('Could not connect to the server.'); });

  const result = await response.json().catch(() => null);
  if (!response.ok) throw new Error((result && result.message) || 'Server error (' + response.status + ').');
  return result;
}

async function loadAll() {
  try {
    data.books = await request('GET', '/books');
    data.orders = await request('GET', '/orders');
    data.machines = await request('GET', '/machines');
    data.times = await request('GET', '/processing-times');
  } catch (error) {
    showMessage(error.message, true);
  }
  for (const list in columns) showTable(list);
  $('orderBook').innerHTML = '<option value="">Select a book</option>' +
    data.books.map(b => `<option value="${b.id}">${safe(b.name)}</option>`).join('');
  showTimes();
  for (const list in columns) $('count-' + list).textContent = data[list].length;
}

const columns = {
  books:    b => [safe(b.name), euro(b.profitPerUnit)],
  orders:   o => [safe(bookName(o.bookId)), o.minQuantity],
  machines: m => [safe(m.name), m.availableTime]
};

function showTable(list) {
  let html = '';
  for (const item of data[list]) {
    html += '<tr>' + columns[list](item).map(cell => `<td>${cell}</td>`).join('');
    if (list !== 'orders') {
      html += `<td class="actions"><button class="edit" title="Edit" onclick="editItem('${list}', ${item.id})"><i class="bi bi-pencil"></i></button></td>`;
    }
    html += '</tr>';
  }
  $(list + '-rows').innerHTML = html || '<tr><td colspan="3" class="empty">Nothing here yet.</td></tr>';
}

for (const form of document.querySelectorAll('form[data-list]')) {
  form.onsubmit = async function (event) {
    event.preventDefault();
    form.classList.add('was-validated');

    if (!form.checkValidity()) return showMessage('Please fill in the highlighted fields correctly.', true);

    const item = {};
    for (const [key, value] of new FormData(form)) {
      item[key] = key === 'name' ? value.trim() : Number(value);
    }
    if (item.name !== undefined && item.name.length < 2) return showMessage('Name must have at least 2 characters.', true);

    const id = item.id;
    delete item.id;
    try {
      if (id) await request('PUT', `/${form.dataset.list}/${id}`, item);
      else await request('POST', '/' + form.dataset.list, item);
      resetForm(form);
      await loadAll();
      showMessage(id ? 'Changes saved.' : 'Added successfully.');
    } catch (error) {
      showMessage(error.message, true);
    }
  };
}

function editItem(list, id) {
  const form = document.querySelector(`form[data-list="${list}"]`);
  const item = data[list].find(x => x.id === id);
  for (const key in item) form.elements[key].value = item[key];
  form.querySelector('span').textContent = 'Save Changes';
  form.querySelector('.cancel').hidden = false;
}

function resetForm(form) {
  form.reset();
  form.classList.remove('was-validated');

  if (form.elements.id) {
    form.elements.id.value = '';
  }

  const label = form.querySelector('span[data-label]');
  if (label) {
    label.textContent = label.dataset.label;
  }

  const cancel = form.querySelector('.cancel');
  if (cancel) {
    cancel.hidden = true;
  }
}

function showTimes() {
  if (!data.books.length || !data.machines.length) {
    $('timesTable').innerHTML = '<tbody><tr><td class="empty">Add books and machines first.</td></tr></tbody>';
    return;
  }
  let html = '<thead><tr><th>Book</th>' + data.machines.map(m => `<th>${safe(m.name)}</th>`).join('') + '</tr></thead><tbody>';
  for (const book of data.books) {
    html += `<tr><td>${safe(book.name)}</td>`;
    for (const machine of data.machines) {
      const found = data.times.find(t => t.bookId === book.id && t.machineId === machine.id);
      html += `<td><input class="form-control" type="number" min="0" step="any" value="${found ? found.time : ''}"
                data-book="${book.id}" data-machine="${machine.id}"></td>`;
    }
    html += '</tr>';
  }
  $('timesTable').innerHTML = html + '</tbody>';
}

$('timesForm').onsubmit = async function (event) {
  event.preventDefault();
  $('timesForm').classList.add('was-validated');
  if (!$('timesForm').checkValidity()) return showMessage('Processing times must be numbers 0 or more.', true);

  try {
    for (const input of $('timesTable').querySelectorAll('input')) { if (input.value === '') continue; await request('PUT', '/processing-times', { bookId: Number(input.dataset.book), machineId: Number(input.dataset.machine), time: Number(input.value) }); }$('timesForm').classList.remove('was-validated');
    await loadAll();
    showMessage('Processing times saved.');
  } catch (error) {
    showMessage(error.message, true);
  }
};

function findMissingData() {
  if (!data.orders.length) return 'Add at least one order first.';
  if (!data.machines.length) return 'Add at least one machine first.';
  for (const order of data.orders) {
    for (const machine of data.machines) {
      if (!data.times.some(t => t.bookId === order.bookId && t.machineId === machine.id)) {
        return `Missing processing time: ${bookName(order.bookId)} on ${machine.name}.`;
      }
    }
  }
  return '';
}

function showPlanError(text) {
  $('result').hidden = true;
  $('planInfo').textContent = text;
  showMessage(text, true);
}

async function runOptimize() {
  $('planInfo').textContent = '';
  const missing = findMissingData();
  if (missing) return showPlanError(missing);

  try {
    const plan = await request('POST', '/optimize', {});
    if (plan.status === 'infeasible') {
      return showPlanError(plan.message || 'The minimum quantities cannot be met with the available machine time.');
    }
    if (plan.status !== 'optimal') return showPlanError(plan.message || 'Optimization failed. Please try again.');
    showPlan(plan);
  } catch (error) {
    showPlanError(error.message);
  }
}

function showPlan(plan) {
  $('result').hidden = false;
  $('totalProfit').textContent = euro(plan.totalProfit);$('count-profit').textContent = euro(plan.totalProfit);

  const maxProfit = Math.max(...plan.items.map(i => i.profit), 1);
  let html = '';
  let total = 0;
  for (const item of plan.items) {
    html += `<tr>
      <td>#${item.orderId} ${safe(item.bookName)}</td>
      <td>${item.quantity}</td>
      <td>${euro(item.profit)}</td>
      <td><progress value="${item.profit}" max="${maxProfit}"></progress></td>
    </tr>`;
    total += item.quantity;
  }
  $('planRows').innerHTML = html + `<tr class="total"><td>Total</td><td>${total}</td><td>${euro(plan.totalProfit)}</td><td></td></tr>`;

  $('loadList').innerHTML = plan.machines.map(m => `
    <li><span>${safe(m.machineName)}</span><span>${Math.round(m.used / m.available * 100)}%</span>
    <progress value="${m.used}" max="${m.available}"></progress>
    <small>Used: ${hours(m.used)} · Remaining: ${hours(m.remaining)}</small></li>`).join('');
}

loadAll();