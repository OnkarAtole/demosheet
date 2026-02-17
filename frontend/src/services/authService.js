import { API } from "./api";
import AsyncStorage from "@react-native-async-storage/async-storage";

export const signup = async (data) => {
  return API.post("/auth/signup", data);
};

export const signin = async (data) => {
  const response = await API.post("/auth/signin", data);
  await AsyncStorage.setItem("token", response.data.access_token);
  return response;
};



export const logout = async () => {
  await AsyncStorage.removeItem("token");
};

export const getToken = async () => {
  return await AsyncStorage.getItem("token");
}


