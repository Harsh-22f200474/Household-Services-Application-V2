export default {
  data() {
    return {
      message: null,
      category: null,
      rating: 0,
      comment: "",
      serviceRequest: null,
      professional: null,
      service: null,
      isLoading: true,
    };
  },
  async mounted() {
    await this.fetchServiceRequestDetails();
  },
  methods: {
    getStatusBadgeClass(status) {
      const statusClasses = {
        requested: "bg-warning",
        accepted: "bg-info",
        rejected: "bg-danger",
        completed: "bg-success",
      };
      return statusClasses[status.toLowerCase()] || "bg-secondary";
    },
    async fetchServiceRequestDetails() {
      try {
        const requestId = this.$route.params.id;
        console.log("Debug - Fetching service request:", requestId);

        const response = await fetch(`/customer/requests`, {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch service request details");
        }

        const requests = await response.json();
        console.log("Debug - All requests:", requests);

        this.serviceRequest = requests.find(
          (req) => req.id === parseInt(requestId)
        );
        console.log("Debug - Found service request:", this.serviceRequest);

        if (!this.serviceRequest) {
          this.message =
            "Service request not found. Please make sure you're trying to review your own service request.";
          this.category = "danger";
          return;
        }

        // Check if the service request has already been reviewed
        const reviewsResponse = await fetch("/reviews/given", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });
        const reviews = await reviewsResponse.json();
        console.log("Debug - User's reviews:", reviews);

        const hasReview = reviews.some(
          (review) => review.service_request_id === this.serviceRequest.id
        );

        if (hasReview) {
          this.message = "You have already reviewed this service request";
          this.category = "warning";
          return;
        }

        // Fetch service details
        const serviceResponse = await fetch(`/customer/services`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });
        const services = await serviceResponse.json();
        this.service = services.find(
          (s) => s.id === this.serviceRequest.service_id
        );

        // Fetch professional details
        const profResponse = await fetch(
          `/customer/professionals/${this.service.service_type}`,
          {
            headers: {
              Authorization: "Bearer " + localStorage.getItem("token"),
            },
          }
        );
        const professionals = await profResponse.json();
        this.professional = professionals.find(
          (p) => p.user_id === this.serviceRequest.professional_id
        );
      } catch (error) {
        console.error("Error fetching details:", error);
        this.message = "Error loading service request details";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
    async submitReview() {
      if (this.rating === 0) {
        this.message = "Please select a rating";
        this.category = "danger";
        return;
      }

      try {
        console.log(
          "Debug - Submitting review for service request:",
          this.serviceRequest.id
        );
        const response = await fetch(`/review/${this.serviceRequest.id}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            rating: this.rating,
            comment: this.comment,
          }),
        });

        const data = await response.json();
        console.log("Debug - Review submission response:", data);

        if (response.ok) {
          this.$router.push({
            path: "/customer/dashboard",
            query: {
              message: "Review submitted successfully",
              category: "success",
            },
          });
        } else {
          this.message =
            data.message || data.error || "Error submitting review";
          this.category = "danger";
          if (data.error === "Can only review completed services") {
            this.message =
              "You can only review completed services. Please wait until the service is marked as completed.";
          } else if (
            data.error ===
            "You are not authorized to review this service request"
          ) {
            this.message =
              data.message ||
              "You can only review service requests that belong to you.";
          }
        }
      } catch (error) {
        console.error("Error submitting review:", error);
        this.message =
          "Error submitting review. Please try again or contact support if the issue persists.";
        this.category = "danger";
      }
    },
  },
  template: `
        <div class="container my-5">
      <!-- Alert Message -->
      <div v-if="message" :class="'alert alert-' + category" role="alert">
        {{ message }}
        <div v-if="category === 'warning' || category === 'danger'" class="mt-2">
          <router-link to="/customer/dashboard" class="btn btn-primary btn-sm">Back to Dashboard</router-link>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="text-center my-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Service Request Not Found -->
      <div v-else-if="!serviceRequest" class="card shadow-sm">
        <div class="card-body">
          <h4 class="text-danger">Service Request Not Found</h4>
          <p>The service request you're trying to review could not be found or you don't have permission to access it.</p>
          <router-link to="/customer/dashboard" class="btn btn-primary">Back to Dashboard</router-link>
        </div>
      </div>

      <!-- Cannot Add Review Yet -->
      <div v-else-if="serviceRequest && serviceRequest.service_status !== 'completed'" class="card shadow-sm">
        <div class="card-body">
          <h4 class="text-warning">Cannot Add Review Yet</h4>
          <p>This service request is not completed yet. You can only add a review once the service is marked as completed.</p>
          <p>
            Current Status: 
            <span class="badge" :class="getStatusBadgeClass(serviceRequest.service_status)">
              {{ serviceRequest.service_status }}
            </span>
          </p>
          <router-link to="/customer/dashboard" class="btn btn-primary">Back to Dashboard</router-link>
        </div>
      </div>

      <!-- Add Review Form -->
      <div v-else-if="serviceRequest && professional && service" class="card shadow-sm">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">Add Review</h4>
        </div>
        <div class="card-body">
          <div class="mb-4">
            <h5>Service Details</h5>
            <p><strong>Service:</strong> {{ service.name }}</p>
            <p><strong>Professional:</strong> {{ professional.full_name }}</p>
            <p><strong>Experience:</strong> {{ professional.experience }}</p>
          </div>

          <div class="mb-4">
            <h5>Your Rating</h5>
            <div class="btn-group" role="group">
              <button 
                v-for="star in 5" 
                :key="star"
                type="button"
                class="btn"
                :class="star <= rating ? 'btn-warning' : 'btn-outline-warning'"
                @click="rating = star"
              >
                ★
              </button>
            </div>
          </div>

          <div class="mb-4">
            <label for="comment" class="form-label">Your Review (Optional)</label>
            <textarea 
              id="comment"
              v-model="comment"
              class="form-control"
              rows="3"
              placeholder="Write your review here..."
            ></textarea>
          </div>

          <div class="d-flex justify-content-between">
            <router-link to="/customer/dashboard" class="btn btn-secondary">Cancel</router-link>
            <button @click="submitReview" class="btn btn-primary">Submit Review</button>
          </div>
        </div>
      </div>
    </div>
    `,
};
