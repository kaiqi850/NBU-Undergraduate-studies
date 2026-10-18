<template>
    <v-container>
      <v-sheet class="pa-12" rounded color="#F7F7F7">
        <v-card class="mx-auto px-6 py-9" max-width="344" elevation="4">
          <template v-slot:title>
            修改密码
          </template>
  
          <v-form v-model="form" @submit.prevent="onSubmit">
            <!-- 当前密码输入框 -->
            <v-text-field
              v-model="currentPassword"
              :readonly="loading"
              :rules="currentPasswordRules"
              class="mb-2"
              label="当前密码"
              clearable
              type="password"
              outlined
              dense
            >
              <template v-slot:prepend>
                <v-icon icon="mdi-lock"></v-icon>
              </template>
            </v-text-field>
  
            <!-- 新密码输入框 -->
            <v-text-field
              v-model="newPassword"
              :readonly="loading"
              :rules="newPasswordRules"
              class="mb-2"
              label="新密码"
              clearable
              type="password"
              outlined
              dense
            >
              <template v-slot:prepend>
                <v-icon icon="mdi-lock-reset"></v-icon>
              </template>
            </v-text-field>
  
            <!-- 确认新密码输入框 -->
            <v-text-field
              v-model="confirmPassword"
              :readonly="loading"
              :rules="confirmPasswordRules"
              class="mb-2"
              label="确认新密码"
              clearable
              type="password"
              outlined
              dense
            >
              <template v-slot:prepend>
                <v-icon icon="mdi-lock-check"></v-icon>
              </template>
            </v-text-field>
  
            <v-btn :loading="loading" color="success" size="large" type="submit" variant="elevated" block>
              提交
            </v-btn>
          </v-form>
        </v-card>
      </v-sheet>
    </v-container>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router';
  import { ref } from 'vue';
  
  const router = useRouter();
  
  // 密码输入
  const currentPassword = ref('');
  const newPassword = ref('');
  const confirmPassword = ref('');
  
  // 表单验证规则
  const currentPasswordRules = ref([
    value => value?.length > 0 || '当前密码未输入',
  ]);
  
  const newPasswordRules = ref([
    value => value?.length > 0 || '新密码未输入',
  ]);
  
  const confirmPasswordRules = ref([
    value => value?.length > 0 || '确认新密码未输入',
  ]);
  
  const form = ref(false);
  const loading = ref(false);
  
  // 提交事件
  function onSubmit() {
    if (!form.value) return;
  
    loading.value = true;
  
    // 这里可以添加实际的后端请求逻辑
    // 例如：调用 API 进行密码修改
  
    loading.value = false;
    router.push('/'); // 修改成功后跳转首页或其他页面
  }
  </script>
  
  <style scoped>
  /* 可以根据需求添加更多的样式 */
  </style>