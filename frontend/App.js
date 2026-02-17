import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import HomeScreen from "./src/screens/HomeScreen";
import LoginScreen from "./src/screens/Auth/LoginScreen";
import RegisterScreen from "./src/screens/Auth/RegisterScreen";
import ForgotPasswordScreen from "./src/screens/Auth/ForgotPasswordScreen";
import MainTabs from "./src/navigation/MainTabs";
const Stack = createNativeStackNavigator();
import { useEffect } from "react";

export default function App() {
  useEffect(() => {
   const checkLogin = async () => {
      const token = await AsyncStorage.getItem("token");

      if (token) {
         navigation.replace("MainTabs");
      } else {
         navigation.replace("Login");
      }
   };

   checkLogin();
}, []);

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Register" component={RegisterScreen}/>
        <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen}/>
        <Stack.Screen name="MainTabs" component={MainTabs}/>
      </Stack.Navigator>
    </NavigationContainer>
  );
}
