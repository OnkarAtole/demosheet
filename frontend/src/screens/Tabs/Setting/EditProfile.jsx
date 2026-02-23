import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView,KeyboardAvoidingView,Platform} from "react-native";
import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
// import { useRoute } from "@react-navigation/native";
import {Ionicons} from "@expo/vector-icons"
import { useEffect } from "react";
import { getCurrentUser, updateProfile } from "../../../services/userService";

const EditProfile = ({navigation}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState("");
const [email, setEmail] = useState("");
const [password, setPassword] = useState("");
const [confirmPassword, setConfirmPassword] = useState("");
const [loading, setLoading] = useState(false);
  // const route = useRoute();
  // const { username } = route.username; // 👈 received class
  useEffect(() => {
  fetchUser();
}, []);

const fetchUser = async () => {
  try {
    const data = await getCurrentUser();
    setName(data.name);
    setEmail(data.email);
  } catch (error) {
    console.log("Fetch user error:", error);
  }
};

const handleupdate = async () => {
  if (password || confirmPassword) {
  if (!password || !confirmPassword) {
    alert("Please fill both password fields");
    return;
  }

  if (password !== confirmPassword) {
    alert("Passwords do not match");
    return;
  }

  if (password.length < 6) {
    alert("Password must be at least 6 characters");
    return;
  }
}
  try {
    setLoading(true);

    await updateProfile({
      name,
      email,
      password: password || undefined,
    });

    alert("Profile updated successfully");
    navigation.goBack();

  } catch (error) {
    console.log("Update error:", error);
    alert("Update failed");
  } finally {
    setLoading(false);
  }
};

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
       <KeyboardAvoidingView
              behavior={Platform.OS == "ios" ? "padding" : "height"}
              style={{ flex: 1 }}
            >
        <ScrollView 
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{flexGrow: 1,paddingBottom: 50, }}
        >
      <View style={styles.container}>
        <View style={styles.header}>
        <Text style={styles.title}>Profile</Text>
       
       </View>

       <View style={styles.main}>
         <View style={styles.inputWrapper}>
            <Text style={styles.label}>Name</Text>
            <TextInput
            value={name}
            onChangeText={setName}
            placeholder="Enter a student name"
            placeholderTextColor="#999"
            style={styles.input}
            />
         </View>
         <View style={styles.inputWrapper}>
            <Text style={styles.label}>Email</Text>
            <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder="Enter a your email"
            placeholderTextColor="#999"
            style={styles.input}
            />
         </View>
         
         <View style={styles.inputWrapper1}>
              <Text style={styles.label}>New Password</Text>

              <View style={styles.inputRow}>
                <TextInput
                value={password}
                onChangeText={setPassword}
                  placeholder="Enter your password"
                  placeholderTextColor="#999"
                  secureTextEntry={!showPassword}
                  style={styles.input}
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

            <View style={styles.inputWrapper1}>
              <Text style={styles.label}>Confirm Password</Text>

              <View style={styles.inputRow}>
                <TextInput
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                  placeholder="Enter your password"
                  placeholderTextColor="#999"
                  secureTextEntry={!showPassword}
                  style={styles.input}
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

         <TouchableOpacity style={styles.addbtn}
         onPress={handleupdate}>
         <Text style={styles.addbtnText}>Update</Text>
         </TouchableOpacity>
         

       </View>
      </View>
      </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default EditProfile;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal:20,
    marginTop:10,
  },
  title:{
    color:"#1f3c88",
    fontWeight:"bold",
    fontSize:20,
  },
  header:{
    marginTop:10,
    justifyContent:"space-between",
    flexDirection:"row"
  },
  main:{
      justifyContent:"center",
      alignItems:"center",
      marginTop:30
  },
  inputWrapper:{
     borderWidth:1,
     borderRadius:25,
     width:"100%",
    flexDirection:"row",
     paddingHorizontal:20,
     paddingTop:12,
     paddingBottom:8,
      marginTop:20,
      
  },
  input:{
   flex:1,
   height:40,
   fontSize:16
  },
  label:{
     backgroundColor:"white",
     position:"absolute",
     left:20,
     top:-10,
     paddingHorizontal:10,
     color:"#777"
  },
   addbtn:{
    marginTop:30,
    backgroundColor:"#000",
    paddingHorizontal:50,
    paddingVertical:12,
    borderRadius:25
   },
    addbtnText:{
    color:"white",
    fontWeight:"bold",

   },
   inputRow:{
    flexDirection:"row",
    alignItems:"center",
   
   },
   inputWrapper1:{
    borderWidth:1,
    width:"100%",
    marginVertical:10,
    borderRadius:25,
    paddingHorizontal:20,
    paddingVertical:12,
    marginTop:20
  },

});
