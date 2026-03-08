// services/omrService.js

import API from "./api";

export const scanOMR = async (examId, images) => {
  const formData = new FormData();

  images.forEach((img, index) => {
    formData.append("files", {
      uri: img.uri,
      name: `omr_page_${index + 1}.jpg`,
      type: "image/jpeg",
    });
  });

  formData.append("exam_id", String(examId));

  const response = await API.post("/omr/scan-omr", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};