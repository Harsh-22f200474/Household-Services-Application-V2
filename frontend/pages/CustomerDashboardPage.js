import Carousel from "../components/Carousel.js";

export default {
  components: {
    Carousel,
  },
  data() {
    return {
      message: null,
      category: null,
      services: [],
      serviceType: null,
      carouselSlides: [
        {
          image: "/static/static/images/cleaning.jpg",
          alt: "Cleaning Services",
          link: "/customer/dashboard?service_type=Cleaning",
          title: "Cleaning Services",
          description:
            "Keep your home or office spotless with our professional cleaning services.",
        },
        {
          image: "/static/static/images/plumber.jpg",
          alt: "Plumbing Services",
          link: "/customer/dashboard?service_type=Plumbing",
          title: "Plumbing Services",
          description:
            "Fix leaks and plumbing issues with our experienced plumbers.",
        },
        {
          image: "/static/static/images/electrical.jpg",
          alt: "Electrical Services",
          link: "/customer/dashboard?service_type=Electrical",
          title: "Electrical Services",
          description:
            "Get reliable electrical services for your home or office needs.",
        },
        {
          image: "/static/static/images/carpentry.jpg",
          alt: "Carpentry Services",
          link: "/customer/dashboard?service_type=Carpentry",
          title: "Carpentry Services",
          description: "Expert carpentry services for all your woodwork needs.",
        },
      ],
      serviceRequests: [],
      serviceDict: {},
      profDict: {},
      professionals: [],
      isLoading: false,
      selectedServiceId: null,
      showProfessionalModal: false,
      selectedProfessionalId: null,
      reviewedRequests: new Set(),
      showCloseServiceModal: false,
      selectedRequestToClose: null,
      isClosing: false,
    };
  },
  mounted() {
    const queryParams = this.$route.query;
    if (queryParams.service_type) {
      this.serviceType = queryParams.service_type;
    }
    this.fetchServices();
    this.fetchServiceRequests();
    this.fetchReviewedRequests();
  },
  watch: {
    "$route.query.service_type": function (newServiceType) {
      this.serviceType = newServiceType;
      this.fetchServices();
      if (newServiceType) {
        this.fetchProfessionals(newServiceType);
      }
    },
  },
  methods: {
    async fetchServices() {
      try {
        this.isLoading = true;
        let endpoint = "/customer/services";
        if (this.serviceType) {
          endpoint = `/services/search?service_type=${this.serviceType}`;
        }

        const response = await fetch(endpoint, {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          this.message = errorData.message || "Error fetching services";
          this.category = errorData.category || "danger";
          return;
        }

        const data = await response.json();
        this.services = data;

        // Create service dictionary
        this.serviceDict = data.reduce((acc, service) => {
          acc[service.id] = service;
          return acc;
        }, {});
      } catch (error) {
        console.error("Error fetching services:", error);
        this.message = "An error occurred while fetching services";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },

    async fetchProfessionals(serviceType) {
      try {
        const response = await fetch(`/customer/professionals/${serviceType}`, {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          this.message = errorData.message || "Error fetching professionals";
          this.category = errorData.category || "danger";
          return;
        }

        const data = await response.json();
        this.professionals = data;

        // Create professional dictionary
        this.profDict = data.reduce((acc, prof) => {
          acc[prof.user_id] = prof;
          return acc;
        }, {});
      } catch (error) {
        console.error("Error fetching professionals:", error);
        this.message = "An error occurred while fetching professionals";
        this.category = "danger";
      }
    },

    async fetchServiceRequests() {
      try {
        const response = await fetch("/customer/requests", {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          this.message = errorData.message || "Error fetching service requests";
          this.category = errorData.category || "danger";
          return;
        }

        const data = await response.json();
        this.serviceRequests = data;
      } catch (error) {
        console.error("Error fetching service requests:", error);
        this.message = "An error occurred while fetching service requests";
        this.category = "danger";
      }
    },

    async fetchReviewedRequests() {
      try {
        const response = await fetch("/reviews/given", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });
        if (response.ok) {
          const reviews = await response.json();
          this.reviewedRequests = new Set(
            reviews.map((review) => review.service_request_id)
          );
        }
      } catch (error) {
        console.error("Error fetching reviews:", error);
      }
    },

    async showProfessionalSelection(serviceId) {
      const service = this.serviceDict[serviceId];
      if (!service) {
        this.message = "Service not found";
        this.category = "danger";
        return;
      }

      await this.fetchProfessionals(service.service_type);

      if (!this.professionals.length) {
        this.message = "No professionals available for this service";
        this.category = "warning";
        return;
      }

      this.selectedServiceId = serviceId;
      this.showProfessionalModal = true;
    },

    async createServiceRequest() {
      if (!this.selectedServiceId || !this.selectedProfessionalId) {
        this.message = "Please select a professional";
        this.category = "danger";
        return;
      }

      try {
        const response = await fetch("/customer/request", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            service_id: this.selectedServiceId,
            professional_id: this.selectedProfessionalId,
          }),
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          await this.fetchServiceRequests();
          this.showProfessionalModal = false;
          this.selectedServiceId = null;
          this.selectedProfessionalId = null;
        }
      } catch (error) {
        console.error("Error creating service request:", error);
        this.message = "An error occurred while processing your request";
        this.category = "danger";
      }
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

    async closeServiceRequest(request) {
      console.log("Debug - Opening close modal for request:", request);
      this.selectedRequestToClose = request;
      this.showCloseServiceModal = true;
    },

    async confirmCloseService() {
      this.isClosing = true;
      console.log(
        "Debug - Attempting to close request:",
        this.selectedRequestToClose
      );
      try {
        const response = await fetch(
          `/customer/request/${this.selectedRequestToClose.id}/close`,
          {
            method: "PUT",
            headers: {
              Authorization: "Bearer " + localStorage.getItem("token"),
              "Content-Type": "application/json",
            },
          }
        );

        const data = await response.json();
        console.log("Debug - Close service response:", data);

        if (!response.ok) {
          throw new Error(data.message || "Failed to close service request");
        }

        this.message = data.message;
        this.category = data.category;
        await this.fetchServiceRequests();
      } catch (error) {
        console.error("Debug - Error closing service:", error);
        this.message = error.message;
        this.category = "danger";
      } finally {
        this.isClosing = false;
        this.showCloseServiceModal = false;
        this.selectedRequestToClose = null;
      }
    },

    cancelCloseService() {
      this.showCloseServiceModal = false;
      this.selectedRequestToClose = null;
    },
  },
  template: `
    <div class="container my-5">
      <!-- Alert Message -->
      <div v-if="message" :class="'alert alert-' + category" role="alert">
        {{ message }}
      </div>

      <!-- Global Loading Indicator -->
      <div v-if="isLoading" class="text-center my-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Close Service Confirmation Modal -->
      <div v-if="showCloseServiceModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Close Service Request</h5>
              <button type="button" class="btn-close" @click="cancelCloseService"></button>
            </div>
            <div class="modal-body">
              <div class="alert alert-warning">
                <p class="mb-0">
                  Are you sure you want to close this service request? This action cannot be undone and will mark the service as completed.
                </p>
              </div>
              <div v-if="selectedRequestToClose">
                <p><strong>Service:</strong> {{ serviceDict[selectedRequestToClose.service_id]?.name }}</p>
                <p><strong>Professional:</strong> {{ profDict[selectedRequestToClose.professional_id]?.full_name }}</p>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="cancelCloseService">Cancel</button>
              <button type="button" class="btn btn-success" @click="confirmCloseService" :disabled="isClosing">
                {{ isClosing ? 'Closing...' : 'Confirm Close Service' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Professional Selection Modal -->
      <div v-if="showProfessionalModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Select Professional</h5>
              <button type="button" class="btn-close" @click="showProfessionalModal = false"></button>
            </div>
            <div class="modal-body">
              <div class="list-group">
                <button 
                  v-for="prof in professionals" 
                  :key="prof.user_id"
                  class="list-group-item list-group-item-action"
                  :class="{ active: selectedProfessionalId === prof.user_id }"
                  @click="selectedProfessionalId = prof.user_id"
                >
                  <div class="d-flex justify-content-between align-items-center">
                    <h6 class="mb-1">{{ prof.full_name }}</h6>
                    <small>{{ prof.experience }} yrs</small>
                  </div>
                  <p class="mb-1">Rating: {{ prof.reviews }} ★</p>
                  <small>{{ prof.address }}</small>
                </button>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showProfessionalModal = false">Cancel</button>
              <button 
                type="button" 
                class="btn btn-primary" 
                @click="createServiceRequest"
                :disabled="!selectedProfessionalId"
              >
                Request Service
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div v-else>
        <div class="row mb-4">
          <div class="col-12 text-center">
            <h3 class="mb-4">Customer Dashboard</h3>
          </div>
        </div>

        <!-- Available Services Card -->
        <div class="card mb-4 shadow-sm">
          <div class="card-body">
            <h4 class="card-title mb-3">Available Services</h4>
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Service Name</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Price</th>
                    <th class="text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="service in services" :key="service.id">
                    <td>{{ service.name }}</td>
                    <td>{{ service.service_type }}</td>
                    <td>{{ service.description }}</td>
                    <td>₹{{ service.price }}</td>
                    <td class="text-center">
                      <button 
                        @click="showProfessionalSelection(service.id)" 
                        class="btn btn-primary btn-sm"
                        :disabled="serviceRequests.some(req => 
                          req.service_id === service.id && 
                          ['requested', 'accepted'].includes(req.service_status.toLowerCase())
                        )"
                      >
                        Request Service
                      </button>
                    </td>
                  </tr>
                  <tr v-if="services.length === 0">
                    <td colspan="5" class="text-center">No services available</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Service History Card -->
        <div class="card mb-4 shadow-sm">
          <div class="card-body">
            <h4 class="card-title mb-3">Service History</h4>
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Service Name</th>
                    <th>Professional</th>
                    <th>Status</th>
                    <th class="text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in serviceRequests" :key="request.id">
                    <td>{{ serviceDict[request.service_id]?.name }}</td>
                    <td>{{ profDict[request.professional_id]?.full_name || 'Not Assigned' }}</td>
                    <td>
                      <span :class="getStatusBadgeClass(request.service_status)">
                        {{ request.service_status }}
                      </span>
                    </td>
                    <td class="text-center">
                      <button 
                        v-if="request.service_status === 'accepted'" 
                        @click="closeServiceRequest(request)" 
                        class="btn btn-success btn-sm"
                      >
                        Close Service
                      </button>
                      <router-link 
                        v-if="request.service_status === 'completed' && !reviewedRequests.has(request.id)" 
                        :to="'/customer/review/' + request.id" 
                        class="btn btn-primary btn-sm"
                      >
                        Add Review
                      </router-link>
                      <span v-else-if="request.service_status === 'completed' && reviewedRequests.has(request.id)">
                        Already Reviewed
                      </span>
                      <span v-else-if="request.service_status === 'requested'">
                        Pending
                      </span>
                    </td>
                  </tr>
                  <tr v-if="serviceRequests.length === 0">
                    <td colspan="4" class="text-center">No service requests found</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
};
