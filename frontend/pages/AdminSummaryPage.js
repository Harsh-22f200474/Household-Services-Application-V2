export default {
  template: `
      <div class="container my-5">
      <div class="row">
        <div class="col-12 text-center">
          <h3 class="mb-5">Admin Summary</h3>
        </div>
      </div>

      <!-- Alert Messages -->
      <div v-if="messages.length > 0" class="row mb-3">
        <div class="col-12">
          <div v-for="(message, index) in messages" 
               :key="index" 
               :class="['alert', 'alert-' + message.category]"
               role="alert">
            {{ message.text }}
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Customer Ratings Chart -->
        <div class="col-md-6 mb-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <h4 class="card-title mb-3">Overall Customer Ratings</h4>
              <div v-if="isLoadingRatings" class="text-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <canvas v-else id="customerRatingsChart" width="400" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Service Requests Chart -->
        <div class="col-md-6 mb-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <h4 class="card-title mb-3">Service Requests Summary</h4>
              <div v-if="isLoadingRequests" class="text-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <canvas v-else id="serviceRequestsChart" width="400" height="300"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Refresh Button -->
      <div class="row mt-4">
        <div class="col-12 text-center">
          <button @click="refreshData" class="btn btn-primary" :disabled="isLoadingRatings || isLoadingRequests">
            <span v-if="isLoadingRatings || isLoadingRequests" class="spinner-border spinner-border-sm me-1" role="status"></span>
            Refresh Data
          </button>
        </div>
      </div>
    </div>
    `,
  data() {
    return {
      customerRatingsChart: null,
      serviceRequestsChart: null,
      messages: [],
      isLoadingRatings: false,
      isLoadingRequests: false,
    };
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.messages.push({
          category: "danger",
          text: "Authentication token not found. Please log in again.",
        });
        this.$router.push("/admin/login");
        return false;
      }
      return true;
    },

    async fetchCustomerRatings() {
      if (!this.checkAuth()) return;

      this.isLoadingRatings = true;
      try {
        const token = localStorage.getItem("token");
        const response = await fetch("/admin/summary/ratings", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token,
          },
        });

        if (response.status === 401 || response.status === 403) {
          this.messages.push({
            category: "danger",
            text: "Session expired. Please log in again.",
          });
          this.$router.push("/admin/login");
          return;
        }

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || "Failed to fetch ratings data");
        }

        const data = await response.json();
        console.log("Service Requests Data:", data);
        this.updateCustomerRatingsChart(data);
      } catch (error) {
        console.error("Error fetching ratings data:", error);
        this.messages.push({
          category: "danger",
          text: `Error fetching ratings data: ${error.message}`,
        });
      } finally {
        this.isLoadingRatings = false;
      }
    },

    updateCustomerRatingsChart(data) {
      const ctx = document
        .getElementById("customerRatingsChart")
        ?.getContext("2d");
      if (!ctx) return;

      if (this.customerRatingsChart) {
        this.customerRatingsChart.destroy();
      }

      // Sample data structure - you'll need to adjust based on your actual API response
      const chartData = {
        labels: ["5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"],
        datasets: [
          {
            data: [
              data.fiveStars || 30,
              data.fourStars || 25,
              data.threeStars || 20,
              data.twoStars || 15,
              data.oneStar || 10,
            ],
            backgroundColor: [
              "rgba(75, 192, 192, 0.7)",
              "rgba(54, 162, 235, 0.7)",
              "rgba(255, 206, 86, 0.7)",
              "rgba(255, 159, 64, 0.7)",
              "rgba(255, 99, 132, 0.7)",
            ],
            borderColor: [
              "rgba(75, 192, 192, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(255, 159, 64, 1)",
              "rgba(255, 99, 132, 1)",
            ],
            borderWidth: 1,
          },
        ],
      };

      this.customerRatingsChart = new Chart(ctx, {
        type: "doughnut",
        data: chartData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "right",
              labels: {
                boxWidth: 15,
                padding: 15,
              },
            },
            tooltip: {
              callbacks: {
                label: (tooltipItem) =>
                  `${tooltipItem.label}: ${tooltipItem.raw} ratings`,
              },
            },
          },
        },
      });
    },

    async fetchServiceRequests() {
      if (!this.checkAuth()) return;

      this.isLoadingRequests = true;
      try {
        const token = localStorage.getItem("token");
        const response = await fetch("/admin/summary/service_requests", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token,
          },
        });

        if (response.status === 401 || response.status === 403) {
          this.messages.push({
            category: "danger",
            text: "Session expired. Please log in again.",
          });
          this.$router.push("/admin/login");
          return;
        }

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(
            errorData.message || "Failed to fetch service requests data"
          );
        }

        const data = await response.json();
        this.updateServiceRequestsChart(data);
      } catch (error) {
        console.error("Error fetching service requests:", error);
        this.messages.push({
          category: "danger",
          text: `Error fetching service requests: ${error.message}`,
        });
      } finally {
        this.isLoadingRequests = false;
      }
    },

    updateServiceRequestsChart(data) {
      const ctx = document
        .getElementById("serviceRequestsChart")
        ?.getContext("2d");
      if (!ctx) return;

      if (this.serviceRequestsChart) {
        this.serviceRequestsChart.destroy();
      }

      const labels = data.map((item) => {
        const date = new Date(item.date);
        return date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        });
      });

      const counts = data.map((item) => item.count);

      this.serviceRequestsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Service Requests",
              data: counts,
              backgroundColor: "rgba(54, 162, 235, 0.7)",
              borderColor: "rgba(54, 162, 235, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
              },
            },
          },
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: (tooltipItem) => `Requests: ${tooltipItem.raw}`,
              },
            },
          },
        },
      });
    },

    refreshData() {
      this.messages = [];
      this.fetchCustomerRatings();
      this.fetchServiceRequests();
    },
  },
  mounted() {
    if (this.checkAuth()) {
      this.refreshData();
    }
  },
  beforeDestroy() {
    if (this.customerRatingsChart) {
      this.customerRatingsChart.destroy();
    }
    if (this.serviceRequestsChart) {
      this.serviceRequestsChart.destroy();
    }
  },
};
