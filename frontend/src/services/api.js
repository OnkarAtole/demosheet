import axios from "axios";

export const API = axios.create({
baseURL: "http://192.168.1.8:8000/api/v1"


});
