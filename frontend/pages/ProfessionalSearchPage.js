export default {
  template: `
      <div class="container mt-4">
        <div class="row">
          <div class="col-md-6 offset-md-3">
            <div class="card">
              <div class="card-body">
                <h3 class="card-title">Service Request Search</h3>
  
            <!-- Flash Messages -->
                <div v-if="message" :class="'alert alert-' + category" role="alert">
                  {{ message }}
            </div>
  
            <!-- Search Form -->
            <form @submit.prevent="submitSearch">
                  <div class="form-group mb-3">
                    <label for="search_type" class="form-label">Search Type</label>
                <select v-model="form.search_type" id="search_type" class="form-control" required>
                      <option value="">Select search type</option>
                  <option value="date">Date</option>
                      <option value="location">Customer Location</option>
                      <option value="pin">Customer PIN Code</option>
                </select>
              </div>

                  <div class="form-group mb-3">
                    <label for="search_text" class="form-label">Search Text</label>
                <input
                  v-model="form.search_text"
                  id="search_text"
                  type="text"
                  class="form-control"
                      :placeholder="getPlaceholder()"
                  required
                />
              </div>

              <div class="form-group text-center">
                    <button type="submit" class="btn btn-primary me-2" :disabled="isLoading">
                      <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                      {{ isLoading ? 'Searching...' : 'Search' }}
                    </button>
                    <router-link to="/professional/dashboard" class="btn btn-secondary">Cancel</router-link>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Search Results -->
        <div class="row mt-4" v-if="hasResults">
          <div class="col-md-12">
            <div class="card">
              <div class="card-body">
                <h4 class="card-title">Search Results</h4>
                <div class="table-responsive">
                  <table class="table table-striped">
              <thead>
                <tr>
                  <th>Customer Name</th>
                  <th>Service</th>
                  <th>Status</th>
                        <th>Request Date</th>
                  <th>Remarks</th>
                </tr>
              </thead>
              <tbody>
                      <tr v-for="request in searchResults" :key="request.id">
                        <td>{{ request.customer_name }}</td>
                        <td>{{ request.service_name }}</td>
                        <td>
                          <span :class="getStatusBadgeClass(request.service_status)">
                            {{ request.service_status }}
                          </span>
                        </td>
                        <td>{{ formatDate(request.date_of_request) }}</td>
                        <td>{{ request.remarks || '-' }}</td>
                      </tr>
                      <tr v-if="searchResults.length === 0">
                        <td colspan="5" class="text-center">No service requests found</td>
                </tr>
              </tbody>
            </table>
                </div>
              </div>
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
      searchResults: [],
      message: null,
      category: null,
      isLoading: false,
      hasResults: false,
    };
  },
  methods: {
    getPlaceholder() {
      switch (this.form.search_type) {
        case "date":
          return "Enter date (YYYY-MM-DD)";
        case "location":
          return "Enter customer location";
        case "pin":
          return "Enter customer PIN code";
        default:
          return "Enter search text";
      }
    },
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
      this.message = null;
      this.isLoading = true;
      this.hasResults = false;
      this.searchResults = [];

      try {
        const response = await fetch("/professional/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify(this.form),
        });

        const data = await response.json();

        if (response.ok) {
          this.searchResults = data.data.service_requests;
          this.hasResults = true;
          this.message = data.message;
          this.category = data.category;
        } else {
          this.message = data.message || "An error occurred during the search";
          this.category = data.category || "danger";
        }
      } catch (error) {
        console.error("Search error:", error);
        this.message = "An unexpected error occurred. Please try again later.";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
  },
};
