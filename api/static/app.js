async function fetchDates() {
  const res = await fetch('/api/ingestions/dates');
  const payload = await res.json();
  if (!res.ok) {
    throw new Error(payload.detail || 'Failed to load ingestion dates');
  }
  return Array.isArray(payload) ? payload : (payload.data || []);
}

async function fetchMovies(date) {
  const res = await fetch(`/api/ingestions?date=${date}&limit=100`);
  const payload = await res.json();
  if (!res.ok) {
    throw new Error(payload.detail || 'Failed to load movies for date');
  }
  return Array.isArray(payload) ? payload : (payload.movies || []);
}

function formatDate(dateStr) {
  const date = new Date(dateStr + 'T00:00:00');
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function updateKPI(selectedDate, dates) {
  const todayCountEl = document.getElementById('todayCount');
  const todayDateEl = document.getElementById('todayDate');

  const dateData = dates.find(d => d.date === selectedDate);
  if (dateData) {
    todayCountEl.textContent = dateData.count.toLocaleString();
    todayDateEl.textContent = formatDate(dateData.date);
  } else {
    todayCountEl.textContent = '0';
    todayDateEl.textContent = 'No data for this date';
  }
}

async function init() {
  const select = document.getElementById('dateSelect');
  const summary = document.getElementById('summary');
  summary.textContent = 'Loading movies...';
  try {
    const dates = await fetchDates();

    if (!dates.length) {
      summary.textContent = 'No ingestions found yet.';
      return;
    }
    dates.forEach(row => {
      const opt = document.createElement('option');
      opt.value = row.date;
      opt.textContent = `${row.date} (${row.count})`;
      select.appendChild(opt);
    });
    select.value = dates[0].date;
    updateKPI(dates[0].date, dates);
    await loadForDate(dates[0].date);
    select.addEventListener('change', async (e) => {
      updateKPI(e.target.value, dates);
      await loadForDate(e.target.value);
    });
  } catch (error) {
    summary.textContent = `Could not load data: ${error.message}`;
  }
}

async function loadForDate(date) {
  const tbody = document.querySelector('#moviesTable tbody');
  const summary = document.getElementById('summary');
  try {
    const movies = await fetchMovies(date);
    tbody.innerHTML = '';
    summary.textContent = `Showing ${movies.length} movie${movies.length !== 1 ? 's' : ''} for ${formatDate(date)}`;
    movies.forEach(m => {
      const row = document.createElement('tr');
      const title = (m.movie_data && (m.movie_data.title || m.movie_data.original_title)) || 'Unknown title';
      const release = (m.movie_data && (m.movie_data.release_date || '')) || '';
      const extractedAt = m.extracted_at ? new Date(m.extracted_at).toLocaleString() : '';
      row.innerHTML = `
        <td>${m.tmdb_id ?? ''}</td>
        <td>${title}</td>
        <td>${release}</td>
        <td>${extractedAt}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (error) {
    summary.textContent = `Could not load movies for ${date}: ${error.message}`;
    tbody.innerHTML = '';
  }
}

function boot() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
    return;
  }
  init();
}

boot();
