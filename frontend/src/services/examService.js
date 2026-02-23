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




export const getExams = async (token) => {
  try {
    const response = await API.get("/exams/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;

  } catch (error) {
    console.log("Get exams error:", error.response?.data || error.message);
    throw error;
  }
};



export const saveAnswerKey = async (examId, answers, token) => {
  return API.post(
    `/answer-key/${examId}`,
    { answers },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
};

// ✅ Get Answer Key
export const getAnswerKey = async (examId, token) => {
  return API.get(
    `/answer-key/${examId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
};

export const getExamDetail = async (examId, token) => {
  return API.get(`/exams/${examId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};




export const generateOMR = async (examId) => {
   return API.get(`/exams/generate-omr/${examId}`, {
    responseType: "blob",   
  });
};