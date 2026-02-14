import React, { useState, useMemo } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
} from "react-native";
import { Picker } from "@react-native-picker/picker";
import { useFocusEffect } from "@react-navigation/native";
import { useCallback } from "react";
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
    }, [navigation]),
  );

  const { totalQuestions, examId, totalSets } = route.params;

  const setOptions = useMemo(
    () => Array.from({ length: totalSets }, (_, i) => `Set ${i + 1}`),
    [totalSets],
  );

  const [selectedSet, setSelectedSet] = useState(setOptions[0]);
  const [answers, setAnswers] = useState({});

  const options = ["A", "B", "C", "D"];

  const handleSelect = (question, option) => {
    setAnswers((prev) => ({
      ...prev,
      [selectedSet]: {
        ...prev[selectedSet],
        [question]: option,
      },
    }));
  };

  const handleSave = () => {
    console.log("Saved Answer Key:", answers);
  };

  const renderItem = ({ item }) => {
    const questionNumber = item;
    const selected = answers[selectedSet]?.[questionNumber];

    return (
      <View style={styles.row}>
        <Text style={styles.questionText}>{questionNumber}</Text>

        <View style={styles.optionsRow}>
          {options.map((option) => {
            const isSelected = selected === option;

            return (
              <TouchableOpacity
                key={option}
                activeOpacity={0.7}
                style={[styles.optionCircle, isSelected && styles.selected]}
                onPress={() => handleSelect(questionNumber, option)}
              >
                <Text
                  style={[styles.optionText, isSelected && { color: "#fff" }]}
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
    <SafeAreaView
      style={{ flex: 1, backgroundColor: "#f5f6fa" }}
      edges={["top", "bottom"]}
    >
      <View style={styles.container}>
        <Text style={styles.heading}>Answer Key</Text>

        {/* Set Dropdown */}
        <View style={styles.dropdownContainer}>
          {/* <Text style={styles.setLabel}>Select Exam Set</Text> */}
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
          data={Array.from({ length: totalQuestions }, (_, i) => i + 1)}
          keyExtractor={(item) => item.toString()}
          renderItem={renderItem}
          showsVerticalScrollIndicator={false}
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
  },

  setLabel: {
    fontWeight: "600",
    marginBottom: 5,
  },

  

  row: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 18,
    paddingVertical: 5,
  },

  questionText: {
    width: 30,
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
});
