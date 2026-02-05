import streamlit as st
import google.generativeai as genai
import PyPDF2

# Cấu hình trang
st.set_page_config(page_title="Trợ lý Học thuật AI", page_icon="✈️")
st.title("✈️ Trợ lý Nghiên cứu & Học thuật")

# Cấu hình API Key từ Secret của Streamlit
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.warning("Chưa cấu hình API Key.")

# Hàm đọc file PDF
def get_pdf_text(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Cột bên trái để upload tài liệu
with st.sidebar:
    st.header("1. Nạp kiến thức")
    uploaded_file = st.file_uploader("Tải lên tài liệu (PDF)", type="pdf")
    
    context_text = ""
    if uploaded_file is not None:
        with st.spinner("Đang đọc tài liệu..."):
            context_text = get_pdf_text(uploaded_file)
            st.success("Đã nạp xong! Hãy hỏi bên phải.")
            
# Giao diện Chat chính
st.header("2. Hỏi đáp chuyên môn")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý khi người dùng nhập câu hỏi
if prompt := st.chat_input("Hỏi gì đó về tài liệu vừa nạp..."):
    # Hiển thị câu hỏi người dùng
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Xử lý trả lời
    if context_text:
        try:
            # Tạo prompt chuyên gia
            full_prompt = f"""
            Bạn là một trợ lý học thuật chuyên sâu (đặc biệt về Kỹ thuật/Hàng không).
            Dựa vào nội dung văn bản được cung cấp dưới đây, hãy trả lời câu hỏi của người dùng một cách chính xác, học thuật và logic.
            Nếu thông tin không có trong văn bản, hãy nói rõ là không tìm thấy trong tài liệu.
            
            VĂN BẢN CUNG CẤP:
            {context_text}
            
            CÂU HỎI:
            {prompt}
            """
            
            model = genai.GenerativeModel('gemini-1.5-flash') # Dùng bản Flash cho nhanh và miễn phí
            response = model.generate_content(full_prompt)
            
            # Hiển thị câu trả lời
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Lỗi: {e}")
    else:
        st.warning("Vui lòng tải lên tài liệu PDF ở cột bên trái trước.")
