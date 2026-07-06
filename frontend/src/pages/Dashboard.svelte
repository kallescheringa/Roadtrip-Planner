<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import maplibregl from 'maplibre-gl';
  import 'maplibre-gl/dist/maplibre-gl.css';
  import { push } from 'svelte-spa-router';
  import { currentUser, logout } from '../lib/auth';

  let mapContainer: HTMLDivElement;
  let map: maplibregl.Map;
  let selectedPark: { name: string; state: string; code: string; description: string } | null = null;
  let isLoading = true;

  // Route builder state
  let startLocation = '';
  let stops: string[] = [];
  let endLocation = '';
  let cyclic = false;

  function addStop() {
    stops = [...stops, ''];
  }

  function removeStop(index: number) {
    stops = stops.filter((_, i) => i !== index);
  }

  function planRoute() {
    console.log('Route:', { startLocation, stops, endLocation, cyclic });
    // TODO: send to backend -> OSRM -> draw path on map
  }

  onMount(async () => {
    map = new maplibregl.Map({
      container: mapContainer,
      style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
      center: [-98.5, 39.8],
      zoom: 3.3,
      attributionControl: false,
    });

    map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');

    map.on('load', async () => {
      const [pointsRes, boundariesRes, statesRes] = await Promise.all([
        fetch('http://localhost:8000/api/attractions/parks/'),
        fetch('http://localhost:8000/api/attractions/parks/boundaries/'),
        fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson'),
      ]);
      const pointsGeojson = await pointsRes.json();
      const boundariesGeojson = await boundariesRes.json();
      // const statesGeojson = await statesRes.json();

      // // State/province borders — add first so everything else renders on top
      // map.addSource('states', { type: 'geojson', data: statesGeojson });

      // map.addLayer({
      //   id: 'state-borders',
      //   type: 'line',
      //   source: 'states',
      //   paint: {
      //     'line-color': '#666666',
      //     'line-width': 1,
      //   },
      // });

      map.addSource('park-boundaries', { type: 'geojson', data: boundariesGeojson });

      map.addLayer({
        id: 'park-boundaries-fill',
        type: 'fill',
        source: 'park-boundaries',
        minzoom: 6,
        paint: {
          'fill-color': '#a8d5a8',  // lighter, brighter green
          'fill-opacity': 0.35,      // slightly more opaque
        },
      });

      map.addLayer({
        id: 'park-boundaries-outline',
        type: 'line',
        source: 'park-boundaries',
        minzoom: 6,
        paint: {
          'line-color': '#4a9d4a',   // darker, saturated green
          'line-width': 2,           // slightly thicker
        },
      });

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

      map.on('click', 'park-points', (e) => {
        const feature = e.features?.[0];
        if (!feature) return;
        selectedPark = feature.properties as any;
        const coords = (feature.geometry as any).coordinates.slice();
        map.flyTo({ center: coords, zoom: Math.max(map.getZoom(), 6), duration: 600 });
      });

      map.on('click', 'park-boundaries-fill', (e) => {
        const feature = e.features?.[0];
        if (!feature) return;
        selectedPark = feature.properties as any;
      });

      map.on('mouseenter', 'park-points', () => (map.getCanvas().style.cursor = 'pointer'));
      map.on('mouseleave', 'park-points', () => (map.getCanvas().style.cursor = ''));
      map.on('mouseenter', 'park-boundaries-fill', () => (map.getCanvas().style.cursor = 'pointer'));
      map.on('mouseleave', 'park-boundaries-fill', () => (map.getCanvas().style.cursor = ''));

      isLoading = false;
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
      <!-- Park overlay -->
      <button class="back-btn" on:click={closePark}>&larr; Back to route</button>
      <h2>{selectedPark.name}</h2>
      <span class="state-tag">{selectedPark.state}</span>
      <p>{selectedPark.description}</p>
    {:else}
      <!-- Route builder -->
      <h2>Plan your route</h2>

      <label>
        Start
        <input type="text" placeholder="e.g. Denver, CO" bind:value={startLocation} />
      </label>

      {#each stops as stop, i}
        <label>
          Stop {i + 1}
          <div class="stop-row">
            <input type="text" placeholder="e.g. Moab, UT" bind:value={stops[i]} />
            <button class="remove-btn" on:click={() => removeStop(i)} aria-label="Remove stop">×</button>
          </div>
        </label>
      {/each}

      <button class="add-stop-btn" on:click={addStop}>+ Add stop</button>

      <label>
        End
        <input type="text" placeholder="e.g. Salt Lake City, UT" bind:value={endLocation} />
      </label>

      <label class="checkbox-row">
        <input type="checkbox" bind:checked={cyclic} />
        Return to start
      </label>

      <button class="plan-btn" on:click={planRoute}>Plan route</button>
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
    width: 320px;
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

  label {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #7a7568;
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }

  input[type='text'] {
    font-family: inherit;
    font-size: 0.95rem;
    font-weight: 400;
    text-transform: none;
    letter-spacing: normal;
    color: #2a2a28;
    padding: 8px 10px;
    border: 1px solid #e5e4e7;
    border-radius: 8px;
  }

  input[type='text']:focus {
    outline: none;
    border-color: #1f4d3a;
  }

  .stop-row {
    display: flex;
    gap: 6px;
  }

  .stop-row input {
    flex: 1;
  }

  .remove-btn {
    background: #f4f1ea;
    border: none;
    border-radius: 8px;
    width: 32px;
    color: #7a7568;
    font-size: 1.1rem;
    cursor: pointer;
  }

  .remove-btn:hover {
    background: #ebe7dd;
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
    flex-direction: row;
    align-items: center;
    gap: 8px;
    text-transform: none;
    font-weight: 500;
    color: #3a3833;
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
</style>