export default {
  template: `
    <div class="container mt-4">
        <!-- Flash Messages -->
                <div v-if="message" :class="'alert alert-' + category" role="alert">
                        {{ message }}
                </div>        

        <!-- Loading State -->
        <div v-if="isLoading" class="text-center my-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <!-- Service Requests -->
        <div class="card mb-4">
            <div class="card-body">
                <h4 class="card-title">Pending Service Requests</h4>
                <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Customer Name</th>
                            <th>Service</th>
                            <th>Request Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                            <tr v-for="request in pendingRequests" :key="request.id">
                                <td>{{ custDict[request.customer_id]?.full_name || 'Unknown Customer' }}</td>
                                <td>{{ serviceDict[request.service_id]?.name || 'Unknown Service' }}</td>
                                <td>{{ formatDate(request.date_of_request) }}</td>
                                <td>
                                    <span :class="getStatusBadgeClass(request.service_status)">
                                        {{ request.service_status }}
                                    </span>
                                </td>
                            <td>
                                    <button 
                                        @click="updateRequestStatus(request.id, 'accepted')" 
                                        class="btn btn-success btn-sm me-2"
                                        :disabled="isUpdating"
                                    >
                                        Accept
                                    </button>
                                    <button 
                                        @click="updateRequestStatus(request.id, 'rejected')" 
                                        class="btn btn-danger btn-sm"
                                        :disabled="isUpdating"
                                    >
                                        Reject
                                    </button>
                            </td>
                        </tr>
                            <tr v-if="pendingRequests.length === 0">
                                <td colspan="5" class="text-center">No pending requests</td>
                        </tr>
                    </tbody>
                </table>
                </div>
            </div>
        </div>

        <!-- Service History -->
        <div class="card mb-4">
            <div class="card-body">
                <h4 class="card-title">Service History</h4>
                <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Customer Name</th>
                            <th>Service</th>
                            <th>Status</th>
                            <th>Completion Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="request in otherRequests" :key="request.id">
                                <td>{{ custDict[request.customer_id]?.full_name || 'Unknown Customer' }}</td>
                                <td>{{ serviceDict[request.service_id]?.name || 'Unknown Service' }}</td>
                                <td>
                                    <span :class="getStatusBadgeClass(request.service_status)">
                                        {{ request.service_status }}
                                    </span>
                                </td>
                                <td>{{ formatDate(request.date_of_completion) }}</td>
                            </tr>
                            <tr v-if="otherRequests.length === 0">
                                <td colspan="5" class="text-center">No service history</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Reviews Section -->
        <div class="card mb-4">
            <div class="card-body">
                <h4 class="card-title">My Reviews</h4>
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5 class="card-title">Average Rating</h5>
                                <h2>{{ reviewStats.average_rating?.toFixed(1) || 0 }} ★</h2>
                                <p class="mb-0">Total Reviews: {{ reviewStats.total_reviews || 0 }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <h5>Rating Distribution</h5>
                        <div v-for="i in 5" :key="i" class="mb-2">
                            <div class="d-flex align-items-center">
                                <span class="me-2" style="width: 60px;">{{ i }} stars</span>
                                <div class="progress flex-grow-1">
                                    <div 
                                        class="progress-bar bg-warning" 
                                        :style="{ width: getDistributionPercentage(i) + '%' }"
                                    ></div>
                                </div>
                                <span class="ms-2">{{ reviewStats.rating_distribution[i + '_star'] || 0 }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Customer</th>
                                <th>Rating</th>
                                <th>Comment</th>
                                <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                            <tr v-for="review in reviews" :key="review.id">
                                <td>{{ custDict[review.customer_id]?.full_name || 'Unknown Customer' }}</td>
                                <td>
                                    <span class="badge bg-warning text-dark">
                                        {{ review.rating }} ★
                                    </span>
                                </td>
                                <td>{{ review.comment || '-' }}</td>
                                <td>{{ formatDate(review.created_at) }}</td>
                            </tr>
                            <tr v-if="reviews.length === 0">
                                <td colspan="4" class="text-center">No reviews yet</td>
                        </tr>
                    </tbody>
                </table>
                </div>
            </div>
        </div>
    </div>
    `,
  data() {
    return {
      message: null,
      category: null,
      isLoading: false,
      isUpdating: false,
      serviceRequests: [],
      custDict: {},
      serviceDict: {},
      reviews: [],
      reviewStats: {
        total_reviews: 0,
        average_rating: 0,
        rating_distribution: {},
      },
    };
  },
  computed: {
    pendingRequests() {
      return this.serviceRequests.filter(
        (req) => req.service_status === "requested"
      );
    },
    otherRequests() {
      return this.serviceRequests.filter(
        (req) => req.service_status !== "requested"
      );
    },
  },
  mounted() {
    this.fetchDashboardData();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return "-";
      return new Date(dateString).toLocaleString("en-US", {
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
    getDistributionPercentage(stars) {
      const count = this.reviewStats.rating_distribution[stars + "_star"] || 0;
      const total = this.reviewStats.total_reviews || 0;
      return total > 0 ? (count / total) * 100 : 0;
    },
    async fetchDashboardData() {
      this.isLoading = true;
      try {
        await Promise.all([
          this.fetchServiceRequests(),
          this.fetchReviews(),
          this.fetchReviewStats(),
        ]);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        this.message = "Failed to load dashboard data";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
    async fetchServiceRequests() {
      try {
        const response = await fetch("/professional/requests", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch service requests");
        }

        const data = await response.json();
        this.serviceRequests = data.requests;
        this.custDict = data.customers;
        this.serviceDict = data.services;
      } catch (error) {
        console.error("Error:", error);
        this.message = "Failed to fetch service requests";
        this.category = "danger";
      }
    },
    async fetchReviews() {
      try {
        const response = await fetch("/reviews/received", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch reviews");
        }

        const data = await response.json();
        this.reviews = data.reviews;
        // Merge customer data into custDict
        this.custDict = { ...this.custDict, ...data.customers };
      } catch (error) {
        console.error("Error:", error);
        this.message = "Failed to fetch reviews";
        this.category = "danger";
      }
    },
    async fetchReviewStats() {
      try {
        const response = await fetch("/reviews/stats", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch review statistics");
        }

        const data = await response.json();
        this.reviewStats = data;
      } catch (error) {
        console.error("Error:", error);
        this.message = "Failed to fetch review statistics";
        this.category = "danger";
      }
    },
    async updateRequestStatus(requestId, status) {
      this.isUpdating = true;
      try {
        const response = await fetch(`/professional/request/${requestId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({ status }),
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          await this.fetchServiceRequests();
        }
      } catch (error) {
        console.error("Error:", error);
        this.message = "Failed to update request status";
        this.category = "danger";
      } finally {
        this.isUpdating = false;
      }
    },
  },
};
