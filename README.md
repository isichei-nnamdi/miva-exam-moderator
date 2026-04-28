<div align="center">

<img src="assets/miva_logo2.png" alt="Miva Open University Logo" width="80"/>

<br/>
<br/>

# Exam Score Moderator

**A data-driven academic quality assurance platform for Miva Open University**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com/)
[![SciPy](https://img.shields.io/badge/SciPy-1.11%2B-8CAAE6?style=flat-square&logo=scipy&logoColor=white)](https://scipy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-C4A07D?style=flat-square)](LICENSE)

---

*Integrity-aware score adjustment · LMS gradebook moderation · Normality-driven calibration*

</div>

---

## Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Key Features](#-key-features)
- [Application Screenshots](#-application-screenshots)
- [Architecture & Data Flow](#-architecture--data-flow)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
  - [Tab 1 - Result Analysis & Adjustment](#tab-1--result-analysis--adjustment)
  - [Tab 2 - Result Moderation](#tab-2--result-moderation)
- [Input File Specifications](#-input-file-specifications)
- [Grading Scale](#-grading-scale)
- [Statistical Methods](#-statistical-methods)
- [Project Structure](#-project-structure)
- [Dependencies](#-dependencies)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Problem Statement

Academic assessment at scale introduces a set of challenges that are difficult to manage through manual review alone. At Miva Open University, examination scores are generated through an online portal and must be reconciled with the Learning Management System (LMS) gradebook - a process that is both error-prone and time-intensive when performed manually.

Three specific pain points motivated the development of this tool:

**1. Integrity Risk in Online Examinations**
Online assessments are vulnerable to integrity breaches. Students who engage in suspicious behaviour often receive inflated scores that misrepresent their true performance. Without a systematic mechanism to identify and penalise such cases, final results are unreliable.

**2. Fragmented Score Pipelines**
Examination scores from the portal and component scores from the LMS (continuous assessment, quizzes, assignments) exist in separate systems. Manually combining these into a final moderated score is labour-intensive and error-prone at cohort scale.

**3. Non-Normal Score Distributions**
Raw aggregated scores frequently exhibit significant skewness - either right-skewed (most students failing) or left-skewed (scores clustered at the high end). Such distributions can indicate systematic difficulty bias in the exam, and correcting them requires statistically informed calibration rather than ad hoc adjustments.

This platform addresses all three problems within a single, auditable workflow.

---

## 💡 Solution Overview

The **Miva Exam Score Moderator** is a two-stage web application built with Streamlit that provides examination administrators and academic moderators with:

- A **result analysis dashboard** with integrity-based score adjustment
- A **LMS moderation engine** that reconciles portal scores with gradebook components and calibrates the final distribution toward normality

All adjustments are fully traceable, reversible within the session, and exportable as clean CSV files ready for LMS re-import.

---

## ✨ Key Features

### Result Analysis & Adjustment (Tab 1)

| Feature | Description |
|--------|-------------|
| 📊 **KPI Dashboard** | Eight key performance indicators including total enrolment, pass/fail rates, average score, CA eligibility, and LMS sync status |
| 📈 **Distribution Charts** | Six interactive Plotly charts: score histogram with KDE overlay, grade status breakdown, risk level distribution, integrity score distribution, programme intake analysis, and grade-boxplot |
| 🔍 **Integrity Flagging** | Configurable integrity score threshold, `is_risk` flag detection, and `risk_level` (High/Medium) filtering - all combinable with boolean logic |
| ✏️ **Individual Overrides** | Editable data table for per-student deduction control alongside a bulk deduction that applies to all flagged students |
| 📉 **Before/After View** | Overlaid histogram and summary statistics comparing pre- and post-adjustment distributions |
| ⬇️ **Export** | One-click download of the adjusted score sheet as a clean CSV file |

### Result Moderation (Tab 2)

| Feature | Description |
|--------|-------------|
| 🔗 **Dual-file Ingestion** | Upload the LMS gradebook and exam portal sheet independently; both are cached for the session |
| ⚙️ **Guided Field Picker** | Four-step configuration: select component columns to sum, choose the exam column to replace, specify the portal score source, and set the student ID join keys |
| 🔄 **Score Reconciliation** | Portal exam scores replace the corresponding gradebook column matched by student ID; unmatched records are flagged and counted |
| 📐 **Normality Analysis** | Shapiro-Wilk test (n ≤ 5,000) or D'Agostino-Pearson (n > 5,000), Q-Q plot, skewness, excess kurtosis, and a plain-language recommendation |
| 🤖 **Statistical Suggestion** | Automatically suggests the optimal shift magnitude and direction (add/subtract) based on skewness × standard deviation |
| 📏 **Uniform Shift** | Apply a fixed mark delta to all students with suggestion pre-filled from the normality report |
| 🎯 **Band-based Adjustment** | Define up to 5 custom score ranges, each with an independent direction and delta - ideal for targeted normalisation of specific performance tiers |
| 📊 **Grade Distribution** | Per-grade KPI cards (A–F) with count and percentage, and a grouped before/after bar chart for every adjustment applied |
| ⬇️ **Export** | Download the fully moderated gradebook (including the computed `_total_score` column) as a CSV |

---

## 📸 Application Screenshots

### Dashboard Overview - Tab 1

```
<img width="722" height="537" alt="image" src="https://github.com/user-attachments/assets/5cf01e5b-5ed9-467e-afb2-8dc61b94b4bc" />

```

---

### Integrity Flagging & Score Adjustment - Tab 1

> **📌 Screenshot placeholder**
> *Replace this block with a screenshot of the Score Adjustment section showing the integrity threshold slider, flagged candidates table, and before/after histogram.*
>
> Suggested filename: `docs/screenshots/tab1_adjustment.png`

```
![Tab 1 – Score Adjustment](docs/screenshots/tab1_adjustment.png)
```

---

### Field Configuration & Moderation Setup - Tab 2

> **📌 Screenshot placeholder**
> *Replace this block with a screenshot of the Tab 2 field configuration panel showing the four-step selector.*
>
> Suggested filename: `docs/screenshots/tab2_config.png`

```
![Tab 2 – Field Configuration](docs/screenshots/tab2_config.png)
```

---

### Normality Analysis & Statistical Suggestion - Tab 2

> **📌 Screenshot placeholder**
> *Replace this block with a screenshot of the normality KPI panel, Q-Q plot, and the recommendation callout.*
>
> Suggested filename: `docs/screenshots/tab2_normality.png`

```
![Tab 2 – Normality Analysis](docs/screenshots/tab2_normality.png)
```

---

### Band-Based Score Adjustment - Tab 2

> **📌 Screenshot placeholder**
> *Replace this block with a screenshot of the band-based adjustment panel showing 3–5 configured bands with their live KPI previews.*
>
> Suggested filename: `docs/screenshots/tab2_band_adjustment.png`

```
![Tab 2 – Band-Based Adjustment](docs/screenshots/tab2_band_adjustment.png)
```

---

### Grade Distribution: Before vs After - Tab 2

> **📌 Screenshot placeholder**
> *Replace this block with a screenshot of the grouped grade distribution bar chart showing before/after counts per grade (A–F).*
>
> Suggested filename: `docs/screenshots/tab2_grade_distribution.png`

```
![Tab 2 – Grade Distribution](docs/screenshots/tab2_grade_distribution.png)
```

---

## 🏗️ Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE (Streamlit)                 │
│                                                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐ │
│  │  TAB 1                   │  │  TAB 2                       │ │
│  │  Result Analysis         │  │  Result Moderation           │ │
│  │  & Adjustment            │  │                              │ │
│  └────────────┬─────────────┘  └──────────────┬───────────────┘ │
└───────────────┼──────────────────────────────── ┼───────────────┘
                │                                 │
                ▼                                 ▼
┌──────────────────────┐            ┌─────────────────────────────┐
│  Exam Portal Sheet   │            │  LMS Gradebook              │
│  (CSV / Excel)       │            │  (CSV / Excel)              │
│                      │            │                             │
│  student_id          │            │  Student ID column          │
│  score / score_%     │            │  CA / Quiz / Assignment     │
│  integrity_score     │            │  Exam score column          │
│  is_risk             │            │  (to be replaced)           │
│  risk_level          │            └──────────────┬──────────────┘
│  grade_status        │                           │
└──────────┬───────────┘            ┌──────────────▼──────────────┐
           │                        │  Score Reconciliation       │
           │                        │  Portal score → Gradebook   │
           │                        │  (joined on student ID)     │
           │                        └──────────────┬──────────────┘
           │                                       │
           ▼                                       ▼
┌──────────────────────┐            ┌─────────────────────────────┐
│  Integrity Engine    │            │  Aggregation Engine         │
│                      │            │                             │
│  • Flag by threshold │            │  _total_score =             │
│  • Flag by is_risk   │            │  Σ(CA + quiz + assignment   │
│  • Flag by risk_level│            │    + replaced exam score)   │
│  • Bulk deduction    │            └──────────────┬──────────────┘
│  • Individual overrides           │
└──────────┬───────────┘            ▼
           │              ┌──────────────────────────┐
           │              │  Normality Engine         │
           │              │                           │
           │              │  • Shapiro-Wilk / D'AP   │
           │              │  • Skewness + Kurtosis   │
           │              │  • Q-Q Plot              │
           │              │  • Statistical suggestion │
           │              │  • Uniform shift          │
           │              │  • Band-based adjustment  │
           │              └──────────────┬────────────┘
           │                             │
           ▼                             ▼
┌──────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                           │
│                                                          │
│  adjusted_exam_scores.csv    moderated_gradebook.csv     │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Clone the Repository

```bash
git clone https://github.com/<your-username>/miva-exam-moderator.git
cd miva-exam-moderator
```

### Install Dependencies

It is strongly recommended to use a virtual environment:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# Install all dependencies
pip install -r requirements.txt
```

### Verify Assets

Ensure the Miva logo is present in the `assets/` folder:

```
assets/
└── miva_logo.png    ← transparent background PNG (required for header & favicon)
```

### Launch the Application

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 📖 Usage Guide

### Tab 1 - Result Analysis & Adjustment

#### Step 1: Upload the Exam Portal Export

Upload a CSV or Excel file exported from the examination portal. The file should contain the columns described in the [Input File Specifications](#-input-file-specifications) section. Both `.csv` and `.xlsx/.xls` formats are supported.

> The file is cached by name and size for the duration of the session. Uploading the same file again after making changes will not reset your adjustments.

#### Step 2: Review the Dashboard

Once uploaded, the dashboard automatically populates with:

- **Row 1 KPIs** - Total registered students, Pass count (score ≥ 40), Fail count, Average score with median
- **Row 2 KPIs** - Total graded students, Flagged (`is_risk`) count, CA-eligible count, LMS-synced count
- **Charts** - Six interactive Plotly visualisations covering score distribution, grade status, risk levels, integrity scores, programme breakdown, and grade-score box plots

All charts use KDE (Kernel Density Estimation) overlays where applicable for a clearer picture of the underlying distribution shape.

#### Step 3: Configure the Integrity Filter

Under **Score Adjustment**, configure the flagging criteria:

| Control | Description |
|---------|-------------|
| **Integrity Score threshold** | Students with `integrity_score` ≤ this value are flagged |
| **Exam Score threshold** | Only flags students who also scored ≥ this value (avoids penalising already-failing students) |
| **Flag `is_risk = True`** | Includes any student explicitly marked as a risk |
| **Flag `risk_level = High/Medium`** | Includes students by risk category |
| **Bulk deduction (marks)** | The mark reduction applied to all flagged students unless overridden |

#### Step 4: Apply Adjustments

The **Flagged Candidates** table appears with every student matching the active criteria. The `deduction_marks` column is editable - set any positive value to override the bulk deduction for that individual student. Leave it at `0` to use the bulk value.

Click **⚡ Apply Adjustments** to execute. A before/after histogram overlay and summary statistics will appear immediately below.

#### Step 5: Download

Click **⬇️ Download Adjusted Score Sheet** to export the result as `adjusted_exam_scores.csv`.

---

### Tab 2 - Result Moderation

#### Step 1: Upload Both Files

| File | Description |
|------|-------------|
| **LMS Gradebook** | The full gradebook from your LMS containing all score components |
| **Exam Portal Sheet** | Either the raw portal export or the adjusted sheet downloaded from Tab 1 |

#### Step 2: Configure Field Mapping

Complete the four-step field picker:

1. **Columns to SUM** - Select all numeric gradebook columns that contribute to the final score (CA, quiz, assignment, etc.)
2. **Exam column to REPLACE** - The gradebook column whose values will be overwritten by portal scores
3. **Portal score column** - The column from the portal sheet that supplies the replacement values
4. **Student ID join keys** - The matching columns in each file used to align records

Click **🚀 Run Moderation** to execute the reconciliation.

#### Step 3: Review the Normality Report

After running, the app computes `_total_score = Σ(selected components + replaced exam score)` for every matched record and presents:

- **Normality test** (Shapiro-Wilk or D'Agostino-Pearson depending on sample size)
- **Skewness and kurtosis** with directional interpretation
- **Q-Q plot** for visual normality assessment
- **Statistical recommendation** - a pre-calculated suggested shift with projected mean after application

#### Step 4: Apply a Global Adjustment (Optional)

Choose between two adjustment modes:

**📏 Uniform Shift**
Applies the same mark delta to every student's exam score. The suggestion from the normality report is pre-filled as the default value.

**🎯 Band-Based Adjustment**
Define up to 5 score bands (e.g., 0–40, 40–60, 60–80) and assign independent deltas per band. A live KPI row shows how many students fall into each band before you apply. This mode is ideal for:
- Providing a larger boost to students who narrowly failed
- Applying no adjustment to high performers
- Correcting specific tiers of a bimodal distribution

> Only the exam score column is modified in both modes. The `_total_score` is recalculated automatically from the updated exam column plus all selected component columns.

#### Step 5: Verify the Grade Distribution

Every adjustment renders:
- A **KPI row** with count and percentage per grade (A–F) including ↑/↓ indicators showing the change from before
- A **grouped bar chart** with before/after bars side-by-side for visual comparison
- An **updated normality callout** showing the new skewness, mean, and test p-value

#### Step 6: Download

Click **⬇️ Download Moderated Gradebook** to export the complete moderated LMS gradebook as `moderated_gradebook.csv`, including the `_total_score` column ready for LMS re-import.

---

## 📋 Input File Specifications

### Exam Portal Sheet (Tab 1 & Tab 2)

| Column | Type | Description |
|--------|------|-------------|
| `student_id` | String / Integer | Unique student identifier |
| `matric_number` | String | Student matriculation number |
| `first_name` | String | Student first name |
| `last_name` | String | Student last name |
| `email` | String | Student email address |
| `level` | String / Integer | Academic level (e.g., 100, 200) |
| `programme_intake` | String | Programme and intake cohort label |
| `course` | String | Course code or name |
| `score_percentage` | Float | Exam score as a percentage (0–100) |
| `score` | Float | Raw exam score (used if `score_percentage` absent) |
| `grade_status` | String | Grading status - `GRADED`, `PENDING`, etc. |
| `lms_sync_status` | String | Whether the score has been synced to the LMS |
| `ca_eligibility` | Boolean | Whether the student met the CA requirement |
| `integrity_score` | Float | Integrity/proctoring score (0–100; higher = more trustworthy) |
| `is_risk` | Boolean | Explicit risk flag from the proctoring system |
| `risk_level` | String | Risk classification: `High`, `Medium`, `Low`, `None` |
| `result_status` | String | Overall result status |
| `name` | String | Full name (optional, used for display) |

> **Note:** Columns with `-` or empty values are automatically detected and converted to `NaN` to ensure numeric operations work correctly.

### LMS Gradebook (Tab 2)

The gradebook can have any column structure. The only requirements are:

- At least one **student identifier column** (matric number, student ID, email, etc.) that matches the portal sheet
- At least one **numeric column** for each score component you wish to aggregate
- A **numeric exam score column** that will be replaced by portal values

---

## 🎓 Grading Scale

The application applies Miva Open University's standard grading scale when computing grade distributions:

| Grade | Score Range | Classification |
|-------|-------------|----------------|
| **A** | 70 – 100 | Distinction |
| **B** | 60 – 69 | Credit |
| **C** | 50 – 59 | Pass |
| **D** | 45 – 49 | Low Pass |
| **E** | 40 – 44 | Marginal Pass |
| **F** | 0 – 39 | Fail |

> Grades are always computed from `_total_score` (the final aggregated score), never from an individual component column.

---

## 📐 Statistical Methods

### Normality Testing

The application selects the appropriate test automatically based on sample size:

| Sample Size | Test Applied | Rationale |
|-------------|-------------|-----------|
| 8 – 5,000 | **Shapiro-Wilk** | Most powerful omnibus test for small-to-medium samples |
| > 5,000 | **D'Agostino-Pearson** | Robust for large samples; tests skewness and kurtosis jointly |

A p-value > 0.05 indicates the distribution does not significantly deviate from normality at the 5% significance level.

### Statistical Suggestion Algorithm

The suggested uniform mark shift is calculated as:

```
suggested_shift = round(|skewness| × σ × 0.45, nearest 0.5)
```

Where:
- `skewness` is the Pearson skewness of `_total_score`
- `σ` is the standard deviation of `_total_score`
- The result is clamped to the range **[0.5, 20.0]** marks

**Direction:**
- Positive skewness (right-skewed, scores cluster low) → **Add marks**
- Negative skewness (left-skewed, scores cluster high) → **Subtract marks**

### KDE Overlay

All score histograms include a Gaussian KDE (Kernel Density Estimation) trace computed via `scipy.stats.gaussian_kde`. The KDE is scaled to match histogram bar heights for visual comparability.

### Q-Q Plot

The Q-Q (Quantile-Quantile) plot compares sample quantiles against theoretical normal distribution quantiles. Deviation from the reference line indicates the nature and severity of non-normality.

---

## 📁 Project Structure

```
miva-exam-moderator/
│
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── LICENSE                   # MIT License
│
├── assets/
│   └── miva_logo.png         # Transparent Miva "M" logo (required)
│
└── docs/
    └── screenshots/          # Add your app screenshots here
        ├── tab1_dashboard.png
        ├── tab1_adjustment.png
        ├── tab2_config.png
        ├── tab2_normality.png
        ├── tab2_band_adjustment.png
        └── tab2_grade_distribution.png
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥ 1.32.0 | Web application framework |
| `pandas` | ≥ 2.0.0 | Data ingestion and manipulation |
| `numpy` | ≥ 1.24.0 | Numerical operations and array masking |
| `plotly` | ≥ 5.18.0 | Interactive visualisations |
| `scipy` | ≥ 1.11.0 | Statistical testing and KDE |
| `Pillow` | ≥ 10.0.0 | Logo image processing and transparency |
| `openpyxl` | ≥ 3.1.0 | Excel `.xlsx` read support |
| `xlrd` | ≥ 2.0.0 | Legacy Excel `.xls` read support |

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome. Please follow the steps below:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Commit** your changes with clear, descriptive messages: `git commit -m "feat: add per-course moderation support"`
4. **Push** to your branch: `git push origin feature/your-feature-name`
5. **Open** a Pull Request against `main` with a description of the changes and their rationale

### Coding Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python style
- Add docstrings to all new functions using the existing format
- Test with both CSV and Excel inputs before submitting
- Ensure the app runs without errors from a clean `streamlit run app.py`

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full terms.

---

## 🏛️ About Miva Open University

[Miva Open University](https://miva.university) is a technology-first higher education institution committed to making world-class university education accessible across Africa. This tool was developed internally to support the academic quality assurance function of the School of Computing and other academic units.

---

<div align="center">

**Built for Miva Open University · Academic Quality Assurance**

<img src="assets/miva_logo2.png" alt="Miva Open University" width="40"/>

<br/>

*Empowering data-driven academic decisions*

</div>
