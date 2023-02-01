from flask_admin.contrib.sqla import ModelView


class MessageView(ModelView):
    column_list = [
        "id",
        "message_id",
        "text",
        "author_id",
        "author_name",
        "auhtor_phone",
        "sent_at",
        "message_media_paths",
        "last_message_id",
        "created_at",
        "chat_id",
    ]