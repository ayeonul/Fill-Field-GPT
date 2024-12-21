import Vue from "vue";
import Vuex from "vuex";
import actions from "./actions.js";
import mutations from "./mutations.js";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    isMenuOpen: true,
    isSending: false,
    useGPT: false,
    chatLog: [
      // { user: "유저예용", assistant: "GPT예용", usedFunc: false },
      // { user: "유저2예용", assistant: "GPT2예용", usedFunc: true},
    ],
    // multiResponsesArr: [{content: "원래 답안", usedFunc: true}, {content: "다른 답안 1", usedFunc: false}, {content: "다른 답안 2", usedFunc: true}],
    userStatus: {},
    multiResponsesArr: [],
    selectedMultiRes: 0,
  },
  getters: {},
  mutations,
  actions,

  modules: {},
});
