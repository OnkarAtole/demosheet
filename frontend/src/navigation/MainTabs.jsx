import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
// import ClassScreen from '../screens/Tabs/Class/ClassScreen'
// import ExamsScreen from '../screens/Tabs/Exams/ExamsScreen'
import SettingScreen from '../screens/Tabs/Setting/SettingScreen'
import SimpleLineIcons from 'react-native-vector-icons/SimpleLineIcons';
import MaterialIcons from 'react-native-vector-icons/MaterialIcons'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import ExamsStack from './ExamsStack';
import ClassStack from './ClassStack'
import SettingStack from './SettingStack';
import { NavigationContainer } from '@react-navigation/native'
const Tab = createBottomTabNavigator();
const MainTabs = () => {
  return (
    
    <Tab.Navigator initialRouteName='Exams' screenOptions={{
        tabBarActiveTintColor:"#1e65d0",
        tabBarInactiveTintColor:"black",
        headerShown:false,
    }}>
        <Tab.Screen name="Exams" component={ExamsStack} options={{tabBarIcon:({color},)=> 
            <SimpleLineIcons name="notebook" size={30} color={color}/>}}
        />  
        <Tab.Screen name="Classes" component={ClassStack} options={{tabBarIcon:({color})=>
            <MaterialIcons name="groups" size={30} color={color}/>}}
        />
        <Tab.Screen name="more" component={SettingStack} options={{tabBarIcon:({color})=>
            <MaterialIcons name="more-horiz" size={30} color={color}/>}}
        
        />
    </Tab.Navigator>
    
  )
}

export default MainTabs

const styles = StyleSheet.create({})