export default {
  props: {
    editing: {
      type: Boolean,
      default: false,
    },
    id: {
      type: [String, Number],
      default: null,
    },
  },
  data() {
    return {
      service: {
        id: this.id,
        service_type: "",
        name: "",
        description: "",
        price: "",
      },
      message: null,
      category: null,
    };
  },
  created() {
    if (this.editing && this.id) {
      this.fetchServiceData();
    }
  },
  methods: {
    async fetchServiceData() {
      try {
        const response = await fetch(`/admin/service/${this.id}`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
            "Content-Type": "application/json",
          },
        });
        if (response.ok) {
          const data = await response.json();
          this.service = {
            id: data.id,
            service_type: data.service_type,
            name: data.name,
            description: data.description,
            price: data.price,
          };
        } else {
          const errorData = await response.json();
          this.message = errorData.message || "Failed to load service data";
          this.category = "danger";
        }
      } catch (error) {
        this.message = "An error occurred while fetching the service data";
        this.category = "danger";
      }
    },
    async submitForm() {
      try {
        const url = this.editing
          ? `/admin/service/${this.id}`
          : "/admin/service";

        const response = await fetch(url, {
          method: this.editing ? "PUT" : "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            name: this.service.name,
            price: Number(this.service.price),
            description: this.service.description,
            service_type: this.service.service_type,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          this.message = data.message;
          this.category = data.category;
          // Wait a moment to show the success message
          setTimeout(() => {
            this.$router.push("/admin/dashboard");
          }, 1500);
        } else {
          this.message = data.message || "An error occurred.";
          this.category = data.category || "danger";
        }
      } catch (error) {
        this.message = "An unexpected error occurred.";
        this.category = "danger";
      }
    },
  },
  template: `
        <div class="row">
            <div class="col-md-4 offset-md-4">
                <h3>{{ editing ? 'Edit Service' : 'New Service' }}</h3>
                
                <div v-if="message" :class="'alert alert-' + category" role="alert">
                    {{ message }}
                </div>

                <form @submit.prevent="submitForm">
                    <div class="form-group mb-3">
                        <label for="service_type">Service Type</label>
                        <select id="service_type" v-model="service.service_type" class="form-control" required>
                            <option value="">Select a service type</option>
                            <option value="Cleaning">Cleaning Services</option>
                            <option value="Plumbing">Plumbing Services</option>
                            <option value="Electrical">Electrical Services</option>
                            <option value="Carpentry">Carpentry Services</option>
                        </select>
                    </div>

                    <div class="form-group mb-3">
                        <label for="name">Name</label>
                        <input type="text" id="name" v-model="service.name" class="form-control" required>
                    </div>

                    <div class="form-group mb-3">
                        <label for="description">Description</label>
                        <textarea id="description" v-model="service.description" class="form-control" rows="3" required></textarea>
                    </div>

                    <div class="form-group mb-3">
                        <label for="price">Price (₹)</label>
                        <input type="number" id="price" v-model="service.price" class="form-control" min="0" step="0.01" required>
                    </div>

                    <div class="form-group text-center mt-4">
                        <button type="submit" class="btn btn-primary me-2">{{ editing ? 'Update' : 'Create' }} Service</button>
                        <router-link to="/admin/dashboard" class="btn btn-secondary">Cancel</router-link>
                    </div>
                </form>
            </div>
        </div>
    `,
};
