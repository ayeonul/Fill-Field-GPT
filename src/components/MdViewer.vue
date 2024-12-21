<template>
  <div>
    <div v-if="image">
      <img :src="imgSrc" />
    </div>
    <div v-html="markedText"></div>
  </div>
</template>

<script>
import { marked } from "marked";
import hljs from "highlight.js";
import "highlight.js/styles/night-owl.css";
import VueHighlightJS from "vue-highlight.js";

export default {
  name: "MarkdownViewer",
  props: {
    markdown: {
      required: true,
    },
    image: {
      type: String,
      required: false,
    },
  },
  computed: {
    imgSrc() {
      return require(`@/assets/img/${this.image}`);
    },
  },
  data() {
    return {
      markedText: "",
    };
  },
  watch: {
    markdown(newMarkdown) {
      this.markedText = marked(newMarkdown);
    },
  },
  mounted() {
    // Set up the markdown renderer
    marked.setOptions({
      renderer: new marked.Renderer(),
      highlight: function (code, language) {
        const validLanguage = hljs.getLanguage(language)
          ? language
          : "plaintext";
        return hljs.highlight(validLanguage, code).value;
      },
      langPrefix: "hljs language-",
      pedantic: false,
      gfm: true,
      breaks: true,
      sanitize: false,
      smartLists: true,
      smartypants: false,
      xhtml: false,
    });

    if (!this.markdown) {
      this.markdown = "";
    }

    this.markedText = marked(this.markdown);
  },
  directives: {
    highlightjs: VueHighlightJS.directive,
  },
};
</script>
<style>
code:not(.hljs) {
  font-weight: bold;
}
</style>
