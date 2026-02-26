import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
export const API = axios.create({
baseURL: "http://192.168.1.11:8000/api/v1"


});
API.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default API;