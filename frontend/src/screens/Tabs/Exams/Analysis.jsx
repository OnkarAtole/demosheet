import React, { useEffect, useRef, useState } from "react";
import {View,Text,StyleSheet,FlatList,TouchableOpacity,Modal,Animated,Dimensions,TextInput} from "react-native";
import { getExamAnalysis } from "../../../services/resultService";

const { width } = Dimensions.get("window");

export default function Analysis({ route }) {

const { examId } = route.params;
const scrollX = useRef(new Animated.Value(0)).current;
const [selectedTopper,setSelectedTopper] = useState(null);
const [modalVisible,setModalVisible] = useState(false);
const [selectedFilter,setSelectedFilter] = useState("ALL");
const [customModal,setCustomModal] = useState(false);
const [customValue,setCustomValue] = useState("");
const [students,setStudents] = useState([]);

const toppers = [...students]
  .sort((a,b)=>b.percentage - a.percentage)
  .slice(0,10);

const [filteredStudents,setFilteredStudents] = useState([]);
const applyFilter = (cutoff) => {
setSelectedFilter(cutoff);

if(cutoff === "ALL"){
setFilteredStudents(students);
return;
}

if(cutoff === "CUSTOM"){
setCustomModal(true);
return;
}

const filtered = students.filter(s => s.percentage >= cutoff);
setFilteredStudents(filtered);

};
const openTopper = (item,index)=>{
setSelectedTopper({...item,rank:index+1});
setModalVisible(true);
};

useEffect(()=>{
    if(students.length > 3){
    Animated.loop(
    Animated.timing(scrollX,{
    toValue:-width*1.5,
    duration:14000,
    useNativeDriver:true
    })
    ).start();

}},[students]);

useEffect(() => {
    const fetchAnalysis = async () => {
    try{
        const data = await getExamAnalysis(examId);

        const sorted = data.sort((a,b)=>b.percentage - a.percentage);

        setStudents(sorted);
        setFilteredStudents(sorted);

    }catch(err){
        console.log(err);
    }

};
fetchAnalysis();
},[]);

return (
    <View style={styles.container}>
        <Text style={styles.heading}>Analysis</Text>
        {/* TOPPER STORIES */}

        <View style={styles.topperContainer}>

            <Animated.View
            style={[
            styles.topperSlider,
            { transform:[{translateX:scrollX}] }
            ]}
            >

            {toppers.map((item,index)=>(
                <TouchableOpacity
                key={index}
                style={styles.story}
                onPress={()=>openTopper(item,index)}
                >
                <View style={styles.storyCircle}>

                    <Text style={styles.rankText}>
                    #{index + 1}
                    </Text>

                    <Text style={styles.rollNumber}>
                    {item.roll_number}
                    </Text>

                </View>
                <Text style={styles.storyText}>
                Roll {item.roll_number}
                </Text>

                </TouchableOpacity> 
            ))}
            </Animated.View>
        </View>

    {/* custom popup */}
        <Modal
        transparent
        visible={customModal}
        animationType="fade"
        >
        <View style={styles.modalBackground}>

        <View style={styles.modalCard}>

        <Text style={styles.modalTitle}>Enter Percentage (0-100)</Text>

        <TextInput
        style={styles.input}
        placeholder="Example: 45 or 67.5"
        keyboardType="numeric"
        value={customValue}
        onChangeText={(text)=>{
        const clean = text.replace(/[^0-9.]/g,'');
        setCustomValue(clean);
        }}
        />

        <TouchableOpacity
        style={styles.applyBtn}
        onPress={()=>{

        const num = parseFloat(customValue);

        // validation
        if(isNaN(num)){
        alert("Please enter a valid number");
        return;
        }

        if(num < 0 || num > 100){
        alert("Percentage must be between 0 and 100");
        return;
        }

        // limit decimals like 67.55
        if(!/^\d{1,3}(\.\d{1,2})?$/.test(customValue)){
        alert("Only numbers like 45 or 67.5 allowed");
        return;
        }

        const filtered = students.filter(s => s.percentage >= num);

        setFilteredStudents(filtered);
        setSelectedFilter("CUSTOM");

        setCustomModal(false);
        setCustomValue("");

        }}
        >
        <Text style={{color:"#fff"}}>Apply</Text>
        </TouchableOpacity>
    {/* cancel btn */}
        <TouchableOpacity
            style={[styles.applyBtn,{backgroundColor:"#888",marginTop:8}]}
            onPress={()=>{
            setCustomModal(false);
            setCustomValue("");
            setSelectedFilter("ALL");
            setFilteredStudents(students);
            }}
            >
            <Text style={{color:"#fff"}}>Cancel</Text>
            </TouchableOpacity>

        </View>

        </View>

        </Modal>



        {/* FILTER BUTTONS */}
        <View style={styles.filterContainer}>

        <TouchableOpacity
        style={[styles.filterBtn, selectedFilter==="ALL" && styles.activeFilter]}
        onPress={()=>applyFilter("ALL")}
        >
        <Text>All</Text>
        </TouchableOpacity>

        <TouchableOpacity
        style={[styles.filterBtn, selectedFilter===20 && styles.activeFilter]}
        onPress={()=>applyFilter(20)}
        >
        <Text>20%</Text>
        </TouchableOpacity>

        <TouchableOpacity
        style={[styles.filterBtn, selectedFilter===30 && styles.activeFilter]}
        onPress={()=>applyFilter(30)}
        >
        <Text>30%</Text>
        </TouchableOpacity>

        <TouchableOpacity
        style={[styles.filterBtn, selectedFilter===40 && styles.activeFilter]}
        onPress={()=>applyFilter(40)}
        >
        <Text>40%</Text>
        </TouchableOpacity>

        <TouchableOpacity
        style={[styles.filterBtn, selectedFilter==="CUSTOM" && styles.activeFilter]}
        onPress={()=>applyFilter("CUSTOM")}
        >
        <Text>Custom</Text>
        </TouchableOpacity>

        </View>

        {/* STUDENT TABLE */}

        <View style={styles.tableHeader}>
        <Text style={[styles.headerText,{flex:0.5}]}>SN</Text>
        <Text style={[styles.headerText,{flex:2}]}>Name</Text>
        <Text style={[styles.headerText,{flex:1}]}>Roll</Text>
        <Text style={[styles.headerText,{flex:0.8}]}>%</Text>
        </View>

        <FlatList
        data={filteredStudents}
        // keyExtractor={(item)=>item.id.toString()}
        keyExtractor={(item)=>item.roll_number.toString()}
        renderItem={({item,index})=>(
        <View style={[
        styles.row,
        {backgroundColor:index%2===0?"#ffffff":"#f3f3f3"}
        ]}>

        <Text style={[styles.cell,{flex:0.5}]}>{index+1}</Text>
        <Text style={[styles.cell,{flex:2}]}>{item.name}</Text>
        {/* <Text style={[styles.cell,{flex:1}]}>{item.roll_number}</Text> */}
        <Text style={[styles.cell,{flex:1}]}>{item.roll_number}</Text>
        <Text style={[styles.cell,{flex:0.8}]}>{item.percentage}%</Text>

        </View>
        )}
        />

        {/* TOPPER MODAL */}
        <Modal
        transparent
        visible={modalVisible}
        animationType="fade"
        >

        <TouchableOpacity
        style={styles.modalBackground}
        activeOpacity={1}
        onPressOut={()=>setModalVisible(false)}
        >

        <View style={styles.modalCard}>

        <Text style={styles.modalTitle}>Topper Rank #{selectedTopper?.rank}</Text>

        <Text>Name : {selectedTopper?.name}</Text>

        {/* <Text>Roll No : {selectedTopper?.roll}</Text> */}
        <Text>Roll No : {selectedTopper?.roll_number}</Text>

        <Text>Percentage : {selectedTopper?.percentage}%</Text>

        </View>

        </TouchableOpacity>

        </Modal>

    </View>
);
}

const styles = StyleSheet.create({

container:{
flex:1,
backgroundColor:"#f2f2f2",
paddingTop:40
},

heading:{
fontSize:20,
fontWeight:"bold",
marginBottom:10,
color:"#1f3c88",
marginLeft:20
},

topperContainer:{
height:120,
marginBottom:15,
overflow:"hidden",
justifyContent:"center"
},
topperSlider:{
flexDirection:"row",
alignItems:"center"
},

story:{
alignItems:"center",
marginHorizontal:18
},

storyCircle:{
width:72,
height:72,
borderRadius:36,
backgroundColor:"#ccc",
marginBottom:6,
justifyContent:"center",
alignItems:"center"
},

storyText:{
fontSize:12,
fontWeight:"500",
textAlign:"center"
},

filterContainer:{
flexDirection:"row",
marginBottom:15
},

filterBtn:{
backgroundColor:"#ddd",
paddingHorizontal:18,
paddingVertical:14,
borderRadius:20,
marginRight:10
},

tableHeader:{
flexDirection:"row",
paddingVertical:12,
paddingLeft:18,
paddingRight:10
},

headerText:{
flex:1,
fontWeight:"bold",
textAlign:"left"
},
row:{
flexDirection:"row",
paddingVertical:14,
paddingLeft:18,
paddingRight:10
},

cell:{
flex:1,
textAlign:"left"
},

modalBackground:{
flex:1,
justifyContent:"center",
alignItems:"center",
backgroundColor:"rgba(0, 0, 0, 0.4)"
},

modalCard:{
backgroundColor:"#fff",
padding:25,
borderRadius:10,
width:"75%"
},

modalTitle:{
fontWeight:"bold",
fontSize:16,
marginBottom:10
},

rollNumber:{
fontSize:20,
fontWeight:"bold",
color:"#222"
},

rankText:{
fontSize:12,
fontWeight:"bold",
color:"#555"
},

// styles for custom filter modal
activeFilter:{
backgroundColor:"#4f6cc3"
},

input:{
borderWidth:1,
borderColor:"#ccc",
borderRadius:6,
padding:8,
marginTop:10,
marginBottom:15
},

applyBtn:{
backgroundColor:"#4f6cc3",
padding:10,
borderRadius:6,
alignItems:"center"
},
});