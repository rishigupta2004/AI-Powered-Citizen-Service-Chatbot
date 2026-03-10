import {
  Activity,
  BookOpen,
  Briefcase,
  Car,
  CreditCard,
  FileCheck,
  FileText,
  Gavel,
  GraduationCap,
  HandCoins,
  HeartPulse,
  Home,
  IdCard,
  Landmark,
  Leaf,
  LucideIcon,
  Scale,
  Shield,
  ShieldCheck,
  Stethoscope,
  Tractor,
  Users,
  Vote,
  Wallet,
} from "lucide-react";

type ServiceMode = "Apply Online" | "Partially Online" | "Info Only";

export interface ServiceData {
  id: string;
  icon: LucideIcon;
  name: string;
  description: string;
  category: string;
  status: string;
  badge: string;
  gradient: string;
  processingTime: string;
  fee: string;
  mode: ServiceMode;
  officialAuthority: string;
  officialUrl: string;
  lastVerifiedAt: string;
  validity?: string;
  documents: Array<{ name: string; required: boolean }>;
  steps: Array<{ number: number; title: string; description: string }>;
  faqs: Array<{ question: string; answer: string }>;
  downloads: Array<{ name: string; size: string; format: string }>;
}

type ServiceSeed = {
  id: string;
  name: string;
  category: string;
  mode: ServiceMode;
  officialAuthority: string;
  officialUrl: string;
  summary: string;
  icon: LucideIcon;
  badge?: string;
  processingTime?: string;
  fee?: string;
  validity?: string;
};

const LAST_VERIFIED_AT = "2026-03-10";

const categoryTheme: Record<string, { gradient: string; status: string; defaultBadge: string }> = {
  "Identity & Travel Documents": { gradient: "from-blue-500 to-blue-700", status: "Available", defaultBadge: "Popular" },
  "Digital Identity": { gradient: "from-indigo-500 to-indigo-700", status: "Available", defaultBadge: "Essential" },
  Taxation: { gradient: "from-purple-500 to-purple-700", status: "Available", defaultBadge: "High Use" },
  "Social Security & Provident Fund": { gradient: "from-emerald-500 to-emerald-700", status: "Available", defaultBadge: "Citizen" },
  Pension: { gradient: "from-teal-500 to-teal-700", status: "Available", defaultBadge: "Senior" },
  "Digital Documents": { gradient: "from-sky-500 to-sky-700", status: "Available", defaultBadge: "Paperless" },
  "Integrated Citizen Services": { gradient: "from-cyan-500 to-cyan-700", status: "Available", defaultBadge: "Unified" },
  "Pension & Retirement": { gradient: "from-green-500 to-green-700", status: "Available", defaultBadge: "Retirement" },
  "Labour & Welfare": { gradient: "from-lime-500 to-lime-700", status: "Available", defaultBadge: "Welfare" },
  Employment: { gradient: "from-amber-500 to-amber-700", status: "Available", defaultBadge: "Jobs" },
  "Skill Development & Employment": { gradient: "from-orange-500 to-orange-700", status: "Available", defaultBadge: "Skill" },
  "Agriculture & Farmer Support": { gradient: "from-green-500 to-lime-700", status: "Available", defaultBadge: "Farmer" },
  "Agriculture Insurance": { gradient: "from-green-600 to-emerald-700", status: "Available", defaultBadge: "Insurance" },
  "Agriculture Market Access": { gradient: "from-emerald-500 to-teal-700", status: "Available", defaultBadge: "Market" },
  "Education & Scholarships": { gradient: "from-violet-500 to-fuchsia-700", status: "Available", defaultBadge: "Students" },
  "Education & Online Learning": { gradient: "from-fuchsia-500 to-pink-700", status: "Available", defaultBadge: "Learning" },
  "School Education": { gradient: "from-pink-500 to-rose-700", status: "Available", defaultBadge: "Teachers" },
  "Higher Education": { gradient: "from-violet-500 to-indigo-700", status: "Available", defaultBadge: "Academic" },
  Elections: { gradient: "from-rose-500 to-red-700", status: "Available", defaultBadge: "Democracy" },
  "Transparency & Governance": { gradient: "from-slate-500 to-slate-700", status: "Available", defaultBadge: "Rights" },
  "Public Grievance Redressal": { gradient: "from-slate-600 to-zinc-700", status: "Available", defaultBadge: "Complaint" },
  Judiciary: { gradient: "from-zinc-500 to-neutral-700", status: "Available", defaultBadge: "Courts" },
  "Law & Legal Information": { gradient: "from-stone-500 to-stone-700", status: "Available", defaultBadge: "Legal" },
  "Law & Notifications": { gradient: "from-neutral-500 to-stone-700", status: "Available", defaultBadge: "Gazette" },
  "Citizen Participation": { gradient: "from-cyan-500 to-blue-700", status: "Available", defaultBadge: "Engage" },
  "Scheme Discovery": { gradient: "from-blue-500 to-cyan-700", status: "Available", defaultBadge: "Discover" },
  "Government Information": { gradient: "from-gray-500 to-slate-700", status: "Available", defaultBadge: "Info" },
  "Road Transport": { gradient: "from-red-500 to-orange-700", status: "Available", defaultBadge: "Transport" },
  "Road Transport Enforcement": { gradient: "from-red-600 to-rose-700", status: "Available", defaultBadge: "Penalty" },
  "Health Insurance": { gradient: "from-emerald-500 to-cyan-700", status: "Available", defaultBadge: "Health" },
  "Digital Health": { gradient: "from-teal-500 to-cyan-700", status: "Available", defaultBadge: "Digital" },
  "Public Health": { gradient: "from-cyan-500 to-sky-700", status: "Available", defaultBadge: "Vaccination" },
  Telemedicine: { gradient: "from-cyan-600 to-blue-700", status: "Available", defaultBadge: "Remote Care" },
  "Healthcare Access": { gradient: "from-teal-500 to-blue-700", status: "Available", defaultBadge: "Hospitals" },
  "Consumer Protection": { gradient: "from-amber-500 to-orange-700", status: "Available", defaultBadge: "Consumer" },
  "Consumer Justice": { gradient: "from-orange-500 to-red-700", status: "Available", defaultBadge: "Justice" },
  "Public Safety": { gradient: "from-red-500 to-pink-700", status: "Available", defaultBadge: "Safety" },
  "Disability Welfare": { gradient: "from-indigo-500 to-violet-700", status: "Available", defaultBadge: "Inclusion" },
  Housing: { gradient: "from-blue-500 to-indigo-700", status: "Available", defaultBadge: "Housing" },
  "Civil Aviation": { gradient: "from-sky-500 to-indigo-700", status: "Available", defaultBadge: "Aviation" },
  "Overseas Employment": { gradient: "from-indigo-500 to-blue-700", status: "Available", defaultBadge: "Global" },
};

const seeds: ServiceSeed[] = [
  { id: "passport_seva", name: "Passport Seva", category: "Identity & Travel Documents", mode: "Apply Online", officialAuthority: "Ministry of External Affairs (MEA), Government of India", officialUrl: "https://www.passportindia.gov.in/", summary: "Apply for fresh passport or re-issue, book PSK appointment, and track status online.", icon: FileCheck },
  { id: "uidai_aadhaar_services", name: "UIDAI Aadhaar Services", category: "Digital Identity", mode: "Partially Online", officialAuthority: "UIDAI", officialUrl: "https://uidai.gov.in/", summary: "Access Aadhaar services, enrollment center info, update guidance, and authentication support.", icon: IdCard },
  { id: "myaadhaar_portal", name: "myAadhaar Portal", category: "Digital Identity", mode: "Apply Online", officialAuthority: "UIDAI", officialUrl: "https://myaadhaar.uidai.gov.in/", summary: "Download Aadhaar, book appointments, and manage Aadhaar self-service tasks.", icon: CreditCard },
  { id: "income_tax_efiling", name: "Income Tax e-Filing", category: "Taxation", mode: "Apply Online", officialAuthority: "Income Tax Department", officialUrl: "https://www.incometax.gov.in/iec/foportal/", summary: "File ITR, pay taxes, view compliance notices, and manage tax profile online.", icon: Wallet },
  { id: "instant_epan_service", name: "Instant e-PAN", category: "Taxation", mode: "Apply Online", officialAuthority: "Income Tax Department", officialUrl: "https://www.incometax.gov.in/", summary: "Generate paperless PAN for eligible citizens using Aadhaar verification.", icon: FileText },
  { id: "gst_portal", name: "GST Portal", category: "Taxation", mode: "Apply Online", officialAuthority: "GSTN", officialUrl: "https://www.gst.gov.in/", summary: "Register GST, file returns, pay tax, and manage GST compliance workflows.", icon: Landmark },
  { id: "epfo_member_esewa", name: "EPFO Member e-Sewa", category: "Social Security & Provident Fund", mode: "Apply Online", officialAuthority: "EPFO", officialUrl: "https://unifiedportal-mem.epfindia.gov.in/memberinterface/", summary: "Manage UAN account, submit PF claims, and update KYC details.", icon: Briefcase },
  { id: "epfo_passbook_portal", name: "EPFO Passbook", category: "Social Security & Provident Fund", mode: "Info Only", officialAuthority: "EPFO", officialUrl: "https://passbook.epfindia.gov.in/MemberPassBook/Login", summary: "View PF contributions and account passbook linked to UAN.", icon: BookOpen },
  { id: "jeevan_pramaan", name: "Jeevan Pramaan", category: "Pension", mode: "Apply Online", officialAuthority: "Department of Pension & Pensioners' Welfare", officialUrl: "https://jeevanpramaan.gov.in/", summary: "Submit digital life certificate for pension continuation.", icon: ShieldCheck },
  { id: "digilocker", name: "DigiLocker", category: "Digital Documents", mode: "Apply Online", officialAuthority: "MeitY", officialUrl: "https://www.digilocker.gov.in/", summary: "Fetch, store, and share government-issued documents digitally.", icon: FileCheck },
  { id: "umang", name: "UMANG", category: "Integrated Citizen Services", mode: "Apply Online", officialAuthority: "MeitY", officialUrl: "https://web.umang.gov.in/", summary: "Single portal/app for multiple central and state e-governance services.", icon: Users },
  { id: "enps_national_pension_system", name: "eNPS", category: "Pension & Retirement", mode: "Apply Online", officialAuthority: "PFRDA", officialUrl: "https://enps.nsdl.com/", summary: "Open and manage National Pension System account online.", icon: HandCoins },
  { id: "pm_shram_yogi_maandhan", name: "PM-SYM", category: "Social Security & Pension", mode: "Apply Online", officialAuthority: "Ministry of Labour & Employment", officialUrl: "https://maandhan.in/", summary: "Enroll unorganised workers in contributory pension scheme.", icon: Wallet },
  { id: "e_shram_portal", name: "e-Shram", category: "Labour & Welfare", mode: "Apply Online", officialAuthority: "Ministry of Labour & Employment", officialUrl: "https://eshram.gov.in/", summary: "Register as unorganised worker and access welfare-linked services.", icon: Briefcase },
  { id: "national_career_service", name: "National Career Service", category: "Employment", mode: "Apply Online", officialAuthority: "DGE, Ministry of Labour & Employment", officialUrl: "https://www.ncs.gov.in/", summary: "Search jobs, get career services, and connect with employers.", icon: Briefcase },
  { id: "apprenticeship_india", name: "Apprenticeship India", category: "Skill Development & Employment", mode: "Apply Online", officialAuthority: "MSDE", officialUrl: "https://www.apprenticeshipindia.gov.in/", summary: "Find and apply for apprenticeship opportunities nationwide.", icon: GraduationCap },
  { id: "pm_kisan", name: "PM-KISAN", category: "Agriculture & Farmer Support", mode: "Apply Online", officialAuthority: "Department of Agriculture & Farmers Welfare", officialUrl: "https://pmkisan.gov.in/", summary: "Register and track beneficiary status for PM-KISAN income support.", icon: Tractor },
  { id: "pmfby_crop_insurance", name: "PM Fasal Bima Yojana", category: "Agriculture Insurance", mode: "Apply Online", officialAuthority: "Ministry of Agriculture & Farmers Welfare", officialUrl: "https://pmfby.gov.in/", summary: "Crop insurance enrollment and claim-related information services.", icon: Shield },
  { id: "enam_national_agri_market", name: "e-NAM", category: "Agriculture Market Access", mode: "Apply Online", officialAuthority: "SFAC", officialUrl: "https://www.enam.gov.in/", summary: "Digital agricultural market platform with mandi integration.", icon: Leaf },
  { id: "national_scholarship_portal", name: "National Scholarship Portal", category: "Education & Scholarships", mode: "Apply Online", officialAuthority: "Government of India", officialUrl: "https://scholarships.gov.in/", summary: "Apply and track central scholarship schemes.", icon: GraduationCap },
  { id: "swayam", name: "SWAYAM", category: "Education & Online Learning", mode: "Apply Online", officialAuthority: "Ministry of Education", officialUrl: "https://swayam.gov.in/", summary: "Access certified online courses from national institutions.", icon: BookOpen },
  { id: "diksha", name: "DIKSHA", category: "School Education", mode: "Info Only", officialAuthority: "Ministry of Education", officialUrl: "https://diksha.gov.in/", summary: "Digital education resources for students and teachers.", icon: BookOpen },
  { id: "academic_bank_of_credits", name: "Academic Bank of Credits", category: "Higher Education", mode: "Apply Online", officialAuthority: "MoE / UGC ecosystem", officialUrl: "https://www.abc.gov.in/", summary: "Create and manage student academic credit account.", icon: GraduationCap },
  { id: "voters_service_portal", name: "Voters' Service Portal", category: "Elections", mode: "Apply Online", officialAuthority: "Election Commission of India", officialUrl: "https://voters.eci.gov.in/", summary: "Apply for voter services including registration and correction.", icon: Vote },
  { id: "electoral_search_service", name: "Electoral Search", category: "Elections", mode: "Info Only", officialAuthority: "Election Commission of India", officialUrl: "https://electoralsearch.eci.gov.in/", summary: "Search your voter record and polling details online.", icon: Vote },
  { id: "rti_online", name: "RTI Online", category: "Transparency & Governance", mode: "Apply Online", officialAuthority: "Department of Personnel and Training", officialUrl: "https://rtionline.gov.in/", summary: "File RTI applications and first appeals with participating authorities.", icon: Scale },
  { id: "cpgrams_pgportal", name: "CPGRAMS", category: "Public Grievance Redressal", mode: "Apply Online", officialAuthority: "DARPG", officialUrl: "https://pgportal.gov.in/", summary: "Submit and track grievances against central government departments.", icon: ShieldCheck },
  { id: "ecourts_services", name: "eCourts Services", category: "Judiciary", mode: "Info Only", officialAuthority: "eCommittee, Supreme Court of India", officialUrl: "https://ecourts.gov.in/", summary: "View case status, cause lists, and court order information.", icon: Gavel },
  { id: "india_code", name: "India Code", category: "Law & Legal Information", mode: "Info Only", officialAuthority: "Legislative Department", officialUrl: "https://www.indiacode.nic.in/", summary: "Browse central Acts and legal text in consolidated form.", icon: FileText },
  { id: "egazette", name: "e-Gazette", category: "Law & Notifications", mode: "Info Only", officialAuthority: "Department of Publication", officialUrl: "https://egazette.gov.in/", summary: "Access official Gazette notifications and publications.", icon: FileText },
  { id: "mygov_citizen_engagement", name: "MyGov", category: "Citizen Participation", mode: "Apply Online", officialAuthority: "MeitY", officialUrl: "https://www.mygov.in/", summary: "Participate in consultations, discussions, and citizen tasks.", icon: Users },
  { id: "myscheme_discovery", name: "MyScheme", category: "Scheme Discovery", mode: "Info Only", officialAuthority: "Government of India", officialUrl: "https://www.myscheme.gov.in/", summary: "Discover government schemes by profile and eligibility.", icon: BookOpen },
  { id: "national_portal_india", name: "National Portal of India", category: "Government Information", mode: "Info Only", officialAuthority: "NIC", officialUrl: "https://www.india.gov.in/", summary: "Official gateway for government information and service links.", icon: Landmark },
  { id: "sarathi_driving_licence_services", name: "Sarathi (Driving Licence)", category: "Road Transport", mode: "Apply Online", officialAuthority: "MoRTH", officialUrl: "https://sarathi.parivahan.gov.in/", summary: "Apply for learner and driving licence services online.", icon: Car },
  { id: "vahan_vehicle_services", name: "Vahan (Vehicle Services)", category: "Road Transport", mode: "Apply Online", officialAuthority: "MoRTH", officialUrl: "https://vahan.parivahan.gov.in/", summary: "Vehicle registration and related transport services portal.", icon: Car },
  { id: "echallan_parivahan", name: "eChallan", category: "Road Transport Enforcement", mode: "Partially Online", officialAuthority: "MoRTH", officialUrl: "https://echallan.parivahan.gov.in/", summary: "Check and pay traffic challans online.", icon: ShieldCheck },
  { id: "national_permit_parivahan", name: "National Permit", category: "Road Transport", mode: "Apply Online", officialAuthority: "MoRTH", officialUrl: "https://nationalpermit.parivahan.gov.in/", summary: "National goods-vehicle permit issuance and payment support.", icon: Car },
  { id: "parivahan_portal", name: "Parivahan Sewa", category: "Road Transport", mode: "Info Only", officialAuthority: "MoRTH", officialUrl: "https://parivahan.gov.in/parivahan/", summary: "Unified entry portal for transport-related citizen services.", icon: Car },
  { id: "ayushman_bharat_pmjay", name: "Ayushman Bharat PM-JAY", category: "Health Insurance", mode: "Info Only", officialAuthority: "National Health Authority", officialUrl: "https://pmjay.gov.in/", summary: "National health assurance scheme information and eligibility tools.", icon: HeartPulse },
  { id: "abha_health_id", name: "ABHA (Health ID)", category: "Digital Health", mode: "Apply Online", officialAuthority: "National Health Authority", officialUrl: "https://abha.abdm.gov.in/", summary: "Create and manage digital health account under ABDM.", icon: IdCard },
  { id: "cowin", name: "CoWIN", category: "Public Health", mode: "Apply Online", officialAuthority: "Ministry of Health and Family Welfare", officialUrl: "https://www.cowin.gov.in/", summary: "Book vaccination appointments and download certificates.", icon: Activity },
  { id: "e_sanjeevani", name: "eSanjeevani", category: "Telemedicine", mode: "Apply Online", officialAuthority: "Ministry of Health and Family Welfare", officialUrl: "https://esanjeevani.in/", summary: "Government telemedicine consultation platform.", icon: Stethoscope },
  { id: "ors_hospital_appointments", name: "ORS Hospital Appointments", category: "Healthcare Access", mode: "Apply Online", officialAuthority: "Ministry of Health and Family Welfare", officialUrl: "https://ors.gov.in/", summary: "Book OPD appointments in participating government hospitals.", icon: HeartPulse },
  { id: "national_consumer_helpline", name: "National Consumer Helpline", category: "Consumer Protection", mode: "Apply Online", officialAuthority: "Department of Consumer Affairs", officialUrl: "https://consumerhelpline.gov.in/", summary: "Register and escalate consumer complaints online.", icon: Users },
  { id: "edaakhil_consumer_cases", name: "eDaakhil", category: "Consumer Justice", mode: "Apply Online", officialAuthority: "Department of Consumer Affairs", officialUrl: "https://edaakhil.nic.in/", summary: "File consumer complaints and upload case documents digitally.", icon: Gavel },
  { id: "national_cyber_crime_reporting", name: "National Cyber Crime Reporting", category: "Public Safety", mode: "Apply Online", officialAuthority: "Ministry of Home Affairs", officialUrl: "https://cybercrime.gov.in/", summary: "Report cyber offences and fraud incidents online.", icon: ShieldCheck },
  { id: "udid_disability_card", name: "UDID", category: "Disability Welfare", mode: "Apply Online", officialAuthority: "Department of Empowerment of Persons with Disabilities", officialUrl: "https://www.swavlambancard.gov.in/", summary: "Apply for disability certificate and UDID card.", icon: IdCard },
  { id: "pmay_urban_mis", name: "PMAY Urban", category: "Housing", mode: "Apply Online", officialAuthority: "Ministry of Housing and Urban Affairs", officialUrl: "https://pmaymis.gov.in/", summary: "Citizen assessment and application support for PMAY-U.", icon: Home },
  { id: "airsewa", name: "AirSewa", category: "Civil Aviation", mode: "Apply Online", officialAuthority: "Ministry of Civil Aviation", officialUrl: "https://airsewa.gov.in/", summary: "File and track aviation passenger grievances.", icon: Shield },
  { id: "emigrate", name: "eMigrate", category: "Overseas Employment", mode: "Apply Online", officialAuthority: "Ministry of External Affairs", officialUrl: "https://emigrate.gov.in/", summary: "Overseas employment processing support for emigrant workers.", icon: Briefcase },
];

function defaultDocuments(mode: ServiceMode): Array<{ name: string; required: boolean }> {
  if (mode === "Info Only") {
    return [
      { name: "No mandatory document for information lookup", required: false },
      { name: "Application/reference ID (if tracking status)", required: false },
    ];
  }
  return [
    { name: "Identity proof (Aadhaar/PAN/Voter ID)", required: true },
    { name: "Address proof (as per official portal list)", required: true },
    { name: "Mobile number linked for OTP", required: true },
    { name: "Service-specific supporting document(s)", required: true },
  ];
}

function defaultSteps(seed: ServiceSeed): Array<{ number: number; title: string; description: string }> {
  return [
    { number: 1, title: "Open official portal", description: `Visit ${seed.officialUrl} and select ${seed.name}.` },
    { number: 2, title: "Verify eligibility", description: "Review scheme/service eligibility, scope, and required documents." },
    { number: 3, title: "Submit request", description: seed.mode === "Info Only" ? "Use available search/tracking/help tools on the portal." : "Complete online form and upload details as required." },
    { number: 4, title: "Track status", description: "Save acknowledgement/reference number and monitor updates on official portal." },
  ];
}

function defaultFaqs(seed: ServiceSeed): Array<{ question: string; answer: string }> {
  return [
    {
      question: `Where should I access ${seed.name}?`,
      answer: `Use the official ${seed.officialAuthority} portal: ${seed.officialUrl}. Avoid unofficial third-party links for submission or payment.`,
    },
    {
      question: `Is ${seed.name} fully online?`,
      answer: `Current mode: ${seed.mode}. For latest process changes, always confirm on the official portal before applying.`,
    },
  ];
}

function defaultDownloads(seed: ServiceSeed): Array<{ name: string; size: string; format: string }> {
  return [
    { name: `${seed.name} official guideline`, size: "Web", format: "URL" },
    { name: `${seed.name} help/document checklist`, size: "Web", format: "URL" },
  ];
}

function toService(seed: ServiceSeed): ServiceData {
  const theme = categoryTheme[seed.category] || {
    gradient: "from-blue-500 to-blue-700",
    status: "Available",
    defaultBadge: "Verified",
  };
  return {
    id: seed.id,
    icon: seed.icon,
    name: seed.name,
    description: seed.summary,
    category: seed.category,
    status: theme.status,
    badge: seed.badge || theme.defaultBadge,
    gradient: theme.gradient,
    processingTime: seed.processingTime || (seed.mode === "Info Only" ? "Instant" : "3-20 working days"),
    fee: seed.fee || (seed.mode === "Info Only" ? "No portal fee" : "As per official portal"),
    mode: seed.mode,
    officialAuthority: seed.officialAuthority,
    officialUrl: seed.officialUrl,
    lastVerifiedAt: LAST_VERIFIED_AT,
    validity: seed.validity,
    documents: defaultDocuments(seed.mode),
    steps: defaultSteps(seed),
    faqs: defaultFaqs(seed),
    downloads: defaultDownloads(seed),
  };
}

export const servicesData: Record<string, ServiceData> = Object.fromEntries(
  seeds.map((seed) => [seed.id, toService(seed)]),
) as Record<string, ServiceData>;

export const getServiceById = (id: string): ServiceData | undefined => servicesData[id];

export const getAllServices = (): ServiceData[] => Object.values(servicesData);

export const getAllFaqItems = () =>
  getAllServices().flatMap((service) =>
    service.faqs.map((faq) => ({
      serviceId: service.id,
      serviceName: service.name,
      category: service.category,
      question: faq.question,
      answer: faq.answer,
      officialUrl: service.officialUrl,
      officialAuthority: service.officialAuthority,
    })),
  );
