import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Platform,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import React, { useEffect, useState, useCallback } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import MaterialIcons from "react-native-vector-icons/MaterialIcons";
import AntDesign from "react-native-vector-icons/AntDesign";
import EvilIcons from "react-native-vector-icons/EvilIcons";
import { logout } from "../../../services/authService";
import { getCurrentUser } from "../../../services/userService";
const Setting = ({ navigation }) => {
  // const username = "Onkar";
  const role="Teacher"
  const [user, setUser] = useState(null);
  // const route = useRoute();

  useFocusEffect(
  useCallback(() => {
    fetchUser();
  }, [])
);

  const fetchUser = async () => {
    try {
      const data = await getCurrentUser();
      // console.log("USER DATA:", data); 
      setUser(data);
    } catch (error) {
      console.log("Error fetching user:", error);
    }
  };
const handleEdit = () => {
  navigation.navigate("EditProfile");
};
  const handlecontact = () => {
    navigation.navigate("ContactScreen");
  };
  const handleSetting = () => {};
  const handleShare = () => {};
  const handleLogout = async () => {
    await logout();
    navigation.replace("Login");
  };
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{ flexGrow: 1, backgroundColor: "white" }}
      >
        <View style={styles.container}>
          <View style={styles.profile}>
            <View style={styles.logo}>
              <Text style={styles.logoText}>
                {user?.name?.charAt(0).toUpperCase()}
              </Text>
            </View>

            <View>
              <Text style={styles.username}>{user?.name || "Loading..."}</Text>
              <Text
                style={[styles.username, { fontSize: 12, fontWeight: "10" }]}
              >
                {role}
              </Text>
            </View>

            <View style={styles.editbtn}>
              <TouchableOpacity onPress={handleEdit}>
                <MaterialIcons name="edit" size={25} />
              </TouchableOpacity>
            </View>
          </View>

          <View style={{ flex: 1, marginTop: 15 }}>
            <View style={styles.setting}>
              <View style={styles.settingbtn}>
                <View
                  style={{
                    backgroundColor: "#e1c7c7",
                    width: 45,
                    height: 45,
                    alignItems: "center",
                    justifyContent: "center",
                    borderRadius: 50,
                  }}
                >
                  <MaterialIcons name="contact-page" size={30} />
                </View>
                <TouchableOpacity
                  onPress={handlecontact}
                  style={{ alignItems: "center", justifyContent: "center" }}
                >
                  <Text style={styles.btnText}>Contact</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.settingbtn}>
                <View
                  style={{
                    backgroundColor: "#e1c7c7",
                    width: 45,
                    height: 45,
                    alignItems: "center",
                    justifyContent: "center",
                    borderRadius: 50,
                  }}
                >
                  <AntDesign name="setting" size={30} />
                </View>
                <TouchableOpacity
                  onPress={handleSetting}
                  style={{ alignItems: "center", justifyContent: "center" }}
                >
                  <Text style={styles.btnText}>Setting</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.settingbtn}>
                <View
                  style={{
                    backgroundColor: "#e1c7c7",
                    width: 45,
                    height: 45,
                    alignItems: "center",
                    justifyContent: "center",
                    borderRadius: 50,
                  }}
                >
                  <EvilIcons
                    name={
                      Platform.OS === "ios" ? "share-apple" : "share-google"
                    }
                    size={28}
                    color="black"
                  />
                </View>
                <TouchableOpacity
                  onPress={handleShare}
                  style={{ alignItems: "center", justifyContent: "center" }}
                >
                  <Text style={styles.btnText}>Share</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.settingbtn}>
                <View
                  style={{
                    backgroundColor: "#e1c7c7",
                    width: 45,
                    height: 45,
                    alignItems: "center",
                    justifyContent: "center",
                    borderRadius: 50,
                  }}
                >
                  <MaterialIcons name="logout" size={30} />
                </View>
                <TouchableOpacity
                  onPress={handleLogout}
                  style={{ alignItems: "center", justifyContent: "center" }}
                >
                  <Text style={styles.btnText}>Sign out</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

export default Setting;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    paddingHorizontal: 10,
    marginTop: 30,
  },
  profile: {
    borderWidth: 1,
    borderColor: "black",
    borderRadius: 5,
    paddingVertical: 15,
    paddingHorizontal: 10,
    flexDirection: "row",
  },
  logo: {
    height: 50,
    width: 50,
    backgroundColor: "#e1c7c7",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 50,
  },
  logoText: {
    fontSize: 30,
    fontWeight: "Bold",
  },
  username: {
    paddingHorizontal: 20,
    fontWeight: "bold",
    fontSize: 20,
  },
  editbtn: {
    position: "absolute",
    right: 20,
    paddingTop: 10,
  },
  settingbtn: {
    paddingVertical: 15,
    flexDirection: "row",
    gap: 15,
  },
  btnText: {
    fontWeight: "bold",
    fontSize: 17,
  },
});
