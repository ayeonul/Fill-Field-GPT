<template>
  <div class="main">
    <Header :height="'48px'" />
    <Chat :height="'calc(100vh - 90px)'" />
  </div>
</template>

<script>
import Header from "@/components/Header.vue";
import Chat from "@/components/Chat.vue";

export default {
  components: {
    Header,
    Chat,
  },
};
</script>

<style scoped></style>
