import { API } from "./api";

export const createExam = async (examData, token) => {
  try {
    
    const response = await API.post(
      "/exams/",
      examData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;

  } catch (error) {
    console.log("Create exam error:", error.response?.data || error.message);
    throw error;
  }
};
