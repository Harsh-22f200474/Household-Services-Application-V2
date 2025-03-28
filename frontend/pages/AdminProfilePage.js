export default {
  template: `
    <div class="container my-5">
      <div class="row">
        <div class="col-md-8 offset-md-2">
          <div class="card shadow-sm">
            <div class="card-body">
              <h3 class="card-title mb-4">Admin Profile</h3>
              
              <!-- Alert Messages -->
              <div v-if="message" :class="'alert alert-' + category" role="alert">
                {{ message }}
              </div>

              <!-- Profile Information -->
              <div v-if="profileData" class="mt-4">
                <div class="table-responsive">
                  <table class="table">
                    <tbody>
                      <tr>
                        <th scope="row" style="width: 30%;">Admin ID</th>
                        <td>{{ profileData.id }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Username</th>
                        <td>{{ profileData.username }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Role</th>
                        <td>
                          <span class="badge bg-primary">
                            {{ profileData.role }}
                          </span>
                        </td>
                      </tr>
                      <tr>
                        <th scope="row">Account Created</th>
                        <td>{{ formatDate(profileData.date_created) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Loading State -->
              <div v-if="isLoading" class="text-center mt-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    `,
  data() {
    return {
      message: null,
      category: null,
      profileData: null,
      isLoading: false,
    };
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return "N/A";
      const date = new Date(dateString);
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    async fetchProfileData() {
      this.isLoading = true;
      try {
        const response = await fetch("/admin/profile", {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        const data = await response.json();

        if (response.ok) {
          this.profileData = data.data;
          this.message = data.message;
          this.category = data.category;
        } else {
          this.message = data.message || "Failed to load profile data";
          this.category = data.category || "danger";
        }
      } catch (error) {
        console.error("Error:", error);
        this.message = "An error occurred while fetching the profile data";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
    showMessage(message, category) {
      this.message = message;
      this.category = category;
      // Clear message after 5 seconds
      setTimeout(() => {
        this.message = null;
        this.category = null;
      }, 5000);
    },
  },
  mounted() {
    this.fetchProfileData();
  },
};
