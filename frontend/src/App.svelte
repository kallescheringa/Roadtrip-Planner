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

<Router {routes} />