<template>
  <div class="professional-summary">
    <h6>Summary shows statistical charts</h6>

    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Reviews/Ratings</h6>
          </div>
          <div class="card-body">
            <canvas ref="ratingsChart"></canvas>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Service Requests</h6>
          </div>
          <div class="card-body">
            <canvas ref="requestsChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";
import axios from "axios";

export default {
  name: "ProfessionalSummary",
  data() {
    return {
      ratingsChart: null,
      requestsChart: null,
    };
  },
  methods: {
    async fetchData() {
      try {
        const token = localStorage.getItem("token");
        const headers = { Authorization: `Bearer ${token}` };

        const [ratingsRes, requestsRes] = await Promise.all([
          axios.get(
            "http://localhost:5000/api/professional/statistics/ratings",
            { headers }
          ),
          axios.get(
            "http://localhost:5000/api/professional/statistics/requests",
            { headers }
          ),
        ]);

        this.createRatingsChart(ratingsRes.data);
        this.createRequestsChart(requestsRes.data);
      } catch (error) {
        console.error("Error fetching statistics:", error);
      }
    },
    createRatingsChart(data) {
      if (this.ratingsChart) {
        this.ratingsChart.destroy();
      }

      const ctx = this.$refs.ratingsChart;
      this.ratingsChart = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels: ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"],
          datasets: [
            {
              data: data,
              backgroundColor: [
                "#28a745",
                "#20c997",
                "#ffc107",
                "#fd7e14",
                "#dc3545",
              ],
            },
          ],
        },
      });
    },
    createRequestsChart(data) {
      if (this.requestsChart) {
        this.requestsChart.destroy();
      }

      const ctx = this.$refs.requestsChart;
      this.requestsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["Received", "Closed", "Rejected"],
          datasets: [
            {
              label: "Service Requests",
              data: data,
              backgroundColor: ["#007bff", "#28a745", "#dc3545"],
            },
          ],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    },
  },
  mounted() {
    this.fetchData();
  },
  beforeUnmount() {
    if (this.ratingsChart) {
      this.ratingsChart.destroy();
    }
    if (this.requestsChart) {
      this.requestsChart.destroy();
    }
  },
};
</script>
