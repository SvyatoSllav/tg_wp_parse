from flask_admin.contrib.sqla import ModelView


class ChatView(ModelView):
    column_list = [
        "id",
        "chat_id",
        "chat_name",
        "messenger_type",
        "last_message_id",
        "chat_avatars_img_paths",
        "messenger_id",
        "created_at",
    ]