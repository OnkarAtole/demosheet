import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Image,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { Ionicons } from "@expo/vector-icons";

export default function LoginScreen({ navigation }) {
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = () => {
    // Example navigation after login
    navigation.navigate("Home");
  };

  return (
    <SafeAreaView style={{ flex: 1,backgroundColor:"white"}}>
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={{ flex: 1}}
    >
      <ScrollView
         contentContainerStyle={{flexGrow: 1,paddingBottom: 50, }}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
      <View style={styles.container}>
        <Text style={styles.title}>Log in</Text>
        <Text style={styles.subtitle}>Hi! Welcome</Text>

        {/* EMAIL */}
        <Text style={styles.label}>Email Address</Text>
        <TextInput
          placeholder="Enter Your Email"
          style={styles.input}
          placeholderTextColor="#999"
        />

        {/* PASSWORD */}
        <Text style={styles.label}>Password</Text>
        <View style={styles.passwordBox}>
          <TextInput
            placeholder="Enter Your Password"
            secureTextEntry={!showPassword}
            style={{ flex: 1 }}
            placeholderTextColor="#999"
          />
          <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
            <Ionicons
              name={showPassword ? "eye" : "eye-off"}
              size={20}
              color="#555"
            />
          </TouchableOpacity>
        </View>
       
        
        


        {/* LOGIN BUTTON */}
        <TouchableOpacity style={styles.loginBtn} onPress={handleLogin}>
          <Text style={styles.loginText}>Log In</Text>
        </TouchableOpacity>

        {/* FORGOT PASSWORD */}
        <TouchableOpacity>
          <Text style={styles.forgot}>Forgotten your password ?</Text>
        </TouchableOpacity>

        {/* DIVIDER */}
        <View style={styles.dividerRow}>
          <View style={styles.line} />
          <Text style={styles.orText}>Or sign in with</Text>
          <View style={styles.line} />
        </View>

        {/* SOCIAL LOGIN */}
        <View style={styles.socialRow}>
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

        {/* REGISTER */}
        <View style={styles.bottomRow}>
          <Text>Don't have an account ? </Text>
          <TouchableOpacity onPress={() => navigation.navigate("Register")}>
            <Text style={styles.create}>Create an Account</Text>
          </TouchableOpacity>
        </View>
      </View>
      </ScrollView>
    </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    paddingHorizontal: 25,
    justifyContent: "center",
  },
  title: {
    fontSize: 26,
    fontWeight: "bold",
    textAlign: "center",
  },
  subtitle: {
    textAlign: "center",
    marginBottom: 30,
    color: "#666",
  },
  label: {
    marginTop: 15,
    marginBottom: 5,
    color: "#444",
    fontSize: 14,
  },
  input: {
    borderBottomWidth: 1,
    borderColor: "#ccc",
    paddingVertical: 10,
    fontSize: 15,
  },
  passwordBox: {
    flexDirection: "row",
    alignItems: "center",
    borderBottomWidth: 1,
    borderColor: "#ccc",
    paddingVertical: 10,
  },
  loginBtn: {
    backgroundColor: "#000",
    marginTop: 30,
    paddingVertical: 15,
    borderRadius: 25,
    alignItems: "center",
  },
  loginText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  forgot: {
    marginTop: 15,
    textAlign: "center",
    color: "#333",
  },
  dividerRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 25,
  },
  line: {
    flex: 1,
    height: 1,
    backgroundColor: "#ddd",
  },
  orText: {
    marginHorizontal: 10,
    color: "#888",
  },
  socialRow: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: 20,
  },
  icon: {
    width: 45,
    height: 45,
    marginHorizontal: 10,
  },
  bottomRow: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: 30,
  },
  create: {
    fontWeight: "bold",
  },
});
