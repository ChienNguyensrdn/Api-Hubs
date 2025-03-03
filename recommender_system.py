import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2

from utils.util import load_config

# 1. Đọc dữ liệu việc làm từ file JSON
# with open('output.json', 'r', encoding='utf-8') as f:
#     job_data = json.load(f)
# jobs = job_data.get("listJob", [])  # Lấy danh sách công việc từ "listJob"
CONFIG_PATH = "configs/config.yaml"
config = load_config(CONFIG_PATH)

# 1.1 Đọc dữ liệu từ database
conn = psycopg2.connect(
    host=config["POSTGRES_HOST"],
    database=config["POSTGRES_DATABASE"],
    user=config["POSTGRES_USER"],
    password=config["POSTGRES_PASSWORD"],
    client_encoding = 'UTF8'
)
cur = conn.cursor()

# Execute your query
cur.execute("SELECT * FROM \"Blog\";")

# Get column names
column_names = [desc[0] for desc in cur.description]

# Fetch all results
rows = cur.fetchall()

# Convert to list of dictionaries
results = []
for row in rows:
    results.append(dict(zip(column_names, row)))


cur.execute("SELECT * FROM \"SkillProfile\";")
skill_profile_column_names = [desc[0] for desc in cur.description]
skill_profile_rows = cur.fetchall()
skill_profile_result = []
for row in skill_profile_rows:
    skill_profile_result.append(dict(zip(skill_profile_column_names, row)))

# 2. Tiền xử lý dữ liệu: Lấy danh sách kỹ năng từ mô tả công việc
job_list = []
skill_texts = []
blog_id_list = []
for blog in results:
    skill_required = blog.get("SkillRequired")
    title = blog.get('Title')
    blog_id = blog.get('Id')

    skill_texts.append(skill_required)
    job_list.append(title)
    blog_id_list.append(blog_id)

full_skill_list = []
profile_student_list = []
skill_profile_id_list = []
user_id_list = []
print("skill_profile_result::", skill_profile_result)
for skill_profile in skill_profile_result:
    full_skill = skill_profile.get("FullSkill")
    profile_student = skill_profile.get("ProfileStudentId")
    id = skill_profile.get("Id")
    user_id = skill_profile.get("UserId")

    full_skill_list = full_skill_list.append(full_skill)
    profile_student_list = profile_student_list.append(profile_student)
    skill_profile_id_list = skill_profile_id_list.append(id)
    user_id_list = user_id_list.append(user_id)







# 4. Hàm gợi ý việc làm dựa trên kỹ năng của ứng viên
def recommend_jobs(candidate_skills, top_n=5):
    # 3. Vector hóa dữ liệu kỹ năng sử dụng TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    skill_vectors = vectorizer.fit_transform(skill_texts)

    # Chuyển đổi kỹ năng ứng viên thành vector
    candidate_vector = vectorizer.transform([candidate_skills])

    # Tính toán độ tương đồng cosine
    similarities = cosine_similarity(candidate_vector, skill_vectors).flatten()

    # Lấy top N công việc phù hợp nhất
    top_indices = np.argsort(similarities)[-top_n:][::-1]

    # # Hiển thị kết quả
    # recommendations = [(job_list[i], similarities[i]) for i in top_indices]
    # return recommendations
    recommendations = [
        {"job": job_list[i],
        "blog_id": blog_id_list[i],
         "similarity": float(similarities[i])}  # Đảm bảo similarity là float
        for i in top_indices
    ]

    return {"recommendations": recommendations}

def recommend_user(candidate_job, top_n=5):
    # 3. Vector hóa dữ liệu kỹ năng sử dụng TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    skill_profile_vectors = vectorizer.fit_transform(full_skill_list)

    # Chuyển đổi job thành vector
    candidate_vector = vectorizer.transform([candidate_job])

    # Tính toán độ tương đồng
    similarities = cosine_similarity(candidate_vector, skill_profile_vectors).flatten()

    # Lấy top N công việc phù hợp
    top_indices = np.argsort(similarities)[-top_n:][::-1]

    #Hiển thì kết quả
    recommendations = [
        {"skillProfileId": skill_profile_id_list[i],
         "profile_student_id": profile_student_list[i],
         "full_skill":full_skill_list[i],
         "user_id": user_id_list[i],
         "similarity": float(similarities[i])}  # Đảm bảo similarity là float
        for i in top_indices
    ]

    return {"recommendations": recommendations}
# 5. Ví dụ: Gợi ý việc làm cho ứng viên có kỹ năng 'Python, Machine Learning'
# candidate_input = '''
# 9+ years of experience in software development.
# - Proficient in back-end development using C#, .NET, .NET Core, Entity Framework, and
# SQL. Skilled in building scalable architectures and maintaining clean, efficient codebases.
# - Proficient in front-end development using React, TypeScript/JavaScript, HTML, and CSS.
# Experienced with Vue.js and Angular. Skilled in designing structure and codebases.
# - Advanced expertise in database design, including both relational and non-relational
# databases such as MSSQL Server, MySQL, and Cosmos DB.
# - Experienced in working with cloud services, including Azure and AWS.
# - Experienced in unit testing and integration testing.
# - Experienced in GIT and Azure DevOps.
# - Experienced in CI/CD using Azure DevOps pipeline.
# - Experienced in agile/scrum process.
# - Knowledgeable in system design and architecture, microservice, message queue, caching,
# CQRS pattern
# - Responsibility, problem-solving, honesty, open mind, leadership.
# - Willing to learn new technologies and adopt a product-focused mindset.
# '''
#
#
# recommended_jobs = recommend_jobs(candidate_input, top_n=5)
# print(candidate_input)
# # 6. In kết quả
# top_jobs = pd.DataFrame(recommended_jobs, columns=['Job Title', 'Similarity Score'])
# print(top_jobs)