# WakeMeUp: Intelligent Sports Alert System


## 📱 Overview

WakeMeUp is an intelligent sports alert system that delivers real-time notifications based on user-defined milestones in cricket matches. This repository contains the server-side code that powers the backend infrastructure, running on AWS EC2.

The server continuously scrapes live match data from Cricbuzz, stores it in Firebase, and triggers notifications when user-defined conditions are met. It serves as the brain of the WakeMeUp ecosystem, providing the Flutter mobile application with reliable and timely sports updates.

## 🚀 Features

- **Real-time Data Scraping**: Periodic scraping of live cricket match data from Cricbuzz
- **Intelligent Alert System**: Decision tree-based ML models to analyze match conditions and trigger notifications
- **Firebase Integration**: Secure storage of match data and user preferences
- **User Alert Management**: Monitoring of user-defined alerts and delivery of notifications when conditions are met
- **Scalable Architecture**: Deployed on AWS EC2 for reliable performance and easy scaling

## 🔧 Tech Stack

- **Server**: Python, Flask
- **Data Processing**: Beautiful Soup, Pandas
- **Machine Learning**: Scikit-learn
- **Database**: Firebase Realtime Database
- **Deployment**: AWS EC2
- **Notification Service**: Firebase Cloud Messaging
- **Client App**: Flutter (separate repository)

## 📋 Prerequisites

- Python 3.8+
- AWS CLI
- Firebase Admin SDK


## 📋 TODO: 

- Make data upload to firebase more effecient. Upload scores and status only if there is a change. 
