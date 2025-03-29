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
            <div class="card-body" style="height: 400px;">
              <h4 class="card-title mb-3">Overall Customer Ratings</h4>
              <div v-if="isLoadingRatings" class="text-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else style="position: relative; height: 300px;">
                <canvas ref="customerRatingsChart" id="customerRatingsChart"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Service Requests Chart -->
        <div class="col-md-6 mb-4">
          <div class="card shadow-sm">
            <div class="card-body" style="height: 400px;">
              <h4 class="card-title mb-3">Service Requests Summary</h4>
              <div v-if="isLoadingRequests" class="text-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else style="position: relative; height: 300px;">
                <canvas ref="serviceRequestsChart" id="serviceRequestsChart"></canvas>
              </div>
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
        console.log("Customer Ratings Data:", data);

        // Ensure we have data before updating chart
        if (data) {
          this.updateCustomerRatingsChart(data);
        } else {
          this.messages.push({
            category: "warning",
            text: "No ratings data available",
          });
        }
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

    async updateCustomerRatingsChart(data) {
      // Wait for Vue to update the DOM before accessing canvas
      await this.$nextTick();

      const canvas = this.$refs.customerRatingsChart;
      if (!canvas) {
        console.error("Customer ratings chart canvas not found");
        return;
      }

      const ctx = canvas.getContext("2d");
      if (!ctx) {
        console.error("Could not get 2d context for customer ratings chart");
        return;
      }

      if (this.customerRatingsChart) {
        this.customerRatingsChart.destroy();
      }

      // Ensure we have proper data structure with defaults
      const chartData = {
        labels: ["5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"],
        datasets: [
          {
            data: [
              parseInt(data.fiveStars || 0),
              parseInt(data.fourStars || 0),
              parseInt(data.threeStars || 0),
              parseInt(data.twoStars || 0),
              parseInt(data.oneStar || 0),
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
          maintainAspectRatio: true,
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
        console.log("Service Requests Data details:", data);

        // Check if we actually have data to display
        if (Array.isArray(data) && data.length > 0) {
          this.updateServiceRequestsChart(data);
        } else {
          console.warn("No service requests data or empty array returned");
          this.messages.push({
            category: "warning",
            text: "No service requests data available",
          });
        }
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

    async updateServiceRequestsChart(data) {
      // Wait for Vue to update the DOM before accessing canvas
      await this.$nextTick();

      const canvas = this.$refs.serviceRequestsChart;
      if (!canvas) {
        console.error("Service requests chart canvas not found");
        return;
      }

      const ctx = canvas.getContext("2d");
      if (!ctx) {
        console.error("Could not get 2d context for service requests chart");
        return;
      }

      if (this.serviceRequestsChart) {
        this.serviceRequestsChart.destroy();
      }

      // Process data safely with validation
      let labels = [];
      let counts = [];

      try {
        // Make sure dates are properly parsed
        labels = data.map((item) => {
          if (!item.date) return "Unknown";
          const date = new Date(item.date);
          return !isNaN(date)
            ? date.toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              })
            : "Invalid date";
        });

        // Make sure counts are numbers
        counts = data.map((item) => parseInt(item.count || 0));
      } catch (error) {
        console.error("Error processing chart data:", error);
        this.messages.push({
          category: "danger",
          text: "Error processing chart data",
        });
        return;
      }

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
          maintainAspectRatio: true,
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
