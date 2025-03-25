<template>
  <div class="customer-layout">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">
        <span class="navbar-brand">Welcome to Customer</span>
        <div class="navbar-nav ms-auto">
          <router-link class="nav-link" to="/customer">Home</router-link>
          <router-link class="nav-link" to="/customer/search"
            >Search</router-link
          >
          <router-link class="nav-link" to="/customer/summary"
            >Summary</router-link
          >
          <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
        </div>
      </div>
    </nav>
    <div class="container mt-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: "CustomerLayout",
  methods: {
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      this.$router.push("/login");
    },
  },
};
</script>
