export default {
  template: `
        <div class="container my-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card shadow-sm">
            <div class="card-header bg-primary text-white text-center">
              <h4 class="mb-0">Register</h4>
            </div>
            <div class="card-body">
              <!-- Alert Message -->
              <div v-if="message" :class="'alert alert-' + category" role="alert" class="mb-3">
                {{ message }}
              </div>
              <!-- Registration Form -->
              <form @submit.prevent="submitRegister">
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input type="text" id="username" v-model="username" class="form-control" required>
                </div>
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input type="password" id="password" v-model="password" class="form-control" required>
                </div>
                <div class="mb-3">
                  <label for="role" class="form-label">Select Role</label>
                  <select id="role" v-model="role" class="form-select" required>
                    <option value="Customer">Customer</option>
                    <option value="Professional">Professional</option>
                  </select>
                </div>
                <div class="text-center">
                  <button type="submit" class="btn btn-primary btn-sm me-2">Register</button>
                  <router-link to="/login" class="btn btn-secondary btn-sm">Cancel</router-link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    `,
  data() {
    return {
      username: null,
      password: null,
      role: null,
      message: null,
      category: null,
    };
  },
  methods: {
    async submitRegister() {
      try {
        const res = await fetch(location.origin + "/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: this.username,
            password: this.password,
            role: this.role,
          }),
        });
        if (res.ok) {
          const data = await res.json();
          this.message = data.message;
          this.category = data.category;
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
