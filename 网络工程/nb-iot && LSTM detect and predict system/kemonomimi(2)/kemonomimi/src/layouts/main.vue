<script>
import { layoutComputed } from "@/state/helpers";

import Vertical from "@/layouts/vertical";
import Horizontal from "@/layouts/horizontal";

export default {
  components: { Vertical, Horizontal },
  computed: {
    ...layoutComputed,
    layoutType(){
      if(this.$store){
        return this.$store.state.layout.layoutType
      }else{
        return 'vertical'
      }
    }
  }
};
</script>

<template>
  <div>
    <Vertical v-if="layoutType === 'vertical'" :layout="layoutType">
      <slot />
    </Vertical>

    <Horizontal v-if="layoutType === 'horizontal'" :layout="layoutType">
      <slot />
    </Horizontal>
  </div>
</template>