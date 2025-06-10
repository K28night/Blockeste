import schedule
import time
import os
from PIL import Image
from io import BytesIO
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
import base64
from datetime import datetime
import requests  # Missing import
from flask import Flask, render_template, redirect, url_for, flash, request, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from database import *
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer
from io import BytesIO
from PyPDF2 import PdfWriter, PdfReader
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from reportlab.lib.utils import ImageReader
# Google Drive API Setup
# SERVICE_ACCOUNT_FILE = "D:/python/BlockEstate/client_secret_978113890751-ddla1nhqobe83fl1c58p7rcvce3opq1s.apps.googleusercontent.com.json"  # Update with your path
# SCOPES = ["https://www.googleapis.com/auth/drive.file"]

app = Flask(__name__)
app.config['SECRET_KEY'] = '7842'
socketio = SocketIO(app)
app.config["ID_VERIFICATION_API"] = "https://api.idanalyzer.com"  # Replace with actual API
app.config["API_KEY"] = "HLQNJZVwI3d7LjxnM0b8P6Be0k2JJi5R"  # Replace with your API key
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
#if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif','pdf'}
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

import re
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')  # Check if user is registering or logging in

        if action == "register":  # Registration
            username = request.form['username']
            email = request.form['email']
            email = request.form.get("email")
            if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
                flash("Enter be a valid Gmail", "danger")
                return redirect(url_for("index"))
            phone = request.form['phone']
            password = request.form['password']

            qry = "SELECT * FROM register WHERE email='%s'" % (email)
            exist = select(qry)
            if exist:
                flash("Username already exists. Choose another.", "danger")
                return redirect(url_for("index"))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            qry4 = "INSERT INTO register VALUES (NULL, '%s', '%s', '%s', '%s', CURRENT_TIMESTAMP)" % (
                username, email, hashed_password, phone)
            res = insert(qry4)
            if res > 0:
                flash("Registration successful! You can now log in.", "success")

        elif action == "login":  # Login
            email = request.form['email']
            password = request.form['password']

            qry = "SELECT * FROM register WHERE email='%s'" % (email)
            n = select(qry)
            if n and check_password_hash(n[0]['password'], password):  # Secure password checking
                session['user_id'] = n[0]['user_id']  # Store user in session
                session['username'] = n[0]['user_name']
                session['email'] = n[0]['email']
                kyc = "SELECT status FROM kyc_verify WHERE user_id='%s'" % (session['user_id'])
                kyc_v = select(kyc)
                if kyc_v:
                    session['status']=kyc_v[0]['status']
                flash("Login successful!", "success")
                 # Redirect to dashboard on success
            else:
                flash("Invalid username or password.", "danger")

    return render_template("index.html")


# Dashboard Route
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("index"))
    owner=''
    prop="select * from property_reg where s_id=%s"%(str(session['user_id']))
    prop_data=select(prop)
    prop_all="select * from property_reg"
    prop_all_data=select(prop_all)
    user = {"username": session.get("username"), "email": session.get("email")}
    items = ["Stock A", "Stock B", "Stock C"]  # Example listed items
    count_in = "select count(*) from interests"
    count=select(count_in)
    count=count[0]['count(*)']
    count_s = "select count(*),p_id from property_reg where s_id=%s"%(str(session['user_id']))
    count_self=select(count_s)
    # count_self=count_self[0]['count(*)']
    watchlist="select w_id,p_id from watchlist where b_id=%s"%(str(session['user_id']))
    intrests="select * from interests where buyer_id=%s"%(str(session['user_id']))
    intrests_data=select(intrests)
    watch=select(watchlist)
    kyc_name="select full_name from kyc_verify where user_id=%s"%(str(session['user_id']))
    name=select(kyc_name)
    kyc="select status from kyc_verify where user_id=%s"%(session['user_id'])
    kyc_status=select(kyc)
    if prop_data:
        seller_name=name[0]['full_name']
        holding="select property_id from property_transfer where status='completed' and seller_name='%s'"%(seller_name)
        holding_data=select(holding)
        holding_id=holding_data[0]['property_id']
    else:
        seller_name=name[0]['full_name']
        holding="SELECT * FROM property_transfer WHERE status='completed' and buyer_name = '%s'"%(seller_name)
        holding_data=select(holding)
    matched_image = 0
    if kyc_status:
        session['status']=kyc_status[0]['status']
    if name:
        name1=name[0]['full_name']
        owner="select * from property_transfer where status='Pending' and buyer_name='%s'"%(name1)
        owner=select(owner)
        watch_ids = [w['property_id'] for w in owner]
    if prop_data:
        return render_template("welcome.html", username=user["username"], email=user["email"], items=items, prop_data=prop_data,intrests_data=intrests_data,count=count,prop_all_data=prop_all_data,watch=watch, count_self= count_self,owner=owner, matched_image= matched_image,watch_ids=watch_ids,holding_data=holding_data, holding_id= holding_id)
    return render_template("welcome.html", username=user["username"], email=user["email"], items=items,watch=watch,intrests_data=intrests_data,prop_all_data=prop_all_data,count=count, count_self= count_self,owner=owner, matched_image= matched_image,watch_ids=watch_ids,holding_data=holding_data)

# ✅ Function to Verify KYC via API
def verify_gov_id(gov_id_number, full_name, dob):
    """Verify Government ID using an external API."""
    response = requests.post(app.config["ID_VERIFICATION_API"], data={
        "apiKey": 'ovGpamrRRuiyZgzK77xvAlNQnB7stQYy',
        "id_number": gov_id_number,
        "full_name": full_name,
        "dob": dob,
    })
   
    if response.status_code == 200:
        result = response.json()
        if result.get("error"):# Return True if verified
            session['API']=result['error']['message']
            return False # True if ID is verified
        else:
             session['API']=result.get("verified")
    else:
        session['API']="request error"
    return True  # Assume failure if no response

# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('index'))



def encrypt_pdf(input_pdf_path, output_pdf_path, password):
    # Read the PDF
    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    # Add all pages to the writer
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    # Encrypt the PDF
    pdf_writer.encrypt(user_password=password, owner_password=None, use_128bit=True)

    # Write the encrypted PDF to the output file
    with open(output_pdf_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

def send_email(receiver_email, subject, body, attachment_path):
    # Create the email
    SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
    SMTP_PORT = 587  # Replace with your SMTP port
    SENDER_EMAIL = "alanpjpnc@gmail.com"  # Replace with your email
    SENDER_PASSWORD = "bioj xczl toqz nhdp"  # Replace with your email password
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF file
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(attachment_path)}'
        )
        msg.attach(part)

    # Send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def fix_base64_padding(b64_string):
    b64_string = b64_string.strip().replace("\n", "").replace(" ", "")
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += "=" * (4 - missing_padding)
    return b64_string


@app.route('/generate_agreement', methods=['GET', 'POST'])
def generate_agreement():
    user_id = request.args.get('id')
    details = "select * from kyc_verify where kyc_id=%s" % (user_id)
    details = select(details)
    username = details[0]['full_name']
    address = details[0]['address']
    phone = "43545758"
    user = details[0]['user_id']
    user_d = "select email from register where user_id=%s" % (user)
    user_d = select(user_d)
    email = user_d[0]['email']
    pan = details[0]['gov_id_number']
    sig = details[0]['signature_path']
    pan_path = details[0]['id_document_path']

    # Handle signature image
    if sig.startswith("data:image"):  # If it's a Base64 string
        base64_data = sig.split(",")[1]  # Remove the "data:image/png;base64," part
        image_data = base64.b64decode(fix_base64_padding(base64_data))
        image_buffer = BytesIO(image_data)  # Convert to BytesIO object
        image_reader = ImageReader(image_buffer)
    else:  # If it's a file path
        if os.path.exists(sig):
            image_reader = ImageReader(sig)

    # Create a BytesIO buffer to store the PDF
    buffer = BytesIO()

    # Create the PDF object using the buffer
    pdf = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['BodyText']
    bold_style = ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold')

    # Content
    content = []

    # Add company logo
    logo = Image("./static/image/logo.jpg", width=1.5*inch, height=0.75*inch)
    content.append(logo)
    content.append(Spacer(1, 12))

    # Add title
    title = Paragraph("Demat Account Agreement", title_style)
    content.append(title)
    content.append(Spacer(1, 12))

    # Add user details
    user_details = [
        ["Name:", username],
        ["Address:", address],
        ["Contact Number:", phone],
        ["Email Address:", email],
        ["PAN Number:", pan]
    ]
    user_table = Table(user_details, colWidths=[1.5*inch, 4*inch])
    user_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    content.append(Paragraph("User Details:", bold_style))
    content.append(Spacer(1, 6))
    content.append(user_table)
    content.append(Spacer(1, 12))

    # Add PAN card image
    pan_image = Image(pan_path, width=2*inch, height=1*inch)
    content.append(Paragraph("PAN Card Image:", bold_style))
    content.append(Spacer(1, 6))
    content.append(pan_image)
    content.append(Spacer(1, 12))

    # Add signature image
    signature_image = Image(sig, width=2*inch, height=1*inch)
    content.append(Paragraph("Signature Image:", bold_style))
    content.append(Spacer(1, 6))
    content.append(signature_image)
    content.append(Spacer(1, 12))

    # Add introduction
    introduction = Paragraph(
        "Welcome to Blockeste! This agreement outlines the terms and conditions...",
        normal_style
    )
    content.append(introduction)
    content.append(Spacer(1, 12))

    # Add disclaimer
    disclaimer = Paragraph(
        "<b>Disclaimer:</b> Please note that Blockeste operates on the Ethereum blockchain and is not regulated by the Securities and Exchange Board of India (SEBI). This platform is designed for [specific purpose, e.g., decentralized record-keeping, transparent transactions, etc.].",
        normal_style
    )
    content.append(disclaimer)
    content.append(Spacer(1, 12))

    # Add definitions
    definitions = [
        ["1. Definitions", ""],
        ["- Demat Account:", "..."],
        ["- Blockchain:", "..."],
        ["- Smart Contract:", "..."],
        ["- Ethereum:", "..."]
    ]
    definitions_table = Table(definitions, colWidths=[1.5*inch, 4*inch])
    definitions_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    content.append(Paragraph("Definitions:", bold_style))
    content.append(Spacer(1, 6))
    content.append(definitions_table)
    content.append(Spacer(1, 12))

    # Add account opening process
    content.append(Paragraph("<b>2. Account Opening</b>", bold_style))
    content.append(Spacer(1, 6))

    account_opening_data = [
    [Paragraph("<b>Eligibility</b>", bold_style), Paragraph("Users must be 18+ and comply with KYC verification.", normal_style)],
    [Paragraph("<b>Documents Required</b>", bold_style), Paragraph("PAN card, Aadhaar, and a signature sample are mandatory.", normal_style)],
    [Paragraph("<b>Blockchain Account</b>", bold_style), Paragraph("An Ethereum wallet address is generated for the Demat account.", normal_style)],
    ]

    account_opening_table = Table(account_opening_data, colWidths=[2*inch, 3.5*inch])  # Adjusted Width
    account_opening_table.setStyle(TableStyle([
    ('FONT', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 11),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('WORDWRAP', (0, 0), (-1, -1), 'ON'),
    ]))

    content.append(account_opening_table)
    content.append(Spacer(1, 12))

    # Add a page break if needed
   

    # Add charges and fees on the second page
    content.append(Paragraph("<b>3. Charges and Fees</b>", bold_style))
    content.append(Spacer(1, 6))

    charges_fees_data = [
    [Paragraph("<b>Account Opening Charge</b>", bold_style), Paragraph("No charge for opening a Demat account.", normal_style)],
    [Paragraph("<b>Annual Maintenance Charge (AMC)</b>", bold_style), Paragraph("0.001 ETH(334.59 INR) per year from the second year.", normal_style)],
    [Paragraph("<b>Transaction Charges</b>", bold_style), Paragraph("0.005 ETH(933.50 INR) per transaction.", normal_style)],
    [Paragraph("<b>Gas Fees</b>", bold_style), Paragraph("Users must pay Ethereum gas fees for blockchain transactions.", normal_style)],
    [Paragraph("<b>Other Charges</b>", bold_style), Paragraph("Additional services like SMS alerts are chargeable.", normal_style)],
    ]

    charges_fees_table = Table(charges_fees_data, colWidths=[2*inch, 3.5*inch])  # Adjusted Width
    charges_fees_table.setStyle(TableStyle([
    ('FONT', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 11),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('WORDWRAP', (0, 0), (-1, -1), 'ON'),
    ]))

    content.append(charges_fees_table)
    content.append(Spacer(1, 12))

    # Build the PDF
    pdf.build(content)

    # Move the buffer's cursor to the beginning
    buffer.seek(0)

    # Save the PDF to a temporary file
    temp_pdf_path = "temp_agreement.pdf"
    with open(temp_pdf_path, "wb") as temp_pdf:
        temp_pdf.write(buffer.getvalue())

    # Encrypt the PDF using the PAN card number as the password
    password = pan  # Use the PAN card number as the password
    encrypted_pdf_path = "encrypted_agreement.pdf"
    encrypt_pdf(temp_pdf_path, encrypted_pdf_path, password)

    # Send the encrypted PDF via email
    subject = "Your Demat Account Agreement"
    body = f"Dear {username},\n\nPlease find attached your Demat Account Agreement. The PDF is encrypted with your PAN card number ({pan}) as the password.\n\nBest regards,\n Blockeste"
    send_email(email, subject, body, encrypted_pdf_path)

    # Delete temporary files
    os.remove(temp_pdf_path)
    os.remove(encrypted_pdf_path)

    kyc = "select * from kyc_verify where status='pending' or status='rejected'"
    kyc_detail = select(kyc)

    return render_template("admin_kyc_verify.html", kyc_detail=kyc_detail)

@app.route("/kyc_verify", methods=["GET", "POST"])
def kyc_verify():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        dob = request.form.get("dob")
        address = request.form.get("address")
        gov_id_number = request.form.get("gov_id_number")
        id_document = request.files.get("id_document")  # PAN Card
        selfie = request.files.get("selfie")
        signature_data = request.form.get("signature_data")
        # signature_data = request.form["signature"].replace('data:image/png;base64,', '')

        # Validate Date of Birth
        session['API']="dvwvw"
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d")
            if dob_date > datetime.today():
                flash("Date of Birth cannot be in the future.", "error")
                return redirect(url_for("kyc_verify"))
            if (datetime.today().year - dob_date.year) < 18:
                flash("You must be at least 18 years old.", "error")
                return redirect(url_for("kyc_verify"))
        except ValueError:
            flash("Invalid Date of Birth format.", "error")
            return redirect(url_for("kyc_verify"))
        # if signature_data:
        #     signature_filename = "signature.png"
        #     signature_path = os.path.join(app.config["UPLOAD_FOLDER"], signature_filename)

        #     # Convert Base64 string to an image
        #     signature_data = signature_data.split(",")[1]  # Remove "data:image/png;base64,"
        #     signature_image = Image.open(BytesIO(base64.b64decode(signature_data)))
        #     signature_image.save(signature_path)

        #     img_paths.append(signature_path)
        # Ensure user is logged in
        user_id = session.get("user_id")
        if not user_id:
            flash("User ID not found. Please log in again.", "danger")
            return redirect(url_for("index"))

        if not (full_name and dob and address and gov_id_number and id_document and selfie and signature_data):
            flash("All fields are required!", "danger")
            return redirect(url_for("kyc_verify"))

        documents = [id_document, selfie]
        img_paths = []  # Initialize empty array

        for file in documents:
            if file and allowed_file(file.filename):  # Check if file exists and has an allowed extension
                filename = secure_filename(file.filename)  # Secure the filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Create the full file path
                file.save(file_path)  # Save the file to the specified path
                img_paths.append(file_path)  # Add the file path to the img_paths list
            else:
                flash("Invalid file type. Only PNG and JPEG files are allowed.", "danger")
                return redirect(url_for("kyc_verify"))
        # Insert image path into database
        # image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # # Read File Data (Convert to Base64 for Storing)
        # id_document_data = base64.b64encode(id_document.read()).decode("utf-8")  # PAN Card
        # selfie_data = base64.b64encode(selfie.read()).decode("utf-8")
        # signature_binary = base64.b64decode(signature_data)
        # signature_base64 = base64.b64encode(signature_binary).decode("utf-8")
        # if  id_document_data:
        #     flash(" {id_document_data}", "danger")
        # else:
        #     flash(" {id_document_data}", "danger")

        # ✅ **Verify PAN Card via API**
        is_verified = verify_gov_id(gov_id_number, full_name, dob)
        verification_status = "verified" if is_verified else "pending"
        verified_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if is_verified else "NULL"
        # if "data:image" in signature_data:
        #     signature_data = signature_data.split(",")[1]  # Get only Base64 data part

        # # Decode and Save the Signature Image
        # signature_filename = f"signature_{session['user_id']}.png"
        # signature_path = os.path.join(app.config["UPLOAD_FOLDER"], signature_filename)

        # with open(signature_path, "wb") as f:
        #     f.write(base64.b64decode(signature_data))  # Convert Base64 to binary
            
        # Store Data in Database
        qry4 = """INSERT INTO kyc_verify (user_id, full_name, dob, address, gov_id_number, id_document_path, selfie_path, signature_path, status, submitted_at, verified_at) 
          VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', CURRENT_TIMESTAMP, %s)""" % (
            user_id, full_name, dob, address, gov_id_number, img_paths[0], img_paths[1],signature_data, verification_status, 
            f"'{verified_at}'" if is_verified else "NULL"
        )
        res = insert(qry4)
        if res:
            flash("KYC Submitted Successfully! Verification is in progress.", "success")
            session['status'] = "Pending"
            return redirect(url_for("kyc_verify"))
        else:
            flash("Database error. Please try again.", "danger")

    return render_template("kyc_verify.html")

# ✅ **Scheduled Function for Re-verifying Pending KYCs**

def verify_kyc():
    """Re-check pending KYCs via API every 24 hours."""
    print("Scheduled KYC verification running...")


    # Fetch pending KYCs
    query=("SELECT kyc_id, gov_id_number, full_name, dob FROM kyc_verify WHERE status = 'pending'")
    pending_kycs = select(query)

    for kyc in pending_kycs:
        kyc_id, gov_id_number, full_name, dob = kyc

        if verify_gov_id(gov_id_number, full_name, dob):
            verified_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_query = "UPDATE kyc_verify SET status = 'verified', verified_at = '%s' WHERE kyc_id = %s" % (verified_at, kyc_id)
            if update(update_query):
                print(f"KYC ID {kyc_id} verified successfully.")
        else:
            verified_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            flash(str(session.get('API', 'API key not found')), "danger")
            update_query = "UPDATE kyc_verify SET status = 'rejected', verified_at = '%s' WHERE kyc_id = %s" % (verified_at, kyc_id)
           
            update(update_query)
    else:
        print(f"No pending KYCs found.{kyc_id}")
   
# ✅ **Schedule Verification Every 24 Hours**
# schedule.every(1).hour.do(verify_kyc)

# Background thread to run scheduled tasks
import threading

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

# Run scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

@app.route("/upload",methods=['POST','GET'])
def upload():
    if session['status']!='verified':
        flash("You have no demate account",'danger')
        return render_template("property_upload.html")
    u_details="select * from register where user_id=%s"%(session['user_id'])
    u_details=select(u_details)
    if 'submit' in request.form:
        pname=request.form['propertyName']
        ptype=request.form['propertyType']
        padd=request.form['propertyAddress']     
        # state,district and city
        state=request.form['state']
        district=request.form['district']
        city=request.form['city']
        s_email=request.form['sellerEmail']
        s_name=request.form['sellerName']
        pin=request.form['pincode']
        phno=request.form['sellerPhone']
        area=request.form['area']
        price=request.form['price']
        discription=request.form['description']
        propertyImage=request.files['propertyImage']
        saleDeed=request.files['saleDeed']
        taxReceipts=request.files['taxReceipts']
        encumbranceCertificate=request.files['encumbranceCertificate']
        approvalPlans=request.files['approvalPlans']
        if  approvalPlans:
            documents = [saleDeed, taxReceipts, encumbranceCertificate,propertyImage,approvalPlans]
        else:
            documents = [saleDeed, taxReceipts, encumbranceCertificate,propertyImage]
        img_paths = []  # Initialize empty array

        for file in documents:
            if file and allowed_file(file.filename):  # Check if file exists and has an allowed extension
                filename = secure_filename(file.filename)  # Secure the filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Create the full file path
                file.save(file_path)  # Save the file to the specified path
                img_paths.append(file_path)  # Add the file path to the img_paths list
            else:
                flash("Invalid file type. Only PNG and JPEG files are allowed.", "danger")
                return redirect(url_for("upload"))
        if img_paths[4]:
           build_plan=img_paths[4]
        else:
            build_plan='null'
    #     if 'img' not in request.files:
    #         return "No file part", 400 
    # file = request.files.get('img')
    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #     img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
        # qry="insert into login values(null,'%s','%s','buyer')"%(email,password)
        # res=insert(qry)

        prop = "INSERT INTO property_reg VALUES (NULL, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', CURRENT_TIMESTAMP,'pending',NULL,0)" % (
        pname, ptype, str(padd), str(state), str(district), str(city), str(pin), str(price), str(area), str(discription), 
        str(session['user_id']), str(img_paths[0]), str(img_paths[1]), str(img_paths[2]), str(build_plan), str(img_paths[3])
        )
        n=insert(prop)
        if n :
             flash("Registration successfull waite for approvel", "success")
        else:
            flash("Somthing went wrong refresh", "danger")
   
    return render_template("property_upload.html", u_details= u_details)

@app.route("/view_property",methods=['POST','GET'])
def view_property():
    view="select * from property_reg where s_index=0"
    proper=select(view)
    count_in = "select count(*),p_id from interests"
    count_in=select(count_in)
    count=count_in[0]['count(*)']
    watchlist="select w_id,p_id from watchlist where b_id=%s"%(str(session['user_id']))
    watch=select(watchlist)
    if watch:
        return render_template("view_property.html",proper=proper,count_in=count_in,count=count,watch=watch) 
    return render_template("view_property.html",proper=proper,count_in=count_in,count=count) 


@app.route("/view_each_property",methods=['GET'])
def view_each_property():
    if 'status' in session:
        if session['status']!='verified':
            flash('You have no Demat account...!','danger')
    else:
        flash('You have no Demat account...!','danger')
    if request.args.get('id'):
        session['id']=request.args.get('id')
        session['s_id']=request.args.get('s_id')
        count="select count(*) from property_reg where p_id='%s'"%(session['id'])
        count=select(count)
        view="select * from property_reg where p_id='%s'"%(str(session['id']))
        each=select(view)
        view1="select user_name,email,phone from register where user_id='%s'"%(session['s_id'])
        seller=select(view1)
        session['s_id']=each[0]['s_id']
    else:
        view="select * from property_reg where p_id='%s'"%(str(session['id']))
        each=select(view)
        view1="select user_name,email,phone from register where user_id='%s'"%(session['s_id'])
        seller=select(view1)
        view="select * from property_reg "
        proper=select(view)
        count="select count(*) from property_reg where p_id='%s'"%(proper[0]['p_id'])
        count=select(count)
    if 'userRate' in request.args:
        b_id=session['user_id'] 
        view="select * from property_reg where p_id='%s'"%(str(session['id']))
        each=select(view)
        view1="select user_name,email,phone from register where user_id='%s'"%(session['s_id'])
        seller=select(view1)
        id=session['id']  
        s_id=session['s_id']
        price=request.args.get('userRate')
        msg=request.args.get('message')
        intrest="INSERT INTO interests values(NULL,%s,%s,%s,%s, '%s' ,'sended',CURRENT_TIMESTAMP)"%( b_id,id,s_id,price,msg)
        if insert(intrest):
            flash('intrest send successful','success')
        else:
            flash('sending Failed!','danger')
    return render_template("view_each_property.html",each_one=each,seller=seller,count=count)


@app.route("/view_intrests",methods=['POST','GET'])
def view_intrests():
        p_id=request.args.get('id')
        view="select * from interests where seller_id=%s and p_id=%s"%(str(session['user_id']),p_id)
        prop=select(view)
        b_id = [item['buyer_id'] for item in prop] 
        # Check if b_id has values
        if b_id:
        # Convert list of IDs to a string format for SQL
            id_list = ', '.join(str(x) for x in b_id)  # "40, 3, 2"
        b_details=f"select user_id,user_name,email,phone from register where user_id IN ({id_list})"
        b_detail=select(b_details)
        proper="select * from property_reg where s_id=%s and p_id=%s"%(str(session['user_id']),p_id)
        propert=select(proper)
        count_in = "select count(*) from interests where seller_id=%s"%(str(session['user_id']))
        count=select(count_in)
        count=count[0]['count(*)']
        return render_template("view_intrests.html",intrest=prop,b_detail=b_detail,propert=propert,count=count)


@app.route("/brokerage",methods=['POST','GET'])
def brokerage():
    return render_template("brokerage_calculator.html")
#watchlist with using b_id and p_id
@app.route("/add_watchlist",methods=['POST','GET'])
def add_watchlist():
    p_id=request.args.get('p_id')
    b_id=session['user_id']
    view="insert into watchlist values(NULL,%s,%s,CURRENT_TIMESTAMP,1)"%(b_id,p_id)
    watch=insert(view)
    return redirect(url_for('view_property'))

@app.route("/remove_watchlist",methods=['POST','GET'])
def remove_watchlist():
    p_id=request.args.get('p_id')
    b_id=session['user_id']
    view="delete from watchlist where b_id=%s and p_id=%s"%(b_id,p_id)
    watch=delete(view)
    view_property()
   
    return redirect(url_for('view_property'))

@app.route("/remove_watchlist_home",methods=['POST','GET'])
def remove_watchlist_get():
    w_id=request.args.get('w_id')
    view="delete from watchlist where w_id=%s"%(w_id)
    watch=delete(view)
    return redirect(url_for('dashboard'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Define the Message model
# class Message(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     sender_id = db.Column(db.Integer, nullable=False)  # ID of the sender
#     receiver_id = db.Column(db.Integer, nullable=False)  # ID of the receiver
#     content = db.Column(db.String(500), nullable=False)  # Message content
#     timestamp = db.Column(db.String(50), nullable=False)  # Timestamp of the message

# # Create the database and tables
# with app.app_context():
#     db.create_all()
    
@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin_kyc_verify",methods=['POST','GET'])
def admin_kyc_verify():
    if 'id' in request.args:
        id=request.args.get('id')
        update_kyc=query = "UPDATE kyc_verify SET verified_at = CURRENT_TIMESTAMP, status = 'verified' WHERE kyc_id = %s"%(id)
        query=update(update_kyc)
        if(query):
            # redirect to the /generate_agreement page with perameter id
           return redirect(url_for('generate_agreement', id=id))
        
        
    kyc="select * from kyc_verify where status='pending' or status='rejected'"
    kyc_detail=select(kyc)
    
    return render_template("admin_kyc_verify.html",kyc_detail=kyc_detail)

@app.route("/admin_property_verify",methods=['POST','GET'])
def admin_property_verify():
    message=""
    seller=""
    if 'a_id' in request.args:
        id=request.args.get('a_id')
        update_property=query = "UPDATE property_reg SET verified_at = CURRENT_TIMESTAMP, status = 'verified' WHERE p_id = %s"%(id)
        query=update(update_property)
    elif 'r_id' in request.args:
            id=request.args.get('r_id')
            update_property=query = "UPDATE property_reg SET verifyed_at = CURRENT_TIMESTAMP, status = 'reject' WHERE p_id = %s"%(id)
            query=update(update_property)
            
    property="select * from property_reg where status='pending' or status='rejected'"
    property_detail=select(property)
    id_list = [item["s_id"] for item in property_detail]
    id_tuple = tuple(id_list)  # Convert list to tuple for SQL query

# Format SQL query
    if len(id_tuple) == 1:
        seller = f"SELECT * FROM kyc_verify WHERE user_id = ({id_tuple[0]})"
        seller=select(seller)
    elif len(id_list)>1:
        seller = f"SELECT * FROM kyc_verify WHERE user_id IN {id_tuple}"
        seller=select(seller)
    else:
        message="no Users"
    return render_template("admin_property_verify.html",property_detail=property_detail,seller=seller,message=message)
    

@app.route("/chat")
def chat():
    if 'user_id' not in session:
        return "User not logged in", 403  # Ensure user is logged in
    sender_id = session['user_id']  # Get sender ID from session
    receiver_id = request.args.get('b_id', type=int)  # Get receiver ID from URL parameter
    return render_template('chat.html', sender_id=sender_id, receiver_id=receiver_id)

# Handle incoming messages
@socketio.on('message')
def handle_message(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    message = data.get('message')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if it's the first message
    if sender_id != 1 and Message.query.count() == 0:  # Assuming seller_id is 1
        # Reject the message if the buyer tries to send the first message
        send({
            'error': 'Seller must send the first message.'
        }, room=request.sid)  # Send error only to the buyer
        return

    # Save the message to the database
    new_message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=message,
        timestamp=timestamp
    )
    db.session.add(new_message)
    db.session.commit()

    # Broadcast the message to all clients
    send({
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'message': message,
        'timestamp': timestamp
    }, broadcast=True)

# Send stored messages to a newly connected client
# @socketio.on('request_messages')
# def send_stored_messages():
#     messages = Message.query.order_by(Message.timestamp).all()
#     for msg in messages:
#         send({
#             'sender_id': msg.sender_id,
#             'receiver_id': msg.receiver_id,
#             'message': msg.content,
#             'timestamp': msg.timestamp
#         })

@app.route("/smart_contract",methods=['POST','GET'])
def smart_contract():
    if 'b_id' in request.args:
        intrest="select * from interests where in_id=%s"%(request.args.get('b_id'))
        intrest=select(intrest)
        buyer="select full_name from kyc_verify where user_id=%s"%(intrest[0]['buyer_id'])
        buyer=select(buyer)
        seller="select full_name from kyc_verify where user_id=%s"%(intrest[0]['seller_id'])
        seller=select(seller)
        property="select state,district,city,p_address from property_reg where p_id=%s"%(intrest[0]['p_id'])
        property=select(property)
        return render_template('smart_contract.html',intrest=intrest,buyer=buyer,seller=seller, property= property)
    elif 'buyer_name' in request.args:
        buyer_name = request.args.get('buyer_name')
        seller_name=request.args.get('seller_name')
        propertyId=request.args.get('propertyId')
        property_loc=request.args.get('property_loc')
        formatted_location = "'{}'".format(property_loc)  # Adds single quotes around the value
        price=request.args.get('price')
        agreement=request.args.get('agreement')
        owner="insert into property_transfer values(NULL,%s,'%s','%s',%s,%s,'%s',NULL,'Pending',CURRENT_TIMESTAMP)"%(propertyId,seller_name,buyer_name,formatted_location,price,agreement)
        owner=insert(owner)
        if owner:
            flash("sumited","sucess")
    else:
        flash("form not submited","danger")
    return render_template("smart_contract.html")
        
@app.route("/buyer_approval_ownership",methods=['POST','GET'])
def buyer_approval_ownership():
    if 'o_id' in request.args:
        intrest="select * from property_transfer where agreement_id=%s"%(request.args.get('o_id'))
        intrest=select(intrest)
    return render_template("buyer_approval_ownership.html",intrest=intrest)

# @socketio.on("send_message")
# def handle_message(data):
#     s_id = data["s_id"]
#     b_id = data["b_id"]
#     message = data["message"]

#     # Store message in DB
#     query = "INSERT INTO chat (s_id, b_id, message) VALUES (%s, %s, %s)"
#     cursor.execute(query, (s_id, b_id, message))
#     db.commit()

#     # Broadcast message to both users
#     emit("receive_message", data, broadcast=True)

# @socketio.on("load_messages")
# def load_messages(data):
#     s_id, b_id = data["s_id"], data["b_id"]
#     query = "SELECT * FROM chat WHERE (s_id=%s AND b_id=%s) OR (s_id=%s AND b_id=%s) ORDER BY datetime ASC"
#     cursor.execute(query, (s_id, b_id, b_id, s_id))
#     messages = cursor.fetchall()

#     chat_history = [{"message": msg[3], "datetime": str(msg[4])} for msg in messages]
#     emit("chat_history", chat_history)
import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
# ✅ Load trained model with error handling
try:
    model = load_model("house_price_model.h5", custom_objects={"mse": MeanSquaredError()})
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# ✅ Load encoders and scaler with error handling
try:
    with open("encoders_scaler.pkl", "rb") as f:
        data_dict = pickle.load(f)

    label_encoders = data_dict["encoders"]
    scaler = data_dict["scaler"]
    print("✅ Encoders and scaler loaded successfully!")
except Exception as e:
    print(f"❌ Error loading encoders/scaler: {e}")
    exit()

# ✅ Function to preprocess user input
def preprocess_input(user_input):
    categorical_cols = ['State', 'City', 'Locality', 'Property_Type', 'Furnished_Status', 
                        'Facing', 'Owner_Type', 'Availability_Status', 
                        'Public_Transport_Accessibility', 'Parking_Space', 'Security']
    
    # Encode categorical inputs
    for col in categorical_cols:
        if col in user_input:
            if user_input[col] in label_encoders[col].classes_:
                user_input[col] = label_encoders[col].transform([user_input[col]])[0]
            else:
                print(f"⚠ Warning: {user_input[col]} not found in training data. Using default 0.")
                user_input[col] = 0  # Default to 0 if unseen category

    # Convert to NumPy array and reshape
    input_features = np.array([list(user_input.values())], dtype=np.float32)

    # Scale the data
    input_features = scaler.transform(input_features)

    # Reshape for LSTM (batch_size, time_steps, features)
    input_features = input_features.reshape((1, 1, input_features.shape[1]))  

    return input_features


import requests

def get_eth_inr_exchange_rate():
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=inr')
        data = response.json()
        return data['ethereum']['inr']
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

def convert_inr_to_eth(inr_amount, exchange_rate):
    if exchange_rate:
        return inr_amount / exchange_rate
    else:
        return None

from flask import Flask, request, jsonify, render_template
from make_prediction import preprocess_input, model  # Import only necessary functions

@app.route('/prediction', methods=['POST', 'GET'])
def prediction():
    result = None  # Initialize result as None

    if request.method == 'POST':  # Check for POST request
        try:
            # Get form data and convert necessary values to correct types
            user_input = {
                "Size_in_SqFt": float(request.form['Size_in_SqFt']),
                "Price_per_SqFt": float(request.form['Price_per_SqFt']),
                "Year_Built": int(request.form['Year_Built']),
                "Floor_No": int(request.form['Floor_No']),
                "Total_Floors": int(request.form['Total_Floors']),
                "Age_of_Property": int(request.form['Age_of_Property']),
                "Nearby_Schools": int(request.form['Nearby_Schools']),
                "Nearby_Hospitals": int(request.form['Nearby_Hospitals']),
                "State": request.form['State'],
                "City": request.form['City'],
                "Locality": request.form['Locality'],
                "Property_Type": request.form['Property_Type'],
                "Furnished_Status": request.form['Furnished_Status'],
                "Facing": request.form['Facing'],
                "Owner_Type": request.form['Owner_Type'],
                "Availability_Status": request.form['Availability_Status'],
                "Public_Transport_Accessibility": request.form['Public_Transport_Accessibility'],
                "Parking_Space": request.form['Parking_Space'],
                "Security": request.form['Security']
            }

            # Preprocess input
            input_data = preprocess_input(user_input)
            
             # Fetch the latest ETH to INR exchange rate
            eth_inr_rate = get_eth_inr_exchange_rate()

            

            # Make prediction
            predicted_price = model.predict(input_data)[0][0]  # Extract the price from the prediction
            # Convert the predicted price to ETH
            predicted_price_eth = convert_inr_to_eth(predicted_price, eth_inr_rate)
            
            result = f"🏠 Predicted Price: ₹{predicted_price:,.2f} Lakhs"
            
            if predicted_price_eth is not None:
                result_eth = f" (≈ {predicted_price_eth:,.4f} ETH)"
            else:
                result_eth = ""

            result = result + result_eth

        except Exception as e:
            result = f"❌ Error: {e}"  # Handle errors gracefully

    
    return render_template('prediction.html', result=result)
# CoinGecko API endpoint for real-time ETH price
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"

@app.route("/get_eth_price")
def get_eth_price():
    try:
        response = requests.get(COINGECKO_API_URL)
        data = response.json()
        eth_price = data["ethereum"]["usd"]
        return jsonify({"eth_price": eth_price})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

@app.route("/payment",methods=['POST','GET'])
def payment():
    if 'o_id' in request.args:
        transfer="select * from property_transfer where agreement_id=%s"%(request.args.get('o_id'))
        transfer=select(transfer)
        property="select * from  property_reg where p_id=%s"%(transfer[0]['property_id'])
        property=select(property)
    return render_template('payment1.html',transfer=transfer,property=property)

from flask import request, make_response
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import base64
import os
import datetime
import qrcode
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pikepdf  # For PDF encryption

# from blk import *
@app.route('/transaction-success')
def transaction_success():
    if 'o_id' in request.args:
        o_id = request.args.get('o_id')
        update_prop="UPDATE property_transfer SET status='completed' WHERE agreement_id=%s"%(o_id)
        update_prop=update(update_prop)
        select_prop="select property_id from property_transfer WHERE agreement_id=%s"%(o_id)
        select_prop=select(select_prop)
        update_property = "UPDATE property_reg SET s_index=1 WHERE p_id=%s"%(select_prop[0]['property_id'])
        update_property=update(update_property)
        def generate_property_agreement(a_id):
            # Get user and property data from request
            user_data = "select * from property_transfer where agreement_id=%s" % (a_id)
            user_data = select(user_data)
            user_id='75'
            user_name = user_data[0]['buyer_name']
            property_id = user_data[0]['property_id']
    
            # Fetch all required details
            buyer_details = get_user_details(user_name)  # Contains buyer PAN
            seller_details = get_seller_details(property_id)  # Contains seller PAN
            property_details = get_property_details(property_id)
            transaction_details = get_transaction_details(user_name, property_id)
       
            # Generate the PDF
            pdf_buffer = generate_agreement_pdf(buyer_details, seller_details, property_details, transaction_details)
       
            # Create encrypted versions with both passwords
            encrypted_pdf_buffer = encrypt_pdf(
              pdf_buffer, 
              passwords=[buyer_details['pan_number'], seller_details['pan_number']]
            )
       
            # Send emails to both parties
            send_agreement_to_parties(
              buyer_details,
              seller_details,
              property_details,
              encrypted_pdf_buffer
                )
       
            # Return the PDF as response (or could return success message)
            encrypted_pdf_buffer.seek(0)
            response = make_response(encrypted_pdf_buffer.read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=Blockeste_Agreement_{property_id}.pdf'
            return response
    return render_template('transaction_success.html')







def generate_agreement_pdf(buyer_details, seller_details, property_details, transaction_details):
    # Create PDF buffer
    buffer = BytesIO()
    
    # Create document with margins
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        leading=22,
        spaceAfter=12,
        alignment=1
    )
    
    heading1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    bold_style = ParagraphStyle(
        'Bold',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        fontName='Helvetica-Bold'
    )
    
    # Story holds all the flowables for the PDF
    story = []
    
    # Add header with logo
    logo_path = "static/images/blockeste_logo.png"
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=1*inch)
        story.append(logo)
    
    # Title and metadata
    today = datetime.datetime.now().strftime("%B %d, %Y")
    agreement_number = f"BLK-{property_id}-{user_id}-{today.replace(' ', '')}"
    
    story.append(Paragraph("BLOCKCHAIN PROPERTY OWNERSHIP AGREEMENT", title_style))
    
    meta_data = [
        ["Agreement Number:", agreement_number],
        ["Date:", today],
        ["Blockchain:", "Ethereum Mainnet"],
        ["Smart Contract:", property_details['contract_address']]
    ]
    
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2e7d32')),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 24))
    
    # Parties section
    story.append(Paragraph("1. PARTIES", heading1_style))
    
    buyer_data = [
        ["<b>BUYER:</b>", ""],
        ["Full Name:", buyer_details['full_name']],
        ["PAN Number:", buyer_details['pan_number']],
        ["Wallet Address:", buyer_details['wallet_address']],
        ["Email:", buyer_details['email']]
    ]
    
    seller_data = [
        ["<b>SELLER:</b>", ""],
        ["Full Name:", seller_details['full_name']],
        ["PAN Number:", seller_details['pan_number']],
        ["Wallet Address:", seller_details['wallet_address']],
        ["Email:", seller_details['email']]
    ]
    
    parties_table = Table(buyer_data + [[Spacer(1, 12)]] + seller_data, 
                         colWidths=[1.5*inch, 4.5*inch])
    story.append(parties_table)
    story.append(Spacer(1, 12))
    
    # Property details
    story.append(Paragraph("2. PROPERTY DETAILS", heading1_style))
    
    property_data = [
        ["Property ID:", property_details['property_id']],
        ["Address:", property_details['full_address']],
        ["Token ID:", property_details['token_id']],
        ["Purchase Price:", f"{property_details['price']} ETH"],
        ["NFT Contract:", property_details['nft_contract']]
    ]
    
    property_table = Table(property_data, colWidths=[1.5*inch, 4.5*inch])
    story.append(property_table)
    story.append(Spacer(1, 12))
    
    # Transaction details
    story.append(Paragraph("3. TRANSACTION DETAILS", heading1_style))
    
    formatted_date = datetime.datetime.strptime(transaction_details['date'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y at %H:%M:%S UTC")
    
    transaction_data = [
        ["Transaction Hash:", transaction_details['tx_hash']],
        ["Block Number:", str(transaction_details['block_number'])],
        ["Date Transferred:", formatted_date]
    ]

    transaction_table = Table(transaction_data, colWidths=[1.5*inch, 4.5*inch])
    story.append(transaction_table)
    story.append(Spacer(1, 24))
    
    # Terms and Conditions
    story.append(Paragraph("4. TERMS AND CONDITIONS", heading1_style))
    terms = [
        Paragraph("<b>4.1 Ownership Transfer:</b> The Seller transfers all rights to the Buyer, recorded on the Ethereum blockchain.", normal_style),
        Paragraph("<b>4.2 Smart Contract:</b> Ownership is governed by the smart contract at " + property_details['contract_address'], normal_style),
        # Add more terms as needed
    ]
    story.extend(terms)
    story.append(Spacer(1, 24))
    
    # Signatures
    story.append(Paragraph("5. SIGNATURES", heading1_style))
    # Prepare signature images
    buyer_signature_img = None
    seller_signature_img = None
    
    if buyer_details.get('signature_image'):
        try:
            if buyer_details['signature_image'].startswith('data:image'):
                # Handle base64 signature
                signature_data = buyer_details['signature_image'].split(',')[1]
                buyer_signature_img = Image(BytesIO(base64.b64decode(signature_data)), 
                                          width=2*inch, height=0.8*inch)
            elif os.path.exists(buyer_details['signature_image']):
                # Handle file path signature
                buyer_signature_img = Image(buyer_details['signature_image'], 
                                          width=2*inch, height=0.8*inch)
        except Exception as e:
            print(f"Error loading buyer signature: {e}")
    
    if seller_details.get('signature_image'):
        try:
            if seller_details['signature_image'].startswith('data:image'):
                signature_data = seller_details['signature_image'].split(',')[1]
                seller_signature_img = Image(BytesIO(base64.b64decode(signature_data)), 
                                          width=2*inch, height=0.8*inch)
            elif os.path.exists(seller_details['signature_image']):
                seller_signature_img = Image(seller_details['signature_image'], 
                                          width=2*inch, height=0.8*inch)
        except Exception as e:
            print(f"Error loading seller signature: {e}")
    
    # Signature table with images or placeholder lines
    sig_data = [
        ["SELLER:", "BUYER:"],
        [Paragraph(seller_details['full_name'], bold_style), 
         Paragraph(buyer_details['full_name'], bold_style)],
        [seller_signature_img or Spacer(1, 0.5*inch), 
         buyer_signature_img or Spacer(1, 0.5*inch)],
        [f"Date: {formatted_date.split(' at ')[0]}", 
         f"Date: {formatted_date.split(' at ')[0]}"]
    ]
    
    sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(sig_table)
    
    # QR Code
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(f"Blockeste Property Transfer\nTX Hash: {transaction_details['tx_hash']}")
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    story.append(Spacer(1, 12))
    story.append(Image(qr_buffer, width=1.5*inch, height=1.5*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def encrypt_pdf(pdf_buffer, passwords):
    """Encrypt PDF with multiple passwords using pikepdf"""
    # Create temporary file
    temp_path = "temp_agreement.pdf"
    with open(temp_path, "wb") as f:
        f.write(pdf_buffer.getvalue())
    
    # Encrypt with all passwords
    pdf = pikepdf.open(temp_path)
    pdf.save("encrypted.pdf", 
            encryption=pikepdf.Encryption(
                user=passwords[0],  # First password (buyer PAN)
                owner=passwords[1],  # Second password (seller PAN)
                R=6,  # AES-256 encryption
                allow_printing=False,
                allow_modify_assembly=False,
                allow_extract=False
            ))
    
    # Read back the encrypted file
    with open("encrypted.pdf", "rb") as f:
        encrypted_buffer = BytesIO(f.read())
    
    # Clean up temp files
    os.remove(temp_path)
    os.remove("encrypted.pdf")
    
    return encrypted_buffer

def send_agreement_to_parties(buyer, seller, property, pdf_buffer):
    """Send encrypted PDF to both buyer and seller"""
    # Email configuration (replace with your SMTP details)
    smtp_server = "smtp.yourdomain.com"
    smtp_port = 587
    smtp_username = "alanpjpnc@gmail.com"
    smtp_password = "bioj xczl toqz nhdp"
    
    # Send to buyer
    send_email(
        smtp_server, smtp_port, smtp_username, smtp_password,
        recipient=buyer['email'],
        subject="Your Blockeste Property Ownership Agreement",
        body=f"""Dear {buyer['full_name']},

Your property purchase agreement for {property['full_address']} is attached.

Important Information:
- Your PAN card number ({buyer['pan_number']}) is the password to open this PDF
- Transaction ID: {property['property_id']}
- Property NFT Contract: {property['nft_contract']}

This PDF is encrypted for your security. Please keep it confidential.

Thank you for using Blockeste!
""",
        pdf_buffer=pdf_buffer,
        filename=f"Blockeste_Agreement_{property['property_id']}.pdf"
    )
    
    # Send to seller
    send_email(
        smtp_server, smtp_port, smtp_username, smtp_password,
        recipient=seller['email'],
        subject="Copy of Property Ownership Transfer Agreement",
        body=f"""Dear {seller['full_name']},

A copy of the property transfer agreement for {property['full_address']} is attached.

Important Information:
- Your PAN card number ({seller['pan_number']}) is the password to open this PDF
- Buyer: {buyer['full_name']}
- Transaction ID: {property['property_id']}
- Sale Price: {property['price']} ETH

This PDF is encrypted for your security. Please keep it confidential.

Thank you,
Blockeste Team
""",
        pdf_buffer=pdf_buffer,
        filename=f"Blockeste_Agreement_{property['property_id']}.pdf"
    )

def send_email(smtp_server, port, username, password, recipient, subject, body, pdf_buffer, filename):
    """Send email with PDF attachment"""
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    pdf_buffer.seek(0)
    part = MIMEApplication(pdf_buffer.read(), Name=filename)
    part['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(part)
    
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)

# Data access functions (replace with your actual implementations)
def get_user_details(user_name):
    # Replace with your actual implementation
    user_data="select * from kyc_verify where full_name=%s"%(user_name)
    user_data=select(user_data)
    user_id="select * from register where user_id=%s"%(user_data[0]['user_id'])
    user_id=select(user_id)
    return {
        'full_name': user_name,
        'email': user_id[0]['email'],
        'pan_number': user_data[0]['gov_id_number'],
        'wallet_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
        'signature_image':user_data[0]['signature_path']
    }

def get_seller_details(property_id):
    # Replace with your actual implementation
    seller_data="select s_id from property_reg where p_id=%s"%(property_id)
    seller_data=select(seller_data)
    user_data="select * from kyc_verify where full_name=%s"%(seller_data[0]['user_id'])
    user_data=select(user_data)
    seller="select * from register where user_id=%s"%(seller_data[0]['user_id'])
    seller=select(seller)
    name="select full_name,gov_id_number from kyc_verify where user_id=%s"%(seller_data[0]['user_id'])
    return {
        'full_name': seller[0][''],
        'email': seller[0]['email'],
        'pan_number': name[0]['gov_id_number'],
        'wallet_address': '0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B',
        'signature_image':user_data[0]['signature_path']
    }

def get_property_details(property_id):
    property="select * from property_reg where p_id=%s"%(property_id)
    property_details=select(property)
    return {
        'property_id': property_id,
        'full_address': property_details[0]['p_address'] ,
        'token_id': 'BLK-2023-0425',
        'nft_contract': '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359',
        'contract_address': '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359',
        'price': 45
    }

def get_transaction_details(user_id, property_id):
    return {
        'tx_hash': '0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b',
        'block_number': 17582000,
        'date': '2023-10-15 14:30:22'
    }


if __name__ == "__main__":
    app.run(debug=True)