from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import logging
from .models import Member, TourOrder, TicketOrder
from django.utils import timezone
import openai
import os
import requests
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

# 獲取環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # 新增 OpenAI API 密鑰
openai.api_key = OPENAI_API_KEY
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

# 初始化 LINE Bot API 和 Webhook Handler
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 設定日誌
logger = logging.getLogger(__name__)

# 生成 AI 回應
def generate_ai_response_hf(question):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    data = {
        "inputs": question,
        "parameters": {
            "max_length": 150,
            "temperature": 0.2  # 嘗試較低的溫度
        }
    }
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        answer = response.json()[0]['generated_text'].strip()
        return answer
    except requests.exceptions.RequestException as e:
        logger.error(f"Hugging Face API error: {e}")
        return "抱歉，目前無法處理您的請求。"

# 接收並處理 Webhook 請求
@csrf_exempt
def callback(request):
    logger.info("Received a request")
    
    # 檢查請求方法
    if request.method != 'POST':
        logger.warning("Invalid request method: %s", request.method)
        return HttpResponseBadRequest('Only POST requests are allowed.')
    
    # 獲取簽名和請求主體
    signature = request.META.get('HTTP_X_LINE_SIGNATURE')
    body = request.body.decode('utf-8')
    logger.info("Received request with signature: %s", signature)

    # 檢查簽名是否存在
    if not signature:
        logger.error("No signature provided")
        return HttpResponseBadRequest('No signature provided.')

    # 處理請求
    try:
        handler.handle(body, signature)
        logger.info("Request handled successfully")
    except InvalidSignatureError:
        logger.error("Invalid signature: %s", signature)
        return HttpResponse(status=400)
    except Exception as e:
        logger.exception("An unexpected error occurred while handling the request: %s", e)
        return HttpResponse(status=500)

    return HttpResponse(status=200)

# 處理接收到的文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    # 查詢當前綁定帳號
    if text == "查詢當前帳號":
        user = Member.objects.filter(line_id=user_id).first()
        if user:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"當前綁定的帳號是: {user.email}"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="您尚未綁定任何帳號。"))

    # 綁定帳號
    elif text.startswith("綁定:") or text.startswith("綁定："):  # 考慮全形和半形冒號
        email = text.split(":")[-1].strip() if ":" in text else text.split("：")[-1].strip()
        logger.info(f"Attempting to bind with email: {email}")

        user = Member.objects.filter(email=email).first()
        if user:
            if user.line_id:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="此帳號已經綁定其他 Line 帳號！"))
            else:
                user.line_id = user_id
                user.save()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="帳號綁定成功！"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到此帳號！"))

    # 查詢個人訂單
    elif text == "查詢訂單":
        user = Member.objects.filter(line_id=user_id).first()
        if user:
            today = timezone.now().date()
            tour_orders = TourOrder.objects.filter(user=user, godate__gte=today)
            ticket_orders = TicketOrder.objects.filter(user=user, departure_time__gte=today)

            order_details = "您的訂單:\n"
            if tour_orders.exists():
                order_details += "\n".join([
                    f"旅遊行程: {order.tour.tourname}, 出團日期：{order.godate}\n" 
                    for order in tour_orders
                ])
                order_details += "\n\n"
            else:
                order_details += "您沒有旅遊訂單。\n"

            if ticket_orders.exists():
                order_details += "車票訂單:\n"
                order_details += "\n".join([
                    f"出發日期：{order.departure_time}, 總金額：{order.order_sum} 元" 
                    for order in ticket_orders
                ])
                order_details += "\n\n"
            else:
                order_details += "您沒有車票訂單。"

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=order_details))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先綁定帳號。"))

    # 處理其他問題並生成 AI 回應
    elif text.startswith("問AI:"):
        user = Member.objects.filter(line_id=user_id).first()
        if user:
            today = timezone.now().date()

            # 如果是新的一天，重置問題計數
            if user.last_question_date != today:
                user.question_count = 0  # 重置計數
                user.last_question_date = today  # 更新日期

            # 檢查是否已達到提問限制
            if user.question_count < 30:  # 限制為每日 30 個問題
                question = text.split("問AI:")[1].strip()
                response = generate_ai_response_hf(question)  # 使用 Hugging Face 生成回應
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
                user.question_count += 1  # 增加問題數量
                user.save()  # 儲存更新
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="您今天已經問過三十個問題了，請明天再試。"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先綁定帳號。"))

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="已收到您的訊息！"))