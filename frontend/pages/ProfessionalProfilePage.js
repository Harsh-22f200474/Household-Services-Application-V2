export default {
  template: `
      <div class="container mt-4">
        <div class="col-md-6 offset-md-3">
          <div class="card">
            <div class="card-body">
              <h3 class="card-title">Professional Profile</h3>
          
          <!-- Flash Messages -->
              <div v-if="message" :class="'alert alert-' + category" role="alert">
                {{ message }}
          </div>
          
          <!-- Form -->
              <form @submit.prevent="submitForm" class="mt-4">
                <div class="form-group mb-3">
                  <label for="user_name" class="form-label">Username (Email)</label>
              <input
                id="user_name"
                v-model="form.user_name"
                class="form-control"
                    type="email"
                readonly
              />
            </div>  
                
                <div class="form-group mb-3">
                  <label for="full_name" class="form-label">Full Name</label>
              <input
                id="full_name"
                v-model="form.full_name"
                class="form-control"
                type="text"
                    required
              />
            </div>
  
                <div class="form-group mb-3">
                  <label for="service_type" class="form-label">Service Type</label>
              <select
                id="service_type"
                v-model="form.service_type"
                class="form-control"
                    required
              >
                    <option value="">Select a service type</option>
                    <option value="Cleaning">Cleaning Services</option>
                    <option value="Plumbing">Plumbing Services</option>
                    <option value="Electrical">Electrical Services</option>
                    <option value="Carpentry">Carpentry Services</option>
              </select>
            </div>
  
                <div class="form-group mb-3">
                  <label for="experience" class="form-label">Years of Experience</label>
              <input
                id="experience"
                v-model="form.experience"
                class="form-control"
                    type="number"
                    min="0"
                    required
              />
            </div>
  
                <div class="form-group mb-3">
                  <label for="file" class="form-label">
                    Certification/License Document
                    <small class="text-muted">(PDF, JPG, PNG only)</small>
                  </label>
              <input
                id="file"
                type="file"
                class="form-control"
                @change="handleFileUpload"
                    accept=".pdf,.jpg,.jpeg,.png,.gif"
                    required
              />
            </div>
  
                <div class="form-group mb-3">
                  <label for="address" class="form-label">Address</label>
              <textarea
                id="address"
                v-model="form.address"
                class="form-control"
                    rows="3"
                    required
              ></textarea>
            </div>
  
                <div class="form-group mb-3">
                  <label for="pin_code" class="form-label">PIN Code</label>
              <input
                id="pin_code"
                v-model="form.pin_code"
                class="form-control"
                type="text"
                    pattern="[0-9]{6}"
                    title="Please enter a valid 6-digit PIN code"
                    required
              />
            </div>
  
                <div class="form-group text-center mt-4">
                  <button type="submit" class="btn btn-primary" :disabled="isLoading">
                    <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                    {{ isLoading ? 'Saving...' : 'Save Profile' }}
              </button>
            </div>
          </form>
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
        service_type: "",
        experience: "",
        address: "",
        pin_code: "",
        file: null,
      },
      message: null,
      category: null,
      isLoading: false,
    };
  },
  mounted() {
    this.fetchProfileData();
  },
  methods: {
    async fetchProfileData() {
      try {
        const response = await fetch("/professional/profile", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          this.message = errorData.message || "Failed to load profile data";
          this.category = "danger";
          return;
        }

        const data = await response.json();
        this.form.user_name = data.username;
        this.form.full_name = data.full_name || "";
        this.form.service_type = data.service_type || "";
        this.form.experience = data.experience || "";
        this.form.address = data.address || "";
        this.form.pin_code = data.pin_code || "";
      } catch (error) {
        console.error("Error fetching profile:", error);
        this.message = "An error occurred while fetching profile data";
        this.category = "danger";
      }
    },

    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const allowedTypes = [
          "image/jpeg",
          "image/png",
          "image/gif",
          "application/pdf",
        ];
        if (!allowedTypes.includes(file.type)) {
          this.message = "Please upload a valid file type (PDF, JPG, PNG, GIF)";
          this.category = "danger";
          event.target.value = "";
          return;
        }
        this.form.file = file;
      }
    },

    async submitForm() {
      if (!this.validateForm()) return;

      this.isLoading = true;
      try {
        const formData = new FormData();
        formData.append("full_name", this.form.full_name);
        formData.append("service_type", this.form.service_type);
        formData.append("experience", this.form.experience);
        formData.append("address", this.form.address);
        formData.append("pin_code", this.form.pin_code);
        if (this.form.file) {
          formData.append("file", this.form.file);
        }

        const response = await fetch("/professional/profile", {
          method: "POST",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: formData,
        });

        const data = await response.json();
        this.message = data.message;
        this.category = data.category;

        if (response.ok) {
          // Wait a moment to show the success message
          setTimeout(() => {
            this.$router.push("/professional/dashboard");
          }, 1500);
        }
      } catch (error) {
        console.error("Error updating profile:", error);
        this.message = "An error occurred while updating the profile";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },

    validateForm() {
      if (
        !this.form.full_name ||
        !this.form.service_type ||
        !this.form.experience ||
        !this.form.address ||
        !this.form.pin_code
      ) {
        this.message = "Please fill in all required fields";
        this.category = "danger";
        return false;
      }

      if (!/^\d{6}$/.test(this.form.pin_code)) {
        this.message = "Please enter a valid 6-digit PIN code";
        this.category = "danger";
        return false;
      }

      if (!this.form.file && !this.form.filename) {
        this.message = "Please upload your certification/license document";
        this.category = "danger";
        return false;
      }

      return true;
    },
  },
};
