# FitGenie AI — Canva Presentation Guide

> Copy-paste the Canva prompts below directly into **Canva Magic Design** or **Canva Docs AI** to generate slides. Each slide includes design notes for manual fine-tuning.

---

## Slide 1 — Title Slide

**Canva Prompt:**
```
Create a corporate title slide with dark navy background (#0f172a). 
Main title "FitGenie AI" in large bold white font with a subtle gradient accent bar underneath in indigo (#6366f1) fading to emerald (#10b981). 
Subtitle "AI-Powered Fitness Assistant" in lighter gray italic below. 
Bottom right: tagline "Personalized Fitness Through Artificial Intelligence" 
Add a subtle geometric grid pattern overlay in very low opacity.
```

**Content:**
- **FitGenie AI**
- AI-Powered Fitness Assistant
- Personalized Fitness Through Artificial Intelligence
- (Optional: Your Name / Team / Date)

**Design Notes:**
- Font: Montserrat / Inter (bold for title, regular for subtitle)
- Colors: #0f172a background, #6366f1 accent, #10b981 accent, #ffffff text, #94a3b8 subtitle

---

## Slide 2 — Problem & Solution

**Canva Prompt:**
```
Two-column corporate slide. Left column: "The Problem" heading in white, 
text below: "Generic fitness plans don't account for individual needs, medical conditions, or evolving goals. Most apps lack intelligent, personalized guidance." in light gray.
Right column: "The Solution" heading in emerald (#10b981), 
text below: "FitGenie AI delivers real-time, personalized fitness coaching powered by Large Language Models and Retrieval-Augmented Generation (RAG)." in light gray.
Background: dark navy (#0f172a). Thin vertical divider line in indigo between columns.
```

**Content:**
| Problem | Solution |
|---------|----------|
| Generic fitness plans ignore individual needs | AI-driven personalized coaching |
| No real-time adaptation to user progress | RAG-powered contextual responses |
| Lack of medical condition awareness | Profile-based personalized advice |

**Design Notes:**
- Split layout (50/50)
- Problem heading in white, Solution heading in emerald
- Use subtle bullet points or small icon above each column

---

## Slide 3 — Key Features

**Canva Prompt:**
```
Grid layout slide with 6 feature cards (2 rows x 3 columns) on dark navy background (#0f172a). 
Each card has a subtle border in indigo (#6366f1 at 30% opacity), rounded corners, 
an icon placeholder (small circle top-left), a white bold feature name, and light gray description text. 
Features: "User Authentication" | "Fitness Profiles" | "AI Chat" | "BMI Calculator" | "RAG Engine" | "Document Upload". 
Slide title "Key Features" in white bold at top center with an indigo underline accent.
```

**Content:**
- ✅ User Registration & Login — Secure authentication with password hashing
- ✅ Personalized Fitness Profiles — Age, weight, height, goals, medical conditions
- ✅ AI-Powered Chat — Context-aware conversations using Groq Llama 3.3
- ✅ BMI Calculator — Instant BMI with health category and advice
- ✅ RAG Engine — Retrieval-Augmented Generation from uploaded documents
- ✅ Document Upload — Upload custom PDF/TXT files to expand AI knowledge

**Design Notes:**
- Use 3×2 or 4+2 grid
- Each card: rounded corners, subtle border, consistent spacing
- Replace icon placeholders with Canva icons (search: user, dumbbell, chat, calculator, database, upload)

---

## Slide 4 — Technology Stack

**Canva Prompt:**
```
Dark navy (#0f172a) slide titled "Technology Stack" in white bold at top with emerald underline accent. 
Below, show 4 columns representing layers: 
Layer 1 "Frontend" — HTML, CSS, JavaScript icons in white text on small rounded pill badges. 
Layer 2 "Backend" — Python, Flask badges. 
Layer 3 "AI & ML" — Groq Llama 3.3, LangChain, HuggingFace badges. 
Layer 4 "Data & Storage" — ChromaDB, SQLite, SQLAlchemy badges. 
Use subtle upward arrows or connecting lines in indigo between layers. 
Each column header in emerald (#10b981) bold. Badges in white on semi-transparent dark cards.
```

**Content:**
| Frontend | Backend | AI & ML | Data & Storage |
|----------|---------|---------|----------------|
| HTML5 | Python 3 | Groq Llama 3.3 (70B) | ChromaDB (Vector Store) |
| CSS3 (Dark Theme) | Flask 3.0 | LangChain Core | SQLite (Relational DB) |
| Vanilla JavaScript | Flask-Login | HuggingFace Embeddings | SQLAlchemy ORM |
| Responsive Design | Werkzeug | RAG Pipeline | File System (Documents) |

**Design Notes:**
- 4-column layout with column headers in emerald
- Use pill-shaped badges for each technology
- Subtle connecting lines or arrows showing data flow left to right
- Canva icons: code, server, brain, database

---

## Slide 5 — How RAG Works (Pipeline)

**Canva Prompt:**
```
Infographic-style slide on dark navy (#0f172a) titled "Retrieval-Augmented Generation Pipeline" in white bold. 
Show a horizontal 4-step flow from left to right:
Step 1: "Load Documents" (PDF/TXT files) in an indigo rounded box 
→ Step 2: "Split & Embed" (500-char chunks, 100 overlap) in a purple box 
→ Step 3: "ChromaDB Vector Store" (semantic search index) in an emerald box 
→ Step 4: "LLM + Context → Answer" in a gold/amber box.
Connect boxes with arrows. Below each step, add 1-line description in light gray. 
Add a floating note: "User Question → Retrieves Top 3 Chunks → LLM Generates Response"
```

**Content:**
1. **Load Documents** — PDF and TXT files loaded from the `documents/` folder
2. **Split into Chunks** — Text split into 500-character segments with 100-character overlap
3. **Embed & Store** — HuggingFace embeddings vectorized and stored in ChromaDB
4. **Retrieve** — User question retrieves top 3 most relevant chunks via semantic search
5. **Generate** — LangChain passes chunks + question + conversation history to Groq Llama 3.3
6. **Response** — AI generates personalized, context-aware fitness advice

**Design Notes:**
- Horizontal or vertical flow diagram
- Color-code each step (indigo → purple → emerald → amber)
- Keep arrows clean and straight
- Add a small "user question" input icon at the start

---

## Slide 6 — User Journey

**Canva Prompt:**
```
Customer journey map style slide on dark navy (#0f172a) titled "User Journey" in white bold. 
Show 6 circular nodes connected by a horizontal curved line (zigzag or S-curve):
1. "Register" — icon: user-plus
2. "Login" — icon: log-in
3. "Set Profile" — icon: settings/sliders
4. "Dashboard" — icon: layout/dashboard
5. "Chat with AI" — icon: message-circle
6. "Get Results" — icon: check-circle
Nodes in emerald (#10b981) with white text. Connecting line in indigo dashed style.
Below the flow, add 3 benefit callouts in gray boxes: "Personalized" | "Real-time" | "Data-driven"
```

**Content:**
1. **Register** — Create account with name, email, password
2. **Login** — Secure authentication with session management
3. **Set Profile** — Enter age, height, weight, goals, medical conditions
4. **Dashboard** — View BMI, recent chats, fitness summary
5. **Chat with AI** — Ask fitness questions, get personalized answers
6. **Achieve Goals** — Track progress, refine approach, stay motivated

**Design Notes:**
- Circular or hexagonal step nodes connected by arrows
- Use emerald for completed steps, indigo for current step
- Keep text minimal — this is visual

---

## Slide 7 — BMI Calculator

**Canva Prompt:**
```
Data visualization slide on dark navy (#0f172a) titled "BMI Calculator" in white bold with emerald accent. 
Left side: show a large BMI scale/gauge visualization — a semi-circle meter from "Underweight" (blue) through "Normal" (green) to "Overweight" (amber) to "Obese" (red). 
Right side: show a small table with categories:
Category | Range
Underweight | < 18.5
Normal | 18.5 – 24.9
Overweight | 25 – 29.9
Obese | ≥ 30
Table headers in emerald, rows alternating dark gray.
Bottom caption: "BMI = weight(kg) / height(m)² — Screening tool, not diagnostic."
```

**Content:**
- **Formula:** BMI = weight(kg) / height(m)²
- **Categories:**
  | Category | Range | Advice |
  |----------|-------|--------|
  | Underweight | < 18.5 | Nutrient-dense diet, strength training |
  | Normal | 18.5 – 24.9 | Maintain with balanced nutrition |
  | Overweight | 25 – 29.9 | Moderate calorie deficit, increase activity |
  | Obese | ≥ 30 | Consult healthcare provider first |
- Real-time health advice generation based on BMI category

**Design Notes:**
- Left: gauge/scale visualization (Canva: chart > gauge)
- Right: clean data table
- Color the BMI categories on the gauge (blue → green → amber → red)

---

## Slide 8 — AI Chat Demo

**Canva Prompt:**
```
Mockup slide on dark navy (#0f172a) titled "AI Chat in Action" in white bold. 
Show a mobile phone or browser window mockup in the center of the slide.
Inside the mockup, show a dark chat interface with:
- User message bubble (indigo #6366f1): "Create a beginner workout plan for weight loss"
- AI response bubble (dark gray #1e293b with white text): a 3-4 line response about starting with 30min cardio, strength training 3x/week, etc. in light gray text with emerald accent on key terms.
Below the mockup, add caption: "Responses are personalized using the user's fitness profile and RAG-enhanced knowledge base."
Shadow behind mockup for depth. Thin indigo border on mockup frame.
```

**Content:**
> **User:** "Create a beginner workout plan for weight loss"
>
> **FitGenie AI:** "Based on your profile (age 30, female, BMI 27, fitness level: beginner), here's a recommended weekly plan:
> - **Cardio:** 30 min brisk walking or cycling, 4×/week
> - **Strength:** Full-body bodyweight circuit, 3×/week (squats, push-ups, rows, planks)
> - **Nutrition:** Calorie deficit of 300-500/day, focus on lean protein and vegetables
> - **Rest:** 2 full rest days for recovery
> 
> Start with week 1 at 60% intensity and gradually increase. Stay hydrated!"

**Design Notes:**
- Centered phone or browser mockup
- Chat bubbles: user in indigo, AI in dark gray
- Key terms in emerald bold
- Soft shadow on mockup for depth

---

## Slide 9 — Future Roadmap

**Canva Prompt:**
```
Timeline/roadmap slide on dark navy (#0f172a) titled "Roadmap" in white bold at top with indigo line underneath. 
Show a horizontal timeline arrow from left to right with 5 milestone nodes:
Node 1 (Q1 2025): "Voice Assistant" — icon: mic
Node 2 (Q2 2025): "Progress Charts" — icon: bar-chart
Node 3 (Q3 2025): "Video Exercise Detection" — icon: camera
Node 4 (Q4 2025): "Mobile App" — icon: smart phone
Node 5 (2026): "AI Trainer Avatar" — icon: user-check
Nodes above the line in indigo, below the line add short description text in light gray.
Use different colors for completed (emerald) vs planned (indigo) vs future (gray) milestones.
```

**Content:**
- **Q1 2025** — Voice Assistant Integration (hands-free coaching)
- **Q2 2025** — Progress Charts & Analytics (weight, BMI, strength trends)
- **Q3 2025** — Exercise Image/Video Detection (form correction)
- **Q4 2025** — Mobile App (Flutter/React Native)
- **2026** — AI Trainer Avatar, Admin Panel, PDF Report Generation, Calorie Prediction

**Design Notes:**
- Horizontal timeline with milestones
- Color by status: emerald (done/current), indigo (planned), gray (future)
- Icons above nodes, descriptions below

---

## Slide 10 — Thank You / Q&A

**Canva Prompt:**
```
Closing slide on dark navy (#0f172a). 
Large centered "Thank You" or "Questions?" in white bold (size 60+). 
Below, a thin horizontal line in indigo (#6366f1) to emerald (#10b981) gradient. 
Below the line: contact or project info in light gray regular font:
"FitGenie AI — AI-Powered Fitness Assistant"
"Built with Flask, LangChain, Groq & ChromaDB"
Bottom center: a subtle link or QR code placeholder for GitHub repository.
Use very minimal design — let the title breathe with generous whitespace.
```

**Content:**
- **Thank You**
- **Questions?**
- FitGenie AI — AI-Powered Fitness Assistant
- Built with Flask, LangChain, Groq & ChromaDB
- [GitHub Repository Link]
- [Contact / Email]

**Design Notes:**
- Minimal, clean closing slide
- Large "Questions?" as focal point
- Gradient line for visual interest
- QR code placeholder (optional — add actual QR later)

---

## Color Palette Summary

| Role | Hex | Usage |
|------|-----|-------|
| Background | `#0f172a` (Slate 900) | Slide backgrounds |
| Card/Surface | `#1e293b` (Slate 800) | Cards, mockups, badges |
| Primary Accent | `#6366f1` (Indigo 500) | Headers, buttons, borders |
| Secondary Accent | `#10b981` (Emerald 500) | Highlights, keywords, success states |
| Text Primary | `#ffffff` | Titles, headings |
| Text Secondary | `#94a3b8` (Slate 400) | Body text, descriptions |
| Warning | `#f59e0b` (Amber) | BMI overweight category |
| Danger | `#ef4444` (Red) | BMI obese category |

## Typography

- **Titles:** Montserrat Bold or Inter Bold (32–44px)
- **Subtitles/Body:** Inter Regular or Open Sans (16–20px)
- **Captions:** Inter Light (12–14px)

---

*Copy each slide's Canva prompt into **Canva Magic Design** (Text to Image or AI Presentation) to generate matching visuals. Then paste the content into Canva text boxes. Adjust colors using the palette above for a consistent corporate professional look.*
