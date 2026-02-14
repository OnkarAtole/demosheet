import React from "react";
import { Text, StyleSheet, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

const HomeScreen = () => {
  return (
    <SafeAreaView
      style={{
        flex: 1,
      }}
    >
      <ScrollView style={{flex:1}}
      showsVerticalScrollIndicator={false}
      keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.text}>HomeScreen</Text>
        <Text style={styles.text}>HomeScreen</Text>
        
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  text: {
    fontSize: 30,
  },
});

export default HomeScreen;
