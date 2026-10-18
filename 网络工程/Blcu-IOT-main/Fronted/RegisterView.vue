<template>
    <div class="register">
      <h1>注册</h1>
      <el-form ref="form" :rules="rules" :model="registerForm" label-width="120px" class="register-form">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="registerForm.password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input type="password" v-model="registerForm.confirmPassword" placeholder="请再次输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">注册</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import {ElMessage} from 'element-plus'
  
  export default {
    data() {
      return {
        registerForm: {
          username: '',
          password: '',
          confirmPassword: ''
        },
        rules: {
          username: [
            { required: true, message: '请输入用户名', trigger: 'blur' },
            { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
          ],
          password: [
            { required: true, message: '请输入密码', trigger: 'blur' },
            { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
          ],
          confirmPassword: [
            { required: true, message: '请再次输入密码', trigger: 'blur' },
            {
              validator: (rule, value, callback) => {
                if (value !== this.registerForm.password) {
                  callback(new Error('两次输入密码不一致'))
                } else {
                  callback()
                }
              },
              trigger: 'blur'
            }
          ]
        }
      }
    },
    methods: {
      submitForm() {
        this.$refs.form.validate(valid => {
          if (valid) {
            // 发送注册请求
            axios.post('http://127.0.0.1:5000/register', this.registerForm)
              .then(res => {
                if (res.data.status === 'success') {
                  ElMessage.success(res.data.message)
                  this.$router.push('/login')
                } else {
                  ElMessage.error(res.data.message)
                }
              })
              .catch(err => {
                console.log(err)
                Message.error('注册失败，请重试')
              })
          }
        })
      },
      resetForm() {
        this.$refs.form.resetFields()
      }
    }
  }
  </script>
  
  <style scoped>
  .register {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }
  
  .register-form {
    width: 400px;
    margin-top: 20px;
  }
  </style>
  