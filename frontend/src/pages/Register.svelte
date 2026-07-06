<script lang="ts">
  import { push } from 'svelte-spa-router';
  import { register } from '../lib/auth';

  let firstName = '';
  let lastName = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let error = '';
  let isLoading = false;

  async function handleSubmit() {
    error = '';

    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      return;
    }

    if (password.length < 8) {
      error = 'Password must be at least 8 characters';
      return;
    }

    isLoading = true;
    try {
      await register(email, password, firstName, lastName);
      push('/login');
    } catch (e) {
      error = e.message;
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="register-container">
  <div class="register-card">
    <h1>Create Account</h1>
    <p class="subtitle">Join Roadtrip Planner</p>

    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-row">
        <div class="form-group">
          <label for="firstName">First Name</label>
          <input
            id="firstName"
            type="text"
            bind:value={firstName}
            placeholder="John"
            required
            disabled={isLoading}
          />
        </div>

        <div class="form-group">
          <label for="lastName">Last Name</label>
          <input
            id="lastName"
            type="text"
            bind:value={lastName}
            placeholder="Doe"
            required
            disabled={isLoading}
          />
        </div>
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          placeholder="john@example.com"
          required
          disabled={isLoading}
        />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          placeholder="At least 8 characters"
          required
          minlength="8"
          disabled={isLoading}
        />
      </div>

      <div class="form-group">
        <label for="confirmPassword">Confirm Password</label>
        <input
          id="confirmPassword"
          type="password"
          bind:value={confirmPassword}
          placeholder="Repeat your password"
          required
          minlength="8"
          disabled={isLoading}
        />
      </div>

      {#if error}
        <div class="error-message">{error}</div>
      {/if}

      <button type="submit" class="submit-btn" disabled={isLoading}>
        {isLoading ? 'Creating account...' : 'Create Account'}
      </button>
    </form>

    <p class="login-link">
      Already have an account? <a href="#/login">Log in</a>
    </p>
  </div>
</div>

<style>
  .register-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #f4f1ea 0%, #ebe7dd 100%);
    font-family: system-ui, sans-serif;
    padding: 16px;
  }

  .register-card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    padding: 48px 40px;
    width: 100%;
    max-width: 500px;
  }

  h1 {
    margin: 0 0 8px 0;
    font-size: 1.8rem;
    color: #1f4d3a;
    text-align: center;
    font-weight: 700;
  }

  .subtitle {
    margin: 0 0 32px 0;
    font-size: 0.95rem;
    color: #7a7568;
    text-align: center;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #7a7568;
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }

  input {
    font-family: inherit;
    font-size: 1rem;
    padding: 12px 14px;
    border: 2px solid #e8e6e1;
    border-radius: 10px;
    color: #2a2a28;
    transition: all 0.2s;
  }

  input:focus {
    outline: none;
    border-color: #1f4d3a;
    box-shadow: 0 0 0 3px rgba(31, 77, 58, 0.1);
  }

  input:disabled {
    background: #f4f1ea;
    cursor: not-allowed;
  }

  .error-message {
    background: #fde8e8;
    color: #c32f2f;
    padding: 12px;
    border-radius: 8px;
    font-size: 0.9rem;
    margin-top: -8px;
  }

  .submit-btn {
    background: #1f4d3a;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 14px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    margin-top: 12px;
  }

  .submit-btn:hover:not(:disabled) {
    background: #163a2b;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(31, 77, 58, 0.2);
  }

  .submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .login-link {
    text-align: center;
    font-size: 0.9rem;
    color: #7a7568;
    margin: 20px 0 0 0;
  }

  .login-link a {
    color: #1f4d3a;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s;
  }

  .login-link a:hover {
    color: #e8823c;
  }

  @media (max-width: 480px) {
    .form-row {
      grid-template-columns: 1fr;
    }

    .register-card {
      padding: 32px 24px;
    }
  }
</style>