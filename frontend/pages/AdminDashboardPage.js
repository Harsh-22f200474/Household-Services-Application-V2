export default {
  data() {
    return {
      services: [],
      professionalProfile: [],
      serviceType: {},
      userDict: {},
      users: [],
      serviceRequests: [],
      profDict: {},
      message: null,
      category: null,
    };
  },
  template: `
    <div class="container my-5">
      <div v-if="message" :class="'alert alert-' + category" role="alert">
        {{ message }}
      </div>

      <!-- Manage Services -->
      <div class="mb-5">
        <h3 class="mb-3">Manage Services</h3>
        <div class="d-flex justify-content-end mb-3">
          <router-link to="/admin/services/create_services" class="btn btn-outline-success me-2">
            Create Service
          </router-link>
          <router-link to="/admin/downloadReport" class="btn btn-outline-success">
            Download Report
          </router-link>
        </div>
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Base Price</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="service in services" :key="service.id">
                <td>{{ service.id }}</td>
                <td>{{ service.name }}</td>
                <td>{{ service.service_type }}</td>
                <td>{{ service.description }}</td>
                <td>₹{{ service.price }}</td>
                <td>
                  <router-link :to="'/admin/services/update/' + service.id" class="btn btn-warning btn-sm me-2">
                    Edit
                  </router-link>
                  <button @click="deleteService(service.id)" class="btn btn-danger btn-sm">
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Manage Professionals -->
      <div class="mb-5">
        <h3 class="mb-3">Manage Professionals</h3>
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Service</th>
                <th>Experience</th>
                <th>Reviews</th>
                <th>Doc</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="professional in professionalProfile" :key="professional.id">
                <td>{{ professional.id }}</td>
                <td>{{ professional.full_name }}</td>
                <td>{{ professional.service_type }}</td>
                <td>{{ professional.experience }}</td>
                <td>{{ professional.reviews }}</td>
                <td>
                  <a href="#" @click.prevent="downloadFile(professional.filename)">
                    {{ professional.filename }}
                  </a>
                </td>
                <td>
                  <button 
                    @click="toggleApproval(professional.user_id)" 
                    :class="['btn btn-sm me-2', userDict[professional.user_id]?.approve ? 'btn-secondary' : 'btn-success']"
                  >
                    {{ userDict[professional.user_id]?.approve ? 'Reject' : 'Approve' }}
                  </button>
                  <button 
                    @click="toggleBlock(professional.user_id)" 
                    :class="['btn btn-sm', userDict[professional.user_id]?.blocked ? 'btn-success' : 'btn-danger']"
                  >
                    {{ userDict[professional.user_id]?.blocked ? 'Unblock' : 'Block' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Service Requests -->
      <div>
        <h3 class="mb-3">Service Requests</h3>
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>ID</th>
                <th>Assigned Professional</th>
                <th>Requested Date</th>
                <th>Status</th>
                <th>Customer Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="serviceRequest in serviceRequests" :key="serviceRequest.id">
                <td>{{ serviceRequest.id }}</td>
                <td>{{ profDict[serviceRequest.professional_id]?.full_name }}</td>
                <td>{{ formatDate(serviceRequest.date_of_request) }}</td>
                <td>{{ serviceRequest.service_status }}</td>
                <td>{{ serviceRequest.remarks || "" }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    `,
  mounted() {
    this.fetchServices();
    this.fetchProfessionals();
    this.fetchServiceRequests();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return "";
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    async fetchServices() {
      try {
        const response = await fetch("/admin/services", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });
        if (response.ok) {
          const data = await response.json();
          this.services = data;
        } else {
          const errorData = await response.json();
          this.message = errorData.message;
          this.category = errorData.category || "danger";
        }
      } catch (error) {
        this.message = "Error fetching services";
        this.category = "danger";
      }
    },
    async fetchProfessionals() {
      try {
        const response = await fetch("/admin/professionals", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });
        if (response.ok) {
          const data = await response.json();
          this.professionalProfile = data;
          // Create userDict from professional data
          this.userDict = data.reduce((acc, prof) => {
            acc[prof.user_id] = {
              approve: prof.approve,
              blocked: prof.blocked,
            };
            return acc;
          }, {});
        } else {
          const errorData = await response.json();
          this.message = errorData.message;
          this.category = "danger";
        }
      } catch (error) {
        this.message = "Error fetching professionals";
        this.category = "danger";
      }
    },
    async fetchServiceRequests() {
      try {
        const response = await fetch("/admin/service-requests", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });
        if (response.ok) {
          const data = await response.json();
          this.serviceRequests = data.requests;
          this.profDict = data.professionals;
        } else {
          const errorData = await response.json();
          this.message = errorData.message;
          this.category = "danger";
        }
      } catch (error) {
        this.message = "Error fetching service requests";
        this.category = "danger";
      }
    },
    async deleteService(serviceId) {
      if (!confirm("Are you sure you want to delete this service?")) return;

      try {
        const response = await fetch(`/admin/service/${serviceId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          // Remove the service from the list
          this.services = this.services.filter(
            (service) => service.id !== serviceId
          );
        }
      } catch (error) {
        console.error("Error deleting service:", error);
        this.message = "An error occurred while deleting the service";
        this.category = "danger";
      }
    },
    async toggleApproval(userId) {
      try {
        if (!userId) {
          this.message = "Invalid user ID";
          this.category = "danger";
          return;
        }

        const response = await fetch(`/admin/professional/${userId}/approve`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            approve: !this.userDict[userId]?.approve,
          }),
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          // Initialize userDict entry if it doesn't exist
          if (!this.userDict[userId]) {
            this.userDict[userId] = {};
          }
          // Update the approval status from the server response
          this.userDict[userId].approve = data.approve;

          // Refresh the professionals list to ensure we have the latest data
          await this.fetchProfessionals();
        }
      } catch (error) {
        console.error("Error in toggleApproval:", error);
        this.message = "Network error while updating approval status";
        this.category = "danger";
      }
    },
    async toggleBlock(userId) {
      try {
        const response = await fetch(`/admin/professional/${userId}/block`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            blocked: !this.userDict[userId]?.blocked,
          }),
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          this.userDict[userId].blocked = !this.userDict[userId].blocked;
        }
      } catch (error) {
        this.message = "Error updating block status";
        this.category = "danger";
      }
    },
    async toggleCustomerApproval(user) {
      try {
        const response = await fetch(`/admin/customer/${user.id}/approve`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            approve: !user.approve,
          }),
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          user.approve = !user.approve;
        }
      } catch (error) {
        this.message = "Error updating customer approval status";
        this.category = "danger";
      }
    },
    async toggleCustomerBlock(user) {
      try {
        const response = await fetch(`/admin/customer/${user.id}/block`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            blocked: !user.blocked,
          }),
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          user.blocked = !user.blocked;
        }
      } catch (error) {
        this.message = "Error updating customer block status";
        this.category = "danger";
      }
    },
    async downloadFile(filename) {
      try {
        const response = await fetch(`/download/${filename}`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          this.message = errorData.message || "Error downloading file";
          this.category = "danger";
          return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        this.message = "Error downloading file";
        this.category = "danger";
      }
    },
  },
};
