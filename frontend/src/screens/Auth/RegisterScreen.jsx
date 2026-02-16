import { React, useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
} from "react-native";
import {
  Text,
  View,
  StyleSheet,
  TextInput,
  TouchableOpacity,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { signup } from "../../services/authService";

const RegisterScreen = ({ navigation }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState("");
const [email, setEmail] = useState("");
const [password, setPassword] = useState("");
const [OTP, setOTP] = useState("");


  const handleRegister = async () => {
    try {
    await signup({ name, email, password });
    navigation.navigate("Login");
  } catch (error) {
    alert("Registration failed");
  }
  };
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <KeyboardAvoidingView
        behavior={Platform.OS == "ios" ? "padding" : "height"}
        style={{ flex: 1 }}
      >
        <ScrollView
          contentContainerStyle={{
            flexGrow: 1,
            paddingBottom: 50,
            backgroundColor: "white",
          }} //imp i need to research
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.container}>
            <Text style={styles.title}>Register</Text>
            <Text style={styles.subtitle}>
              Fill your information below or register
            </Text>
            <Text style={[styles.subtitle, { paddingBottom: 15 }]}>
              with your social account
            </Text>

            <View style={styles.inputWrapper}>
              <Text style={styles.label}>Name</Text>
              <TextInput
                placeholder="Your Name"
                placeholderTextColor="#999"
                style={styles.input}
                value={name}
                onChangeText={setName}
              />
            </View>
            <View style={styles.inputWrapper}>
              <Text style={styles.label}>Email</Text>
              <TextInput
                placeholder="Enter Your Email"
                placeholderTextColor="#999"
                style={styles.input}
                value={email}
                onChangeText={setEmail}
              />
            </View>
            <View style={styles.inputWrapper}>
              <Text style={styles.label}>OTP</Text>
              <TextInput
                placeholder="Enter OTP"
                placeholderTextColor="#999"
                style={styles.input}
                value={OTP}
                onChangeText={setOTP}
              />
            </View>
            <View style={styles.inputWrapper}>
              <Text style={styles.label}>Password</Text>

              <View style={styles.inputRow}>
                <TextInput
                  placeholder="Enter your password"
                  placeholderTextColor="#999"
                  secureTextEntry={!showPassword}
                  style={styles.input}
                  value={password}
                  onChangeText={setPassword}
                />

                <TouchableOpacity
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Ionicons
                    name={showPassword ? "eye" : "eye-off"}
                    size={20}
                    color="#555"
                  />
                </TouchableOpacity>
              </View>
            </View>
            <TouchableOpacity
              style={styles.registerbtn}
              onPress={handleRegister}
            >
              <Text style={styles.registerText}>Register</Text>
            </TouchableOpacity>

            <View style={styles.linebox}>
              <View style={styles.line} />
              <Text style={styles.lineText}>Or sing up with</Text>
              <View style={styles.line} />
            </View>

            <View style={styles.socialrow}>
              <Image
                source={{
                  uri: "https://img.icons8.com/ios-filled/50/mac-os.png",
                }}
                style={styles.icon}
              />
              <Image
                source={{
                  uri: "https://img.icons8.com/color/48/google-logo.png",
                }}
                style={styles.icon}
              />
            </View>
            <View style={{flexDirection:"row", marginTop:15}}>
              <Text> Already have an account? </Text>
              <TouchableOpacity
                onPress={() => {
                  navigation.navigate("Login");
                }}
              >
                <Text style={{color:"#1e65d0", fontWeight:"bold"}}>Signup</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default RegisterScreen;
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    paddingHorizontal: 25,
    justifyContent: "center",
    alignItems: "center",
    
  },
  title: {
    fontWeight: "bold",
    fontSize: 26,
    alignItems: "center",
  },
  subtitle: {
    color: "#685a5a",
    textAlign: "center",
  },
  inputWrapper: {
    borderWidth: 1,
    borderColor: "#E5E5E5",
    borderRadius: 30,
    paddingTop: 12,
    paddingHorizontal: 20,
    paddingBottom: 8,
    marginTop: 12,
    backgroundColor: "#fff",
    position: "relative",
    width: "100%",
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 10,
  },
  label: {
    position: "absolute",
    top: -10,
    left: 20,
    backgroundColor: "#fff",
    paddingHorizontal: 6,
    fontSize: 14,
    color: "#777",
  },
  input: {
    flex: 1,
    height: 40,
    fontSize: 16,
    // paddingEnd:"40%"
  },
  inputRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  registerbtn: {
    marginTop: 15,
    backgroundColor: "#000",
    width: "100%",
    borderRadius: "25",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 15,
    borderRadius: 25,
  },
  registerText: {
    color: "white",
  },
  linebox: {
    marginTop: 25,
    alignItems: "center",
    flexDirection: "row",
  },
  line: {
    flex: 1,
    height: 1,
    backgroundColor: "#ddd",
  },
  lineText: {
    color: "#4b4040",
    paddingHorizontal: 10,
  },
  socialrow: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: 15,
  },
  icon: {
    width: 45,
    height: 45,
    marginHorizontal: 10,
  },
});
