import { StyleSheet, Text, View, TouchableOpacity } from "react-native";
import React from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRoute } from "@react-navigation/native";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as DocumentPicker from "expo-document-picker";
import Papa from "papaparse";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { bulkCreateStudents } from "../../../services/studentService";
import * as XLSX from "xlsx";   // ✅ ADDED
import { API } from "../../../services/api";
import { Linking } from "react-native";

const BulkStudentUpload = () => {

  const route = useRoute();
  const { classId } = route.params;

const handleUpload = async () => {
  try {
    const result = await DocumentPicker.getDocumentAsync({
      type: "*/*",
      copyToCacheDirectory: true,
    });

    if (result.canceled) return;

    const file = result.assets[0];
    const fileUri = file.uri;
    const fileName = file.name;

    let parsedData = [];

    // ✅ If CSV
    if (fileName.endsWith(".csv")) {
      const response = await fetch(fileUri);
      const fileContent = await response.text();

      const parsed = Papa.parse(fileContent, {
        header: true,
        skipEmptyLines: true,
      });

      parsedData = parsed.data;
    }

    // ✅ If XLSX
    else if (fileName.endsWith(".xlsx")) {
      const response = await fetch(fileUri);
      const arrayBuffer = await response.arrayBuffer();

      const workbook = XLSX.read(arrayBuffer, { type: "array" });

      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];

      parsedData = XLSX.utils.sheet_to_json(worksheet);
    }

    else {
      alert("Unsupported file type");
      return;
    }

    // console.log("Parsed Data:", parsedData);

    // ✅ Format Data Safely
    const formattedData = parsedData.map((item) => {

  // 🔥 Clean all keys (trim spaces)
  const cleanedItem = {};
  Object.keys(item).forEach((key) => {
    cleanedItem[key.trim()] = item[key];
  });

  return {
    name: cleanedItem.name?.trim(),
    roll_no: parseInt(cleanedItem.roll_no),
    email: cleanedItem.email?.trim(),
    class_id: parseInt(classId),
  };
});

    // console.log("Formatted Data:", formattedData);

    const token = await AsyncStorage.getItem("token");

    await bulkCreateStudents(formattedData, token);

    alert("Bulk upload successful!");

  } catch (error) {
    console.log("Bulk Upload Error:", error?.response?.data || error.message);
    alert("Upload failed");
  }
};


const downloadDemoFile = () => {
  const apiBase = API.defaults.baseURL;  // e.g. http://IP:8000/api/v1
  const rootUrl = apiBase.replace("/api/v1", "");  // remove api prefix

  const fileUrl = `${rootUrl}/static/student_demo.xlsx`;

  // console.log("DOWNLOAD URL:", fileUrl);

  Linking.openURL(fileUrl);
};

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      <View style={styles.container}>

        <Text style={styles.title}>
          Bulk Upload -Class {classId}
        </Text>

        <View style={styles.uploadBox}>
          <MaterialIcons name="upload-file" size={50} color="#1f3c88" />
          <Text style={styles.uploadText}>
            Upload Excel (.xlsx) file
          </Text>
        </View>

        <TouchableOpacity style={styles.uploadBtn} onPress={handleUpload}>
          <Text style={{ color: "#fff", fontWeight: "bold" }}>
            Choose File
          </Text>
        </TouchableOpacity>
        <TouchableOpacity 
  style={[styles.uploadBtn, { marginTop: 15, backgroundColor: "#28a745" }]} 
  onPress={downloadDemoFile}
>
  <Text style={{ color: "#fff", fontWeight: "bold" }}>
    Download Demo File
  </Text>
</TouchableOpacity>

      </View>
    </SafeAreaView>
  );
};

export default BulkStudentUpload;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#1f3c88",
    marginBottom: 30,
  },
  uploadBox: {
    borderWidth: 2,
    borderColor: "#ddd",
    borderStyle: "dashed",
    padding: 40,
    borderRadius: 15,
    alignItems: "center",
    marginBottom: 30,
  },
  uploadText: {
    marginTop: 10,
    color: "#777",
  },
  uploadBtn: {
    backgroundColor: "#1f3c88",
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
  },
});
