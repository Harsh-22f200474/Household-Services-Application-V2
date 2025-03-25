<template>
  <div class="professional-dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h5>Home Page below</h5>
      <div>
        <router-link
          to="/professional/profile"
          class="btn btn-outline-primary btn-sm"
        >
          View/Edit Profile details
        </router-link>
      </div>
    </div>

    <!-- Today's Services -->
    <div class="card mb-4">
      <div class="card-header">
        <h6 class="mb-0">Today Services</h6>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Customer Name</th>
                <th>Contact Phone</th>
                <th>Location(with pin code)</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in todayRequests" :key="request.id">
                <td>{{ request.id }}</td>
                <td>{{ request.customer_name }}</td>
                <td>{{ request.contact_phone }}</td>
                <td>{{ request.address }}</td>
                <td>
                  <button
                    class="btn btn-sm btn-success me-2"
                    @click="acceptRequest(request.id)"
                    v-if="request.status === 'requested'"
                  >
                    Accept
                  </button>
                  <button
                    class="btn btn-sm btn-danger"
                    @click="rejectRequest(request.id)"
                    v-if="request.status === 'requested'"
                  >
                    Reject
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Closed Services -->
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">Closed Services</h6>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Customer Name</th>
                <th>Contact Phone</th>
                <th>Location(with pin code)</th>
                <th>Date</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in closedRequests" :key="request.id">
                <td>{{ request.id }}</td>
                <td>{{ request.customer_name }}</td>
                <td>{{ request.contact_phone }}</td>
                <td>{{ request.address }}</td>
                <td>{{ formatDate(request.completion_date) }}</td>
                <td>{{ request.customer_rating || "N/A" }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Rejection Modal -->
    <div class="modal" tabindex="-1" v-if="showRejectionModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reject Service Request</h5>
            <button
              type="button"
              class="btn-close"
              @click="closeRejectionModal"
            ></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Reason for rejection:</label>
              <textarea
                class="form-control"
                v-model="rejectionReason"
                rows="3"
                required
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="closeRejectionModal"
            >
              Cancel
            </button>
            <button type="button" class="btn btn-danger" @click="confirmReject">
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ProfessionalDashboard",
  data() {
    return {
      todayRequests: [],
      closedRequests: [],
      showRejectionModal: false,
      rejectionReason: "",
      selectedRequestId: null,
    };
  },
  methods: {
    async fetchRequests() {
      try {
        const token = localStorage.getItem("token");
        const headers = { Authorization: `Bearer ${token}` };

        const [availableRes, completedRes] = await Promise.all([
          axios.get(
            "http://localhost:5000/api/professional/service-requests/available",
            { headers }
          ),
          axios.get(
            "http://localhost:5000/api/professional/service-requests/my-requests",
            { headers }
          ),
        ]);

        this.todayRequests = availableRes.data;
        this.closedRequests = completedRes.data.filter(
          (req) => req.status === "completed"
        );
      } catch (error) {
        console.error("Error fetching requests:", error);
      }
    },
    async acceptRequest(requestId) {
      try {
        const token = localStorage.getItem("token");
        await axios.post(
          `http://localhost:5000/api/professional/service-requests/${requestId}/accept`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        this.fetchRequests();
      } catch (error) {
        console.error("Error accepting request:", error);
      }
    },
    rejectRequest(requestId) {
      this.selectedRequestId = requestId;
      this.showRejectionModal = true;
    },
    async confirmReject() {
      try {
        const token = localStorage.getItem("token");
        await axios.post(
          `http://localhost:5000/api/professional/service-requests/${this.selectedRequestId}/reject`,
          { reason: this.rejectionReason },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        this.closeRejectionModal();
        this.fetchRequests();
      } catch (error) {
        console.error("Error rejecting request:", error);
      }
    },
    closeRejectionModal() {
      this.showRejectionModal = false;
      this.rejectionReason = "";
      this.selectedRequestId = null;
    },
    formatDate(dateString) {
      if (!dateString) return "N/A";
      return new Date(dateString).toLocaleDateString();
    },
  },
  mounted() {
    this.fetchRequests();
  },
};
</script>

<style scoped>
.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
