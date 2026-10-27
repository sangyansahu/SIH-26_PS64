import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import (
    db, Bureau, User, Institution, Complaint,
    CaseAction, CaseLink, Notification, AuditEvent
)

def seed_database(reset=False):
    app = create_app()
    with app.app_context():
        print("Ensuring database tables exist...")
        db.create_all()

        admin_exists = db.session.query(User).filter_by(email="admin@aicte.gov.in").first()

        if reset:
            print("Resetting all existing complaints, case links, actions, and notifications...")
            db.session.query(Notification).delete()
            db.session.query(CaseLink).delete()
            db.session.query(CaseAction).delete()
            db.session.query(Complaint).delete()
            db.session.commit()
            print("Complaints register cleared.")
        elif admin_exists:
            print("Database already contains seed data. Use --reset to re-seed complaints.")
            return

        # 1. Bureaus and Cells
        bureaus_data = [
            ("PGRC", "Public Grievance Redressal Cell", "Citizen, student, and faculty grievances regarding unfair practices, unauthorized fees, and service rules."),
            ("AB", "Approval Bureau", "Regulatory approvals, Extension of Approval (EoA), land and infrastructure compliance, and sanctioned intake."),
            ("RPC", "Ragging Prevention Cell", "Monitoring anti-ragging compliance, emergency helpline referrals, and FIR tracking under statutory regulations."),
            ("PAPB", "Policy & Academic Planning Bureau", "Curriculum norms, faculty minimum qualification standards, and mandatory academic credit disputes."),
            ("FAB", "Finance & Accounts Bureau", "Grant disbursements, research lab grants, student scholarship delivery, and financial audit objections."),
        ]

        bureau_map = {}
        for code, name, desc in bureaus_data:
            b = db.session.query(Bureau).filter_by(code=code).first()
            if not b:
                b = Bureau(code=code, name=name, description=desc)
                db.session.add(b)
                db.session.flush()
            bureau_map[code] = b

        # 2. Portal Users across 3 Levels
        user_specs = [
            ("Dr. Rajiv Sharma", "admin@aicte.gov.in", "admin", "SYSTEM_ADMIN", None, "Chief System Administrator & Director (IT)"),
            ("Grievance Redressal Industry Desk", "industry@aicte.gov.in", "industry", "INDUSTRY", bureau_map["PGRC"].id, "Senior Grievance Coordinator"),
            ("Smt. Ananya Sen", "officer.pgrc@aicte.gov.in", "Officer@12345", "INDUSTRY", bureau_map["PGRC"].id, "Senior Grievance Officer (PGRC)"),
            ("Shri Vikramaditya Rao", "officer.ab@aicte.gov.in", "Officer@12345", "INDUSTRY", bureau_map["AB"].id, "Joint Director (Approval Bureau)"),
            ("Dr. Meenakshi Sundaram", "officer.rpc@aicte.gov.in", "Officer@12345", "INDUSTRY", bureau_map["RPC"].id, "Anti-Ragging Coordination Officer"),
            ("Pooja Sharma (Student Complainant)", "user@aicte.gov.in", "user", "USER", None, "Citizen Complainant"),
        ]

        user_map = {}
        for name, email, pwd, role, bureau_id, designation in user_specs:
            u = db.session.query(User).filter_by(email=email).first()
            if not u:
                u = User(name=name, email=email, role=role, bureau_id=bureau_id, designation=designation)
                u.set_password(pwd)
                db.session.add(u)
                db.session.flush()
            user_map[email] = u

        admin = user_map["admin@aicte.gov.in"]
        industry_desk = user_map["industry@aicte.gov.in"]
        officer_pgrc = user_map["officer.pgrc@aicte.gov.in"]
        officer_ab = user_map["officer.ab@aicte.gov.in"]
        officer_rpc = user_map["officer.rpc@aicte.gov.in"]
        user_citizen = user_map["user@aicte.gov.in"]

        # 3. Institutions
        inst_specs = [
            ("1-10293847", "Apex Institute of Technology and Management", '["Apex Inst. of Technology", "Apex Tech Bangalore", "AITM Bangalore"]', "Engineering & Technology", "Karnataka", "Bengaluru Urban", "Survey No. 42/1, Electronic City Phase 1", "560100", "https://www.apextech-sample.edu.in"),
            ("1-48201948", "National Institute of Technical Excellence", '["NITE Pune", "National Tech Pune"]', "Engineering & Technology", "Maharashtra", "Pune", "Hinjawadi Infotech Park, Phase 2", "411057", "https://www.nite-pune-sample.edu.in"),
            ("1-77392014", "Kalinga Academy of Pharmaceutical Sciences", '["KAPS Bhubaneswar", "Kalinga Pharmacy"]', "Pharmacy", "Odisha", "Khurda", "Plot 104, Chandaka Industrial Estate, Bhubaneswar", "751024", "https://www.kalinga-pharm-sample.edu.in"),
            ("1-33920194", "Delhi Institute of Advanced Polytechnic Studies", '["DIAPS Delhi", "Delhi Adv Poly"]', "Polytechnic", "Delhi", "South West Delhi", "Institutional Area, Sector 9, Dwarka", "110077", "https://www.diaps-delhi-sample.edu.in"),
            ("1-99201842", "Saraswati College of Engineering and Architecture", '["SCEA Lucknow", "Saraswati Engg Lucknow"]', "Engineering & Technology", "Uttar Pradesh", "Lucknow", "Faizabad Road, Chinhat, Lucknow", "226028", "https://www.scea-lucknow-sample.edu.in"),
            ("1-55829103", "St. Xavier Institute of Business Management", '["SXIBM Chennai", "St Xavier Management Chennai"]', "Management", "Tamil Nadu", "Chennai", "Mount Road, Guindy, Chennai", "600032", "https://www.sxibm-chennai-sample.edu.in"),
        ]

        inst_map = {}
        for code, name, aliases, itype, state, district, addr, pin, web in inst_specs:
            inst = db.session.query(Institution).filter_by(institution_code=code).first()
            if not inst:
                inst = Institution(institution_code=code, name=name, aliases=aliases, institution_type=itype, state=state, district=district, address=addr, pincode=pin, website=web)
                db.session.add(inst)
                db.session.flush()
            inst_map[code] = inst

        print("Seeding Bureau-Specific Complaints...")
        now = datetime.now(timezone.utc)

        # ------------------------------------------------------------------
        # BUREAU 1: Public Grievance Redressal Cell (PGRC)
        # ------------------------------------------------------------------
        c1 = Complaint(
            case_number="AICTE-26-PGRC-0101",
            ticket_number="AICTE-2026-PG0101",
            external_reference="CPGRAMS/2026/004189",
            institution_id=inst_map["1-10293847"].id,
            category="Fee Overcharging / Capitation",
            subject="Demand for unauthorized development fee during admission counselling",
            description="The complainant states that during admission counselling for B.Tech Computer Science, the college administration insisted on an unreceipted cash payment of Rs 1,50,000 titled 'Campus Development Contribution' over and above the approved government quota fee schedule.",
            complainant_name=user_citizen.name,
            complainant_email=user_citizen.email,
            complainant_mobile="+91 98450 11223",
            created_by_user_id=user_citizen.id,
            source="Public Portal",
            receiving_bureau_id=bureau_map["PGRC"].id,
            current_bureau_id=bureau_map["PGRC"].id,
            assigned_user_id=officer_pgrc.id,
            priority="Critical",
            status="Action Required",
            received_at=now - timedelta(days=18),
            due_at=now - timedelta(days=2),  # Overdue
            last_action_at=now - timedelta(days=3),
            created_at=now - timedelta(days=18),
            next_action="Conduct statutory hearing with Chairman and Registrar of the institution",
            next_action_due=now + timedelta(days=3),
            next_action_assignee="Smt. Ananya Sen (Senior Grievance Officer)",
            query_to_complainant="Provide bank statement extract and any formal written demand letter received from the admissions office.",
            complainant_response="Submitted bank withdrawal slip and photograph of the payment slip handed over at counter 4.",
            coordination_notes="Cross-referenced with Approval Bureau case AICTE-26-AB-0104. Institution appears to be extracting excess fees to cover unapproved supernumerary seats.",
        )

        c2 = Complaint(
            case_number="AICTE-26-PGRC-0102",
            ticket_number="AICTE-2026-PG0102",
            external_reference="DARPG/E/2026/008821",
            institution_id=inst_map["1-48201948"].id,
            category="Withholding of Certificates",
            subject="Withholding of original degree certificate and migration certificate on graduation",
            description="The complainant completed B.Tech Mechanical Engineering in July 2025. The college administration refuses to release the original Class 12 marksheet, transfer certificate, and degree certificate citing disputed hostel maintenance dues of Rs 18,000.",
            complainant_name=user_citizen.name,
            complainant_email=user_citizen.email,
            complainant_mobile="+91 98450 11223",
            created_by_user_id=user_citizen.id,
            source="Public Portal",
            receiving_bureau_id=bureau_map["PGRC"].id,
            current_bureau_id=bureau_map["PGRC"].id,
            assigned_user_id=officer_pgrc.id,
            priority="High",
            status="Awaiting Response",
            received_at=now - timedelta(days=12),
            due_at=now + timedelta(days=3),
            last_action_at=now - timedelta(days=2),
            created_at=now - timedelta(days=12),
            next_action="Review complainant submission and issue Section 10(1) directive",
            next_action_due=now + timedelta(days=5),
            next_action_assignee="Smt. Ananya Sen",
            query_to_complainant="Please furnish a scanned copy of your final semester no-dues clearance slip and student roll number to verify hostel fee records.",
            complainant_response="Uploaded signed no-dues clearance slip dated 14 May 2026 with student roll number ME-2021-044.",
        )

        c3 = Complaint(
            case_number="AICTE-26-PGRC-0103",
            ticket_number="AICTE-2026-PG0103",
            institution_id=inst_map["1-99201842"].id,
            category="Faculty Service Grievance",
            subject="Non-payment of mandatory salary arrears as per AICTE 7th CPC notifications",
            description="Faculty members representation regarding non-disbursement of approved salaries for five months and arbitrary deduction of Provident Fund contributions without deposit into EPFO accounts.",
            complainant_name="Dr. Alok Verma (Assistant Professor)",
            complainant_email="alok.verma@faculty-forum.org",
            complainant_mobile="+91 94150 99881",
            source="Official Representation",
            receiving_bureau_id=bureau_map["PGRC"].id,
            current_bureau_id=bureau_map["PGRC"].id,
            assigned_user_id=industry_desk.id,
            priority="Medium",
            status="Under Review",
            received_at=now - timedelta(days=8),
            due_at=now + timedelta(days=7),
            last_action_at=now - timedelta(days=1),
            created_at=now - timedelta(days=8),
            next_action="Examine EPFO electronic challan receipts submitted by institution registrar",
            next_action_due=now + timedelta(days=7),
            next_action_assignee="Senior Grievance Coordinator",
        )

        # ------------------------------------------------------------------
        # BUREAU 2: Approval Bureau (AB)
        # ------------------------------------------------------------------
        c4 = Complaint(
            case_number="AICTE-26-AB-0104",
            ticket_number="AICTE-2026-AB0104",
            external_reference="CPGRAMS/2026/004189",
            institution_id=inst_map["1-10293847"].id,
            category="Admission Irregularity / Excess Intake",
            subject="Admissions conducted in excess of sanctioned intake in B.Tech Computer Science",
            description="The sanctioned intake for B.Tech Computer Science is 180 seats as per EoA 2025-26. State admission portal data and physical roll lists indicate that 234 candidates were enrolled, exceeding statutory limits by 54 seats without Council approval.",
            complainant_name="State Admission Monitoring Committee",
            complainant_email="kea-admissions@karnataka.gov.in",
            source="State Directorate",
            receiving_bureau_id=bureau_map["AB"].id,
            current_bureau_id=bureau_map["AB"].id,
            assigned_user_id=officer_ab.id,
            priority="Critical",
            status="Under Review",
            received_at=now - timedelta(days=14),
            due_at=now + timedelta(days=2),
            last_action_at=now - timedelta(days=3),
            created_at=now - timedelta(days=14),
            next_action="Issue formal show cause notice under Approval Process Handbook Chapter IV",
            next_action_due=now + timedelta(days=2),
            next_action_assignee="Shri Vikramaditya Rao (Joint Director)",
            coordination_notes="Primary linked case to AICTE-26-PGRC-0101. Overlap confirmed. Excess students were subjected to unauthorized fee extraction.",
        )

        c5 = Complaint(
            case_number="AICTE-26-AB-0105",
            ticket_number="AICTE-2026-AB0105",
            institution_id=inst_map["1-33920194"].id,
            category="Unapproved Extension Center",
            subject="Operation of unapproved off-campus study center at Rohini Sector 16",
            description="Complaint filed regarding an unapproved teaching facility operating under the institution brand name offering 3-year diploma courses without land, fire safety, or AICTE regulatory approvals.",
            complainant_name="Technical Education Vigilance Wing",
            complainant_email="dte.delhi@gov.in",
            source="Inter-Departmental Referral",
            receiving_bureau_id=bureau_map["AB"].id,
            current_bureau_id=bureau_map["AB"].id,
            assigned_user_id=officer_ab.id,
            priority="High",
            status="Action Required",
            received_at=now - timedelta(days=10),
            due_at=now + timedelta(days=4),
            last_action_at=now - timedelta(days=2),
            created_at=now - timedelta(days=10),
            next_action="Depute surprise inspection committee from Northern Regional Office Kanpur",
            next_action_due=now + timedelta(days=4),
            next_action_assignee="Shri Vikramaditya Rao",
        )

        c6 = Complaint(
            case_number="AICTE-26-AB-0106",
            ticket_number="AICTE-2026-AB0106",
            institution_id=inst_map["1-77392014"].id,
            category="Infrastructure Compliance",
            subject="Verification of built-up area and pharmacy laboratory equipment compliance",
            description="Annual scrutiny inspection indicated shortage of instructional built-up area by 18 percent and non-availability of working HPLC apparatus for M.Pharm pharmacology labs.",
            complainant_name="Regional Inspection Squad",
            complainant_email="ero.kolkata@aicte.gov.in",
            source="Inspection Report",
            receiving_bureau_id=bureau_map["AB"].id,
            current_bureau_id=bureau_map["AB"].id,
            assigned_user_id=officer_ab.id,
            priority="Medium",
            status="Disposed",
            received_at=now - timedelta(days=25),
            due_at=now - timedelta(days=10),
            disposed_at=now - timedelta(days=4),
            last_action_at=now - timedelta(days=4),
            created_at=now - timedelta(days=25),
            resolution_summary="Institution submitted geo-tagged video verification and procurement invoices for lab equipment. Deficiency cleared with warning issued on 22 October 2026.",
        )

        # ------------------------------------------------------------------
        # BUREAU 3: Ragging Prevention Cell (RPC)
        # ------------------------------------------------------------------
        c7 = Complaint(
            case_number="AICTE-26-RPC-0107",
            ticket_number="AICTE-2026-RP0107",
            external_reference="UGC-NERH/2026/09214",
            institution_id=inst_map["1-48201948"].id,
            category="Anti-Ragging Violation",
            subject="Hostel ragging incident reported on 1st year engineering students",
            description="Emergency referral from National Anti-Ragging Helpline. First year hostel residents subjected to physical harassment and intimidation by senior students in Hostel Block C. Institutional squad failed to file police report within 24 hours.",
            complainant_name="Anti-Ragging Monitoring Agency Helpline",
            complainant_email="helpline@antiragging.in",
            source="National Helpline",
            receiving_bureau_id=bureau_map["RPC"].id,
            current_bureau_id=bureau_map["RPC"].id,
            assigned_user_id=officer_rpc.id,
            priority="Critical",
            status="Escalated",
            is_escalated=True,
            escalation_reason="Statutory 24-hour compliance breached by institution. Police FIR status pending.",
            received_at=now - timedelta(days=24),
            due_at=now - timedelta(days=4),  # Overdue
            last_action_at=now - timedelta(days=4),
            created_at=now - timedelta(days=24),
            next_action="Summons issued to Principal and Hostel Warden to appear before National Monitoring Committee",
            next_action_due=now - timedelta(days=2),
            next_action_assignee="Dr. Meenakshi Sundaram (Anti-Ragging Officer)",
        )

        c8 = Complaint(
            case_number="AICTE-26-RPC-0108",
            ticket_number="AICTE-2026-RP0108",
            institution_id=inst_map["1-99201842"].id,
            category="Anti-Ragging Committee Non-Compliance",
            subject="Non-constitution of mandatory Anti-Ragging Committee and Squad for academic year 2026-27",
            description="Institution failed to upload mandatory anti-ragging undertaking affidavits and details of Anti-Ragging Squad members on the national portal prior to commencement of classes.",
            complainant_name="Student Welfare Council",
            complainant_email="swc.up@nic.in",
            source="State Council",
            receiving_bureau_id=bureau_map["RPC"].id,
            current_bureau_id=bureau_map["RPC"].id,
            assigned_user_id=officer_rpc.id,
            priority="Medium",
            status="Received",
            received_at=now - timedelta(days=5),
            due_at=now + timedelta(days=10),
            last_action_at=now - timedelta(days=5),
            created_at=now - timedelta(days=5),
            next_action="Issue automated regulatory reminder for compliance submission within 7 days",
            next_action_due=now + timedelta(days=6),
            next_action_assignee="Dr. Meenakshi Sundaram",
        )

        # ------------------------------------------------------------------
        # BUREAU 4: Policy & Academic Planning Bureau (PAPB)
        # ------------------------------------------------------------------
        c9 = Complaint(
            case_number="AICTE-26-PAPB-0109",
            ticket_number="AICTE-2026-PA0109",
            institution_id=inst_map["1-55829103"].id,
            category="Faculty Qualifications Non-Compliance",
            subject="Recruitment of teaching faculty without mandatory NET/SLET or PhD qualifications",
            description="Audit of teaching staff profiles revealed that 8 out of 14 appointed Assistant Professors in the MBA department do not possess UGC-NET qualification or PhD as prescribed in AICTE Regulations 2019.",
            complainant_name="Academic Standards Forum",
            complainant_email="academic.standards@tn-education.org",
            source="Public Representation",
            receiving_bureau_id=bureau_map["PAPB"].id,
            current_bureau_id=bureau_map["PAPB"].id,
            assigned_user_id=industry_desk.id,
            priority="High",
            status="Under Review",
            received_at=now - timedelta(days=11),
            due_at=now + timedelta(days=5),
            last_action_at=now - timedelta(days=2),
            created_at=now - timedelta(days=11),
            next_action="Verify faculty service books and appointment orders against statutory cadred norms",
            next_action_due=now + timedelta(days=5),
            next_action_assignee="Senior Grievance Coordinator",
        )

        c10 = Complaint(
            case_number="AICTE-26-PAPB-0110",
            ticket_number="AICTE-2026-PA0110",
            institution_id=inst_map["1-77392014"].id,
            category="Internship & Credit Transfer",
            subject="Denial of mandatory industrial internship credits for final year B.Pharm batch",
            description="Students completed 8-week hospital and industrial training in accredited units, but college administration refused to award mandated academic credits required for registration with State Pharmacy Council.",
            complainant_name="Final Year Student Delegation",
            complainant_email="student.rep.kaps@gmail.com",
            source="Student Representation",
            receiving_bureau_id=bureau_map["PAPB"].id,
            current_bureau_id=bureau_map["PAPB"].id,
            assigned_user_id=industry_desk.id,
            priority="Low",
            status="Received",
            received_at=now - timedelta(days=4),
            due_at=now + timedelta(days=12),
            last_action_at=now - timedelta(days=4),
            created_at=now - timedelta(days=4),
            next_action="Direct Dean of Academics to convene Board of Studies for credit validation",
            next_action_due=now + timedelta(days=10),
            next_action_assignee="Senior Grievance Coordinator",
        )

        # ------------------------------------------------------------------
        # BUREAU 5: Finance & Accounts Bureau (FAB)
        # ------------------------------------------------------------------
        c11 = Complaint(
            case_number="AICTE-26-FAB-0111",
            ticket_number="AICTE-2026-FA0111",
            institution_id=inst_map["1-10293847"].id,
            category="Scholarship Misappropriation / Delay",
            subject="Delay and unauthorized retention of AICTE PRAGATI scholarship disbursements",
            description="First year girl students enrolled under PRAGATI scholarship scheme report that direct financial assistance received from the ministry was withheld by the accounts office under the pretext of hostel security deposit adjustment.",
            complainant_name=user_citizen.name,
            complainant_email=user_citizen.email,
            complainant_mobile="+91 98450 11223",
            created_by_user_id=user_citizen.id,
            source="Public Portal",
            receiving_bureau_id=bureau_map["FAB"].id,
            current_bureau_id=bureau_map["FAB"].id,
            assigned_user_id=industry_desk.id,
            priority="High",
            status="Under Review",
            received_at=now - timedelta(days=7),
            due_at=now + timedelta(days=8),
            last_action_at=now - timedelta(days=2),
            created_at=now - timedelta(days=7),
            next_action="Obtain bank ledger reconciliation from Canara Bank nodal branch",
            next_action_due=now + timedelta(days=4),
            next_action_assignee="Senior Grievance Coordinator",
            coordination_notes="Institutional financial overlap with AICTE-26-PGRC-0101 and AICTE-26-AB-0104 at Apex Institute.",
        )

        c12 = Complaint(
            case_number="AICTE-26-FAB-0112",
            ticket_number="AICTE-2026-FA0112",
            institution_id=inst_map["1-48201948"].id,
            category="Grant Misappropriation",
            subject="Non-utilization and unverified diversion of MODROBS lab modernization grant",
            description="A capital grant of Rs 14,80,000 sanctioned under MODROBS scheme in 2024 for IoT research laboratory has not been accounted for. No utilization certificate (UC) or expenditure statement has been submitted within the statutory 18-month period.",
            complainant_name="AICTE Finance Audit Inspection Cell",
            complainant_email="audit.fab@aicte.gov.in",
            source="Statutory Audit",
            receiving_bureau_id=bureau_map["FAB"].id,
            current_bureau_id=bureau_map["FAB"].id,
            assigned_user_id=industry_desk.id,
            priority="Critical",
            status="Escalated",
            is_escalated=True,
            escalation_reason="Statutory 18-month UC submission deadline passed without submission.",
            received_at=now - timedelta(days=28),
            due_at=now - timedelta(days=6),  # Overdue
            last_action_at=now - timedelta(days=6),
            created_at=now - timedelta(days=28),
            next_action="Issue recovery notice with 10 percent penal interest under General Financial Rules",
            next_action_due=now - timedelta(days=5),
            next_action_assignee="Senior Grievance Coordinator",
        )

        # ------------------------------------------------------------------
        # Complainant Resolved History Case (for Pooja Sharma)
        # ------------------------------------------------------------------
        c13 = Complaint(
            case_number="AICTE-26-PGRC-0113",
            ticket_number="AICTE-2026-PG0113",
            institution_id=inst_map["1-10293847"].id,
            category="Exam / Marksheet Correction",
            subject="Correction of typographical error in official degree transcript",
            description="The complainant requested correction of mother's name spelling on the semester grade transcript which was incorrectly printed by the evaluation cell.",
            complainant_name=user_citizen.name,
            complainant_email=user_citizen.email,
            complainant_mobile="+91 98450 11223",
            created_by_user_id=user_citizen.id,
            source="Public Portal",
            receiving_bureau_id=bureau_map["PGRC"].id,
            current_bureau_id=bureau_map["PGRC"].id,
            assigned_user_id=officer_pgrc.id,
            priority="Low",
            status="Disposed",
            received_at=now - timedelta(days=35),
            due_at=now - timedelta(days=15),
            disposed_at=now - timedelta(days=15),
            last_action_at=now - timedelta(days=15),
            created_at=now - timedelta(days=35),
            resolution_summary="Institution Controller of Examinations reissued the corrected transcript with verified identity documents on 12 October 2026.",
        )

        all_complaints = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13]
        db.session.add_all(all_complaints)
        db.session.flush()

        print("Seeding Case Action History...")
        actions = [
            # Case 1 timeline
            CaseAction(complaint_id=c1.id, action_type="Submitted", description="Grievance registered through public portal with supporting cash slip.", performed_by_id=user_citizen.id, created_at=now - timedelta(days=18)),
            CaseAction(complaint_id=c1.id, action_type="Under Review", description="Assigned to Senior Grievance Officer PGRC for preliminary scrutiny.", performed_by_id=industry_desk.id, created_at=now - timedelta(days=15)),
            CaseAction(complaint_id=c1.id, action_type="Action Required", description="Show cause notice issued to Chairman of Apex Institute. Statutory hearing scheduled.", performed_by_id=officer_pgrc.id, created_at=now - timedelta(days=3)),

            # Case 2 timeline
            CaseAction(complaint_id=c2.id, action_type="Submitted", description="Grievance filed regarding withholding of degree certificates.", performed_by_id=user_citizen.id, created_at=now - timedelta(days=12)),
            CaseAction(complaint_id=c2.id, action_type="Awaiting Response", description="Clarification sought from complainant regarding clearance of hostel dues.", performed_by_id=officer_pgrc.id, created_at=now - timedelta(days=5)),
            CaseAction(complaint_id=c2.id, action_type="Information Provided", description="Complainant uploaded signed no-dues receipt dated 14 May 2026.", performed_by_id=user_citizen.id, created_at=now - timedelta(days=2)),

            # Case 4 timeline
            CaseAction(complaint_id=c4.id, action_type="Intake", description="Intake received from State Admission Committee regarding excess student intake.", performed_by_id=officer_ab.id, created_at=now - timedelta(days=14)),
            CaseAction(complaint_id=c4.id, action_type="Under Review", description="Discrepancy confirmed between approved EoA intake (180) and enrolled count (234).", performed_by_id=officer_ab.id, created_at=now - timedelta(days=6)),

            # Case 6 timeline
            CaseAction(complaint_id=c6.id, action_type="Received", description="Inspection report logged with built-up area and equipment deficiency.", performed_by_id=officer_ab.id, created_at=now - timedelta(days=25)),
            CaseAction(complaint_id=c6.id, action_type="Disposed", description="Deficiencies cleared on verification of geo-tagged procurement records. Warning recorded.", performed_by_id=officer_ab.id, created_at=now - timedelta(days=4)),

            # Case 7 timeline
            CaseAction(complaint_id=c7.id, action_type="Emergency Referral", description="National Anti-Ragging Helpline emergency dossier received.", performed_by_id=officer_rpc.id, created_at=now - timedelta(days=24)),
            CaseAction(complaint_id=c7.id, action_type="Escalated", description="Institution breached 24-hour statutory FIR reporting deadline. Escalated to Bureau Head.", performed_by_id=officer_rpc.id, created_at=now - timedelta(days=10)),

            # Case 11 timeline
            CaseAction(complaint_id=c11.id, action_type="Submitted", description="Scholarship grievance registered by student beneficiary.", performed_by_id=user_citizen.id, created_at=now - timedelta(days=7)),
            CaseAction(complaint_id=c11.id, action_type="Under Review", description="Assigned to Finance Bureau coordinator for Canara Bank DBT reconciliation.", performed_by_id=industry_desk.id, created_at=now - timedelta(days=2)),

            # Case 13 timeline
            CaseAction(complaint_id=c13.id, action_type="Submitted", description="Transcript correction request submitted with identity proofs.", performed_by_id=user_citizen.id, created_at=now - timedelta(days=35)),
            CaseAction(complaint_id=c13.id, action_type="Disposed", description="Corrected transcript issued by examination cell. Case closed.", performed_by_id=officer_pgrc.id, created_at=now - timedelta(days=15)),
        ]
        db.session.add_all(actions)

        print("Seeding Cross-Bureau Overlap Links...")
        links = [
            # Link 1: PGRC-0101 & AB-0104 (Apex Institute: excess admission & capitation fee)
            CaseLink(
                complaint_id_a=c1.id,
                complaint_id_b=c4.id,
                relationship_type="potential_overlap",
                match_score=0.94,
                match_method="hybrid",
                match_reason="Exact Institution match: 'Apex Institute of Technology and Management' (1-10293847) • Same external reference CPGRAMS/2026/004189 • Shared admission intake keywords.",
                evidence_json='{"institution_match": true, "code_match": true, "category_similarity": 0.88, "text_similarity": 0.91, "external_ref_match": true}',
                review_status="pending",
                created_at=now - timedelta(days=14),
            ),
            # Link 2: PGRC-0101 & FAB-0111 (Apex Institute: dual fee overcharge & scholarship diversion)
            CaseLink(
                complaint_id_a=c1.id,
                complaint_id_b=c11.id,
                relationship_type="potential_overlap",
                match_score=0.82,
                match_method="exact_identifier",
                match_reason="Exact Institution match: 'Apex Institute of Technology and Management' (1-10293847) • Common complainant Pooja Sharma registered simultaneous fee overcharge and scholarship retention.",
                evidence_json='{"institution_match": true, "complainant_match": true, "text_similarity": 0.65}',
                review_status="pending",
                created_at=now - timedelta(days=7),
            ),
            # Link 3: PGRC-0102 & RPC-0107 (National Tech: student welfare & hostel intimidation)
            CaseLink(
                complaint_id_a=c2.id,
                complaint_id_b=c7.id,
                relationship_type="potential_overlap",
                match_score=0.72,
                match_method="hybrid",
                match_reason="Entity match: 'National Institute of Technical Excellence' (1-48201948) • Dual student welfare and hostel safety complaints under active inquiry.",
                evidence_json='{"institution_match": true, "category_similarity": 0.60, "text_similarity": 0.74}',
                review_status="deferred",
                reviewed_by_id=officer_pgrc.id,
                reviewed_at=now - timedelta(days=2),
                review_remarks="Kept under review pending submission of Anti-Ragging Committee inquiry findings.",
                created_at=now - timedelta(days=10),
            ),
            # Link 4: RPC-0107 & FAB-0112 (National Tech: dual escalated statutory breaches)
            CaseLink(
                complaint_id_a=c7.id,
                complaint_id_b=c12.id,
                relationship_type="confirmed_related",
                match_score=0.65,
                match_method="exact_identifier",
                match_reason="Entity match: 'National Institute of Technical Excellence' (1-48201948) • Dual escalated matters in RPC and FAB warranting consolidated Council notice.",
                evidence_json='{"institution_match": true, "escalation_overlap": true}',
                review_status="confirmed",
                reviewed_by_id=admin.id,
                reviewed_at=now - timedelta(days=3),
                review_remarks="Confirmed institutional coordination link. Both matters referred to Standing Scrutiny Committee.",
                created_at=now - timedelta(days=6),
            ),
        ]
        db.session.add_all(links)

        print("Seeding Operational Notifications...")
        notifications = [
            # For System Administrator
            Notification(
                user_id=admin.id,
                role="admin",
                notification_type="overlap_detected",
                title="Potential Cross-Bureau Overlap Alert (94% Score)",
                message="Potential relationship detected between PGRC (AICTE-26-PGRC-0101) and Approval Bureau (AICTE-26-AB-0104) for Apex Institute of Technology.",
                related_complaint_id=c1.id,
                created_at=now - timedelta(days=14),
            ),
            Notification(
                user_id=admin.id,
                role="admin",
                notification_type="case_overdue",
                title="Statutory Deadline Breach Escalation",
                message="Case AICTE-26-RPC-0107 (National Institute of Technical Excellence) is overdue by 4 days. Emergency police FIR status pending.",
                related_complaint_id=c7.id,
                created_at=now - timedelta(days=4),
            ),
            Notification(
                user_id=admin.id,
                role="admin",
                notification_type="case_overdue",
                title="Audit Grant Recovery Overdue Notice",
                message="MODROBS grant recovery notice on case AICTE-26-FAB-0112 is overdue by 6 days.",
                related_complaint_id=c12.id,
                created_at=now - timedelta(days=6),
            ),
            # For Citizen Complainant (Pooja Sharma)
            Notification(
                user_id=user_citizen.id,
                role="citizen",
                notification_type="status_updated",
                title="Action Required: Update on Case AICTE-26-PGRC-0101",
                message="Officer Smt. Ananya Sen has requested bank withdrawal slip and payment slip to verify capitation fee demand.",
                related_complaint_id=c1.id,
                created_at=now - timedelta(days=3),
            ),
            Notification(
                user_id=user_citizen.id,
                role="citizen",
                notification_type="status_updated",
                title="Clarification Acknowledged on AICTE-26-PGRC-0102",
                message="Your no-dues clearance slip has been received. Section 10(1) directive under process for certificate release.",
                related_complaint_id=c2.id,
                created_at=now - timedelta(days=2),
            ),
            Notification(
                user_id=user_citizen.id,
                role="citizen",
                notification_type="status_updated",
                title="Grievance Registered: AICTE-26-FAB-0111",
                message="Your PRAGATI scholarship disbursement grievance has been assigned to Finance & Accounts Bureau for bank reconciliation.",
                related_complaint_id=c11.id,
                created_at=now - timedelta(days=7),
            ),
            # For PGRC Officer
            Notification(
                user_id=officer_pgrc.id,
                bureau_id=bureau_map["PGRC"].id,
                role="officer",
                notification_type="status_updated",
                title="Complainant Document Submission",
                message="Pooja Sharma uploaded no-dues clearance certificate on case AICTE-26-PGRC-0102.",
                related_complaint_id=c2.id,
                created_at=now - timedelta(days=2),
            ),
            # For RPC Officer
            Notification(
                user_id=officer_rpc.id,
                bureau_id=bureau_map["RPC"].id,
                role="officer",
                notification_type="case_overdue",
                title="Mandatory Anti-Ragging Hearing Overdue",
                message="Statutory response deadline elapsed for case AICTE-26-RPC-0107. Immediate notice dispatch required.",
                related_complaint_id=c7.id,
                created_at=now - timedelta(days=3),
            ),
        ]
        db.session.add_all(notifications)

        db.session.commit()

        print("\nAll complaints reset and fresh bureau-specific dummy complaints successfully seeded!")
        print("----------------------------------------------------------------")
        print("Summary of Seeded Complaints:")
        print(f"  Total Complaints:       {len(all_complaints)}")
        print("  Bureaus Represented:    PGRC (3), AB (3), RPC (2), PAPB (2), FAB (2), History (1)")
        print(f"  Overlap Pairs Linked:   {len(links)}")
        print(f"  Case Actions Logged:    {len(actions)}")
        print(f"  Notifications Created:  {len(notifications)}")
        print("----------------------------------------------------------------")

if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    seed_database(reset=reset_flag)
