<template>
  <div id="loginContainer">
    <div id="loginContent">
    <h2 id="title">SmartAgri</h2>
      <el-form label-width="120px" size="large">
        <el-form-item label="账号:" class="itemLogin">
          <el-input placeholder="账号/邮箱" v-model="user.loginName" ></el-input>
        </el-form-item>
        <el-form-item label="密码:" class="itemLogin">
          <el-input type="password" placeholder="登录密码" v-model="user.loginPwd"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button @click="doLogin($event)"  class=".special.el-button" color="dark" ><a>登录</a></el-button>
        </el-form-item>
       <el-form-item>
         <div id="loginBottom">
          <el-button class=".special.el-button" color="dark" @click="remove($event)"> <router-link to="/register">快速注册</router-link></el-button>
         </div>
       </el-form-item>
      </el-form>
    </div>

  </div>
  <span id="bottom">
  <router-link to="">联系管理员</router-link>
</span>
</template>

<script>
    export default {
      name:'LoginView',
      data(){
        return{
          user:{
            loginName:'',
            loginPwd:''
          }
        }
      },
      methods:{
        doLogin(e){
          this.remove(e);
          this.$axios.post("/user_login",this.user)
              .then(rst=>{
                let resultJson = rst.data;
                let code = resultJson.code;
                console.log(resultJson)
                if (code == -1){
                  this.$message("账号或密码输入有误!")
                }
                else if(code == 0){
                  const jwt = resultJson.body.token
                  window.localStorage.setItem('jwt', jwt);
                  this.$router.push("/home");
            
                }
              }).catch(err=>{
                console.log(err);
          })

        },
        remove(e) { // 或者参数里直接获取$event
          let target = e.target
          if (target.nodeName === 'SPAN') {
            target = e.target.parentNode
          }
          target.blur()
        }
      }
    }
</script>

<style scoped>
#loginContainer{
  width: 100%;
  height: 100%;
  /* background-color:rgb(148, 146, 149); */
  background-image: url('@/assets/aaa.JPG');
  background-size: 100% 100%;
  display:flex;
  justify-content: center;
  align-items: center;
}
#loginContent{
   width: 500px;
  border: 1px solid rgb(0, 0, 0);
  background-clip: padding-box;
  box-shadow: 0 0 10px rgb(255, 255, 255);
  background: rgba(255, 255, 255, 0.5);
  padding-right: 80px;
  padding-top: 20px;
  padding-bottom: 20px;
  border-radius: 20px;
  font-family: "中國龍標準明";
}

#loginContent h2{
  display: flex;
  justify-content: center;
  align-items: center;
  width: 120%;
  height: 60px;
  margin-bottom: 20px;
  font-size: 45px;
  font-family: "中國龍標準明";
  color: rgb(0, 0, 0);
  text-shadow:5px 5px 5px #2c3e50;

}

#loginBottom{
  width: 100%;
  height: 100%;
  text-align: right;
  margin-right: 5px;
  margin-top: -127px;
}
a{
  color: rgb(0, 0, 0);
}
a:hover{
  color: silver;
}
#bottom{
  position: absolute;
  top: 95%;
  left: 47%;
}
</style>
<style>
.itemLogin .el-form-item__label{
  color: rgb(0, 0, 0);
  /* 账号密码 */
}
.color.el-form-item_label{
  color: rgb(0, 0, 0);
}
.special.el-button{
  border: 1px solid black;
  color: black;
}
.special.el-button:hover{
  
  color: rgb(255, 255, 255);
  background-color: transparent!important;
  border: 2px solid rgb(255, 255, 255);
}
.special.el-button:focus{
  border: 4px solid rgb(0, 0, 0);
  color: rgb(0, 0, 0);
  background-color: transparent!important;
}
.top{
  position: absolute;
  top: 20%;
  left: 47%;
}
</style>