import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import SettingScreen from '../screens/Tabs/Setting/SettingScreen'
import ContactScreen from "../screens/Tabs/Setting/ContactScreen";


const Stack = createNativeStackNavigator();

export default function SettingStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="SettingScreen" component={SettingScreen} />
      <Stack.Screen name="ContactScreen" component={ContactScreen} />
   
    </Stack.Navigator>
  );
}
