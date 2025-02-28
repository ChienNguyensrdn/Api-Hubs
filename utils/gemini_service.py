import json

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
        # result = response.text
        # data = json.loads(cleaned_string)
        # formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
        # return formatted_json
        result = response.text
        print(result)
        cleaned_string = result.strip("```json\n").strip("```")
        data = json.loads(cleaned_string)  # Chuyển từ chuỗi JSON sang đối tượng Python
        return data