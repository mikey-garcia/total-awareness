import {getSnapshot, sendTestPush} from './http.js';
import {connect} from './websocket.js';
import {enablePush} from './push.js';

const $ = id => document.getElementById(id);

function render(snapshot) {
  const entities = snapshot.entities || [];
  $('total').textContent = snapshot.counts?.total ?? entities.length;
  $('rf').textContent = snapshot.counts?.rf ?? entities.filter(e => e.type === 'wifi_device').length;
  $('sources').textContent = new Set(entities.map(e => e.sensor).filter(Boolean)).size;
  $('updated').textContent = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'});
  $('entities').innerHTML = entities.length ? entities.map(entityCard).join('') : '<p class="muted">No entities observed yet.</p>';
}

function entityCard(entity) {
  const data = entity.data || {};
  const name = data.name || data.vendor || entity.id;
  const fields = [
    data.rssi != null && `RSSI <b>${data.rssi} dBm</b>`,
    data.channel != null && `CH <b>${data.channel}</b>`,
    entity.sensor && `SRC <b>${escapeHtml(entity.sensor)}</b>`,
  ].filter(Boolean).join('<span> · </span>');
  return `<article class="entity"><div class="entity-top"><span class="entity-name">${escapeHtml(name)}</span><span class="entity-type">${escapeHtml(entity.type)}</span></div><div class="entity-id">${escapeHtml(entity.id)}</div><div class="entity-data">${fields}</div></article>`;
}

function escapeHtml(value) {
  const node = document.createElement('div'); node.textContent = String(value); return node.innerHTML;
}

function connection(state) {
  $('live').textContent = state.toUpperCase();
  $('live').classList.toggle('live', state === 'live');
}

try { render(await getSnapshot()); } catch (error) { $('entities').innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`; }
connect(render, connection);

$('enable-push').onclick = async () => {
  try {
    await enablePush();
    $('push-status').textContent = 'ON';
    $('test-push').disabled = false;
  } catch (error) {
    $('push-status').textContent = 'ERROR';
    alert(error.message);
  }
};

$('test-push').onclick = async () => {
  try { await sendTestPush(); } catch (error) { alert(error.message); }
};
