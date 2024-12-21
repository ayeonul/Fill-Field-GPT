import axios from "axios";

const config = {
  url: "http://localhost:5000",
  chat: "/api/chat",
  greeting: "/api/greeting",
};

const chatPost = (payload) => {
  const res = axios.post(`${config.url}${config.chat}`, payload);
  return res;
};

const greeting = () => {
  const res = axios.post(`${config.url}${config.greeting}`);
  return res;
};

export { chatPost, greeting };
