import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import ClassScreen from "../screens/Tabs/Class/ClassScreen";

const Stack = createNativeStackNavigator();

export default function ClassStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ClassScreen" component={ClassScreen} />
     
    </Stack.Navigator>
  );
}
