// Loads CSV, transforms data, and renders a stacked Plotly area chart.
document.addEventListener('DOMContentLoaded', function() {
  const defaultDataset = 'set_2';
  const datasetSelect = document.getElementById('dataset-select');
  let activeDataset = defaultDataset;
  const datasetDisplayNames = {};

  // datasetConfigs holds parsed metadata for each dataset folder
  const datasetConfigs = {};

  // runtime config derived strictly from metadata.json for the active dataset
  let desiredOrder = [];
  let multipliers = {};
  let colorMap = {};
  let audioFileMap = {};

  if (datasetSelect) {
    datasetSelect.value = defaultDataset;
    datasetSelect.addEventListener('change', function(event) {
      const selected = event.target && event.target.value;
      if (!selected || selected === activeDataset) return;
      activeDataset = selected;
      updateAudioSources(activeDataset);
      loadDataset(activeDataset);
    });
  }

  hydrateDatasetNames().then(() => {
    loadDataset(activeDataset);
  }).catch(() => {
    // if hydration fails, still attempt to load (will validate metadata)
    loadDataset(activeDataset);
  });

  async function hydrateDatasetNames() {
    if (!datasetSelect) return;

    const options = Array.from(datasetSelect.options);
    await Promise.all(options.map(async option => {
      const datasetName = option.value;
      try {
        const resp = await fetch(`static/data/${datasetName}/metadata.json`);
        if (resp.ok) {
          const meta = await resp.json();
          datasetConfigs[datasetName] = meta;
          const label = meta.name || datasetName;
          datasetDisplayNames[datasetName] = label;
          option.textContent = label;
        } else {
          option.textContent = datasetName;
        }
      } catch (e) {
        option.textContent = datasetName;
      }
    }));
  }

  // Apply metadata config for a dataset. Returns true on success, false on invalid metadata.
  async function applyDatasetConfig(datasetName) {
    let meta = datasetConfigs[datasetName];
    if (!meta) {
      try {
        const resp = await fetch(`static/data/${datasetName}/metadata.json`);
        if (!resp.ok) throw new Error('metadata fetch failed');
        meta = await resp.json();
        datasetConfigs[datasetName] = meta;
        datasetDisplayNames[datasetName] = meta.name || datasetName;
        const opt = datasetSelect && Array.from(datasetSelect.options).find(o => o.value === datasetName);
        if (opt) opt.textContent = datasetDisplayNames[datasetName];
      } catch (e) {
        const gc = document.getElementById('graph-container');
        if (gc) gc.innerText = `Missing metadata.json for dataset: ${datasetName}`;
        return false;
      }
    }

    // Expected schema: { name, desc, metadata: { VarName: { audio_file, multipliers, graphColor } }, data_headers: [...] }
    if (!meta || !meta.metadata || !Array.isArray(meta.data_headers)) {
      const gc = document.getElementById('graph-container');
      if (gc) gc.innerText = `Invalid metadata.json for dataset: ${datasetName}`;
      return false;
    }

    // derive desiredOrder from data_headers (exclude timestamp/measurement)
    desiredOrder = meta.data_headers.filter(h => typeof h === 'string').map(h => h.trim()).filter(h => h && h.toLowerCase() !== 'timestamp' && h.toLowerCase() !== 'measurement');

    multipliers = {};
    colorMap = {};
    audioFileMap = {};

    for (const key of desiredOrder) {
      const cfg = meta.metadata[key];
      if (!cfg) {
        const gc = document.getElementById('graph-container');
        if (gc) gc.innerText = `Missing sensor metadata for '${key}' in ${datasetName}`;
        return false;
      }
      multipliers[key] = cfg.multipliers;
      colorMap[key] = cfg.graphColor;
      audioFileMap[key] = cfg.audio_file;
    }

    return true;
  }

  async function loadDataset(datasetName) {
    const ok = await applyDatasetConfig(datasetName);
    if (!ok) return;

    const csvUrl = `static/data/${datasetName}/data.csv`;
    try {
      const resp = await fetch(csvUrl);
      if (!resp.ok) throw new Error('csv fetch failed');
      const text = await resp.text();
      const parsed = parseCSV(text);
      const label = datasetDisplayNames[datasetName] || (datasetConfigs[datasetName] && datasetConfigs[datasetName].name) || datasetName;
      renderPlot(parsed, label);
    } catch (err) {
      console.error('Failed to load CSV:', err);
      const gc = document.getElementById('graph-container');
      if (gc) gc.innerText = 'Failed to load data.';
    }
  }

  async function updateAudioSources(datasetName) {
    const ok = await applyDatasetConfig(datasetName);
    if (!ok) return;

    const audioElements = document.getElementsByTagName('audio');
    for (let audio of audioElements) {
      const source = audio.querySelector('source');
      if (!source) continue;
      const fileName = audioFileMap[audio.id];
      if (!fileName) continue;

      const wasPlaying = !audio.paused;
      const nextSrc = `static/data/${datasetName}/audio/${fileName}`;
      if (source.getAttribute('src') !== nextSrc) {
        source.setAttribute('src', nextSrc);
        audio.load();
      }

      if (wasPlaying) {
        audio.play().catch(() => {});
      }
    }
  }

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

  function renderPlot(parsed, datasetLabel) {
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
      title: { text: datasetLabel, standoff: 18 },
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
