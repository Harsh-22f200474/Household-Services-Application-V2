import { adminService } from "@/services/api";

export default {
  namespaced: true,

  state: {
    services: [],
    professionals: [],
    serviceRequests: [],
    loading: false,
    error: null,
  },

  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    SET_SERVICES(state, services) {
      state.services = services;
    },
    SET_PROFESSIONALS(state, professionals) {
      state.professionals = professionals;
    },
    SET_SERVICE_REQUESTS(state, requests) {
      state.serviceRequests = requests;
    },
    ADD_SERVICE(state, service) {
      state.services.push(service);
    },
    UPDATE_SERVICE(state, updatedService) {
      const index = state.services.findIndex((s) => s.id === updatedService.id);
      if (index !== -1) {
        state.services.splice(index, 1, updatedService);
      }
    },
    DELETE_SERVICE(state, serviceId) {
      state.services = state.services.filter((s) => s.id !== serviceId);
    },
  },

  actions: {
    async fetchServices({ commit }) {
      try {
        commit("SET_LOADING", true);
        const response = await adminService.getServices();
        commit("SET_SERVICES", response.data);
      } catch (error) {
        commit("SET_ERROR", error.message);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async createService({ commit }, service) {
      try {
        commit("SET_LOADING", true);
        const response = await adminService.createService(service);
        commit("ADD_SERVICE", response.data.service);
        return response.data;
      } catch (error) {
        commit("SET_ERROR", error.message);
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async updateService({ commit }, { id, service }) {
      try {
        commit("SET_LOADING", true);
        const response = await adminService.updateService(id, service);
        commit("UPDATE_SERVICE", response.data);
        return response.data;
      } catch (error) {
        commit("SET_ERROR", error.message);
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async deleteService({ commit }, id) {
      try {
        commit("SET_LOADING", true);
        await adminService.deleteService(id);
        commit("DELETE_SERVICE", id);
      } catch (error) {
        commit("SET_ERROR", error.message);
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async fetchProfessionals({ commit }) {
      try {
        commit("SET_LOADING", true);
        const response = await adminService.getProfessionals();
        commit("SET_PROFESSIONALS", response.data);
      } catch (error) {
        commit("SET_ERROR", error.message);
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async verifyProfessional({ dispatch }, id) {
      try {
        await adminService.verifyProfessional(id);
        dispatch("fetchProfessionals");
      } catch (error) {
        throw error;
      }
    },

    async blockProfessional({ dispatch }, id) {
      try {
        await adminService.blockProfessional(id);
        dispatch("fetchProfessionals");
      } catch (error) {
        throw error;
      }
    },

    async fetchServiceRequests({ commit }) {
      try {
        commit("SET_LOADING", true);
        const response = await adminService.getServiceRequests();
        commit("SET_SERVICE_REQUESTS", response.data);
      } catch (error) {
        commit("SET_ERROR", error.message);
      } finally {
        commit("SET_LOADING", false);
      }
    },
  },
};
