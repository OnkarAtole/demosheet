import { StyleSheet, Text, View, TouchableOpacity } from "react-native";
import React from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRoute } from "@react-navigation/native";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";

const BulkStudentUpload = () => {

  const route = useRoute();
  const { classItem } = route.params;

  const handleUpload = () => {
    console.log("Upload Excel/CSV for:", classItem.class);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      <View style={styles.container}>

        <Text style={styles.title}>
          Bulk Upload - {classItem.class}
        </Text>

        <View style={styles.uploadBox}>
          <MaterialIcons name="upload-file" size={50} color="#1f3c88" />
          <Text style={styles.uploadText}>
            Upload Excel (.xlsx) or CSV file
          </Text>
        </View>

        <TouchableOpacity style={styles.uploadBtn} onPress={handleUpload}>
          <Text style={{ color: "#fff", fontWeight: "bold" }}>
            Choose File
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
