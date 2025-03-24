<template>
  <div class="admin-search">
    <h6>Search Functionality</h6>

    <div class="card">
      <div class="card-body">
        <div class="row mb-4">
          <div class="col-md-4">
            <select class="form-select" v-model="searchType">
              <option value="services">Services</option>
              <option value="customers">Customers</option>
              <option value="professionals">Professionals</option>
            </select>
          </div>
          <div class="col-md-6">
            <div class="input-group">
              <input
                type="text"
                class="form-control"
                v-model="searchQuery"
                placeholder="Enter search text..."
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
                <th>Assigned Professional</th>
                <th>Requested By</th>
                <th>Status(R/A/C)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in searchResults" :key="result.id">
                <td>{{ result.id }}</td>
                <td>{{ result.professional_name || "Not Assigned" }}</td>
                <td>{{ result.customer_name }}</td>
                <td>{{ result.status }}</td>
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
  name: "AdminSearch",
  data() {
    return {
      searchType: "services",
      searchQuery: "",
      searchResults: [],
    };
  },
  methods: {
    async handleSearch() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          `http://localhost:5000/api/admin/search`,
          {
            headers: { Authorization: `Bearer ${token}` },
            params: {
              type: this.searchType,
              query: this.searchQuery,
            },
          }
        );
        this.searchResults = response.data;
      } catch (error) {
        console.error("Search error:", error);
        alert("Error performing search");
      }
    },
  },
};
</script>
