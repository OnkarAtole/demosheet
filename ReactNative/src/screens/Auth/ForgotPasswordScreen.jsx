import { StyleSheet, Text, View,KeyboardAvoidingView,Platform,ScrollView,TextInput,TouchableOpacity,Image} from 'react-native'
import {React,useState} from 'react'
import { SafeAreaView } from 'react-native-safe-area-context'
import {Ionicons} from "@expo/vector-icons"

const ForgotPassword = ({navigation}) => {
  const [showPassword,setShowPassword]=useState(false)
  const handleSubmit=()=>{

  }
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
              />
            </View>
            <View style={styles.inputWrapper}>
              <Text style={styles.label}>OTP</Text>
              <TextInput
                placeholder="Enter Your OTP"
                placeholderTextColor="#999"
                style={styles.input}
              />
            </View>
           
            <View style={styles.inputWrapper}>
              <Text style={styles.label}>New Password</Text>

              <View style={styles.inputRow}>
                <TextInput
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

            <View style={styles.inputWrapper}>
              <Text style={styles.label}>Confirm Password</Text>

              <View style={styles.inputRow}>
                <TextInput
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

            <TouchableOpacity
              style={styles.submitbtn}
              onPress={handleSubmit}
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

})