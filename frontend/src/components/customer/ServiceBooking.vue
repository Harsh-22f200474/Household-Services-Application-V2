<template>
  <div class="service-booking">
    <div class="card mb-4">
      <div class="card-header">
        <h6 class="mb-0">{{ service?.name }} Service Details</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <p><strong>Description:</strong> {{ service?.description }}</p>
            <p><strong>Base Price:</strong> ₹{{ service?.base_price }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Available Professionals -->
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">Available Professionals</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div
            v-for="professional in professionals"
            :key="professional.id"
            class="col-md-6 mb-3"
          >
            <div class="card">
              <div class="card-body">
                <h6>{{ professional.name }}</h6>
                <div class="d-flex align-items-center mb-2">
                  <div class="rating me-2">
                    <span
                      v-for="star in 5"
                      :key="star"
                      class="star"
                      :class="{ active: star <= professional.rating }"
                      >★</span
                    >
                  </div>
                  <small class="text-muted"
                    >({{ professional.reviews_count }} reviews)</small
                  >
                </div>
                <p class="mb-2">
                  Experience: {{ professional.experience }} years
                </p>
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <small class="text-muted"
                      >Completed Services:
                      {{ professional.completed_services }}</small
                    >
                  </div>
                  <button
                    class="btn btn-primary btn-sm"
                    @click="selectProfessional(professional)"
                  >
                    Select & Book
                  </button>
                </div>
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
            <h5 class="modal-title">Book {{ service?.name }} Service</h5>
            <button
              type="button"
              class="btn-close"
              @click="closeBookingModal"
            ></button>
          </div>
          <div class="modal-body">
            <div class="selected-professional mb-3">
              <h6>Selected Professional:</h6>
              <div class="d-flex align-items-center">
                <span class="me-2">{{ selectedProfessional?.name }}</span>
                <div class="rating">
                  <span
                    v-for="star in 5"
                    :key="star"
                    class="star"
                    :class="{ active: star <= selectedProfessional?.rating }"
                    >★</span
                  >
                </div>
              </div>
            </div>

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
  name: "ServiceBooking",
  data() {
    return {
      service: null,
      professionals: [],
      showBookingModal: false,
      selectedProfessional: null,
      bookingForm: {
        requested_date: "",
        address: "",
        notes: "",
      },
    };
  },
  methods: {
    async fetchServiceDetails() {
      try {
        const serviceId = this.$route.params.id;
        const response = await axios.get(
          `http://localhost:5000/api/services/public/${serviceId}`
        );
        this.service = response.data;
      } catch (error) {
        console.error("Error fetching service details:", error);
      }
    },
    async fetchProfessionals() {
      try {
        const serviceId = this.$route.params.id;
        const token = localStorage.getItem("token");
        const response = await axios.get(
          `http://localhost:5000/api/customer/services/${serviceId}/professionals`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.professionals = response.data;
      } catch (error) {
        console.error("Error fetching professionals:", error);
      }
    },
    selectProfessional(professional) {
      this.selectedProfessional = professional;
      this.showBookingModal = true;
    },
    closeBookingModal() {
      this.showBookingModal = false;
      this.selectedProfessional = null;
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
            service_id: this.service.id,
            professional_id: this.selectedProfessional.id,
            ...this.bookingForm,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.$router.push("/customer");
      } catch (error) {
        console.error("Booking error:", error);
      }
    },
  },
  mounted() {
    this.fetchServiceDetails();
    this.fetchProfessionals();
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
