import axios from "axios";

export const API = axios.create({
   baseURL: "http://192.168.43.172:8000/api/v1",
});
