import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Switch,
  TouchableOpacity,
  TextInput,
  Alert,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import MaterialIcons from "react-native-vector-icons/MaterialIcons";
// import { checkBiometricSupport } from "../../../utils/biometricAuth";
const Settingpage = ({ navigation }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [autoScan, setAutoScan] = useState(true);
  const [negativeMarking, setNegativeMarking] = useState(false);
  const [biometric, setBiometric] = useState(false);

  const [correctMarks, setCorrectMarks] = useState("1");
  const [wrongMarks, setWrongMarks] = useState("0");
  const [totalQuestions, setTotalQuestions] = useState("50");

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    const theme = await AsyncStorage.getItem("darkMode");
    const auto = await AsyncStorage.getItem("autoScan");
    if (theme === "true") setDarkMode(true);
    if (auto === "true") setAutoScan(true);
  };

  const saveSetting = async (key, value) => {
    await AsyncStorage.setItem(key, value.toString());
  };


  // biomatric toggle handler
 const handleBiometricToggle = async () => {
  const supported = await checkBiometricSupport();

  if (!supported) {
    Alert.alert("Biometric not available on this device");
    return;
  };

  const newValue = !biometric;
  setBiometric(newValue);

  await AsyncStorage.setItem("biometricEnabled", newValue.toString());
};
  const handleDeleteAccount = () => {
    Alert.alert(
      "Delete Account",
      "This action cannot be undone.",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: () => console.log("Delete API Call Here"),
        },
      ]
    );
  };

  const SectionTitle = ({ title }) => (
    <Text style={styles.sectionTitle}>{title}</Text>
  );

  const SettingRow = ({ icon, title, rightComponent }) => (
    <View style={styles.row}>
      <View style={styles.iconCircle}>
        <MaterialIcons name={icon} size={22} color="#000" />
      </View>
      <Text style={styles.rowText}>{title}</Text>
      <View style={{ marginLeft: "auto" }}>{rightComponent}</View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>

      {/* ACCOUNT */}
      <SectionTitle title="Account" />
      <SettingRow
        icon="delete"
        title="Delete Account"
        rightComponent={
          <TouchableOpacity onPress={handleDeleteAccount}>
            <Text style={{ color: "red", fontWeight: "600" }}>Delete</Text>
          </TouchableOpacity>
        }
      />

      {/* APP PREFERENCES */}
      <SectionTitle title="App Preferences" />

      <SettingRow
        icon="dark-mode"
        title="Dark Mode"
        rightComponent={
          <Switch
            value={darkMode}
            onValueChange={(val) => {
              setDarkMode(val);
              saveSetting("darkMode", val);
            }}
          />
        }
      />

      <SettingRow
        icon="notifications"
        title="Notifications"
        rightComponent={
          <Switch
            value={notifications}
            onValueChange={setNotifications}
          />
        }
      />

      <SettingRow
        icon="camera-alt"
        title="Auto Scan After Capture"
        rightComponent={
          <Switch
            value={autoScan}
            onValueChange={(val) => {
              setAutoScan(val);
              saveSetting("autoScan", val);
            }}
          />
        }
      />





      {/* EXAM SETTINGS */}
      <SectionTitle title="Exam Settings" />

      <View style={styles.inputRow}>
        <Text style={styles.label}>Correct Marks</Text>
        <TextInput
          style={styles.input}
          value={correctMarks}
          onChangeText={setCorrectMarks}
          keyboardType="numeric"
        />
      </View>

      <View style={styles.inputRow}>
        <Text style={styles.label}>Wrong Marks</Text>
        <TextInput
          style={styles.input}
          value={wrongMarks}
          onChangeText={setWrongMarks}
          keyboardType="numeric"
        />
      </View>

      <SettingRow
        icon="remove-circle"
        title="Negative Marking"
        rightComponent={
          <Switch
            value={negativeMarking}
            onValueChange={setNegativeMarking}
          />
        }
      />

      <View style={styles.inputRow}>
        <Text style={styles.label}>Default Total Questions</Text>
        <TextInput
          style={styles.input}
          value={totalQuestions}
          onChangeText={setTotalQuestions}
          keyboardType="numeric"
        />
      </View>

      {/* SECURITY */}
      <SectionTitle title="Security" />

      <SettingRow
        icon="fingerprint"
        title="Biometric Login"
        rightComponent={
          <Switch
            value={biometric}
            onValueChange={handleBiometricToggle}
          />
        }
      />

      <SettingRow
        icon="logout"
        title="Logout From All Devices"
        rightComponent={
          <TouchableOpacity onPress={() => console.log("Logout All API")}>
            <Text style={{ fontWeight: "600" }}>Logout</Text>
          </TouchableOpacity>
        }
      />

    </ScrollView>
  );
};

export default Settingpage;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f4f4f4",
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    marginVertical: 14,
    color: "#333",
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 14,
  },
  iconCircle: {
    backgroundColor: "#e7c9c9",
    width: 38,
    height: 38,
    borderRadius: 50,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  rowText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#000",
  },
  inputRow: {
    marginVertical: 10,
  },
  label: {
    fontSize: 14,
    marginBottom: 4,
    fontWeight: "600",
  },
  input: {
    backgroundColor: "#fff",
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#ddd",
  },
});