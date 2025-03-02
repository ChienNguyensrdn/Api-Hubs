import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Đọc dữ liệu việc làm từ file JSON
with open('output.json', 'r', encoding='utf-8') as f:
    job_data = json.load(f)
jobs = job_data.get("listJob", [])  # Lấy danh sách công việc từ "listJob"
# print(f"Tổng số công việc: {len(jobs)}")
# print("Ví dụ một công việc:", jobs[0].get('jobExperience', ''))
# 2. Tiền xử lý dữ liệu: Lấy danh sách kỹ năng từ mô tả công việc
job_list = []
cv_list = []
skill_texts = []
for job in jobs:
    title = job.get('name', 'Unknown')
    skills = job.get('jobExperience', '')  # Lấy kỹ năng từ mô tả công việc
    # print(skills)
    job_list.append(title)
    skill_texts.append(skills)

    # 3. Vector hóa dữ liệu kỹ năng sử dụng TF-IDF
vectorizer = TfidfVectorizer(stop_words='english')
# print(skill_texts)
skill_vectors = vectorizer.fit_transform(skill_texts)

# 4. Hàm gợi ý việc làm dựa trên kỹ năng của ứng viên
def recommend_jobs(candidate_skills, top_n=9):
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
        {"job": job_list[i], "similarity": float(similarities[i])}  # Đảm bảo similarity là float
        for i in top_indices
    ]

    return {"recommendations": recommendations}

def recommend_user(candidate_user, top_n=9):
    # Chuyển đổi cv của user thành vector
    candidate_vector = vectorizer.transform([candidate_user])

    # Tính toán độ tương đồng
    similarities = cosine_similarity(candidate_vector, skill_vectors).flatten()

    # Lấy top N công việc phù hợp
    top_indices = np.argsort(similarities)[-top_n:][::-1]

    #Hiển thì kết quả
    recommendations = [(cv_list[i], similarities[i]) for i in top_indices]
    return recommendations
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