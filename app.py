from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    FollowEvent,
    PostbackEvent,
    TextMessageContent
)

app = Flask(__name__)
import os
configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# 加入好友事件
@line_handler.add(FollowEvent)
def handle_follow(event):
    print(f'Got {event.type} event')
    # 設置歡迎訊息
    welcome_message = TextMessage(text="嗨!我是自言自語機器人，感謝您的加入！正在修改程式碼，可能會有Bug喔!!😊")

    # 使用 MessagingApi 傳送訊息
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,  # 使用 event 的 reply_token 回應
                messages=[welcome_message]
            )
        )


# 訊息事件
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if event.message.text == 'postback':
            # 建立按鈕模板
            buttons_template = ButtonsTemplate(
                title='Postback Sample',
                text='Postback Action',
                actions=[
                    PostbackAction(label='Click Me!', text='You clicked the button!', data='postback_action'),
                ]
            )
            template_message = TemplateMessage(
                alt_text='Postback Sample',
                template=buttons_template
            )
            # 回覆按鈕模板訊息
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        else:
            # 回覆一般文字訊息
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="您傳送的訊息是：" + event.message.text)]
                )
            )


# 處理 Postback 事件
@line_handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'postback_action':
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="Postback 已觸發！")]
                )
            )


if __name__ == "__main__":
    # 修改此行以綁定到 0.0.0.0 並使用 Render 提供的端口
    port = int(os.getenv("PORT", 5000))  # 默認端口為 5000
    app.run(host='0.0.0.0', port=port)


