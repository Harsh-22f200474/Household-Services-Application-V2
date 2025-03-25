<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header text-center">
            <h3>A to Z Household Services</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="email" class="form-label"
                  >Registered Email ID:</label
                >
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="email"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Password:</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="password"
                  required
                />
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary">Login</button>
              </div>

              <div class="mt-3 text-center">
                <p>
                  Create Account?
                  <router-link to="/register/customer">Customer</router-link> |
                  <router-link to="/register/professional"
                    >Register as professional</router-link
                  >
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authService } from "@/services/api";

export default {
  name: "Login",
  data() {
    return {
      email: "",
      password: "",
      error: null,
      loading: false,
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;

      try {
        const response = await authService.login({
          email: this.email,
          password: this.password,
        });

        // Redirect based on user role
        switch (response.user.role) {
          case "admin":
            this.$router.push("/admin");
            break;
          case "professional":
            this.$router.push("/professional");
            break;
          case "customer":
            this.$router.push("/customer");
            break;
        }
      } catch (err) {
        this.error = err.message || "Login failed";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
