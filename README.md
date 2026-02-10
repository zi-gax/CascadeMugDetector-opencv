# ☕ Mug Detection – OpenCV Cascade Classifier

An **OpenCV Haar/LBP Cascade Classifier**
to detect **mugs**, including dataset preparation, annotation, and training.

Most preprocessing steps are automated using **`precascade.py`**.

---

## 📁 Project Structure

```
cascadeclassimug/
│
├── positive/
│   ├── (images)
│   ├── (xmls)
│   └── positives.txt
│
├── negative/
│   ├── (images)
│   └── neg.txt
│
├── vec/
│   └── positives.vec
│
├── cascade/
│   └── (stages.xml)
│
├── labelImg/
│   ├── data
│   └── labelimg.exe
│
├── precascade.py
├── requirements.txt
│
├── .git/
└── README.md
```

---

## 🚀 Dataset Preparation Pipeline

### 1️⃣ Download Images (Positive & Negative)

```bash
python precascade.py (option 1 or 2)
```

### 2️⃣ Remove Duplicate Images

```bash
python precascade.py (option 3)
```

### 3️⃣ Clean Noise & Useless Images

Remove blurry, wrong, very small, or corrupted images.

### 4️⃣ Rename Images

```bash
python precascade.py (option 4)
```

### 5️⃣ Annotate Positive Images (LabelImg)

```bash
labelimg/labelImg.exe
```

Save XML files to:
```
positive/
```

### 6️⃣ Convert XML → OpenCV Annotation

```bash
python precascade.py (option 5 xml-to-txt positive/ positive/positives.txt)
```

### 7️⃣ Fix Windows Paths

open positive/positives.txt and replace bslash \ to slash / 

### 8️⃣ Create neg.txt

```bash
python precascade.py (option 6 negative/ negative/neg.txt)
```

### 9️⃣ Optional: Find Best Resize Size

```bash
python precascade.py (option 7)
```

---

## 🧱 Training the Cascade Classifier

### Create `.vec` File

```bash
opencv_createsamples.exe -info positive/positives.txt -w 24 -h 24 -num 1000 -vec vec/positives.vec
```

### Train Cascade

```bash
opencv_traincascade.exe -data cascade/ -vec vec/positives.vec -bg negative/neg.txt -w 24 -h 24 -numPos 500 -numNeg 1000 -numStages 10
```
