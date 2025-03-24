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
                <label for="email" class="form-label"
                  >Email ID (Username):</label
                >
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="formData.email"
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
                <label for="fullname" class="form-label">Fullname:</label>
                <input
                  type="text"
                  class="form-control"
                  id="fullname"
                  v-model="formData.fullname"
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
                <label for="pincode" class="form-label">Pin Code:</label>
                <input
                  type="text"
                  class="form-control"
                  id="pincode"
                  v-model="formData.pincode"
                  required
                />
              </div>

              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary">Register</button>
              </div>

              <div class="mt-3 text-center">
                <router-link to="/login">Login here</router-link>
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
  name: "CustomerRegister",
  data() {
    return {
      formData: {
        email: "",
        password: "",
        fullname: "",
        address: "",
        pincode: "",
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
        await authService.registerCustomer(this.formData);
        this.$router.push("/login");
      } catch (err) {
        this.error = err.message || "Registration failed";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
