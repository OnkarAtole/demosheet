import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
} from "react-native";

const { width } = Dimensions.get("window");
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getExamDetail } from "../../../services/examService";
import * as FileSystem from "expo-file-system";
import * as Sharing from "expo-sharing";
import { generateOMR } from "../../../services/examService";
import { downloadResultsExcel } from "../../../services/examService";
export default function ExamDetails({ route, navigation }) {
  const { examData } = route.params;

  // Placeholder status if needed
  const status = "Ongoing";
  
  const formatDate = (dateString) => {
    if (!dateString) return { day: "??", month: "???" };
    try {
      const date = new Date(dateString);
      const day = date.getDate();
      const month = date.toLocaleString("en-US", { month: "short" }).toUpperCase();
      return { day, month };
    } catch (err) {
      return { day: "??", month: "???" };
    }
  };

  const { day, month } = formatDate(examData.exam_date);

  //   const openAnswerKey = async () => {
  //   const token = await AsyncStorage.getItem("token");
  //   const response = await getExamDetail(examData.id, token);

  //   navigation.navigate("AnswerKey", {
  //     examId: response.data.id,
  //     totalSets: response.data.exam_set,
  //     subjects: response.data.subjects
  //   });
  // };
  const openAnswerKey = () => {
    // console.log("CLICKED ANSWER KEY");
    // console.log("DATA:", examData);

    navigation.navigate("AnswerKey", {
      examId: examData.id,
      totalSets: examData.exam_set,
      subjects: examData.subjects || [],
    });
  };

  const downloadOMR = async () => {
    try {
      const response = await generateOMR(examData.id);

      const fileUri = FileSystem.documentDirectory + "OMR.pdf";

      const reader = new FileReader();

      reader.onload = async () => {
        const base64 = reader.result.split(",")[1];

        await FileSystem.writeAsStringAsync(fileUri, base64, {
          encoding: FileSystem.EncodingType.Base64,
        });

        await Sharing.shareAsync(fileUri);
      };

      reader.readAsDataURL(response.data);
    } catch (error) {
      console.log("Download error:", error);
    }
  };


  const downloadExcel = async () => {
  try {
    const response = await downloadResultsExcel(examData.id);

    // const fileUri = FileSystem.documentDirectory + "results.xlsx";
    const fileUri = FileSystem.documentDirectory + `${examData.exam_name}_results.xlsx`;

    const reader = new FileReader();

    reader.onload = async () => {
      const base64 = reader.result.split(",")[1];

      await FileSystem.writeAsStringAsync(fileUri, base64, {
        encoding: FileSystem.EncodingType.Base64,
      });

      await Sharing.shareAsync(fileUri);
    };

    reader.readAsDataURL(response.data);
  } catch (error) {
    console.log("Excel download error:", error);
  }
};


  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Exams Details</Text>

      {/* Exam Card */}
      <View style={styles.card}>
        <View style={styles.dateBox}>
          <View style={styles.dateInner}>
            <Text style={styles.dateDay}>{day}</Text>
            <Text style={styles.dateMonth}>{month}</Text>
          </View>
        </View>

        <View style={styles.middle}>
          <Text style={styles.title}>{examData.exam_name}</Text>
          <Text style={styles.questions}>👥 {examData.student_count || 0} students</Text>
        </View>

        <View style={styles.right}>
          <View style={styles.statusBadge}>
            <Text>{status}</Text>
          </View>

          <View style={styles.courseBadge}>
            <Text style={{ color: "#fff" }}>{examData.class_name}</Text>
          </View>
        </View>
      </View>

      {/* Progress section removed as it was not part of original design */}

      {/* Generate Button */}
      <TouchableOpacity style={styles.generateBtn} onPress={downloadOMR}>
        <Text style={styles.generateText}>Generate OMR Sheet</Text>
      </TouchableOpacity>

      {/* Grid */}
      <View style={styles.grid}>
        <TouchableOpacity
          style={styles.optionBox}
          onPress={openAnswerKey}
        >
          <View style={styles.circle} />
          <Text style={styles.optionText}>Answer Key</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.optionBox}
          onPress={() =>
            navigation.navigate("OMRScanner", {
              examId: examData.id,
              totalPages: examData.total_pages || 1,
            })
          }
        >
          <View style={styles.circle} />
          <Text style={styles.optionText}>Scan Sheet</Text>
        </TouchableOpacity>
        {renderOption("Download Excel", downloadExcel)}
        {renderOption("Analysis")}
      </View>
    </View>
  );
}

// const renderOption = (title) => (
//   <TouchableOpacity style={styles.optionBox}>
//     <View style={styles.circle} />
//     <Text style={styles.optionText}>{title}</Text>
//   </TouchableOpacity>
// );
const renderOption = (title, onPress) => (
  <TouchableOpacity style={styles.optionBox} onPress={onPress}>
    <View style={styles.circle} />
    <Text style={styles.optionText}>{title}</Text>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f2f2f2",
    padding: 20,
    paddingTop: 40,
  },

  heading: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 20,
    color: "#1f3c88",
  },

  card: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 15,
    borderRadius: 8,
    justifyContent: "space-between",
    alignItems: "center",
  },

  dateBox: {
    backgroundColor: "#ddd",
    paddingVertical: 12,
    width: width * 0.18,
    alignItems: "center",
    justifyContent: "center",
  },

  dateInner: {
    alignItems: "center",
  },

  dateDay: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#222",
  },

  dateMonth: {
    fontSize: 12,
    fontWeight: "600",
    color: "#555",
    marginTop: -2,
  },

  middle: {
    flex: 1,
    marginLeft: 15,
  },

  title: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 5,
  },

  questions: {
    fontSize: 14,
  },

  right: {
    alignItems: "flex-end",
  },

  statusBadge: {
    backgroundColor: "#e0e0e0",
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 5,
    marginBottom: 8,
  },

  courseBadge: {
    backgroundColor: "#9e9e9e",
    paddingHorizontal: 15,
    paddingVertical: 6,
    borderRadius: 5,
  },

  progressContainer: {
    marginTop: 25,
  },

  progressBackground: {
    height: 10,
    backgroundColor: "#ddd",
    borderRadius: 10,
    overflow: "hidden",
  },

  progressFill: {
    height: 10,
    backgroundColor: "#6a4fb3",
  },

  progressText: {
    alignSelf: "flex-end",
    marginTop: 5,
    fontWeight: "500",
  },

  generateBtn: {
    marginTop: 20,
    backgroundColor: "#4f6cc3",
    padding: 15,
    borderRadius: 30,
    alignItems: "center",
  },

  generateText: {
    color: "#fff",
    fontWeight: "bold",
  },

  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    marginTop: 30,
  },

  optionBox: {
    width: "48%",
    alignItems: "center",
    marginBottom: 25,
  },

  circle: {
    width: width * 0.25,
    height: width * 0.25,
    borderRadius: (width * 0.25) / 2,
    backgroundColor: "#ccc",
    marginBottom: 10,
  },

  optionText: {
    fontWeight: "600",
    textAlign: "center",
  },
});
