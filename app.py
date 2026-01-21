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
# ✅ Google Drive Image IDs (System & Characters)
DEFAULT_DRIVE_ID = "1a1ZK5uiLl0a63Pto1EQDUY0VaIlqp21u" # Using this as fallback background if needed
LOGO_ID = "1BGvxglcgZ2G6FdVelLjXZVo-_v4e4a42"
SIGNATURE_ID = "1U0es4MVJgGniK27rcrA6hiLFFRazmwCs"

# ✅ NEW CHARACTER IMAGE IDs (Staff & Subjects)
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

# 🎨 ROYAL THEME COLORS
COLOR_ROYAL_BLUE = colors.HexColor("#002147") # Dark Royal Blue
COLOR_MAROON = colors.HexColor("#800000")     # Deep Maroon
COLOR_GOLD = colors.HexColor("#DAA520")       # GoldenRod
COLOR_TEXT_BLACK = colors.HexColor("#2C2C2C")

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
        if opacity < 1.0:
            r, g, b, alpha = img.split()
            alpha = alpha.point(lambda p: int(p * opacity))
            img.putalpha(alpha)
        new_buffer = io.BytesIO()
        img.save(new_buffer, format='PNG')
        new_buffer.seek(0)
        return ImageReader(new_buffer)
    except:
        return None

# ---------------- ROYAL CERTIFICATE GENERATOR ----------------
def generate_royal_certificate(data, logo_bytes, sign_bytes, char_images_bytes):
    buffer = io.BytesIO()
    # A4 Landscape
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    center_x = width / 2

    # --- 1. WATERMARK (Logo with low opacity) ---
    if logo_bytes:
        watermark = get_transparent_image_reader(logo_bytes, opacity=0.08)
        if watermark:
            wm_w, wm_h = 120*mm, 120*mm
            c.drawImage(watermark, (width-wm_w)/2, (height-wm_h)/2, width=wm_w, height=wm_h, mask='auto', preserveAspectRatio=True)

    # --- 2. ROYAL BORDER ---
    # Outer Maroon Border
    c.setStrokeColor(COLOR_MAROON)
    c.setLineWidth(4)
    c.rect(10*mm, 10*mm, width-20*mm, height-20*mm)
    
    # Inner Golden Border
    c.setStrokeColor(COLOR_GOLD)
    c.setLineWidth(2)
    c.rect(13*mm, 13*mm, width-26*mm, height-26*mm)

    # Decorative Corners (Simple circles for royal look)
    c.setFillColor(COLOR_GOLD)
    for x, y in [(10*mm, 10*mm), (width-10*mm, 10*mm), (10*mm, height-10*mm), (width-10*mm, height-10*mm)]:
        c.circle(x, y, 3*mm, fill=1, stroke=0)

    # --- 3. CHARACTER IMAGE (Right Side) ---
    char_key = data.get('char_key')
    if char_key and char_key in char_images_bytes and char_images_bytes[char_key]:
        char_img = get_transparent_image_reader(char_images_bytes[char_key], opacity=1.0)
        if char_img:
            # Position: Right side, slightly overlapping bottom
            CHAR_W, CHAR_H = 85*mm, 85*mm
            c.drawImage(char_img, width - CHAR_W - 20*mm, 20*mm, width=CHAR_W, height=CHAR_H, mask='auto', preserveAspectRatio=True)

    # --- 4. HEADER & SHLOKA ---
    # Logo (Top Left - Smaller & Formal)
    if logo_bytes:
        logo_img = ImageReader(Image.open(logo_bytes))
        c.drawImage(logo_img, 20*mm, height - 45*mm, width=30*mm, height=30*mm, mask='auto', preserveAspectRatio=True)

    # Sanskrit Shloka
    c.setFont("Times-BoldItalic", 12)
    c.setFillColor(COLOR_MAROON)
    c.drawCentredString(center_x, height - 25*mm, "|| સા વિદ્યા યા વિમુક્તયે ||")

    # Main Title
    c.setFont("Times-Bold", 36)
    c.setFillColor(COLOR_ROYAL_BLUE)
    c.drawCentredString(center_x, height - 40*mm, "MURLIDHAR ACADEMY")
    
    c.setFont("Times-Roman", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(center_x, height - 48*mm, "JUNAGADH")

    # Award Header
    c.setFont("Times-Italic", 20)
    c.setFillColor(colors.darkgray)
    c.drawCentredString(center_x, height - 65*mm, "Certificate of Honor & Appreciation")

    # Presented To Line
    c.setFont("Times-Roman", 14)
    c.setFillColor(colors.gray)
    c.drawCentredString(center_x, height - 80*mm, "This prestigious award is proudly presented to")

    # --- 5. RECIPIENT NAME ---
    c.setFont("Times-Bold", 32)
    c.setFillColor(COLOR_MAROON)
    c.drawCentredString(center_x, height - 95*mm, data['recipient_name'].upper())
    
    # Underline
    c.setLineWidth(1)
    c.setStrokeColor(COLOR_GOLD)
    c.line(center_x - 70*mm, height - 98*mm, center_x + 70*mm, height - 98*mm)

    # --- 6. AWARD TITLE & DESCRIPTION ---
    c.setFont("Times-Bold", 26)
    c.setFillColor(COLOR_ROYAL_BLUE)
    c.drawCentredString(center_x, height - 118*mm, data['award_title'])

    # Description Paragraph
    # Using 'Times-Roman' for description to look like a formal letter
    desc_style = ParagraphStyle('Desc', parent=getSampleStyleSheet()['Normal'], fontName='Times-Roman', fontSize=14, leading=18, alignment=TA_CENTER, textColor=colors.black)
    p = Paragraph(data['award_desc'], desc_style)
    w, h = p.wrap(width - 90*mm, 60*mm) # Reduced width to avoid hitting char image
    # Centering logic adjustment for paragraph
    p.drawOn(c, (width - w)/2 - 10*mm, height - 145*mm)

    # --- 7. DATE & SIGNATURE ---
    # Date (Left)
    c.setFont("Times-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(25*mm, 35*mm, f"Date: {data['date']}")
    c.drawString(25*mm, 30*mm, "Place: Junagadh")

    # Signature (Right Center - shifted left of image)
    SIGN_X = width - 80*mm 
    if sign_bytes:
        sign_img = ImageReader(Image.open(sign_bytes))
        c.drawImage(sign_img, SIGN_X - 30*mm, 35*mm, width=60*mm, height=20*mm, mask='auto', preserveAspectRatio=True)
    
    c.setLineWidth(1); c.setStrokeColor(colors.black)
    c.line(SIGN_X - 25*mm, 32*mm, SIGN_X + 25*mm, 32*mm)
    
    c.setFont("Times-Roman", 10)
    c.drawCentredString(SIGN_X, 27*mm, "With Gratitude,")
    c.setFont("Times-Bold", 12)
    c.drawCentredString(SIGN_X, 22*mm, "Director of Murlidhar Academy")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Royal Certificate Maker", page_icon="👑", layout="centered")
st.title("👑 Royal Award Generator")
st.caption("For Teachers, Staff, and Subject Experts of Murlidhar Academy")

# Load Assets
if 'logo_data' not in st.session_state: st.session_state['logo_data'] = download_image_from_drive(LOGO_ID)
if 'sign_data' not in st.session_state: st.session_state['sign_data'] = download_image_from_drive(SIGNATURE_ID)
if 'char_images' not in st.session_state:
    st.session_state['char_images'] = {}
    with st.spinner("Preparing Royal Gallery..."):
        for name, file_id in CHAR_IDS.items():
            img_data = download_image_from_drive(file_id)
            if img_data: st.session_state['char_images'][name] = img_data

# --- UI INPUTS ---
with st.container():
    col1, col2 = st.columns([2, 1])
    recipient_name = col1.text_input("Recipient Name (શિક્ષક/સ્ટાફનું નામ)", "Mr. Rahul Sir")
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
            
        # Subject Experts Descriptions
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

    # Editable Text Area in case user wants to change English to Gujarati manually
    final_desc = st.text_area("Award Description (You can edit or paste Gujarati here)", award_desc, height=100)

    # GENERATE BUTTON
    if st.button("⚜️ Generate Royal Certificate", type="primary"):
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
            
            pdf_bytes = generate_royal_certificate(
                data, 
                st.session_state['logo_data'], 
                st.session_state['sign_data'], 
                st.session_state['char_images']
            )
            
            fname = f"Royal_Award_{recipient_name.replace(' ','_')}.pdf"
            st.success(f"🎉 Certificate Created for {recipient_name}!")
            st.download_button("📥 Download PDF", pdf_bytes, file_name=fname, mime="application/pdf")
