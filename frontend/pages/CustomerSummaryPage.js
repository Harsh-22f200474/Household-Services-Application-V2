export default {
  template: `
      <div class="container mt-4">
        <div class="row">
          <div class="col-md-12 text-center">        
            <h3>Customer Summary</h3>
          </div>
        </div>

        <!-- Alert Messages -->
        <div v-if="message" :class="'alert alert-' + category" role="alert">
          {{ message }}
        </div>

        <!-- Service History -->
        <div class="card mt-4">
          <div class="card-body">
            <h4 class="card-title">My Reviews</h4>
            <div class="table-responsive">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>Professional</th>
                    <th>Rating</th>
                    <th>Comment</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="review in reviews" :key="review.id">
                    <td>{{ review.professional_name }}</td>
                    <td>
                      <span class="badge bg-primary">{{ review.rating }} ★</span>
                    </td>
                    <td>{{ review.comment || '-' }}</td>
                    <td>{{ formatDate(review.created_at) }}</td>
                  </tr>
                  <tr v-if="reviews.length === 0">
                    <td colspan="4" class="text-center">No reviews given yet</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Service Requests Chart -->
        <div class="card mt-4">
          <div class="card-body">
            <h4 class="card-title">Service Requests History</h4>
            <div v-if="isLoading" class="text-center">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <canvas v-else id="serviceRequests" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    `,
  data() {
    return {
      serviceRequestsChart: null,
      reviews: [],
      message: null,
      category: null,
      isLoading: false,
    };
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return "-";
      const date = new Date(dateString);
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    async fetchReviews() {
      try {
        const response = await fetch("/reviews/given", {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          this.message = errorData.message || "Error fetching reviews";
          this.category = "danger";
          return;
        }

        this.reviews = await response.json();
      } catch (error) {
        console.error("Error fetching reviews:", error);
        this.message = "An error occurred while fetching reviews";
        this.category = "danger";
      }
    },
    async fetchServiceRequests() {
      this.isLoading = true;
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
          this.category = "danger";
          return;
        }

        const requests = await response.json();

        // Process the data for the chart
        const statusCounts = {
          requested: 0,
          accepted: 0,
          rejected: 0,
          completed: 0,
        };

        requests.forEach((request) => {
          const status = request.service_status.toLowerCase();
          if (status in statusCounts) {
            statusCounts[status]++;
          }
        });

        this.updateServiceRequestChart(
          Object.keys(statusCounts).map(
            (s) => s.charAt(0).toUpperCase() + s.slice(1)
          ),
          Object.values(statusCounts)
        );
      } catch (error) {
        console.error("Error fetching service requests:", error);
        this.message = "An error occurred while fetching service requests";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
    updateServiceRequestChart(labels, data) {
      const ctx = document.getElementById("serviceRequests")?.getContext("2d");
      if (!ctx) return;

      if (this.serviceRequestsChart) {
        this.serviceRequestsChart.destroy();
      }

      this.serviceRequestsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Service Requests by Status",
              data: data,
              backgroundColor: [
                "rgba(255, 193, 7, 0.5)", // requested - yellow
                "rgba(13, 110, 253, 0.5)", // accepted - blue
                "rgba(220, 53, 69, 0.5)", // rejected - red
                "rgba(25, 135, 84, 0.5)", // completed - green
              ],
              borderColor: [
                "rgba(255, 193, 7, 1)",
                "rgba(13, 110, 253, 1)",
                "rgba(220, 53, 69, 1)",
                "rgba(25, 135, 84, 1)",
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
            legend: {
              display: false,
            },
            tooltip: {
              callbacks: {
                label: (context) => `Count: ${context.raw}`,
              },
            },
          },
        },
      });
    },
  },
  mounted() {
    this.fetchReviews();
    this.fetchServiceRequests();
  },
  beforeDestroy() {
    if (this.serviceRequestsChart) {
      this.serviceRequestsChart.destroy();
    }
  },
};
