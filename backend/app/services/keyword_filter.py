"""
Keyword filtering service for content filtering by category
Supports English, French, and Arabic keywords
"""

KEYWORD_FILTERS = {
    "no_filter": {
        "name": "No Filter",
        "keywords": []
    },
    "finance": {
        "name": "Finance",
        "keywords": {
            "en": [
                "finance", "financial", "bank", "banking", "investment", "investor", "stock", "market",
                "trading", "portfolio", "earnings", "revenue", "profit", "loss", "cash flow", "balance sheet",
                "valuation", "dividend", "capital", "equities", "bonds", "fixed income", "commodities", "forex",
                "ETF", "derivatives", "futures", "options", "regulation", "compliance", "audit", "risk management",
                "fraud", "AML", "KYC", "sanctions"
            ],
            "fr": [
                "finance", "financier", "banque", "bancaire", "investissement", "investisseur", "action", "marché",
                "trading", "portefeuille", "résultats", "revenus", "profit", "perte", "flux de trésorerie", "bilan",
                "valorisation", "dividende", "capital", "actions", "obligations", "revenus fixes", "matières premières",
                "change", "ETF", "produits dérivés", "contrats à terme", "options", "réglementation", "conformité",
                "audit", "gestion des risques", "fraude", "LCB FT", "KYC", "sanctions"
            ],
            "ar": [
                "التمويل", "مالي", "بنك", "مصرفي", "استثمار", "مستثمر", "أسهم", "سوق", "تداول", "محفظة",
                "أرباح", "إيرادات", "ربح", "خسارة", "تدفق نقدي", "ميزانية", "تقييم", "توزيعات أرباح",
                "رأس المال", "الأسهم", "السندات", "الدخل الثابت", "السلع", "العملات الأجنبية", "صناديق ETF",
                "مشتقات مالية", "العقود الآجلة", "الخيارات", "التنظيم", "الامتثال", "التدقيق", "إدارة المخاطر",
                "احتيال", "مكافحة غسل الأموال", "اعرف عميلك", "العقوبات"
            ]
        }
    },
    "education": {
        "name": "Education",
        "keywords": {
            "en": [
                "education", "school", "university", "college", "student", "teacher", "academic", "learning",
                "higher education", "bachelor", "master", "PhD", "diploma", "certification", "accreditation",
                "education policy", "curriculum", "reform", "literacy", "public education", "private education",
                "e learning", "online course", "MOOC", "digital education", "learning platform", "LMS"
            ],
            "fr": [
                "éducation", "école", "université", "collège", "étudiant", "enseignant", "académique", "apprentissage",
                "enseignement supérieur", "licence", "master", "doctorat", "diplôme", "certification", "accréditation",
                "politique éducative", "programme scolaire", "réforme", "alphabétisation", "éducation publique",
                "éducation privée", "e learning", "cours en ligne", "MOOC", "éducation numérique", "plateforme éducative", "LMS"
            ],
            "ar": [
                "تعليم", "مدرسة", "جامعة", "كلية", "طالب", "أستاذ", "أكاديمي", "تعلم", "التعليم العالي",
                "بكالوريوس", "ماجستير", "دكتوراه", "دبلوم", "شهادة", "اعتماد", "سياسة تعليمية", "منهاج",
                "إصلاح", "محو الأمية", "التعليم العمومي", "التعليم الخاص", "التعلم الإلكتروني", "دورات عبر الإنترنت",
                "MOOC", "التعليم الرقمي", "منصة تعليمية", "نظام إدارة التعلم"
            ]
        }
    },
    "technology": {
        "name": "Technology",
        "keywords": {
            "en": [
                "technology", "tech", "digital", "software", "hardware", "IT", "artificial intelligence", "AI",
                "machine learning", "data science", "cloud computing", "cybersecurity", "blockchain", "automation",
                "ERP", "CRM", "SaaS", "information systems"
            ],
            "fr": [
                "technologie", "numérique", "digital", "logiciel", "matériel", "informatique", "intelligence artificielle",
                "IA", "apprentissage automatique", "science des données", "cloud computing", "cybersécurité", "blockchain",
                "automatisation", "ERP", "CRM", "SaaS", "systèmes d information"
            ],
            "ar": [
                "تكنولوجيا", "تقنية", "رقمي", "برمجيات", "أجهزة", "تكنولوجيا المعلومات", "الذكاء الاصطناعي",
                "الذكاء الصناعي", "تعلم الآلة", "علم البيانات", "الحوسبة السحابية", "الأمن السيبراني",
                "سلسلة الكتل", "الأتمتة", "ERP", "CRM", "SaaS", "أنظمة المعلومات"
            ]
        }
    },
    "economy": {
        "name": "Economy",
        "keywords": {
            "en": [
                "economy", "economic", "growth", "recession", "inflation", "GDP", "monetary policy",
                "fiscal policy", "interest rates", "central bank", "unemployment", "consumer confidence"
            ],
            "fr": [
                "économie", "économique", "croissance", "récession", "inflation", "PIB", "politique monétaire",
                "politique budgétaire", "taux d intérêt", "banque centrale", "chômage", "confiance des consommateurs"
            ],
            "ar": [
                "اقتصاد", "اقتصادي", "نمو", "ركود", "تضخم", "الناتج المحلي الإجمالي", "السياسة النقدية",
                "السياسة المالية", "أسعار الفائدة", "البنك المركزي", "البطالة", "ثقة المستهلك"
            ]
        }
    },
    "politics": {
        "name": "Politics",
        "keywords": {
            "en": [
                "government", "politics", "policy", "public sector", "regulation", "legislation", "reform",
                "elections", "parliament", "governance", "public spending"
            ],
            "fr": [
                "gouvernement", "politique", "politique publique", "secteur public", "réglementation", "législation",
                "réforme", "élections", "parlement", "gouvernance", "dépenses publiques"
            ],
            "ar": [
                "حكومة", "سياسة", "سياسات عامة", "القطاع العام", "تنظيم", "تشريع", "إصلاح", "انتخابات",
                "برلمان", "حوكمة", "الإنفاق العام"
            ]
        }
    },
    "esg": {
        "name": "ESG",
        "keywords": {
            "en": [
                "sustainability", "ESG", "environment", "social responsibility", "governance", "climate change",
                "carbon", "net zero", "renewable energy", "green finance", "CSR"
            ],
            "fr": [
                "durabilité", "ESG", "environnement", "responsabilité sociale", "governance", "changement climatique",
                "carbone", "neutralité carbone", "énergies renouvelables", "finance verte", "RSE"
            ],
            "ar": [
                "الاستدامة", "ESG", "البيئة", "المسؤولية الاجتماعية", "الحوكمة", "تغير المناخ", "الكربون",
                "الحياد الكربوني", "الطاقة المتجددة", "التمويل الأخضر", "المسؤولية الاجتماعية للشركات"
            ]
        }
    },
    "health": {
        "name": "Health",
        "keywords": {
            "en": [
                "health", "healthcare", "hospital", "medicine", "public health", "pharmaceutical", "biotech",
                "clinical trial", "medical research"
            ],
            "fr": [
                "santé", "soins de santé", "hôpital", "médecine", "santé publique", "pharmaceutique",
                "biotechnologie", "essai clinique", "recherche médicale"
            ],
            "ar": [
                "الصحة", "الرعاية الصحية", "مستشفى", "طب", "الصحة العامة", "الأدوية", "التكنولوجيا الحيوية",
                "تجربة سريرية", "البحث الطبي"
            ]
        }
    },
    "business": {
        "name": "Business",
        "keywords": {
            "en": [
                "company", "corporate", "business", "industry", "enterprise", "merger", "acquisition", "M&A",
                "restructuring", "strategy", "leadership"
            ],
            "fr": [
                "entreprise", "corporate", "affaires", "industrie", "organisation", "fusion", "acquisition",
                "fusions acquisitions", "restructuration", "stratégie", "leadership"
            ],
            "ar": [
                "شركة", "شركات", "أعمال", "صناعة", "مؤسسة", "اندماج", "استحواذ", "اندماجات واستحواذات",
                "إعادة هيكلة", "استراتيجية", "قيادة"
            ]
        }
    },
    "exclude": {
        "name": "Exclude (Celebrity, Sports, etc.)",
        "keywords": {
            "en": [
                "celebrity", "gossip", "sports", "fashion", "entertainment", "lifestyle", "horoscope"
            ],
            "fr": [
                "célébrité", "potins", "sport", "mode", "divertissement", "style de vie", "horoscope"
            ],
            "ar": [
                "مشاهير", "نميمة", "رياضة", "موضة", "ترفيه", "نمط الحياة", "أبراج"
            ]
        }
    }
}


def get_filter_keywords(filter_name):
    """Get all keywords for a filter across all languages"""
    if filter_name == "no_filter" or filter_name not in KEYWORD_FILTERS:
        return []
    
    filter_data = KEYWORD_FILTERS[filter_name]
    keywords = []
    for lang_keywords in filter_data["keywords"].values():
        keywords.extend(lang_keywords)
    return keywords


def matches_filter(text, filter_name):
    """
    Check if text contains any keywords from the specified filter.
    Returns True if text matches filter keywords, False otherwise.
    For 'exclude' filter, returns False if text contains exclude keywords (to exclude it).
    """
    if filter_name == "no_filter" or not filter_name:
        return True  # No filter means accept all
    
    if filter_name not in KEYWORD_FILTERS:
        return True  # Unknown filter, accept by default
    
    filter_data = KEYWORD_FILTERS[filter_name]
    text_lower = text.lower()
    
    # For exclude filter, we want to exclude content that matches
    is_exclude = filter_name == "exclude"
    
    for lang, keywords in filter_data["keywords"].items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                # If exclude filter matches, return False (exclude this content)
                # If other filter matches, return True (include this content)
                return not is_exclude
    
    # If exclude filter and no matches, include it (return True)
    # If other filter and no matches, exclude it (return False)
    return is_exclude


def get_available_filters():
    """Get list of available filters"""
    return [
        {"value": key, "name": value["name"]}
        for key, value in KEYWORD_FILTERS.items()
    ]
