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
export default function ExamDetails({ route, navigation }) {
  const { examData } = route.params;

  // 🔥 CHANGE 1: Convert backend date to Date object
  const examDate = new Date(examData.exam_date);
  examDate.setHours(0, 0, 0, 0);

  // 🔥 CHANGE 2: Create today date for status logic
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // 🔥 CHANGE 3: Dynamic Status Logic
  let status = "";

  if (examDate > today) {
    status = "Incoming";
  } else if (examDate.getTime() === today.getTime()) {
    status = "Ongoing";
  } else {
    status = "Completed";
  }

  // 🔥 CHANGE 4: Use student_count instead of questions
  const progress = 0;
  const total = examData.student_count || 1;

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
  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Exams Details</Text>

      {/* Exam Card */}
      <View style={styles.card}>
        {/* 🔥 CHANGE 5: Replace old date with formatted backend date */}
        <View style={styles.dateBox}>
          <Text style={styles.dateText}>{examDate.getDate()}</Text>
          <Text style={styles.dateText}>
            {examDate.toLocaleString("default", { month: "short" })}
          </Text>
        </View>

        {/* Middle */}
        <View style={styles.middle}>
          {/* 🔥 CHANGE 6: Replace title with exam_name */}
          <Text style={styles.title}>{examData.exam_name}</Text>

          {/* 🔥 CHANGE 7: Replace ? questions with student_count */}
          <Text style={styles.questions}>👥 {examData.student_count}</Text>
        </View>

        {/* Right */}
        <View style={styles.right}>
          {/* 🔥 CHANGE 8: Replace examData.status with calculated status */}
          <View style={styles.statusBadge}>
            <Text>{status}</Text>
          </View>

          {/* 🔥 CHANGE 9: Replace class with class_name */}
          <View style={styles.courseBadge}>
            <Text style={{ color: "#fff" }}>
              {examData.class_name.toUpperCase()}
            </Text>
          </View>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        <View style={styles.progressBackground}>
          <View
            style={[
              styles.progressFill,
              { width: `${(progress / total) * 100}%` },
            ]}
          />
        </View>

        <Text style={styles.progressText}>
          {progress}/{total}
        </Text>
      </View>

      {/* Generate Button */}
      <TouchableOpacity style={styles.generateBtn} onPress={downloadOMR}>
        <Text style={styles.generateText}>Generate OMR Sheet</Text>
      </TouchableOpacity>

      {/* Grid */}
      <View style={styles.grid}>
        <TouchableOpacity
          style={styles.optionBox}
          onPress={() =>
            // navigation.navigate("AnswerKey", {
            //   subjects: examData.subjects,
            //   totalSets: 2,
            // })
            // navigation.navigate("AnswerKey", {
            //   subjects: examData.subjects || [],
            //   totalSets: 2,
            //   examId: examData.id,
            // })
            openAnswerKey()
          }
        >
          <View style={styles.circle} />
          <Text style={styles.optionText}>Answer Key</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.optionBox}
          onPress={() =>
            navigation.navigate("OMRScanner", {
              examId: examData.id,
              totalPages: examData.total_pages || 1, // adjust based on backend
            })
          }
        >
          <View style={styles.circle} />
          <Text style={styles.optionText}>Scan Sheet</Text>
        </TouchableOpacity>
        {renderOption("Download Excel")}
        {renderOption("Analysis")}
      </View>
    </View>
  );
}

const renderOption = (title) => (
  <TouchableOpacity style={styles.optionBox}>
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
    padding: 12,
    alignItems: "center",
    width: width * 0.18,
  },

  dateText: {
    fontWeight: "bold",
    fontSize: 16,
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
    borderRadius: 20,
    marginBottom: 8,

    minWidth: 90, // ✅ ensures equal width
    alignItems: "center", // ✅ center text
  },

  courseBadge: {
    backgroundColor: "#9e9e9e",
    paddingHorizontal: 15,
    paddingVertical: 6,
    borderRadius: 20, // 🔥 changed from 5 to 20 for professional pill look
    minWidth: 90, // ✅ equal width with status
    alignItems: "center",
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
