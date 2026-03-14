"""
Agent 1 – Structural Parser Prompt
Few-shot examples for high-precision resume parsing using LangChain FewShotPromptTemplate.
"""

PARSER_PREFIX = """You are an expert resume parsing AI with 10+ years of experience in talent acquisition and HR tech.
Your task is to extract structured information from raw resume text with extremely high precision.

RULES:
- Always return ONLY a valid JSON object — no markdown, no explanation, no surrounding text.
- Extract ALL technical skills explicitly mentioned, including tools, languages, frameworks, platforms.
- If a field is missing from the resume, use an empty list [] or empty string "".
- Normalize skill names to their canonical form (e.g. "JS" → "JavaScript", "ML" → "Machine Learning").
- For achievements, preserve quantified metrics EXACTLY as written (e.g. "reduced latency by 40%").
- Education: extract degree level, field, institution, and graduation year if available.

Study the following examples carefully before parsing the target resume:"""

PARSER_EXAMPLES = [
    {
        "resume_snippet": """John Doe | johndoe@gmail.com | linkedin.com/in/johndoe | +1-555-0100 | San Francisco, CA

SUMMARY
Full-stack engineer with 4 years of experience building scalable web applications. Passionate about clean code and distributed systems.

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, SQL
Frameworks: FastAPI, React, Node.js, Express
Databases: PostgreSQL, Redis, MongoDB
Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, GitHub Actions

EXPERIENCE
Senior Software Engineer | TechCorp Inc. | Jan 2022 – Present
- Engineered microservices architecture serving 1M+ daily active users
- Reduced API latency by 45% through Redis caching and query optimization
- Led migration from monolith to Kubernetes, cutting infrastructure costs by $120K/year
- Mentored 3 junior engineers and established code review processes

Software Engineer | StartupXYZ | Jun 2020 – Dec 2021
- Built RESTful APIs using FastAPI and PostgreSQL for fintech application
- Implemented CI/CD pipelines using GitHub Actions, reducing deployment time by 60%

EDUCATION
B.Sc. Computer Science | Stanford University | 2020

CERTIFICATIONS
AWS Certified Solutions Architect – Associate (2023)""",
        "output": """{
  "name": "John Doe",
  "contact": {
    "email": "johndoe@gmail.com",
    "phone": "+1-555-0100",
    "linkedin": "linkedin.com/in/johndoe",
    "location": "San Francisco, CA"
  },
  "summary": "Full-stack engineer with 4 years of experience building scalable web applications. Passionate about clean code and distributed systems.",
  "skills": {
    "languages": ["Python", "JavaScript", "TypeScript", "SQL"],
    "frameworks": ["FastAPI", "React", "Node.js", "Express"],
    "databases": ["PostgreSQL", "Redis", "MongoDB"],
    "cloud_devops": ["AWS", "EC2", "S3", "Lambda", "Docker", "Kubernetes", "GitHub Actions"],
    "soft_skills": ["mentoring", "code review", "team leadership"]
  },
  "experience": [
    {
      "title": "Senior Software Engineer",
      "company": "TechCorp Inc.",
      "duration": "Jan 2022 – Present",
      "years": 2,
      "achievements": [
        "Engineered microservices architecture serving 1M+ daily active users",
        "Reduced API latency by 45% through Redis caching and query optimization",
        "Led migration from monolith to Kubernetes, cutting infrastructure costs by $120K/year",
        "Mentored 3 junior engineers and established code review processes"
      ]
    },
    {
      "title": "Software Engineer",
      "company": "StartupXYZ",
      "duration": "Jun 2020 – Dec 2021",
      "years": 1.5,
      "achievements": [
        "Built RESTful APIs using FastAPI and PostgreSQL for fintech application",
        "Implemented CI/CD pipelines using GitHub Actions, reducing deployment time by 60%"
      ]
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "institution": "Stanford University",
      "graduation_year": "2020"
    }
  ],
  "certifications": ["AWS Certified Solutions Architect – Associate (2023)"],
  "total_experience_years": 3.5,
  "keywords": ["Python", "JavaScript", "TypeScript", "FastAPI", "React", "PostgreSQL", "Redis", "Docker", "Kubernetes", "AWS", "Microservices", "CI/CD", "REST API"]
}"""
    },
    {
        "resume_snippet": """Priya Sharma | priya.sharma@email.com | github.com/priyasharma

OBJECTIVE
Data Scientist with 2 years of experience in NLP and predictive modeling seeking ML Engineer role.

SKILLS
Python, R, TensorFlow, PyTorch, scikit-learn, Pandas, NumPy, SQL, Tableau, Spark, FAISS, LangChain, Hugging Face

WORK EXPERIENCE
Data Scientist | Analytics Corp | Jul 2022 – Present
- Developed NLP sentiment analysis model achieving 92% accuracy on 50K+ reviews
- Built recommendation engine using collaborative filtering, increasing CTR by 28%
- Deployed models using FastAPI and Docker on AWS SageMaker

Research Intern | IIT Bombay AI Lab | Jan 2022 – Jun 2022
- Implemented transformer-based text classification using Hugging Face

EDUCATION
M.Sc. Data Science | IIT Bombay | 2022
B.Sc. Statistics | University of Mumbai | 2020""",
        "output": """{
  "name": "Priya Sharma",
  "contact": {
    "email": "priya.sharma@email.com",
    "phone": "",
    "linkedin": "",
    "github": "github.com/priyasharma",
    "location": ""
  },
  "summary": "Data Scientist with 2 years of experience in NLP and predictive modeling seeking ML Engineer role.",
  "skills": {
    "languages": ["Python", "R", "SQL"],
    "frameworks": ["TensorFlow", "PyTorch", "scikit-learn", "LangChain", "Hugging Face"],
    "data_tools": ["Pandas", "NumPy", "Tableau", "Spark"],
    "vector_databases": ["FAISS"],
    "cloud_devops": ["AWS SageMaker", "Docker", "FastAPI"],
    "soft_skills": []
  },
  "experience": [
    {
      "title": "Data Scientist",
      "company": "Analytics Corp",
      "duration": "Jul 2022 – Present",
      "years": 2,
      "achievements": [
        "Developed NLP sentiment analysis model achieving 92% accuracy on 50K+ reviews",
        "Built recommendation engine using collaborative filtering, increasing CTR by 28%",
        "Deployed models using FastAPI and Docker on AWS SageMaker"
      ]
    },
    {
      "title": "Research Intern",
      "company": "IIT Bombay AI Lab",
      "duration": "Jan 2022 – Jun 2022",
      "years": 0.5,
      "achievements": [
        "Implemented transformer-based text classification using Hugging Face"
      ]
    }
  ],
  "education": [
    {
      "degree": "Master of Science",
      "field": "Data Science",
      "institution": "IIT Bombay",
      "graduation_year": "2022"
    },
    {
      "degree": "Bachelor of Science",
      "field": "Statistics",
      "institution": "University of Mumbai",
      "graduation_year": "2020"
    }
  ],
  "certifications": [],
  "total_experience_years": 2,
  "keywords": ["Python", "NLP", "TensorFlow", "PyTorch", "scikit-learn", "FAISS", "LangChain", "Hugging Face", "Pandas", "SQL", "AWS SageMaker", "Docker", "Machine Learning", "Deep Learning"]
}"""
    },
    {
        "resume_snippet": """Alex Rivera | alex.rivera@email.com | New York, NY

No formal summary provided.

Technologies Used: Java, Spring Boot, MySQL, HTML, CSS
Worked at Google for 5 years as a backend dev.
Did some AWS stuff.
Got a degree from NYU in CS.""",
        "output": """{
  "name": "Alex Rivera",
  "contact": {
    "email": "alex.rivera@email.com",
    "phone": "",
    "linkedin": "",
    "location": "New York, NY"
  },
  "summary": "",
  "skills": {
    "languages": ["Java", "HTML", "CSS"],
    "frameworks": ["Spring Boot"],
    "databases": ["MySQL"],
    "cloud_devops": ["AWS"],
    "soft_skills": []
  },
  "experience": [
    {
      "title": "Backend Developer",
      "company": "Google",
      "duration": "5 years",
      "years": 5,
      "achievements": []
    }
  ],
  "education": [
    {
      "degree": "Bachelor's",
      "field": "Computer Science",
      "institution": "NYU",
      "graduation_year": ""
    }
  ],
  "certifications": [],
  "total_experience_years": 5,
  "keywords": ["Java", "Spring Boot", "MySQL", "AWS", "Backend Development"]
}"""
    }
]
