const CAMPUS = {
  center: { lat: 37.546475, lng: 126.9646916 },
  bounds: { north: 37.5521, south: 37.5408, west: 126.9568, east: 126.9726 },
  nodes: {
    gate: { name: '평화문 · 제1캠퍼스 정문 (09)', position: null, xy: [112, 392] },
    queen: { name: '순헌관 · 본관 (01)', position: null, xy: [354, 194] },
    myung: { name: '명신관 · 서관 (05)', position: null, xy: [531, 237] },
    library: { name: '중앙도서관 (22)', position: null, xy: [435, 373] },
    union: { name: '학생회관 (10)', position: null, xy: [594, 344] },
    science: { name: '과학관 (23)', position: null, xy: [716, 230] },
  },
  edges: [
    { id: 'gate-queen', from: 'gate', to: 'queen', width: 1120, slope: 3, distance: 170, stairs: false, obstacle: false, note: '폭이 넉넉하고 경사가 완만해요.' },
    { id: 'gate-myung', from: 'gate', to: 'myung', width: 870, slope: 7, distance: 135, stairs: false, obstacle: false, note: '짧지만 경사가 조금 있는 구간이에요.' },
    { id: 'queen-library', from: 'queen', to: 'library', width: 960, slope: 2, distance: 145, stairs: false, obstacle: false, note: '넓고 완만한 구간이에요.' },
    { id: 'myung-library', from: 'myung', to: 'library', width: 760, slope: 4, distance: 160, stairs: false, obstacle: false, note: '안전 여유 폭을 확인해 주세요.' },
    { id: 'myung-union', from: 'myung', to: 'union', width: 720, slope: 1, distance: 100, stairs: true, obstacle: false, note: '계단이 포함된 구간이에요.' },
    { id: 'library-union', from: 'library', to: 'union', width: 900, slope: 5, distance: 120, stairs: false, obstacle: true, note: '최근 측정에서 통로 장애물이 기록됐어요.' },
    { id: 'queen-science', from: 'queen', to: 'science', width: 820, slope: 4, distance: 210, stairs: false, obstacle: true, note: '보행 공간이 넓지만 장애물 확인이 필요해요.' },
    { id: 'science-union', from: 'science', to: 'union', width: 1040, slope: 2, distance: 160, stairs: false, obstacle: false, note: '넓고 완만한 구간이에요.' },
    { id: 'myung-science', from: 'myung', to: 'science', width: 790, slope: 9, distance: 155, stairs: false, obstacle: false, note: '경사도가 큰 구간이에요.' },
  ],
};

const presets = {
  wheelchair: { width: 650, slope: 8, margin: 100 },
  walker: { width: 520, slope: 10, margin: 80 },
  custom: null,
};
const $ = (selector) => document.querySelector(selector);
const state = { selectedRouteId: null, routes: [], map: null, overlays: [], usingGoogleMap: false, toastTimer: null };

function initPlaces() {
  const entries = Object.entries(CAMPUS.nodes);
  for (const id of ['start-place', 'end-place']) {
    const select = document.getElementById(id);
    select.innerHTML = entries.map(([key, node]) => `<option value="${key}">${node.name}</option>`).join('');
  }
  $('#start-place').value = 'gate';
  $('#end-place').value = 'library';
}

function getConditions() {
  return {
    width: Math.max(0, Number($('#width-input').value) || 0),
    slope: Math.max(0, Number($('#slope-input').value) || 0),
    margin: Math.max(0, Number($('#margin-input').value) || 0),
    avoidStairs: $('#avoid-stairs').checked,
    avoidObstacles: $('#avoid-obstacles').checked,
    preferGentle: true,
  };
}

function isEdgeUsable(edge, conditions) {
  if (edge.width < conditions.width + conditions.margin) return false;
  if (edge.slope > conditions.slope) return false;
  if (conditions.avoidStairs && edge.stairs) return false;
  if (conditions.avoidObstacles && edge.obstacle) return false;
  return true;
}

function enumerateRoutes(start, end, conditions) {
  if (start === end) return [];
  const found = [];
  const maxDepth = Object.keys(CAMPUS.nodes).length - 1;
  function walk(current, visited, path) {
    if (current === end) {
      const edges = path;
      const distance = edges.reduce((sum, edge) => sum + edge.distance, 0);
      const maxSlope = Math.max(...edges.map((edge) => edge.slope));
      const minWidth = Math.min(...edges.map((edge) => edge.width));
      const score = distance + edges.reduce((sum, edge) => sum + edge.slope * 3 + (edge.obstacle ? 120 : 0), 0);
      found.push({ id: edges.map((edge) => edge.id).join('|'), edges, nodes: [start, ...edges.map((edge) => edge.from === current ? edge.to : edge.to)], distance, maxSlope, minWidth, score });
      return;
    }
    if (path.length >= maxDepth) return;
    for (const edge of CAMPUS.edges) {
      if (!isEdgeUsable(edge, conditions)) continue;
      const next = edge.from === current ? edge.to : edge.to === current ? edge.from : null;
      if (!next || visited.has(next)) continue;
      const nextPath = [...path, edge];
      walk(next, new Set([...visited, next]), nextPath);
    }
  }
  walk(start, new Set([start]), []);
  return found;
}

function getRouteNodes(route, start) {
  const ids = [start];
  let cursor = start;
  for (const edge of route.edges) {
    cursor = edge.from === cursor ? edge.to : edge.from;
    ids.push(cursor);
  }
  return ids;
}

function formatDistance(meters) { return meters >= 1000 ? `${(meters / 1000).toFixed(1)} km` : `${meters} m`; }

function routeLabel(route, index) {
  if (index === 0) return '균형 추천';
  if (route.distance === Math.min(...state.routes.map((item) => item.distance))) return '가장 짧은 길';
  if (route.maxSlope === Math.min(...state.routes.map((item) => item.maxSlope))) return '경사 낮은 길';
  return '대안 경로';
}

function renderRoutes() {
  const list = $('#route-options');
  $('#result-count').textContent = `${state.routes.length}개`;
  if (!state.routes.length) {
    list.innerHTML = '<div class="empty-routes">입력한 조건을 모두 만족하는 경로를 찾지 못했어요.<br />기기 폭이나 허용 경사도를 조금 조정하거나, 지도에서 미확인 구간을 확인해 주세요.</div>';
    $('#segment-list').innerHTML = '<div class="empty-routes">선택할 수 있는 경로가 없습니다.</div>';
    return;
  }
  const sort = $('#sort-select').value;
  const sorted = [...state.routes].sort((a, b) => sort === 'distance' ? a.distance - b.distance : sort === 'slope' ? a.maxSlope - b.maxSlope || a.distance - b.distance : a.score - b.score);
  if (!sorted.some((route) => route.id === state.selectedRouteId)) state.selectedRouteId = sorted[0].id;
  list.innerHTML = sorted.slice(0, 3).map((route, index) => {
    const selected = route.id === state.selectedRouteId;
    const label = routeLabel(route, index);
    const stops = getRouteNodes(route, $('#start-place').value).slice(1, -1).map((id) => CAMPUS.nodes[id].name.replace(/ 앞$/, '')).join(' · ');
    return `<button class="route-card ${selected ? 'selected' : ''}" data-route-id="${route.id}" aria-pressed="${selected}">
      <div class="route-card-head"><div class="route-card-title"><span class="route-number">${String(index + 1).padStart(2, '0')}</span><h4>${label}</h4></div>${index === 0 ? '<span class="recommend-tag">조건 적합</span>' : ''}</div>
      <div class="route-metrics"><strong>${formatDistance(route.distance)}</strong><span>약 ${Math.max(2, Math.round(route.distance / 65))}분</span><i class="metric-divider"></i><span>최대 경사 ${route.maxSlope}%</span></div>
      <p class="route-reason">${stops ? `경유: ${stops}` : `${CAMPUS.nodes[$('#start-place').value].name}에서 목적지로 바로 이동해요.`}<br />통로 최소 폭 ${route.minWidth}mm · 입력 조건 충족</p>
      <div class="route-tags"><span>계단 없음</span><span>장애물 정보 확인</span><span>안전 여유 ${getConditions().margin}mm 반영</span></div>
    </button>`;
  }).join('');
  list.querySelectorAll('.route-card').forEach((button) => button.addEventListener('click', () => {
    state.selectedRouteId = button.dataset.routeId;
    renderRoutes(); renderSegments(); drawMapOverlays();
  }));
  renderSegments();
  drawMapOverlays();
}

function currentRoute() { return state.routes.find((route) => route.id === state.selectedRouteId); }

function renderSegments() {
  const route = currentRoute();
  const container = $('#segment-list');
  if (!route) return;
  const start = $('#start-place').value;
  const ids = getRouteNodes(route, start);
  container.innerHTML = route.edges.map((edge, index) => {
    const status = edge.slope >= getConditions().slope * .8 || edge.width < getConditions().width + getConditions().margin + 100 ? 'caution' : 'pass';
    const label = status === 'caution' ? '여유 확인' : '조건 적합';
    const extras = [edge.stairs ? '계단' : null, edge.obstacle ? '장애물' : null].filter(Boolean);
    return `<div class="segment-item"><span class="segment-index">${String(index + 1).padStart(2, '0')}</span><div class="segment-copy"><strong>${CAMPUS.nodes[ids[index]].name} → ${CAMPUS.nodes[ids[index + 1]].name}</strong><span>폭 ${edge.width}mm · 경사 ${edge.slope}% · ${formatDistance(edge.distance)}${extras.length ? ` · ${extras.join(', ')}` : ''} · ${edge.note}</span></div><span class="segment-status ${status}">${label}</span></div>`;
  }).join('');
}

function edgeStatus(edge) {
  const conditions = getConditions();
  if (isEdgeUsable(edge, conditions)) return edge.slope >= conditions.slope * .8 || edge.width < conditions.width + conditions.margin + 100 ? 'caution' : 'safe';
  return 'blocked';
}

function clearGoogleOverlays() { state.overlays.forEach((overlay) => overlay.setMap(null)); state.overlays = []; }

function drawMapOverlays() {
  const route = currentRoute();
  const schematicEdges = $('#schematic-edges');
  const schematicRoute = $('#schematic-route');
  const schematicPins = $('#schematic-pins');
  if (schematicEdges) {
    schematicEdges.innerHTML = CAMPUS.edges.map((edge) => {
      const a = CAMPUS.nodes[edge.from].xy; const b = CAMPUS.nodes[edge.to].xy; const status = edgeStatus(edge);
      return `<path d="M${a[0]} ${a[1]} L${b[0]} ${b[1]}" class="map-edge ${status}"/>`;
    }).join('');
    if (route) {
      const nodes = getRouteNodes(route, $('#start-place').value);
      const points = nodes.map((id) => CAMPUS.nodes[id].xy.map((n) => `${n}`).join(',')).join(' ');
      schematicRoute.innerHTML = `<polyline points="${points}" class="selected-route-line"/>`;
      schematicPins.innerHTML = nodes.map((id, index) => {
        const [x, y] = CAMPUS.nodes[id].xy; const isStart = index === 0; const isEnd = index === nodes.length - 1;
        const label = CAMPUS.nodes[id].name.replace(/ 앞$/, '');
        return `<g class="map-pin ${isStart ? 'start' : ''} ${isEnd ? 'end' : ''}" transform="translate(${x} ${y})"><circle r="11" class="pin-halo"/><circle r="5.5" class="pin-core"/><text x="0" y="-17">${label}</text></g>`;
      }).join('');
    } else { schematicRoute.innerHTML = ''; schematicPins.innerHTML = ''; }
  }
  if (state.map && state.usingGoogleMap) {
    clearGoogleOverlays();
    for (const edge of CAMPUS.edges) {
      const status = edgeStatus(edge);
      const fromPosition = CAMPUS.nodes[edge.from].position; const toPosition = CAMPUS.nodes[edge.to].position;
      if (!fromPosition || !toPosition) continue;
      const polyline = new google.maps.Polyline({ map: state.map, path: [fromPosition, toPosition], strokeColor: status === 'safe' ? '#4b956e' : status === 'caution' ? '#d29c4d' : '#cf8a75', strokeOpacity: status === 'blocked' ? .56 : .78, strokeWeight: status === 'blocked' ? 4 : 5, clickable: true, zIndex: status === 'blocked' ? 1 : 2 });
      polyline.addListener('click', () => showToast(`${CAMPUS.nodes[edge.from].name} ↔ ${CAMPUS.nodes[edge.to].name} · 폭 ${edge.width}mm · 경사 ${edge.slope}%${edge.stairs ? ' · 계단' : ''}${edge.obstacle ? ' · 장애물' : ''}`));
      state.overlays.push(polyline);
    }
    if (route) {
      const nodeIds = getRouteNodes(route, $('#start-place').value);
      const path = nodeIds.map((id) => CAMPUS.nodes[id].position);
      if (path.every(Boolean)) state.overlays.push(new google.maps.Polyline({ map: state.map, path, strokeColor: '#245b40', strokeOpacity: .96, strokeWeight: 8, zIndex: 10, clickable: false }));
      for (let index = 0; index < nodeIds.length; index += 1) {
        const id = nodeIds[index]; if (!CAMPUS.nodes[id].position) continue; const isFirst = index === 0; const isLast = index === nodeIds.length - 1;
        const marker = new google.maps.Marker({ map: state.map, position: CAMPUS.nodes[id].position, title: CAMPUS.nodes[id].name, label: { text: isFirst ? '출발' : isLast ? '도착' : String(index), color: '#315f49', fontSize: '10px', fontWeight: '700' }, icon: { path: google.maps.SymbolPath.CIRCLE, scale: 8, fillColor: isLast ? '#d98465' : '#fff', fillOpacity: 1, strokeColor: '#315f49', strokeWeight: 3 }, zIndex: 20 });
        state.overlays.push(marker);
      }
    }
  }
}

function runSearch() {
  const start = $('#start-place').value; const end = $('#end-place').value;
  if (start === end) { showToast('출발지와 도착지를 다르게 선택해 주세요.'); return; }
  const conditions = getConditions();
  state.routes = enumerateRoutes(start, end, conditions);
  state.routes.sort((a, b) => a.score - b.score);
  state.selectedRouteId = state.routes[0]?.id ?? null;
  renderRoutes();
  if (!state.routes.length) showToast('현재 조건에 맞는 경로가 없습니다. 조건을 조정해 보세요.');
  else showToast(`${state.routes.length}개의 이동 가능 경로를 찾았어요.`);
}

function showToast(message) {
  const toast = $('#toast'); toast.textContent = message; toast.classList.add('show');
  clearTimeout(state.toastTimer); state.toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
}

function openMapSettings() {
  const dialog = $('#map-settings-dialog');
  $('#api-key-input').value = localStorage.getItem('allwaysGoogleMapsApiKey') || '';
  dialog.showModal();
}

function loadGoogleMap(apiKey) {
  if (!apiKey) return;
  if (window.google?.maps) { initializeGoogleMap(); return; }
  window.initAllWaysGoogleMap = initializeGoogleMap;
  const script = document.createElement('script');
  script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&callback=initAllWaysGoogleMap&loading=async&v=weekly`;
  script.async = true; script.defer = true;
  script.onerror = () => showToast('Google 지도를 불러오지 못했어요. API 키와 브라우저 제한 설정을 확인해 주세요.');
  document.head.appendChild(script);
}

function initializeGoogleMap() {
  const mapCanvas = $('#map-canvas');
  const schematic = $('#schematic-map');
  if (!window.google?.maps || state.map) return;
  const mapDiv = document.createElement('div'); mapDiv.id = 'google-map'; mapDiv.setAttribute('aria-label', 'Google 지도 위 숙명여대 접근성 경로');
  mapDiv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;';
  mapCanvas.insertBefore(mapDiv, schematic);
  state.map = new google.maps.Map(mapDiv, {
    center: CAMPUS.center,
    zoom: 17,
    minZoom: 16,
    maxZoom: 20,
    restriction: { latLngBounds: CAMPUS.bounds, strictBounds: true },
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
    clickableIcons: false,
    gestureHandling: 'greedy',
    backgroundColor: '#f2f3ec',
  });
  state.usingGoogleMap = true;
  schematic.style.display = 'none';
  $('.campus-illustration').style.display = 'none';
  $('#map-mode-label').textContent = '실제 지도';
  $('#map-caption').textContent = '숙명여대 본캠퍼스 · Google 지도';
  $('#map-attribution').textContent = '구간 폭·경사·장애물은 시연용 임의 데이터입니다.';
  $('#recenter-map').addEventListener('click', () => state.map.setCenter(CAMPUS.center));
  drawMapOverlays();
  geocodeCampusNodes();
  showToast('Google 지도를 연결했어요. 건물 위치를 확인하고 있어요.');
}


async function geocodeCampusNodes() {
  try {
    const { Geocoder } = await google.maps.importLibrary('geocoding');
    const geocoder = new Geocoder();
    const entries = Object.entries(CAMPUS.nodes);
    await Promise.all(entries.map(async ([, node]) => {
      const placeName = node.name.replace(/\s*[·].*?\(\d+\)/, '').replace(/\s*\(\d+\)/, '');
      try {
        const response = await geocoder.geocode({ address: `${placeName}, 숙명여자대학교, 서울특별시`, bounds: CAMPUS.bounds, region: 'kr' });
        const candidate = response.results.find((result) => {
          const point = result.geometry.location.toJSON();
          return point.lat >= CAMPUS.bounds.south && point.lat <= CAMPUS.bounds.north && point.lng >= CAMPUS.bounds.west && point.lng <= CAMPUS.bounds.east;
        });
        if (candidate) node.position = candidate.geometry.location.toJSON();
      } catch (error) {
        console.warn(`장소 위치를 찾지 못했습니다: ${node.name}`, error);
      }
    }));
    drawMapOverlays();
    showToast('학교 지도에서 확인된 건물 위치를 표시했어요. 경로 수치는 시연 데이터입니다.');
  } catch (error) {
    console.error('Google Geocoding API를 사용할 수 없습니다.', error);
    showToast('건물 위치 조회 실패: Geocoding API 사용 설정을 확인해 주세요.');
  }
}

function setPreset(name) {
  document.querySelectorAll('.preset').forEach((button) => button.classList.toggle('active', button.dataset.preset === name));
  if (!presets[name]) return;
  $('#width-input').value = presets[name].width;
  $('#slope-input').value = presets[name].slope;
  $('#margin-input').value = presets[name].margin;
  runSearch();
}

function wireEvents() {
  $('#find-route').addEventListener('click', runSearch);
  $('#sort-select').addEventListener('change', renderRoutes);
  $('#swap-places').addEventListener('click', () => { const a = $('#start-place').value; $('#start-place').value = $('#end-place').value; $('#end-place').value = a; runSearch(); });
  $('#reset-profile').addEventListener('click', () => setPreset('wheelchair'));
  document.querySelectorAll('.preset').forEach((button) => button.addEventListener('click', () => setPreset(button.dataset.preset)));
  ['start-place', 'end-place', 'width-input', 'slope-input', 'margin-input', 'avoid-stairs', 'avoid-obstacles'].forEach((id) => {
    const element = document.getElementById(id);
    element.addEventListener('change', () => { if (id === 'width-input' || id === 'slope-input' || id === 'margin-input') document.querySelectorAll('.preset').forEach((button) => button.classList.toggle('active', button.dataset.preset === 'custom')); runSearch(); });
  });
  $('#open-map-settings').addEventListener('click', openMapSettings);
  $('#open-map-settings-secondary').addEventListener('click', openMapSettings);
  $('#save-map-key').addEventListener('click', () => {
    const key = $('#api-key-input').value.trim();
    if (!key) { showToast('API 키를 입력해 주세요.'); return; }
    localStorage.setItem('allwaysGoogleMapsApiKey', key);
    $('#map-settings-dialog').close();
    if (state.map) { showToast('이미 지도가 연결되어 있어요. 새로고침하면 변경된 키가 적용돼요.'); return; }
    loadGoogleMap(key);
  });
  $('#clear-map-key').addEventListener('click', () => { localStorage.removeItem('allwaysGoogleMapsApiKey'); $('#api-key-input').value = ''; $('#map-settings-dialog').close(); showToast('이 브라우저에 저장된 지도 키를 삭제했어요.'); });
  $('#recenter-map').addEventListener('click', () => { if (!state.usingGoogleMap) showToast('숙명여대 캠퍼스를 중심으로 보고 있어요.'); });
  $('#data-info').addEventListener('click', () => showToast('경로 폭·경사·장애물 값은 화면 시연을 위한 예시입니다. 로봇 실측 데이터가 아닙니다.'));
  $('#show-route-list').addEventListener('click', () => $('#recommendations').scrollIntoView({ behavior: 'smooth', block: 'start' }));
}

initPlaces();
wireEvents();
runSearch();
const savedKey = localStorage.getItem('allwaysGoogleMapsApiKey');
if (savedKey) loadGoogleMap(savedKey);

