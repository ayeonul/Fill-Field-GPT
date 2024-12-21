import { chatPost, greeting } from "./api.js";

export default {
  async CHAT({ state }, userInput) {
    if (userInput.trim() && !state.isSending) {
      state.isSending = true;
      state.chatLog.push({ user: userInput.trim() });

      let chatLog = state.chatLog
        .map((obj) => {
          let tempArr = [];
          if (obj.user) {
            tempArr.push({ role: "user", content: obj.user });
          }
          if (obj.assistant) {
            tempArr.push({ role: "assistant", content: obj.assistant });
          }
          if (obj.args) {
            tempArr.push({
              role: "function",
              name: obj.usedFunc,
              content: JSON.stringify(obj.args),
            });
          }
          return tempArr;
        })
        .reduce((acc, val) => acc.concat(val), []);

      const payload = { messages: chatLog, user_status: state.userStatus };
      const res = await chatPost(payload);
      const resData = res.data;

      state.chatLog[state.chatLog.length - 1].assistant =
        resData.chat_res.res[0].content;
      state.chatLog[state.chatLog.length - 1].usedFunc = resData?.func_name;
      state.chatLog[state.chatLog.length - 1].args = resData?.args;

      if (resData?.args) {
        state.userStatus = { ...state.userStatus, ...resData.args };
      }

      state.isSending = false;
    }
  },
  async CALL_GREETING({ state }) {
    state.isSending = true;

    const res = await greeting();
    const resData = res.data.res;

    state.chatLog.push({
      user: null,
      assistant: resData[0].content,
      args: null,
      usedFunc: null,
    });
    state.isSending = false;
  },
  async RESET_CHAT_LOG({ state, dispatch }) {
    state.chatLog = [];
    state.userStatus = {};
    return dispatch("CALL_GREETING");
  },
};
