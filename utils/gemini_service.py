import google.generativeai as gemini



# Cấu hình GenAI với API Key trực tiếp
api_key = ""  # API Key của bạn
gemini.configure(api_key=api_key)
# Khởi tạo mô hình Gemini
model = gemini.GenerativeModel('gemini-1.5-flash')

features = '''
context, Abbreviation, profession, specialty
'''

'''
fullname, phone, skill, học vấn
'''
def extract_feature_text(texts:str):
    all_text = texts
    response = model.generate_content(f"Đọc nội dung {all_text} và lưu lại thông tin không cần phẩn hồi")
    # print(response.text)
    question = f"tôi muốn lấy thông tin tư {all_text} và trả về thông tin: {features} format lại thành json"
    response = model.generate_content(question)
    if response.text:
        return response.text