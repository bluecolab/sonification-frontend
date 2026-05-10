// Loads CSV, transforms data, and renders a stacked Plotly area chart.
document.addEventListener('DOMContentLoaded', function() {
  const csvUrl = 'static/data/set_2/data.csv';

  const desiredOrder = ['Salinity', 'pH', 'Temperature(F)', 'Turbidity', 'Dissolved Oxygen', 'Conductivity'];

  const multipliers = {
    'Salinity': 30,
    'Dissolved Oxygen': 1,
    'Temperature(F)': 1,
    'Conductivity': 0.3,
    'pH': 10,
    'Turbidity': 1
  };

  const colorMap = {
    'Salinity': '#FF9F1C',
    'Dissolved Oxygen': '#8FE1F4',
    'Temperature(F)': '#169873',
    'Conductivity': '#2081C3',
    'pH': '#EFE9AE',
    'Turbidity': '#B57BA6'
  };

  fetch(csvUrl).then(resp => resp.text()).then(text => {
    const parsed = parseCSV(text);
    renderPlot(parsed);
  }).catch(err => {
    console.error('Failed to load CSV:', err);
    const gc = document.getElementById('graph-container');
    if (gc) gc.innerText = 'Failed to load data.';
  });

  function parseCSV(text) {
    const lines = text.trim().split(/\r?\n/).filter(Boolean);
    const header = lines[0].split(',');
    const rows = lines.slice(1).map(line => {
      // naive split (works for this simple CSV)
      const cols = line.split(',');
      const obj = {};
      header.forEach((h, i) => obj[h] = cols[i]);
      return obj;
    });
    return { header, rows };
  }

  function renderPlot(parsed) {
    const { rows } = parsed;
    const timestamps = rows.map(r => r['timestamp']);

    const traces = desiredOrder.map((varName, idx) => {
      const y = rows.map(r => {
        const raw = parseFloat(r[varName]);
        return (isNaN(raw) ? 0 : raw) * (multipliers[varName] || 1);
      });

      return {
        x: timestamps,
        y: y,
        name: varName,
        stackgroup: 'one',
        mode: 'none',
        fillcolor: colorMap[varName],
        line: { color: colorMap[varName] }
      };
    });

    const layout = {
      title: { text: 'Winter 25-26 Data', standoff: 18 },
      paper_bgcolor: '#030227',
      plot_bgcolor: '#e1e7f4e9',
      font: { color: 'white' },
      xaxis: {
        title: { text: 'Timestamp', standoff: 12 },
        showgrid: false,
        nticks: 10,
        automargin: true
      },
      yaxis: {
        title: { text: 'Sensors', standoff: 18 },
        showgrid: false,
        showticklabels: false,
        automargin: true
      },
      margin: { b: 50, l: 20, r: 20, t: 50 }
    };

    const config = { displayModeBar: false };

    const plotDiv = document.getElementById('plot');
    Plotly.newPlot(plotDiv, traces, layout, config).then(() => {
      attachRestyleHandler(plotDiv);
    });
  }

  function attachRestyleHandler(plotDiv) {
    const audioElements = document.getElementsByTagName('audio');
    plotDiv.on('plotly_restyle', function(eventdata) {
      try {
        const updatedVisibility = eventdata[0].visible;
        const changed = eventdata[1];

        if (Array.isArray(updatedVisibility)) {
          for (let i = 0; i < updatedVisibility.length; i++) {
            const vis = updatedVisibility[i];
            const audioIndex = changed[i];
            if (audioElements[audioIndex]) audioElements[audioIndex].muted = (vis === 'legendonly');
          }
        } else {
          for (let i = 0; i < changed.length; i++) {
            const audioIndex = changed[i];
            if (audioElements[audioIndex]) audioElements[audioIndex].muted = (updatedVisibility === 'legendonly');
          }
        }
      } catch (e) {
        console.debug('restyle handler error', e);
      }
    });
  }

});

// Audio controls (start / toggle) reused by the HTML page
function startAudio() {
  const playStart = document.getElementById('playStart');
  if (playStart) playStart.style.display = 'none';
  const control = document.getElementById('control');
  if (control) control.innerHTML = pauseSVG();
  const audioElements = document.getElementsByTagName('audio');
  for (let audio of audioElements) {
    audio.play();
  }
}

function toggleAudio() {
  const audioElements = document.getElementsByTagName('audio');
  for (let audio of audioElements) {
    const control = document.getElementById('control');
    if (audio.paused) {
      if (control) control.innerHTML = playSVG();
      audio.play();
    } else {
      if (control) control.innerHTML = pauseSVG();
      audio.pause();
    }
  }
}

function playSVG() {
  return '<svg width="50px" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M48 64C21.5 64 0 85.5 0 112V400c0 26.5 21.5 48 48 48H80c26.5 0 48-21.5 48-48V112c0-26.5-21.5-48-48-48H48zm192 0c-26.5 0-48 21.5-48 48V400c0 26.5 21.5 48 48 48h32c26.5 0 48-21.5 48-48V112c0-26.5-21.5-48-48-48H240z"/></svg>';
}

function pauseSVG() {
  return '<svg width="50px" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path d="M73 39c-14.8-9.1-33.4-9.4-48.5-.9S0 62.6 0 80V432c0 17.4 9.4 33.4 24.5 41.9s33.7 8.1 48.5-.9L361 297c14.3-8.7 23-24.2 23-41s-8.7-32.2-23-41L73 39z"/></svg>';
}
