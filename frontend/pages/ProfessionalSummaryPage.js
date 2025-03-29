export default {
  template: `
      <div class="container my-5">
      <!-- Page Title -->
      <div class="row">
        <div class="col-12 text-center">
          <h3 class="mb-4">Professional Summary</h3>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center my-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <!-- Summary Charts -->
      <div v-show="!isLoading && !error" class="row">
        <!-- Reviews / Ratings Chart -->
        <div class="col-md-6 mb-4">
          <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
              <h4 class="mb-0">Reviews / Ratings</h4>
            </div>
            <div class="card-body">
              <canvas ref="reviewsDoughnutChart"></canvas>
            </div>
          </div>
        </div>
        <!-- Service Requests Chart -->
        <div class="col-md-6 mb-4">
          <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
              <h4 class="mb-0">Service Requests</h4>
            </div>
            <div class="card-body">
              <canvas ref="serviceRequestsChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
    `,
  data() {
    return {
      isLoading: true,
      error: null,
      reviewsDoughnutChart: null,
      serviceRequestsChart: null,
      userId: null,
      reviewsData: {
        labels: [],
        data: [],
      },
      requestsData: {
        labels: ["Received", "Closed", "Rejected"],
        data: [0, 0, 0],
      },
    };
  },
  methods: {
    checkToken() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.error = "No authentication token found. Please login again.";
        this.$router.push("/login");
        return false;
      }
      return true;
    },
    async fetchUserClaims() {
      if (!this.checkToken()) return;

      try {
        const response = await fetch("/get-claims", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (response.status === 401 || response.status === 403) {
          this.error = "Session expired. Please login again.";
          this.$router.push("/login");
          return;
        }

        if (!response.ok) {
          throw new Error(
            `Failed to fetch user claims: ${response.statusText}`
          );
        }

        const data = await response.json();
        if (!data.claims || !data.claims.user_id) {
          throw new Error("User ID not found in claims");
        }

        if (data.claims.role !== "Professional") {
          this.error = "Unauthorized access. Professional role required.";
          this.$router.push("/login");
          return;
        }

        this.userId = data.claims.user_id;
      } catch (error) {
        console.error("Error fetching claims:", error);
        this.error = error.message || "Failed to fetch user information";
        return null;
      }
    },
    async fetchReviewsData() {
      if (!this.userId) return;

      try {
        const response = await fetch(
          `/professional/summary/reviews/${this.userId}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + localStorage.getItem("token"),
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch reviews data");
        }

        const reviews = await response.json();
        if (!Array.isArray(reviews)) {
          throw new Error("Invalid reviews data format");
        }

        // Process reviews data by rating
        const ratingCounts = {
          "5 Stars": 0,
          "4 Stars": 0,
          "3 Stars": 0,
          "2 Stars": 0,
          "1 Star": 0,
        };

        reviews.forEach((review) => {
          const rating = review.rating;
          const label = rating === 1 ? "1 Star" : `${rating} Stars`;
          ratingCounts[label]++;
        });

        this.reviewsData = {
          labels: Object.keys(ratingCounts),
          data: Object.values(ratingCounts),
        };

        await this.$nextTick();
        this.updateDoughnutChart();
      } catch (error) {
        console.error("Error fetching reviews:", error);
        this.error = error.message;
      }
    },
    updateDoughnutChart() {
      const canvas = this.$refs.reviewsDoughnutChart;
      if (!canvas) {
        console.error("Reviews chart canvas not found");
        return;
      }

      const ctx = canvas.getContext("2d");
      if (this.reviewsDoughnutChart) {
        this.reviewsDoughnutChart.destroy();
      }

      this.reviewsDoughnutChart = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: this.reviewsData.labels,
          datasets: [
            {
              data: this.reviewsData.data,
              backgroundColor: [
                "rgba(75, 192, 192, 0.6)", // 5 stars - teal
                "rgba(54, 162, 235, 0.6)", // 4 stars - blue
                "rgba(255, 206, 86, 0.6)", // 3 stars - yellow
                "rgba(255, 159, 64, 0.6)", // 2 stars - orange
                "rgba(255, 99, 132, 0.6)", // 1 star - red
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
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "bottom" },
            title: {
              display: true,
              text: "Rating Distribution",
            },
          },
        },
      });
    },
    async fetchServiceRequests() {
      if (!this.userId) return;

      try {
        const response = await fetch(
          `/professional/summary/service_requests/${this.userId}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + localStorage.getItem("token"),
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch service requests data");
        }

        const requests = await response.json();
        if (!Array.isArray(requests)) {
          throw new Error("Invalid service requests data format");
        }

        // Process requests data
        const statusCounts = {
          Received: 0,
          Closed: 0,
          Rejected: 0,
        };

        requests.forEach((request) => {
          if (request.service_status === "requested") statusCounts.Received++;
          else if (request.service_status === "completed")
            statusCounts.Closed++;
          else if (request.service_status === "rejected")
            statusCounts.Rejected++;
        });

        this.requestsData = {
          labels: Object.keys(statusCounts),
          data: Object.values(statusCounts),
        };

        await this.$nextTick();
        this.updateServiceRequestChart();
      } catch (error) {
        console.error("Error fetching service requests:", error);
        this.error = error.message;
      }
    },
    updateServiceRequestChart() {
      const canvas = this.$refs.serviceRequestsChart;
      if (!canvas) {
        console.error("Service requests chart canvas not found");
        return;
      }

      const ctx = canvas.getContext("2d");
      if (this.serviceRequestsChart) {
        this.serviceRequestsChart.destroy();
      }

      this.serviceRequestsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: this.requestsData.labels,
          datasets: [
            {
              label: "Number of Requests",
              data: this.requestsData.data,
              backgroundColor: [
                "rgba(54, 162, 235, 0.6)", // Received - blue
                "rgba(75, 192, 192, 0.6)", // Closed - green
                "rgba(255, 99, 132, 0.6)", // Rejected - red
              ],
              borderColor: [
                "rgba(54, 162, 235, 1)",
                "rgba(75, 192, 192, 1)",
                "rgba(255, 99, 132, 1)",
              ],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
              },
            },
          },
          plugins: {
            legend: { display: false },
            title: {
              display: true,
              text: "Requests by Status",
            },
          },
        },
      });
    },
    async initializeCharts() {
      try {
        await this.fetchUserClaims();
        if (this.userId) {
          await Promise.all([
            this.fetchReviewsData(),
            this.fetchServiceRequests(),
          ]);
        }
      } catch (error) {
        console.error("Error initializing charts:", error);
        this.error = "Failed to initialize charts";
      } finally {
        this.isLoading = false;
      }
    },
  },
  mounted() {
    this.initializeCharts();
  },
  beforeDestroy() {
    if (this.reviewsDoughnutChart) {
      this.reviewsDoughnutChart.destroy();
    }
    if (this.serviceRequestsChart) {
      this.serviceRequestsChart.destroy();
    }
  },
};
