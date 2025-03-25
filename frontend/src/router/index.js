import { createRouter, createWebHistory } from "vue-router";
import Login from "../components/auth/Login.vue";
import CustomerRegister from "../components/auth/CustomerRegister.vue";
import ProfessionalRegister from "../components/auth/ProfessionalRegister.vue";
import AdminLayout from "@/components/admin/AdminLayout.vue";
import AdminDashboard from "@/components/admin/AdminDashboard.vue";
import CustomerLayout from "@/components/customer/CustomerLayout.vue";
import ProfessionalLayout from "@/components/professional/ProfessionalLayout.vue";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
  },
  {
    path: "/register/customer",
    name: "CustomerRegister",
    component: CustomerRegister,
  },
  {
    path: "/register/professional",
    name: "ProfessionalRegister",
    component: ProfessionalRegister,
  },
  {
    path: "/admin",
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: "",
        component: () => import("@/components/admin/AdminDashboard.vue"),
      },
      {
        path: "search",
        component: () => import("@/components/admin/AdminSearch.vue"),
      },
      {
        path: "summary",
        component: () => import("@/components/admin/AdminSummary.vue"),
      },
    ],
  },
  {
    path: "/customer",
    component: CustomerLayout,
    meta: { requiresAuth: true, requiresCustomer: true },
    children: [
      {
        path: "",
        component: () => import("@/components/customer/CustomerDashboard.vue"),
      },
      {
        path: "search",
        component: () => import("@/components/customer/CustomerSearch.vue"),
      },
      {
        path: "summary",
        component: () => import("@/components/customer/CustomerSummary.vue"),
      },
      {
        path: "services/:id/book",
        component: () => import("@/components/customer/ServiceBooking.vue"),
      },
    ],
  },
  {
    path: "/professional",
    component: ProfessionalLayout,
    meta: { requiresAuth: true, requiresProfessional: true },
    children: [
      {
        path: "",
        component: () =>
          import("@/components/professional/ProfessionalDashboard.vue"),
      },
      {
        path: "search",
        component: () =>
          import("@/components/professional/ProfessionalSearch.vue"),
      },
      {
        path: "summary",
        component: () =>
          import("@/components/professional/ProfessionalSummary.vue"),
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!token) {
      next("/login");
    } else {
      if (to.matched.some((record) => record.meta.requiresAdmin)) {
        if (user.role === "admin") {
          next();
        } else {
          next("/login");
        }
      } else if (to.matched.some((record) => record.meta.requiresCustomer)) {
        if (user.role === "customer") {
          next();
        } else {
          next("/login");
        }
      } else if (
        to.matched.some((record) => record.meta.requiresProfessional)
      ) {
        if (user.role === "professional") {
          next();
        } else {
          next("/login");
        }
      } else {
        next();
      }
    }
  } else {
    next();
  }
});

export default router;
