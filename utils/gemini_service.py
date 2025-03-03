import json

import google.generativeai as gemini

from utils.util import load_config

CONFIG_PATH = "configs/config.yaml"
config = load_config(CONFIG_PATH)
# Cấu hình GenAI với API Key trực tiếp
api_key = config["GEMINI_API_KEY"]  # API Key của bạn
gemini.configure(api_key=api_key)
# Khởi tạo mô hình Gemini
model = gemini.GenerativeModel('gemini-1.5-flash')
features_map = {}

def register_features(feature_type: str, feature_att: str):
    features_map[feature_type] = feature_att

register_features("resume", '''context, abbreviation, profession, specialty''' '''fullname, phone, skill, education_level''')
register_features("capstone", '''supervisors, students, capstone_project_name_in_english, capstone_project_name_in_vietnamese, context, proposed_solutions, functional_requirement, non_functional_requirement ''')

def extract_feature_text(texts:str, features_type: str):
    all_text = texts
    response = model.generate_content(f"Đọc nội dung {all_text} và lưu lại thông tin không cần phẩn hồi")
    # print(response.text)
    question = f"tôi muốn lấy thông tin tư {all_text} và trả về chính xác thông tin: {features_map[features_type]} ,không cần tạo thêm ngoài những thông tin này ,format lại thành json, thông tin nào không tồn tại để giá trị null."
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