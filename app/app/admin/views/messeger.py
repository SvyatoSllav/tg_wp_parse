from flask_admin.contrib.sqla import ModelView


class MessengerView(ModelView):
    column_list = [
        "id",
        "api_token",
        "api_id",
        "phone",
        "type",
        "is_active",
        "created_at",
    ]