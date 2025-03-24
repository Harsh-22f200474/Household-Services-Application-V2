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
                <label for="service" class="form-label">Service Name:</label>
                <select
                  class="form-select"
                  id="service"
                  v-model="formData.service_type"
                  required
                >
                  <option value="">Select a service</option>
                  <option
                    v-for="service in services"
                    :key="service"
                    :value="service"
                  >
                    {{ service }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label for="experience" class="form-label"
                  >Experience (in yrs):</label
                >
                <input
                  type="number"
                  class="form-control"
                  id="experience"
                  v-model="formData.experience"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="document" class="form-label"
                  >Attach documents (PDF):</label
                >
                <input
                  type="file"
                  class="form-control"
                  id="document"
                  @change="handleFileUpload"
                  accept=".pdf"
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
  name: "ProfessionalRegister",
  data() {
    return {
      services: ["Plumbing", "Electrical", "Carpentry", "Cleaning", "Painting"],
      formData: {
        email: "",
        password: "",
        fullname: "",
        service_type: "",
        experience: "",
        document: null,
        address: "",
        pincode: "",
      },
      error: null,
      loading: false,
    };
  },
  methods: {
    handleFileUpload(event) {
      this.formData.document = event.target.files[0];
    },
    async handleRegister() {
      this.loading = true;
      this.error = null;

      try {
        await authService.registerProfessional(this.formData);
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
