<script lang="ts">
  import { push } from 'svelte-spa-router';
  import { currentUser, logout } from '../lib/auth';

  function handleLogout() {
    logout();
    push('/login');
  }
</script>

<h1>Dashboard</h1>
{#if $currentUser}
  <p>Logged in as {$currentUser.username} ({$currentUser.email})</p>
{:else}
  <p>Not logged in</p>
{/if}
<button on:click={handleLogout}>Logout</button>