import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  FlatList,
} from "react-native";
import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRoute } from "@react-navigation/native";
import { useFocusEffect } from "@react-navigation/native";
import { getStudentsByClass } from "../../../services/studentService";
import AsyncStorage from "@react-native-async-storage/async-storage";
const StudentDetailScreen = ({ navigation }) => {
  const route = useRoute();
  const { classItem } = route.params; // 👈 selected class
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  // const [students, setStudents] = useState([
  //   { id: "1", name: "Onkar Atole" },
  //   { id: "2", name: "Rahul Patil" },
  //   { id: "3", name: "Sneha Kulkarni" },
  // ]);
  const fetchStudents = async () => {
    try {
      setLoading(true);

      const token = await AsyncStorage.getItem("token");

      const data = await getStudentsByClass(classItem.id, token);

      const formattedData = data.map((item) => ({
        id: item.id.toString(),
        name: item.name,
      }));

      setStudents(formattedData);
    } catch (error) {
      console.log(
        "Fetch students error:",
        error.response?.data || error.message,
      );
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    React.useCallback(() => {
      fetchStudents();
    }, []),
  );

  const handleAddStudent = () => {
    navigation.navigate("AddStudent", {
      classId: classItem.id,
    });
  };

  const renderStudent = ({ item }) => (
    <View style={styles.studentCard}>
      <Text style={styles.studentName}>{item.name}</Text>
    </View>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      <View style={styles.container}>
        {/* HEADER */}
        <View style={styles.header}>
          <Text style={styles.title}>{classItem.class}</Text>
          <TouchableOpacity style={styles.addbtn} onPress={handleAddStudent}>
            <Text style={styles.addtext}>Add Student</Text>
          </TouchableOpacity>
        </View>

        {students.length === 0 && !loading && (
          <Text style={{ marginTop: 20, color: "gray" }}>
            No students in this class
          </Text>
        )}

        {/* STUDENT LIST */}
        <FlatList
          data={students}
          keyExtractor={(item) => item.id}
          renderItem={renderStudent}
          showsVerticalScrollIndicator={false}
        />
      </View>
    </SafeAreaView>
  );
};

export default StudentDetailScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 20,
    marginTop: 30,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 15,
  },
  title: {
    color: "#1f3c88",
    fontSize: 20,
    fontWeight: "bold",
  },
  addbtn: {
    backgroundColor: "#d9d9d9",
    borderRadius: 25,
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  addtext: {
    fontWeight: "500",
  },

  /* 🔥 Attractive Student Card */
  studentCard: {
    borderWidth: 1,
    borderColor: "#eee",
    padding: 15,
    borderRadius: 12,
    marginTop: 12,
    backgroundColor: "#fafafa",
    elevation: 2,
  },
  studentName: {
    fontSize: 15,
    fontWeight: "600",
  },
});
