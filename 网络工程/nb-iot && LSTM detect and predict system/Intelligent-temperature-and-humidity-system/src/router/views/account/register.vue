<script>
import {
  authMethods,
  authFackMethods,
  notificationMethods,
} from "@/state/helpers";
import { required, email } from "vuelidate/lib/validators";
import { mapState } from "vuex";

import appConfig from "@/app.config";

/**
 * Register component
 */
export default {
  page: {
    title: "注册",
    meta: [{ name: "description", content: appConfig.description }],
  },
  data() {
    return {
      user: {
        username: "",
        email: "",
        password: "",
      },
      submitted: false,
      regError: null,
      tryingToRegister: false,
      isRegisterError: false,
      registerSuccess: false,
    };
  },
  validations: {
    user: {
      username: {
        required,
      },
      email: {
        required,
        email,
      },
      password: {
        required,
      },
    },
  },
  methods: {
    ...authMethods,
    ...authFackMethods,
    ...notificationMethods,
    // Try to register the user in with the email, username
    // and password they provided.
    tryToRegisterIn() {
      this.submitted = true;

      this.$v.$touch();

      if (this.$v.$invalid) {
        return;
      } else {
        if (process.env.VUE_APP_DEFAULT_AUTH === "firebase") {
          this.tryingToRegister = true;
          // Reset the regError if it existed.
          this.regError = null;
          return (
            this.register({
              email: this.email,
              password: this.password,
            })
              // eslint-disable-next-line no-unused-vars
              .then((token) => {
                this.$router.push(
                  this.$route.query.redirectFrom || { name: "home" }
                );
              })
              .catch((error) => {
                this.tryingToRegister = false;
                this.regError = error ? error : "";
                this.isRegisterError = true;
              })
          );
        } else if (process.env.VUE_APP_DEFAULT_AUTH === "fakebackend") {
          const { email, username, password } = this.user;
          if (email && username && password) {
            this.registeruser(this.user);
          }
        }
      }
    },
  },

  computed: {
    ...mapState("authfack", ["status"]),
    notification() {
      return this.$store ? this.$store.state.notification : null;
    },
  },
};
</script>

<template>
  <div class="account-pages my-5 pt-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6 col-xl-4">
          <div class="card overflow-hidden">
            <div class="bg-primary">
              <div class="text-primary text-center p-4">
                <h5 class="text-white font-size-20">立即注册</h5>
                <p class="text-white-50">获取你的智能温湿度管理系统的账户</p>
                <a href="/" class="logo logo-admin">
                  <img
                    src="@/assets/images/logo-sm.png"
                    height="24"
                    alt="logo"
                  />
                </a>
              </div>
            </div>

            <div class="card-body p-4">
              <div class="p-3">
                <b-alert
                  v-model="registerSuccess"
                  class="mt-3"
                  variant="success"
                  dismissible
                  >Registration successfull.</b-alert
                >

                <b-alert
                  v-model="isRegisterError"
                  class="mt-3"
                  variant="danger"
                  dismissible
                  >{{ regError }}</b-alert
                >

                <div
                  v-if="notification.message"
                  :class="'alert ' + notification.type"
                >
                  {{ notification.message }}
                </div>

                <b-form
                  @submit.prevent="tryToRegisterIn"
                  class="form-horizontal mt-4"
                >
                  <b-form-group
                    id="username-group"
                    label="用户名"
                    label-for="username"
                    label-class="form-label"
                    class="mb-3"
                  >
                    <b-form-input
                      id="username"
                      v-model="user.username"
                      type="text"
                      placeholder="输入用户名"
                      :class="{
                        'is-invalid': submitted && $v.user.username.$error,
                      }"
                    ></b-form-input>
                    <div
                      v-if="submitted && !$v.user.username.required"
                      class="invalid-feedback"
                    >
                      Username is required.
                    </div>
                  </b-form-group>

                  <b-form-group
                    id="email-group"
                    label="邮箱"
                    label-for="email"
                    label-class="form-label"
                    class="mb-3"
                  >
                    <b-form-input
                      id="email"
                      v-model="user.email"
                      type="email"
                      placeholder="输入邮箱"
                      :class="{
                        'is-invalid': submitted && $v.user.email.$error,
                      }"
                    ></b-form-input>
                    <div
                      v-if="submitted && $v.user.email.$error"
                      class="invalid-feedback"
                    >
                      <span v-if="!$v.user.email.required"
                        >Email is required.</span
                      >
                      <span v-if="!$v.user.email.email"
                        >Please enter valid email.</span
                      >
                    </div>
                  </b-form-group>

                  <b-form-group
                    id="password-group"
                    label="密码"
                    label-for="password"
                    label-class="form-label"
                    class="mb-3"
                  >
                    <b-form-input
                      id="password"
                      v-model="user.password"
                      type="password"
                      placeholder="输入密码"
                      :class="{
                        'is-invalid': submitted && $v.user.password.$error,
                      }"
                    ></b-form-input>
                    <div
                      v-if="submitted && !$v.user.password.required"
                      class="invalid-feedback"
                    >
                      Password is required.
                    </div>
                  </b-form-group>

                  <div class="form-group mb-0 text-center">
                    <div class="col-12 text-end">
                      <b-button type="submit" variant="primary" class="w-md"
                        >注册</b-button
                      >
                    </div>
                  </div>
                  <div class="form-group mt-2 mb-0 row">
                    <div class="col-12 mt-4">
                      <p class="mb-0">
                        注册前请认真阅读
                        <a href="#" class="text-primary">使用协议</a>
                      </p>
                    </div>
                  </div>
                </b-form>
              </div>
            </div>
            <!-- end card-body -->
          </div>
          <!-- end card -->
          <div class="mt-5 text-center">
            <p>
              已有帐户 ?
              <router-link to="/login" class="fw-medium text-primary"
                >登录</router-link
              >
            </p>
            
          </div>
        </div>
        <!-- end col -->
      </div>
      <!-- end row -->
    </div>
  </div>
</template>

<style lang="scss" module></style>
