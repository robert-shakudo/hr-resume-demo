"""Mock Paycom data: 30 Ski Lift Operator applicants with realistic profiles."""
import random
from datetime import datetime, timedelta

APPLICANTS = [
    {
        "id": f"PAY-{str(i+1).zfill(4)}",
        "first_name": fn,
        "last_name": ln,
        "email": f"{fn.lower()}.{ln.lower()}@email.com",
        "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "location": loc,
        "distance_miles": dist,
        "applied_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
        "status": "new",
        "resume": resume,
    }
    for i, (fn, ln, loc, dist, resume) in enumerate([
        ("Jake", "Morrison", "Breckenridge, CO", 4.2, {
            "summary": "5 years outdoor recreation experience. Previous lift operator at Keystone Resort. OSHA 10 certified. Weekend and holiday availability. First Aid/CPR certified.",
            "experience": [
                {"title": "Lift Operator", "company": "Keystone Resort", "years": 3, "ski_related": True},
                {"title": "Trail Crew", "company": "USFS", "years": 2, "ski_related": False},
            ],
            "certifications": ["OSHA 10", "First Aid/CPR", "Ski Patrol Assistant"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["chairlift operation", "safety protocols", "guest communication", "snow grooming"],
        }),
        ("Sierra", "Walsh", "Frisco, CO", 8.1, {
            "summary": "Former lift mechanic with 4 seasons at Copper Mountain. Electrical safety cert. Open availability including 6am shifts.",
            "experience": [
                {"title": "Lift Mechanic", "company": "Copper Mountain", "years": 2, "ski_related": True},
                {"title": "Lift Operator", "company": "Copper Mountain", "years": 2, "ski_related": True},
            ],
            "certifications": ["OSHA 30", "Electrical Safety", "First Responder"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["mechanical maintenance", "lift operations", "safety inspection", "emergency procedures"],
        }),
        ("Tyler", "Nguyen", "Silverthorne, CO", 12.3, {
            "summary": "Seasonal ski resort worker for 3 years at Arapahoe Basin. Guest services and lift operations background. Weekend availability.",
            "experience": [
                {"title": "Lift Operator", "company": "Arapahoe Basin", "years": 3, "ski_related": True},
            ],
            "certifications": ["First Aid/CPR"],
            "availability": {"weekends": True, "holidays": True, "early_am": False},
            "skills": ["chairlift loading", "guest relations", "safety protocols"],
        }),
        ("Morgan", "Chen", "Dillon, CO", 9.8, {
            "summary": "Zero ski resort experience. Looking to break into outdoor work. Flexible schedule, physically fit.",
            "experience": [
                {"title": "Warehouse Worker", "company": "Amazon", "years": 2, "ski_related": False},
            ],
            "certifications": [],
            "availability": {"weekends": True, "holidays": False, "early_am": True},
            "skills": ["physical labor", "teamwork", "reliability"],
        }),
        ("Alex", "Rivera", "Vail, CO", 2.1, {
            "summary": "8 seasons at Vail Mountain. Head lift supervisor for 3 years. ANSI/ASME B77.1 standards training. All shift availability.",
            "experience": [
                {"title": "Head Lift Supervisor", "company": "Vail Mountain", "years": 3, "ski_related": True},
                {"title": "Lift Operator", "company": "Vail Mountain", "years": 5, "ski_related": True},
            ],
            "certifications": ["OSHA 30", "ANSI/ASME B77.1", "First Responder", "Avalanche Safety Level 1"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["lift supervision", "staff training", "emergency response", "equipment inspection", "ANSI standards"],
        }),
        ("Cody", "Patel", "Avon, CO", 6.5, {
            "summary": "2 seasons at Beaver Creek as lift attendant. Good with guests. Weekend shifts preferred.",
            "experience": [
                {"title": "Lift Attendant", "company": "Beaver Creek", "years": 2, "ski_related": True},
            ],
            "certifications": ["CPR"],
            "availability": {"weekends": True, "holidays": True, "early_am": False},
            "skills": ["guest service", "chairlift operation", "safety awareness"],
        }),
        ("Jordan", "Kim", "Denver, CO", 85.0, {
            "summary": "Entry level, Denver-based. No ski experience. Software background. Looking for seasonal change.",
            "experience": [
                {"title": "Software Developer", "company": "Tech Corp", "years": 5, "ski_related": False},
            ],
            "certifications": [],
            "availability": {"weekends": False, "holidays": False, "early_am": False},
            "skills": ["problem solving", "technical skills"],
        }),
        ("Casey", "Thompson", "Leadville, CO", 18.4, {
            "summary": "Outdoor enthusiast with OSHA 10 cert. 1 season at Ski Cooper as lift operator. Available all shifts.",
            "experience": [
                {"title": "Lift Operator", "company": "Ski Cooper", "years": 1, "ski_related": True},
                {"title": "Hiking Guide", "company": "Colorado Adventures", "years": 3, "ski_related": False},
            ],
            "certifications": ["OSHA 10", "Wilderness First Aid"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["outdoor safety", "guest guiding", "lift operations", "emergency first aid"],
        }),
        ("Sam", "Rodriguez", "Minturn, CO", 7.2, {
            "summary": "4 years at Beaver Creek, 2 as lead operator. Safety champion award 2023. Early morning availability.",
            "experience": [
                {"title": "Lead Lift Operator", "company": "Beaver Creek", "years": 2, "ski_related": True},
                {"title": "Lift Operator", "company": "Beaver Creek", "years": 2, "ski_related": True},
            ],
            "certifications": ["OSHA 10", "First Aid/CPR", "Ski Resort Safety"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["lift operation", "safety leadership", "team training", "incident reporting"],
        }),
        ("Drew", "Martinez", "Gypsum, CO", 22.1, {
            "summary": "Physical laborer with construction background. OSHA 30. No ski resort experience but eager to learn.",
            "experience": [
                {"title": "Construction Worker", "company": "Alpine Builders", "years": 6, "ski_related": False},
            ],
            "certifications": ["OSHA 30"],
            "availability": {"weekends": True, "holidays": False, "early_am": True},
            "skills": ["heavy labor", "safety compliance", "equipment operation"],
        }),
        ("Riley", "Anderson", "Eagle, CO", 28.3, {
            "summary": "Ski instructor with 6 years at Vail. PSIA certified. Knows resort operations inside out. Full availability.",
            "experience": [
                {"title": "Ski Instructor", "company": "Vail Mountain", "years": 6, "ski_related": True},
            ],
            "certifications": ["PSIA Level 3", "First Aid/CPR", "Avalanche Safety Level 2"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["ski operations", "guest communication", "safety protocols", "mountain environment"],
        }),
        ("Quinn", "Lee", "Grand Junction, CO", 112.0, {
            "summary": "Retail manager seeking career change. No outdoor experience. Lives far from resort.",
            "experience": [
                {"title": "Store Manager", "company": "Retail Chain", "years": 8, "ski_related": False},
            ],
            "certifications": [],
            "availability": {"weekends": False, "holidays": True, "early_am": False},
            "skills": ["management", "customer service", "scheduling"],
        }),
        ("Blake", "Jackson", "Frisco, CO", 7.8, {
            "summary": "3 seasons at Breckenridge. Lift operator and snow safety crew. OSHA 10 and avalanche training.",
            "experience": [
                {"title": "Lift Operator", "company": "Breckenridge Ski Resort", "years": 2, "ski_related": True},
                {"title": "Snow Safety Crew", "company": "Breckenridge Ski Resort", "years": 1, "ski_related": True},
            ],
            "certifications": ["OSHA 10", "Avalanche Level 1", "First Aid"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["lift operations", "avalanche safety", "snow assessment", "patrol support"],
        }),
        ("Avery", "White", "Keystone, CO", 3.4, {
            "summary": "5 years at Keystone. Trained 12 new operators. Full certification suite. Morning availability.",
            "experience": [
                {"title": "Senior Lift Operator", "company": "Keystone Resort", "years": 3, "ski_related": True},
                {"title": "Lift Operator", "company": "Keystone Resort", "years": 2, "ski_related": True},
            ],
            "certifications": ["OSHA 30", "ANSI/ASME B77.1", "First Responder", "CPR/AED"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["senior operations", "new operator training", "safety inspection", "incident command"],
        }),
        ("Hayden", "Brown", "Dillon, CO", 11.2, {
            "summary": "Fitness trainer with outdoor passion. No ski resort experience. Available weekends only.",
            "experience": [
                {"title": "Personal Trainer", "company": "24 Hour Fitness", "years": 4, "ski_related": False},
            ],
            "certifications": ["CPR/AED"],
            "availability": {"weekends": True, "holidays": False, "early_am": True},
            "skills": ["physical fitness", "safety awareness", "client communication"],
        }),
        ("Parker", "Davis", "Steamboat Springs, CO", 85.5, {
            "summary": "5 seasons at Steamboat. Lift operator and mountain host. OSHA 10. Too far for daily commute.",
            "experience": [
                {"title": "Lift Operator", "company": "Steamboat Resort", "years": 3, "ski_related": True},
                {"title": "Mountain Host", "company": "Steamboat Resort", "years": 2, "ski_related": True},
            ],
            "certifications": ["OSHA 10", "First Aid"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["lift operations", "guest relations", "resort navigation", "safety protocols"],
        }),
        ("Reese", "Miller", "Vail, CO", 1.8, {
            "summary": "Recent college grad seeking gap year work. No ski experience. Lives in Vail. Very available.",
            "experience": [
                {"title": "Barista", "company": "Coffee Shop", "years": 2, "ski_related": False},
            ],
            "certifications": [],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["customer service", "punctuality", "team player"],
        }),
        ("Cameron", "Wilson", "Edwards, CO", 5.9, {
            "summary": "Former ski patrol with 4 years experience. EMT-B certified. Expert in mountain safety protocols.",
            "experience": [
                {"title": "Ski Patrol", "company": "Vail Mountain", "years": 4, "ski_related": True},
            ],
            "certifications": ["EMT-B", "Avalanche Pro Level 2", "OSHA 30", "First Responder"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["emergency medicine", "avalanche control", "lift evacuation", "incident command"],
        }),
        ("Jamie", "Taylor", "Minturn, CO", 8.3, {
            "summary": "2 seasons at Beaver Creek as lift attendant. Part-time only due to school schedule.",
            "experience": [
                {"title": "Lift Attendant", "company": "Beaver Creek", "years": 2, "ski_related": True},
            ],
            "certifications": ["CPR"],
            "availability": {"weekends": True, "holidays": False, "early_am": False},
            "skills": ["chairlift loading", "guest service"],
        }),
        ("Hunter", "Garcia", "Silverthorne, CO", 14.7, {
            "summary": "Mountain guide and outdoor ed instructor. Wilderness First Responder certified. OSHA 10.",
            "experience": [
                {"title": "Mountain Guide", "company": "Colorado Mountain School", "years": 5, "ski_related": False},
                {"title": "Outdoor Ed Instructor", "company": "Outward Bound", "years": 2, "ski_related": False},
            ],
            "certifications": ["WFR", "OSHA 10", "Swift Water Rescue"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["outdoor safety", "risk management", "team leadership", "emergency response"],
        }),
        ("Skyler", "Moore", "Vail, CO", 3.1, {
            "summary": "3 years lift operations at Vail. Promoted to quality check inspector. ANSI standards training.",
            "experience": [
                {"title": "Lift QC Inspector", "company": "Vail Mountain", "years": 1, "ski_related": True},
                {"title": "Lift Operator", "company": "Vail Mountain", "years": 2, "ski_related": True},
            ],
            "certifications": ["OSHA 10", "ANSI/ASME B77.1", "First Aid/CPR"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["quality inspection", "lift standards compliance", "operational safety", "documentation"],
        }),
        ("Peyton", "Jones", "Aurora, CO", 92.0, {
            "summary": "Office worker wanting seasonal job. Lives in Denver area. No relevant experience.",
            "experience": [
                {"title": "Office Administrator", "company": "Corp LLC", "years": 3, "ski_related": False},
            ],
            "certifications": [],
            "availability": {"weekends": True, "holidays": False, "early_am": False},
            "skills": ["administration", "organization"],
        }),
        ("Dakota", "Harris", "Breckenridge, CO", 5.0, {
            "summary": "Ski lift operator for 2 seasons at Breck. Currently finishing OSHA 30. Full time availability.",
            "experience": [
                {"title": "Lift Operator", "company": "Breckenridge Ski Resort", "years": 2, "ski_related": True},
            ],
            "certifications": ["OSHA 10", "First Aid"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["lift operations", "safety protocols", "guest service"],
        }),
        ("Finley", "Clark", "Leadville, CO", 21.8, {
            "summary": "Firefighter/EMT with 6 years service. Pursuing seasonal work during off-rotation. Emergency response expert.",
            "experience": [
                {"title": "Firefighter/EMT", "company": "Lake County Fire", "years": 6, "ski_related": False},
            ],
            "certifications": ["EMT-B", "OSHA 10", "CPR/AED", "Rope Rescue"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["emergency response", "safety protocols", "team operations", "incident command"],
        }),
        ("Rory", "Lewis", "Wolcott, CO", 16.4, {
            "summary": "4 seasons at Eagle Point (Utah). Relocated to Colorado. OSHA 30, all certifications current.",
            "experience": [
                {"title": "Lift Operator", "company": "Eagle Point Resort", "years": 4, "ski_related": True},
            ],
            "certifications": ["OSHA 30", "First Responder", "Avalanche Level 1"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["chairlift operations", "emergency response", "avalanche safety", "equipment checks"],
        }),
        ("Wren", "Walker", "Avon, CO", 4.7, {
            "summary": "3 seasons Beaver Creek lift ops. Safety excellence award 2022. All shifts available.",
            "experience": [
                {"title": "Lift Operator", "company": "Beaver Creek Resort", "years": 3, "ski_related": True},
            ],
            "certifications": ["OSHA 10", "First Aid/CPR"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["lift operations", "safety protocols", "incident reporting", "guest assistance"],
        }),
        ("Sage", "Hall", "Glenwood Springs, CO", 65.2, {
            "summary": "River guide with physical fitness. No ski resort experience. Far from resort.",
            "experience": [
                {"title": "Whitewater Guide", "company": "Blazing Adventures", "years": 5, "ski_related": False},
            ],
            "certifications": ["WFR", "Swift Water Rescue"],
            "availability": {"weekends": True, "holidays": False, "early_am": True},
            "skills": ["physical endurance", "outdoor safety", "guest guiding"],
        }),
        ("Lane", "Young", "Vail, CO", 2.5, {
            "summary": "7 seasons at Vail. Master lift technician. Trains new hires. Authored resort safety manual update.",
            "experience": [
                {"title": "Master Lift Technician", "company": "Vail Mountain", "years": 4, "ski_related": True},
                {"title": "Senior Lift Operator", "company": "Vail Mountain", "years": 3, "ski_related": True},
            ],
            "certifications": ["OSHA 30", "ANSI/ASME B77.1", "Master Lift Tech", "First Responder", "Avalanche Pro 2"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["lift mechanics", "safety manual authoring", "staff training", "regulatory compliance", "evacuation procedures"],
        }),
        ("Emery", "Allen", "Frisco, CO", 10.1, {
            "summary": "1 season at A-Basin as lift attendant. Still learning. Good attitude, improving skills.",
            "experience": [
                {"title": "Lift Attendant", "company": "Arapahoe Basin", "years": 1, "ski_related": True},
            ],
            "certifications": [],
            "availability": {"weekends": True, "holidays": True, "early_am": False},
            "skills": ["basic lift operations", "guest service", "safety awareness"],
        }),
        ("Rowan", "Scott", "Edwards, CO", 6.8, {
            "summary": "Certified ski patroller transitioning to lift ops. 5 years patrol at Beaver Creek. Expert safety knowledge.",
            "experience": [
                {"title": "Ski Patroller", "company": "Beaver Creek Resort", "years": 5, "ski_related": True},
            ],
            "certifications": ["NREMT-B", "OEC", "Avalanche Pro Level 3", "OSHA 30"],
            "availability": {"weekends": True, "holidays": True, "early_am": True},
            "skills": ["ski patrol", "emergency medicine", "avalanche control", "lift evacuation", "mountain safety"],
        }),
    ])
]


JOB_POSTING = {
    "id": "PAY-JOB-2026-0041",
    "title": "Ski Lift Operator",
    "department": "Mountain Operations",
    "location": "Vail, CO",
    "type": "Seasonal Full-Time",
    "season": "Winter 2025-2026",
    "applicant_count": 170,
    "loaded_count": 30,
    "description": "Operate and monitor ski lifts to safely transport guests up the mountain. Ensure all safety protocols are followed, assist guests loading/unloading, perform daily equipment checks, and respond to emergencies.",
    "requirements": [
        "Outdoor/physical labor experience",
        "Prior ski resort or lift operator experience preferred",
        "Weekend, holiday, and early morning availability required",
        "Safety certifications (OSHA, First Aid) preferred",
        "Must live within 35 miles of resort",
    ],
    "scoring_criteria": {
        "ski_resort_experience": 35,
        "safety_certifications": 25,
        "availability": 20,
        "proximity": 15,
        "physical_outdoor_experience": 5,
    }
}


def score_applicant(applicant: dict) -> dict:
    """AI-style scoring with reasoning."""
    resume = applicant["resume"]
    score = 0
    breakdown = {}
    reasons = []

    # Ski resort experience (35 pts)
    ski_jobs = [e for e in resume["experience"] if e.get("ski_related")]
    ski_years = sum(e.get("years", 0) for e in ski_jobs)
    lift_jobs = [e for e in ski_jobs if "lift" in e["title"].lower() or "operator" in e["title"].lower()]

    if lift_jobs:
        pts = min(35, 20 + ski_years * 3)
        reasons.append(f"✅ Direct lift operator experience ({ski_years} years)")
    elif ski_jobs:
        pts = min(25, 10 + ski_years * 3)
        reasons.append(f"✅ Ski resort experience ({ski_years} years, non-lift roles)")
    else:
        pts = 0
        reasons.append("❌ No ski resort experience")
    score += pts
    breakdown["Ski Resort Experience"] = {"points": pts, "max": 35}

    # Safety certifications (25 pts)
    certs = [c.upper() for c in resume.get("certifications", [])]
    cert_pts = 0
    if any("OSHA 30" in c for c in certs):
        cert_pts += 12
    elif any("OSHA 10" in c for c in certs):
        cert_pts += 7
    if any("ANSI" in c or "B77" in c for c in certs):
        cert_pts += 8
        reasons.append("✅ ANSI/ASME B77.1 lift standards certification")
    if any("FIRST AID" in c or "CPR" in c or "EMT" in c or "RESPONDER" in c for c in certs):
        cert_pts += 5
    cert_pts = min(25, cert_pts)
    if cert_pts >= 15:
        reasons.append(f"✅ Strong safety certification suite ({', '.join(resume['certifications'][:2])})")
    elif cert_pts > 0:
        reasons.append(f"⚠️ Basic certifications ({', '.join(resume['certifications'][:2]) if resume['certifications'] else 'none'})")
    else:
        reasons.append("❌ No safety certifications")
    score += cert_pts
    breakdown["Safety Certifications"] = {"points": cert_pts, "max": 25}

    # Availability (20 pts)
    avail = resume.get("availability", {})
    avail_pts = 0
    if avail.get("weekends"):
        avail_pts += 8
    if avail.get("holidays"):
        avail_pts += 7
    if avail.get("early_am"):
        avail_pts += 5
    if avail_pts >= 18:
        reasons.append("✅ Full availability (weekends, holidays, early AM)")
    elif avail_pts >= 10:
        reasons.append("⚠️ Partial availability")
    else:
        reasons.append("❌ Limited availability — misses weekends/holidays")
    score += avail_pts
    breakdown["Availability"] = {"points": avail_pts, "max": 20}

    # Proximity (15 pts)
    dist = applicant.get("distance_miles", 100)
    if dist <= 10:
        prox_pts = 15
        reasons.append(f"✅ Very close to resort ({dist:.1f} miles)")
    elif dist <= 25:
        prox_pts = 10
        reasons.append(f"⚠️ Reasonable commute ({dist:.1f} miles)")
    elif dist <= 50:
        prox_pts = 5
        reasons.append(f"⚠️ Long commute ({dist:.1f} miles)")
    else:
        prox_pts = 0
        reasons.append(f"❌ Too far from resort ({dist:.1f} miles)")
    score += prox_pts
    breakdown["Proximity"] = {"points": prox_pts, "max": 15}

    # Physical/outdoor experience (5 pts)
    physical_keywords = ["outdoor", "physical", "labor", "construction", "guide", "patrol", "crew"]
    summary_lower = resume.get("summary", "").lower()
    if any(kw in summary_lower for kw in physical_keywords):
        phys_pts = 5
        reasons.append("✅ Physical/outdoor labor background")
    else:
        phys_pts = 2
    score += phys_pts
    breakdown["Physical/Outdoor Experience"] = {"points": phys_pts, "max": 5}

    # Determine recommendation
    if score >= 75:
        recommendation = "Strong Hire"
        badge = "🟢"
    elif score >= 55:
        recommendation = "Consider"
        badge = "🟡"
    elif score >= 35:
        recommendation = "Weak Candidate"
        badge = "🟠"
    else:
        recommendation = "Reject"
        badge = "🔴"

    return {
        "score": score,
        "max_score": 100,
        "recommendation": recommendation,
        "badge": badge,
        "breakdown": breakdown,
        "reasons": reasons,
    }
