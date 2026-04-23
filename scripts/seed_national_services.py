"""Upsert a verified pan-India services catalog into warehouse tables.

Seeds:
- services
- faqs (2 per service)
- documents (1 profile document per service)
- content_chunks (1 chunk per service)

Optional:
- --embed : generate embeddings for FAQ/document/chunk text

Usage examples:
  python scripts/seed_national_services.py
  python scripts/seed_national_services.py --embed
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text

from core.database import SessionLocal
from core.models import ContentChunk, Document, FAQ, Service
from core.config import EMBEDDING_DIM


@dataclass(frozen=True)
class ServiceSeed:
    slug: str
    name: str
    category: str
    mode: str
    authority: str
    url: str
    summary: str


LAST_VERIFIED = "2026-03-10"

SEEDS: list[ServiceSeed] = [
    ServiceSeed(
        "passport_seva",
        "Passport Seva",
        "Identity & Travel Documents",
        "Apply Online",
        "Ministry of External Affairs (MEA), Government of India",
        "https://www.passportindia.gov.in/",
        "Apply for fresh passport or re-issue, book appointment, and track status through Passport Seva.",
    ),
    ServiceSeed(
        "uidai_aadhaar_services",
        "UIDAI Aadhaar Services",
        "Digital Identity",
        "Partially Online",
        "Unique Identification Authority of India (UIDAI)",
        "https://uidai.gov.in/",
        "Access Aadhaar service guidance, update flows, and resident support from UIDAI.",
    ),
    ServiceSeed(
        "myaadhaar_portal",
        "myAadhaar Portal",
        "Digital Identity",
        "Apply Online",
        "Unique Identification Authority of India (UIDAI)",
        "https://myaadhaar.uidai.gov.in/",
        "Use myAadhaar for downloads, appointments, and select Aadhaar self-service updates.",
    ),
    ServiceSeed(
        "income_tax_efiling",
        "Income Tax e-Filing Portal",
        "Taxation",
        "Apply Online",
        "Income Tax Department, Government of India",
        "https://www.incometax.gov.in/iec/foportal/",
        "File income tax returns, pay taxes, and manage compliance through the official portal.",
    ),
    ServiceSeed(
        "instant_epan_service",
        "Instant e-PAN",
        "Taxation",
        "Apply Online",
        "Income Tax Department, Government of India",
        "https://www.incometax.gov.in/",
        "Eligible citizens can generate e-PAN using paperless Aadhaar-based verification.",
    ),
    ServiceSeed(
        "gst_portal",
        "GST Portal",
        "Taxation",
        "Apply Online",
        "Goods and Services Tax Network (GSTN)",
        "https://www.gst.gov.in/",
        "GST portal supports registration, return filing, payments, and refund workflows.",
    ),
    ServiceSeed(
        "epfo_member_esewa",
        "EPFO Member e-Sewa",
        "Social Security & Provident Fund",
        "Apply Online",
        "Employees' Provident Fund Organisation (EPFO)",
        "https://unifiedportal-mem.epfindia.gov.in/memberinterface/",
        "Manage UAN profile, KYC, PF claims, and EPFO member services online.",
    ),
    ServiceSeed(
        "epfo_passbook_portal",
        "EPFO Passbook",
        "Social Security & Provident Fund",
        "Info Only",
        "Employees' Provident Fund Organisation (EPFO)",
        "https://passbook.epfindia.gov.in/MemberPassBook/Login",
        "View PF contribution passbook and account transaction history linked to UAN.",
    ),
    ServiceSeed(
        "jeevan_pramaan",
        "Jeevan Pramaan",
        "Pension",
        "Apply Online",
        "Department of Pension & Pensioners' Welfare",
        "https://jeevanpramaan.gov.in/",
        "Generate and submit digital life certificate for pension continuation.",
    ),
    ServiceSeed(
        "digilocker",
        "DigiLocker",
        "Digital Documents",
        "Apply Online",
        "Ministry of Electronics and Information Technology (MeitY)",
        "https://www.digilocker.gov.in/",
        "Fetch, store, and share official digital documents securely.",
    ),
    ServiceSeed(
        "umang",
        "UMANG",
        "Integrated Citizen Services",
        "Apply Online",
        "Ministry of Electronics and Information Technology (MeitY)",
        "https://web.umang.gov.in/",
        "Access multiple government services from a unified web and app interface.",
    ),
    ServiceSeed(
        "enps_national_pension_system",
        "eNPS",
        "Pension & Retirement",
        "Apply Online",
        "Pension Fund Regulatory and Development Authority (PFRDA)",
        "https://enps.nsdl.com/",
        "Open and manage National Pension System accounts online.",
    ),
    ServiceSeed(
        "pm_shram_yogi_maandhan",
        "PM-SYM",
        "Social Security & Pension",
        "Apply Online",
        "Ministry of Labour & Employment",
        "https://maandhan.in/",
        "Enroll unorganised workers in a contributory pension scheme.",
    ),
    ServiceSeed(
        "e_shram_portal",
        "e-Shram",
        "Labour & Welfare",
        "Apply Online",
        "Ministry of Labour & Employment",
        "https://eshram.gov.in/",
        "Register unorganised workers for national labour welfare access.",
    ),
    ServiceSeed(
        "national_career_service",
        "National Career Service",
        "Employment",
        "Apply Online",
        "Directorate General of Employment",
        "https://www.ncs.gov.in/",
        "Discover jobs, career counseling, and employment services.",
    ),
    ServiceSeed(
        "apprenticeship_india",
        "Apprenticeship India",
        "Skill Development & Employment",
        "Apply Online",
        "Ministry of Skill Development and Entrepreneurship",
        "https://www.apprenticeshipindia.gov.in/",
        "Find and apply for apprenticeship opportunities nationwide.",
    ),
    ServiceSeed(
        "pm_kisan",
        "PM-KISAN",
        "Agriculture & Farmer Support",
        "Apply Online",
        "Department of Agriculture & Farmers Welfare",
        "https://pmkisan.gov.in/",
        "Register and track PM-KISAN beneficiary and installment status.",
    ),
    ServiceSeed(
        "pmfby_crop_insurance",
        "PM Fasal Bima Yojana",
        "Agriculture Insurance",
        "Apply Online",
        "Ministry of Agriculture & Farmers Welfare",
        "https://pmfby.gov.in/",
        "Crop insurance enrollment and claim-related official information.",
    ),
    ServiceSeed(
        "enam_national_agri_market",
        "e-NAM",
        "Agriculture Market Access",
        "Apply Online",
        "Small Farmers' Agribusiness Consortium (SFAC)",
        "https://www.enam.gov.in/",
        "Digital agriculture market integration across mandis.",
    ),
    ServiceSeed(
        "national_scholarship_portal",
        "National Scholarship Portal",
        "Education & Scholarships",
        "Apply Online",
        "Government of India",
        "https://scholarships.gov.in/",
        "Apply for and track central scholarship schemes.",
    ),
    ServiceSeed(
        "swayam",
        "SWAYAM",
        "Education & Online Learning",
        "Apply Online",
        "Ministry of Education",
        "https://swayam.gov.in/",
        "National online learning portal for courses and certifications.",
    ),
    ServiceSeed(
        "diksha",
        "DIKSHA",
        "School Education",
        "Info Only",
        "Ministry of Education",
        "https://diksha.gov.in/",
        "Digital learning platform for teachers and students.",
    ),
    ServiceSeed(
        "academic_bank_of_credits",
        "Academic Bank of Credits",
        "Higher Education",
        "Apply Online",
        "Ministry of Education / UGC ecosystem",
        "https://www.abc.gov.in/",
        "Create and manage academic credit accounts.",
    ),
    ServiceSeed(
        "voters_service_portal",
        "Voters' Service Portal",
        "Elections",
        "Apply Online",
        "Election Commission of India",
        "https://voters.eci.gov.in/",
        "Voter registration and correction services from ECI.",
    ),
    ServiceSeed(
        "electoral_search_service",
        "Electoral Search",
        "Elections",
        "Info Only",
        "Election Commission of India",
        "https://electoralsearch.eci.gov.in/",
        "Search electoral roll and polling details.",
    ),
    ServiceSeed(
        "rti_online",
        "RTI Online",
        "Transparency & Governance",
        "Apply Online",
        "Department of Personnel and Training",
        "https://rtionline.gov.in/",
        "File RTI requests and first appeals online.",
    ),
    ServiceSeed(
        "cpgrams_pgportal",
        "CPGRAMS",
        "Public Grievance Redressal",
        "Apply Online",
        "DARPG",
        "https://pgportal.gov.in/",
        "Register and track grievances against central government entities.",
    ),
    ServiceSeed(
        "ecourts_services",
        "eCourts Services",
        "Judiciary",
        "Info Only",
        "eCommittee, Supreme Court of India",
        "https://ecourts.gov.in/",
        "Access case status, orders, and cause lists.",
    ),
    ServiceSeed(
        "india_code",
        "India Code",
        "Law & Legal Information",
        "Info Only",
        "Legislative Department",
        "https://www.indiacode.nic.in/",
        "Read consolidated central Acts and legal text.",
    ),
    ServiceSeed(
        "egazette",
        "e-Gazette",
        "Law & Notifications",
        "Info Only",
        "Department of Publication",
        "https://egazette.gov.in/",
        "Official Gazette notifications and publications.",
    ),
    ServiceSeed(
        "mygov_citizen_engagement",
        "MyGov",
        "Citizen Participation",
        "Apply Online",
        "Ministry of Electronics and Information Technology (MeitY)",
        "https://www.mygov.in/",
        "Participate in citizen consultation and government engagement.",
    ),
    ServiceSeed(
        "myscheme_discovery",
        "MyScheme",
        "Scheme Discovery",
        "Info Only",
        "Government of India",
        "https://www.myscheme.gov.in/",
        "Discover suitable government schemes by profile.",
    ),
    ServiceSeed(
        "national_portal_india",
        "National Portal of India",
        "Government Information",
        "Info Only",
        "National Informatics Centre (NIC)",
        "https://www.india.gov.in/",
        "Official national information gateway for government services.",
    ),
    ServiceSeed(
        "sarathi_driving_licence_services",
        "Sarathi (Driving Licence)",
        "Road Transport",
        "Apply Online",
        "Ministry of Road Transport and Highways",
        "https://sarathi.parivahan.gov.in/",
        "Apply and manage learner and driving licence workflows.",
    ),
    ServiceSeed(
        "vahan_vehicle_services",
        "Vahan (Vehicle Services)",
        "Road Transport",
        "Apply Online",
        "Ministry of Road Transport and Highways",
        "https://vahan.parivahan.gov.in/",
        "Vehicle registration and owner-related services.",
    ),
    ServiceSeed(
        "echallan_parivahan",
        "eChallan",
        "Road Transport Enforcement",
        "Partially Online",
        "Ministry of Road Transport and Highways",
        "https://echallan.parivahan.gov.in/",
        "Check and pay traffic challans online.",
    ),
    ServiceSeed(
        "national_permit_parivahan",
        "National Permit",
        "Road Transport",
        "Apply Online",
        "Ministry of Road Transport and Highways",
        "https://nationalpermit.parivahan.gov.in/",
        "National permit issuance and payment support for goods vehicles.",
    ),
    ServiceSeed(
        "parivahan_portal",
        "Parivahan Sewa",
        "Road Transport",
        "Info Only",
        "Ministry of Road Transport and Highways",
        "https://parivahan.gov.in/parivahan/",
        "Unified entry portal for transport services and links.",
    ),
    ServiceSeed(
        "ayushman_bharat_pmjay",
        "Ayushman Bharat PM-JAY",
        "Health Insurance",
        "Info Only",
        "National Health Authority",
        "https://pmjay.gov.in/",
        "PM-JAY scheme information, eligibility support, and beneficiary tools.",
    ),
    ServiceSeed(
        "abha_health_id",
        "ABHA (Health ID)",
        "Digital Health",
        "Apply Online",
        "National Health Authority",
        "https://abha.abdm.gov.in/",
        "Create and manage Ayushman Bharat Health Account.",
    ),
    ServiceSeed(
        "cowin",
        "CoWIN",
        "Public Health",
        "Apply Online",
        "Ministry of Health and Family Welfare",
        "https://www.cowin.gov.in/",
        "Vaccination appointment booking and certificate management.",
    ),
    ServiceSeed(
        "e_sanjeevani",
        "eSanjeevani",
        "Telemedicine",
        "Apply Online",
        "Ministry of Health and Family Welfare",
        "https://esanjeevani.in/",
        "Government telemedicine consultation service.",
    ),
    ServiceSeed(
        "ors_hospital_appointments",
        "ORS Hospital Appointments",
        "Healthcare Access",
        "Apply Online",
        "Ministry of Health and Family Welfare",
        "https://ors.gov.in/",
        "Book OPD appointments in participating hospitals.",
    ),
    ServiceSeed(
        "national_consumer_helpline",
        "National Consumer Helpline",
        "Consumer Protection",
        "Apply Online",
        "Department of Consumer Affairs",
        "https://consumerhelpline.gov.in/",
        "Register consumer complaints and escalation support.",
    ),
    ServiceSeed(
        "edaakhil_consumer_cases",
        "eDaakhil",
        "Consumer Justice",
        "Apply Online",
        "Department of Consumer Affairs",
        "https://edaakhil.nic.in/",
        "File consumer cases online before commissions.",
    ),
    ServiceSeed(
        "national_cyber_crime_reporting",
        "National Cyber Crime Reporting",
        "Public Safety",
        "Apply Online",
        "Ministry of Home Affairs",
        "https://cybercrime.gov.in/",
        "Report cyber offences, fraud, and abuse incidents.",
    ),
    ServiceSeed(
        "udid_disability_card",
        "UDID",
        "Disability Welfare",
        "Apply Online",
        "Department of Empowerment of Persons with Disabilities",
        "https://www.swavlambancard.gov.in/",
        "Apply for disability certificate and UDID card.",
    ),
    ServiceSeed(
        "pmay_urban_mis",
        "PMAY Urban",
        "Housing",
        "Apply Online",
        "Ministry of Housing and Urban Affairs",
        "https://pmaymis.gov.in/",
        "Citizen assessment and application support for PMAY-U.",
    ),
    ServiceSeed(
        "airsewa",
        "AirSewa",
        "Civil Aviation",
        "Apply Online",
        "Ministry of Civil Aviation",
        "https://airsewa.gov.in/",
        "Submit and track air passenger grievances.",
    ),
    ServiceSeed(
        "emigrate",
        "eMigrate",
        "Overseas Employment",
        "Apply Online",
        "Ministry of External Affairs",
        "https://emigrate.gov.in/",
        "Overseas worker migration process support and compliance workflows.",
    ),
]


def _build_faqs(seed: ServiceSeed) -> list[tuple[str, str]]:
    return [
        (
            f"Where should I access {seed.name}?",
            f"Use the official portal managed by {seed.authority}: {seed.url}. Avoid unofficial third-party submission links.",
        ),
        (
            f"Is {seed.name} fully online?",
            f"Current mode is {seed.mode}. Check the official portal for latest process and service-center requirements. Last verified: {LAST_VERIFIED}.",
        ),
    ]


def _build_profile_text(seed: ServiceSeed) -> str:
    return (
        f"Service: {seed.name}\n"
        f"Category: {seed.category}\n"
        f"Mode: {seed.mode}\n"
        f"Authority: {seed.authority}\n"
        f"Official URL: {seed.url}\n"
        f"Summary: {seed.summary}\n"
        f"Last verified: {LAST_VERIFIED}\n"
    )


def _get_embedding_engine(enabled: bool):
    if not enabled:
        return None
    from core.embeddings import get_embedding_engine

    return get_embedding_engine()


def _embed_text(engine, text: str, is_query: bool = False):
    if not engine:
        return None
    vector = engine.embed_text(text, is_query=is_query)
    if not vector:
        return None
    if len(vector) != EMBEDDING_DIM:
        return None
    return vector


def run(embed: bool = False) -> None:
    db = SessionLocal()
    emb_engine = _get_embedding_engine(embed)
    inserted = {"services": 0, "faqs": 0, "documents": 0, "chunks": 0}
    updated = {"services": 0, "faqs": 0, "documents": 0, "chunks": 0}

    try:
        db.execute(
            text(
                "SELECT setval('services_service_id_seq', COALESCE((SELECT MAX(service_id) FROM services), 1), true)"
            )
        )
        db.execute(
            text(
                "SELECT setval('faqs_faq_id_seq', COALESCE((SELECT MAX(faq_id) FROM faqs), 1), true)"
            )
        )
        db.execute(
            text(
                "SELECT setval('documents_doc_id_seq', COALESCE((SELECT MAX(doc_id) FROM documents), 1), true)"
            )
        )
        db.execute(
            text(
                "SELECT setval('content_chunks_chunk_id_seq', COALESCE((SELECT MAX(chunk_id) FROM content_chunks), 1), true)"
            )
        )
        db.flush()

        for seed in SEEDS:
            service = db.query(Service).filter(Service.name == seed.name).first()
            if service is None:
                service = Service(
                    name=seed.name,
                    category=seed.category,
                    description=f"{seed.summary}\nOfficial source: {seed.url}\nMode: {seed.mode}",
                    ministry=seed.authority,
                    is_active=True,
                    languages_supported=["en", "hi"],
                )
                db.add(service)
                db.flush()
                inserted["services"] += 1
            else:
                service.category = seed.category
                service.description = (
                    f"{seed.summary}\nOfficial source: {seed.url}\nMode: {seed.mode}"
                )
                service.ministry = seed.authority
                service.is_active = True
                updated["services"] += 1

            for question, answer in _build_faqs(seed):
                faq = (
                    db.query(FAQ)
                    .filter(
                        FAQ.service_id == service.service_id, FAQ.question == question
                    )
                    .first()
                )
                if faq is None:
                    faq = FAQ(
                        service_id=service.service_id,
                        question=question,
                        answer=answer,
                        category=seed.category,
                        language="en",
                    )
                    db.add(faq)
                    inserted["faqs"] += 1
                else:
                    faq.answer = answer
                    faq.category = seed.category
                    updated["faqs"] += 1

                if emb_engine:
                    faq.question_embedding = _embed_text(
                        emb_engine, faq.question, is_query=True
                    )
                    faq.answer_embedding = _embed_text(emb_engine, faq.answer)

            doc_name = f"{seed.name} official profile"
            doc = (
                db.query(Document)
                .filter(
                    Document.service_id == service.service_id, Document.name == doc_name
                )
                .first()
            )
            profile_text = _build_profile_text(seed)
            if doc is None:
                doc = Document(
                    service_id=service.service_id,
                    name=doc_name,
                    description=f"Official profile for {seed.name}",
                    document_type="service_profile",
                    is_mandatory=False,
                    copies_required=0,
                    language="en",
                    is_processed=True,
                    raw_content=profile_text,
                )
                db.add(doc)
                inserted["documents"] += 1
            else:
                doc.description = f"Official profile for {seed.name}"
                doc.raw_content = profile_text
                doc.document_type = "service_profile"
                doc.is_processed = True
                updated["documents"] += 1

            if emb_engine:
                doc.embedding = _embed_text(emb_engine, profile_text)

            chunk = (
                db.query(ContentChunk)
                .filter(
                    ContentChunk.service_id == service.service_id,
                    ContentChunk.chunk_type == "service_profile",
                    ContentChunk.chunk_index == 0,
                )
                .first()
            )
            if chunk is None:
                chunk = ContentChunk(
                    service_id=service.service_id,
                    chunk_text=profile_text,
                    chunk_index=0,
                    chunk_type="service_profile",
                    chunk_metadata={
                        "official_url": seed.url,
                        "official_authority": seed.authority,
                        "mode": seed.mode,
                        "verified_at": LAST_VERIFIED,
                        "slug": seed.slug,
                    },
                )
                db.add(chunk)
                inserted["chunks"] += 1
            else:
                chunk.chunk_text = profile_text
                chunk.chunk_metadata = {
                    "official_url": seed.url,
                    "official_authority": seed.authority,
                    "mode": seed.mode,
                    "verified_at": LAST_VERIFIED,
                    "slug": seed.slug,
                }
                updated["chunks"] += 1

            if emb_engine:
                chunk.embedding = _embed_text(emb_engine, profile_text)

        db.commit()

        print("Seed complete")
        print(f"Services total in seed: {len(SEEDS)}")
        print("Inserted:", inserted)
        print("Updated:", updated)
        print("Embeddings:", "enabled" if embed else "disabled")
    except Exception as exc:
        db.rollback()
        raise RuntimeError(f"Seeding failed: {exc}") from exc
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed national services catalog")
    parser.add_argument("--embed", action="store_true", help="Generate embeddings")
    args = parser.parse_args()
    run(embed=args.embed)


if __name__ == "__main__":
    main()
