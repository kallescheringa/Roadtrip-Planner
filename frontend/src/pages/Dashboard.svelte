<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import maplibregl from 'maplibre-gl';
  import 'maplibre-gl/dist/maplibre-gl.css';
  import { push } from 'svelte-spa-router';
  import { currentUser, logout, accessToken } from '../lib/auth';
  import { get } from 'svelte/store';
  import { dndzone } from 'svelte-dnd-action';

  const API = 'http://localhost:8000';

  let mapContainer: HTMLDivElement;
  let map: maplibregl.Map;
  let selectedPark: { name: string; state: string; code: string; description: string } | null = null;
  let isLoading = true;

  const generateId = () => Math.random().toString(36).substring(2, 9);

  let routePoints: Array<{ id: string; value: string }> = [
    { id: generateId(), value: '' },
    { id: generateId(), value: '' }
  ];
  let cyclic = false;

  function addStop() {
    const newStop = { id: generateId(), value: '' };
    if (routePoints.length >= 2) {
      routePoints = [
        ...routePoints.slice(0, -1),
        newStop,
        routePoints[routePoints.length - 1]
      ];
    } else {
      routePoints = [...routePoints, newStop];
    }
  }

  function removeStop(id: string) {
    if (routePoints.length > 2) {
      routePoints = routePoints.filter(p => p.id !== id);
    }
  }

  let routeGeojson: any = null;
  let nearbyParks: any[] = [];
  let isPlanning = false;
  let routeError = '';

  function handleDnd(event: any) {
    routePoints = event.detail.items;
  }

  async function planRoute() {
    routeError = '';
    isPlanning = true;

    const startLocation = routePoints[0]?.value || '';
    const endLocation = routePoints[routePoints.length - 1]?.value || '';
    const stops = routePoints.slice(1, -1).map(s => s.value).filter(val => val.trim());

    try {
      const token = get(accessToken);
      const res = await fetch(`${API}/api/routes/plan/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          start: startLocation,
          stops,
          end: endLocation,
          cyclic,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to plan route');
      }

      const data = await res.json();
      nearbyParks = data.nearby_parks;

      if (map.getSource('route')) {
        (map.getSource('route') as maplibregl.GeoJSONSource).setData(data.path);
      } else {
        map.addSource('route', { type: 'geojson', data: data.path });
        map.addLayer({
          id: 'route-line',
          type: 'line',
          source: 'route',
          paint: {
            'line-color': '#e8823c',
            'line-width': 4,
          },
        });
      }

      const coords = data.path.coordinates;
      const bounds = coords.reduce(
        (b: maplibregl.LngLatBounds, coord: [number, number]) => b.extend(coord),
        new maplibregl.LngLatBounds(coords[0], coords[0])
      );
      map.fitBounds(bounds, { padding: 60 });

    } catch (e: any) {
      routeError = e.message;
    } finally {
      isPlanning = false;
    }
  }

  function attachPointHandlers() {
    map.on('click', 'park-points', (e) => {
      const feature = e.features?.[0];
      if (!feature) return;
      selectedPark = feature.properties as any;
      const coords = (feature.geometry as any).coordinates.slice();
      map.flyTo({ center: coords, zoom: Math.max(map.getZoom(), 6), duration: 600 });
    });

    map.on('mouseenter', 'park-points', () => (map.getCanvas().style.cursor = 'pointer'));
    map.on('mouseleave', 'park-points', () => (map.getCanvas().style.cursor = ''));
  }

  function attachBoundaryHandlers() {
    map.on('click', 'park-boundaries-fill', (e) => {
      const feature = e.features?.[0];
      if (!feature) return;
      selectedPark = feature.properties as any;
    });

    map.on('mouseenter', 'park-boundaries-fill', () => (map.getCanvas().style.cursor = 'pointer'));
    map.on('mouseleave', 'park-boundaries-fill', () => (map.getCanvas().style.cursor = ''));
  }

  onMount(() => {
    map = new maplibregl.Map({
      container: mapContainer,
      style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
      center: [-98.5, 39.8],
      zoom: 3.3,
      attributionControl: false,
    });

    map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');

    // Start fetching immediately, in parallel with the basemap style.
    const pointsPromise = fetch(`${API}/api/attractions/parks/`).then((r) => r.json());
    const boundariesPromise = fetch(`${API}/api/attractions/parks/boundaries/`).then((r) => r.json());

    map.on('load', async () => {
      try {
        // 1. Points only: this is all the first view needs.
        const pointsGeojson = await pointsPromise;

        map.addSource('parks', { type: 'geojson', data: pointsGeojson });
        map.addLayer({
          id: 'park-points',
          type: 'circle',
          source: 'parks',
          maxzoom: 6,
          paint: {
            'circle-radius': 7,
            'circle-color': '#e8823c',
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
          },
        });
        attachPointHandlers();
        isLoading = false; // show the map now

        // 2. Boundaries arrive in the background.
        const boundariesGeojson = await boundariesPromise;

        map.addSource('park-boundaries', { type: 'geojson', data: boundariesGeojson });
        map.addLayer(
          {
            id: 'park-boundaries-fill',
            type: 'fill',
            source: 'park-boundaries',
            minzoom: 6,
            paint: {
              'fill-color': '#a8d5a8',
              'fill-opacity': 0.35,
            },
          },
          'park-points' // insert beneath the points layer
        );
        map.addLayer(
          {
            id: 'park-boundaries-outline',
            type: 'line',
            source: 'park-boundaries',
            minzoom: 6,
            paint: {
              'line-color': '#4a9d4a',
              'line-width': 2,
            },
          },
          'park-points'
        );
        attachBoundaryHandlers();
      } catch (e) {
        console.error('Failed to load parks', e);
        isLoading = false; // don't leave the user on an infinite spinner
      }
    });
  });

  onDestroy(() => map?.remove());

  function handleLogout() {
    logout();
    push('/login');
  }

  function closePark() {
    selectedPark = null;
  }
</script>

{#if isLoading}
  <div class="loading-overlay">
    <div class="spinner"></div>
    <p>Loading parks...</p>
  </div>
{/if}

<div class="dashboard">
  <div bind:this={mapContainer} class="map"></div>

  <div class="side-panel">
    {#if selectedPark}
      <button class="back-btn" on:click={closePark}>&larr; Back to route</button>
      <h2>{selectedPark.name}</h2>
      <span class="state-tag">{selectedPark.state}</span>
      <p>{selectedPark.description}</p>
    {:else}
      <h2>Plan your route</h2>

      <div
        class="stops-container"
        use:dndzone={{
            items: routePoints,
            flipDurationMs: 200
        }}
        on:consider={handleDnd}
        on:finalize={handleDnd}
      >
        {#each routePoints as point, i (point.id)}
          <div class="stop-item">
            <span class="drag-handle">
              {#if i === 0}
                Start
              {:else if i === routePoints.length - 1}
                End
              {:else}
                {i}
              {/if}
            </span>

            <input
              type="text"
              bind:value={point.value}
              placeholder={i === 0 ? "e.g. Denver, CO" : i === routePoints.length - 1 ? "e.g. Salt Lake City, UT" : "Stop"}
            />

            {#if i > 0 && i < routePoints.length - 1}
              <button class="remove-btn" on:click={() => removeStop(point.id)}>×</button>
            {:else}
              <div class="remove-placeholder"></div>
            {/if}
          </div>
        {/each}
      </div>

      <button class="add-stop-btn" on:click={addStop}>+ Add stop</button>

      <label class="checkbox-row">
        <input type="checkbox" bind:checked={cyclic} />
        Return to start
      </label>

      {#if routeError}
        <div class="error-message">{routeError}</div>
      {/if}
      <button class="plan-btn" on:click={planRoute} disabled={isPlanning}>
        {isPlanning ? 'Planning...' : 'Plan route'}
      </button>
    {/if}
  </div>

  <div class="user-card">
    {#if $currentUser}
      <div class="user-info">
        <span class="avatar">{$currentUser.first_name?.[0]?.toUpperCase() || 'U'}</span>
        <span class="username">{$currentUser.first_name}</span>
      </div>
    {/if}
    <button class="logout-btn" on:click={handleLogout}>Log out</button>
  </div>
</div>

<style>
  .dashboard {
    position: absolute;
    inset: 0;
  }

  .map {
    position: absolute;
    inset: 0;
  }

  .side-panel {
    position: absolute;
    top: 16px;
    left: 16px;
    bottom: 16px;
    width: 340px;
    background: #fff;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    padding: 20px;
    overflow-y: auto;
    font-family: system-ui, sans-serif;
    z-index: 5;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .side-panel h2 {
    margin: 0 0 2px 0;
    font-size: 1.2rem;
    color: #1f4d3a;
  }

  .stops-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    outline: none;
  }

  input[type='text'] {
    flex: 1;
    font-family: inherit;
    font-size: 0.95rem;
    font-weight: 400;
    text-transform: none;
    letter-spacing: normal;
    color: #2a2a28;
    padding: 8px 10px;
    border: 1px solid #e5e4e7;
    border-radius: 8px;
    min-width: 0;
  }

  input[type='text']:focus {
    outline: none;
    border-color: #1f4d3a;
  }

  .remove-btn {
    background: #f4f1ea;
    border: none;
    border-radius: 8px;
    width: 32px;
    height: 34px;
    color: #7a7568;
    font-size: 1.1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .remove-btn:hover {
    background: #ebe7dd;
  }

  .remove-placeholder {
    width: 32px;
  }

  .add-stop-btn {
    align-self: flex-start;
    background: none;
    border: none;
    color: #1f4d3a;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    padding: 4px 0;
  }

  .checkbox-row {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 8px;
    text-transform: none;
    font-weight: 500;
    color: #3a3833;
    font-size: 0.85rem;
  }

  .error-message {
    background: #fde8e8;
    color: #c32f2f;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 0.85rem;
  }

  .plan-btn {
    margin-top: auto;
    background: #1f4d3a;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 12px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
  }

  .plan-btn:hover {
    background: #163a2b;
  }

  .back-btn {
    align-self: flex-start;
    background: none;
    border: none;
    color: #7a7568;
    font-size: 0.85rem;
    cursor: pointer;
    padding: 0 0 4px 0;
  }

  .back-btn:hover {
    color: #2a2a28;
  }

  .state-tag {
    display: inline-block;
    align-self: flex-start;
    background: #f4f1ea;
    color: #7a7568;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 6px;
  }

  .side-panel p {
    font-size: 0.9rem;
    line-height: 1.5;
    color: #3a3833;
    margin: 0;
  }

  .user-card {
    position: absolute;
    top: 16px;
    right: 16px;
    background: #fff;
    border-radius: 14px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: system-ui, sans-serif;
    z-index: 5;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #1f4d3a;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .username {
    font-size: 0.9rem;
    font-weight: 500;
    color: #2a2a28;
  }

  .logout-btn {
    background: none;
    border: none;
    color: #7a7568;
    font-size: 0.85rem;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 6px;
  }

  .logout-btn:hover {
    background: #f4f1ea;
    color: #2a2a28;
  }

  .loading-overlay {
    position: fixed;
    inset: 0;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #e8e6e1;
    border-top-color: #1f4d3a;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .loading-overlay p {
    margin-top: 16px;
    color: #7a7568;
    font-family: system-ui;
  }

  .drag-handle {
    cursor: grab;
    user-select: none;
    padding: 6px 10px;
    color: #1f4d3a;
    background: #f4f1ea;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    min-width: 48px;
    text-align: center;
    box-sizing: border-box;
  }

  .stop-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }
</style>