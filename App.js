import { createAppContainer } from "react-navigation";
import { createStackNavigator } from "react-navigation-stack";
import HomeScreen from "./src/screens/HomeScreen";
import LoginScreen from "./src/screens/LoginScreen";
const navigator = createStackNavigator(
  // {
  //   Home: HomeScreen,
  //   Login:LoginScreen
  // },
    {
    Home: {
      screen: HomeScreen,
      navigationOptions: {
        headerShown: false,   // 👈 hide header here
      },
    },
    Login: {
      screen: LoginScreen,
      navigationOptions: {
        headerShown: false,   // 👈 hide header here
      },
    },
  },
  {
    initialRouteName: "Login",
    defaultNavigationOptions: {
      title: "App",
    },
  }
);

export default createAppContainer(navigator);
