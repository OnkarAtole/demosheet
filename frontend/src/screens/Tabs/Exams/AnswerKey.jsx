import React, { useState, useMemo, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import { useFocusEffect } from "@react-navigation/native";
import { SafeAreaView } from "react-native-safe-area-context";

export default function AnswerKey({ route, navigation }) {

  useFocusEffect(
    useCallback(() => {
      const parent = navigation.getParent();

      parent?.setOptions({
        tabBarStyle: { display: "none" },
      });

      return () => {
        parent?.setOptions({
          tabBarStyle: { display: "flex" },
        });
      };
    }, [navigation])
  );

  // 🔥 SAFE PARAMS
  const {
    subjects,
    totalQuestions,
    examId,
    totalSets = 1,
  } = route.params;

  // 🔥 Fallback if subjects not provided
  const subjectList = subjects
    ? subjects
    : [{ name: "General", questions: totalQuestions }];

  const setOptions = useMemo(
    () => Array.from({ length: totalSets }, (_, i) => `Set ${i + 1}`),
    [totalSets]
  );

  const [selectedSet, setSelectedSet] = useState(setOptions[0]);
  const [answers, setAnswers] = useState({});

  const options = ["A", "B", "C", "D"];

  const handleSelect = (key, option) => {
    setAnswers((prev) => ({
      ...prev,
      [selectedSet]: {
        ...prev[selectedSet],
        [key]: option,
      },
    }));
  };

  const handleSave = () => {
    console.log("Saved Answer Key:", answers);
  };

  // 🔥 Flatten subject-wise questions
  const flatQuestions = [];
  let counter = 1;

  subjectList.forEach((subject) => {
    for (let i = 1; i <= subject.questions; i++) {
      flatQuestions.push({
        subject: subject.name,
        questionNumber: counter,
        displayNumber: i,
      });
      counter++;
    }
  });

  const renderItem = ({ item }) => {
    const selected =
      answers[selectedSet]?.[item.questionNumber];

    return (
      <View style={styles.row}>
        <Text style={styles.questionText}>
          {item.questionNumber}
        </Text>

        <View style={styles.optionsRow}>
          {options.map((option) => {
            const isSelected = selected === option;

            return (
              <TouchableOpacity
                key={option}
                style={[
                  styles.optionCircle,
                  isSelected && styles.selected,
                ]}
                onPress={() =>
                  handleSelect(item.questionNumber, option)
                }
              >
                <Text
                  style={[
                    styles.optionText,
                    isSelected && { color: "#fff" },
                  ]}
                >
                  {option}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#f5f6fa" }}>
      <View style={styles.container}>
        <Text style={styles.heading}>Answer Key</Text>

        {/* Set Dropdown */}
        <View style={styles.dropdownContainer}>
          <Picker
            selectedValue={selectedSet}
            onValueChange={(value) => setSelectedSet(value)}
          >
            {setOptions.map((set) => (
              <Picker.Item key={set} label={set} value={set} />
            ))}
          </Picker>
        </View>

        {/* Questions List */}
        <FlatList
  data={subjectList}
  keyExtractor={(item) => item.name}
  renderItem={({ item }) => {
    return (
      <View style={{ marginBottom: 25 }}>
        {/* Subject Heading */}
        <Text style={styles.subjectHeading}>{item.name}</Text>

        {Array.from({ length: item.questions }, (_, i) => {
          const questionNumber = i + 1;
          const key = `${item.name}-${questionNumber}`;
          const selected = answers[selectedSet]?.[key];

          return (
            <View key={key} style={styles.row}>
              <Text style={styles.questionText}>
                {questionNumber}
              </Text>

              <View style={styles.optionsRow}>
                {options.map((option) => {
                  const isSelected = selected === option;

                  return (
                    <TouchableOpacity
                      key={option}
                      style={[
                        styles.optionCircle,
                        isSelected && styles.selected,
                      ]}
                      onPress={() => handleSelect(key, option)}
                    >
                      <Text
                        style={[
                          styles.optionText,
                          isSelected && { color: "#fff" },
                        ]}
                      >
                        {option}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>
          );
        })}
      </View>
    );
  }}
/>


        {/* Save Button */}
        <TouchableOpacity style={styles.saveBtn} onPress={handleSave}>
          <Text style={styles.saveText}>Save</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f6fa",
    padding: 20,
    paddingTop: 40,
  },

  heading: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 20,
    color: "#1f3c88",
  },

  dropdownContainer: {
    marginBottom: 15,
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 10,
    elevation: 2,
  },

  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 18,
    paddingVertical: 5,
  },

  questionText: {
    width: 40,
    fontSize: 16,
    fontWeight: "600",
  },

  optionsRow: {
    flexDirection: "row",
    marginLeft: 20,
  },

  optionCircle: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: "#ddd",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },

  selected: {
    backgroundColor: "#0a7d12",
  },

  optionText: {
    fontWeight: "bold",
    fontSize: 16,
  },

  saveBtn: {
    backgroundColor: "#2e64b5",
    padding: 15,
    borderRadius: 30,
    alignItems: "center",
    marginTop: 10,
  },

  saveText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  subjectHeading: {
  fontSize: 18,
  fontWeight: "bold",
  marginBottom: 10,
  color: "#2e64b5",
},

});
