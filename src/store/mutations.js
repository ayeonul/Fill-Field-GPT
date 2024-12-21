export default {
  SET_MENU_OPEN(state) {
    state.isMenuOpen = !state.isMenuOpen;
  },
  USE_GPT_HANDLER(state) {
    state.useGPT = !state.useGPT;
  },
  SET_OTHER_RESPONSE(state, resNum) {
    state.selectedMultiRes = resNum;
    state.chatLog[state.chatLog.length - 1].assistant =
      state.multiResponsesArr[resNum].content;
    state.chatLog[state.chatLog.length - 1].usedFunc =
      state.multiResponsesArr[resNum].used_func;
  },
  SET_CHAT_LOG(state, data) {
    state.chatLog = data.chatLog;
    state.userStatus = data.userStatus;
  },
};
