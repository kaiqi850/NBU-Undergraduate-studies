<script>
/**
 * Horizontal-topbar component
 */
export default {
  props: {
    width: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: true,
    },
  },
  watch: {
    width: {
      immediate: true,
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          switch (newVal) {
            case "boxed":
              document.body.setAttribute("data-layout-size", "boxed");
              break;
            case "fluid":
              document.body.removeAttribute("data-layout-size", "boxed");
              break;
            default:
              document.body.setAttribute("data-topbar", "light");
              break;
          }
        }
      },
    },
    type: {
      immediate: true,
      handler(newVal, oldVal) {
        if (newVal !== oldVal) {
          switch (newVal) {
            case "dark":
              document.body.setAttribute("data-topbar", "dark");
              break;
            case "light":
              document.body.setAttribute("data-topbar", "light");
              document.body.removeAttribute("data-layout-size", "boxed");
              break;
            default:
              document.body.setAttribute("data-topbar", "dark");
              break;
          }
        }
      },
    },
  },
  methods: {
    initFullScreen() {
      document.body.classList.toggle("fullscreen-enable");
      if (
        !document.fullscreenElement &&
        /* alternative standard method */ !document.mozFullScreenElement &&
        !document.webkitFullscreenElement
      ) {
        // current working methods
        if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen();
        } else if (document.documentElement.mozRequestFullScreen) {
          document.documentElement.mozRequestFullScreen();
        } else if (document.documentElement.webkitRequestFullscreen) {
          document.documentElement.webkitRequestFullscreen(
            Element.ALLOW_KEYBOARD_INPUT
          );
        }
      } else {
        if (document.cancelFullScreen) {
          document.cancelFullScreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitCancelFullScreen) {
          document.webkitCancelFullScreen();
        }
      }
    },
    toggleMenu() {
      let element = document.getElementById("topnav-menu-content");
      element.classList.toggle("show");
    },
    toggleRightSidebar() {
      this.$parent.toggleRightSidebar();
    },
  },
};
</script>

<template>
  <header id="page-topbar">
    <div class="navbar-header">
      <div class="d-flex">
        <!-- LOGO -->
        <div class="navbar-brand-box">
          <a href="/" class="logo logo-dark">
            <span class="logo-sm">
              <img src="@/assets/images/logo-sm.png" alt height="22" />
            </span>
            <span class="logo-lg">
              <img src="@/assets/images/logo-dark.png" alt height="17" />
            </span>
          </a>

          <a href="/" class="logo logo-light">
            <span class="logo-sm">
              <img src="@/assets/images/logo-sm.png" alt height="22" />
            </span>
            <span class="logo-lg">
              <img src="@/assets/images/logo-light.png" alt height="18" />
            </span>
          </a>
        </div>

        <button
          type="button"
          class="btn btn-sm me-2 font-size-24 d-lg-none header-item"
          @click="toggleMenu"
        >
          <i class="mdi mdi-menu"></i>
        </button>
      </div>

      <div class="d-flex">
        <!-- App Search-->
        <form class="app-search d-none d-lg-block">
          <div class="position-relative">
            <input type="text" class="form-control" placeholder="Search..." />
            <span class="fa fa-search"></span>
          </div>
        </form>

        <b-dropdown
          class="d-none d-md-block ms-2"
          toggle-class="header-item"
          right
          variant="white"
        >
          <template v-slot:button-content>
            <img
              class="me-2"
              src="@/assets/images/flags/us_flag.jpg"
              alt="Header Language"
              height="16"
            />
            English
            <span class="mdi mdi-chevron-down"></span>
          </template>
          <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/germany_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">German</span>
          </a>

          <!-- item-->
          <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/italy_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">Italian</span>
          </a>

          <!-- item-->
          <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/french_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">French</span>
          </a>

          <!-- item-->
          <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/spain_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">Spanish</span>
          </a>

          <!-- item-->
          <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/russia_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">Russian</span>
          </a>
        </b-dropdown>

        <div class="dropdown d-none d-lg-inline-block">
          <button
            type="button"
            class="btn header-item noti-icon"
            @click="initFullScreen"
          >
            <i class="mdi mdi-fullscreen"></i>
          </button>
        </div>

        <b-dropdown
          class="d-inline-block"
          toggle-class="header-item noti-icon"
          menu-class="dropdown-menu-lg p-0 dropdown-menu-end"
          right
          variant="white"
        >
          <template v-slot:button-content>
            <i class="mdi mdi-bell-outline"></i>
            <span class="badge bg-danger rounded-pill">3</span>
          </template>
          <div class="p-3">
            <div class="row align-items-center">
              <div class="col">
                <h5 class="m-0 font-size-16">Notifications (258)</h5>
              </div>
            </div>
          </div>
          <div data-simplebar style="max-height: 230px;">
            <a href="javascript:void(0);" class="text-reset notification-item">
              <div class="d-flex">
                <div class="flex-shrink-0 me-3">
                  <div class="avatar-xs">
                    <span
                      class="avatar-title bg-success rounded-circle font-size-16"
                    >
                      <i class="mdi mdi-cart-outline"></i>
                    </span>
                  </div>
                </div>
                <div class="flex-grow-1">
                  <h6 class="mb-1">Your order is placed</h6>
                  <div class="font-size-12 text-muted">
                    <p class="mb-1">
                      Dummy text of the printing and typesetting industry.
                    </p>
                  </div>
                </div>
              </div>
            </a>

            <a href="javascript:void(0);" class="text-reset notification-item">
              <div class="d-flex">
                <div class="flex-shrink-0 me-3">
                  <div class="avatar-xs">
                    <span
                      class="avatar-title bg-warning rounded-circle font-size-16"
                    >
                      <i class="mdi mdi-message-text-outline"></i>
                    </span>
                  </div>
                </div>
                <div class="flex-grow-1">
                  <h6 class="mt-0 mb-1">New Message received</h6>
                  <div class="font-size-12 text-muted">
                    <p class="mb-1">You have 87 unread messages</p>
                  </div>
                </div>
              </div>
            </a>

            <a href="javascript:void(0);" class="text-reset notification-item">
              <div class="d-flex">
                <div class="flex-shrink-0 me-3">
                  <div class="avatar-xs">
                    <span
                      class="avatar-title bg-info rounded-circle font-size-16"
                    >
                      <i class="mdi mdi-glass-cocktail"></i>
                    </span>
                  </div>
                </div>
                <div class="flex-grow-1">
                  <h6 class="mt-0 mb-1">Your item is shipped</h6>
                  <div class="font-size-12 text-muted">
                    <p class="mb-1">
                      It is a long established fact that a reader will
                    </p>
                  </div>
                </div>
              </div>
            </a>

            <a href="javascript:void(0);" class="text-reset notification-item">
              <div class="d-flex">
                <div class="flex-shrink-0 me-3">
                  <div class="avatar-xs">
                    <span
                      class="avatar-title bg-primary rounded-circle font-size-16"
                    >
                      <i class="mdi mdi-cart-outline"></i>
                    </span>
                  </div>
                </div>
                <div class="flex-grow-1">
                  <h6 class="mt-0 mb-1">Your order is placed</h6>
                  <div class="font-size-12 text-muted">
                    <p class="mb-1">
                      Dummy text of the printing and typesetting industry.
                    </p>
                  </div>
                </div>
              </div>
            </a>

            <a href="javascript:void(0);" class="text-reset notification-item">
              <div class="d-flex">
                <div class="flex-shrink-0 me-3">
                  <div class="avatar-xs">
                    <span
                      class="avatar-title bg-danger rounded-circle font-size-16"
                    >
                      <i class="mdi mdi-message-text-outline"></i>
                    </span>
                  </div>
                </div>
                <div class="flex-grow-1">
                  <h6 class="mt-0 mb-1">New Message received</h6>
                  <div class="font-size-12 text-muted">
                    <p class="mb-1">You have 87 unread messages</p>
                  </div>
                </div>
              </div>
            </a>
          </div>
          <div class="p-2 border-top">
            <div class="d-grid">
              <a
                class="btn btn-sm btn-link font-size-14 text-center"
                href="javascript:void(0)"
              >
                View all
              </a>
            </div>
          </div>
        </b-dropdown>

        <b-dropdown
          class="d-inline-block"
          right
          toggle-class="header-item"
          variant="white"
          menu-class="dropdown-menu-end"
        >
          <template v-slot:button-content>
            <img
              class="rounded-circle header-profile-user"
              src="@/assets/images/users/user-4.jpg"
              alt="Header Avatar"
            />
          </template>
          <a class="dropdown-item" href="#">
            <i
              class="mdi mdi-account-circle font-size-17 align-middle me-1"
            ></i>
            Profile
          </a>
          <a class="dropdown-item" href="#">
            <i class="mdi mdi-wallet font-size-17 align-middle me-1"></i> My
            Wallet
          </a>
          <a class="dropdown-item d-block" href="#">
            <span class="badge bg-success float-end">11</span>
            <i class="mdi mdi-cog font-size-17 align-middle me-1"></i>
            Settings
          </a>
          <a class="dropdown-item" href="#">
            <i
              class="mdi mdi-lock-open-outline font-size-17 align-middle me-1"
            ></i>
            Lock screen
          </a>
          <div class="dropdown-divider"></div>
          <a class="dropdown-item text-danger" href="#">
            <i
              class="bx bx-power-off font-size-17 align-middle me-1 text-danger"
            ></i>
            Logout
          </a>
        </b-dropdown>

        <div class="dropdown d-inline-block">
          <button
            type="button"
            class="btn header-item noti-icon right-bar-toggle toggle-right"
            @click="toggleRightSidebar"
          >
            <i class="mdi mdi-cog-outline toggle-right"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
