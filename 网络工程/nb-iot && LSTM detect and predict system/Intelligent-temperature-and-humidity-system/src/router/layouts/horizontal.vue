<script>
import { layoutComputed } from "@/state/helpers";

import HorizontalTopbar from "@/components/horizontal-topbar";
import HorizontalNav from "@/components/horizontal-nav";
import Footer from "@/components/footer";
import RightBar from "@/components/right-bar";

/**
 * Horizontal-layout component
 */
export default {
  components: { HorizontalTopbar, HorizontalNav, RightBar, Footer },
  computed: {
    ...layoutComputed
  },
  created: () => {
    document.body.setAttribute("data-layout", "horizontal");
    document.body.setAttribute("data-topbar", "dark");
    document.body.removeAttribute('data-sidebar','dark');
  },
  methods: {
    toggleRightSidebar() {
      document.body.classList.toggle("right-bar-enabled");
    },
    hideRightSidebar() {
      document.body.classList.remove("right-bar-enabled");
    }
  }
};
</script>

<template>
  <div id="layout-wrapper">
    <HorizontalTopbar :width="layoutWidth" :type="topbar" />
    <HorizontalNav />

    <div class="main-content">
      <div class="page-content">
        <div class="container-fluid">
          <slot />
        </div>
      </div>
      <Footer />
    </div>
    <RightBar />
  </div>
</template>