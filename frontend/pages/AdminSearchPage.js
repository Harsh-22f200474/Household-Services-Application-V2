export default {
  template: `
      <div class="container mt-4">
        <div class="row">
          <div class="col-md-6 offset-md-3">
            <div class="card">
              <div class="card-body">
                <h3 class="card-title">Admin Search</h3>
                
                <!-- Alert Messages -->
                <div v-if="messages.length" class="mb-4">
                  <div v-for="(message, index) in messages" 
                       :key="index" 
                       :class="'alert alert-' + message.category"
                       role="alert"
                  >
                {{ message.text }}
              </div>
            </div>

                <!-- Search Form -->
            <form @submit.prevent="submitSearch">
                  <div class="form-group mb-3">
                    <label for="search_type" class="form-label">Search Type</label>
                    <select v-model="form.search_type" id="search_type" class="form-select" required>
                      <option value="">Select a type</option>
                  <option value="customer">Customer</option>
                  <option value="service">Service</option>
                  <option value="professional">Professional</option>
                </select>
              </div>
                  
                  <div class="form-group mb-4">
                    <label for="search_text" class="form-label">Search Text</label>
                    <input 
                      v-model="form.search_text" 
                      id="search_text" 
                      type="text" 
                      class="form-control"
                      placeholder="Enter search terms..."
                    />
              </div>
                  
              <div class="form-group text-center">
                    <button type="submit" class="btn btn-primary me-2" :disabled="isLoading">
                      <span v-if="isLoading" class="spinner-border spinner-border-sm me-1"></span>
                      {{ isLoading ? 'Searching...' : 'Search' }}
                    </button>
                    <router-link to="/admin/dashboard" class="btn btn-secondary">Cancel</router-link>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Search Results -->
        <div class="row mt-4" v-if="hasResults">
          <div class="col-md-12">
            <!-- Services Results -->
            <div v-if="services.length" class="card mb-4">
              <div class="card-body">
                <h4 class="card-title">Services</h4>
                <div class="table-responsive">
                  <table class="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                        <th>Type</th>
                        <th>Description</th>
                  <th>Base Price</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="service in services" :key="service.id">
                  <td>{{ service.id }}</td>
                  <td>{{ service.name }}</td>
                        <td>{{ service.service_type }}</td>
                        <td>{{ service.description }}</td>
                        <td>₹{{ service.price }}</td>
                </tr>
              </tbody>
            </table>
                </div>
              </div>
            </div>
  
            <!-- Professionals Results -->
            <div v-if="professionals.length" class="card mb-4">
              <div class="card-body">
                <h4 class="card-title">Professionals</h4>
                <div class="table-responsive">
                  <table class="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Service</th>
                  <th>Experience</th>
                  <th>Reviews</th>
                        <th>Address</th>
                        <th>Pin Code</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="professional in professionals" :key="professional.id">
                  <td>{{ professional.id }}</td>
                  <td>{{ professional.full_name }}</td>
                        <td>{{ professional.service_type }}</td>
                  <td>{{ professional.experience }}</td>
                  <td>{{ professional.reviews }}</td>
                        <td>{{ professional.address }}</td>
                        <td>{{ professional.pin_code }}</td>
                </tr>
              </tbody>
            </table>
                </div>
              </div>
            </div>
  
            <!-- Service Requests Results -->
            <div v-if="serviceRequests.length && !customers.length" class="card mb-4">
              <div class="card-body">
                <h4 class="card-title">Service Requests</h4>
                <div class="table-responsive">
                  <table class="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                        <th>Professional</th>
                        <th>Request Date</th>
                  <th>Status</th>
                        <th>Accept/Reject Date</th>
                        <th>Completion Date</th>
                        <th>Remarks</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="request in serviceRequests" :key="request.id">
                  <td>{{ request.id }}</td>
                  <td>{{ profDict[request.professional_id]?.full_name }}</td>
                        <td>{{ formatDate(request.date_of_request) }}</td>
                        <td>
                          <span :class="getStatusBadgeClass(request.service_status)">
                            {{ request.service_status }}
                          </span>
                        </td>
                        <td>{{ formatDate(request.date_of_accept_reject) }}</td>
                        <td>{{ formatDate(request.date_of_completion) }}</td>
                        <td>{{ request.remarks || '-' }}</td>
                </tr>
              </tbody>
            </table>
                </div>
              </div>
            </div>
  
            <!-- Customer Results -->
            <div v-if="customers.length" class="card mb-4">
              <div class="card-body">
                <h4 class="card-title">Customer Service History</h4>
                <div class="table-responsive">
                  <table class="table table-striped">
              <thead>
                <tr>
                  <th>Customer Name</th>
                  <th>Address</th>
                  <th>Pin Code</th>
                  <th>Service</th>
                  <th>Status</th>
                        <th>Professional</th>
                  <th>Start Date</th>
                        <th>Completion Date</th>
                  <th>Remarks</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="request in serviceRequests" :key="request.id">
                  <td>{{ custDict[request.customer_id]?.full_name }}</td>
                  <td>{{ custDict[request.customer_id]?.address }}</td>
                  <td>{{ custDict[request.customer_id]?.pin_code }}</td>
                  <td>{{ serviceDict[request.service_id]?.name }}</td>
                        <td>
                          <span :class="getStatusBadgeClass(request.service_status)">
                            {{ request.service_status }}
                          </span>
                        </td>
                        <td>{{ profDict[request.professional_id]?.full_name || '-' }}</td>
                        <td>{{ formatDate(request.date_of_request) }}</td>
                        <td>{{ formatDate(request.date_of_completion) }}</td>
                        <td>{{ request.remarks || '-' }}</td>
                </tr>
              </tbody>
            </table>
                </div>
              </div>
            </div>

            <!-- No Results Message -->
            <div v-if="!hasResults && hasSearched" class="alert alert-info">
              No results found for your search criteria.
            </div>
          </div>
        </div>
      </div>
    `,
  data() {
    return {
      form: {
        search_type: "",
        search_text: "",
      },
      services: [],
      professionals: [],
      serviceRequests: [],
      customers: [],
      messages: [],
      profDict: {},
      serviceType: {},
      custDict: {},
      serviceDict: {},
      isLoading: false,
      hasSearched: false,
    };
  },
  computed: {
    hasResults() {
      return (
        this.services.length > 0 ||
        this.professionals.length > 0 ||
        this.serviceRequests.length > 0 ||
        this.customers.length > 0
      );
    },
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return "-";
      const date = new Date(dateString);
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    getStatusBadgeClass(status) {
      const statusClasses = {
        requested: "badge bg-info",
        accepted: "badge bg-primary",
        rejected: "badge bg-danger",
        completed: "badge bg-success",
      };
      return statusClasses[status.toLowerCase()] || "badge bg-secondary";
    },
    async submitSearch() {
      this.messages = [];
      this.isLoading = true;
      this.hasSearched = true;

      try {
        const response = await fetch("/admin/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            search_type: this.form.search_type,
            search_text: this.form.search_text,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          this.customers = data.data.customers;
          this.professionals = data.data.professionals;
          this.services = data.data.services;
          this.serviceRequests = data.data.service_requests;
          this.serviceType = data.data.service_type;
          this.profDict = data.data.prof_dict;
          this.custDict = data.data.cust_dict;
          this.serviceDict = data.data.service_dict;

          if (this.hasResults) {
            this.messages.push({
              category: "success",
              text: data.message,
            });
          }
        } else {
          this.messages.push({
            category: data.category || "danger",
            text: data.message || "An error occurred during the search.",
          });
        }
      } catch (error) {
        console.error("Unexpected error:", error);
        this.messages.push({
          category: "danger",
          text: "An unexpected error occurred. Please try again later.",
        });
      } finally {
        this.isLoading = false;
      }
    },
    clearResults() {
      this.services = [];
      this.professionals = [];
      this.serviceRequests = [];
      this.customers = [];
      this.profDict = {};
      this.serviceType = {};
      this.custDict = {};
      this.serviceDict = {};
      this.messages = [];
      this.hasSearched = false;
    },
  },
  beforeDestroy() {
    this.clearResults();
  },
};
