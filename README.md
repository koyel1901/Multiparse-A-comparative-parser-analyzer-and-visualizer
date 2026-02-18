# 🚀 Multiparse – A Comparative Parser Analyzer and Visualizer

Multiparse is an educational compiler design project that implements and compares multiple parsing techniques in a unified framework.

The goal of this project is to bridge the gap between theoretical parsing concepts and practical implementation by providing step-by-step simulation and comparative analysis of different parsing strategies.

---

## 📌 Project Objective

Parsing is a core component of compilers and interpreters. However, understanding the differences between top-down and bottom-up parsing strategies can be challenging when studied purely theoretically.

Multiparse provides:

- Implementation of multiple parsing algorithms
- Automatic FIRST and FOLLOW computation
- Parsing table construction
- Conflict detection
- Stack-based parsing simulation
- Comparative analysis between parsing techniques

---

## 🧠 Parsing Techniques Covered

### 🔹 LL(1) – Predictive Parsing (Top-Down)
- FIRST & FOLLOW computation
- Predictive parsing table
- Stack-based simulation
- Conflict detection

### 🔹 LR(0) – Bottom-Up Parsing
- Augmented grammar
- Closure function
- GOTO function
- Canonical collection of LR(0) items
- Shift-reduce parsing

### 🔹 SLR(1) – Simple LR Parsing
- LR(0) item reuse
- FOLLOW-based reduction filtering
- Improved conflict resolution

---

## ⚙️ Core Components

### 1️⃣ Grammar Module
- Stores productions
- Identifies terminals & non-terminals
- Manages start symbol

### 2️⃣ FIRST & FOLLOW Module
- Uses fixed-point iterative algorithm
- Handles epsilon propagation
- Supports LL(1) and SLR(1)

### 3️⃣ LL(1) Engine
- Predictive parsing table
- Conflict detection
- Stack simulation
- Accept / Reject validation

### 4️⃣ LR(0) Engine
- Grammar augmentation
- Closure computation
- GOTO transitions
- Canonical collection of items
- Shift-reduce parsing

### 5️⃣ SLR(1) Extension
- Reuses LR(0) states
- Applies FOLLOW-based reduction rules
- Reduces conflicts compared to LR(0)

### 6️⃣ Comparative Layer
- Number of states comparison
- Table size comparison
- Conflict count analysis
- Parsing step comparison

---



