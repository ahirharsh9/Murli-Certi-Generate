import streamlit as st
import io
import datetime
import requests
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER

# ---------------- CONFIGURATION ----------------
# ✅ Google Drive Image IDs
LOGO_ID = "1BGvxglcgZ2G6FdVelLjXZVo-_v4e4a42"
SIGNATURE_ID = "1U0es4MVJgGniK27rcrA6hiLFFRazmwCs"

# ✅ ALL 15 CHARACTER IMAGE IDs (Staff & Subjects)
CHAR_IDS = {
    # Staff / Roles
    "KRISHNA": "17M893cNMFHJMTAdI7q63Rco-IPfbPzDV",       # Mentor
    "VASHISHTHA": "1zGIr0w-bDKniX_YixYLbWRTvjgQMngFc",    # Expert Teacher
    "HANUMAN": "1mjModpBJPt6z5_oOWSAFNAbHVKfh92OO",       # Motivator
    "VISHWAKARMA": "1qeVY4aCjgrNgw-3JoEDbOkYsCKJUlk5N",   # Management
    "BHISHMA": "19tjccM9X2TGseoqwdLx8r_v0r124RLl_",       # Loyal Staff
    "SARASWATI": "1yP0MDaBa1nyBnqSbOiYF9YfbY3NZjOfU",     # Anchor
    "KEVAT": "1TACSn2dkT2CvsEeDzjklrOJ-WxLufcKa",         # Supporter
    
    # Subject Experts
    "VED_VYAS": "1CZu-SqL5_HsjMDXT9RI791koQua7WBCB",      # History
    "VARAHAMIHIRA": "1K9_yjGTTFt_bEvm2UE3lNBiy5kKLjF6M",  # Geography
    "HEMCHANDRACHARYA": "18rAhMPr8YEOiC8IE5NkOnuQaDMtlMg4W", # Literature
    "VIVEKANANDA": "1NmPraE54Y2uX3DSUC4UGijqU9PxbjEVH",   # Global/Current
    "ARYABHATA": "1oK6X51bZuTJZTbx7IGjqkQ54SB835fSM",     # Maths
    "GAUTAMA": "1kj-_eSd2ZXDjxY5xY60od5n8yPraWvg2",       # Reasoning
    "KANADA": "1hWsU_f7kUUacD0xBuYwhu8da2qU00FhI",        # Science
    "VIDUR": "1WVpPjHz8Ic9-WXfoXTAzg8L1eML81SUG"          # Law/Niti
}

# 🎨 THEME COLORS (Keeping it Royal but simple)
COLOR_BLUE_HEADER = colors.HexColor("#0f5f9a")
COLOR_AWARD_TITLE = colors.HexColor("#8B0000") # Dark Red
COLOR_GOLD = colors.HexColor("#B8860B")

# ==========================================
# 🎛️ ORIGINAL LAYOUT CONFIGURATION (Restored)
# ==========================================

# 1. LOGO SETTINGS (Left Side)
CERT_LOGO_WIDTH = 42 * mm        
CERT_LOGO_HEIGHT = 42 * mm       
CERT_LOGO_X_POS = 36 * mm        
CERT_LOGO_Y_POS = 143 * mm       

# 2. SIGNATURE SETTINGS (Bottom Right)
CERT_SIGN_WIDTH = 65 * mm        
CERT_SIGN_HEIGHT = 22 * mm       
CERT_SIGN_X_POS = 235 * mm       
CERT_SIGN_Y_POS = 38 * mm        

# 3. CHARACTER IMAGE SETTINGS (Right Side - Background)
CERT_CHAR_WIDTH = 74 * mm        
CERT_CHAR_HEIGHT = 74 * mm       
CERT_CHAR_OPACITY = 1.0  # Full Opacity

# Margins
CERT_CHAR_MARGIN_RIGHT = 16 * mm    
CERT_CHAR_MARGIN_TOP = 24 * mm      

PAGE_W_MM = 297 
PAGE_H_MM = 210 
CERT_CHAR_X_POS = (PAGE_W_MM * mm) - CERT_CHAR_WIDTH - CERT_CHAR_MARGIN_RIGHT
CERT_CHAR_Y_POS = (PAGE_H_MM * mm) - CERT_CHAR_HEIGHT - CERT_CHAR_MARGIN_TOP

# ---------------- HELPER FUNCTIONS ----------------
def get_drive_url(file_id):
    return f'https://drive.google.com/uc?export=download&id={file_id}'

@st.cache_data(show_spinner=False)
def download_image_from_drive(file_id):
    try:
        url = get_drive_url(file_id)
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except:
        pass
    return None

def get_transparent_image_reader(img_bytes, opacity=1.0):
    if not img_bytes: return None
    try:
        img_bytes.seek(0)
        img = Image.open(img_bytes).convert("RGBA")
        new_buffer = io.BytesIO()
        img.save(new_buffer, format='PNG')
        new_buffer.seek(0)
        return ImageReader(new_buffer)
    except:
        return None

# ---------------- CERTIFICATE GENERATOR ----------------
def generate_certificate(data, logo_bytes, sign_bytes, char_images_bytes):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    center_x = width / 2

    # --- 1. BORDER (Simple Line Border) ---
    c.setStrokeColor(COLOR_BLUE_HEADER)
    c.setLineWidth(5); c.rect(15*mm, 15*mm, width-30*mm, height-30*mm)
    c.setLineWidth(1); c.rect(18*mm, 18*mm, width-36*mm, height-36*mm)

    # --- 2. LOGO (Original Position) ---
    if logo_bytes:
        logo_img = ImageReader(Image.open(logo_bytes))
        c.drawImage(logo_img, CERT_LOGO_X_POS, CERT_LOGO_Y_POS, width=CERT_LOGO_WIDTH, height=CERT_LOGO_HEIGHT, mask='auto', preserveAspectRatio=True)

    # --- 3. CHARACTER IMAGE (Original Position) ---
    char_key = data.get('char_key')
    if char_key and char_key in char_images_bytes and char_images_bytes[char_key]:
        char_img = get_transparent_image_reader(char_images_bytes[char_key])
        if char_img:
            c.drawImage(char_img, CERT_CHAR_X_POS, CERT_CHAR_Y_POS, width=CERT_CHAR_WIDTH, height=CERT_CHAR_HEIGHT, mask='auto', preserveAspectRatio=True)

    # --- 4. HEADER TEXT ---
    c.setFont("Helvetica-Bold", 32); c.setFillColor(COLOR_BLUE_HEADER)
    c.drawCentredString(center_x, height - 52*mm, "MURLIDHAR ACADEMY")
    
    c.setFont("Helvetica", 12); c.setFillColor(colors.black)
    c.drawCentredString(center_x, height - 60*mm, "JUNAGADH")

    c.setFont("Helvetica-Oblique", 18); c.setFillColor(colors.black)
    c.drawCentredString(center_x, height - 75*mm, "Certificate of Achievement")

    c.setFont("Helvetica", 12); c.setFillColor(colors.gray)
    c.drawCentredString(center_x, height - 85*mm, "This is proudly presented to")

    # --- 5. RECIPIENT NAME ---
    c.setFont("Helvetica-Bold", 32); c.setFillColor(COLOR_BLUE_HEADER)
    c.drawCentredString(center_x, height - 100*mm, data['recipient_name'].upper())
    
    # Line under name
    c.setStrokeColor(colors.black); c.setLineWidth(0.5)
    c.line(center_x - 60*mm, height - 103*mm, center_x + 60*mm, height - 103*mm)

    # --- 6. AWARD TITLE ---
    c.setFont("Times-Bold", 28); c.setFillColor(COLOR_AWARD_TITLE)
    c.drawCentredString(center_x, height - 120*mm, data['award_title'])

    # --- 7. DESCRIPTION ---
    style = ParagraphStyle('Desc', parent=getSampleStyleSheet()['Normal'], fontName='Helvetica', fontSize=13, leading=16, alignment=TA_CENTER, textColor=colors.darkgray)
    p = Paragraph(data['award_desc'], style)
    w, h = p.wrap(width - 60*mm, 50*mm)
    p.drawOn(c, (width - w)/2, height - 145*mm)

    # --- 8. DATE & SIGNATURE (Original Position) ---
    c.setFont("Helvetica-Bold", 12); c.setFillColor(colors.black)
    c.drawString(30*mm, 35*mm, f"Date: {data['date']}")
    
    if sign_bytes:
        img_x = CERT_SIGN_X_POS - (CERT_SIGN_WIDTH / 2)
        sign_img = ImageReader(Image.open(sign_bytes))
        c.drawImage(sign_img, img_x, CERT_SIGN_Y_POS, width=CERT_SIGN_WIDTH, height=CERT_SIGN_HEIGHT, mask='auto', preserveAspectRatio=True)

    line_width = 50*mm
    line_start_x = CERT_SIGN_X_POS - (line_width / 2)
    line_end_x = CERT_SIGN_X_POS + (line_width / 2)
    line_y = 35*mm
    
    c.setLineWidth(1); c.setStrokeColor(colors.black)
    c.line(line_start_x, line_y, line_end_x, line_y)
    c.drawCentredString(CERT_SIGN_X_POS, 29*mm, "Director Signature")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Murlidhar Awards", page_icon="🎓", layout="centered")
st.title("🎓 Murlidhar Academy Awards")
st.caption("Generate Certificates for Staff & Experts")

# Load Assets
if 'logo_data' not in st.session_state: st.session_state['logo_data'] = download_image_from_drive(LOGO_ID)
if 'sign_data' not in st.session_state: st.session_state['sign_data'] = download_image_from_drive(SIGNATURE_ID)
if 'char_images' not in st.session_state:
    st.session_state['char_images'] = {}
    with st.spinner("Loading Images..."):
        for name, file_id in CHAR_IDS.items():
            img_data = download_image_from_drive(file_id)
            if img_data: st.session_state['char_images'][name] = img_data

# --- UI INPUTS ---
with st.container():
    col1, col2 = st.columns([2, 1])
    recipient_name = col1.text_input("Name (Recipient)", "Mr. Rahul Sir")
    cert_date = col2.text_input("Date", datetime.date.today().strftime('%d-%m-%Y'))

    # Award Categories
    CATEGORY_MAP = {
        "--- STAFF & ROLES ---": None,
        "Krishna Sarthi (Best Mentor)": "KRISHNA",
        "Vashishtha Guru (Subject Expert)": "VASHISHTHA",
        "Hanuman Sanjeevani (Motivator)": "HANUMAN",
        "Vishwakarma Nirman (Management)": "VISHWAKARMA",
        "Bhishma Stambh (Loyal Staff)": "BHISHMA",
        "Saraswati Vagdhara (Best Anchor)": "SARASWATI",
        "Kevat Sahyog (Best Supporter)": "KEVAT",
        "--- SUBJECT EXPERTS ---": None,
        "Ved Vyas (History Expert)": "VED_VYAS",
        "Varahamihira (Geography Expert)": "VARAHAMIHIRA",
        "Hemchandracharya (Literature Expert)": "HEMCHANDRACHARYA",
        "Vivekananda (Current Affairs/Global)": "VIVEKANANDA",
        "Aryabhata (Maths Expert)": "ARYABHATA",
        "Gautama Tark (Reasoning Expert)": "GAUTAMA",
        "Kanada Vignan (Science Expert)": "KANADA",
        "Vidur Niti (Law/Constitution)": "VIDUR"
    }
    
    award_selection = st.selectbox("Select Award Category", list(CATEGORY_MAP.keys()))

    # Logic to get details
    selected_key = CATEGORY_MAP.get(award_selection)
    
    award_title = ""
    award_desc = ""

    if selected_key:
        if selected_key == "KRISHNA":
            award_title = "THE KRISHNA SARTHI AWARD"
            award_desc = "Like Lord Krishna guided Arjuna to victory, you have been the guiding light for our students. This award honors your exceptional mentorship and direction."
        elif selected_key == "VASHISHTHA":
            award_title = "THE VASHISHTHA GURU AWARD"
            award_desc = "Just as Guru Vashishtha molded Lord Ram, your deep knowledge and teaching skills have shaped the future of our students. We honor your wisdom as a Subject Expert."
        elif selected_key == "HANUMAN":
            award_title = "THE HANUMAN SANJEEVANI AWARD"
            award_desc = "Whenever a challenge arose, you brought the 'Sanjeevani' of hope and solutions. This award celebrates your 'Can Do' attitude and selfless motivation."
        elif selected_key == "VISHWAKARMA":
            award_title = "THE VISHWAKARMA NIRMAN AWARD"
            award_desc = "The architect of our success! For your outstanding contribution in Management, Planning, and creating the best materials for the Academy."
        elif selected_key == "BHISHMA":
            award_title = "THE BHISHMA STAMBH AWARD"
            award_desc = "Standing tall like Bhishma Pitamah, you are the pillar of Murlidhar Academy. This award honors your unwavering Loyalty and years of dedication."
        elif selected_key == "SARASWATI":
            award_title = "THE SARASWATI VAGDHARA AWARD"
            award_desc = "Blessed by Goddess Saraswati, your speech and anchoring mesmerized everyone. This award honors your eloquence and command over the stage."
        elif selected_key == "KEVAT":
            award_title = "THE KEVAT SAHYOG AWARD"
            award_desc = "Like Kevat helped Lord Ram cross the river, your selfless support has helped this Academy move forward. We are grateful for your service."
        elif selected_key == "VED_VYAS":
            award_title = "THE VED VYAS ITIHAS AWARD"
            award_desc = "Like Maharshi Ved Vyas penned the vast history of Mahabharata, your knowledge of History is profound. Honoring the Best History Teacher."
        elif selected_key == "VARAHAMIHIRA":
            award_title = "THE VARAHAMIHIRA BHUGOL AWARD"
            award_desc = "Varahamihira unlocked the secrets of Earth and Space. Your mastery over Geography is equally deep. Honoring the Best Geography Teacher."
        elif selected_key == "HEMCHANDRACHARYA":
            award_title = "THE HEMCHANDRACHARYA SAHITYA AWARD"
            award_desc = "Like the 'Kalikalsarvajna' Hemchandracharya immortalized language, your command over Literature and Grammar is exemplary."
        elif selected_key == "VIVEKANANDA":
            award_title = "THE VIVEKANANDA GLOBAL AWARD"
            award_desc = "Swami Vivekananda enlightened the world with wisdom. Your knowledge of Current Affairs and General Knowledge is equally brilliant."
        elif selected_key == "ARYABHATA":
            award_title = "THE ARYABHATA GANIT AWARD"
            award_desc = "Aryabhata gave the world the Zero and new mathematics. Your logic and problem-solving skills in Maths are truly unique."
        elif selected_key == "GAUTAMA":
            award_title = "THE GAUTAMA TARK AWARD"
            award_desc = "Maharshi Gautama founded the Nyaya Sutras (Logic). Your Reasoning skills and sharp intellect are commendable. Honoring the Reasoning Expert."
        elif selected_key == "KANADA":
            award_title = "THE KANADA VIGNAN AWARD"
            award_desc = "Like Maharshi Kanada, the pioneer of atomic theory, your scientific temper and understanding of Science are outstanding."
        elif selected_key == "VIDUR":
            award_title = "THE VIDUR NITI AWARD"
            award_desc = "Mahatma Vidur was known for his ethics and policy. Your understanding of Law, Constitution, and Ethics is highly respected."

    final_desc = st.text_area("Award Description", award_desc, height=100)

    if st.button("📄 Generate Certificate", type="primary"):
        if not recipient_name or not selected_key:
            st.error("Please enter a name and select a valid award category.")
        else:
            data = {
                "recipient_name": recipient_name,
                "award_title": award_title,
                "award_desc": final_desc,
                "date": cert_date,
                "char_key": selected_key
            }
            
            pdf_bytes = generate_certificate(
                data, 
                st.session_state['logo_data'], 
                st.session_state['sign_data'], 
                st.session_state['char_images']
            )
            
            fname = f"Certificate_{recipient_name.replace(' ','_')}.pdf"
            st.success(f"Certificate Created for {recipient_name}!")
            st.download_button("📥 Download PDF", pdf_bytes, file_name=fname, mime="application/pdf")
