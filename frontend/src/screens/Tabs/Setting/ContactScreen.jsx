
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Linking,
  SafeAreaView,
} from 'react-native';
import { FontAwesome, MaterialIcons } from '@expo/vector-icons';
import { useState } from 'react';
const ContactScreen = () => {

  const openLink = async (appUrl, webUrl) => {
    const supported = await Linking.canOpenURL(appUrl);
    if (supported) {
      await Linking.openURL(appUrl);
    } else {
      await Linking.openURL(webUrl);
    }
  };

  const openEmail = () => {
    Linking.openURL('mailto:support@evalsnap.com');
  };

  // Faq raw data

  const [activeIndex, setActiveIndex] = useState(null);

const faqData = [
  {
    question: 'How do I scan an OMR sheet?',
    answer: 'Go to Exams → Select Exam → Scan OMR. Ensure proper lighting and align sheet correctly.'
  },
  {
    question: 'Why is my OMR not detecting bubbles?',
    answer: 'Check lighting conditions and ensure bubbles are filled completely using dark ink.'
  },
  {
    question: 'How can I create a new exam?',
    answer: 'Navigate to Exams tab and tap on Add Exam to create a new test.'
  },
  {
    question: 'How can I create new class and Add students?',
    answer: 'Go to Classes tab and tap on Add Class to create a new class. Then, add students to the class from the class details screen.'    
  },
  {
    question: 'Is internet required for scanning?',
    answer: 'Internet is required to sync results.'
  },
  {
    question: 'How do I edit my profile?',
    answer: 'Go to More → Edit Profile to update your details.'
  },
];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>

        <Text style={styles.headerTitle}>Contact & Support</Text>
        <Text style={styles.subTitle}>
          Need help with exams or scanning? Connect with us anytime.
        </Text>

        <Text style={styles.sectionTitle}>Connect With Us</Text>
        
      {/* Email service */}
        <TouchableOpacity style={styles.card} onPress={openEmail}>
          <View style={styles.iconCircle}>
            <MaterialIcons name="email" size={22} color="#000" />
          </View>
          <View style={styles.cardContent}>
            <Text style={styles.cardTitle}>Email Support</Text>
            <Text style={styles.cardSubtitle}>support@evalsnap.com</Text>
          </View>
          <MaterialIcons name="arrow-forward-ios" size={16} color="#555" />
        </TouchableOpacity>

      {/* Whatasaap section */}
        <TouchableOpacity
          style={styles.card}
          onPress={() =>
            openLink(
              'whatsapp://send?phone=918999006052',
              'https://wa.me/8999006052'
            )
          }>
          <View style={styles.iconCircle}>
            <FontAwesome name="whatsapp" size={22} color="#000" />
          </View>
          <View style={styles.cardContent}>
            <Text style={styles.cardTitle}>WhatsApp</Text>
            <Text style={styles.cardSubtitle}>Chat with support</Text>
          </View>
          <MaterialIcons name="arrow-forward-ios" size={16} color="#555" />
        </TouchableOpacity>


          {/* FAQ section */}
          <Text style={styles.sectionTitle}>Frequently Asked Questions</Text>

              {faqData.map((item, index) => (
                <View key={index} style={styles.faqContainer}>
                  <TouchableOpacity
                    style={styles.faqHeader}
                    onPress={() =>
                      setActiveIndex(activeIndex === index ? null : index)
                    }>
                    <Text style={styles.faqQuestion}>{item.question}</Text>
                    <MaterialIcons
                      name={activeIndex === index ? 'keyboard-arrow-up' : 'keyboard-arrow-down'}
                      size={22}
                      color="#1f3c88"
                    />
                  </TouchableOpacity>

                  {activeIndex === index && (
                    <Text style={styles.faqAnswer}>{item.answer}</Text>
                  )}
                </View>
              ))}

        <View style={styles.footer}>
          <Text style={styles.footerText}>Version 1.0.0</Text>
          <Text style={styles.footerText}>© 2026 EvalSnap</Text>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
};

export default ContactScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    paddingHorizontal: 16,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '600',
    marginTop: 45,
    color: '#1f3c88',
  },
  subTitle: {
    fontSize: 14,
    color: '#555',
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 15,
    marginBottom: 10,
    color: '#1f3c88',
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    padding: 14,
    borderRadius: 12,
    marginBottom: 12,
  },
  iconCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#E8DADA',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  cardContent: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: '500',
  },
  cardSubtitle: {
    fontSize: 12,
    color: '#777',
  },
  footer: {
    alignItems: 'center',
    marginTop: 30,
    marginBottom: 20,
  },
  footerText: {
    fontSize: 12,
    color: '#888',
  },

  // faq styles
  faqContainer: {
  backgroundColor: '#FFF',
  borderRadius: 12,
  marginBottom: 10,
  paddingHorizontal: 14,
  paddingVertical: 12,
},

faqHeader: {
  flexDirection: 'row',
  justifyContent: 'space-between',
  alignItems: 'center',
},

faqQuestion: {
  fontSize: 14,
  fontWeight: '500',
  flex: 1,
  paddingRight: 10,
},

faqAnswer: {
  marginTop: 8,
  fontSize: 13,
  color: '#555',
  lineHeight: 18,
},
});