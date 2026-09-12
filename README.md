# 🛡️ GoalSafe AI

## Goal-Driven Visual Safety Assessment

GoalSafe AI is an AI-powered visual safety assistant that evaluates an image based on a **user-defined safety goal**.

Instead of treating every visible object as a hazard, GoalSafe AI evaluates the **visible condition** and checks whether it is relevant to the user's specific safety goal.

---

## 🎯 Problem

An object visible in an image is not automatically a safety hazard.

For example:

- A gas burner is not automatically a fire hazard.
- A box is not automatically a trip hazard.
- A ladder is not automatically unsafe.
- An electrical cable is not automatically a trip hazard.

The relevance of an object depends on the **user's safety goal and the visible condition**.

GoalSafe AI addresses this by combining **visual evidence extraction** with **goal-aware deterministic verification**.

---

## 💡 Core Idea

> **An object is not automatically a hazard. A visible condition becomes relevant only when it matches the user's safety goal.**

For example:

**Safety Goal:**

> Check this area for trip hazards.

**Image:**

An electrical cable is visible on the floor.

**Assessment:**

The system evaluates whether the cable visibly creates an obstruction or trip condition before classifying it as a trip hazard.

This allows GoalSafe AI to distinguish between:

- What is visible
- What condition exists
- What the user is concerned about
- Whether the condition matches that concern

---

## 🔄 How It Works

```text
          Image + Safety Goal
                   │
                   ▼
            Gemini Vision
                   │
                   ▼
        Visible Facts & Condition
                   │
                   ▼
       Python Goal-Aware Verification
                   │
                   ▼
          HAZARD / NO_HAZARD
                   │
                   ▼
        Evidence + Safety Guidance
```

Gemini analyzes the uploaded image and returns structured visual information. Python then performs goal matching and deterministic safety verification before producing the final decision.

---

## 🧠 Decision Logic

The final hazard decision follows:

```text
HAZARD =
Goal Match
AND
Unsafe Condition
AND
Sufficient Evidence
```

This helps prevent the system from treating every detected object as a hazard without considering the user's specific safety goal.

---

## 🎯 Supported Safety Goals

GoalSafe AI currently supports goal-aware assessment for:

| Safety Goal | Relevant Conditions |
|---|---|
| Trip | Obstruction, exposure, spill |
| Slip | Spill, obstruction |
| Electrical | Electrical exposure, abnormality, damage |
| Fire / Smoke | Fire or smoke conditions |
| Structural | Structural abnormality, damage |
| Damage | Damage, electrical abnormality, structural abnormality |

The final classification depends on the user's goal and the visible evidence in the image.

---

## 🧪 Example Assessments

### Trip Hazard

**Goal:** Check this area for trip hazards.

**Visible condition:** Cable creating an obstruction across a walkway.

**Result:**

```text
HAZARD
Reason: OBSTRUCTION
```

### Electrical Hazard

**Goal:** Check this area for electrical hazards.

**Visible condition:** Water spill with no visible electrical equipment.

**Result:**

```text
NO_HAZARD
```

The visible spill is not classified as an electrical hazard because no relevant electrical condition is present.

### Normal Operation

**Goal:** Check this area for trip hazards.

**Visible condition:** Normal blue cooking flame.

**Result:**

```text
NO_HAZARD
```

No relevant trip condition is visible.

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Google Gemini API**
- **Gemini 3.1 Flash-Lite**
- **Pydantic**
- **Pillow**
- **python-dotenv**
- **Git & GitHub**
- **Streamlit Community Cloud**

---

## 🏗️ Project Structure

```text
GoalSafe-AI/
│
├── app/
│   ├── main.py
│   └── hazard_verifier.py
│
├── tests/
│
├── .streamlit/
│   └── config.toml
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🔐 Security

The Gemini API key is not stored in the source code.

For local development, environment variables are used.

For deployment, the API key is stored using Streamlit Secrets.

Sensitive configuration files such as `.env` and `secrets.toml` are excluded through `.gitignore`.

---

## ☁️ Deployment

GoalSafe AI is deployed as a web application using **Streamlit Community Cloud**.

```text
Local Development
       ↓
     Git
       ↓
    GitHub
       ↓
Streamlit Cloud
       ↓
   Web Application
```

---

## 🧪 Validation

The MVP was validated using multiple visual safety scenarios:

- Wet floor / puddle with a slip-hazard goal
- Wet floor with an electrical-hazard goal
- Cable across a walkway with a trip-hazard goal
- Wall or ceiling crack with a trip-hazard goal
- Normal stove flame with a trip-hazard goal

These tests verify that the system considers the **user's safety goal, visible condition, and available evidence** before producing a final decision.

---

## ⚠️ Limitations

- Assessment is based only on **visible evidence** in the uploaded image.
- Hidden or non-visible hazards cannot be verified.
- The system is not a replacement for professional safety inspection.
- Assessment history currently uses session-based storage and is not persisted in a database.

---

## 🚀 Future Improvements

- Persistent assessment history
- Additional safety-goal categories
- Improved evidence visualization
- User feedback and assessment correction
- Database integration
- Larger safety validation datasets
- Production-grade authentication and monitoring

---

## 📌 Project Status

**MVP Completed and Deployed**

GoalSafe AI demonstrates how multimodal AI can be combined with deterministic program logic to create a **goal-aware visual safety assessment system**.

---

## ⚠️ Disclaimer

GoalSafe AI provides an AI-based visual assessment based on visible evidence and should not replace professional safety inspection.