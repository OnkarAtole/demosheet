import React, { useRef, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  Image,
  ActivityIndicator,
  SafeAreaView,
  StatusBar,
  Animated,
  Dimensions,
} from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as ImageManipulator from "expo-image-manipulator";

const { width: SW } = Dimensions.get("window");
const API_BASE_URL = "http://192.168.1.11:8000";

// ─────────────────────────────────────────────
// MAIN SCREEN — Camera + Capture + Evaluate
// ─────────────────────────────────────────────
export default function OMRScanner({ route, navigation }) {
  const { examId, totalPages = 1, examName = "OMR Scan" } = route?.params || {
    examId: 1,
    totalPages: 1,
    examName: "OMR Scan",
  };

  const cameraRef = useRef(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const flashAnim = useRef(new Animated.Value(0)).current;

  if (!permission) return <View style={styles.container} />;

  if (!permission.granted) {
    return (
      <SafeAreaView style={styles.permissionScreen}>
        <Text style={styles.permTitle}>Camera Required</Text>
        <Text style={styles.permSub}>
          We need camera access to scan OMR sheets.
        </Text>
        <TouchableOpacity style={styles.permBtn} onPress={requestPermission}>
          <Text style={styles.permBtnText}>Grant Permission</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  // If we have a result, show the result screen
  if (result) {
    return (
      <ResultScreen
        result={result}
        examName={examName}
        onRescan={() => {
          setResult(null);
          setImages([]);
        }}
      />
    );
  }

  // ── Capture ──────────────────────────────────
  const captureSheet = async () => {
    if (images.length >= Number(totalPages)) {
      Alert.alert("All pages captured", "Tap Evaluate to grade the sheet.");
      return;
    }
    try {
      // Flash animation
      Animated.sequence([
        Animated.timing(flashAnim, { toValue: 1, duration: 80, useNativeDriver: true }),
        Animated.timing(flashAnim, { toValue: 0, duration: 200, useNativeDriver: true }),
      ]).start();

      const photo = await cameraRef.current.takePictureAsync({ quality: 1 });

      const processed = await ImageManipulator.manipulateAsync(
        photo.uri,
        [{ resize: { width: 1400 } }],
        { compress: 0.92, format: ImageManipulator.SaveFormat.JPEG }
      );

      setImages((prev) => [...prev, processed]);
    } catch (err) {
      console.error(err);
      Alert.alert("Capture Error", "Failed to capture image. Try again.");
    }
  };

  // ── Evaluate ─────────────────────────────────
  const evaluateSheet = async () => {
    if (loading) return;
    if (images.length !== Number(totalPages)) {
      Alert.alert(
        "Incomplete",
        `Please capture all ${totalPages} page(s) before evaluating.\n\nCaptured: ${images.length}/${totalPages}`
      );
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      images.forEach((img, idx) => {
        formData.append("files", {
          uri: img.uri,
          name: `omr_page_${idx + 1}.jpg`,
          type: "image/jpeg",
        });
      });
      formData.append("exam_id", String(examId));

      const response = await fetch(`${API_BASE_URL}/api/v1/omr/scan-omr`, {
        method: "POST",
        body: formData,
        headers: { Accept: "application/json" },
      });

      const json = await response.json();

      if (!response.ok || json.status !== "success") {
        Alert.alert("Evaluation Failed", json.detail || json.message || "Server error");
        return;
      }

      setResult(json.data);
    } catch (error) {
      console.error("Fetch error:", error);
      Alert.alert("Connection Error", `Could not reach server.\n${API_BASE_URL}`);
    } finally {
      setLoading(false);
    }
  };

  // ── Retake last photo ─────────────────────────
  const retakeLast = () => setImages((prev) => prev.slice(0, -1));

  const allCaptured = images.length >= Number(totalPages);
  const progress = images.length / Number(totalPages);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" />

      {/* Camera */}
      <CameraView
        style={StyleSheet.absoluteFillObject}
        ref={cameraRef}
        ratio="4:3"
      />

      {/* Capture flash overlay */}
      <Animated.View
        style={[
          StyleSheet.absoluteFillObject,
          { backgroundColor: "#fff", opacity: flashAnim, pointerEvents: "none" },
        ]}
      />

      {/* Top bar */}
      <SafeAreaView style={styles.topBar}>
        <View style={styles.topContent}>
          <Text style={styles.examName} numberOfLines={1}>
            {examName}
          </Text>
          <View style={styles.pageCounter}>
            <Text style={styles.pageText}>
              {images.length} / {totalPages}
            </Text>
          </View>
        </View>

        {/* Progress bar */}
        <View style={styles.progressTrack}>
          <Animated.View style={[styles.progressFill, { width: `${progress * 100}%` }]} />
        </View>
      </SafeAreaView>

      {/* Scan frame overlay */}
      <View style={styles.frameContainer}>
        <View style={styles.frame}>
          {/* Corner accents */}
          <View style={[styles.corner, styles.cornerTL]} />
          <View style={[styles.corner, styles.cornerTR]} />
          <View style={[styles.corner, styles.cornerBL]} />
          <View style={[styles.corner, styles.cornerBR]} />
          {!allCaptured && (
            <Text style={styles.frameHint}>
              Align OMR sheet inside the frame
            </Text>
          )}
          {allCaptured && (
            <View style={styles.frameReady}>
              <Text style={styles.frameReadyIcon}>✓</Text>
              <Text style={styles.frameReadyText}>All pages captured</Text>
            </View>
          )}
        </View>
      </View>

      {/* Thumbnails */}
      {images.length > 0 && (
        <View style={styles.thumbRow}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {images.map((img, idx) => (
              <View key={idx} style={styles.thumbWrap}>
                <Image source={{ uri: img.uri }} style={styles.thumb} />
                <View style={styles.thumbBadge}>
                  <Text style={styles.thumbBadgeText}>{idx + 1}</Text>
                </View>
              </View>
            ))}
          </ScrollView>
          {images.length > 0 && (
            <TouchableOpacity style={styles.retakeBtn} onPress={retakeLast}>
              <Text style={styles.retakeBtnText}>↩ Retake</Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      {/* Bottom buttons */}
      <SafeAreaView style={styles.bottomBar}>
        <TouchableOpacity
          style={[styles.captureBtn, allCaptured && styles.captureBtnDone]}
          onPress={captureSheet}
          disabled={allCaptured}
        >
          <View style={styles.captureBtnInner} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.evalBtn, !allCaptured && styles.evalBtnDisabled]}
          onPress={evaluateSheet}
          disabled={!allCaptured || loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.evalBtnText}>Evaluate →</Text>
          )}
        </TouchableOpacity>
      </SafeAreaView>
    </View>
  );
}

// ─────────────────────────────────────────────
// RESULT SCREEN
// ─────────────────────────────────────────────
function ResultScreen({ result, examName, onRescan }) {
  const {
    roll_number,
    score,
    total,
    percentage,
    wrong_questions,
    unanswered_questions,
    detailed_results,
  } = result;

  const passed = percentage >= 40;
  const scoreColor = percentage >= 75 ? "#4ECDC4" : percentage >= 40 ? "#FFE66D" : "#FF6B6B";

  return (
    <SafeAreaView style={styles.resultContainer}>
      <StatusBar barStyle="light-content" />
      <ScrollView contentContainerStyle={styles.resultScroll} showsVerticalScrollIndicator={false}>

        {/* Header card */}
        <View style={styles.resultCard}>
          <Text style={styles.resultExamName}>{examName}</Text>
          <Text style={styles.resultRoll}>Roll No: {roll_number}</Text>

          <View style={styles.scoreCircle}>
            <Text style={[styles.scoreMain, { color: scoreColor }]}>{score}</Text>
            <Text style={styles.scoreTotal}>/{total}</Text>
          </View>

          <Text style={[styles.scorePercent, { color: scoreColor }]}>
            {percentage}%
          </Text>
          <Text style={[styles.passLabel, { color: passed ? "#4ECDC4" : "#FF6B6B" }]}>
            {passed ? "✓ PASSED" : "✗ FAILED"}
          </Text>

          {/* Stats row */}
          <View style={styles.statsRow}>
            <StatBox label="Correct" value={score} color="#4ECDC4" />
            <StatBox label="Wrong" value={wrong_questions?.length ?? 0} color="#FF6B6B" />
            <StatBox label="Skipped" value={unanswered_questions?.length ?? 0} color="#888" />
          </View>
        </View>

        {/* Detailed answer breakdown */}
        {detailed_results && (
          <View style={styles.detailCard}>
            <Text style={styles.detailTitle}>Answer Breakdown</Text>
            {Object.entries(detailed_results).map(([q, data]) => (
              <View key={q} style={styles.detailRow}>
                <Text style={styles.detailQ}>Q{q}</Text>
                <View style={styles.detailAnswers}>
                  <Text style={styles.detailLabel}>Yours: </Text>
                  <Text
                    style={[
                      styles.detailAnswer,
                      {
                        color:
                          data.result === "correct"
                            ? "#4ECDC4"
                            : data.result === "unanswered"
                            ? "#888"
                            : "#FF6B6B",
                      },
                    ]}
                  >
                    {data.student ?? "–"}
                  </Text>
                  {data.result !== "correct" && (
                    <>
                      <Text style={styles.detailLabel}>  Correct: </Text>
                      <Text style={[styles.detailAnswer, { color: "#4ECDC4" }]}>
                        {data.correct}
                      </Text>
                    </>
                  )}
                </View>
                <View
                  style={[
                    styles.detailDot,
                    {
                      backgroundColor:
                        data.result === "correct"
                          ? "#4ECDC4"
                          : data.result === "unanswered"
                          ? "#333"
                          : "#FF6B6B",
                    },
                  ]}
                />
              </View>
            ))}
          </View>
        )}

        <TouchableOpacity style={styles.rescanBtn} onPress={onRescan}>
          <Text style={styles.rescanBtnText}>Scan Another Sheet</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

function StatBox({ label, value, color }) {
  return (
    <View style={styles.statBox}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

// ─────────────────────────────────────────────
// STYLES
// ─────────────────────────────────────────────
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },

  // Permission
  permissionScreen: {
    flex: 1,
    backgroundColor: "#0F0F1A",
    justifyContent: "center",
    alignItems: "center",
    padding: 32,
  },
  permTitle: { color: "#F0F0FF", fontSize: 22, fontWeight: "800", marginBottom: 12 },
  permSub: { color: "#666", fontSize: 15, textAlign: "center", marginBottom: 32 },
  permBtn: {
    backgroundColor: "#FF6B35",
    paddingHorizontal: 28,
    paddingVertical: 14,
    borderRadius: 12,
  },
  permBtnText: { color: "#fff", fontWeight: "700", fontSize: 15 },

  // Top bar
  topBar: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 10,
    backgroundColor: "rgba(0,0,0,0.55)",
    paddingBottom: 8,
  },
  topContent: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 8,
  },
  examName: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "700",
    flex: 1,
    marginRight: 12,
  },
  pageCounter: {
    backgroundColor: "#FF6B35",
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 5,
  },
  pageText: { color: "#fff", fontWeight: "800", fontSize: 13 },
  progressTrack: {
    height: 3,
    backgroundColor: "rgba(255,255,255,0.15)",
    marginHorizontal: 20,
    borderRadius: 2,
  },
  progressFill: {
    height: 3,
    backgroundColor: "#FF6B35",
    borderRadius: 2,
  },

  // Frame overlay
  frameContainer: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: "center",
    alignItems: "center",
  },
  frame: {
    width: SW * 0.82,
    height: SW * 1.1,
    justifyContent: "center",
    alignItems: "center",
  },
  corner: {
    position: "absolute",
    width: 24,
    height: 24,
    borderColor: "#FF6B35",
    borderWidth: 3,
  },
  cornerTL: { top: 0, left: 0, borderRightWidth: 0, borderBottomWidth: 0, borderTopLeftRadius: 4 },
  cornerTR: { top: 0, right: 0, borderLeftWidth: 0, borderBottomWidth: 0, borderTopRightRadius: 4 },
  cornerBL: { bottom: 0, left: 0, borderRightWidth: 0, borderTopWidth: 0, borderBottomLeftRadius: 4 },
  cornerBR: { bottom: 0, right: 0, borderLeftWidth: 0, borderTopWidth: 0, borderBottomRightRadius: 4 },
  frameHint: {
    color: "rgba(255,255,255,0.6)",
    fontSize: 13,
    fontWeight: "500",
    textAlign: "center",
    backgroundColor: "rgba(0,0,0,0.45)",
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
  },
  frameReady: { alignItems: "center" },
  frameReadyIcon: { fontSize: 40, color: "#4ECDC4" },
  frameReadyText: {
    color: "#4ECDC4",
    fontWeight: "700",
    fontSize: 15,
    marginTop: 6,
  },

  // Thumbnails
  thumbRow: {
    position: "absolute",
    bottom: 130,
    left: 0,
    right: 0,
    paddingHorizontal: 16,
    flexDirection: "row",
    alignItems: "center",
  },
  thumbWrap: { marginRight: 10, position: "relative" },
  thumb: {
    width: 70,
    height: 95,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: "#FF6B35",
  },
  thumbBadge: {
    position: "absolute",
    top: -6,
    right: -6,
    backgroundColor: "#FF6B35",
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: "center",
    alignItems: "center",
  },
  thumbBadgeText: { color: "#fff", fontSize: 11, fontWeight: "800" },
  retakeBtn: {
    backgroundColor: "rgba(0,0,0,0.65)",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#FF6B35",
    marginLeft: 10,
  },
  retakeBtnText: { color: "#FF6B35", fontWeight: "700", fontSize: 13 },

  // Bottom buttons
  bottomBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    paddingBottom: 24,
    paddingTop: 16,
    backgroundColor: "rgba(0,0,0,0.55)",
  },
  captureBtn: {
    width: 72,
    height: 72,
    borderRadius: 36,
    borderWidth: 4,
    borderColor: "#fff",
    justifyContent: "center",
    alignItems: "center",
  },
  captureBtnDone: { borderColor: "#444" },
  captureBtnInner: {
    width: 54,
    height: 54,
    borderRadius: 27,
    backgroundColor: "#fff",
  },
  evalBtn: {
    backgroundColor: "#FF6B35",
    paddingHorizontal: 28,
    paddingVertical: 16,
    borderRadius: 14,
    minWidth: 130,
    alignItems: "center",
  },
  evalBtnDisabled: { backgroundColor: "#333" },
  evalBtnText: { color: "#fff", fontWeight: "800", fontSize: 16 },

  // Result screen
  resultContainer: { flex: 1, backgroundColor: "#0F0F1A" },
  resultScroll: { padding: 20, paddingBottom: 40 },
  resultCard: {
    backgroundColor: "#1A1A2E",
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
    marginBottom: 16,
  },
  resultExamName: {
    color: "#F0F0FF",
    fontSize: 18,
    fontWeight: "800",
    marginBottom: 4,
    textAlign: "center",
  },
  resultRoll: { color: "#666", fontSize: 14, marginBottom: 24 },
  scoreCircle: {
    flexDirection: "row",
    alignItems: "flex-end",
    marginBottom: 8,
  },
  scoreMain: { fontSize: 72, fontWeight: "900", lineHeight: 80 },
  scoreTotal: { fontSize: 28, color: "#555", marginBottom: 10 },
  scorePercent: { fontSize: 28, fontWeight: "800", marginBottom: 6 },
  passLabel: { fontSize: 16, fontWeight: "700", letterSpacing: 2, marginBottom: 24 },
  statsRow: {
    flexDirection: "row",
    gap: 20,
    borderTopWidth: 1,
    borderTopColor: "#2A2A3E",
    paddingTop: 20,
    width: "100%",
    justifyContent: "center",
  },
  statBox: { alignItems: "center", minWidth: 70 },
  statValue: { fontSize: 26, fontWeight: "800" },
  statLabel: { color: "#666", fontSize: 12, fontWeight: "600", marginTop: 2 },

  detailCard: {
    backgroundColor: "#1A1A2E",
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
  },
  detailTitle: {
    color: "#F0F0FF",
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 16,
  },
  detailRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#2A2A3E",
  },
  detailQ: { color: "#888", fontSize: 13, fontWeight: "700", width: 32 },
  detailAnswers: { flex: 1, flexDirection: "row", alignItems: "center" },
  detailLabel: { color: "#555", fontSize: 13 },
  detailAnswer: { fontSize: 14, fontWeight: "800" },
  detailDot: { width: 10, height: 10, borderRadius: 5 },

  rescanBtn: {
    backgroundColor: "#FF6B35",
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: "center",
  },
  rescanBtnText: { color: "#fff", fontWeight: "800", fontSize: 16 },
});
