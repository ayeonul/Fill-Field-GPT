<template>
  <div class="header" :style="setHeight()">
    <div class="main-header">
      <div class="menu-bar" @click="SET_MENU_OPEN">
        <unicon name="bars" fill="#5F6368" />
      </div>
      <span class="title">진로상담챗봇</span>
    </div>
    <div class="sub-header"></div>
  </div>
</template>

<script>
import { mapMutations } from "vuex";
export default {
  props: {
    height: {
      required: true,
    },
  },
  methods: {
    ...mapMutations(["SET_MENU_OPEN"]),
    setHeight() {
      return { height: this.height };
    },
  },
};
</script>

<style scoped>
@import url("../assets/styles/Header.css");
</style>
