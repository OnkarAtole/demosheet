import api from "./api";

export const getExamAnalysis = async (examId) => {
  try {
    const response = await api.get(`/results/analysis/${examId}`);
    return response.data;
  } catch (error) {
    console.log("Analysis fetch error:", error);
    throw error;
  }
};