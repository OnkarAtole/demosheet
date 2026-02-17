import {
  KeyboardAvoidingView,
 
  StyleSheet,
  Text,
  View,
  Platform,
  TextInput,FlatList
} from 'react-native'
import { Dropdown } from 'react-native-element-dropdown'
import React from 'react'
import { SafeAreaView } from 'react-native-safe-area-context'

const AddExam = () => {

  const [rollDigits, setRollDigits] = React.useState(1)
  const [examset, setExamSet] = React.useState(1)

  const [subjectCount, setSubjectCount] = React.useState(null)
  const [subjects, setSubjects] = React.useState([])

  const [selectedClass, setSelectedClass] = React.useState(null)
  const [questionCount, setQuestionCount] = React.useState("")



  const subjectOptions = Array.from({ length: 10 }, (_, i) => ({
    label: `${i + 1}`,
    value: i + 1,
  }))

  
  const handleSubjectCountChange = (value) => {
    setSubjectCount(value)

    const newSubjects = Array.from({ length: value }, () => ({
      name: "",
       questionCount: "",
    
    }))

    setSubjects(newSubjects)
  }


//   dummy classes for dropdown
const classOptions = [
  { label: "FY BCA", value: "fybca" },
  { label: "SY BCA", value: "sybca" },
  { label: "TY BCA", value: "tybca" }
]


return (
  <SafeAreaView style={{ flex: 1 }}>
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={{ flex: 1 }}
    >

      <FlatList
        data={subjects}
        keyExtractor={(_, index) => index.toString()}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}

        ListHeaderComponent={
          <View style={styles.container}>

            <Text style={styles.title}>Add Exam</Text>

            {/* Exam Name */}
            <View style={styles.inputWrapper}>
              <Text style={styles.label}>Exam Name</Text>
              <TextInput
                placeholder="Exam Name"
                placeholderTextColor="#999"
                style={styles.input}
              />
            </View>

            {/* Class Dropdown */}
            <View style={styles.inputWrapper}>
              <Text style={styles.label}>Class</Text>
              <Dropdown
                style={styles.dropdown}
                data={classOptions}
                labelField="label"
                valueField="value"
                placeholder="Select class"
                value={selectedClass}
                onChange={item => setSelectedClass(item.value)}
              />
            </View>

            <Text
              style={styles.addClassText}
              onPress={() => console.log("Navigate to Add Class")}
            >
              + Add Class
            </Text>

            {/* Roll Number Counter */}
            <View style={styles.counterRow}>
              <Text style={styles.counterLabel}>Roll Number Digits</Text>
              <View style={styles.counterControls}>
                <Text
                  style={styles.counterBtn}
                  onPress={() => rollDigits > 1 && setRollDigits(rollDigits - 1)}
                >−</Text>
                <Text style={styles.counterValue}>{rollDigits}</Text>
                <Text
                  style={styles.counterBtn}
                  onPress={() => rollDigits < 9 && setRollDigits(rollDigits + 1)}
                >+</Text>
              </View>
            </View>

            {/* Exam Set Counter */}
            <View style={styles.counterRow}>
              <Text style={styles.counterLabel}>Exam Set</Text>
              <View style={styles.counterControls}>
                <Text
                  style={styles.counterBtn}
                  onPress={() => examset > 1 && setExamSet(examset - 1)}
                >−</Text>
                <Text style={styles.counterValue}>{examset}</Text>
                <Text
                  style={styles.counterBtn}
                  onPress={() => examset < 4 && setExamSet(examset + 1)}
                >+</Text>
              </View>
            </View>

            {/* Number of Subjects */}
            <View style={{ width: "100%", marginVertical: 12 }}>
              <Text style={{ fontWeight: "600", marginBottom: 6 }}>
                Number of Subjects
              </Text>
              <Dropdown
                style={styles.dropdown}
                data={subjectOptions}
                labelField="label"
                valueField="value"
                placeholder="Select subjects"
                value={subjectCount}
                onChange={item => handleSubjectCountChange(item.value)}
              />
            </View>

            {/* Table Header */}
            {subjects.length > 0 && (
              <View style={styles.tableContainer}>
                <View style={styles.tableHeader}>
                  <Text style={styles.headerSr}>Sr No.</Text>
                  <Text style={styles.headerSubject}>Subject</Text>
                  <Text style={styles.headerQuestion}>No. Of Questions</Text>
                </View>
              </View>
            )}

          </View>
        }

        renderItem={({ item, index }) => (
          subjects.length > 0 && (
            <View style={[styles.tableRow, { paddingHorizontal: 20 }]}>
              <Text style={styles.srNo}>{index + 1}</Text>

              <TextInput
                style={styles.subjectInput}
                placeholder="Subject name"
                value={item.name}
                onChangeText={(text) => {
                  const updated = [...subjects]
                  updated[index].name = text
                  setSubjects(updated)
                }}
              />

              <TextInput
                style={styles.questionInput}
                placeholder="0"
                keyboardType="number-pad"
                value={item.questionCount}
                onChangeText={(text) => {
                  const numeric = text.replace(/[^0-9]/g, "")
                  const updated = [...subjects]
                  updated[index].questionCount = numeric
                  setSubjects(updated)
                }}
              />
            </View>
          )
        )}

        ListFooterComponent={
          <View style={[styles.submitBtnWrapper, { paddingHorizontal: 20 }]}>
            <Text
              style={styles.submitBtn}
              onPress={() => console.log("Submit Exam")}
            >
              Create Exam
            </Text>
          </View>
        }
      />

    </KeyboardAvoidingView>
  </SafeAreaView>
)}

export default AddExam


const styles = StyleSheet.create({

   container: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 20,
    marginTop: 10,
  },

  title:{
     fontSize:23,
     fontWeight:"bold",
    marginBottom:15,
    color:"#1f3c88"
  },
// for name input

inputWrapper: {
  width: "100%",
  marginVertical: 12
},

label: {
  fontSize: 14,
  fontWeight: "600",
  marginBottom: 6,
  color: "#333"
},

input: {
  height: 50,
  borderWidth: 1,
  borderColor: "#ccc",
  borderRadius: 8,
  paddingHorizontal: 12,
  fontSize: 16,
  backgroundColor: "#fff"
},


  inputRow: {
    flexDirection: "row",
    alignItems: "center",
  },

counterRow: {
  width: "100%",
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  marginVertical: 10
},

counterLabel: {
  fontSize: 14,
  fontWeight: "600",
  color: "#333"
},

counterControls: {
  flexDirection: "row",
  alignItems: "center"
},

counterBtn: {
  backgroundColor: "#000",
  color: "#fff",
  width: 55,
  height: 32,
  textAlign: "center",
  textAlignVertical: "center",
  borderRadius: 6,
  fontSize: 18,
  marginHorizontal: 6
},

counterValue: {
  minWidth: 30,
  textAlign: "center",
  fontSize: 15,
  fontWeight: "600",
  borderWidth: 1,
  borderColor: "#ccc",
  paddingVertical: 5,
  borderRadius: 6
},

// css for dropdownj
dropdown: {
  height: 50,
  borderWidth: 1,
  borderColor: "#ccc",
  borderRadius: 8,
  paddingHorizontal: 12
},


// for table color change 
tableContainer: {
  backgroundColor: "#fff",
  marginTop: 10,
  paddingVertical: 10,
  
 
},

tableHeader: {
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "space-between",
  
},

tableRow: {
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "space-between",
  marginVertical: 6,
  color: "#1c49de"
},

headerSr: {
  width: "12%",
  fontWeight: "700",
  fontSize: 13
},

headerSubject: {
  width: "48%",
  fontWeight: "700",
  fontSize: 13
},

headerQuestion: {
  width: "30%",
  fontWeight: "700",
  fontSize: 13,
  textAlign: "center"
},

srNo: {
  width: "12%",
  fontSize: 13
},

subjectInput: {
  width: "48%",
  borderWidth: 1,
  borderColor: "#ccc",
  borderRadius: 6,
  paddingHorizontal: 8,
  height: 40,
  marginRight: 6
},

questionInput: {
  width: "30%",
  borderWidth: 1,
  borderColor: "#ccc",
  borderRadius: 6,
  paddingHorizontal: 8,
  height: 40,
  textAlign: "center"
},
// for class dropdown
addClassText: {
  color: "#4A6CF7",
  fontSize: 13,
  fontWeight: "600",
  marginTop: 4,
  alignSelf: "flex-end"
},

// submit btn
submitBtnWrapper: {
  width: "100%",
  marginTop: 30,
  marginBottom: 20
},

submitBtn: {
  backgroundColor: "#000",
  color: "#fff",
  textAlign: "center",
  paddingVertical: 14,
  borderRadius: 8,
  fontSize: 16,
  fontWeight: "600"
},


})