import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from members.models import User, Member, Tour, Rating, UserBehavior  # 確保引入 UserBehavior 模型
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
from decimal import Decimal
import random

def get_current_season():
    """根據當前月份返回對應的季節：春、夏、秋或冬。"""
    month = datetime.now().month
    if 3 <= month <= 5:
        return 'spring'  # 春天
    elif 6 <= month <= 8:
        return 'summer'  # 夏天
    elif 9 <= month <= 11:
        return 'autumn'  # 秋天
    else:
        return 'winter'  # 冬天

def collaborative_filtering(user_id):
    """基於用戶評分的協同過濾推薦行程。"""
    users = list(Member.objects.all())
    tours = list(Tour.objects.all())
    ratings_matrix = np.zeros((len(tours), len(users)))

    for i, tour in enumerate(tours):
        for j, user in enumerate(users):
            rating = Rating.objects.filter(user_name=user, tour=tour).first()
            ratings_matrix[i, j] = rating.value if rating else 0

    # 計算用戶之間的相似性（使用餘弦相似度）
    user_similarity = cosine_similarity(ratings_matrix.T)

    user_index = users.index(Member.objects.get(id=user_id))
    similar_users = user_similarity[user_index]

    # 使用均值填充
    for i in range(len(ratings_matrix)):
        if np.count_nonzero(ratings_matrix[i]) > 0:  # 確保該行有評分
            mean_rating = np.mean(ratings_matrix[i][ratings_matrix[i] != 0])
            ratings_matrix[i][ratings_matrix[i] == 0] = mean_rating  # 填充零評分

    recommended_tours = np.dot(ratings_matrix, similar_users)

    return [tours[i].id for i in np.argsort(recommended_tours)[::-1]]

def content_based_filtering(user_id):
    """基於用戶評分的內容過濾推薦行程。"""
    tours = list(Tour.objects.all())
    feature_matrix = extract_features(tours)  # 提取特徵矩陣

    # 假設 user_id 的偏好特徵與行程相似度的計算邏輯
    user_ratings = Rating.objects.filter(user_name__id=user_id)
    
    if not user_ratings.exists():
        return []  # 如果用戶沒有評分，返回空列表

    user_feature_vector = np.zeros(feature_matrix.shape[1])
    for rating in user_ratings:
        tour_index = tours.index(rating.tour)
        user_feature_vector += feature_matrix[tour_index].toarray().flatten() * rating.value

    # 計算相似度
    cosine_similarities = cosine_similarity(user_feature_vector.reshape(1, -1), feature_matrix).flatten()
    recommended_tours_indices = np.argsort(cosine_similarities)[::-1]

    return [tours[i].id for i in recommended_tours_indices]

def hybrid_recommendation(user_id):
    """綜合協同過濾和內容過濾生成最終推薦行程。"""
    cf_result = collaborative_filtering(user_id)
    cb_result = content_based_filtering(user_id)

    if not cf_result and not cb_result:
        all_tours = list(Tour.objects.all())
        random_recommendations = random.sample(all_tours, min(5, len(all_tours)))
        return [tour.id for tour in random_recommendations]  # 返回隨機推薦

    recommendations = {}

    # 確保有協同過濾的推薦
    if cf_result:
        for tour_id in cf_result:
            recommendations[tour_id] = recommendations.get(tour_id, 0) + 0.3

    # 確保有內容過濾的推薦
    if cb_result:
        for tour_id in cb_result:
            recommendations[tour_id] = recommendations.get(tour_id, 0) + 0.7

    # 如果 recommendations 還是空的，則返回隨機行程
    if not recommendations:
        all_tours = list(Tour.objects.all())
        random_recommendations = random.sample(all_tours, min(5, len(all_tours)))
        return [tour.id for tour in random_recommendations]

    final_recommendations = sorted(recommendations.items(), key=lambda item: item[1], reverse=True)
    return [tour_id for tour_id, score in final_recommendations]

def extract_features(tours):
    descriptions = [tour.description for tour in tours]
    vectorizer = TfidfVectorizer()
    feature_matrix = vectorizer.fit_transform(descriptions)
    return feature_matrix

def get_season_weight(tour, current_season):
    """判斷行程是否符合當前季節，符合的話返回較高的權重，不符合則返回0."""
    return Decimal(0.2) if tour.season == current_season else Decimal(0.0)

def get_recommendations(user):
    current_season = get_current_season()  # 获取当前季节
    user_id = user.id

    # 获取用户的评分和浏览记录等数据
    user_behavior = UserBehavior.objects.filter(user=user)

    # 如果没有相关数据，随机推荐
    if not user_behavior.exists():
        all_tours = list(Tour.objects.all())
        random_recommendations = random.sample(all_tours, min(6, len(all_tours)))
        return random_recommendations  # 返回Tour对象列表

    recommendations = []
    # 基于用户行为生成推荐
    for behavior in user_behavior:
        # 这里可以根据行为生成推荐逻辑
        recommendations += some_recommendation_logic(behavior)

    print("Recommendations based on user behavior:", recommendations)

    # 创建推荐分数字典
    recommended_scores = {tour.id: idx for idx, tour in enumerate(recommendations)}

    # 根据不同权重计算最终推荐
    final_recommendations = sorted(
        Tour.objects.all(),
        key=lambda tour: (
            recommended_scores.get(tour.id, 0) * Decimal(0.5) +
            Decimal(tour.average_rating) * Decimal(0.3) +
            (Decimal(tour.view_count) / Decimal(100)) * Decimal(0.1) +
            get_season_weight(tour, current_season)  # 根据季节进行加权
        ),
        reverse=True
    )[:6]  # 返回前5个推荐

    print("Final recommendations before returning:", final_recommendations)

    # 如果没有最终推荐，则随机选择
    if not final_recommendations:
        all_tours = list(Tour.objects.all())
        random_recommendations = random.sample(all_tours, min(5, len(all_tours)))
        return random_recommendations  # 返回Tour对象列表

    # 返回推荐的Tour对象列表
    return final_recommendations