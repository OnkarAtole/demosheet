import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  FlatList,
} from "react-native";
import React, { useState, useEffect } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { Modal, TextInput } from "react-native"; //add
import { createClass, getClasses } from "../../../services/classService"; //add
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect } from "@react-navigation/native";

const ClassScreen = ({ navigation }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [newClassName, setNewClassName] = useState("");
  const [classData, setClassData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchClasses = async () => {
    try {
      setLoading(true); 
      const token = await AsyncStorage.getItem("token");

      const data = await getClasses(token);


      const formattedData = data.map((item) => ({
        id: item.id.toString(),
        class: item.classname,
        students: item.student_count, 
      }));

      setClassData(formattedData);
    } catch (error) {
      console.log(
        "Error fetching classes:",
        error.response?.data || error.message,
      ); 
    } finally {
      setLoading(false); 
    }
  };

  useFocusEffect(
  React.useCallback(() => {
    fetchClasses();
  }, [])
);


  const handleAdd = () => {
    setModalVisible(true);
  };

  const handleSaveClass = async () => {
    if (!newClassName.trim()) return;

    try {
      setLoading(true);
      const token = await AsyncStorage.getItem("token");

      await createClass(newClassName, token); 

      await fetchClasses(); 

      setNewClassName("");
      setModalVisible(false);
    } catch (error) {
  if (error.response?.status === 400) {
    alert("Class already exists");
  } else {
    alert("Something went wrong");
  }
}
  };

  const handlePress = (item) => {
    navigation.navigate("StudentDetail", { classItem: item });

  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.card} activeOpacity={1}>
      <View>
        <Text style={styles.titleHead}>{item.class}</Text>
        <Text style={styles.subtitleHead}>{item.students}</Text>
      </View>
      <TouchableOpacity
        style={styles.pressbtn}
        onPress={() => handlePress(item)}
      >
        <Text style={styles.pressText}>View Student</Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      <Modal visible={modalVisible} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <Text style={styles.modalTitle}>Add New Class</Text>

            <TextInput
              placeholder="Enter Class Name"
              value={newClassName}
              onChangeText={setNewClassName}
              style={styles.input}
            />

            <View
              style={{ flexDirection: "row", justifyContent: "space-between" }}
            >
              <TouchableOpacity
                style={styles.cancelBtn}
                onPress={() => setModalVisible(false)}
              >
                <Text>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.saveBtn}
                onPress={handleSaveClass}
              >
                <Text style={{ color: "#fff" }}>
                {loading ? "Saving..." : "Save"}
              </Text>
              </TouchableOpacity>
              
            </View>
          </View>
        </View>
      </Modal>

      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Class</Text>
          <TouchableOpacity style={styles.addbtn} onPress={handleAdd}>
            <Text style={styles.addtext}>Add Class</Text>
          </TouchableOpacity>
        </View>
       {classData.length === 0 && !loading && (
          <Text style={{ marginTop: 20, color: "gray" }}>
            No classes available
          </Text>
        )}
        <FlatList
          data={classData}
          // keyExtractor={(item) => item.id.toString()}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          showsVerticalScrollIndicator={false}
        />
      </View>
    </SafeAreaView>
  );
};

export default ClassScreen;

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
  card: {
    flexDirection: "row",
    justifyContent: "space-between",
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 15,
    marginTop: 15,
    borderRadius: 10,
    borderColor: "#ccc",
    alignItems: "center",
  },
  pressText: {
    color: "#6984c8",
    fontWeight: "bold",
    fontSize: 13,
  },
  titleHead: {
    fontWeight: "bold",
    fontSize: 16,
  },
  subtitleHead: {
    color: "#ccc",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.4)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalContainer: {
    width: "85%",
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 15,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 10,
    padding: 10,
    marginBottom: 20,
  },
  cancelBtn: {
    padding: 10,
  },
  saveBtn: {
    backgroundColor: "#1f3c88",
    padding: 10,
    borderRadius: 8,
  },
});
