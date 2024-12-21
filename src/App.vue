<template>
  <div id="app">
    <MainView />
  </div>
</template>

<script>
import MainView from "@/views/MainView.vue";
export default {
  components: {
    MainView,
  },
};
</script>

<style>
html,
body {
  margin: 0;
  padding: 0;
  font-family: "Noto Sans", sans-serif;
}

.title {
  font-weight: 600;
  font-size: 21px;
  color: #5f6368;
}
</style>
