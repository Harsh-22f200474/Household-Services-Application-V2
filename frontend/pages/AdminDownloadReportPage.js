export default {
  template: `
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-12">  
                    <div class="card">
                        <div class="card-body">
                            <h3 class="card-title">Export Service Requests</h3>
                            
                            <!-- Alert Messages -->
                            <div v-if="message" :class="'alert alert-' + category" role="alert">
                                {{ message }}
                            </div>
                            
                            <!-- Export Form -->
                            <div class="mb-4">
                                <div class="form-group">
                                    <label for="professionalId" class="form-label">Professional ID:</label>
                                    <div class="input-group">
                                        <input 
                                            type="number" 
                                            class="form-control" 
                                            id="professionalId" 
                                            v-model="professionalId" 
                                            placeholder="Enter Professional ID" 
                                            :disabled="isProcessing"
                                        />
                                        <button 
                                            class="btn btn-primary" 
                                            @click="triggerExport" 
                                            :disabled="isProcessing || !professionalId"
                                        >
                                            <span v-if="isProcessing" class="spinner-border spinner-border-sm" role="status"></span>
                        {{ isProcessing ? 'Processing...' : 'Export Service Requests' }}
                    </button> 
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Available Downloads -->
                            <div class="mt-4">
                                <h4>Available Reports</h4>
                                <div class="table-responsive">
                                    <table class="table table-striped">
                                        <thead>
                                            <tr>
                                                <th>Filename</th>
                                                <th>Action</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr v-for="(file, index) in downloads" :key="index">
                                                <td>{{ file }}</td>
                                                <td>
                                                    <button 
                                                        class="btn btn-sm btn-success" 
                                                        @click="downloadFile(file)"
                                                    >
                                                        Download
                                                    </button>
                                                </td>
                                            </tr>
                                            <tr v-if="downloads.length === 0">
                                                <td colspan="2" class="text-center">No reports available</td>
                                            </tr>
                                        </tbody>
                                    </table>
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
      isProcessing: false,
      downloads: [],
      professionalId: "",
      message: null,
      category: null,
      timer: null,
    };
  },
  methods: {
    async triggerExport() {
      if (!this.professionalId) {
        this.showMessage("Please enter a valid professional ID!", "danger");
        return;
      }

      this.isProcessing = true;
      try {
        const response = await fetch("/admin/export/" + this.professionalId, {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        const data = await response.json();

        if (response.ok) {
          this.showMessage(data.message, data.category);
          await this.fetchDownloads(); // Refresh the downloads list
        } else {
          this.showMessage(
            data.message || "Failed to generate report",
            "danger"
          );
        }
      } catch (error) {
        this.showMessage(
          "An error occurred while generating the report",
          "danger"
        );
        console.error("Error:", error);
      } finally {
        this.isProcessing = false;
      }
    },

    async fetchDownloads() {
      try {
        const response = await fetch("/admin/reports/list", {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (response.ok) {
          const data = await response.json();
          this.downloads = data.downloads;
        } else {
          const errorData = await response.json();
          this.showMessage(
            errorData.message || "Failed to fetch reports",
            "danger"
          );
        }
      } catch (error) {
        console.error("Error fetching downloads:", error);
        this.showMessage("Failed to fetch available reports", "danger");
      }
    },

    async downloadFile(filename) {
      try {
        const response = await fetch("/admin/reports/download/" + filename, {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          this.showMessage(
            errorData.message || "Error downloading file",
            "danger"
          );
          return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error("Error downloading file:", error);
        this.showMessage(
          "An error occurred while downloading the file",
          "danger"
        );
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
    this.fetchDownloads();
    // Refresh downloads list every 10 seconds
    this.timer = setInterval(() => {
      this.fetchDownloads();
    }, 10000);
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  },
};
