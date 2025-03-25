<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header text-center">
            <h3>Service Professional Signup</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label for="email" class="form-label">Email:</label>
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
                <label for="service" class="form-label">Service Type:</label>
                <select
                  class="form-select"
                  id="service"
                  v-model="formData.service_type_id"
                  required
                >
                  <option value="">Select a service</option>
                  <option
                    v-for="service in services"
                    :key="service.id"
                    :value="service.id"
                  >
                    {{ service.name }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label for="experience" class="form-label"
                  >Experience (in years):</label
                >
                <input
                  type="number"
                  class="form-control"
                  id="experience"
                  v-model="formData.experience"
                  required
                  min="0"
                />
              </div>

              <div class="mb-3">
                <label for="description" class="form-label">Description:</label>
                <textarea
                  class="form-control"
                  id="description"
                  v-model="formData.description"
                  rows="3"
                  required
                ></textarea>
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
  name: "ProfessionalRegister",
  data() {
    return {
      services: [],
      formData: {
        username: "",
        email: "",
        password: "",
        name: "",
        service_type_id: "",
        experience: "",
        description: "",
        address: "",
        phone: "",
        role: "professional",
      },
      error: null,
      loading: false,
    };
  },
  methods: {
    async fetchServices() {
      try {
        const response = await axios.get(
          "http://localhost:5000/api/services/public"
        );
        this.services = response.data;
      } catch (err) {
        console.error("Error fetching services:", err);
        this.error = "Error loading services. Please try again later.";
      }
    },
    async handleRegister() {
      this.loading = true;
      this.error = null;

      try {
        await axios.post(
          "http://localhost:5000/api/auth/register",
          this.formData
        );

        // Show success message and redirect to login
        alert(
          "Registration successful! Please wait for admin approval before logging in."
        );
        this.$router.push("/login");
      } catch (err) {
        this.error = err.response?.data?.error || "Registration failed";
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    this.fetchServices();
  },
};
</script>
