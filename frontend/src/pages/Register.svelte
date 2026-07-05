<script lang="ts">
  import { push } from 'svelte-spa-router';
  import { register } from '../lib/auth';

  let username = '';
  let email = '';
  let name = '';
  let password = '';
  let error = '';

  async function handleSubmit() {
    error = '';
    try {
      await register(username, email, password, name);
      push('/login');
    } catch (e) {
      error = e.message;
    }
  }
</script>

<h1>Register</h1>
<form on:submit|preventDefault={handleSubmit}>
  <div>
    <label>Username</label>
    <input bind:value={username} required />
  </div>
  <div>
    <label>Name</label>
    <input bind:value={name} />
  </div>
  <div>
    <label>Email</label>
    <input type="email" bind:value={email} />
  </div>
  <div>
    <label>Password</label>
    <input type="password" bind:value={password} required minlength="8" />
  </div>
  {#if error}<p style="color: red">{error}</p>{/if}
  <button type="submit">Register</button>
</form>
<p>Already have an account? <a href="#/login">Login</a></p>