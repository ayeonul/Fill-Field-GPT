import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import Unicon from "vue-unicons/dist/vue-unicons-vue2.umd";
import {
  uniBars,
  uniMessage,
  uniExport,
  uniCommentAltDownload,
  uniQuestionCircle,
  uniUserNurseMonochrome,
  uniAngleDown,
  uniEllipsisV,
  uniSync,
} from "vue-unicons/dist/icons";

Unicon.add([
  uniBars,
  uniMessage,
  uniExport,
  uniCommentAltDownload,
  uniQuestionCircle,
  uniUserNurseMonochrome,
  uniAngleDown,
  uniEllipsisV,
  uniSync,
]);
Vue.use(Unicon);

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");
