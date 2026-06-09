<div align="center">

# ⬡ TrafficAI
### Detection of Severity in Traffic Accidents

![Status](https://img.shields.io/badge/status-active-3fb850?style=flat-square)
![Language](https://img.shields.io/badge/language-HTML%20%7C%20CSS%20%7C%20JS-3b82f6?style=flat-square)
![Model](https://img.shields.io/badge/model-Orange%20Data%20Mining-f97316?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-7d8590?style=flat-square)
![Year](https://img.shields.io/badge/base%20year-2020-7d8590?style=flat-square)

**An AI-powered platform for real-time classification of traffic accident severity.**

[Demo](#demo) · [How It Works](#how-it-works) · [Dataset](#dataset) · [Model](#model)

---

</div>

## Overview

TrafficAI is a full-stack prototype that applies machine learning to classify traffic accidents into three levels: Light, Moderate, and Critical enabling faster and more accurate emergency response dispatch.

Built on a real 2020 dataset with 22,643 records, the system was trained using Orange Data Mining with algorithms including Random Forest and XGBoost. The front-end interface allows users to submit accident images or text descriptions and receive a severity classification with confidence score and suggested emergency resources.

> Road safety is a critical public health challenge. Every second between an accident and the right emergency team arriving can mean the difference between life and death.

---

## Demo

The front-end platform (`index.html`) includes a fully interactive demo section where you can:

- Upload an accident image via drag-and-drop or file picker
- Describe an accident in text and receive an AI-based classification
- See the detected severity level, confidence percentage, Suggested emergency resource, and analysis time

> ⚠️ The current demo uses simulated inference logic in JavaScript. Integration with the real trained model (`.pkcls`) via a backend API is the next development step.

---

## How It Works

The system follows a four-stage automated pipeline:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│  01 · Capture   │───▶│ 02 · Preprocess  │───▶│  03 · Inference │───▶│  04 · Alert      │
│                 │    │                  │    │                 │    │                  │
│ Traffic cameras │    │ Normalization    │    │ Trained model   │    │ Severity level   │
│ Drones / photos │    │ Metadata extract │    │ Random Forest / │    │ Emergency dispatch│
│ Text input      │    │ Null treatment   │    │ XGBoost         │    │ Resource routing │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └──────────────────┘
```

Stage 1 - Capture: Images from traffic cameras, drones, smartphones, or text descriptions submitted by users.

Stage 2 - Preprocessing: The pipeline normalizes inputs, extracts contextual metadata (time, location, weather), encodes categorical variables, and treats null values.

Stage 3 - Inference: The trained classifier analyzes damage patterns, vehicle positioning, debris distribution, and contextual factors to predict severity.

Stage 4 - Classification & Alert: Output is mapped to one of three severity levels. Alerts are dispatched to the appropriate emergency services.

---

## Dataset

| Property | Value |
|---|---|
| Total records | 22,643 |
| Base year | 2020 |
| Target variable | Severity (Light / Moderate / Critical) |
| Source | Brazilian traffic accident registry |

### Key variables

| Variable | Relevance |
|---|---|
| `sex` | Male involvement ~76% of all cases |
| `seatbelt` | Single strongest predictor of injury severity |
| `hour` | Peak accident time: 6 PM |
| `road_type` | Contextual predictor |
| `severity` | Target - Light / Moderate / Critical |

### Severity distribution

```
Moderate  ████████████████████████████████░░░░  ~54%
Light     █████████████████████░░░░░░░░░░░░░░░  ~45%
Critical  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ~0.5%
```

> The significant class imbalance critical cases represent only 0.5% of records is the main modeling challenge and requires special handling (see [Model](#model)).

---

## Model

### Training environment

The model was trained using [Orange Data Mining](https://orangedatamining.com/), a visual workflow tool for machine learning. The workflow file is available at:

```
severity_detection_training.ows
```

The trained model is exported as:

```
trained_accident_model.pkcls
```

### Why Recall?

In this context, a false negative on a critical accident is far more dangerous than a false positive. Missing a life-threatening case because the model underestimated severity could cost lives. Therefore, Recall for the critical class is the primary optimization target ahead of overall accuracy.

---


## Getting Started

### 1. Install Live Server

In VS Code:

- Open Extensions (`Ctrl + Shift + X`)
- Search for Live Server
- Click Install

### 2. Open the Project

Open Git Bash in VS Code and navigate to the API folder:

```bash
cd /c/Users/natas/OneDrive/Documents/Project/trafficai/api
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
python app.py
```

### 5. Access the API

The API will be available at:

```
http://127.0.0.1:5000
```

### 6. Open the Front-End

Open the project root folder in VS Code and click Open with Live Server on `index.html`.

---

## Key Findings

Gender disparity
- 76% of those involved in accidents were male (17,351 men vs. 4,727 women)
- Suggests higher driving exposure and risk-taking behavior among men

Seatbelt use
- 86.5% of those involved wore a seatbelt (19,583 people)
- The 13.5% who did not (3,060 people) showed disproportionately higher severity outcomes
- Seatbelt use is the single strongest individual predictor of injury severity

Peak hours
- Accident frequency peaks at 6 PM, coinciding with end-of-day traffic congestion
- Secondary peak at 8 AM (morning rush)
- Lowest risk period: 2–4 AM

Class imbalance
- Critical cases account for only 0.5% of records
- Without balancing, models default to predicting Light/Moderate and miss all Critical cases
- SMOTE or undersampling is required before training

---

## Severity Classification

| Level | Label | Criteria | Emergency Resource |
|---|---|---|---|
| 🟢 Level 1 | Light | Minor damage, no apparent victims, vehicles on road | Traffic patrol unit |
| 🟡 Level 2 | Moderate | Structural damage, airbag deployed, conscious victims with pain | SAMU + Municipal Guard |
| 🔴 Level 3 | Critical | Severe destruction, fire risk, trapped/unconscious victims, road blocked | SAMU + Fire Brigade + Police |

---

## Roadmap

- [x] Exploratory data analysis (2020 dataset)
- [x] Model training in Orange Data Mining
- [x] Front-end prototype (HTML/CSS/JS)
- [x] Interactive demo with severity simulation
- [ ] Python backend API exposing the `.pkcls` model
- [ ] Real model inference connected to front-end
- [ ] Integration with live traffic camera feeds
- [ ] Expand dataset to multiple years and cities
- [ ] Mobile application for field reporting

---

## Tech Stack

| Layer | Technology |
|---|---|
| Front-end | HTML5, CSS3, Vanilla JavaScript |
| Back-end | Python, Flask |
| Fonts | Bebas Neue, DM Sans, Space Mono (Google Fonts) |
| ML Training | Orange Data Mining 3 |
| Algorithms | Random Forest, XGBoost |
| Model format | `.pkcls` (Orange pickle) |
| Balancing | SMOTE / Undersampling |
| Evaluation | Confusion Matrix, F1-Score, Recall |

---


## License

This project was developed for academic purposes as part of the Software Analysis and Development 4th Semester. Dataset and results are for educational use only.