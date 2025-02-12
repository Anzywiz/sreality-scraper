![Sreality Dashboard](https://github.com/Anzywiz/sreality-scraper/blob/main/images/sreality_dashboard.png)

# Sreality Scraper

The **Sreality Scraper** is designed to extract comprehensive real estate data from the [Sreality.cz](https://www.sreality.cz) website. It provides structured information for property listings, making it valuable for market research, real estate analysis, and business applications. The dataset contains diverse fields capturing property details, location, agent information, and more.

---

## 📚 **Table of Contents**

1. [📊 Sample Data](#-sample-data)
2. [🔎 Field Details](#-field-details)
3. [📌 Setup](#-setup)
4. [🔄 Updates](#-updates)
5. [🛠 Issues & Contributions](#-issues--contributions)
6. [📜 License](#-license)
7. [💬 Inquiries and Support](#-inquiries-and-support)
8. [⭐ Show Your Support!](#-show-your-support)
9. [🚀 License and Disclaimer](#-license-and-disclaimer)

---

## 📊 **Sample Data**

A **[sample dataset](https://github.com/Anzywiz/sreality-scraper/blob/main/sreality_sample.xlsx)** containing 20 rows is provided in this repository for demonstration purposes. It showcases the structure and quality of the extracted data. 

---

## 🔎 **Field Details**

The detailed descriptions of all dataset fields are provided in the file [`field_description.csv`](field_description.csv). This document includes explanations of fixed values, derived fields, and scraped data fields.

---

## 📌 **Setup**

Follow these steps to set up and run the bot.

1️⃣ **Clone the Repository**

```bash
git clone https://github.com/Anzywiz/sreality-scraper.git
cd sreality-scraper
```

2️⃣ **Create and Activate a Virtual Environment**

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3️⃣ **Install Dependencies**

```bash
pip install -r requirements.txt
```

4️⃣ **Run the Bot**

```bash
python main.py
```

When prompted, enter the number corresponding to the property type you want to scrape.
The scraped data would be in the **data** directory

*(Refer to the image below for guidance on selecting property types.)*

---

## 🔄 **Updates**

Stay tuned for updates and improvements!

---

## 🛠 **Issues & Contributions**

If you encounter any issues, please report them in the [**Issues**](https://github.com/Anzywiz/sreality-scraper/issues) section of the repository.

💡 Want to improve the bot? Fork the repository, make your changes, and submit a **pull request (PR)**! Contributions are always welcome.

---

## 📜 **License**

This project is licensed under the **MIT License**.

---

## 💬 **Inquiries and Support**

For inquiries or support, feel free to reach out:

- **Telegram Group:** [Join the chat](https://t.me/bot_arena_chat)
- **Email:** [ifeanyi.webapp@gmail.com](mailto:ifeanyi.webapp@gmail.com)

---

## ⭐ **Show Your Support!**

If you find this project useful, please **star** the repository! Your support helps keep the project growing. 😊

---

## 🚀 **License and Disclaimer**

This scraper is for educational and research purposes only. Ensure compliance with the [Sreality.cz Terms of Service](https://www.sreality.cz/) when using this scraper. Data usage is subject to licensing terms.

---

Thank you for exploring the **Sreality Scraper**!

