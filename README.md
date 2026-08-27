# 🛡️ GoalSafe AI

## Goal-Driven Visual Safety Assessment

GoalSafe AI is an AI-powered visual safety assistant that evaluates an image based on a **user-defined safety goal**.

Instead of treating every potentially dangerous object as a hazard, GoalSafe AI focuses on the **visible condition** and determines whether that condition is relevant to the user's specific safety goal.

---

## 🎯 Problem

Traditional image-based safety systems may identify objects without understanding whether they are actually relevant to a particular safety concern.

For example:

- A gas burner is not automatically a hazard.
- A box is not automatically a hazard.
- A ladder is not automatically a hazard.
- An electrical cable is not automatically a trip hazard.

The relevance of an object depends on the **user's safety goal and the visible condition**.

GoalSafe AI addresses this by combining **visual evidence extraction** with **goal-aware deterministic verification**.

---

## 💡 Core Idea

GoalSafe AI follows a simple principle:

> **An object is not automatically a hazard. A visible condition becomes relevant only when it matches the user's safety goal.**

For example:

### Safety Goal
> "Check this area for trip hazards."

### Image
An electrical cable is visible on the floor.

### Assessment
If the cable does not visibly create a significant obstruction or trip condition, GoalSafe AI should not automatically classify it as a trip hazard.

This allows the system to distinguish between:

- What is visible
- What condition exists
- What the user is concerned about
- Whether the condition actually matches that concern

---

## 🔄 How It Works

```text
User Safety Goal
       +
     Image
       ↓
  Gemma Vision
       ↓
  Visible Facts
       ↓
Visible Condition
       ↓
   Goal Match
       ↓
Python Safety Verification
       ↓
   Final Decision
       ↓
Evidence + Safety Guidance