import { API } from "./api";   // same API file you use for classService

// ✅ Create Student
export const createStudent = async (studentData, token) => {
  try {
    const response = await API.post(
      "/students/",
      studentData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.log(
      "Create student error:",
      error.response?.data || error.message
    );
    throw error;
  }
};

// ✅ Get Students By Class
export const getStudentsByClass = async (classId, token) => {
  try {
    const response = await API.get(
      `/students/class/${classId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.log(
      "Fetch students error:",
      error.response?.data || error.message
    );
    throw error;
  }
};

// Bulk Create Students 
export const bulkCreateStudents = async (students, token) => {
  try {
    const response = await API.post(
      "/students/bulk/",   
      students,            
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.log(
      "Bulk create error:",
      error.response?.data || error.message
    );
    throw error;
  }
};