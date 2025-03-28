export default {
  template: `
      <div class="container d-flex align-items-center justify-content-center vh-100">
        <div class="card shadow-sm">
          <div class="card-body text-center">
            <h3 class="card-title mb-4">A-Z Household Services</h3>
            <div class="mb-3">
              <router-link to="/admin/login" class="btn btn-primary btn-block">
                Admin Login
              </router-link>
            </div>
            <div>
              <router-link to="/login" class="btn btn-outline-primary btn-block">
                Customer/Professional Login
              </router-link>
            </div>
          </div>
        </div>
      </div>
    `,
};
