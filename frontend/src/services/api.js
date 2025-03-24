import axios from "axios";

const API_URL = "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  async login(credentials) {
    try {
      const response = await api.post("/auth/login", credentials);
      if (response.data.access_token) {
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("user", JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error.response.data;
    }
  },

  async registerCustomer(userData) {
    try {
      const response = await api.post("/auth/register", {
        ...userData,
        role: "customer",
      });
      return response.data;
    } catch (error) {
      throw error.response.data;
    }
  },

  async registerProfessional(userData) {
    const formData = new FormData();
    Object.keys(userData).forEach((key) => {
      formData.append(key, userData[key]);
    });
    formData.append("role", "professional");

    try {
      const response = await api.post("/auth/register", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error) {
      throw error.response.data;
    }
  },

  logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },
};

export const adminService = {
  // Services
  getServices() {
    return api.get("/admin/services");
  },
  createService(service) {
    return api.post("/admin/services", service);
  },
  updateService(id, service) {
    return api.put(`/admin/services/${id}`, service);
  },
  deleteService(id) {
    return api.delete(`/admin/services/${id}`);
  },

  // Professionals
  getProfessionals() {
    return api.get("/admin/professionals");
  },
  verifyProfessional(id) {
    return api.post(`/admin/professionals/${id}/verify`);
  },
  blockProfessional(id) {
    return api.post(`/admin/professionals/${id}/block`);
  },

  // Service Requests
  getServiceRequests() {
    return api.get("/admin/service-requests");
  },
};
