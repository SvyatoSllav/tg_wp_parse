from flask_admin.contrib.sqla import ModelView


class DeviceView(ModelView):
    column_list = [
        "id",
        "name",
        "device_id",
        "created_at",
    ]