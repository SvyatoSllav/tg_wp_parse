from flask_admin.contrib.sqla import ModelView


class ChatView(ModelView):
    column_list = [
        "id",
        "chat_id",
        "chat_name",
        "created_at",
        "chat_avatars_img_paths",
        "messenger_id",
    ]