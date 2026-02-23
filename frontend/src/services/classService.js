import { API } from "./api";   // adjust path if needed

// Create Class
export const createClass = async (className, token) => {
  try {
    const response = await API.post(
      "/classes/",
      {
        classname: className,   // must match backend field
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;
  } catch (error) {
    console.log("Create class error:", error.response?.data || error.message);
    throw error;
  }
};

// Get All Classes
export const getClasses = async (token) => {
  try {
    const response = await API.get("/classes/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error) {
    console.log("Fetch class error:", error.response?.data || error.message);
    throw error;
  }
};
export const getClassById = async (classId, token) => {
  try {
    const response = await API.get(`/classes/${classId}/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;   // ✅ ADD THIS
  } catch (error) {
    console.log("Fetch class by ID error:", error.response?.data || error.message);
    throw error;
  }
};
