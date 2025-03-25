<template>
  <div class="customer-search">
    <h6>Search Functionality</h6>

    <!-- Search Section -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row align-items-end">
          <div class="col-md-4">
            <label class="form-label">Search by:</label>
            <select class="form-select" v-model="searchBy">
              <option value="service_name">Service name</option>
              <option value="pin">Pin Code</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label">Search text:</label>
            <div class="input-group">
              <input
                type="text"
                class="form-control"
                v-model="searchQuery"
                :placeholder="getPlaceholder()"
              />
              <button class="btn btn-primary" @click="handleSearch">
                Search
              </button>
            </div>
          </div>
        </div>

        <div class="text-muted mt-2">
          <small>(Service name/Pin Code/...)</small>
          <small class="ms-3">(Example: Salon)</small>
        </div>
      </div>
    </div>

    <!-- Best Service Packages -->
    <div class="search-results mt-4" v-if="searchResults.length > 0">
      <h6>Best {{ selectedService }} Packages</h6>
      <div class="row">
        <div
          v-for="(service, index) in searchResults"
          :key="index"
          class="col-md-6 mb-3"
        >
          <div class="card">
            <div class="card-body">
              <h6>{{ service.name }}</h6>
              <div class="d-flex align-items-center mb-2">
                <div class="rating me-2">
                  <span
                    v-for="star in 5"
                    :key="star"
                    class="star"
                    :class="{ active: star <= service.rating }"
                    >★</span
                  >
                </div>
                <small class="text-muted"
                  >({{ service.reviews_count }} reviews)</small
                >
              </div>
              <p class="mb-2">{{ service.description }}</p>
              <div class="d-flex justify-content-between align-items-center">
                <div class="price">Base Price: ₹{{ service.base_price }}</div>
                <button
                  class="btn btn-primary btn-sm"
                  @click="bookService(service)"
                >
                  Book
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div class="modal" tabindex="-1" v-if="showBookingModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Book Service</h5>
            <button
              type="button"
              class="btn-close"
              @click="closeBookingModal"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="confirmBooking">
              <div class="mb-3">
                <label class="form-label">Service Date & Time:</label>
                <input
                  type="datetime-local"
                  class="form-control"
                  v-model="bookingForm.requested_date"
                  required
                />
              </div>
              <div class="mb-3">
                <label class="form-label">Address:</label>
                <textarea
                  class="form-control"
                  v-model="bookingForm.address"
                  rows="3"
                  required
                ></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Additional Notes:</label>
                <textarea
                  class="form-control"
                  v-model="bookingForm.notes"
                  rows="2"
                ></textarea>
              </div>
              <div class="text-end">
                <button
                  type="button"
                  class="btn btn-secondary me-2"
                  @click="closeBookingModal"
                >
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary">
                  Confirm Booking
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
  name: "CustomerSearch",
  data() {
    return {
      searchBy: "service_name",
      searchQuery: "",
      selectedService: "",
      searchResults: [],
      showBookingModal: false,
      selectedServiceData: null,
      bookingForm: {
        requested_date: "",
        address: "",
        notes: "",
      },
    };
  },
  methods: {
    getPlaceholder() {
      return this.searchBy === "service_name"
        ? "Enter service name"
        : "Enter pin code";
    },
    async handleSearch() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          "http://localhost:5000/api/customer/services/search",
          {
            headers: { Authorization: `Bearer ${token}` },
            params: {
              type: this.searchBy,
              query: this.searchQuery,
            },
          }
        );
        this.searchResults = response.data;
        this.selectedService = this.searchQuery;
      } catch (error) {
        console.error("Search error:", error);
      }
    },
    bookService(service) {
      this.selectedServiceData = service;
      this.showBookingModal = true;
    },
    closeBookingModal() {
      this.showBookingModal = false;
      this.selectedServiceData = null;
      this.bookingForm = {
        requested_date: "",
        address: "",
        notes: "",
      };
    },
    async confirmBooking() {
      try {
        const token = localStorage.getItem("token");
        await axios.post(
          "http://localhost:5000/api/customer/service-requests",
          {
            service_id: this.selectedServiceData.id,
            ...this.bookingForm,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.closeBookingModal();
        this.$router.push("/customer");
      } catch (error) {
        console.error("Booking error:", error);
      }
    },
  },
  mounted() {
    // Check if there's a service parameter in the URL
    const urlParams = new URLSearchParams(window.location.search);
    const serviceParam = urlParams.get("service");
    if (serviceParam) {
      this.searchBy = "service_name";
      this.searchQuery = serviceParam;
      this.handleSearch();
    }
  },
};
</script>

<style scoped>
.rating {
  display: flex;
  gap: 2px;
}
.star {
  color: #ddd;
  font-size: 16px;
}
.star.active {
  color: #ffc107;
}
.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
