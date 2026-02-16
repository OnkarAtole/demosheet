import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import ExamsScreen from "../screens/Tabs/Exams/ExamsScreen";
import ExamDetails from "../screens/Tabs/Exams/ExamDetails";
import AnswerKey from "../screens/Tabs/Exams/AnswerKey";
import AddExam from "../screens/Tabs/Exams/AddExam";
const Stack = createNativeStackNavigator();

export default function ExamsStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ExamsScreen" component={ExamsScreen} />
      <Stack.Screen name="ExamDetails" component={ExamDetails} />
      <Stack.Screen name="AnswerKey" component={AnswerKey} />
      <Stack.Screen name="AddExam" component={AddExam} />
    </Stack.Navigator>
  );
}
