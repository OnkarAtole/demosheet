import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
export const API = axios.create({
  // baseURL: "http://192.168.1.13:8000/api/v1"
  // baseURL: "http://harshalonkar.local:8000/api/v1"
  
// baseURL: "http://10.0.2.2:8000/api/v1"
// baseURL: "https://yourdomain.com/api/v1" will use this for production
baseURL:"https://omr.lmsoftwaresolutions.com/api/v1"
});
API.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default API;