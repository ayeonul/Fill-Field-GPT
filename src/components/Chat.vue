<template>
  <div class="main-container" :style="setHeight()">
    <transition name="slide-nav">
      <Nav v-show="isMenuOpen" />
    </transition>
    <div class="chat-nav-container" :style="containerStyle">
      <div class="chat-container">
        <div
          class="chat-history-scroll-container"
          :class="{ shadow: showShadow }"
        >
          <div class="scroll-viewer" ref="scrollViewer" @scroll="checkScroll">
            <!-- 챗봇 로그 시작 -->
            <div class="conversation-container">
              <div v-for="(chat, index) in chatLog" :key="'chat' + index">
                <div class="user-query" v-show="chat.user != null">
                  <div class="chat-user-profile">
                    <unicon
                      name="user-nurse"
                      fill="#eed814"
                      icon-style="monochrome"
                      width="30px"
                      height="30px"
                    />
                  </div>
                  <div class="user-text">{{ chat.user }}</div>
                  <!-- <div v-if="index === chatLog.length - 1" class="edit-query-btn">
                  <unicon
                    name="pen"
                    width="20px"
                    height="20px"
                    style="position: relative; top: 8px"
                  />
                </div> -->
                </div>
                <!-- 챗봇 답안 -->
                <div v-show="chat.assistant" class="model-response">
                  <div class="response-container">
                    <div class="model-res-container">
                      <div class="model-pic-container">
                        <div class="model-pic">
                          <img
                            v-if="index === chatLog.length - 1"
                            src="https://www.gstatic.com/lamda/images/sparkle_resting_v2_1ff6f6a71f2d298b1a31.gif"
                            width="30px"
                            height="30px"
                          />
                          <img
                            v-else
                            src="https://www.gstatic.com/lamda/images/logo_single_color_v2_0aa36c7aa309a6fe6bd2.svg"
                            width="30px"
                            height="30px"
                          />
                        </div>
                      </div>
                      <div class="model-res-content">
                        <!-- <div v-if="contents.type == 'speak'"> -->
                        <div>
                          <MdViewer :markdown="chat.assistant" />
                        </div>
                        <div class="model-res-bottom">
                          <div class="message-actions-container">
                            <div class="message-reactions-container">
                              <div
                                class="mulit-response-container"
                                v-show="chat.args"
                                style="
                                  background-color: #666;
                                  color: #fff;
                                  font-size: 0.7rem;
                                "
                              >
                                {{ chat.args }}
                              </div>
                              <!-- <button
                              v-for="(btn, btnIdx) in chat.assistant.button"
                              class="reaction-btn"
                              @click="btnAction(btn)"
                            >
                              {{ btn.text }}
                            </button> -->
                            </div>
                          </div>
                        </div>
                        <!-- </div> -->
                        <!-- <div v-else-if="contents.type == 'carousel'">
                          <div
                            v-for="(slide, slideIdx) in contents.content"
                            :key="slideIdx"
                            v-if="slideIdx === activeSlide"
                            class="slide"
                          >
                            <MdViewer
                              :markdown="slide.text"
                              :image="slide.image"
                            />
                            <div class="model-res-bottom">
                              <div class="message-actions-container">
                                <div class="message-reactions-container">
                                  <button
                                    v-for="(btn, btnIdx) in slide.button"
                                    class="reaction-btn"
                                    @click="btnAction(btn)"
                                  >
                                    {{ btn.text }}
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                          <button @click="prevSlide(contents.content)">
                            Prev
                          </button>
                          <button @click="nextSlide(contents.content)">
                            Next
                          </button>
                        </div> -->
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="isSending" class="model-response">
                <div class="response-container">
                  <div class="model-res-container">
                    <div class="model-pic-container">
                      <div class="model-pic">
                        <img
                          src="https://www.gstatic.com/lamda/images/sparkle_thinking_v2_e272afd4f8d4bbd25efe.gif"
                          width="30px"
                          height="30px"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 챗 로그 종료 -->
          </div>
        </div>

        <div class="bottom-container">
          <div class="input-area-container">
            <div class="input-area">
              <div class="input-field">
                <div class="text-input" :style="promptOutline">
                  <textarea
                    placeholder="여기에 답변을 입력하세요."
                    ref="promptInput"
                    v-model="userPrompt"
                    @input="adjustHeight"
                    @focus="focusOnPrompt"
                    @blur="blurOutPrompt"
                    @keydown.enter.exact.prevent="chatSend"
                  />
                </div>
              </div>
              <div v-if="!userPrompt.trim()" class="send-btn">
                <unicon
                  name="message"
                  class="send-btn-icon"
                  fill="rgba(31, 31, 31, 0.38)"
                />
              </div>
              <div v-else class="send-btn send-btn-clickable" @click="chatSend">
                <unicon name="message" class="send-btn-icon" fill="#ebd514" />
              </div>
            </div>
          </div>
        </div>
        <div class="caution">
          <!-- <p class="caution-text">
            Bard가 부정확하거나 불쾌감을 주는 정보를 표시할 수 있으며, 이는
            Google의 입장을 대변하지 않습니다.
            <a
              class="caution-text-link"
              @click="
                newTabUrl(
                  'https://support.google.com/bard/answer/13594961?visit_id=638254157390045903-3599147583&p=privacy_notice&rd=1#privacy_notice'
                )
              "
              >Bard 개인정보처리방침</a
            >
          </p> -->
          <p class="caution-text"></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Nav from "@/components/Nav.vue";
import MdViewer from "@/components/MdViewer.vue";
import { mapState, mapActions } from "vuex";

export default {
  props: {
    height: {
      required: true,
    },
  },
  components: {
    Nav,
    MdViewer,
  },
  computed: {
    ...mapState([
      "isSending",
      "isMenuOpen",
      "chatLog",
      "multiResponsesArr",
      "selectedMultiRes",
    ]),
    containerStyle() {
      return this.isMenuOpen ? { marginLeft: "258px" } : { marginLeft: "0" };
      // return { marginLeft: "0" };
    },
  },

  data() {
    return {
      randomSample: [],
      promptOutline: { border: "1px solid rgb(128,134,139)", outline: "none" },
      userPrompt: "",
      showMultiResponse: false,
      showShadow: false,
      activeSlide: 0,
    };
  },
  mounted() {
    this.CALL_GREETING();
  },

  methods: {
    ...mapActions(["CHAT", "CALL_GREETING"]),
    newTabUrl(url) {
      window.open(url, "_blank");
    },
    setHeight() {
      return { height: this.height };
    },
    adjustHeight() {
      this.$nextTick(() => {
        this.$refs.promptInput.style.height = "1px";
        this.$refs.promptInput.style.height =
          this.$refs.promptInput.scrollHeight - 30 + "px";
      });
    },
    multiResponseHandler() {
      this.showMultiResponse = !this.showMultiResponse;
    },
    isSelectedRes(idx) {
      if (idx === this.selectedMultiRes) {
        return { borderColor: "#ebd514", backgroundColor: "#d3e3fd" };
      }
    },
    isSelectedResLabel(idx) {
      if (idx === this.selectedMultiRes) {
        return {
          color: "#fff",
          backgroundColor: "#ebd514",
        };
      }
    },
    checkScroll() {
      const scrollViewer = this.$refs.scrollViewer;
      const atBottom =
        scrollViewer.scrollHeight - scrollViewer.scrollTop ===
        scrollViewer.clientHeight;

      if (!atBottom) {
        this.showShadow = true;
      } else {
        this.showShadow = false;
      }
    },
    focusOnPrompt() {
      this.promptOutline = {
        border: "1px solid #eed814",
        outline: "1px solid #eed814",
      };
    },
    blurOutPrompt() {
      this.promptOutline = {
        border: "1px solid rgb(128,134,139)",
        outline: "none",
      };
    },
    chatSend() {
      if (!this.isSending) {
        this.CHAT(this.userPrompt);
        // this.$refs.promptInput.blur();
        this.userPrompt = "";
      }
    },
    chatSample(sampleTxt) {
      this.CHAT(sampleTxt);
    },

    nextSlide(slides) {
      if (this.activeSlide < slides.length - 1) {
        this.activeSlide++;
      }
    },
    prevSlide(slides) {
      if (this.activeSlide > 0) {
        this.activeSlide--;
      }
    },
    btnAction(btn) {
      if (btn.type == "url") {
        this.newTabUrl(btn.action);
      } else if (btn.type == "call_flow") {
        this.CALL_FLOW({ text: btn.text, code: btn.action });
      }
    },
  },
};
</script>

<style scoped>
@import url("../assets/styles/Chat.css");
</style>
