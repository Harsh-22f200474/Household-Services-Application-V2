<template>
  <div class="customer-summary">
    <h6>Summary shows statistical charts</h6>

    <!-- Service Requests Chart -->
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">Service Requests</h6>
      </div>
      <div class="card-body">
        <div class="chart-container" style="height: 300px">
          <canvas ref="requestsChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";
import axios from "axios";

export default {
  name: "CustomerSummary",
  data() {
    return {
      requestsChart: null,
    };
  },
  methods: {
    async fetchData() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          "http://localhost:5000/api/customer/statistics/requests",
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.createChart(response.data);
      } catch (error) {
        console.error("Error fetching statistics:", error);
      }
    },
    createChart(data) {
      if (this.requestsChart) {
        this.requestsChart.destroy();
      }

      const ctx = this.$refs.requestsChart;
      this.requestsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["Requested", "Assigned", "Completed"],
          datasets: [
            {
              label: "Service Requests",
              data: [
                data.requested || 0,
                data.assigned || 0,
                data.completed || 0,
              ],
              backgroundColor: [
                "#007bff", // Blue for requested
                "#28a745", // Green for assigned
                "#17a2b8", // Cyan for completed
              ],
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
        },
      });
    },
  },
  mounted() {
    this.fetchData();
  },
  beforeUnmount() {
    if (this.requestsChart) {
      this.requestsChart.destroy();
    }
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  margin: auto;
}
</style>
