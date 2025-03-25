<template>
  <div class="professional-layout">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container-fluid">
        <span class="navbar-brand">Welcome to Professional</span>
        <div class="navbar-nav ms-auto">
          <router-link class="nav-link" to="/professional">Home</router-link>
          <router-link class="nav-link" to="/professional/search"
            >Search</router-link
          >
          <router-link class="nav-link" to="/professional/summary"
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
  name: "ProfessionalLayout",
  methods: {
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      this.$router.push("/login");
    },
  },
};
</script>
