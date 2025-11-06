# Attendance Analyzer - Smart Bunking Buddy

A Flask-based web application that analyzes student attendance, provides notifications, and helps plan safe "bunk" days using AI.

## Features

- **ERP Integration**: Automatically scrapes attendance data from ERP portal
- **AI-Powered Timetable**: Uses Gemini API to process timetable files
- **Attendance Dashboard**: View overall and subject-wise attendance
- **Smart Notifications**: Alerts for low attendance and discrepancies
- **Bunking Buddy**: Interactive full-year calendar to plan safe bunk days
- **Real-time Projections**: See attendance impact before bunking
- **Beautiful UI**: Liquid glass design with smooth animations

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Chrome Browser

Make sure you have Google Chrome installed (for Selenium web scraping).

### 3. Configure Gemini API (Optional)

Edit `app.py` and set your Gemini API key:

```python
GEMINI_API_KEY = "your-api-key-here"
```

Get a free API key from: https://makersuite.google.com/app/apikey

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## How to Use

1. **Login**: Enter your ERP username and password
2. **Upload Timetable**: Upload your weekly timetable (Excel/CSV) and enter batch details
3. **Wait for Processing**: The app will automatically:
   - Scrape your attendance from ERP
   - Process your timetable with AI
4. **View Dashboard**: See your attendance stats and notifications
5. **Use Bunking Buddy**: Select days to bunk and see real-time attendance impact

## File Structure

```
python mini project/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── index.html
│   ├── loading.html
│   ├── dashboard.html
│   └── bunking_buddy.html
├── static/                # CSS files
│   └── styles.css
├── uploads/               # Uploaded timetables (auto-created)
└── outputs/               # Generated data files (auto-created)
```

## Technologies Used

- **Backend**: Flask (Python)
- **Web Scraping**: Selenium
- **AI**: Google Gemini API
- **Data Processing**: Pandas
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Liquid Glass/Glassmorphism

## Notes

- Keep your ERP credentials secure
- The app runs locally on your machine
- All data is stored locally
- Internet connection required for ERP scraping and AI features

## Troubleshooting

**Issue**: Selenium not working
- Make sure Chrome browser is installed
- Check if chromedriver is compatible with your Chrome version

**Issue**: Gemini API not working
- Set your API key in `app.py`
- Check internet connection
- Verify API key is valid

**Issue**: ERP login fails
- Verify credentials are correct
- Check if ERP portal is accessible
- ERP structure may have changed (update selectors in code)

## License

Educational project - free to use and modify.
