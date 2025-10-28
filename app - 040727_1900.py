import streamlit as st
from google import genai
from google.genai import types
#import fitz  # PyMuPDF
import re
from datetime import datetime
import chromadb
import os

# تنظیمات صفحه
st.set_page_config(
    page_title="سامانه استعلامات حقوقی",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل CSS کامل با راست‌چینی
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        background: linear-gradient(120deg, #2c3e50, #3498db);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        animation: fadeIn 0.8s ease-in;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        letter-spacing: 1px;
    }
    
    .main-header p {
        font-size: 1.3rem;
        margin-top: 1rem;
        font-weight: 400;
        opacity: 0.95;
    }
    
    .card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        direction: rtl;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .card h2 {
        color: #2c3e50;
        font-weight: 700;
        font-size: 2rem;
        margin-bottom: 1.5rem;
        text-align: right;
        border-right: 5px solid #3498db;
        padding-right: 15px;
    }
    
    .info-box {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: right;
        font-size: 1.1rem;
        line-height: 1.8;
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
    }
    
    .info-box h4 {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: right;
    }
    
    .info-box ul {
        list-style: none;
        padding-right: 0;
        margin: 0;
    }
    
    .info-box li {
        padding: 0.5rem 0;
        padding-right: 1.5rem;
        position: relative;
    }
    
    .info-box li:before {
        content: "✓";
        position: absolute;
        right: 0;
        color: #2ecc71;
        font-weight: bold;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f39c12, #e67e22);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: right;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(243, 156, 18, 0.3);
    }
    
    .question-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        animation: slideIn 0.5s ease-out;
    }
    
    .question-card h4 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: right;
    }
    
    .question-card p {
        font-size: 1.2rem;
        line-height: 1.8;
        text-align: right;
    }
    
    .answer-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 20px rgba(240, 147, 251, 0.4);
        animation: slideIn 0.5s ease-out 0.2s both;
    }
    
    .answer-card h4 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: right;
    }
    
    .answer-card p {
        font-size: 1.1rem;
        line-height: 2;
        text-align: right;
        white-space: pre-wrap;
    }
    
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 8px 20px rgba(17, 153, 142, 0.4);
        animation: bounceIn 0.6s ease-out;
    }
    
    .success-box h3 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .success-box p {
        font-size: 1.3rem;
        margin: 0;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2.5rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        direction: rtl;
        text-align: right;
        font-family: 'Vazirmatn', sans-serif;
        font-size: 1.1rem;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: border 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
    }
    
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(240, 147, 251, 0.4);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .stat-number {
        font-size: 3.5rem;
        font-weight: 800;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1.2rem;
        font-weight: 500;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 1rem;
        color: #7f8c8d;
        line-height: 1.6;
    }
    
    /* انیمیشن‌ها */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* راست‌چینی اجباری */
    .element-container, .stMarkdown, p, h1, h2, h3, h4, h5, h6, div, span {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* راست‌چینی تب‌ها */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        direction: rtl;
    }
    
    .stTabs [data-baseweb="tab"] {
        direction: rtl;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* راست‌چینی expander */
    .streamlit-expanderHeader {
        direction: rtl;
        text-align: right;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* راست‌چینی sidebar */
    .css-1d391kg, .css-1lcbmhc, [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    .css-1d391kg p, .css-1lcbmhc p {
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# دیتابیس
class LegalDatabase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./legal_db")
        try:
            self.collection = self.client.get_collection("legal_inquiries")
        except:
            self.collection = self.client.create_collection(name="legal_inquiries")
    
    def add_document(self, doc_data):
        doc_id = f"{doc_data['شماره_نامه']}_{doc_data['تاریخ']}".replace('/', '_').replace(' ', '_')
        full_text = f"""
شماره نامه: {doc_data['شماره_نامه']}
تاریخ: {doc_data['تاریخ']}
شماره پرونده: {doc_data['شماره_پرونده']}
استعلام: {doc_data['استعلام']}
پاسخ: {doc_data['پاسخ']}
"""
        try:
            self.collection.upsert(documents=[full_text], metadatas=[doc_data], ids=[doc_id])
            return True
        except:
            return False
    
    def search(self, query, n_results=5):
        try:
            count = self.collection.count()
            if count == 0:
                return {'documents': [[]], 'metadatas': [[]]}
            return self.collection.query(query_texts=[query], n_results=min(n_results, count))
        except:
            return {'documents': [[]], 'metadatas': [[]]}
    
    def get_all_count(self):
        try:
            return self.collection.count()
        except:
            return 0

# پارسر PDF
class PDFExtractor:
    @staticmethod
    def extract_text_from_pdf(pdf_file):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    
    @staticmethod
    def parse_simple(text):
        """پارسر ساده"""
        documents = []
        
        signature_patterns = [
            'دکتر احمد محمدی باردئی',
            'دكتر احمد محمدي باردئي'
        ]
        
        parts = [text]
        for pattern in signature_patterns:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(pattern))
            parts = new_parts
        
        st.info(f"🔍 تعداد بخش‌های پیدا شده: {len(parts)} بخش")
        
        for idx, part in enumerate(parts):
            if len(part.strip()) < 100:
                continue
            
            try:
                date_matches = re.findall(r'\d{4}/\d{1,2}/\d{1,2}', part)
                if not date_matches:
                    continue
                date = date_matches[0]
                
                number_matches = re.findall(r'\d+/\d+/\d+', part)
                if len(number_matches) < 1:
                    continue
                number = number_matches[0] if number_matches[0] != date else (number_matches[1] if len(number_matches) > 1 else number_matches[0])
                
                case_match = re.search(r'شماره پرونده\s*:?\s*([^\n]+)', part)
                case_number = case_match.group(1).strip() if case_match else "نامشخص"
                
                inquiry_match = re.search(r'استعلام\s*:?\s*(.*?)\s*(?:پاسخ|ﭘاسﺦ)', part, re.DOTALL | re.IGNORECASE)
                inquiry = inquiry_match.group(1).strip() if inquiry_match else ""
                
                answer_match = re.search(r'(?:پاسخ|ﭘاسﺦ)\s*:?\s*(.*)', part, re.DOTALL | re.IGNORECASE)
                answer = answer_match.group(1).strip() if answer_match else ""
                
                inquiry = re.sub(r'\s+', ' ', inquiry).strip()
                answer = re.sub(r'\s+', ' ', answer).strip()
                
                if len(inquiry) < 20 or len(answer) < 20:
                    continue
                
                doc = {
                    'تاریخ': date,
                    'شماره_نامه': number,
                    'شماره_پرونده': case_number,
                    'استعلام': inquiry[:2000],
                    'پاسخ': answer[:3000],
                    'پاسخ_دهنده': 'دکتر احمد محمدی باردئی'
                }
                
                documents.append(doc)
                st.success(f"✅ سند {idx+1} با موفقیت پردازش شد - تاریخ: {date} - شماره: {number}")
                
            except Exception as e:
                continue
        
        return documents

# RAG
class LegalRAG:
    def __init__(self, api_key):
        self.api_key = api_key
        self.db = LegalDatabase()
        self.client = genai.Client(api_key=api_key)
        
        self.models = [
            "gemini-2.5-pro",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]
    
    def test_api_key(self):
        """تست API Key"""
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text="سلام، یک عدد تصادفی بگو")],
                )
            ]
            
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=contents,
            )
            
            if response.text:
                return True, f"✅ کلید API معتبر است و به درستی کار می‌کند!\n\n🤖 مدل آزمایش شده: gemini-1.5-flash\n📝 پاسخ نمونه: {response.text[:100]}..."
            else:
                return False, "❌ پاسخ خالی دریافت شد"
                
        except Exception as e:
            error_msg = str(e)
            
            if "403" in error_msg or "invalid" in error_msg.lower():
                return False, """
❌ کلید API نامعتبر است یا غیرفعال شده

**راه‌حل:**
1. به آدرس https://aistudio.google.com/apikey مراجعه کنید
2. یک کلید API جدید ایجاد کنید
3. کلید را کامل کپی کنید (بدون فاصله اضافی)
4. در کادر بالا وارد کنید
"""
            elif "429" in error_msg:
                return False, "❌ تعداد درخواست‌ها زیاد است. لطفاً 1 دقیقه صبر کنید"
            else:
                return False, f"❌ خطا: {error_msg}"
    
    def generate_answer(self, question):
        """تولید پاسخ"""
        search_results = self.db.search(question, n_results=3)
        
        if not search_results['documents'][0]:
            return "⚠️ اطلاعاتی در پایگاه داده یافت نشد. لطفاً ابتدا اسناد حقوقی را بارگذاری کنید."
        
        context = ""
        sources = []
        for i, doc in enumerate(search_results['documents'][0]):
            metadata = search_results['metadatas'][0][i]
            sources.append(f"📌 سند {i+1}: شماره نامه {metadata.get('شماره_نامه')} - تاریخ {metadata.get('تاریخ')}")
            context += f"\n\n📄 سند شماره {i+1}:\n"
            context += f"🔢 شماره نامه: {metadata.get('شماره_نامه')}\n"
            context += f"📅 تاریخ: {metadata.get('تاریخ')}\n"
            context += f"📁 شماره پرونده: {metadata.get('شماره_پرونده')}\n"
            context += f"❓ استعلام: {metadata.get('استعلام', '')[:400]}\n"
            context += f"💡 پاسخ: {metadata.get('پاسخ', '')[:800]}\n"
        
        prompt = f"""شما یک دستیار حقوقی متخصص هستید که بر اساس نظرات مشورتی اداره کل حقوقی قوه قضاییه جمهوری اسلامی ایران به سوالات حقوقی پاسخ می‌دهید.

📚 اطلاعات مرتبط استخراج شده از پایگاه داده:
{context}

❓ سوال کاربر:
{question}

💡 دستورالعمل پاسخ‌دهی:
1. پاسخ را به زبان فارسی روان و قابل فهم بنویسید
2. از اطلاعات موجود در اسناد بالا استفاده کنید
3. شماره نامه و تاریخ اسناد مرتبط را حتماً ذکر کنید
4. در صورت لزوم، ماده قانونی مرتبط را نیز بیان کنید
5. پاسخ باید ساختارمند، دقیق و کامل باشد

پاسخ:
"""
        
        for model_name in self.models:
            try:
                st.info(f"🤖 در حال استفاده از مدل: {model_name}")
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    )
                ]
                
                config = types.GenerateContentConfig(
                    temperature=0.4,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048,
                )
                
                answer_text = ""
                for chunk in self.client.models.generate_content_stream(
                    model=model_name,
                    contents=contents,
                    config=config,
                ):
                    if chunk.text:
                        answer_text += chunk.text
                
                if answer_text:
                    final_answer = answer_text + f"\n\n{'─' * 50}\n\n📚 **منابع و مستندات:**\n" + "\n".join(sources)
                    return final_answer
                
            except Exception as e:
                error_msg = str(e)
                st.warning(f"⚠️ خطا در مدل {model_name}: {error_msg[:80]}...")
                continue
        
        return f"""
❌ متأسفانه نتوانستم با سرویس هوش مصنوعی ارتباط برقرار کنم.

**اطلاعات یافت شده در پایگاه داده:**
{context}

{'─' * 50}

📚 **منابع:**
{chr(10).join(sources)}

💡 **پیشنهاد:** لطفاً کلید API خود را بررسی کرده یا چند دقیقه دیگر مجدداً امتحان کنید.
"""

# برنامه اصلی
def main():
    # هدر اصلی
    st.markdown('''
    <div class="main-header">
        <h1>⚖️ سامانه هوشمند استعلامات حقوقی</h1>
        <p>🤖 مدیریت و جستجوی نظرات مشورتی قوه قضاییه با قدرت هوش مصنوعی Gemini</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # سایدبار
    with st.sidebar:
        st.markdown("### ⚙️ تنظیمات سامانه")
        
        st.markdown('''
        <div class="info-box">
            <h4>🔑 کلید API</h4>
            <p>برای استفاده از سامانه، کلید API خود را وارد کنید</p>
        </div>
        ''', unsafe_allow_html=True)
        
        api_key = st.text_input(
            "کلید API Gemini را وارد کنید:",
            type="password",
            help="از https://aistudio.google.com/apikey دریافت کنید",
            placeholder="کلید API خود را اینجا وارد کنید..."
        )
        
        if api_key:
            st.session_state['api_key'] = api_key
            
            if st.button("🧪 تست اعتبار کلید API", use_container_width=True):
                with st.spinner("در حال بررسی اعتبار کلید..."):
                    rag = LegalRAG(api_key)
                    success, message = rag.test_api_key()
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        st.markdown("---")
        
        # نمایش آمار
        if 'db' in st.session_state:
            count = st.session_state['db'].get_all_count()
            st.markdown(f'''
            <div class="stat-card">
                <span class="stat-number">{count}</span>
                <span class="stat-label">سند حقوقی در پایگاه داده</span>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # راهنمای استفاده
        st.markdown('''
        <div class="info-box">
            <h4>📖 راهنمای استفاده</h4>
            <ul>
                <li>ابتدا کلید API را دریافت و وارد کنید</li>
                <li>فایل PDF نظرات مشورتی را بارگذاری کنید</li>
                <li>سوالات خود را از سامانه بپرسید</li>
                <li>پاسخ‌های دقیق و مستند دریافت کنید</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="warning-box">
            <h4>⚠️ نکات مهم</h4>
            <p>• کلید API را از Google AI Studio دریافت کنید</p>
            <p>• فایل PDF باید شامل نظرات مشورتی باشد</p>
            <p>• برای نتایج بهتر از سوالات دقیق استفاده کنید</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # تب‌های اصلی
    tab1, tab2, tab3 = st.tabs([
        "📤 بارگذاری اسناد حقوقی",
        "💬 پرسش و پاسخ هوشمند",
        "📊 مشاهده اسناد ذخیره شده"
    ])
    
    # تب 1: بارگذاری
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 📤 بارگذاری فایل PDF نظرات مشورتی")
        
        st.markdown('''
        <div class="info-box">
            <h4>📋 توضیحات</h4>
            <p>در این بخش می‌توانید فایل PDF حاوی نظرات مشورتی اداره کل حقوقی قوه قضاییه را بارگذاری کنید. سامانه به صورت خودکار اطلاعات را استخراج و در پایگاه داده ذخیره می‌کند.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📁 فایل PDF خود را انتخاب کنید:",
            type=['pdf'],
            help="فایل باید شامل نظرات مشورتی با فرمت استاندارد باشد"
        )
        
        if uploaded_file:
            st.markdown(f'''
            <div class="info-box">
                <p>📄 <strong>نام فایل:</strong> {uploaded_file.name}</p>
                <p>📏 <strong>حجم فایل:</strong> {uploaded_file.size / 1024:.1f} کیلوبایت</p>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button("🚀 شروع پردازش و استخراج اطلاعات", use_container_width=True):
                with st.spinner('⏳ در حال پردازش فایل و استخراج اطلاعات...'):
                    try:
                                      
                        extractor = PDFExtractor()
                        uploaded_file.seek(0)
                        text = extractor.extract_text_from_pdf(uploaded_file)
                        
                        st.success(f"✅ متن فایل با موفقیت استخراج شد - تعداد کاراکترها: {len(text):,}")
                        
                        st.markdown("### 🔄 در حال تجزیه و تحلیل اسناد...")
                        documents = extractor.parse_simple(text)
                        
                        if documents:
                            if 'db' not in st.session_state:
                                st.session_state['db'] = LegalDatabase()
                            
                            db = st.session_state['db']
                            success = 0
                            progress = st.progress(0)
                            status_text = st.empty()
                            
                            for i, doc in enumerate(documents):
                                if db.add_document(doc):
                                    success += 1
                                progress.progress((i + 1) / len(documents))
                                status_text.text(f"در حال ذخیره سند {i+1} از {len(documents)}...")
                            
                            st.markdown(f'''
                            <div class="success-box">
                                <h3>✅ عملیات با موفقیت انجام شد!</h3>
                                <p>🎉 تعداد {success} سند حقوقی با موفقیت در پایگاه داده ذخیره شد</p>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            with st.expander("📋 مشاهده جزئیات اسناد استخراج شده"):
                                for i, doc in enumerate(documents[:5], 1):
                                    st.markdown(f"### 📄 سند شماره {i}")
                                    st.json(doc)
                                    st.markdown("---")
                                
                                if len(documents) > 5:
                                    st.info(f"ℹ️ تعداد {len(documents) - 5} سند دیگر نیز استخراج شده است")
                        else:
                            st.markdown('''
                            <div class="warning-box">
                                <h4>❌ هیچ سندی استخراج نشد</h4>
                                <p><strong>دلایل احتمالی:</strong></p>
                                <ul>
                                    <li>فایل PDF ممکن است اسکن شده باشد (نه متنی)</li>
                                    <li>فرمت فایل با الگوی مورد نظر مطابقت ندارد</li>
                                    <li>فایل خالی یا معیوب است</li>
                                </ul>
                                <p><strong>پیشنهاد:</strong> لطفاً از فایل PDF متنی با فرمت استاندارد استفاده کنید</p>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"❌ خطا در پردازش فایل: {str(e)}")
                        st.info("💡 لطفاً فایل دیگری را امتحان کنید یا با پشتیبانی تماس بگیرید")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # تب 2: پرسش و پاسخ
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 💬 پرسش و پاسخ هوشمند حقوقی")
        
        if 'api_key' not in st.session_state:
            st.markdown('''
            <div class="warning-box">
                <h4>⚠️ کلید API وارد نشده</h4>
                <p>لطفاً ابتدا کلید API Gemini خود را در سایدبار سمت راست وارد کنید.</p>
                <p><strong>نحوه دریافت کلید API:</strong></p>
                <ol style="text-align: right; padding-right: 20px;">
                    <li>به آدرس https://aistudio.google.com/apikey مراجعه کنید</li>
                    <li>با حساب Google خود وارد شوید</li>
                    <li>روی دکمه "Create API Key" کلیک کنید</li>
                    <li>کلید را کپی کرده و در کادر سایدبار وارد کنید</li>
                </ol>
            </div>
            ''', unsafe_allow_html=True)
            
        elif 'db' not in st.session_state or st.session_state['db'].get_all_count() == 0:
            st.markdown('''
            <div class="warning-box">
                <h4>⚠️ پایگاه داده خالی است</h4>
                <p>هنوز هیچ سند حقوقی در پایگاه داده بارگذاری نشده است.</p>
                <p>لطفاً ابتدا به تب "📤 بارگذاری اسناد حقوقی" بروید و فایل PDF نظرات مشورتی را بارگذاری کنید.</p>
            </div>
            ''', unsafe_allow_html=True)
            
        else:
            st.markdown('''
            <div class="info-box">
                <h4>💡 راهنمای استفاده</h4>
                <p>سوال حقوقی خود را در کادر زیر بنویسید یا از سوالات نمونه استفاده کنید. سامانه با استفاده از هوش مصنوعی و بر اساس اسناد موجود، پاسخ دقیق و مستند ارائه می‌دهد.</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # سوالات نمونه
            st.markdown("### 🎯 سوالات نمونه برای شروع:")
            st.markdown("می‌توانید روی هر یک از سوالات زیر کلیک کنید:")
            
            sample_questions = [
                "مسئولیت امضاکنندگان چک مشترک به چه صورت است؟",
                "شرایط و ضوابط اعطای مرخصی به محکومان چیست؟",
                "صلاحیت دادگاه صلح در چه مواردی است؟",
            ]
            
            cols = st.columns(3)
            for i, question in enumerate(sample_questions):
                with cols[i]:
                    if st.button(f"📌 {question}", key=f"sample_{i}", use_container_width=True):
                        st.session_state['current_question'] = question
            
            st.markdown("---")
            
            # کادر ورودی سوال
            question = st.text_area(
                "✍️ سوال حقوقی خود را اینجا بنویسید:",
                value=st.session_state.get('current_question', ''),
                height=120,
                placeholder="مثال: آیا دادگاه صلح می‌تواند اجراییه چک صادر کند؟",
                help="سوال خود را به صورت واضح و دقیق مطرح کنید"
            )
            
            if st.button("🔍 جستجو و دریافت پاسخ", type="primary", use_container_width=True):
                if question.strip():
                    with st.spinner('🤖 در حال پردازش سوال و جستجو در اسناد...'):
                        try:
                            rag = LegalRAG(st.session_state['api_key'])
                            answer = rag.generate_answer(question)
                            
                            st.markdown(f'''
                            <div class="question-card">
                                <h4>❓ سوال شما:</h4>
                                <p>{question}</p>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            st.markdown(f'''
                            <div class="answer-card">
                                <h4>💡 پاسخ سامانه:</h4>
                                <p>{answer}</p>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # ذخیره در تاریخچه
                            if 'history' not in st.session_state:
                                st.session_state['history'] = []
                            
                            st.session_state['history'].append({
                                'question': question,
                                'answer': answer,
                                'timestamp': datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
                            })
                            
                        except Exception as e:
                            st.error(f"❌ خطا در تولید پاسخ: {str(e)}")
                            st.info("💡 لطفاً کلید API خود را بررسی کنید یا چند لحظه دیگر مجدداً تلاش کنید")
                else:
                    st.warning("⚠️ لطفاً ابتدا سوال خود را وارد کنید")
            
            # نمایش تاریخچه
            if 'history' in st.session_state and st.session_state['history']:
                st.markdown("---")
                st.markdown("### 📜 تاریخچه سوالات اخیر")
                
                for i, item in enumerate(reversed(st.session_state['history'][-5:]), 1):
                    with st.expander(f"🕐 {item['timestamp']} - {item['question'][:60]}..."):
                        st.markdown(f"**❓ سوال:** {item['question']}")
                        st.markdown("---")
                        st.markdown(f"**💡 پاسخ:** {item['answer']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # تب 3: مشاهده اسناد
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("## 📊 اسناد ذخیره شده در پایگاه داده")
        
        if 'db' in st.session_state and st.session_state['db'].get_all_count() > 0:
            all_docs = st.session_state['db'].collection.get()
            
            if all_docs['ids']:
                total_docs = len(all_docs['ids'])
                st.markdown(f'''
                <div class="success-box">
                    <h3>✅ پایگاه داده فعال است</h3>
                    <p>📚 تعداد کل اسناد: {total_docs} سند حقوقی</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # جستجو در اسناد
                st.markdown("### 🔍 جستجو در اسناد")
                search_term = st.text_input(
                    "جستجو بر اساس شماره نامه، تاریخ یا کلمه کلیدی:",
                    placeholder="مثال: 1404 یا چک یا مهریه",
                    help="می‌توانید هر کلمه‌ای را جستجو کنید"
                )
                
                st.markdown("---")
                st.markdown("### 📄 لیست اسناد")
                
                displayed_count = 0
                for i, meta in enumerate(all_docs['metadatas'], 1):
                    if search_term and search_term.strip():
                        # جستجو در تمام فیلدهای سند
                        if not any(search_term in str(v) for v in meta.values()):
                            continue
                    
                    displayed_count += 1
                    
                    with st.expander(f"📄 سند {i} - شماره نامه: {meta.get('شماره_نامه', 'نامشخص')} - تاریخ: {meta.get('تاریخ', 'نامشخص')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**🔢 شماره نامه:** {meta.get('شماره_نامه', 'نامشخص')}")
                            st.markdown(f"**📅 تاریخ:** {meta.get('تاریخ', 'نامشخص')}")
                        
                        with col2:
                            st.markdown(f"**📁 شماره پرونده:** {meta.get('شماره_پرونده', 'نامشخص')}")
                            st.markdown(f"**✍️ پاسخ‌دهنده:** {meta.get('پاسخ_دهنده', 'نامشخص')}")
                        
                        st.markdown("---")
                        
                        st.markdown("**❓ استعلام:**")
                        st.info(meta.get('استعلام', 'اطلاعاتی موجود نیست')[:500] + "...")
                        
                        st.markdown("**💡 پاسخ:**")
                        st.success(meta.get('پاسخ', 'اطلاعاتی موجود نیست')[:500] + "...")
                
                if search_term and displayed_count == 0:
                    st.warning("⚠️ هیچ سندی با این عبارت جستجو پیدا نشد. لطفاً کلمه دیگری را امتحان کنید.")
                
                if displayed_count > 0:
                    st.info(f"ℹ️ تعداد {displayed_count} سند نمایش داده شد")
            else:
                st.markdown('''
                <div class="info-box">
                    <h4>📭 پایگاه داده خالی است</h4>
                    <p>هنوز هیچ سند حقوقی بارگذاری نشده است.</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="warning-box">
                <h4>⚠️ پایگاه داده ایجاد نشده</h4>
                <p>لطفاً ابتدا به تب "📤 بارگذاری اسناد حقوقی" بروید و فایل PDF را بارگذاری کنید.</p>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # فوتر
    st.markdown("---")
    st.markdown('''
    <div style="text-align: center; color: white; padding: 2rem; background: rgba(255,255,255,0.1); border-radius: 15px; margin-top: 2rem;">
        <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">
            <strong>⚖️ سامانه هوشمند استعلامات حقوقی</strong>
        </p>
        <p style="font-size: 1rem; opacity: 0.9;">
            ساخته شده با ❤️ برای قوه قضاییه جمهوری اسلامی ایران
        </p>
        <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
            🤖 نسخه 2.0 - با قدرت هوش مصنوعی Gemini
        </p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":

    main()
