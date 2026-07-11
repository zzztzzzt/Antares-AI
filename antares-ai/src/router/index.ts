import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import TrainingDataHistoryView from "../views/TrainingDataHistoryView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/training-data-history",
      name: "training-data-history",
      component: TrainingDataHistoryView,
    },
  ],
});

export default router;
