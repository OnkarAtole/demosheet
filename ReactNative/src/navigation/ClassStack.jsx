import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import ClassScreen from "../screens/Tabs/Class/ClassScreen";
import StudentDetailScreen from "../screens/Tabs/Class/StudentDetailScreen";
import AddStudentScreen from "../screens/Tabs/Class/AddStudentScreen";
import BulkStudentUpload from "../screens/Tabs/Class/BulkStudentUpload" 
const Stack = createNativeStackNavigator();

export default function ClassStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ClassScreen" component={ClassScreen} />
      <Stack.Screen name="StudentDetail" component={StudentDetailScreen}/>
      <Stack.Screen name="AddStudent" component={AddStudentScreen}/>
      <Stack.Screen name="BulkStudentUpload" component={BulkStudentUpload}/>
    </Stack.Navigator>
  );
}
