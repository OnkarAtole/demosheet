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


// for otp 
export const sendOtp = async (email) => {
  return API.post("/auth/send-otp", { email });
};

export const verifyOtp = async (email, otp) => {
  return API.post("/auth/verify-otp", { email, otp });
};

// forgot password
export const forgotPasswordSendOtp = async (email) => {
  return API.post("/auth/forgot-password/send-otp", { email });
};

export const forgotPasswordVerifyOtp = async (email, otp) => {
  return API.post("/auth/forgot-password/verify-otp", { email, otp });
};

export const resetPassword = async (email, newPassword) => {
  return API.post("/auth/reset-password", {
    email,
    new_password: newPassword,
  });
};
