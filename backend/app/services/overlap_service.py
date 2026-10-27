import re
from datetime import datetime, timezone
from rapidfuzz import fuzz
from ..models import db, Complaint, CaseLink, Notification, Institution, AuditEvent, User

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    # Replace common abbreviations in Indian higher education institutions
    abbreviations = {
        r"\binst\.\b": "institute",
        r"\binst\b": "institute",
        r"\btech\.\b": "technology",
        r"\btech\b": "technology",
        r"\bengg\.\b": "engineering",
        r"\bengg\b": "engineering",
        r"\bcoll\.\b": "college",
        r"\bcoll\b": "college",
        r"\buniv\.\b": "university",
        r"\buniv\b": "university",
        r"\bdept\.\b": "department",
        r"\bmgmt\.\b": "management",
        r"\bpoly\.\b": "polytechnic",
    }
    for pattern, replacement in abbreviations.items():
        text = re.sub(pattern, replacement, text)
    # Remove punctuation except alphanumeric and spaces
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_keywords(text: str) -> set:
    normalized = normalize_text(text)
    # Stop words common in complaint descriptions
    stop_words = {
        "the", "and", "or", "to", "in", "of", "a", "an", "is", "for", "with", "on", 
        "at", "by", "from", "up", "about", "into", "over", "after", "it", "this", 
        "that", "these", "those", "we", "they", "our", "their", "has", "have", "been",
        "regarding", "complaint", "issue", "against", "student", "students", "college",
        "institute", "management", "aicte", "request", "action", "kindly", "please"
    }
    tokens = [w for w in normalized.split() if len(w) > 3 and w not in stop_words]
    return set(tokens)

def compute_similarity(comp_a: Complaint, comp_b: Complaint):
    """
    Multi-stage overlap detection pipeline:
    - Stage A: Exact Identifier Matching
    - Stage B: Institution Identity Resolution
    - Stage C: Complaint Content & Category Similarity
    - Stage D: Matching Evidence & Explainability Synthesis
    """
    reasons = []
    evidence = {}
    
    # --- STAGE A: Exact Identifier Matching ---
    inst_a = comp_a.institution
    inst_b = comp_b.institution
    
    same_institution_id = (inst_a.id == inst_b.id)
    same_institution_code = (inst_a.institution_code == inst_b.institution_code)
    
    # External reference match (e.g., CPGRAMS docket number, court case, FIR ref)
    same_ext_ref = False
    if comp_a.external_reference and comp_b.external_reference:
        ref_a = comp_a.external_reference.strip().lower()
        ref_b = comp_b.external_reference.strip().lower()
        if ref_a == ref_b:
            same_ext_ref = True
            reasons.append(f"Identical external reference: {comp_a.external_reference}")

    evidence["same_institution_id"] = same_institution_id
    evidence["same_institution_code"] = same_institution_code
    evidence["same_external_reference"] = same_ext_ref

    # --- STAGE B: Institution Identity Resolution ---
    if same_institution_id or same_institution_code:
        institution_score = 1.0
        reasons.append(f"Exact Institution match: '{inst_a.name}' ({inst_a.institution_code})")
    else:
        # Fuzzy match institution names and aliases
        norm_name_a = normalize_text(inst_a.name)
        norm_name_b = normalize_text(inst_b.name)
        token_set_ratio = fuzz.token_set_ratio(norm_name_a, norm_name_b) / 100.0
        
        # Check aliases
        alias_scores = []
        for alias in inst_a.alias_list:
            alias_scores.append(fuzz.token_set_ratio(normalize_text(alias), norm_name_b) / 100.0)
        for alias in inst_b.alias_list:
            alias_scores.append(fuzz.token_set_ratio(norm_name_a, normalize_text(alias)) / 100.0)
            
        best_alias_score = max(alias_scores) if alias_scores else 0.0
        institution_score = max(token_set_ratio, best_alias_score)
        
        # State check: if institutions are in different states, reduce score significantly
        if inst_a.state and inst_b.state and inst_a.state.lower() != inst_b.state.lower():
            institution_score *= 0.5
            
        if institution_score >= 0.80:
            reasons.append(f"High-confidence Institution name match ({int(institution_score*100)}%): '{inst_a.name}' and '{inst_b.name}'")

    evidence["institution_match_score"] = round(institution_score, 2)

    # --- STAGE C: Complaint Similarity ---
    # Category match
    category_match = (comp_a.category.lower().strip() == comp_b.category.lower().strip())
    category_score = 1.0 if category_match else 0.0
    if category_match:
        reasons.append(f"Identical complaint category: '{comp_a.category}'")
    evidence["category_match"] = category_match

    # Subject & Description keyword overlap (Jaccard similarity)
    keywords_a = extract_keywords(comp_a.subject + " " + comp_a.description)
    keywords_b = extract_keywords(comp_b.subject + " " + comp_b.description)
    
    if keywords_a and keywords_b:
        intersection = keywords_a.intersection(keywords_b)
        union = keywords_a.union(keywords_b)
        keyword_jaccard = len(intersection) / len(union) if union else 0.0
        shared_keywords = sorted(list(intersection))[:8]
    else:
        keyword_jaccard = 0.0
        shared_keywords = []

    # Text fuzz ratio on subjects & descriptions
    norm_text_a = normalize_text(comp_a.subject + " " + comp_a.description[:400])
    norm_text_b = normalize_text(comp_b.subject + " " + comp_b.description[:400])
    text_fuzz_score = fuzz.token_sort_ratio(norm_text_a, norm_text_b) / 100.0

    content_score = (0.5 * keyword_jaccard) + (0.5 * text_fuzz_score)
    evidence["shared_keywords"] = shared_keywords
    evidence["keyword_jaccard"] = round(keyword_jaccard, 2)
    evidence["text_similarity"] = round(text_fuzz_score, 2)
    evidence["content_score"] = round(content_score, 2)

    if shared_keywords:
        reasons.append(f"Shared salient keywords: {', '.join(shared_keywords)}")

    # Cross-Bureau aspect: highlight if complaints belong to different Bureaus
    cross_bureau = (comp_a.current_bureau_id != comp_b.current_bureau_id)
    evidence["cross_bureau"] = cross_bureau
    if cross_bureau:
        bureau_a_code = comp_a.current_bureau.code if comp_a.current_bureau else "B1"
        bureau_b_code = comp_b.current_bureau.code if comp_b.current_bureau else "B2"
        reasons.append(f"Cross-departmental case ({bureau_a_code} vs {bureau_b_code})")

    # --- STAGE D: Overall Score Calculation & Classification ---
    if same_ext_ref:
        overall_score = 1.0
        match_method = "exact_identifier"
    elif same_institution_id or same_institution_code:
        if content_score > 0.40 or category_match:
            overall_score = 0.50 + (0.30 * content_score) + (0.20 * category_score)
            match_method = "hybrid"
        else:
            # Same institution, but different topics
            overall_score = 0.40 + (0.30 * content_score)
            match_method = "same_institution_different_topic"
            reasons.append("Shared institution, distinct complaint matters")
    elif institution_score >= 0.80:
        overall_score = (0.45 * institution_score) + (0.35 * content_score) + (0.20 * category_score)
        match_method = "fuzzy_institution_name"
    else:
        overall_score = (0.30 * institution_score) + (0.70 * content_score)
        match_method = "text_similarity"

    evidence["overall_score"] = round(overall_score, 2)

    return {
        "match_score": min(round(overall_score, 2), 1.0),
        "match_method": match_method,
        "match_reason": " • ".join(reasons) if reasons else "Contextual match flagged by system rules",
        "evidence": evidence,
        "is_alertable": (
            (same_ext_ref) or
            (same_institution_id and (category_match or content_score >= 0.25)) or
            (institution_score >= 0.80 and content_score >= 0.30) or
            (overall_score >= 0.55)
        )
    }

def scan_complaint_overlaps(complaint_id: int):
    """
    Scan a newly created or updated complaint against all other complaints in the system.
    Generates or updates CaseLink records with ordered IDs (A < B).
    """
    target = db.session.get(Complaint, complaint_id)
    if not target:
        return []

    # Get candidate complaints (excluding self)
    candidates = db.session.query(Complaint).filter(Complaint.id != complaint_id).all()
    created_links = []

    for other in candidates:
        # Enforce canonical ordering: id_a < id_b
        id_a, id_b = (target.id, other.id) if target.id < other.id else (other.id, target.id)
        comp_a, comp_b = (target, other) if target.id < other.id else (other, target)

        # Check existing link
        existing_link = db.session.query(CaseLink).filter_by(
            complaint_id_a=id_a,
            complaint_id_b=id_b
        ).first()

        # If already reviewed as confirmed, unrelated, or deferred by an official, don't overwrite decision
        if existing_link and existing_link.review_status != "pending":
            continue

        res = compute_similarity(comp_a, comp_b)

        if res["is_alertable"]:
            if not existing_link:
                new_link = CaseLink(
                    complaint_id_a=id_a,
                    complaint_id_b=id_b,
                    relationship_type="potential_overlap",
                    match_score=res["match_score"],
                    match_method=res["match_method"],
                    match_reason=res["match_reason"],
                    review_status="pending",
                )
                new_link.set_evidence(res["evidence"])
                db.session.add(new_link)
                db.session.flush()

                # Generate notification for involved bureaus
                bureau_codes = set()
                if comp_a.current_bureau:
                    bureau_codes.add(comp_a.current_bureau.code)
                if comp_b.current_bureau:
                    bureau_codes.add(comp_b.current_bureau.code)

                notif = Notification(
                    notification_type="overlap_detected",
                    title=f"Potential Cross-Bureau Overlap Flagged: {comp_a.case_number} & {comp_b.case_number}",
                    message=f"Potential related complaints detected between {', '.join(bureau_codes)} concerning '{comp_a.institution.name}'. Rationale: {res['match_reason']}",
                    related_complaint_id=target.id,
                    related_case_link_id=new_link.id,
                )
                db.session.add(notif)
                created_links.append(new_link)
            else:
                # Update existing pending link with fresh score and evidence
                existing_link.match_score = res["match_score"]
                existing_link.match_method = res["match_method"]
                existing_link.match_reason = res["match_reason"]
                existing_link.set_evidence(res["evidence"])
                created_links.append(existing_link)

    db.session.commit()
    return created_links

def review_case_link(link_id: int, decision: str, user_id: int, remarks: str = ""):
    """
    Review a potential overlap:
    - Confirmed Overlap: confirmed / confirmed_overlap
    - False Alert: false_alert / unrelated / dismissed
    - Needs Review: needs_review / deferred
    """
    from ..models import CaseAction
    link = db.session.get(CaseLink, link_id)
    if not link:
        return None, "Overlap link not found"

    norm_decision = decision.strip().lower().replace(" ", "_")

    if norm_decision in ("confirmed_overlap", "confirmed", "confirmed_related"):
        canonical_rel = norm_decision if norm_decision in ("confirmed_overlap", "confirmed_related") else "confirmed_overlap"
        canonical_status = "confirmed"
        display_label = "Confirmed Overlap"
    elif norm_decision in ("false_alert", "unrelated", "dismissed"):
        canonical_rel = norm_decision if norm_decision in ("false_alert", "unrelated") else "false_alert"
        canonical_status = "dismissed"
        display_label = "False Alert"
    elif norm_decision in ("needs_review", "deferred"):
        canonical_rel = norm_decision
        canonical_status = "deferred"
        display_label = "Needs Review"
    else:
        return None, f"Invalid decision '{decision}'. Expected: 'Confirmed Overlap', 'False Alert', or 'Needs Review'."

    reviewer = db.session.get(User, user_id)
    reviewer_name = reviewer.name if reviewer else f"Official #{user_id}"

    link.relationship_type = canonical_rel
    link.review_status = canonical_status
    link.reviewed_by_id = user_id
    link.reviewed_at = datetime.now(timezone.utc)
    link.review_remarks = remarks

    comp_a = link.complaint_a
    comp_b = link.complaint_b

    # Record coordination action on both cases
    action_desc = f"Overlap review completed: Marked as '{display_label}' by {reviewer_name}."
    if remarks:
        action_desc += f" Remarks: {remarks}"

    if comp_a:
        action_a = CaseAction(
            complaint_id=comp_a.id,
            action_type="overlap_verification",
            description=action_desc + f" (Linked case: {comp_b.case_number if comp_b else ''})",
            old_status=comp_a.status,
            new_status=comp_a.status,
            performed_by_id=user_id,
        )
        db.session.add(action_a)

    if comp_b:
        action_b = CaseAction(
            complaint_id=comp_b.id,
            action_type="overlap_verification",
            description=action_desc + f" (Linked case: {comp_a.case_number if comp_a else ''})",
            old_status=comp_b.status,
            new_status=comp_b.status,
            performed_by_id=user_id,
        )
        db.session.add(action_b)

    # When Confirmed Overlap: Notify both involved bureaus
    if canonical_status == "confirmed":
        bureaus_to_notify = set()
        if comp_a and comp_a.current_bureau_id:
            bureaus_to_notify.add(comp_a.current_bureau_id)
        if comp_b and comp_b.current_bureau_id:
            bureaus_to_notify.add(comp_b.current_bureau_id)

        for b_id in bureaus_to_notify:
            notif = Notification(
                bureau_id=b_id,
                notification_type="overlap_confirmed",
                title=f"Confirmed Overlap: {comp_a.case_number if comp_a else ''} & {comp_b.case_number if comp_b else ''}",
                message=f"Overlap confirmed by {reviewer_name} concerning '{comp_a.institution.name if comp_a and comp_a.institution else 'institution'}'. Both cases remain independent; coordination actions are enabled.",
                related_complaint_id=comp_a.id if comp_a else None,
                related_case_link_id=link.id,
            )
            db.session.add(notif)

    # Record audit event
    audit = AuditEvent(
        user_id=user_id,
        action="OVERLAP_REVIEW",
        entity_type="CaseLink",
        entity_id=link.id,
    )
    audit.set_details({
        "complaint_id_a": link.complaint_id_a,
        "complaint_id_b": link.complaint_id_b,
        "decision": display_label,
        "review_status": canonical_status,
        "remarks": remarks
    })
    db.session.add(audit)
    db.session.commit()

    return link, None

