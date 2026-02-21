import { StyleSheet, Text, View,KeyboardAvoidingView,Platform,ScrollView,TextInput,TouchableOpacity,Image} from 'react-native'
import {React,useState} from 'react'
import { SafeAreaView } from 'react-native-safe-area-context'
import {Ionicons} from "@expo/vector-icons"
import {forgotPasswordSendOtp,forgotPasswordVerifyOtp, resetPassword,} from "../../services/authService";



const ForgotPassword = ({navigation}) => {

const [email, setEmail] = useState("");
const [otp, setOtp] = useState("");
const [newPassword, setNewPassword] = useState("");
const [confirmPassword, setConfirmPassword] = useState("");

const [otpSent, setOtpSent] = useState(false);
const [otpVerified, setOtpVerified] = useState(false);
const [loadingOtp, setLoadingOtp] = useState(false);

const [showPassword, setShowPassword] = useState(false);


  // email valida
  const isValidEmail = (email) => {
  return /\S+@\S+\.\S+/.test(email);
};

  const handleSubmit = async () => {
  
  if (!otpVerified) {
    alert("Please verify OTP first");
    return;
  }

  if (!newPassword || !confirmPassword) {
    alert("Please fill all fields");
    return;
  }

  if (newPassword !== confirmPassword) {
    alert("Passwords do not match");
    return;
  }

  try {
    await resetPassword(email, newPassword);
    alert("Password reset successful");
    navigation.navigate("Login");
  } catch (error) {
    alert(error?.response?.data?.detail || "Something went wrong");
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
            <Text style={styles.title}>Forget passpassword </Text>
            

            <View style={styles.inputWrapper}>
              <Text style={styles.label}>Email address</Text>
              <TextInput
                placeholder="Enter Your Email"
                placeholderTextColor="#999"
                style={styles.input}
                value={email}
                onChangeText={(text) => setEmail(text.trimStart())}
                onBlur={() => {
                  if (email && !isValidEmail(email.trim())) {
                    alert("Please enter valid email format");
                  }
                }}
              />
            </View>

              
           {/* forget password */}
                        <View style={{ width: "100%", marginTop: 12 }}>
                <View style={styles.otpRow}>
                  
                  <View style={[styles.inputWrapper, { flex: 0.65 }]}>
                    <Text style={styles.label}>OTP</Text>

                    <TextInput
                      placeholder="Enter OTP"
                      placeholderTextColor="#999"
                      style={styles.input}
                      value={otp}
                      onChangeText={setOtp}
                      editable={otpSent && !otpVerified}
                    />
                  </View>

                  {!otpVerified && (
                    <TouchableOpacity
                      style={styles.otpButton}
                      disabled={loadingOtp}
                      // onPress={async () => {
                      //   try {
                      //     if (!otpSent) {
                      //       setLoadingOtp(true);
                      //       await forgotPasswordSendOtp(email);
                      //       setOtpSent(true);
                      //       alert("OTP sent successfully");
                      //     } else {
                      //       setLoadingOtp(true);
                      //       await forgotPasswordVerifyOtp(email, otp);
                      //       setOtpVerified(true);
                      //       alert("OTP verified successfully");
                      //     }
                      //   } catch (error) {
                      //     alert(error?.response?.data?.detail || "Something went wrong");
                      //   } finally {
                      //     setLoadingOtp(false);
                      //   }
                      // }}
                      onPress={async () => {
  if (!email || email.trim() === "") {
    alert("Please enter email first");
    return;
  }

  if (!isValidEmail(email.trim())) {
    alert("Please enter valid email");
    return;
  }

  try {
    if (!otpSent) {
      setLoadingOtp(true);
      await forgotPasswordSendOtp(email.trim());
      setOtpSent(true);
      alert("OTP sent successfully");
    } else {
      setLoadingOtp(true);
      await forgotPasswordVerifyOtp(email.trim(), otp);
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
  } else if (error?.response?.data?.message) {
    message = error.response.data.message;
  }

  alert(message);

  } finally {
    setLoadingOtp(false);
  }
}}
                    >
                      {/* <Text style={styles.otpButtonText}>
                        {!otpSent ? "Get OTP" : "Verify"}
                      </Text> */}
                      <Text style={styles.otpButtonText}>
                        {loadingOtp
                          ? otpSent
                            ? "Verifying..."
                            : "Sending..."
                          : !otpSent
                          ? "Get OTP"
                          : "Verify"}
                      </Text>

                    </TouchableOpacity>
                  )}
                </View>
              </View>

              <View style={styles.inputWrapper}>
              <Text style={styles.label}>New Password</Text>

              <View style={styles.inputRow}>
                <TextInput
                  placeholder="Enter your password"
                  placeholderTextColor="#999"
                  secureTextEntry={!showPassword}
                  style={styles.input}
                  editable={otpVerified}
                  value={newPassword}
                  onChangeText={setNewPassword}
  

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

            <View style={styles.inputWrapper}>
              <Text style={styles.label}>Confirm Password</Text>

              <View style={styles.inputRow}>
                <TextInput
                  placeholder="Enter your password"
                  placeholderTextColor="#999"
                  secureTextEntry={!showPassword}
                  style={styles.input}
                  editable={otpVerified}
                  value={confirmPassword}
                    onChangeText={setConfirmPassword}

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
              style={styles.submitbtn}
              onPress={handleSubmit}
            >
              <Text style={styles.submitText}>Reset Password</Text>
            </TouchableOpacity> */}

              <TouchableOpacity
                    style={[
                      styles.submitbtn,
                      { backgroundColor: otpVerified ? "#000" : "#c8c0c0" }
                    ]}
                    onPress={handleSubmit}
                    disabled={!otpVerified}
                  >
                    <Text style={styles.submitText}>Reset Password</Text>
              </TouchableOpacity>


           <View style={{color:"black",fontWeight:"bold", marginTop:15}}>
            <TouchableOpacity onPress={()=>{
                navigation.navigate("Login");
            }}>
            <Text>Back To Login</Text>
            </TouchableOpacity>
           </View>


          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
}

export default ForgotPassword

const styles = StyleSheet.create({
  container:{
     flex:1,
     justifyContent:"center",
     alignItems:"center",
     paddingHorizontal:25,
     backgroundColor:"#fff"
  },
  title:{
     fontSize:26,
     fontWeight:"bold",
    marginBottom:15,
  },
  inputWrapper:{
    borderWidth:1,
    width:"100%",
    marginVertical:10,
    borderRadius:25,
    paddingHorizontal:20,
    paddingVertical:10
  },
  label:{
    color:"#777",
    position:"absolute",
    backgroundColor:"#fff",
    left:20,
    top:-10
  },
  input:{
    flex:1,
  },
  inputRow:{
    flexDirection:"row",
    alignItems:"center",
  },
  submitbtn:{
    backgroundColor:"#000",
    width:"100%",
    paddingVertical:15,
    alignItems:"center",
    borderRadius:25,
    marginTop:10,
  },
  submitText:{
    color:"white",
  },

  // forgot password
  otpRow: {
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
},

otpButton: {
  flex: 0.3,
  backgroundColor: "#4A55A2",
  height: 60,
  borderRadius: 30,
  alignItems: "center",
  justifyContent: "center",
  elevation: 3,
},

otpButtonText: {
  color: "white",
  fontWeight: "600",
  fontSize: 13,
},


})