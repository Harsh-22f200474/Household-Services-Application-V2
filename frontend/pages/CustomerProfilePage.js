export default {
  template: `
    <div class="container my-5">
      <div class="row">
        <div class="col-md-6 offset-md-3">
          <div class="card shadow-sm">
            <div class="card-header text-center bg-primary text-white">
              <h4 class="mb-0">Customer Profile</h4>
            </div>
            <div class="card-body">
              <!-- Alert Message -->
              <div v-if="message" :class="'alert alert-' + category" role="alert">
                {{ message }}
              </div>
              <!-- Profile Form -->
              <form @submit.prevent="handleSubmit">
                <div class="mb-3">
                  <label for="user_name" class="form-label">Username (Email)</label>
                  <input 
                    type="email" 
                    id="user_name" 
                    v-model="form.user_name" 
                    class="form-control" 
                    readonly
                  />
                </div>
                <div class="mb-3">
                  <label for="full_name" class="form-label">Full Name</label>
                  <input 
                    type="text" 
                    id="full_name" 
                    v-model="form.full_name" 
                    class="form-control" 
                    required
                  />
                </div>
                <div class="mb-3">
                  <label for="address" class="form-label">Address</label>
                  <textarea 
                    id="address" 
                    v-model="form.address" 
                    class="form-control" 
                    rows="3"
                    required
                  ></textarea>
                </div>
                <div class="mb-4">
                  <label for="pin_code" class="form-label">PIN Code</label>
                  <input 
                    type="text" 
                    id="pin_code" 
                    v-model="form.pin_code" 
                    class="form-control" 
                    pattern="[0-9]{6}"
                    title="Please enter a valid 6-digit PIN code"
                    required
                  />
                </div>
                <div class="text-center">
                  <button type="submit" class="btn btn-primary" :disabled="isLoading">
                    <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ isLoading ? 'Saving...' : 'Save Profile' }}
                  </button>
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
      form: {
        user_name: "",
        full_name: "",
        address: "",
        pin_code: "",
      },
      user_id: "",
      message: "",
      category: "",
      isLoading: false,
    };
  },
  mounted() {
    this.fetchCustomerProfile();
  },
  methods: {
    async fetchCustomerProfile() {
      try {
        this.isLoading = true;
        const response = await fetch("/customer/profile", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        const data = await response.json();

        if (response.ok) {
          this.user_id = data.user_id;
          this.form.user_name = data.username;
          this.form.full_name = data.full_name || "";
          this.form.address = data.address || "";
          this.form.pin_code = data.pin_code || "";
        } else {
          this.message = data.message || "Failed to load profile data";
          this.category = data.category || "danger";
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
        this.message = "An error occurred while fetching the profile data";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
    async handleSubmit() {
      if (!this.form.full_name || !this.form.address || !this.form.pin_code) {
        this.message = "Please fill in all required fields";
        this.category = "danger";
        return;
      }

      try {
        this.isLoading = true;
        const response = await fetch("/customer/profile", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            full_name: this.form.full_name,
            address: this.form.address,
            pin_code: this.form.pin_code,
          }),
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          // If profile was created successfully, redirect to dashboard
          setTimeout(() => {
            this.$router.push("/customer/dashboard");
          }, 1500);
        }
      } catch (error) {
        console.error("Error updating profile:", error);
        this.message = "An error occurred while updating the profile data";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
  },
};
