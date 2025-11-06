from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import threading
import time

# Selenium imports for ERP scraping
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Gemini API imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
ERP_URL = "https://learner.pceterp.in/"
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')  # Set via environment variable

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Subject name mappings for better display
SUBJECT_MAPPINGS = {
    # UHV variations
    'UH': 'UHV',
    'UHV': 'UHV',
    'ACUHV': 'UHV',
    # Data Structures
    'DSA': 'DSA',
    'DS': 'DS',
    'UBTDS': 'DSA',
    # Python
    'PP': 'PYP',
    'PYP': 'PYP',
    'PYTHON': 'PYP',
    'UBTDS203': 'PYP',
    # DLM
    'DLM': 'DLM',
    # Computer Organization
    'COA': 'COA',
    'UBTDS206': 'COA',
    # Operating Systems
    'OS': 'OS',
    'MOOCDS301': 'OS MOOC',
    'MOOCDS': 'OS MOOC',
    'MOOC': 'OS MOOC',
    # Linux
    'LINUX': 'Linux MOOC',
    'MOOCDS302': 'Linux MOOC',
    # Languages
    'GERMAN': 'German',
    'JAPANESE': 'Japanese',
    # Labs
    'LAB': 'Lab',
    'UBTDS202': 'DSA Lab',
    'UBTDS204': 'PYP Lab',
    'UBTDS201': 'DSA',
    'UBTDS205': 'DS'
}

# Global storage for processing status
processing_status = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def scrape_erp_attendance(username, password, session_id):
    """Background task to scrape ERP for attendance data"""
    global processing_status
    processing_status[session_id] = {'status': 'scraping', 'progress': 10, 'message': 'Connecting to ERP...'}
    
    try:
        if not SELENIUM_AVAILABLE:
            processing_status[session_id] = {'status': 'error', 'message': 'Selenium not installed'}
            return
        
        # Setup Chrome
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        
        # Login to ERP
        processing_status[session_id]['progress'] = 20
        processing_status[session_id]['message'] = 'Logging in to ERP...'
        
        driver.get(ERP_URL)
        time.sleep(2)
        
        processing_status[session_id]['progress'] = 25
        processing_status[session_id]['message'] = 'Entering credentials...'
        
        username_field = driver.find_element(By.ID, "input-0")
        password_field = driver.find_element(By.ID, "input-2")
        
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        processing_status[session_id]['progress'] = 35
        processing_status[session_id]['message'] = 'Submitting login form...'
        
        login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        time.sleep(3)
        
        # Navigate to attendance page
        processing_status[session_id]['progress'] = 50
        processing_status[session_id]['message'] = 'Navigating to attendance page...'
        
        driver.get("https://learner.pceterp.in/attendance")
        time.sleep(4)
        
        # Extract attendance data
        processing_status[session_id]['progress'] = 60
        processing_status[session_id]['message'] = 'Reading attendance cards...'
        
        cards = driver.find_elements(By.CSS_SELECTOR, "div.v-card")
        attendance_data = []
        total_cards = len(cards)
        
        processing_status[session_id]['progress'] = 65
        processing_status[session_id]['message'] = f'Found {total_cards} subjects, extracting data...'
        
        for idx, card in enumerate(cards):
            try:
                # Try to use CSS selectors to extract data directly from HTML structure
                subject_code = None
                subject_name = None
                professor = "Unknown"
                percentage_value = None
                attended = 0
                total_classes = 0
                
                # Try to find elements by CSS class
                try:
                    # Get text content from card
                    card_text = card.text.strip()
                    if not card_text:
                        continue
                    
                    lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                    if len(lines) < 4:
                        continue
                    
                    # Line 0: Professor info (e.g., "7252 / KOMAL VIKRANT RAJGUDE")
                    professor_line = lines[0]
                    if '/' in professor_line:
                        professor = professor_line.split('/')[-1].strip()
                    else:
                        professor = professor_line
                except:
                    pass
                
                # Extract from card text - parse more carefully
                card_text = card.text.strip()
                lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                
                if len(lines) < 4:
                    continue
                
                # Find percentage (has % symbol)
                percentage_idx = -1
                for i, line in enumerate(lines):
                    if '%' in line:
                        try:
                            percentage_value = float(line.replace('%', '').strip())
                            percentage_idx = i
                            break
                        except:
                            continue
                
                # Find fraction (format: "number / number")
                fraction_idx = -1
                for i, line in enumerate(lines):
                    if ' / ' in line and line != lines[0]:  # Skip professor line
                        parts = line.split(' / ')
                        if len(parts) == 2:
                            try:
                                attended = int(parts[0].strip())
                                total_classes = int(parts[1].strip())
                                fraction_idx = i
                                break
                            except:
                                continue
                
                if percentage_value is None or fraction_idx == -1:
                    continue
                
                # Extract subject info from lines between professor and percentage
                # Look for: Subject Code (has letters+numbers), then Subject Name (short)
                potential_codes = []
                potential_names = []
                
                for i in range(1, min(percentage_idx, len(lines))):
                    line = lines[i]
                    
                    # Skip fraction, percentage, and professor lines
                    if (' / ' in line and i == fraction_idx) or '%' in line or i == 0:
                        continue
                    
                    # Subject code: Mix of letters and numbers (e.g., ACUHV201, MOOCDS301, UBTDS201)
                    if any(c.isalpha() for c in line) and any(c.isdigit() for c in line) and len(line) >= 4:
                        potential_codes.append(line)
                    # Subject name: Short, mostly letters, 2-4 chars (e.g., UH, DSA, PP)
                    elif len(line) >= 2 and len(line) <= 6 and line.isalpha():
                        potential_names.append(line)
                
                # Pick best matches
                if potential_codes:
                    subject_code = potential_codes[0]
                if potential_names:
                    subject_name = potential_names[0]
                
                # Build display name using mappings
                # Check both subject_name and subject_code for mappings
                mapped_name = None
                
                # First try exact match on subject code
                if subject_code and subject_code.upper() in SUBJECT_MAPPINGS:
                    mapped_name = SUBJECT_MAPPINGS[subject_code.upper()]
                # Then try subject name
                elif subject_name:
                    if subject_name.upper() in SUBJECT_MAPPINGS:
                        mapped_name = SUBJECT_MAPPINGS[subject_name.upper()]
                    else:
                        # Try partial match
                        for key, value in SUBJECT_MAPPINGS.items():
                            if key.upper() in subject_name.upper() or subject_name.upper() in key.upper():
                                mapped_name = value
                                break
                # Try matching code with partial string
                if not mapped_name and subject_code:
                    for key, value in SUBJECT_MAPPINGS.items():
                        if key.upper() in subject_code.upper():
                            mapped_name = value
                            break
                
                # Check if it's a lab
                is_lab = False
                if subject_code or subject_name:
                    check_text = ((subject_code or '') + (subject_name or '')).upper()
                    if 'LAB' in check_text or '-LAB' in check_text:
                        is_lab = True
                
                # Build final display name
                if mapped_name:
                    # If mapped name already contains 'Lab', don't add again
                    if 'Lab' in mapped_name:
                        display_name = mapped_name
                    else:
                        display_name = f"{mapped_name} Lab" if is_lab else mapped_name
                elif subject_name and not subject_code:
                    display_name = subject_name
                elif subject_code and not subject_name:
                    display_name = subject_code
                elif subject_name and subject_code:
                    # Both available, combine them
                    display_name = f"{subject_name} ({subject_code})"
                else:
                    # Last resort
                    display_name = f"Subject {idx + 1}"
                
                # Debug print
                print(f"Extracted: code={subject_code}, name={subject_name}, mapped={mapped_name}, final={display_name}")
                
                subject_data = {
                    'Subject': display_name,
                    'Percentage': f"{percentage_value}%",
                    'Attended Classes': attended,
                    'Total Classes': total_classes,
                    'Professor': professor,
                    'DateWiseAttendance': []
                }
                
                # Click on card to get date-wise details
                try:
                    # Scroll card into view and use JavaScript click to avoid interception
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(0.5)
                    
                    # Try JavaScript click first (more reliable)
                    try:
                        driver.execute_script("arguments[0].click();", card)
                    except:
                        # Fallback to regular click
                        card.click()
                    
                    time.sleep(2)
                    
                    # Look for the modal table with attendance details
                    # Based on screenshot: table has columns Sr No, Date, Attendance, Faculty
                    try:
                        # Find all table rows
                        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr, .v-data-table tbody tr")
                        if not rows:
                            # Try alternative: list items in modal
                            rows = driver.find_elements(By.CSS_SELECTOR, ".v-dialog .v-list-item")
                        
                        for row in rows:
                            try:
                                row_text = row.text.strip()
                                if not row_text:
                                    continue
                                
                                # Parse row: should have date and status (Present/Absent)
                                # Present is in green, Absent is in red
                                row_lines = row_text.split('\n')
                                
                                # Look for date pattern (e.g., "23-Jul-2025", "25-Jul-2025")
                                date_str = None
                                status = None
                                
                                for line in row_lines:
                                    # Check if it's a date
                                    if '-' in line and any(c.isdigit() for c in line):
                                        date_str = line
                                    # Check for Present/Absent
                                    if 'present' in line.lower():
                                        status = 'Present'
                                    elif 'absent' in line.lower():
                                        status = 'Absent'
                                
                                if date_str and status:
                                    subject_data['DateWiseAttendance'].append({
                                        'date': date_str,
                                        'status': status
                                    })
                            except:
                                continue
                        
                        # Close modal
                        try:
                            close_btn = driver.find_element(By.CSS_SELECTOR, ".v-dialog button[aria-label='close'], .v-dialog .v-icon.mdi-close")
                            close_btn.click()
                            time.sleep(0.5)
                        except:
                            # Try pressing Escape
                            driver.find_element(By.TAG_NAME, 'body').send_keys('\ue00c')  # ESC key
                            time.sleep(0.5)
                    except:
                        # If modal parsing fails, just close and continue
                        try:
                            driver.find_element(By.TAG_NAME, 'body').send_keys('\ue00c')
                            time.sleep(0.5)
                        except:
                            pass
                    
                except Exception as e:
                    print(f"Failed to get date-wise data for {display_name}: {e}")
                    pass
                
                attendance_data.append(subject_data)
                
                # Update progress
                progress = 65 + int((idx / total_cards) * 25)
                processing_status[session_id]['progress'] = progress
                processing_status[session_id]['message'] = f'Extracted {len(attendance_data)} subjects...'
                
            except Exception as e:
                print(f"Error processing card {idx}: {e}")
                continue
        
        driver.quit()
        
        # Calculate overall attendance from all subjects
        if attendance_data:
            total_attended = sum(s['Attended Classes'] for s in attendance_data)
            total_classes_all = sum(s['Total Classes'] for s in attendance_data)
            overall_pct = round((total_attended / total_classes_all * 100), 2) if total_classes_all > 0 else 0
            
            attendance_data.append({
                'Subject': 'OVERALL ATTENDANCE',
                'Percentage': f"{overall_pct}%",
                'Attended Classes': total_attended,
                'Total Classes': total_classes_all,
                'Professor': '---',
                'DateWiseAttendance': []
            })
        
        # Save to CSV and Excel
        processing_status[session_id]['progress'] = 80
        processing_status[session_id]['message'] = 'Saving attendance data...'
        
        df = pd.DataFrame(attendance_data)
        csv_path = os.path.join(OUTPUT_FOLDER, f'attendance_{session_id}.csv')
        excel_path = os.path.join(OUTPUT_FOLDER, f'attendance_{session_id}.xlsx')
        
        df.to_csv(csv_path, index=False)
        df.to_excel(excel_path, index=False)
        
        processing_status[session_id] = {
            'status': 'completed',
            'progress': 100,
            'message': 'Attendance data fetched successfully!',
            'data': attendance_data,
            'csv_path': csv_path,
            'excel_path': excel_path
        }
        
    except Exception as e:
        processing_status[session_id] = {
            'status': 'error',
            'message': f'Error scraping ERP: {str(e)}'
        }


def process_timetable_with_gemini(file_path, batch_info, session_id):
    """Background task to process timetable with Gemini API"""
    global processing_status
    
    try:
        if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
            # Fallback to basic processing
            processing_status[session_id]['timetable_status'] = 'completed'
            processing_status[session_id]['timetable_message'] = 'Timetable processed (basic mode)'
            return
        
        processing_status[session_id]['timetable_status'] = 'processing'
        processing_status[session_id]['timetable_message'] = 'Processing timetable with AI...'
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        df = pd.read_excel(file_path)
        file_content = df.to_csv(index=False)
        
        language_info = ''
        if batch_info.get('language') == 'german':
            language_info = 'The student has opted for German language course.'
        elif batch_info.get('language') == 'japanese':
            language_info = 'The student has opted for Japanese language course.'
        
        prompt = f"""
        Extract the weekly timetable schedule for batch {batch_info['batch']} from the timetable data.
        
        Student Details:
        - Year: {batch_info['year']}
        - Semester: {batch_info['semester']}
        - Division: {batch_info['division']}
        - Batch: {batch_info['batch']}
        {language_info}
        
        Return ONLY a JSON object with days as keys (Monday, Tuesday, etc.) and arrays of subject names as values.
        Example: {{"Monday": ["DSA", "PP"], "Tuesday": ["COA", "DLM"]}}
        
        --- TIMETABLE DATA ---
        {file_content[:2000]}
        ---
        """
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        raw_text = getattr(response, 'text', None) or str(response)
        clean_json = raw_text.strip().replace('```json', '').replace('```', '')
        
        schedule = json.loads(clean_json)
        
        # Save schedule
        schedule_path = os.path.join(OUTPUT_FOLDER, f'schedule_{session_id}.json')
        with open(schedule_path, 'w') as f:
            json.dump(schedule, f)
        
        processing_status[session_id]['timetable_status'] = 'completed'
        processing_status[session_id]['timetable_data'] = schedule
        processing_status[session_id]['schedule_path'] = schedule_path
        
    except Exception as e:
        processing_status[session_id]['timetable_status'] = 'error'
        processing_status[session_id]['timetable_message'] = f'Error processing timetable: {str(e)}'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'})
    
    # Create session ID
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    session['session_id'] = session_id
    session['username'] = username
    
    # Store credentials for later processing
    processing_status[session_id] = {
        'status': 'waiting_timetable',
        'username': username,
        'password': password
    }
    
    return jsonify({'success': True, 'session_id': session_id})


@app.route('/upload-timetable', methods=['POST'])
def upload_timetable():
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'message': 'Session expired'})
    
    if 'timetable' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['timetable']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file'})
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Get batch info
    batch_info = {
        'batch': request.form.get('batch'),
        'division': request.form.get('division'),
        'year': request.form.get('year'),
        'semester': request.form.get('semester'),
        'language': request.form.get('language')
    }
    
    # Start background processing
    username = processing_status[session_id]['username']
    password = processing_status[session_id]['password']
    
    # Start ERP scraping thread
    erp_thread = threading.Thread(target=scrape_erp_attendance, args=(username, password, session_id))
    erp_thread.start()
    
    # Start timetable processing thread
    timetable_thread = threading.Thread(target=process_timetable_with_gemini, args=(filepath, batch_info, session_id))
    timetable_thread.start()
    
    return jsonify({'success': True, 'session_id': session_id})


@app.route('/status/<session_id>')
def get_status(session_id):
    status = processing_status.get(session_id, {'status': 'unknown'})
    return jsonify(status)


@app.route('/dashboard/<session_id>')
def dashboard(session_id):
    if session_id not in processing_status:
        return redirect(url_for('index'))
    
    status = processing_status[session_id]
    if status.get('status') != 'completed':
        return render_template('loading.html', session_id=session_id)
    
    # Convert status data to match dashboard template expectations
    dashboard_data = {
        'current_overall': {
            'percentage': 0,
            'attended': 0,
            'total': 0
        },
        'projected_normal': {
            'percentage': 0,
            'attended': 0,
            'total': 0
        },
        'projected_selected': {
            'percentage': 0,
            'attended': 0,
            'total': 0
        },
        'subjects': [],
        'alerts': [],
        'calendar': [],
        'safe_bunk_days': [],
        'bunk_dates': [],
        'schedule_file': f'schedule_{session_id}.json',
        'horizon_days': 90
    }
    
    # Parse attendance data if available
    if 'data' in status and status['data']:
        attendance_data = status['data']
        total_attended = 0
        total_classes = 0
        subjects_list = []
        overall_found = False
        
        for item in attendance_data:
            if item['Subject'] == 'OVERALL ATTENDANCE':
                overall_found = True
                percentage_str = item['Percentage'].replace('%', '')
                dashboard_data['current_overall'] = {
                    'percentage': float(percentage_str),
                    'attended': item['Attended Classes'],
                    'total': item['Total Classes']
                }
                dashboard_data['projected_normal'] = {
                    'percentage': float(percentage_str),
                    'attended': item['Attended Classes'],
                    'total': item['Total Classes']
                }
                dashboard_data['projected_selected'] = {
                    'percentage': float(percentage_str),
                    'attended': item['Attended Classes'],
                    'total': item['Total Classes']
                }
            else:
                percentage_str = item['Percentage'].replace('%', '')
                subjects_list.append({
                    'id': item['Subject'].replace(' ', '_'),
                    'display_name': item['Subject'],
                    'professor': item.get('Professor', ''),
                    'future_classes': 0,
                    'date_wise': item.get('DateWiseAttendance', []),  # Add date-wise data
                    'current': {
                        'attended': item['Attended Classes'],
                        'total': item['Total Classes'],
                        'percentage': float(percentage_str)
                    },
                    'normal': {
                        'attended': item['Attended Classes'],
                        'total': item['Total Classes'],
                        'percentage': float(percentage_str)
                    },
                    'selected': {
                        'attended': item['Attended Classes'],
                        'total': item['Total Classes'],
                        'percentage': float(percentage_str)
                    }
                })
                total_attended += item['Attended Classes']
                total_classes += item['Total Classes']
        
        dashboard_data['subjects'] = subjects_list
        
        # If no OVERALL ATTENDANCE record, calculate from subjects
        if not overall_found and total_classes > 0:
            overall_percentage = round((total_attended / total_classes) * 100, 2)
            dashboard_data['current_overall'] = {
                'percentage': overall_percentage,
                'attended': total_attended,
                'total': total_classes
            }
            dashboard_data['projected_normal'] = {
                'percentage': overall_percentage,
                'attended': total_attended,
                'total': total_classes
            }
            dashboard_data['projected_selected'] = {
                'percentage': overall_percentage,
                'attended': total_attended,
                'total': total_classes
            }
        
        # Add alerts for low attendance
        if dashboard_data['current_overall']['percentage'] < 75:
            dashboard_data['alerts'].append(
                f"⚠️ Your overall attendance is {dashboard_data['current_overall']['percentage']}%, which is below the required 75%."
            )
        
        for subject in subjects_list:
            if subject['current']['percentage'] < 75:
                dashboard_data['alerts'].append(
                    f"⚠️ {subject['display_name']}: {subject['current']['percentage']}% (below 75%)"
                )
    
    student_info = {
        'year': 'N/A',
        'semester': 'N/A',
        'division': 'N/A',
        'batch': 'N/A',
        'language': 'none'
    }
    
    return render_template('dashboard.html', dashboard_data=dashboard_data, student_info=student_info, session_id=session_id)


@app.route('/bunking-buddy/<session_id>')
def bunking_buddy(session_id):
    if session_id not in processing_status:
        return redirect(url_for('index'))
    
    status = processing_status[session_id]
    
    # Use the same dashboard_data structure
    # For now, redirect to dashboard if not completed
    if status.get('status') != 'completed':
        return redirect(url_for('dashboard', session_id=session_id))
    
    # Reuse the dashboard data preparation logic
    dashboard_data = {
        'current_overall': {'percentage': 0, 'attended': 0, 'total': 0},
        'projected_normal': {'percentage': 0, 'attended': 0, 'total': 0},
        'projected_selected': {'percentage': 0, 'attended': 0, 'total': 0},
        'subjects': [],
        'alerts': [],
        'calendar': [],
        'safe_bunk_days': [],
        'bunk_dates': [],
        'schedule_file': f'schedule_{session_id}.json',
        'horizon_days': 365  # Full year for bunking buddy
    }
    
    if 'data' in status and status['data']:
        attendance_data = status['data']
        for item in attendance_data:
            if item['Subject'] == 'OVERALL ATTENDANCE':
                percentage_str = item['Percentage'].replace('%', '')
                dashboard_data['current_overall'] = {
                    'percentage': float(percentage_str),
                    'attended': item['Attended Classes'],
                    'total': item['Total Classes']
                }
                dashboard_data['projected_normal'] = {
                    'percentage': float(percentage_str),
                    'attended': item['Attended Classes'],
                    'total': item['Total Classes']
                }
                break
    
    student_info = {'year': 'N/A', 'semester': 'N/A', 'division': 'N/A', 'batch': 'N/A', 'language': 'none'}
    return render_template('bunking_buddy_new.html', dashboard_data=dashboard_data, student_info=student_info, session_id=session_id)


@app.route('/api/dashboard/simulate', methods=['POST'])
def simulate_bunking():
    """API endpoint to simulate attendance with bunk dates"""
    data = request.get_json()
    
    if not data or 'schedule_file' not in data:
        return jsonify({'error': 'Missing schedule_file parameter'}), 400
    
    # For now, return the same data since we don't have timetable yet
    # This is a simplified version - in full app, this would calculate based on timetable
    bunk_dates = data.get('bunk_dates', [])
    
    # Get session from schedule file name (extract session_id)
    schedule_file = data.get('schedule_file', '')
    session_id = schedule_file.replace('schedule_', '').replace('.json', '')
    
    if session_id not in processing_status:
        return jsonify({'error': 'Session not found'}), 404
    
    status = processing_status[session_id]
    if 'data' not in status:
        return jsonify({'error': 'No attendance data available'}), 404
    
    attendance_data = status['data']
    
    # Calculate current overall
    total_attended = 0
    total_classes = 0
    for item in attendance_data:
        if item['Subject'] != 'OVERALL ATTENDANCE':
            total_attended += item['Attended Classes']
            total_classes += item['Total Classes']
    
    current_percentage = round((total_attended / total_classes) * 100, 2) if total_classes > 0 else 0
    
    # For simulation, assume each bunk day removes 4 classes (average)
    # In a real implementation, this would use actual timetable data
    bunked_classes = len(bunk_dates) * 4
    projected_total = total_classes + 50  # Assume 50 upcoming classes
    projected_attended = total_attended + 50 - bunked_classes  # Attend all except bunked
    projected_percentage = round((projected_attended / projected_total) * 100, 2) if projected_total > 0 else 0
    
    result = {
        'current_overall': {
            'percentage': current_percentage,
            'attended': total_attended,
            'total': total_classes
        },
        'projected_normal': {
            'percentage': round(((total_attended + 50) / projected_total) * 100, 2),
            'attended': total_attended + 50,
            'total': projected_total
        },
        'projected_selected': {
            'percentage': projected_percentage,
            'attended': projected_attended,
            'total': projected_total
        },
        'calendar': [],
        'subjects': [],
        'safe_bunk_days': [],
        'bunk_dates': bunk_dates
    }
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
