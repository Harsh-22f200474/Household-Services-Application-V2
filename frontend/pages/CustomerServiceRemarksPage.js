export default {
  template: `
        <div class="container mt-4">
            <div class="col-md-6 offset-md-3">
                <div class="card">
                    <div class="card-body">
                        <h3 class="card-title">Close Service Request</h3>
                
                <!-- Flash Messages -->
                        <div v-if="message" :class="'alert alert-' + category" role="alert">
                            {{ message }}
                </div>

                        <!-- Service Review Form -->
                        <form @submit.prevent="submitForm" class="mt-4">
                            <div class="form-group mb-3">
                                <label for="rating" class="form-label">Rating (1-5 stars)</label>
                        <input 
                            type="number" 
                            id="rating" 
                            v-model="formData.rating" 
                                    class="form-control" 
                                    min="1" 
                                    max="5" 
                                    required
                                >
                            </div>

                            <div class="form-group mb-3">
                                <label for="comment" class="form-label">Comments</label>
                                <textarea 
                                    id="comment" 
                                    v-model="formData.comment" 
                                    class="form-control" 
                                    rows="3"
                                    placeholder="Share your experience..."
                                ></textarea>
                            </div>

                            <div class="form-group text-center mt-4">
                                <button type="submit" class="btn btn-primary me-2" :disabled="isLoading">
                                    <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                                    {{ isLoading ? 'Submitting...' : 'Submit Review' }}
                                </button>
                                <router-link to="/customer/dashboard" class="btn btn-secondary">Cancel</router-link>
                            </div>
                        </form>
                    </div>
                    </div>
            </div>
        </div>
    `,
  props: {
    id: {
      type: [String, Number],
      required: true,
    },
  },
  data() {
    return {
      message: null,
      category: null,
      isLoading: false,
      formData: {
        rating: 5,
        comment: "",
      },
    };
  },
  methods: {
    async submitForm() {
      if (!this.validateForm()) return;

      this.isLoading = true;
      try {
        const response = await fetch(`/review/${this.id}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify(this.formData),
        });

        const data = await response.json();

        if (response.ok) {
          this.message = "Review submitted successfully";
          this.category = "success";
          // Wait a moment to show the success message
          setTimeout(() => {
            this.$router.push("/customer/dashboard");
          }, 1500);
        } else {
          this.message = data.error || "Failed to submit review";
          this.category = "danger";
        }
      } catch (error) {
        console.error("Error submitting review:", error);
        this.message = "An error occurred while submitting the review";
        this.category = "danger";
      } finally {
        this.isLoading = false;
      }
    },
    validateForm() {
      if (
        !this.formData.rating ||
        this.formData.rating < 1 ||
        this.formData.rating > 5
      ) {
        this.message = "Rating must be between 1 and 5";
        this.category = "danger";
        return false;
      }
      return true;
    },
  },
};
