<template>
  <div class="admin-summary">
    <h6>Summary shows statistical charts</h6>

    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Overall Customer Ratings</h6>
          </div>
          <div class="card-body">
            <canvas ref="ratingsChart"></canvas>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Service Requests Summary</h6>
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
import axios from "axios";
import Chart from "chart.js/auto";

export default {
  name: "AdminSummary",
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
          axios.get("http://localhost:5000/api/admin/statistics/ratings", {
            headers,
          }),
          axios.get("http://localhost:5000/api/admin/statistics/requests", {
            headers,
          }),
        ]);

        this.createRatingsChart(ratingsRes.data);
        this.createRequestsChart(requestsRes.data);
      } catch (error) {
        console.error("Error fetching statistics:", error);
        alert("Error loading statistics");
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
          labels: ["Requested", "Assigned", "Completed", "Cancelled"],
          datasets: [
            {
              label: "Number of Requests",
              data: data,
              backgroundColor: ["#007bff", "#17a2b8", "#28a745", "#dc3545"],
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
