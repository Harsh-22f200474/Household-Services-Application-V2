export default {
  template: `
    <div class="container d-flex align-items-center justify-content-center vh-100">
      <div class="card shadow-sm" style="width: 100%; max-width: 400px;">
        <div class="card-body">
          <h3 class="card-title text-center mb-4">Login</h3>
          <div v-if="message" :class="'alert alert-' + category" role="alert">
            {{ message }}
          </div>
          <form @submit.prevent="submitLogin">
            <div class="mb-3">
              <label for="username" class="form-label">Username (e-mail):</label>
              <input
                type="text"
                id="username"
                v-model="username"
                class="form-control"
                required
              >
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password:</label>
              <input
                type="password"
                id="password"
                v-model="password"
                class="form-control"
                required
              >
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
              {{ isLoading ? 'Logging in...' : 'Login' }}
            </button>
          </form>
          <div class="text-center mt-3">
            <router-link to="/register" class="text-decoration-none">
              Register Customer/Professional
            </router-link>
          </div>
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
      isLoading: false,
    };
  },
  methods: {
    async submitLogin() {
      this.isLoading = true;
      this.message = null;

      try {
        // First, attempt login
        const loginResponse = await fetch("/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: this.username,
            password: this.password,
          }),
        });

        const loginData = await loginResponse.json();

        if (!loginResponse.ok) {
          this.message = loginData.message;
          this.category = loginData.category;
          return;
        }

        if (!loginData.access_token) {
          this.message = "No access token received from server";
          this.category = "danger";
          return;
        }

        // Get claims after successful login
        const claimsResponse = await fetch("/get-claims", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${loginData.access_token}`,
          },
        });

        const claimsData = await claimsResponse.json();

        if (!claimsResponse.ok) {
          this.message = claimsData.message || "Failed to get user claims";
          this.category = claimsData.category || "danger";
          return;
        }

        // Check if user is blocked
        if (claimsData.claims.blocked) {
          this.message =
            "Your account has been blocked. Please contact support.";
          this.category = "danger";
          return;
        }

        // For professionals, check if approved
        if (
          claimsData.claims.role === "Professional" &&
          !claimsData.claims.approved
        ) {
          this.message =
            "Your account is pending approval. Please wait for admin approval.";
          this.category = "warning";
          return;
        }

        // Login successful, update root state
        this.$root.login(claimsData.claims.role, loginData.access_token);

        // Handle redirects based on role and redirect path
        if (claimsData.claims.role === "Customer") {
          this.$router.push(
            claimsData.claims.redirect === "customer_profile"
              ? "/customer/profile"
              : "/customer/dashboard"
          );
        } else if (claimsData.claims.role === "Professional") {
          this.$router.push(
            claimsData.claims.redirect === "professional_profile"
              ? "/professional/profile"
              : "/professional/dashboard"
          );
        } else if (claimsData.claims.role === "Admin") {
          this.$router.push("/admin/dashboard");
        } else {
          this.message = "Invalid role received from server";
          this.category = "danger";
        }
      } catch (error) {
        console.error("Login error:", error);
        this.message = "An unexpected error occurred. Please try again.";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
  },
  mounted() {
    // Clear any existing auth data on mount
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userRole");
    localStorage.removeItem("token");
  },
};
