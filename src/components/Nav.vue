<template>
  <div class="nav">
    <div class="nav-container">
      <button class="nav-menu" @click="dataDownload">
        <unicon
          name="comment-alt-download"
          class="nav-icon"
          fill="#1f1f1f"
          width="24px"
          height="24px"
        />
        <span class="nav-text">대화내역 다운로드</span>
      </button>
      <input
        type="file"
        ref="fileInput"
        @change="uploadJSON"
        style="display: none"
      />
      <button class="nav-menu" @click="triggerFileInput">
        <unicon
          name="export"
          class="nav-icon"
          fill="#1f1f1f"
          width="24px"
          height="24px"
        />
        <span class="nav-text">대화내역 업로드</span>
      </button>
      <button class="nav-menu" @click="RESET_CHAT_LOG">
        <unicon
          name="sync"
          class="nav-icon"
          fill="#1f1f1f"
          width="24px"
          height="24px"
        />
        <span class="nav-text">대화내역 초기화</span>
      </button>
      <!-- <button class="nav-menu" @click="USE_GPT_HANDLER">
        <span class="nav-text" style="margin-left: 16px">추론에 GPT 사용</span>
        <div class="switch" :class="{ 'switch-on': useGPT }">
          <div class="switch-handle"></div>
        </div>
      </button> -->
      <div class="status-section">
        <span class="nav-text" style="font-weight: 600; margin-left: 8px"
          >현재 정보</span
        >
        <pre>{{ prettyJson }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapMutations, mapActions } from "vuex";
export default {
  computed: {
    ...mapState(["useGPT", "userStatus", "chatLog", "isSending"]),
    prettyJson() {
      return JSON.stringify(this.userStatus, null, 2);
    },
  },
  methods: {
    ...mapMutations(["USE_GPT_HANDLER", "SET_CHAT_LOG"]),
    ...mapActions(["RESET_CHAT_LOG"]),
    dataDownload() {
      const targetData = {
        chatLog: this.chatLog,
        userStatus: this.userStatus,
      };
      const dataStr =
        "data:text/json;charset=utf-8," +
        encodeURIComponent(JSON.stringify(targetData));
      const downloadAnchorNode = document.createElement("a");
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute("download", "chatlog.json");
      document.body.appendChild(downloadAnchorNode); // required for firefox
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
    },
    triggerFileInput() {
      this.$refs.fileInput.click(); // 숨겨진 파일 업로드 input을 트리거
    },
    uploadJSON(event) {
      if (!this.isSending) {
        const file = event.target.files[0];
        if (file && file.type === "application/json") {
          const reader = new FileReader();
          reader.onload = () => {
            try {
              const data = JSON.parse(reader.result);
              if (
                typeof data !== "object" ||
                !data.hasOwnProperty("chatLog") ||
                !Array.isArray(data.chatLog) ||
                !data.hasOwnProperty("userStatus") ||
                typeof data.userStatus !== "object"
              ) {
                // alert("Invalid JSON format.");
                throw new Error("Invalid JSON format.");
              }
              this.SET_CHAT_LOG(data); // 읽은 데이터를 Vuex store에 저장
            } catch (error) {
              alert("Invalid JSON format.");
              console.error("Invalid JSON format", error);
            }
          };
          reader.readAsText(file);
        } else {
          alert("Invalid File Type. Please upload a JSON file.");
          console.error("Invalid File Type. Please upload a JSON file.");
        }
        this.$refs.fileInput.value = ""; // Reset file input
      }
    },
  },
};
</script>

<style scoped>
@import url("../assets/styles/Nav.css");

.switch {
  width: 45px;
  height: 20px;
  background-color: #ccc;
  border-radius: 10px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s;
  top: calc(50% - 10px);
}

.switch-on {
  background-color: #eed814;
}

.switch-handle {
  width: 16px;
  height: 16px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: left 0.3s;
}

.switch-on .switch-handle {
  left: 27px;
}
</style>
