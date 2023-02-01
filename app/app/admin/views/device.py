from flask_admin.contrib.sqla import ModelView


class DeviceView(ModelView):
    column_list = [
        "id",
        "name",
        "created_at",
    ]