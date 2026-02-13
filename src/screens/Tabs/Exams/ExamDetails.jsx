import React from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
} from "react-native";

const { width } = Dimensions.get("window");

export default function ExamDetails({ route }) {

  const { examData } = route.params;

  const progress = 7;
  const total = examData.questions;

  return (
    <View style={styles.container}>

      <Text style={styles.heading}>Exams Details</Text>

      {/* Exam Card */}
      <View style={styles.card}>

        {/* Date Box */}
        <View style={styles.dateBox}>
          <Text style={styles.dateText}>{examData.date}</Text>
          <Text style={styles.dateText}>{examData.month}</Text>
        </View>

        {/* Middle */}
        <View style={styles.middle}>
          <Text style={styles.title}>{examData.title}</Text>
          <Text style={styles.questions}>? {examData.questions}</Text>
        </View>

        {/* Right */}
        <View style={styles.right}>
          <View style={styles.statusBadge}>
            <Text>{examData.status}</Text>
          </View>

          <View style={styles.courseBadge}>
            <Text style={{ color: "#fff" }}>{examData.course}</Text>
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
      <TouchableOpacity style={styles.generateBtn}>
        <Text style={styles.generateText}>Generate OMR Sheet</Text>
      </TouchableOpacity>

      {/* 2x2 Grid */}
      <View style={styles.grid}>

        {renderOption("Answer Key")}
        {renderOption("Scan Sheet")}
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
    width: width * 0.18, // responsive width
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
