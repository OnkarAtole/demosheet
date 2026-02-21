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
import { signup ,sendOtp,verifyOtp} from "../../services/authService";

const RegisterScreen = ({ navigation }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState("");
const [email, setEmail] = useState("");
const [password, setPassword] = useState("");
const [OTP, setOTP] = useState("");


// current change 5.06  17_02
const [otpSent, setOtpSent] = useState(false);
const [otpVerified, setOtpVerified] = useState(false);
const [loadingOtp, setLoadingOtp] = useState(false);

const isValidEmail = (email) => {
  return /\S+@\S+\.\S+/.test(email);
};
  const handleRegister = async () => {
  if (!otpVerified) {
    alert("Please verify your email first");
    return;
  }

  try {
    await signup({ name, email, password });
    alert("Registration successful");
    navigation.navigate("Login");
  // } catch (error) {
  //   alert(error?.response?.data?.detail || "Registration failed");
  // }
  }catch (error) {
  let message = "Registration failed";

  if (error?.response?.data?.detail) {
    if (Array.isArray(error.response.data.detail)) {
      message = error.response.data.detail[0]?.msg || message;
    } else {
      message = error.response.data.detail;
    }
  }

  alert(message);
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
                // onChangeText={setEmail}
                 editable={!otpSent}
                  onChangeText={(text) => setEmail(text.trimStart())}
              />
            </View>
            
            
            {/* new logic for otp */}
      <View style={{ width: "100%", marginTop: 12 }}>
  <View style={styles.otpRow}>
    
    <View style={[styles.inputWrapper, { flex: 0.65 }]}>
      <Text style={styles.label}>OTP</Text>

      <TextInput
        placeholder="Enter OTP"
        placeholderTextColor="#999"
        style={styles.input}
        value={OTP}
        onChangeText={setOTP}
        editable={otpSent && !otpVerified}
      />
    </View>

    {!otpVerified && (
      <TouchableOpacity
        style={[styles.otpButtonNew, { opacity: loadingOtp ? 0.6 : 1 }]}
        disabled={loadingOtp}
        onPress={async () => {
            if (!email || email.trim() === "") {
              alert("Please enter email first");
              return;
            }

            if (!isValidEmail(email.trim())) {
              alert("Please enter valid email format");
              return;
            }

            if (otpSent && !OTP) {
              alert("Please enter OTP");
              return;
            }

            try {
              setLoadingOtp(true);

              if (!otpSent) {
                await sendOtp(email.trim());
                setOtpSent(true);
                alert("OTP sent to your email");
              } else {
                await verifyOtp(email.trim(), OTP);
                setOtpVerified(true);
                alert("OTP verified successfully");
              }
            } catch (error) {
              let message = "Something went wrong";

              if (error?.response?.data?.detail) {
                if (Array.isArray(error.response.data.detail)) {
                  message = error.response.data.detail[0]?.msg || message;
                } else {
                  message = error.response.data.detail;
                }
              }

              alert(message);
            } finally {
              setLoadingOtp(false);
            }
          }}
      >
        <Text style={styles.otpButtonTextNew}>
                        {loadingOtp ? otpSent
                            ? "Verifying..."
                            : "Sending..."
                          : !otpSent
                          ? "Get OTP"
                          : "Verify"}
                      </Text>
      </TouchableOpacity>
    )}
  </View>

  {otpSent && !otpVerified && (
    <TouchableOpacity
      onPress={() => {
        setOtpSent(false);
        setOtpVerified(false);
        setOTP("");
      }}
      style={{ alignSelf: "flex-end", marginTop: 6 }}
    >
      <Text style={{ color: "red", fontSize: 12 }}>
        Change Email
      </Text>
    </TouchableOpacity>
  )}
</View>


              {/* otp verification end */}
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
                  editable={otpVerified}

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
            {/* <TouchableOpacity
            
              style={styles.registerbtn}
              onPress={handleRegister}
            >
              <Text style={styles.registerText}>Register</Text>
            </TouchableOpacity> */}

              <TouchableOpacity
                style={[
                  styles.registerbtn,
                  { backgroundColor: otpVerified ? "#000" : "#c8c0c0" }
                ]}
                onPress={handleRegister}
                disabled={!otpVerified}
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
    borderRadius: 25,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 15,
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

// otp button style
otpLabel: {
  marginLeft: 20,
  marginBottom: 8,
  fontSize: 14,
  color: "#777",
},

otpRow: {
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
},

otpInputContainer: {
  flex: 0.65,
  borderWidth: 1,
  borderColor: "#E5E5E5",
  borderRadius: 30,
  paddingHorizontal: 20,
  paddingVertical: 12,
  backgroundColor: "#fff",
},

otpInput: {
  fontSize: 16,
},

otpButtonNew: {
  flex: 0.3,
  backgroundColor: "#4A55A2",
height: 60,

  borderRadius: 30,
  alignItems: "center",
  justifyContent: "center",
  elevation: 3,
},

otpButtonTextNew: {
  color: "white",
  fontWeight: "600",
  fontSize: 13,
}
})
