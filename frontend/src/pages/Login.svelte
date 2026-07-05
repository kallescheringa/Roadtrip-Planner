<script lang="ts">
  import { push } from 'svelte-spa-router';
  import { login } from '../lib/auth';

  let username = '';
  let password = '';
  let error = '';

  async function handleSubmit() {
    error = '';
    try {
      await login(username, password);
      push('/dashboard');
    } catch (e) {
      error = e.message;
    }
  }
</script>

<h1>Login</h1>
<form on:submit|preventDefault={handleSubmit}>
  <div>
    <label>Username</label>
    <input bind:value={username} required />
  </div>
  <div>
    <label>Password</label>
    <input type="password" bind:value={password} required />
  </div>
  {#if error}<p style="color: red">{error}</p>{/if}
  <button type="submit">Login</button>
</form>
<p>No account? <a href="#/register">Register</a></p>