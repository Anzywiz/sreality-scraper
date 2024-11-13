# Sreality Scraper

The **Sreality Scraper** is a tool designed to extract comprehensive real estate data from the [Sreality.cz](https://www.sreality.cz) website. It provides structured information for property listings, making it valuable for market research, real estate analysis, and business applications. The dataset contains diverse fields capturing property details, location, agent information, and more.

---

## 📑 **Dataset Overview**

The dataset includes detailed fields, grouped into categories for clarity:

### **Property Details**
- `dbq_prd_type`: Fixed value set to `REAL-ESTATE-BASIC`.
- `listing_title`: Title of the listing exactly as it appears on the website.
- `listing_description`: Longer property description, when available.
- `property_type`: Type of property (e.g., house, apartment, box).
- `price`: Property price with numeric precision up to 2 decimals.
- `note_on_price`: Additional price-related details (e.g., negotiable, includes VAT).
- `currency_code`: ISO 3-letter currency code consistent with the country.

### **Location Information**
- `location_description`: General description of the property's location.
- `location_region`: Region or state, if available.
- `location_city`: City, if available.
- `location_street`: Street address, if available.
- `location_province`: Province or country, if available.
- `location_lon` and `location_lat`: Longitude and latitude coordinates, when available.

### **Area Measurements**
- `area_unit`: Fixed value (`SQFT` or `SQMT`) for square foot or square meter measurements.
- `total_area`: Total land or plot area associated with the property.
- `usable_area`: Actual livable or usable area within the property.
- `built_up_area`: Total covered area of the property, including constructed spaces.

### **Construction Details**
- `construction`: Full construction details, if available.
- `construction_type`: Type of building structure or material used (e.g., brick, concrete).
- `construction_status`: Current state of construction (e.g., completed, under construction).

### **Other Features**
- `floor_location`: Specifies the floor number of the property (e.g., ground floor, 5th floor).
- `amenities_list`: All amenities listed, such as balcony, terrace, A/C, heating.
- `energy_intensity`: Measures the energy efficiency of the property.

### **Agent Information**
- `agent_name`: Name of the real estate agent or agency.
- `agent_email`: Contact email for the agent.
- `agent_phone1` and `agent_phone2`: Primary and secondary contact numbers for the agent.
- `agent_url`: Direct URL to the agent's profile.
- `agent_website`: Agent’s official website.

### **Listing Metadata**
- `listing_date`: Original date the property was listed (DD-MM-YYYY).
- `listing_date_updated`: Date the listing was last updated (DD-MM-YYYY).
- `item_url`: URL to the detailed listing page.
- `image_url`: URL to the primary image of the property.

---

## 📊 **Sample Data**

A **sample dataset** containing 20 rows is provided in this repository for demonstration purposes. It showcases the structure and quality of the extracted data. 

### **Full Dataset**
The full dataset is available for purchase at [Data Boutique](https://databoutique.com). It includes thousands of records with regular updates.

---

## 🔎 **Field Details**

The detailed descriptions of all dataset fields are provided in the file [`field_description.csv`](field_description.csv). This document includes explanations of fixed values, derived fields, and scraped data fields.

---

## 💬 **Inquiries and Updates**

For an updated dataset, custom data requirements, or further inquiries, feel free to reach out:  
📧 Email: **your-email@example.com**  
🌐 Visit: [Data Boutique](https://databoutique.com)  

---

## 🚀 **License and Disclaimer**

This scraper is for educational and research purposes only. Ensure compliance with the [Sreality.cz Terms of Service](https://www.sreality.cz/) when using this scraper. Data usage is subject to licensing terms provided by Data Boutique.

---

Thank you for exploring the **Sreality Scraper**!  

