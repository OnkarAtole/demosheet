import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useEffect } from "react";
import { getExams } from "../../../services/examService";
import { useFocusEffect } from "@react-navigation/native";
import { useCallback } from "react";

export default function ExamsScreen({ navigation }) {
  const [exams, setExams] = useState([]);

  useFocusEffect(
    useCallback(() => {
      fetchExams();
    }, [])
  );

  const fetchExams = async () => {
    try {
      const token = await AsyncStorage.getItem("token");
      const data = await getExams(token);
      setExams(data);
    } catch (error) {
      console.log("Exam fetch error:", error.response?.data || error.message);
    }
  };


  const handlePress = (item) => {
    navigation.navigate("ExamDetails", { examData: item });
  };

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

  const renderItem = ({ item }) => {
    const { day, month } = formatDate(item.exam_date);
    return (
      <TouchableOpacity
        style={styles.card}
        activeOpacity={0.8}
        onPress={() => handlePress(item)}
      >
        <View style={styles.dateBox}>
        <View style={styles.dateInner}>
          <Text style={styles.dateDay}>{day}</Text>
          <Text style={styles.dateMonth}>{month}</Text>
        </View>
      </View>

        <View style={styles.middleSection}>
          <Text style={styles.examTitle}>{item.exam_name}</Text>
          <Text style={styles.questionText}>👥 {item.student_count}</Text>
        </View>

        <View style={styles.rightSection}>
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>Ongoing</Text>
          </View>
          <View style={styles.classBadge}>
            <Text style={styles.classText}>{item.class_name.toUpperCase()}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };



  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Exams</Text>

          <TouchableOpacity
            style={styles.addBtn}
            onPress={() => navigation.navigate("AddExam")}
          >
            <Text style={styles.addText}>Add Exam</Text>
          </TouchableOpacity>
        </View>

        {/* List */}
        <FlatList
          data={exams}
          keyExtractor={(item) => item.id.toString()}
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
    paddingHorizontal: 20,
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
    paddingVertical: 10,
    width: 70,
    alignItems: "center",
    justifyContent: "center",
  },

  dateInner: {
    alignItems: "center",
  },

  dateDay: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#222",
  },

  dateMonth: {
    fontSize: 10,
    fontWeight: "600",
    color: "#555",
    marginTop: -2,
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
    paddingHorizontal: 10,
    paddingVertical: 5,
    marginBottom: 8,
  },

  statusText: {
    fontSize: 12,
  },

  classBadge: {
    backgroundColor: "#bdbdbd",
    paddingHorizontal: 10,
    paddingVertical: 5,
  },

  classText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },

});
