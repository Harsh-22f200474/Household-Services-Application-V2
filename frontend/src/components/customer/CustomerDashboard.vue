<template>
  <div class="customer-dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h6>Home Page below</h6>
      <button
        class="btn btn-outline-primary"
        @click="$router.push('/customer/profile')"
      >
        View/Edit Profile details
      </button>
    </div>

    <!-- Looking For Section -->
    <div class="card mb-4">
      <div class="card-header">
        <h6 class="mb-0">Looking For?</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div
            v-for="service in services"
            :key="service.id"
            class="col-md-3 mb-3"
          >
            <div
              class="service-card p-3 border rounded text-center cursor-pointer"
              :class="{ selected: selectedService === service.id }"
              @click="selectService(service)"
            >
              {{ service.name }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Service History -->
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">Service History</h6>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Service Name</th>
                <th>Professional Name</th>
                <th>Phone no.</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in serviceHistory" :key="request.id">
                <td>{{ request.id }}</td>
                <td>{{ request.service_name }}</td>
                <td>{{ request.professional_name || "Not Assigned" }}</td>
                <td>{{ request.professional_phone || "N/A" }}</td>
                <td>{{ request.status }}</td>
                <td>
                  <button
                    v-if="
                      request.status === 'completed' && !request.customer_rating
                    "
                    class="btn btn-primary btn-sm"
                    @click="openReviewModal(request)"
                  >
                    Add Review
                  </button>
                  <button
                    v-if="request.status === 'requested'"
                    class="btn btn-danger btn-sm"
                    @click="cancelRequest(request.id)"
                  >
                    Cancel
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Review Modal -->
    <div class="modal" tabindex="-1" v-if="showReviewModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Service Remarks</h5>
            <button
              type="button"
              class="btn-close"
              @click="closeReviewModal"
            ></button>
          </div>
          <div class="modal-body">
            <div class="service-info mb-3">
              <div class="row mb-2">
                <div class="col-md-6">
                  <label class="form-label">Service Name:</label>
                  <input
                    type="text"
                    class="form-control"
                    :value="selectedRequest?.service_name"
                    readonly
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Date:</label>
                  <input
                    type="text"
                    class="form-control"
                    :value="formatDate(selectedRequest?.requested_date)"
                    readonly
                  />
                </div>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <label class="form-label">Professional Name:</label>
                  <input
                    type="text"
                    class="form-control"
                    :value="selectedRequest?.professional_name"
                    readonly
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Contact No:</label>
                  <input
                    type="text"
                    class="form-control"
                    :value="selectedRequest?.professional_phone"
                    readonly
                  />
                </div>
              </div>
            </div>

            <div class="rating mb-3">
              <label class="form-label d-block">Service rating:</label>
              <div class="stars">
                <span
                  v-for="star in 5"
                  :key="star"
                  class="star"
                  :class="{ active: star <= reviewForm.rating }"
                  @click="reviewForm.rating = star"
                  >★</span
                >
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Remarks(if any):</label>
              <textarea
                class="form-control"
                v-model="reviewForm.review"
                rows="3"
              ></textarea>
            </div>

            <div class="text-end">
              <button
                type="button"
                class="btn btn-secondary me-2"
                @click="closeReviewModal"
              >
                Close
              </button>
              <button
                type="button"
                class="btn btn-primary"
                @click="submitReview"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "CustomerDashboard",
  data() {
    return {
      services: [],
      serviceHistory: [],
      selectedService: null,
      showReviewModal: false,
      selectedRequest: null,
      reviewForm: {
        rating: 0,
        review: "",
      },
    };
  },
  methods: {
    async fetchServices() {
      try {
        const response = await axios.get(
          "http://localhost:5000/api/services/public"
        );
        this.services = response.data;
      } catch (error) {
        console.error("Error fetching services:", error);
      }
    },
    async fetchServiceHistory() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          "http://localhost:5000/api/customer/service-requests",
          { headers: { Authorization: `Bearer ${token}` } }
        );
        this.serviceHistory = response.data;
      } catch (error) {
        console.error("Error fetching service history:", error);
      }
    },
    selectService(service) {
      this.$router.push(`/customer/services/${service.id}/book`);
    },
    openReviewModal(request) {
      this.selectedRequest = request;
      this.showReviewModal = true;
    },
    closeReviewModal() {
      this.showReviewModal = false;
      this.selectedRequest = null;
      this.reviewForm = { rating: 0, review: "" };
    },
    async submitReview() {
      try {
        const token = localStorage.getItem("token");
        await axios.post(
          `http://localhost:5000/api/customer/service-requests/${this.selectedRequest.id}/review`,
          this.reviewForm,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        this.closeReviewModal();
        this.fetchServiceHistory();
      } catch (error) {
        console.error("Error submitting review:", error);
      }
    },
    async cancelRequest(requestId) {
      if (confirm("Are you sure you want to cancel this service request?")) {
        try {
          const token = localStorage.getItem("token");
          await axios.post(
            `http://localhost:5000/api/customer/service-requests/${requestId}/cancel`,
            {},
            { headers: { Authorization: `Bearer ${token}` } }
          );
          this.fetchServiceHistory();
        } catch (error) {
          console.error("Error canceling request:", error);
        }
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString();
    },
  },
  mounted() {
    this.fetchServices();
    this.fetchServiceHistory();
  },
};
</script>

<style scoped>
.service-card {
  cursor: pointer;
  transition: all 0.3s;
}
.service-card:hover {
  background-color: #f8f9fa;
}
.service-card.selected {
  background-color: #007bff;
  color: white;
}
.stars {
  display: flex;
  gap: 5px;
}
.star {
  cursor: pointer;
  font-size: 24px;
  color: #ddd;
}
.star.active {
  color: #ffc107;
}
.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
