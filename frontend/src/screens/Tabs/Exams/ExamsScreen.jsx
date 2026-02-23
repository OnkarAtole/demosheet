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
  // 🔥 Hardcoded API Response (Same structure backend will return)
  const [exams, setExams] = useState([]);

//  useEffect(() => {
//   fetchExams();
// }, []);
useFocusEffect(
  useCallback(() => {
    fetchExams();
  }, [])
);
const fetchExams = async () => {
  try {
    const token = await AsyncStorage.getItem("token");
    // console.log("TOKEN:", token);

    const data = await getExams(token);
    // console.log("EXAMS DATA:", data);

    setExams(data);
  } catch (error) {
    console.log("Exam fetch error:", error.response?.data || error.message);
  }
};


  const handlePress = (item) => {
    navigation.navigate("ExamDetails", { examData: item });
  };

  const renderItem = ({ item }) => {

  // 🔥 CHANGE 1: Create exam date object
  const examDate = new Date(item.exam_date);
  examDate.setHours(0, 0, 0, 0);

  // 🔥 CHANGE 2: Create today date without time
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // 🔥 CHANGE 3: Status logic
  let status = "";

  if (examDate > today) {
    status = "Incoming";
  } else if (examDate.getTime() === today.getTime()) {
    status = "Ongoing";     // 🔥 Today = Ongoing
  } else {
    status = "Completed";
  }

  // 🔥 CHANGE 4: Optional dynamic color
 

  return (
    <TouchableOpacity
      style={styles.card}
      activeOpacity={0.8}
      onPress={() => handlePress(item)}
    >
      {/* Date Box */}
      <View style={styles.dateBox}>
        <Text style={styles.dateText}>
          {examDate.getDate()}
        </Text>
        <Text style={styles.dateText}>
          {examDate.toLocaleString("default", { month: "short" })}
        </Text>
      </View>

     
      <View style={styles.middleSection}>
        <Text style={styles.examTitle}>{item.exam_name}</Text>

       
        <Text style={styles.questionText}>
          👥 {item.student_count}
        </Text>
      </View>

      {/* Right Section */}
      <View style={styles.rightSection}>
        <View
          style={[
            styles.statusBadge,
           
          ]}
        >
          <Text style={styles.statusText}>
            {status}   
          </Text>
        </View>

        <View style={styles.classBadge}>
          <Text style={styles.classText}>
            {item.class_name.toUpperCase()}

          </Text>
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
  minWidth: 90,
  paddingVertical: 5,
  paddingHorizontal: 10,
  borderRadius: 20,
  marginBottom: 8,
  alignItems: "center",
},


  statusText: {
    fontSize: 12,
  },

 classBadge: {
  backgroundColor: "#bdbdbd",  // ✅ keep same color
  paddingHorizontal: 14,
  paddingVertical: 6,
  borderRadius: 20,            // 🔥 pill shape (professional)
  minWidth: 80,                // 🔥 equal width
  alignItems: "center",        // 🔥 center text
  justifyContent: "center",
},


 classText: {
  color: "#fff",
  fontSize: 12,
  fontWeight: "600",
  letterSpacing: 0.5,   // 🔥 subtle professional spacing
},

});
