<script lang="ts">
  import Router from 'svelte-spa-router';
  import Register from './pages/Register.svelte';
  import Login from './pages/Login.svelte';
  import Dashboard from './pages/Dashboard.svelte';

  const routes = {
    '/register': Register,
    '/login': Login,
    '/dashboard': Dashboard,
    '*': Login,
  };
</script>

<div class="app-shell">
  <header class="app-header">
    <span class="logo">Roadtrip Planner</span>
  </header>
  <main class="app-content">
    <Router {routes} />
  </main>
</div>

<style>
  :global(html, body, #app) {
    margin: 0;
    height: 100%;
  }

  .app-shell {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  .app-header {
    flex: 0 0 auto;
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 24px;
    background: #fff;
    border-bottom: 1px solid #e8e6e1;
    z-index: 10;
  }

  .logo {
    font-family: 'Poppins', system-ui, sans-serif;
    font-weight: 600;
    font-size: 1.1rem;
    color: #1f4d3a;
    letter-spacing: -0.01em;
  }

  .app-content {
    flex: 1 1 auto;
    min-height: 0;
    position: relative;
  }
</style>