"""
Seed additional FAQs to reach 100 total
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from core.models import FAQ, Service
from core.embeddings import get_transformer

# Additional FAQs for various government services
ADDITIONAL_FAQS = [
    # Income Tax - Additional
    ("What is Form 26AS?", "Form 26AS is an annual consolidated tax statement showing all tax-related information including TDS, TCS, advance tax, and self-assessment tax.", "income_tax", "forms"),
    ("How do I file ITR online for free?", "You can file ITR online for free using the Income Tax e-filing portal. Choose the appropriate ITR form based on your income sources.", "income_tax", "filing"),
    ("What is the penalty for late filing of ITR?", "The penalty for late filing is Rs. 5,000 if filed before December 31st, and Rs. 10,000 if filed after that date.", "income_tax", "penalties"),
    ("Can I revise my ITR multiple times?", "Yes, you can revise your ITR multiple times before the end of the assessment year or before completion of assessment.", "income_tax", "revision"),
    ("What is the difference between ITR-1 and ITR-2?", "ITR-1 is for individuals with salary income, while ITR-2 is for individuals with capital gains or income from house property.", "income_tax", "forms"),
    
    # GST - Additional
    ("What is the penalty for late GST filing?", "The penalty for late filing is Rs. 100 per day (Rs. 50 each for CGST and SGST) with a maximum of Rs. 5,000.", "gst", "penalties"),
    ("How do I apply for GST composition scheme?", "Apply for composition scheme by filing CMP-02 form on the GST portal before the start of the financial year.", "gst", "composition"),
    ("What is the difference between GSTR-1 and GSTR-3B?", "GSTR-1 contains outward supplies details, while GSTR-3B is a monthly summary return with tax payment.", "gst", "returns"),
    ("Can I claim ITC on capital goods?", "Yes, you can claim ITC on capital goods used for business purposes, subject to certain conditions.", "gst", "credit"),
    ("What is the time limit for GST registration?", "You must apply for GST registration within 30 days of becoming liable for registration.", "gst", "registration"),
    
    # Voter ID - Additional
    ("How do I check my polling station?", "Check your polling station details on the CEO website of your state or the National Voter Service Portal.", "voter_id", "polling"),
    ("What documents are required for voter registration?", "You need proof of identity, proof of address, and date of birth proof for voter registration.", "voter_id", "documents"),
    ("Can I vote if my name is not in the voter list?", "No, you cannot vote if your name is not in the electoral roll. You must register first.", "voter_id", "eligibility"),
    ("How do I update my photo in voter ID?", "Submit Form 8 with a new passport-size photo at your local electoral office or online portal.", "voter_id", "update"),
    ("What is the age limit for voter registration?", "You must be at least 18 years old on the qualifying date (January 1st of the year) to register as a voter.", "voter_id", "age"),
    
    # Ration Card - Additional
    ("How do I check my ration card status?", "Check your ration card status online on your state's food and civil supplies department website.", "ration_card", "status"),
    ("What is the validity of a ration card?", "Ration cards are generally valid for 5 years and need to be renewed before expiry.", "ration_card", "validity"),
    ("How do I add a new family member to my ration card?", "Submit an application with required documents and passport-size photos to your local ration office.", "ration_card", "addition"),
    ("What is the difference between APL and BPL cards?", "APL (Above Poverty Line) cards are for higher-income families, while BPL (Below Poverty Line) cards are for economically weaker families.", "ration_card", "types"),
    ("Can I use my ration card as identity proof?", "Yes, ration cards are accepted as valid identity proof for various government and private purposes.", "ration_card", "identity"),
    
    # Bank Account - New Category
    ("How do I open a Jan Dhan account?", "Visit any bank branch with Aadhaar card and fill out the Pradhan Mantri Jan Dhan Yojana account opening form.", "banking", "jan_dhan"),
    ("What is the minimum balance for savings account?", "Many banks offer zero balance savings accounts. For regular accounts, minimum balance varies from Rs. 1,000 to Rs. 10,000.", "banking", "minimum_balance"),
    ("How do I link my Aadhaar with bank account?", "Visit your bank branch with Aadhaar card or use net banking/mobile banking to link Aadhaar with your account.", "banking", "aadhaar_linking"),
    ("What is the interest rate on savings account?", "Savings account interest rates typically range from 2.5% to 7% per annum, depending on the bank and balance.", "banking", "interest"),
    ("How do I update my mobile number in bank account?", "Visit your bank branch with a valid ID proof and fill out the mobile number update form.", "banking", "mobile_update"),
    
    # Employment - New Category
    ("How do I register for employment in rural areas?", "Register at your local employment exchange or online through the National Career Service portal.", "employment", "registration"),
    ("What is the minimum wage in India?", "Minimum wage varies by state and skill level. It ranges from Rs. 176 to Rs. 450 per day across different states.", "employment", "minimum_wage"),
    ("How do I apply for unemployment benefits?", "Unemployment benefits are available through state employment exchanges. Check your state's employment department website.", "employment", "benefits"),
    ("What is the Mahatma Gandhi National Rural Employment Guarantee Act?", "MGNREGA guarantees 100 days of wage employment per year to rural households willing to do unskilled manual work.", "employment", "mgnrega"),
    ("How do I get a job card for MGNREGA?", "Apply for a job card at your Gram Panchayat office with required documents including Aadhaar and ration card.", "employment", "job_card"),
    
    # Healthcare - New Category
    ("How do I apply for Ayushman Bharat health card?", "Apply online on the PM-JAY portal or visit a Common Service Centre with Aadhaar and ration card.", "healthcare", "ayushman_bharat"),
    ("What is the coverage under Ayushman Bharat?", "Ayushman Bharat provides health coverage of up to Rs. 5 lakh per family per year for secondary and tertiary care.", "healthcare", "coverage"),
    ("How do I find empaneled hospitals?", "Search for empaneled hospitals on the PM-JAY website or call the helpline number 14555.", "healthcare", "hospitals"),
    ("What is the Janani Suraksha Yojana?", "JSY is a safe motherhood intervention providing cash assistance to pregnant women for institutional delivery.", "healthcare", "jsy"),
    ("How do I apply for disability certificate?", "Apply at your district medical board with medical reports and photographs. The certificate is valid for 5 years.", "healthcare", "disability"),
    
    # Education - New Category
    ("How do I apply for scholarships online?", "Apply for various government scholarships through the National Scholarship Portal (scholarships.gov.in).", "education", "scholarships"),
    ("What is the Right to Education Act?", "RTE Act ensures free and compulsory education for children aged 6-14 years in government and aided schools.", "education", "rte"),
    ("How do I get admission under RTE quota?", "Apply for admission under RTE quota at private schools through your state's education department portal.", "education", "admission"),
    ("What is the Mid-Day Meal Scheme?", "MDMS provides free lunch to students in government and government-aided schools to improve nutritional status.", "education", "mid_day_meal"),
    ("How do I apply for student loan?", "Apply for education loans at banks or through the Vidya Lakshmi portal for higher education financing.", "education", "student_loan"),
    
    # Agriculture - New Category
    ("How do I apply for PM Kisan scheme?", "Apply for PM Kisan benefits at your local agriculture office or online through the PM Kisan portal.", "agriculture", "pm_kisan"),
    ("What is the amount under PM Kisan?", "PM Kisan provides Rs. 6,000 per year in three equal installments of Rs. 2,000 each to farmer families.", "agriculture", "amount"),
    ("How do I get soil health card?", "Apply for soil health card at your local agriculture office or Krishi Vigyan Kendra.", "agriculture", "soil_card"),
    ("What is the Pradhan Mantri Fasal Bima Yojana?", "PMFBY is a crop insurance scheme providing financial support to farmers in case of crop failure.", "agriculture", "crop_insurance"),
    ("How do I apply for KCC (Kisan Credit Card)?", "Apply for KCC at your bank with land documents, Aadhaar card, and passport-size photos.", "agriculture", "kcc"),
    
    # Housing - New Category
    ("How do I apply for PM Awas Yojana?", "Apply for PMAY benefits online through the PMAY portal or visit your local municipal office.", "housing", "pmay"),
    ("What is the subsidy under PMAY?", "PMAY provides interest subsidy of up to Rs. 2.67 lakh for home loans under the Credit Linked Subsidy Scheme.", "housing", "subsidy"),
    ("How do I check my PMAY application status?", "Check your PMAY application status online using your application number on the PMAY portal.", "housing", "status"),
    ("What is the Pradhan Mantri Awas Yojana Urban?", "PMAY-U aims to provide affordable housing to urban poor through various schemes and subsidies.", "housing", "urban"),
    ("How do I get a house site patta?", "Apply for house site patta at your local revenue office with required documents and application form.", "housing", "patta"),
]

def seed_more_faqs():
    """Seed additional FAQs to reach 100 total"""
    db = SessionLocal()
    try:
        # Get embedding model
        print("Loading embedding model...")
        model = get_transformer()
        
        # Get existing FAQ count
        existing_count = db.query(FAQ).count()
        print(f"Current FAQ count: {existing_count}")
        
        if existing_count >= 100:
            print("Already have 100+ FAQs. No seeding needed.")
            return
        
        # Get a default service for FAQs without specific service
        default_service = db.query(Service).first()
        
        added_count = 0
        for question, answer, service_name, category in ADDITIONAL_FAQS:
            # Check if FAQ already exists
            existing = db.query(FAQ).filter(FAQ.question == question).first()
            if existing:
                continue
            
            # Find service by name
            service = db.query(Service).filter(Service.name.ilike(f"%{service_name}%")).first()
            if not service:
                service = default_service
            
            # Generate embeddings
            question_embedding = model.encode(question).tolist()
            answer_embedding = model.encode(answer).tolist()
            
            # Create FAQ
            faq = FAQ(
                question=question,
                answer=answer,
                category=category,
                service_id=service.service_id if service else None,
                question_embedding=question_embedding,
                answer_embedding=answer_embedding,
                language="en"
            )
            
            db.add(faq)
            added_count += 1
            
            if (existing_count + added_count) >= 100:
                break
        
        db.commit()
        
        final_count = db.query(FAQ).count()
        print(f"\n✅ Additional seeding complete!")
        print(f"   Added: {added_count} FAQs")
        print(f"   Total: {final_count} FAQs")
        print(f"   Status: {'✅ Target reached!' if final_count >= 100 else f'⚠️  Need {100 - final_count} more'}")
        
    except Exception as e:
        print(f"❌ Error seeding additional FAQs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_more_faqs()
