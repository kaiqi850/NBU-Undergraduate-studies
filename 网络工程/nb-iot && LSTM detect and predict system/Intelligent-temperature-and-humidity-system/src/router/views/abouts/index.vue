<script>


import Layout from "../../layouts/main";
import PageHeader from "@/components/page-header";
import appConfig from "@/app.config";

/**
 * Form Advanced component
 */
export default {
  page: {
    title: "关于我们",
    meta: [{ name: "description", content: appConfig.description }]
  },
  components: { Layout, PageHeader },
  data() {
    return {
      title: "关于我们",
      items: [
        {
          text: "温湿度监测系统",
          href: "/"
        },
      
        {
          text: "关于我们",
          active: true
        }
      ],
    };
  }
};
</script>

<template>
  <Layout>
    <PageHeader :title="title" :items="items" />

    <div>
      
    </div>
    
  </Layout>
</template>