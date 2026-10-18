<script>
import { layoutMethods } from "@/state/helpers";

/**
 * Right sidebar component
 */
export default {
  components: {},
  data() {
    return {
      layout: this.$store ? this.$store.state.layout.layoutType : {} || {},
      width: this.$store ? this.$store.state.layout.layoutWidth : {} || {},
      topbar: this.$store ? this.$store.state.layout.topbar : {} || {},
      sidebarType: this.$store
        ? this.$store.state.layout.leftSidebarType
        : {} || {},
      config: {
        handler: this.handleRightBarClick,
        middleware: this.middleware,
        events: ["click"],
      },
    };
  },

  methods: {
    ...layoutMethods,
    hide() {
      this.$parent.toggleRightSidebar();
    },
    // eslint-disable-next-line no-unused-vars
    handleRightBarClick(e, el) {
      this.$parent.hideRightSidebar();
    },
    // eslint-disable-next-line no-unused-vars
    middleware(event, el) {
      return !event.target.classList.contains("toggle-right");
    },
    changeLayout(layout) {
      this.changeLayoutType({ layoutType: layout });
    },
    changeType(type) {
      this.changeLayoutType({ layoutType: "vertical" });
      return this.changeLeftSidebarType({ leftSidebarType: type });
    },
    changeWidth(width) {
      return this.changeLayoutWidth({ layoutWidth: width });
    },
    changeTopbartype(value) {
      return this.changeTopbar({ topbar: value });
    },
  },
};
</script>

<template>
  <div>
    <div v-click-outside="config" class="right-bar">
      <div data-simplebar class="h-100">
        <div class="rightbar-title px-3 py-4">
          <a
            href="javascript:void(0);"
            class="right-bar-toggle float-end"
            @click="hide"
          >
            <i class="mdi mdi-close noti-icon"></i>
          </a>
          <h5 class="m-0">Settings</h5>
        </div>
        <div class="p-3">
          <h6 class="mb-0">Layout</h6>
          <hr class="mt-1" />
          <b-form-radio-group
            v-model="layout"
            stacked
            @change="changeLayout($event)"
            class="ms-1"
          >
            <b-form-radio value="vertical" class="mb-1">Vertical</b-form-radio>
            <b-form-radio value="horizontal" class="mb-1"
              >Horizontal</b-form-radio
            >
          </b-form-radio-group>
          <!-- Width -->
          <h6 class="mt-3">Width</h6>
          <hr class="mt-1" />
          <b-form-radio-group
            v-model="width"
            stacked
            @change="changeWidth($event)"
          >
            <b-form-radio value="fluid" class="mb-1">Fluid</b-form-radio>
            <b-form-radio value="boxed">Boxed</b-form-radio>
          </b-form-radio-group>
          <!-- Sidebar -->
          <div v-if="layout === 'vertical'">
            <h6 class="mt-3">Sidebar</h6>
            <hr class="mt-1" />
            <b-form-radio-group
              v-model="sidebarType"
              stacked
              @change="changeType($event)"
            >
              <b-form-radio value="dark" class="mb-1">Dark</b-form-radio>
              <b-form-radio value="light" class="mb-1">Light</b-form-radio>
              <b-form-radio value="compact" class="mb-1">Compact</b-form-radio>
              <b-form-radio value="icon">Icon</b-form-radio>
            </b-form-radio-group>
          </div>
          <!-- Topbar -->
          <div v-if="layout === 'horizontal'">
            <h6 class="mt-3">Topbar</h6>
            <hr class="mt-1" />
            <b-form-radio-group
              v-model="topbar"
              stacked
              @input="changeTopbartype($event)"
            >
              <b-form-radio value="dark" class="mb-1">Dark</b-form-radio>
              <b-form-radio value="light" class="mb-1">Light</b-form-radio>
            </b-form-radio-group>
          </div>
        </div>
        <!-- Settings -->
        <hr class="mt-0" />
        <h6 class="text-center">Choose Layouts</h6>

        <div class="p-4">
          <div class="mb-2">
            <router-link
              target="_blank"
              to="//veltrix.vuejs-light.themesbrand.com/"
            >
              <img
                src="@/assets/images/layouts/layout-1.jpg"
                class="img-fluid img-thumbnail"
                alt
              />
            </router-link>
          </div>

          <div class="mb-2">
            <router-link
              target="_blank"
              to="//veltrix.vuejs-dark.themesbrand.com/"
            >
              <img
                src="@/assets/images/layouts/layout-2.jpg"
                class="img-fluid img-thumbnail"
                alt
              />
            </router-link>
          </div>

          <div class="mb-2">
            <router-link
              target="_blank"
              to="//veltrix.vuejs-rtl.themesbrand.com/"
            >
              <img
                src="@/assets/images/layouts/layout-3.jpg"
                class="img-fluid img-thumbnail"
                alt
              />
            </router-link>
          </div>
          <div class="d-grid">
            <a
              href="https://1.envato.market/grNDB"
              class="btn btn-primary mt-3"
              target="_blank"
            >
              <i class="mdi mdi-cart me-1"></i> Purchase Now
            </a>
          </div>
        </div>
      </div>
      <!-- end scroll-->
    </div>

    <!-- Right bar overlay-->
    <div class="rightbar-overlay"></div>
  </div>
</template>

<style lang="scss"></style>
