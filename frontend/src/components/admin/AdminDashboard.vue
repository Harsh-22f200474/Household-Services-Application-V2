<template>
  <div class="admin-dashboard">
    <h6>Home page/dashboard details are below</h6>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger mb-4">
      {{ error }}
    </div>

    <!-- Services Section -->
    <div class="card mb-4">
      <div class="card-header">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Services</h5>
          <button class="btn btn-primary btn-sm" @click="openNewServiceModal">
            New Service
          </button>
        </div>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Service Name</th>
                <th>Base Price</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="service in services" :key="service.id">
                <td>{{ service.id }}</td>
                <td>{{ service.name }}</td>
                <td>${{ service.base_price }}</td>
                <td>
                  <button
                    class="btn btn-sm btn-warning me-2"
                    @click="editService(service)"
                  >
                    Edit
                  </button>
                  <button
                    class="btn btn-sm btn-danger"
                    @click="deleteService(service.id)"
                  >
                    Delete
                  </button>
                </td>
              </tr>
              <tr v-if="services.length === 0">
                <td colspan="4" class="text-center">No services found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Professionals Section -->
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">Professionals</h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Service Type</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="prof in professionals" :key="prof.id">
                <td>{{ prof.id }}</td>
                <td>{{ prof.name }}</td>
                <td>{{ prof.email }}</td>
                <td>{{ prof.service_type }}</td>
                <td>{{ prof.is_verified ? "Verified" : "Pending" }}</td>
                <td>
                  <button
                    class="btn btn-sm"
                    :class="prof.is_verified ? 'btn-danger' : 'btn-success'"
                    @click="toggleProfessionalStatus(prof)"
                  >
                    {{ prof.is_verified ? "Block" : "Verify" }}
                  </button>
                </td>
              </tr>
              <tr v-if="professionals.length === 0">
                <td colspan="6" class="text-center">No professionals found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Service Requests Section -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">Service Requests</h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Assigned Professional</th>
                <th>Requested By</th>
                <th>Status(R/A/C)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in serviceRequests" :key="request.id">
                <td>{{ request.id }}</td>
                <td>{{ request.professional_name || "Not Assigned" }}</td>
                <td>{{ request.customer_name }}</td>
                <td>{{ request.status }}</td>
              </tr>
              <tr v-if="serviceRequests.length === 0">
                <td colspan="4" class="text-center">
                  No service requests found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- New Service Modal -->
    <div class="modal" tabindex="-1" v-if="showServiceModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingService ? "Edit" : "New" }} Service
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="closeServiceModal"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleServiceSubmit">
              <div class="mb-3">
                <label class="form-label">Service Name:</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="serviceForm.name"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Description:</label>
                <textarea
                  class="form-control"
                  v-model="serviceForm.description"
                  required
                ></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Base Price:</label>
                <input
                  type="number"
                  class="form-control"
                  v-model="serviceForm.base_price"
                  required
                />
              </div>
              <div class="text-end">
                <button
                  type="button"
                  class="btn btn-secondary me-2"
                  @click="closeServiceModal"
                >
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary">
                  {{ editingService ? "Update" : "Add" }}
                </button>
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
  name: "AdminDashboard",
  data() {
    return {
      services: [],
      professionals: [],
      serviceRequests: [],
      showServiceModal: false,
      editingService: null,
      serviceForm: {
        name: "",
        description: "",
        base_price: "",
      },
      error: null,
      isDevelopment: process.env.NODE_ENV === "development",
    };
  },
  methods: {
    async fetchData() {
      try {
        const token = localStorage.getItem("token");
        console.log("Using token:", token); // Debug log

        const headers = { Authorization: `Bearer ${token}` };

        // Fetch services
        const servicesRes = await axios.get(
          "http://localhost:5000/api/admin/services",
          { headers }
        );
        console.log("Services response:", servicesRes.data); // Debug log
        this.services = servicesRes.data;

        // Fetch professionals
        const professionalsRes = await axios.get(
          "http://localhost:5000/api/admin/professionals",
          { headers }
        );
        console.log("Professionals response:", professionalsRes.data); // Debug log
        this.professionals = professionalsRes.data;

        // Fetch service requests
        const requestsRes = await axios.get(
          "http://localhost:5000/api/admin/service-requests",
          { headers }
        );
        console.log("Service requests response:", requestsRes.data); // Debug log
        this.serviceRequests = requestsRes.data;
      } catch (error) {
        console.error("Error fetching data:", error);
        if (error.response) {
          console.error("Response data:", error.response.data);
          console.error("Response status:", error.response.status);
          this.error = error.response.data.error || "Error loading data";
        } else {
          this.error = "Network error occurred";
        }
      }
    },

    openNewServiceModal() {
      this.editingService = null;
      this.serviceForm = {
        name: "",
        description: "",
        base_price: "",
      };
      this.showServiceModal = true;
    },

    editService(service) {
      this.editingService = service;
      this.serviceForm = { ...service };
      this.showServiceModal = true;
    },

    closeServiceModal() {
      this.showServiceModal = false;
      this.editingService = null;
      this.serviceForm = {
        name: "",
        description: "",
        base_price: "",
      };
    },

    async handleServiceSubmit() {
      try {
        const token = localStorage.getItem("token");
        const headers = { Authorization: `Bearer ${token}` };

        if (this.editingService) {
          await axios.put(
            `http://localhost:5000/api/admin/services/${this.editingService.id}`,
            this.serviceForm,
            { headers }
          );
        } else {
          await axios.post(
            "http://localhost:5000/api/admin/services",
            this.serviceForm,
            { headers }
          );
        }

        this.closeServiceModal();
        this.fetchData();
      } catch (error) {
        console.error("Error saving service:", error);
        alert("Error saving service");
      }
    },

    async deleteService(id) {
      if (confirm("Are you sure you want to delete this service?")) {
        try {
          const token = localStorage.getItem("token");
          const headers = { Authorization: `Bearer ${token}` };

          await axios.delete(`http://localhost:5000/api/admin/services/${id}`, {
            headers,
          });
          this.fetchData();
        } catch (error) {
          console.error("Error deleting service:", error);
          alert("Error deleting service");
        }
      }
    },

    async toggleProfessionalStatus(professional) {
      try {
        const token = localStorage.getItem("token");
        const endpoint = professional.is_verified ? "block" : "verify";

        await axios.post(
          `http://localhost:5000/api/admin/professionals/${professional.id}/${endpoint}`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );

        this.fetchData();
      } catch (error) {
        console.error("Error updating professional status:", error);
      }
    },
  },
  mounted() {
    console.log("AdminDashboard mounted"); // Debug log
    this.fetchData();
  },
};
</script>

<style scoped>
.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
