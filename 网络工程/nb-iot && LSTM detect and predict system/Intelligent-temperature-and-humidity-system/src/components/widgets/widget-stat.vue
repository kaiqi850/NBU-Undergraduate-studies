<script>
/**
 * Widget-stat component -- specify the widget title, image, value, subtext and color of subtext.
 */
export default {
  props: {
    title: {
      type: String,
      default: ""
    },
    image: {
      type: String,
      default: ""
    },
    value: {
      type: String,
      default: ""
    },
    subText: {
      type: String,
      default: ""
    },
    color: {
      type: String,
      default: ""
    },
    arrowup:{
      type: Boolean,
      default: true
    }
  }
};
</script>

<template>
  <div class="card mini-stat bg-primary text-white">
    <div class="card-body">
      <div class="mb-4">
        <div class="float-start mini-stat-img me-4">
          <img :src="`${image}`" alt />
        </div>
        <h5 class="font-size-18 text-uppercase mt-0 text-white-50">{{title}}</h5>
        <h4 class="fw-medium font-size-24">
          {{value}}
          <i v-if="arrowup" class="mdi mdi-arrow-up text-success ms-2"></i>
          <i v-else class="mdi mdi-arrow-down text-success ms-2"></i>
        </h4>
        <div :class="`mini-stat-label bg-${color}`">
          <p class="mb-0">{{subText}}</p>
        </div>
      </div>
      <div class="pt-2">
        <div class="float-end">
          <a href="#" class="text-white-50">
            <i class="mdi mdi-arrow-right h5"></i>
          </a>
        </div>
        <p class="text-white-50 mb-0 mt-1">过去一小时</p>
      </div>
    </div>
  </div>
</template>