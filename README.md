# 🚕 Ride Duration Prediction System

A machine learning based web application that predicts NYC taxi ride duration using trip details such as passenger count, trip distance, pickup hour, and day type.

This project was developed as a Data Science portfolio project using Python, Scikit-learn, Streamlit, and SQLite.



## 📌 Project Overview

The Ride Duration Prediction System helps estimate taxi trip duration using a trained machine learning model.  
The system includes a modern dashboard, real-time prediction, user login and registration, prediction history, database storage, and analytics.



## ✨ Features

- User registration and login
- User-wise prediction history
- Real-time ride duration prediction
- Save predictions to SQLite database
- View prediction history
- Search prediction records
- Delete prediction records
- Download prediction history as CSV
- Analytics dashboard
- Interactive Streamlit UI
- Machine learning model integration



## 🧠 Machine Learning

The model predicts taxi trip duration based on:

- Passenger count
- Trip distance
- Pickup hour
- Day type

Model used:

- Linear Regression



## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit
- SQLite
- Pickle
- GitHub



## 📊 Dataset

Dataset used:

**NYC Yellow Taxi Trip Record Data**

Official dataset source:  
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Note:  
The full dataset is not included in this repository because it is large.  
Only source code, model file, and application files are included.

-

## 📁 Project Structure

```text
ride-duration-prediction-system/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── models/
│   └── model.pkl
│
├── data/
│   └── dataset not included
│
└── ride_predictions.db

## 🚀 How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ride-duration-prediction-system.git
```

### 2. Go to project folder

```bash
cd ride-duration-prediction-system
```

### 3. Install required libraries

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit app

```bash
python -m streamlit run app.py
```



## 👥 Target Users

This system can be used by:

* Taxi drivers
* Ride-hailing companies
* Transport analysts
* City planners
* Data science students
* Researchers



## 📈 System Modules

### Login and Register

Users can create an account and login securely.

### Prediction Dashboard

Users can enter ride details and get estimated trip duration.

### Prediction History

Saved predictions can be viewed, searched, deleted, and downloaded.

### Analytics Dashboard

The system provides analytics based on saved prediction data.


## 🔮 Future Improvements

* Add advanced ML models such as Random Forest or XGBoost
* Add real-time traffic data
* Add map-based route visualization
* Add admin dashboard
* Add cloud database
* Add password reset feature
* Deploy with Docker



## 👩‍💻 Author

Developed by **Chamodi Hansika**



## 📄 License

This project is licensed under the MIT License.
