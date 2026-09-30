# 🦷 CBCT Sinus AI Analyzer

An AI-powered medical image analysis application for **maxillary sinus segmentation, anatomical measurement, and gender prediction from CBCT scans**.

The system accepts either a collection of DICOM slices or an NRRD volume, performs automated 3D segmentation using a trained **3D U-Net**, extracts sinus measurements, and uses a machine-learning model to predict gender based on the left maxillary sinus volume.

> **Academic / Research Prototype**
> This project is intended for educational and research purposes and is not a medical diagnostic system.

---

## ✨ Features

* 📂 Upload **DICOM/CBCT scan files**
* 🧠 Upload pre-converted **NRRD volumes**
* 🔄 Automatic **DICOM → NRRD conversion**
* 🧬 Automated **3D maxillary sinus segmentation**
* 📏 Extraction of sinus measurements:

  * Volume
  * Length
  * Breadth
  * Height
* 👤 Gender prediction using a trained machine-learning model
* 📊 Prediction confidence
* 🔬 Visualization of the original scan and segmentation
* 💾 Export processed medical volumes
* 🖼️ Generate segmentation preview images
* 📑 Generate downloadable Excel reports
* 🌙 Dark-themed Streamlit interface

---

## 🧠 System Architecture

```text
                    ┌─────────────────────┐
                    │     CBCT / DICOM    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  DICOM → NRRD       │
                    │     SimpleITK       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Preprocessing     │
                    │ Normalization/Resize│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      3D U-Net       │
                    │  Sinus Segmentation │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Post-processing    │
                    │ Largest Component   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Sinus Metrics     │
                    │ V / L / B / H       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Gender Prediction   │
                    │ Scaler + ML Model   │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
      Visualization                       Excel Report
```

---

## 🔬 Methodology

### 1. Input

The application supports two input modes:

**DICOM mode**

A complete CBCT DICOM series can be uploaded as multiple files.

**NRRD mode**

A previously converted NRRD volume can be uploaded directly.

---

### 2. DICOM to NRRD Conversion

For DICOM input, the application uses **SimpleITK** to identify the DICOM series and reconstruct the volumetric image.

```text
DICOM slices
     ↓
DICOM series detection
     ↓
3D volume reconstruction
     ↓
NRRD volume
```

---

### 3. 3D U-Net Segmentation

The NRRD volume is preprocessed before being passed to the trained 3D U-Net.

The current pipeline:

1. Read the NRRD volume
2. Clip intensity values
3. Normalize the volume
4. Resize to:

```text
64 × 128 × 128
```

5. Add the required channel and batch dimensions
6. Run the trained 3D U-Net
7. Apply a probability threshold of `0.5`
8. Keep the largest connected component
9. Resize the segmentation back to the original volume dimensions
10. Save the segmentation as an NRRD file

The trained segmentation model is stored as:

```text
models/3dunet.h5
```

---

## 📏 Sinus Measurements

After segmentation, the application extracts measurements from the left and right maxillary sinus regions.

The results include:

| Measurement | Description            |
| ----------- | ---------------------- |
| Volume      | Estimated sinus volume |
| Length      | Sinus length           |
| Breadth     | Sinus breadth          |
| Height      | Sinus height           |

The measurements are displayed in the Streamlit interface and included in the generated Excel report.

---

## 🧬 Gender Prediction

The gender prediction module uses the **left maxillary sinus volume** as the prediction feature.

The pipeline is:

```text
Left sinus volume
        ↓
Feature scaling
        ↓
Trained ML model
        ↓
Prediction
        ↓
Gender + probability
```

The trained files are:

```text
models/model.pkl
models/scaler.pkl
```

The current implementation only performs gender prediction when the left sinus volume is above the configured threshold of:

```text
2000 mm³
```

The model returns:

```text
Predicted Gender
Confidence
```

---

## 🖥️ Application Interface

The application is built using **Streamlit** and provides a dark-themed interface for the complete analysis workflow.

The workflow is:

```text
Upload Scan
     ↓
Run AI Analysis
     ↓
Segmentation
     ↓
Measurements
     ↓
Gender Prediction
     ↓
Visualization
     ↓
Download Report
```

---

## 📁 Project Structure

```text
Dental_Project/
│
├── .streamlit/
│   └── config.toml
│
├── core/
│   ├── dicom_to_nrrd.py
│   ├── segment.py
│   ├── metrics.py
│   ├── visualize.py
│   ├── export.py
│   └── gender_prediction.py
│
├── models/
│   ├── 3dunet.h5
│   ├── model.pkl
│   └── scaler.pkl
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🛠️ Technologies Used

### Frontend / Application

* **Streamlit**

### Medical Image Processing

* **SimpleITK**
* **pynrrd**

### Deep Learning

* **TensorFlow**
* **3D U-Net**

### Machine Learning

* **scikit-learn**
* **Joblib**

### Scientific Computing

* **NumPy**
* **SciPy**

### Data Processing & Reporting

* **Pandas**
* **OpenPyXL**
* **Pillow**
* **Matplotlib**

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/spoorthi133/Dental_Project.git
cd Dental_Project
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

---

## ▶️ Run the Application

Start the Streamlit application:

```powershell
python -m streamlit run app.py
```

The application will be available locally at:

```text
http://localhost:8501
```

---

## 📊 Output

After analysis, the application generates:

### Segmentation

```text
cbct_volume.nrrd
sinus_segmentation.seg.nrrd
```

### Visualization

```text
preview_overlay.png
```

### Report

```text
measurements.xlsx
```

The Excel report contains:

* Left sinus volume
* Left sinus length
* Left sinus breadth
* Left sinus height
* Right sinus volume
* Right sinus length
* Right sinus breadth
* Right sinus height
* Predicted gender
* Prediction confidence

---

## 🚀 Deployment

The application is designed to be deployable as a Streamlit web application.

The repository contains the required:

```text
app.py
requirements.txt
.streamlit/config.toml
models/
core/
```

For deployment, ensure that the trained model files are available to the application.

---

## ⚠️ Important Disclaimer

This project is an **academic/research prototype**.

The predictions and measurements generated by the application should **not be used as a substitute for professional medical diagnosis, clinical decision-making, or radiological interpretation**.

The system has not been presented here as clinically validated.

---

## 🔮 Future Improvements

Potential future improvements include:

* Automatic left/right sinus identification
* Improved segmentation accuracy
* Additional anatomical measurements
* 3D interactive visualization
* Model performance metrics and validation
* Support for additional CBCT formats
* GPU-based inference
* Patient/session management
* PDF report generation
* Improved model explainability
* Clinical validation using a larger dataset

---

## 👩‍💻 Project

**Dental Project — CBCT Maxillary Sinus AI Analysis**

Built using deep learning, medical image processing, and machine learning to automate parts of the CBCT sinus analysis workflow.
