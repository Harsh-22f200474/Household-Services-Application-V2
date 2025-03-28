export default {
  template: `
    <div class="container d-flex align-items-center justify-content-center vh-100">
      <div class="card shadow-sm" style="max-width: 400px; width: 100%;">
        <div class="card-body">
          <h3 class="card-title text-center mb-4">Admin Login</h3>
          <div v-if="message" :class="'alert alert-' + category" role="alert">
            {{ message }}
          </div>
          <form @submit.prevent="submitLogin">
            <div class="mb-3">
              <label for="username" class="form-label">Username:</label>
              <input type="text" id="username" v-model="username" class="form-control" required>
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password:</label>
              <input type="password" id="password" v-model="password" class="form-control" required>
            </div>
            <div class="d-grid">
              <input type="submit" value="Login" class="btn btn-primary">
            </div>
          </form>
        </div>
      </div>
    </div>
    `,
  data() {
    return {
      username: null,
      password: null,
      message: null,
      category: null,
    };
  },
  methods: {
    async submitLogin() {
      try {
        const res = await fetch(location.origin + "/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: this.username,
            password: this.password,
          }),
        });
        if (res.ok) {
          const data = await res.json();
          this.$root.login("admin", data.access_token);
          this.$router.push("/admin/dashboard");
        } else {
          const errorData = await res.json();
          this.message = errorData.message;
          this.category = errorData.category;
        }
      } catch (error) {
        this.message = "An unexpected error occurred.";
        this.category = "danger";
      }
    },
  },
};
