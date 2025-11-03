import {
  FileCheck,
  CreditCard,
  Briefcase,
  GraduationCap,
  Car,
  Building2,
  Heart,
  Home as HomeIcon,
  Receipt,
  Vote,
} from "lucide-react";

export interface ServiceData {
  id: string;
  icon: any;
  name: string;
  description: string;
  category: string;
  status: string;
  badge: string;
  gradient: string;
  processingTime: string;
  fee: string;
  validity?: string;
  documents: Array<{
    name: string;
    required: boolean;
  }>;
  steps: Array<{
    number: number;
    title: string;
    description: string;
  }>;
  faqs: Array<{
    question: string;
    answer: string;
  }>;
  downloads: Array<{
    name: string;
    size: string;
    format: string;
  }>;
}

export const servicesData: Record<string, ServiceData> = {
  passport: {
    id: "passport",
    icon: FileCheck,
    name: "Passport Services",
    description:
      "Apply for a new passport, renew your existing passport, or update details on your passport.",
    category: "Documents",
    status: "Available",
    badge: "Popular",
    gradient: "from-blue-500 to-blue-600",
    processingTime: "15-20 working days",
    fee: "₹1,500 - ₹3,500",
    validity: "10 years",
    documents: [
      {
        name: "Proof of Identity (Aadhaar/PAN)",
        required: true,
      },
      { name: "Proof of Address", required: true },
      { name: "Recent Photographs", required: true },
      { name: "Birth Certificate", required: true },
    ],
    steps: [
      {
        number: 1,
        title: "Register Online",
        description:
          "Create an account on the Passport Seva Portal with your email and mobile number",
      },
      {
        number: 2,
        title: "Fill Application Form",
        description:
          "Complete the passport application form with accurate personal details",
      },
      {
        number: 3,
        title: "Upload Documents",
        description:
          "Upload scanned copies of required documents as per specifications",
      },
      {
        number: 4,
        title: "Pay Fee",
        description:
          "Pay the application fee online through available payment methods",
      },
      {
        number: 5,
        title: "Book Appointment",
        description:
          "Schedule your visit to the nearest Passport Seva Kendra",
      },
      {
        number: 6,
        title: "Visit PSK",
        description:
          "Visit the center on your appointment date with original documents",
      },
    ],
    faqs: [
      {
        question: "What is the processing time for a passport?",
        answer:
          "Regular processing takes 15-20 working days from the date of application. Tatkal service is available for urgent cases and takes 3-5 working days.",
      },
      {
        question: "Can I track my application status?",
        answer:
          "Yes, you can track your application status using your application reference number on the Passport Seva website.",
      },
      {
        question: "What is the validity of an Indian passport?",
        answer:
          "An Indian passport is valid for 10 years from the date of issue for adults and 5 years for minors.",
      },
    ],
    downloads: [
      {
        name: "Passport Application Form",
        size: "2.5 MB",
        format: "PDF",
      },
      {
        name: "Document Checklist",
        size: "1.2 MB",
        format: "PDF",
      },
      {
        name: "Guidelines & Instructions",
        size: "3.8 MB",
        format: "PDF",
      },
      { name: "Fee Structure", size: "890 KB", format: "PDF" },
    ],
  },
  aadhaar: {
    id: "aadhaar",
    icon: CreditCard,
    name: "Aadhaar Services",
    description:
      "Update Aadhaar details, download e-Aadhaar, or link with various government services.",
    category: "Documents",
    status: "Available",
    badge: "Essential",
    gradient: "from-purple-500 to-purple-600",
    processingTime: "7-10 working days",
    fee: "₹50 - ₹100",
    validity: "Lifetime",
    documents: [
      { name: "Proof of Identity", required: true },
      { name: "Proof of Address", required: true },
      { name: "Date of Birth Proof", required: true },
    ],
    steps: [
      {
        number: 1,
        title: "Locate Enrollment Center",
        description:
          "Find your nearest Aadhaar enrollment or update center",
      },
      {
        number: 2,
        title: "Fill Enrollment Form",
        description:
          "Complete the Aadhaar enrollment/update form with required details",
      },
      {
        number: 3,
        title: "Submit Documents",
        description:
          "Provide original documents for verification",
      },
      {
        number: 4,
        title: "Biometric Capture",
        description:
          "Fingerprints, iris scan, and photograph will be captured",
      },
      {
        number: 5,
        title: "Receive Acknowledgment",
        description:
          "Get your enrollment/update acknowledgment slip",
      },
    ],
    faqs: [
      {
        question: "How do I update my Aadhaar address?",
        answer:
          "You can update your address online through the UIDAI website or by visiting an Aadhaar enrollment center with address proof documents.",
      },
      {
        question: "What is the fee for Aadhaar updates?",
        answer:
          "Demographic updates (name, address, etc.) cost ₹50. Biometric updates cost ₹100. The first update is free.",
      },
    ],
    downloads: [
      {
        name: "Aadhaar Update Form",
        size: "1.8 MB",
        format: "PDF",
      },
      {
        name: "List of Acceptable Documents",
        size: "950 KB",
        format: "PDF",
      },
      {
        name: "Update Process Guide",
        size: "2.1 MB",
        format: "PDF",
      },
    ],
  },
  epfo: {
    id: "epfo",
    icon: Briefcase,
    name: "EPFO Services",
    description:
      "Check PF balance, transfer PF between employers, and process withdrawal claims.",
    category: "Employment",
    status: "Available",
    badge: "Trending",
    gradient: "from-green-500 to-green-600",
    processingTime: "7-10 working days",
    fee: "Free",
    documents: [
      {
        name: "UAN (Universal Account Number)",
        required: true,
      },
      { name: "Aadhaar Card", required: true },
      { name: "Bank Account Details", required: true },
      { name: "PAN Card", required: false },
    ],
    steps: [
      {
        number: 1,
        title: "Activate UAN",
        description:
          "Activate your Universal Account Number if not already done",
      },
      {
        number: 2,
        title: "Link Aadhaar & Bank",
        description:
          "Link your Aadhaar and bank account to your UAN",
      },
      {
        number: 3,
        title: "Login to Portal",
        description:
          "Access the EPFO member portal with your UAN and password",
      },
      {
        number: 4,
        title: "Submit Claim Form",
        description:
          "Fill and submit the appropriate claim form online",
      },
      {
        number: 5,
        title: "Track Status",
        description: "Monitor your claim status online",
      },
    ],
    faqs: [
      {
        question: "How do I check my PF balance?",
        answer:
          "You can check your PF balance by logging into the EPFO portal with your UAN or by sending an SMS to 7738299899 in the format: EPFOHO UAN ENG.",
      },
      {
        question: "What is the PF withdrawal process?",
        answer:
          "You can withdraw PF online by submitting Form 19 or 10C through the EPFO portal. The amount will be credited to your linked bank account within 7-10 days.",
      },
    ],
    downloads: [
      {
        name: "PF Claim Form 19",
        size: "1.5 MB",
        format: "PDF",
      },
      {
        name: "PF Claim Form 10C",
        size: "1.3 MB",
        format: "PDF",
      },
      {
        name: "Transfer Claim Form 13",
        size: "1.4 MB",
        format: "PDF",
      },
    ],
  },
  scholarship: {
    id: "scholarship",
    icon: GraduationCap,
    name: "Scholarship Programs",
    description:
      "Apply for government scholarships, educational grants, and fee reimbursements.",
    category: "Education",
    status: "New",
    badge: "New",
    gradient: "from-orange-500 to-orange-600",
    processingTime: "30-45 days",
    fee: "Free",
    documents: [
      { name: "Mark Sheets / Grade Cards", required: true },
      { name: "Income Certificate", required: true },
      {
        name: "Caste Certificate (if applicable)",
        required: false,
      },
      { name: "Bank Account Details", required: true },
      { name: "Bonafide Certificate", required: true },
    ],
    steps: [
      {
        number: 1,
        title: "Check Eligibility",
        description:
          "Verify if you meet the scholarship criteria",
      },
      {
        number: 2,
        title: "Register on Portal",
        description:
          "Create account on National Scholarship Portal",
      },
      {
        number: 3,
        title: "Fill Application",
        description:
          "Complete scholarship application with accurate details",
      },
      {
        number: 4,
        title: "Upload Documents",
        description:
          "Submit all required certificates and documents",
      },
      {
        number: 5,
        title: "Institute Verification",
        description:
          "Your application will be verified by your institution",
      },
    ],
    faqs: [
      {
        question: "Who is eligible for scholarships?",
        answer:
          "Eligibility varies by scheme but generally includes criteria based on academic performance, family income, and category (SC/ST/OBC/General).",
      },
      {
        question: "When can I apply for scholarships?",
        answer:
          "Most scholarship applications open in August-September for the academic year. Check the National Scholarship Portal for specific dates.",
      },
    ],
    downloads: [
      {
        name: "Scholarship Application Guide",
        size: "2.8 MB",
        format: "PDF",
      },
      {
        name: "Eligibility Criteria",
        size: "1.6 MB",
        format: "PDF",
      },
      {
        name: "Document Requirements",
        size: "1.1 MB",
        format: "PDF",
      },
    ],
  },
  "driving-license": {
    id: "driving-license",
    icon: Car,
    name: "Driving License",
    description:
      "Apply for a new driving license or renew your existing license online.",
    category: "Transport",
    status: "Available",
    badge: "Quick",
    gradient: "from-red-500 to-red-600",
    processingTime: "10-15 days",
    fee: "₹200 - ₹1,000",
    validity: "20 years (until age 50)",
    documents: [
      { name: "Proof of Age", required: true },
      { name: "Proof of Address", required: true },
      { name: "Medical Certificate (Form 1A)", required: true },
      { name: "Learner's License", required: true },
      { name: "Passport Size Photos", required: true },
    ],
    steps: [
      {
        number: 1,
        title: "Obtain Learner's License",
        description:
          "Pass the learner's test if you don't have one",
      },
      {
        number: 2,
        title: "Practice Period",
        description:
          "Wait for mandatory 30-day practice period",
      },
      {
        number: 3,
        title: "Book Slot Online",
        description: "Schedule your driving test at RTO",
      },
      {
        number: 4,
        title: "Pass Driving Test",
        description: "Clear the practical driving test",
      },
      {
        number: 5,
        title: "Receive License",
        description: "Collect your driving license from RTO",
      },
    ],
    faqs: [
      {
        question:
          "What is the minimum age for a driving license?",
        answer:
          "You must be at least 18 years old to apply for a permanent driving license for light motor vehicles. For commercial vehicles, the minimum age is 20.",
      },
      {
        question: "How long is a driving license valid?",
        answer:
          "A driving license is valid for 20 years from the date of issue or until the holder attains the age of 50 years, whichever is earlier.",
      },
    ],
    downloads: [
      {
        name: "DL Application Form",
        size: "1.7 MB",
        format: "PDF",
      },
      {
        name: "Medical Certificate Format",
        size: "850 KB",
        format: "PDF",
      },
      {
        name: "Driving Test Guidelines",
        size: "2.2 MB",
        format: "PDF",
      },
    ],
  },
};

export const getServiceById = (
  id: string,
): ServiceData | undefined => {
  return servicesData[id];
};

export const getAllServices = (): ServiceData[] => {
  return Object.values(servicesData);
};