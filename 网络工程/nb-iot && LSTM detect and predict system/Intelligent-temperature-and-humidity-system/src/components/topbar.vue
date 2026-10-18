<script>
/**
 * Topbar component
 */
export default {
  data() {
    return {};
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
      this.$parent.toggleMenu();
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
          <router-link to="/" class="logo logo-dark">
            <span class="logo-sm">
              <img src="@/assets/images/logo-sm.png" alt height="22" />
            </span>
            <span class="logo-lg">
              <img src="@/assets/images/logo-dark.png" alt height="17" />
            </span>
          </router-link>

          <router-link to="/" class="logo logo-light">
            <span class="logo-sm">
              <img src="@/assets/images/logo-sm.png" alt height="22" />
            </span>
            <!-- <span style="margin-top: 30px;">
              <p style="font-size: large;">智能温湿度监测系统</p>
            </span> -->
            <span class="logo-lg">
              <img src="@/assets/images/logo-light2.png" alt height="28" />
            </span>
          </router-link>
        </div>

        <button
          type="button"
          class="btn btn-sm px-3 font-size-24 header-item"
          id="vertical-menu-btn"
          @click="toggleMenu()"
        >
          <i class="mdi mdi-menu"></i>
        </button>

        <!-- <div class="d-none d-sm-block">
          <b-dropdown variant="white" class="pt-3 d-inline-block">
            <template v-slot:button-content>
              Create
              <i class="mdi mdi-chevron-down"></i>
            </template>
            <b-dropdown-item>Action</b-dropdown-item>
            <b-dropdown-item>Another action</b-dropdown-item>
            <b-dropdown-item>Something else here</b-dropdown-item>
            <b-dropdown-divider></b-dropdown-divider>
            <b-dropdown-item>Separated link</b-dropdown-item>
          </b-dropdown>
        </div> -->
      </div>

      <div class="d-flex">
        <b-dropdown
          variant="white"
          class="d-inline-block"
          toggle-class="header-item noti-icon"
          menu-class="dropdown-menu-lg dropdown-menu-end"
        >
          <template v-slot:button-content>
            <i class="mdi mdi-magnify"></i>
          </template>
          <form class="p-3">
            <div class="form-group m-0">
              <div class="input-group">
                <input
                  type="text"
                  class="form-control"
                  placeholder="Search ..."
                  aria-label="Recipient's username"
                />
                <div class="input-group-append">
                  <button class="btn btn-primary" type="submit">
                    <i class="mdi mdi-magnify"></i>
                  </button>
                </div>
              </div>
            </div>
          </form>
        </b-dropdown>
        <!-- App Search-->

        <b-dropdown
          class="d-none d-md-block ms-2"
          toggle-class="header-item"
          menu-class="dropdown-menu-end"
          right
          variant="white"
        >
          <template v-slot:button-content>
            <img
              class="me-2"
              src="@/assets/images/flags/cn_flag.png"
              alt="Header Language"
              height="16"
            />
            简体中文
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

          <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/us_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">English</span>
          </a>

          <!-- item-->
          <!-- <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/french_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">French</span>
          </a> -->

          <!-- item-->
          <!-- <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/spain_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">Spanish</span>
          </a> -->

          <!-- item-->
          <!-- <a href="javascript:void(0);" class="dropdown-item notify-item">
            <img
              src="@/assets/images/flags/russia_flag.jpg"
              alt="user-image"
              class="me-1"
              height="12"
            />
            <span class="align-middle">Russian</span>
          </a> -->
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

        <!-- 消息 -->
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
                <h5 class="m-0 font-size-16">消息 (3)</h5>
              </div>
            </div>
          </div>

          <div data-simplebar style="max-height: 230px;">
            <!-- <a href="javascript:void(0);" class="text-reset notification-item">
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
            </a> -->

            <!-- <a href class="text-reset notification-item">
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
            </a> -->

            <!-- <a href class="text-reset notification-item">
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
            </a> -->

            <a href class="text-reset notification-item">
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
                  <h6 class="mt-0 mb-1">新设备已部署</h6>
                  <div class="font-size-12 text-muted">
                    <p class="mb-1">
                      新的温湿度设备已连接，设备类型为ESP8266(id=1)。
                    </p>
                  </div>
                </div>
              </div>
            </a>

            <a href class="text-reset notification-item">
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
                  <h6 class="mt-0 mb-1">新设备已部署</h6>
                  <div class="font-size-12 text-muted">
                    <p class="mb-1">
                      新的温湿度设备已连接，设备类型为ESP8266(id=2)。
                    </p>
                  </div>
                </div>
              </div>
            </a>

            <a href class="text-reset notification-item">
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
                  <h6 class="mt-0 mb-1">MQTT服务器已启动</h6>
                  <div class="font-size-12 text-muted">
                    <p class="mb-1">MQTT消息队列服务器已启动。</p>
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
                查看所有
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
              src="@/assets/images/users/user-0.jpg"
              alt="Header Avatar"
            />
          </template>

          <b-dropdown-item>
            <i
              class="mdi mdi-account-circle font-size-17 align-middle me-1"
            ></i>
            个人中心
          </b-dropdown-item>

          <b-dropdown-item>
            <i class="mdi mdi-wallet font-size-17 align-middle me-1"></i> 
            设备管理
          </b-dropdown-item>

         <a class="dropdown-item d-block" href="#"><span class="badge bg-success float-end">1</span><i class="mdi mdi-cog font-size-17 align-middle me-1"></i> 系统设置</a>

          <b-dropdown-item>
            <i
              class="mdi mdi-lock-open-outline font-size-17 align-middle me-1"
            ></i>
            屏幕锁定
          </b-dropdown-item>

          <div class="dropdown-divider"></div>
          <a class="dropdown-item text-danger" href="/logout">
            <i
              class="bx bx-power-off font-size-17 align-middle me-1 text-danger"
            ></i>
            账号登出
          </a>

        </b-dropdown>

        <div class="dropdown d-inline-block">
          <button
            type="button"
            class="btn header-item noti-icon right-bar-toggle toggle-right"
            
          >
          <!-- @click="toggleRightSidebar" -->
            <i class="mdi mdi-cog-outline toggle-right"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
