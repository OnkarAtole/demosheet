import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView,KeyboardAvoidingView,Platform} from "react-native";
import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRoute } from "@react-navigation/native";
import MaterialIcons from 'react-native-vector-icons/MaterialIcons';
const AddStudentScreen = ({navigation}) => {

  const route = useRoute();
  const { classItem } = route.params; // 👈 received class

  const [studentName, setStudentName] = useState("");

  const handleSaveStudent = () => {
    console.log("Student:", studentName);
    console.log("Class:", classItem.class);
  };

  const handleBulkAdd = () => {
  navigation.navigate("BulkStudentUpload", {
    classItem: classItem,   // 👈 pass selected class
  });
};

  const handleAdd=()=>{

  }
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
            style={styles.input}
            />
         </View>
         <View style={styles.inputWrapper}>
            <Text style={styles.label}>Roll NO</Text>
            <TextInput
            placeholder="Enter a student Roll NO"
            placeholderTextColor="#999"
            style={styles.input}
            />
         </View>
         <View style={styles.inputWrapper}>
            <Text style={styles.label}>Email</Text>
            <TextInput
            placeholder="Enter a student Email"
            placeholderTextColor="#999"
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
