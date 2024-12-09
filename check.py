import joblib

def predict_cluster(title):
    model = joblib.load('model_with_stopwords_removed_without_thousand_again.joblib')
    prediction = model.predict([title])  # ทำนาย cluster จาก title
    return prediction  # แปลงผลลัพธ์กลับเป็น label เดิม

# ตัวอย่างการใช้ฟังก์ชั่น
title_input = "Enter your keyword or title here"
predicted_cluster = predict_cluster(title_input)
print(f"The title belongs to cluster: {predicted_cluster[0]}")