# analyzer/keywords.py

# ==============================================================================
# 🚨 DANGER_KEYWORDS: High Risk (Immediate Flagging)
# Includes: Legal Threats, HR Violations, Security Breaches, and Toxicity
# ==============================================================================
DANGER_KEYWORDS = [
    # --- 1. LEGAL & LITIGATION TRIGGERS ---
    "sue", "lawyer", "attorney", "legal action", "court", "litigation", 
    "prosecute", "plaintiff", "defendant", "testimony", "subpoena", "deposition",
    "damages", "compensation", "liability", "negligence", "gross negligence",
    "breach of contract", "violation", "infringement", "cease and desist",
    "tribunal", "arbitration", "dispute resolution", "settlement", "appeal", 
    "statute", "injunction", "warrant", "affidavit", "allegation", "hearing", 
    "verdict", "slander", "libel", "defamation", "fraud", "embezzlement", 
    "extortion", "blackmail", "bribery", "corruption", "money laundering",
    "illegal", "unlawful", "criminal", "felony", "misdemeanor", "regulatory",

    # --- 2. HR, HARASSMENT & DISCRIMINATION ---
    "harass", "harassment", "sexual harassment", "abuse", "discriminate", 
    "discrimination", "racist", "racism", "sexist", "sexism", "gender bias", 
    "bigot", "slur", "derogatory", "offensive", "hostile environment", "toxic",
    "bully", "bullying", "threaten", "threat", "assault", "violence", "physical",
    "hit", "strike", "punch", "unsafe", "danger", "injury", "accident", 
    "workers comp", "disability", "medical leave", "firing", "termination", 
    "wrongful termination", "fired", "sacked", "resign", "quit", "constructive dismissal",
    "whistleblower", "retaliation", "misconduct", "inappropriate", "unprofessional",
    "nepotism", "favoritism", "ethics", "code of conduct",

    # --- 3. TOXICITY & PROFANITY (Uncensored for exact matching) ---
    # Note: The system needs exact string matches to detect these words.
    "shit", "bullshit", "fuck", "fucking", "fucked", "damn", "dammit", "hell", 
    "stupid", "idiot", "moron", "imbecile", "dumb", "shut up", "piss", "pissed",
    "crap", "bastard", "bitch", "asshole", "dick", "cock", "prick", "cunt",
    "useless", "incompetent", "lazy", "brainless", "kill", "die", "hate", 
    "loathe", "despise", "crazy", "insane", "psycho", "maniac", "liar", 
    "cheat", "thief", "scam", "scumbag", "trash", "garbage", "filth", 
    "worst", "horrible", "disgusting", "pathetic", "ridiculous", "nonsense",

    # --- 4. SECURITY & DATA PRIVACY ---
    "data breach", "security breach", "hack", "hacked", "compromised", 
    "password", "credential", "leak", "leaked", "phishing", "malware", 
    "virus", "ransomware", "trojan", "backdoor", "keylogger", "spyware",
    "attack", "vulnerability", "exploit", "zero-day", "unauthorized access",
    "denied", "blocked", "firewall", "encryption", "decryption", "private key",
    "secret", "confidential", "proprietary", "trade secret", "intellectual property",
    "gdpr", "ccpa", "hipaa", "compliance", "audit", "investigation"
]

# ==============================================================================
# 😡 COMPLAINT_KEYWORDS: Medium Risk (Customer Service Issues)
# Includes: Product Failures, Shipping Delays, Service Quality
# ==============================================================================
COMPLAINT_KEYWORDS = [
    # --- 1. DISSATISFACTION ---
    "bad", "poor", "terrible", "awful", "dreadful", "horrendous", "abysmal",
    "disappointed", "dissatisfied", "unhappy", "frustrated", "annoyed", 
    "upset", "angry", "furious", "livid", "regret", "mistake", "fail", 
    "failure", "failing", "defect", "flaw", "glitch", "bug", "error", 
    "crash", "freeze", "slow", "lag", "broken", "damage", "damaged", 
    "scratch", "dent", "ruined", "destroy", "mess", "disaster", "catastrophe",
    "chaos", "nightmare", "headache", "trouble", "issue", "problem",

    # --- 2. SERVICE FAILURES ---
    "delay", "delayed", "late", "overdue", "wait", "waiting", "hold", 
    "ignored", "neglected", "rude", "impolite", "unhelpful", "incompetent",
    "unresponsive", "ghosted", "missed", "cancel", "cancelled", "reschedule", 
    "postpone", "unavailable", "offline", "down", "outage", "disconnect", 
    "drop", "lost", "stolen", "missing", "wrong", "incorrect", "misleading", 
    "false", "lie", "deceive", "dishonest", "bait and switch",

    # --- 3. RETURNS & REFUNDS ---
    "refund", "money back", "reimburse", "return", "exchange", "replace", 
    "guarantee", "warranty", "defective", "quality control", "junk", "waste of money",
    "rip off", "overpriced", "expensive", "value", "useless", "stopped working", 
    "function", "feature", "shipment", "delivery", "shipping", "tracking", 
    "package", "box", "open", "wrong item", "missing part"
]

# ==============================================================================
# 💰 FINANCE_KEYWORDS: Business Context (Usually Neutral/Low Risk)
# Includes: Invoicing, Payments, Salaries, Taxes
# ==============================================================================
FINANCE_KEYWORDS = [
    # --- 1. DOCUMENTS ---
    "invoice", "bill", "receipt", "quote", "quotation", "estimate", "proposal", 
    "contract", "agreement", "sow", "statement of work", "po", "purchase order", 
    "statement", "report", "spreadsheet", "excel", "ledger", "balance sheet", 
    "p&l", "profit and loss", "audit", "tax", "return", "filing", "w9", "1099",

    # --- 2. TRANSACTIONS ---
    "payment", "pay", "paid", "payable", "receivable", "due", "overdue", 
    "outstanding", "owe", "debt", "credit", "debit", "charge", "transaction", 
    "transfer", "wire", "ach", "swift", "deposit", "withdrawal", "refund", 
    "reimbursement", "expense", "expenditure", "cost", "price", "rate", 
    "fee", "fine", "penalty", "discount", "rebate", "commission", "royalty",

    # --- 3. PAYROLL & BUDGET ---
    "salary", "wages", "bonus", "compensation", "payroll", "deduction", 
    "benefits", "insurance", "401k", "budget", "forecast", "projection", 
    "profit", "loss", "margin", "revenue", "sales", "pricing", "valuation", 
    "asset", "liability", "equity", "capital", "investment", "fund", 
    "bank", "account", "wallet", "currency", "dollar", "crypto", "bitcoin"
]