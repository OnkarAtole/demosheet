import API from "./api";

export const getCurrentUser = async () => {
  const response = await API.get("/users/me");
  return response.data;
};

export const updateProfile = async (data) => {
  const response = await API.put("/users/me", data);
  return response.data;
};