import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export default function ExamsScreen({ navigation }) {

  // 🔥 Hardcoded API Response (Same structure backend will return)
const [exams, setExams] = useState([
  {
    id: "1",
    date: "28",
    month: "Feb",
    title: "Unit",
    status: "Incoming",
    class: "MCA",
    subjects: [
      { name: "Math", questions: 5 },
      { name: "Physics", questions: 8 },
    ],
  },
  {
    id: "2",
    date: "5",
    month: "Mar",
    title: "Mid Term",
    status: "Completed",
    class: "BCA",
    subjects: [
      { name: "Java", questions: 10 },
      { name: "DBMS", questions: 10 },
    ],
  },
]);


  const handlePress = (item) => {
    navigation.navigate("ExamDetails", { examData: item });
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.card}
      activeOpacity={0.8}
      onPress={() => handlePress(item)}
    >
      {/* Date Box */}
      <View style={styles.dateBox}>
        <Text style={styles.dateText}>{item.date}</Text>
        <Text style={styles.dateText}>{item.month}</Text>
      </View>

      {/* Middle Section */}
      <View style={styles.middleSection}>
        <Text style={styles.examTitle}>{item.title}</Text>
        <Text style={styles.questionText}>? {item.questions}</Text>
      </View>

      {/* Right Section */}
      <View style={styles.rightSection}>
        <View style={styles.statusBadge}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>

        <View style={styles.classBadge}>
          <Text style={styles.classText}>{item.class}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
     <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
          
    <View style={styles.container}>

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Exams</Text>

        <TouchableOpacity style={styles.addBtn} onPress={() => navigation.navigate("AddExam")}>
          <Text style={styles.addText}>Add Exam</Text>
        </TouchableOpacity>
      </View>

      {/* List */}
      <FlatList
        data={exams}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        showsVerticalScrollIndicator={false}
      />
    </View>
    </SafeAreaView>
    
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: "#fff",
    paddingHorizontal:20,
    marginTop: 30,
  },

  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
  },

  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#1f3c88",
  },

  addBtn: {
    backgroundColor: "#d9d9d9",
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },

  addText: {
    fontWeight: "500",
  },

  card: {
    flexDirection: "row",
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 15,
    borderRadius: 6,
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 15,
  },

  dateBox: {
    backgroundColor: "#d9d9d9",
    padding: 10,
    alignItems: "center",
    width: 70,
  },

  dateText: {
    fontSize: 16,
    fontWeight: "bold",
  },

  middleSection: {
    flex: 1,
    marginLeft: 15,
  },

  examTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 5,
  },

  questionText: {
    fontSize: 14,
  },

  rightSection: {
    alignItems: "flex-end",
  },

  statusBadge: {
    backgroundColor: "#e0e0e0",
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 20,
    marginBottom: 8,
  },

  statusText: {
    fontSize: 12,
  },

  classBadge: {
    backgroundColor: "#bdbdbd",
    paddingHorizontal: 15,
    paddingVertical: 6,
    borderRadius: 4,
  },

  classText: {
    color: "#fff",
    fontWeight: "500",
  },

});
