import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView,KeyboardAvoidingView,Platform} from "react-native";
import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRoute } from "@react-navigation/native";
import MaterialIcons from 'react-native-vector-icons/MaterialIcons';
import AsyncStorage from "@react-native-async-storage/async-storage";
import { createStudent } from "../../../services/studentService";


const AddStudentScreen = ({navigation}) => {

  const route = useRoute();
  const { classId } = route.params; // 👈 received class

  const [studentName, setStudentName] = useState("");

  const [rollNo, setRollNo] = useState("");
  const [email, setEmail] = useState("");
  const handleSaveStudent = () => {
    // console.log("Student:", studentName);
    // console.log("Class:", classItem.class);
  };

  const handleBulkAdd = () => {



  navigation.navigate("BulkStudentUpload", {
    classId: classId,   // 👈 pass selected class
  });
};

const handleAdd = async () => {
  if (!studentName || !rollNo || !email) {
    alert("Please fill all fields");
    return;
  }

if (isNaN(parseInt(rollNo))) {
  alert("Roll No must be a number");
  return;
}

// console.log("Sending Data →", {
//     name: studentName,
//     roll_no: parseInt(rollNo),
//     email: email,
//     class_id: parseInt(classId),
//   });
  try {
    const token = await AsyncStorage.getItem("token");

    await createStudent(
      {
        name: studentName,
        roll_no: parseInt(rollNo),
        email: email,
        class_id: parseInt(classId),
      },
      token
    );

    // Clear inputs after success
    setStudentName("");
    setRollNo("");
    setEmail("");

    navigation.goBack();

  }catch (error) {
  const message = error.response?.data?.detail;

  if (message === "Email already exists") {
    alert("This email is already registered for another student.");
  } else {
    alert("Something went wrong. Please try again.");
  }

  console.log("FULL ERROR:", error.response?.data);
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
        <Text style={styles.title}>Add Student</Text>
        <TouchableOpacity onPress={handleBulkAdd}>
          <MaterialIcons name="group-add" size={27} color={"#1f3c88"}/>
        </TouchableOpacity>
       </View>

       <View style={styles.main}>
         <View style={styles.inputWrapper}>
            <Text style={styles.label}>Name</Text>
            <TextInput
            placeholder="Enter a student name"
            placeholderTextColor="#999"
            value={studentName}
            onChangeText={setStudentName}
            style={styles.input}
            />
         </View>
         <View style={styles.inputWrapper}>
            <Text style={styles.label}>Roll NO</Text>
            <TextInput
            placeholder="Enter a student Roll NO"
            placeholderTextColor="#999"
            value={rollNo}
            onChangeText={setRollNo}
            keyboardType="numeric"
            style={styles.input}
            />
         </View>
         <View style={styles.inputWrapper}>
            <Text style={styles.label}>Email</Text>
            <TextInput
            placeholder="Enter a student Email"
            placeholderTextColor="#999"
            value={email}
            onChangeText={setEmail}
            style={styles.input}
            />
         </View>
         <TouchableOpacity style={styles.addbtn}
         onPress={handleAdd}>
         <Text style={styles.addbtnText}>Add</Text>
         </TouchableOpacity>
         

       </View>
      </View>
      </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default AddStudentScreen;

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
      marginTop:20
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

   }
});
