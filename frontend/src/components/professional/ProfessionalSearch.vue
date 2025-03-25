<template>
  <div class="professional-search">
    <h6>Search Functionality</h6>

    <div class="card">
      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-4">
            <select class="form-select" v-model="searchBy">
              <option value="date">Date</option>
              <option value="location">Location</option>
              <option value="name">Customer Name</option>
            </select>
          </div>
          <div class="col-md-6">
            <div class="input-group">
              <input
                type="text"
                class="form-control"
                v-model="searchText"
                :placeholder="getPlaceholder()"
              />
              <button class="btn btn-primary" @click="handleSearch">
                Search
              </button>
            </div>
          </div>
        </div>

        <!-- Search Results -->
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
              <tr v-for="result in searchResults" :key="result.id">
                <td>{{ result.id }}</td>
                <td>{{ result.customer_name }}</td>
                <td>{{ result.contact_phone }}</td>
                <td>{{ result.address }}</td>
                <td>{{ formatDate(result.requested_date) }}</td>
                <td>{{ result.customer_rating || "N/A" }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ProfessionalSearch",
  data() {
    return {
      searchBy: "date",
      searchText: "",
      searchResults: [],
    };
  },
  methods: {
    getPlaceholder() {
      switch (this.searchBy) {
        case "date":
          return "Enter date (DD/MM/YYYY)";
        case "location":
          return "Enter location or pin code";
        case "name":
          return "Enter customer name";
        default:
          return "Enter search text";
      }
    },
    async handleSearch() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          "http://localhost:5000/api/professional/service-requests/search",
          {
            headers: { Authorization: `Bearer ${token}` },
            params: {
              type: this.searchBy,
              query: this.searchText,
            },
          }
        );
        this.searchResults = response.data;
      } catch (error) {
        console.error("Search error:", error);
      }
    },
    formatDate(dateString) {
      if (!dateString) return "N/A";
      return new Date(dateString).toLocaleDateString();
    },
  },
};
</script>
