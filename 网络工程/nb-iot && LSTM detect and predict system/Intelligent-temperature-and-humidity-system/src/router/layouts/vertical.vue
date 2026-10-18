<script>
import router from "@/router";
import { layoutComputed } from "@/state/helpers";

import Topbar from "@/components/topbar";
import Sidebar from "@/components/sidebar";
import Footer from "@/components/footer";
import RightBar from "@/components/right-bar";

/**
 * Vertical layout
 */
export default {
   data() {
    return {
      type: this.$store
        ? this.$store.state.layout.leftSidebarType
        : null || null,
      width: this.$store ? this.$store.state.layout.layoutWidth : null || null,
    };
  },
  components: {
    Topbar,
    Sidebar,
    Footer,
    RightBar
  },
  computed: {
    ...layoutComputed,
  },
  created() {
    document.body.setAttribute("data-sidebar", "dark");
    document.body.removeAttribute("data-topbar", "light");
    document.body.removeAttribute("data-layout-size", "boxed");
    document.body.removeAttribute("data-layout", "horizontal");
  },
  methods: {
    toggleMenu() {
      document.body.classList.toggle("sidebar-enable");
      document.body.classList.toggle("vertical-collpsed");

      if (window.screen.width <= 768) {
        document.body.classList.remove("vertical-collpsed");
        // eslint-disable-next-line no-unused-vars
        router.afterEach((routeTo, routeFrom) => {
          document.body.classList.remove("sidebar-enable");
        });
      }
    },
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
    <Topbar />
    <Sidebar :type="leftSidebarType" :width="layoutWidth" />
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