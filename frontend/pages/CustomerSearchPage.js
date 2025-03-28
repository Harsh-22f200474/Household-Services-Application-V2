export default {
  template: `
      <div class="container mt-4">
        <div class="row">
          <div class="col-md-6 offset-md-3">
            <div class="card">
              <div class="card-body">
                <h3 class="card-title">Customer Search</h3>
                
                <!-- Flash Messages -->
                <div v-if="messages.length" class="mb-4">
                  <div v-for="(message, index) in messages" 
                       :key="index" 
                       :class="'alert alert-' + message.category"
                  >
                    {{ message.text }}
                  </div>
                </div>

                <!-- Search Form -->
                <form @submit.prevent="submitSearch">
                  <div class="form-group mb-3">
                    <label for="search_type" class="form-label">Search Type</label>
                    <select v-model="form.search_type" id="search_type" class="form-control" required>
                      <option value="">Select search type</option>
                      <option value="service">Service Type</option>
                      <option value="location">Location</option>
                      <option value="pin_code">PIN Code</option>
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
                    <router-link to="/customer/dashboard" class="btn btn-secondary">Cancel</router-link>
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
                        <th>Service Name</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Price</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="service in services" :key="service.id">
                        <td>{{ service.name }}</td>
                        <td>{{ service.service_type }}</td>
                        <td>{{ service.description }}</td>
                        <td>₹{{ service.price }}</td>
                        <td>
                          <router-link 
                            :to="'/customer/dashboard?service_type=' + service.service_type" 
                            class="btn btn-primary btn-sm"
                          >
                            View Details
                          </router-link>
                        </td>
                      </tr>
                      <tr v-if="services.length === 0">
                        <td colspan="5" class="text-center">No services found matching your criteria</td>
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
      services: [],
      messages: [],
      isLoading: false,
      hasResults: false,
    };
  },
  methods: {
    getPlaceholder() {
      switch (this.form.search_type) {
        case "service":
          return "Enter service type (e.g., Cleaning, Plumbing)";
        case "location":
          return "Enter location";
        case "pin_code":
          return "Enter 6-digit PIN code";
        default:
          return "Enter search text";
      }
    },
    async submitSearch() {
      this.messages = [];
      this.isLoading = true;
      this.hasResults = false;

      try {
        let endpoint = "/services/search?";

        if (this.form.search_type === "service") {
          endpoint += `service_type=${this.form.search_text}`;
        } else if (this.form.search_type === "pin_code") {
          endpoint += `pin_code=${this.form.search_text}`;
        } else if (this.form.search_type === "location") {
          endpoint += `location=${this.form.search_text}`;
        }

        const response = await fetch(endpoint, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        const data = await response.json();

        if (response.ok) {
          this.services = data;
          this.hasResults = true;

          if (this.services.length === 0) {
            this.messages.push({
              category: "info",
              text: "No services found matching your criteria",
            });
          } else {
            this.messages.push({
              category: "success",
              text: `Found ${this.services.length} service(s)`,
            });
          }
        } else {
          this.services = [];
          this.messages.push({
            category: data.category || "danger",
            text: data.message || "An error occurred during the search",
          });
        }
      } catch (error) {
        console.error("Search error:", error);
        this.services = [];
        this.messages.push({
          category: "danger",
          text: "An unexpected error occurred. Please try again later.",
        });
      } finally {
        this.isLoading = false;
      }
    },
  },
};
