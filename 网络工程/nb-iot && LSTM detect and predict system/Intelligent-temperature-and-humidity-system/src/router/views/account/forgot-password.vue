<script>
import { authMethods } from "@/state/helpers";
import appConfig from "@/app.config";

/**
 * Forgot password component
 */
export default {
  page: {
    title: "忘记密码",
    meta: [{ name: "description", content: appConfig.description }]
  },
  data() {
    return {
      email: "",
      error: null,
      tryingToReset: false,
      isResetError: false
    };
  },
  methods: {
    ...authMethods,
    // Try to register the user in with the email, fullname
    // and password they provided.
    tryToReset() {
      this.tryingToReset = true;
      // Reset the authError if it existed.
      this.error = null;
      return (
        this.resetPassword({
          email: this.email
        })
          // eslint-disable-next-line no-unused-vars
          .then(token => {
            this.tryingToReset = false;
            this.isResetError = false;
          })
          .catch(error => {
            this.tryingToReset = false;
            this.error = error ? error : "";
            this.isResetError = true;
          })
      );
    }
  }
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
                <h5 class="text-white font-size-20 p-2">重置密码</h5>
                <a href="/" class="logo logo-admin">
                  <img src="@/assets/images/logo-sm.png" height="24" alt="logo" />
                </a>
              </div>
            </div>
            <div class="card-body p-4">
              <div class="p-3">
                <b-alert v-model="isResetError" class="mt-3" variant="danger" dismissible>{{error}}</b-alert>

                <b-form @submit.prevent="tryToReset" class="form-horizontal mt-4">
                  <b-form-group id="email-group" label="邮箱" label-for="email" class="mb-3" label-class="form-label">
                    <b-form-input id="email" v-model="email" type="email" placeholder="输入邮箱"></b-form-input>
                  </b-form-group>

                  <div class="row mb-0">
                    <div class="col-12 text-end">
                      <b-button type="submit" variant="primary" class="w-md">重置</b-button>
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
              记得密码 ?
              <router-link to="/login" class="fw-medium text-primary">点此进行登录</router-link>
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
