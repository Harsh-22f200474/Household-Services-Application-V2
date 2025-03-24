import { createRouter, createWebHistory } from "vue-router";
import Login from "../components/auth/Login.vue";
import CustomerRegister from "../components/auth/CustomerRegister.vue";
import ProfessionalRegister from "../components/auth/ProfessionalRegister.vue";
import AdminLayout from "@/components/admin/AdminLayout.vue";
import AdminDashboard from "@/components/admin/AdminDashboard.vue";

const routes = [
  {
    path: "/",
    redirect: "/admin",
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
    component: () => import("@/components/admin/AdminLayout.vue"),
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
    path: "/admin/dashboard",
    redirect: "/admin",
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
    } else if (
      to.matched.some((record) => record.meta.requiresAdmin) &&
      user.role !== "admin"
    ) {
      next("/login");
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
