<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header text-center">
            <h3>Customer Signup</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label for="email" class="form-label">Email ID:</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="formData.email"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="username" class="form-label">Username:</label>
                <input
                  type="text"
                  class="form-control"
                  id="username"
                  v-model="formData.username"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Password:</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="formData.password"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="name" class="form-label">Full Name:</label>
                <input
                  type="text"
                  class="form-control"
                  id="name"
                  v-model="formData.name"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="address" class="form-label">Address:</label>
                <textarea
                  class="form-control"
                  id="address"
                  v-model="formData.address"
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label for="phone" class="form-label">Phone:</label>
                <input
                  type="text"
                  class="form-control"
                  id="phone"
                  v-model="formData.phone"
                  required
                />
              </div>

              <div class="d-grid gap-2">
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  {{ loading ? "Registering..." : "Register" }}
                </button>
              </div>

              <div v-if="error" class="alert alert-danger mt-3">
                {{ error }}
              </div>

              <div class="mt-3 text-center">
                <router-link to="/login"
                  >Already have an account? Login here</router-link
                >
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "CustomerRegister",
  data() {
    return {
      formData: {
        username: "",
        email: "",
        password: "",
        name: "",
        address: "",
        phone: "",
        role: "customer", // Set the role automatically
      },
      error: null,
      loading: false,
    };
  },
  methods: {
    async handleRegister() {
      this.loading = true;
      this.error = null;

      try {
        const response = await axios.post(
          "http://localhost:5000/api/auth/register",
          this.formData
        );

        // Store the token and user data
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("user", JSON.stringify(response.data.user));

        // Redirect to customer dashboard
        this.$router.push("/customer");
      } catch (err) {
        this.error = err.response?.data?.error || "Registration failed";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
