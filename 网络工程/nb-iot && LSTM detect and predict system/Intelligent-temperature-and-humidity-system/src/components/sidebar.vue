<script>
import simplebar from "simplebar-vue";
import MetisMenu from "metismenujs/dist/metismenujs";

import { layoutMethods } from "@/state/helpers";
import { menuItems } from "./menu";

/**
 * Sidebar component
 */
export default {
  data() {
    return {
      menuItems: menuItems,
    };
  },
  props: {
    type: {
      type: String,
      required: true,
    },
    width: {
      type: String,
      required: true,
    },
  },
  components: {
    simplebar,
  },
  mounted: function() {
    // eslint-disable-next-line no-unused-vars
    var menuRef = new MetisMenu("#side-menu");
    var links = document.getElementsByClassName("side-nav-link");
    var matchingMenuItem = null;
    for (var i = 0; i < links.length; i++) {
      if (window.location.pathname === links[i].pathname) {
        matchingMenuItem = links[i];
        break;
      }
    }

    if (matchingMenuItem) {
      matchingMenuItem.classList.add("active");
      var parent = matchingMenuItem.parentElement;
      /**
       * TODO: This is hard coded way of expading/activating parent menu dropdown and working till level 3.
       * We should come up with non hard coded approach
       */
      if (parent) {
        parent.classList.add("mm-active");
        const parent2 = parent.parentElement.closest("ul");
        if (parent2 && parent2.id !== "side-menu") {
          parent2.classList.add("mm-show");
          const parent3 = parent2.parentElement;
          if (parent3) {
            parent3.classList.add("mm-active");
            var childAnchor = parent3.querySelector(".has-arrow");
            var childDropdown = parent3.querySelector(".has-dropdown");
            if (childAnchor) childAnchor.classList.add("mm-active");
            if (childDropdown) childDropdown.classList.add("mm-active");
            const parent4 = parent3.parentElement;
            if (parent4) parent4.classList.add("mm-show");
            const parent5 = parent4.parentElement;
            if (parent5) parent5.classList.add("active");
          }
        } else {
          parent.classList.add("mm-active");
        }
      }
    }
  },
  methods: {
    ...layoutMethods,
    changeLayout(layout) {
      this.changeLayoutType({ layoutType: layout });
    },
    compactSidebar() {
      document.body.setAttribute("data-sidebar-size", "small");
      document.body.classList.remove("vertical-collpsed");
      document.body.removeAttribute("data-keep-enlarged", "true");
      document.body.removeAttribute("data-layout-size", "boxed");
    },
    iconSidebar() {
      document.body.classList.add("vertical-collpsed");
      document.body.setAttribute("data-keep-enlarged", "true");
      document.body.removeAttribute("data-sidebar-size", "small");
      document.body.removeAttribute("data-layout-size", "boxed");
    },
    boxedLayout() {
      document.body.setAttribute("data-layout-size", "boxed");
      document.body.classList.add("vertical-collpsed");
      document.body.setAttribute("data-keep-enlarged", "true");
    },
    /**
     * Returns true or false if given menu item has child or not
     * @param item menuItem
     */
    hasItems(item) {
      return item.subItems !== undefined ? item.subItems.length > 0 : false;
    },
  },
  watch: {
    type: {
      immediate: true,
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          switch (newVal) {
            case "dark":
              document.body.setAttribute("data-sidebar", "dark");
              document.body.removeAttribute("data-topbar");
              document.body.removeAttribute("data-sidebar-size");
              document.body.classList.remove("vertical-collpsed");
              break;
            case "light":
              document.body.setAttribute("data-topbar", "dark");
              document.body.removeAttribute("data-sidebar");
              document.body.removeAttribute("data-sidebar-size");
              document.body.classList.remove("vertical-collpsed");
              break;
            case "compact":
              document.body.setAttribute("data-sidebar-size", "small");
              document.body.setAttribute("data-sidebar", "dark");
              document.body.setAttribute("data-topbar", "light");
              document.body.classList.remove("vertical-collpsed");
              document.body.removeAttribute("data-keep-enlarged");
              break;
            case "icon":
              document.body.classList.add("vertical-collpsed");
              document.body.setAttribute("data-keep-enlarged", "true");
              document.body.removeAttribute("data-sidebar-size");
              break;
            case "colored":
              document.body.setAttribute("data-sidebar", "colored");
              document.body.removeAttribute("data-keep-enlarged");
              document.body.classList.remove("vertical-collpsed");
              break;
            default:
              document.body.setAttribute("data-sidebar", "dark");
              break;
          }
        }
      },
    },
    width: {
      immediate: true,
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          switch (newVal) {
            case "boxed":
              document.body.setAttribute("data-layout-size", "boxed");
              break;
            case "fluid":
              document.body.setAttribute("data-layout-mode", "fluid");
              document.body.removeAttribute("data-layout-size");
              document.body.classList.remove("vertical-collpsed");
              break;
            default:
              document.body.setAttribute("data-layout-mode", "fluid");
              break;
          }
        }
      },
    },
  },
};
</script>

<template>
  <!-- ========== Left Sidebar Start ========== -->
  <div class="vertical-menu">
    <simplebar class="h-100">
      <!--- Sidemenu -->
      <div id="sidebar-menu">
        <!-- Left Menu Start -->
        <ul class="metismenu list-unstyled" id="side-menu">
          <template v-for="item in menuItems">
            <li class="menu-title" v-if="item.isTitle" :key="item.id">
              {{ item.label }}
            </li>
            <li v-if="!item.isTitle && !item.isLayout" :key="item.id">
              <a
                v-if="hasItems(item)"
                href="javascript:void(0);"
                class="is-parent"
                :class="{
                  'has-arrow': !item.badge,
                  'has-dropdown': item.badge,
                }"
              >
                <i :class="`bx ${item.icon}`" v-if="item.icon"></i>
                <span>{{ item.label }}</span>
                <span
                  :class="
                    `badge rounded-pill bg-${item.badge.variant} float-end`
                  "
                  v-if="item.badge"
                  >{{ item.badge.text }}</span
                >
              </a>

              <router-link
                :to="item.link"
                v-if="!hasItems(item)"
                class="side-nav-link"
              >
                <i :class="`bx ${item.icon}`" v-if="item.icon"></i>
                <span>{{ item.label }}</span>
                <span
                  :class="
                    `badge rounded-pill bg-${item.badge.variant} float-end`
                  "
                  v-if="item.badge"
                  >{{ item.badge.text }}</span
                >
              </router-link>

              <ul v-if="hasItems(item)" class="sub-menu" aria-expanded="false">
                <li v-for="(subitem, index) of item.subItems" :key="index">
                  <router-link
                    :to="subitem.link"
                    v-if="!hasItems(subitem)"
                    class="side-nav-link"
                    >{{ subitem.label }}</router-link
                  >
                  <a
                    v-if="hasItems(subitem)"
                    class="side-nav-link-a has-arrow"
                    href="javascript:void(0);"
                    >{{ subitem.label }}</a
                  >
                  <ul
                    v-if="hasItems(subitem)"
                    class="sub-menu mm-collapse"
                    aria-expanded="false"
                  >
                    <li
                      v-for="(subSubitem, index) of subitem.subItems"
                      :key="index"
                    >
                      <router-link
                        :to="subSubitem.link"
                        class="side-nav-link"
                        >{{ subSubitem.label }}</router-link
                      >
                    </li>
                  </ul>
                </li>
              </ul>
            </li>
          </template>
        </ul>
      </div>
      <!-- Sidebar -->
    </simplebar>
  </div>
  <!-- Left Sidebar End -->
</template>
