import React, { useRef, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  Image,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as ImageManipulator from "expo-image-manipulator";

export default function OMRScanner({ route }) {
  const { examId, totalPages } = route.params;

  const cameraRef = useRef(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);

  if (!permission) return <View />;

  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text>No camera access</Text>
        <TouchableOpacity onPress={requestPermission}>
          <Text>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // ================= CAPTURE =================
  const captureSheet = async () => {
    if (images.length >= Number(totalPages)) {
      Alert.alert("All pages captured");
      return;
    }

    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.7,
      });

      // 🔥 IMPORTANT: smaller image = no network crash
      const resized = await ImageManipulator.manipulateAsync(
        photo.uri,
        [{ resize: { width: 700 } }],
        {
          compress: 0.6,
          format: ImageManipulator.SaveFormat.JPEG,
        }
      );

      setImages((prev) => [...prev, resized]);
    } catch (err) {
      console.log(err);
      Alert.alert("Error capturing image");
    }
  };

  // ================= EVALUATE =================
  const evaluateSheet = async () => {
    if (loading) return;

    if (images.length !== Number(totalPages)) {
      Alert.alert(`Capture all ${totalPages} pages first`);
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();

      images.forEach((img, index) => {
        formData.append("files", {
          uri: img.uri,
          name: `page_${index}.jpg`,
          type: "image/jpeg",
        });
      });

      formData.append("exam_id", examId);

      // Use configurable API base URL
      const API_BASE_URL = "http://192.168.43.172:8000";
      const API_URL = `${API_BASE_URL}/api/v1/omr/scan-omr`;

      console.log("Sending request to:", API_URL);
      console.log("Exam ID:", examId);
      console.log("Images count:", images.length);

      // 🔥 Timeout protection - increased to 60 seconds for image processing
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
        headers: {
          "Accept": "application/json",
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      console.log("Response status:", response.status);

      const result = await response.json();
      console.log("Response data:", result);

      if (!response.ok || result.status !== "success") {
        console.log("Server Error:", result);
        Alert.alert(
          "Evaluation Failed",
          result.message || "Unknown error occurred"
        );
        return;
      }

      console.log("Extracted Answers:", result.data.extracted_answers);

      Alert.alert(
        "Success 🎉",
        `Score: ${result.data.score} / ${result.data.total}
Set: ${result.data.set}
Roll: ${result.data.roll_number}`
      );

      setImages([]);
    } catch (error) {
      console.log("FETCH ERROR:", error);
      
      if (error.name === "AbortError") {
        Alert.alert("Timeout", "Request took too long. Please try again.");
      } else if (error.message && error.message.includes("Network request failed")) {
        Alert.alert("Network Error", "Unable to connect to server. Please check your network.");
      } else {
        Alert.alert("Error", "An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <Text style={styles.pageText}>
          {images.length} / {totalPages}
        </Text>
      </View>

      <CameraView
        style={StyleSheet.absoluteFillObject}
        ref={cameraRef}
        ratio="4:3"
      />

      <View style={styles.overlayContainer}>
        <View style={styles.overlayBox} />
      </View>

      <View style={styles.thumbnailContainer}>
        <ScrollView horizontal>
          {images.map((img, index) => (
            <Image
              key={index}
              source={{ uri: img.uri }}
              style={styles.thumbnail}
            />
          ))}
        </ScrollView>
      </View>

      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.captureBtn} onPress={captureSheet}>
          <Text style={styles.btnText}>Capture</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.evaluateBtn}
          onPress={evaluateSheet}
          disabled={loading}
        >
          <Text style={styles.btnText}>
            {loading ? "Processing..." : "Evaluate"}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  topBar: {
    position: "absolute",
    top: 50,
    alignSelf: "center",
    zIndex: 10,
  },
  pageText: {
    fontSize: 18,
    color: "#fff",
    fontWeight: "bold",
    backgroundColor: "rgba(0,0,0,0.6)",
    paddingHorizontal: 15,
    paddingVertical: 5,
    borderRadius: 20,
  },
  overlayContainer: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
  },
  overlayBox: {
    width: "85%",
    height: "65%",
    borderWidth: 3,
    borderColor: "lime",
    borderRadius: 12,
  },
  thumbnailContainer: {
    position: "absolute",
    bottom: 150,
    width: "100%",
    paddingHorizontal: 10,
  },
  thumbnail: {
    width: 80,
    height: 110,
    marginRight: 10,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: "#fff",
  },
  buttonRow: {
    position: "absolute",
    bottom: 40,
    width: "100%",
    flexDirection: "row",
    justifyContent: "space-evenly",
  },
  captureBtn: {
    backgroundColor: "#000",
    paddingHorizontal: 25,
    paddingVertical: 15,
    borderRadius: 30,a
  },
  evaluateBtn: {
    backgroundColor: "green",
    paddingHorizontal: 25,
    paddingVertical: 15,
    borderRadius: 30,
  },
  btnText: {
    color: "#fff",
    fontWeight: "bold",
  },
});