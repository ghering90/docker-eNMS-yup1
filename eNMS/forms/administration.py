from wtforms.validators import InputRequired
from wtforms.widgets import TextArea

from eNMS.forms import BaseForm, choices
from eNMS.forms.fields import (
    BooleanField,
    HiddenField,
    IntegerField,
    JsonField,
    MultipleInstanceField,
    PasswordField,
    StringField,
    SelectField,
    SelectMultipleField,
    SelectMultipleStringField,
)
from eNMS.setup import settings, themes


class SettingsForm(BaseForm):
    form_type = HiddenField(default="settings_panel")
    action = "eNMS.administration.saveSettings"
    settings = JsonField("Settings")
    write_changes = BooleanField("Write changes back to 'settings.json' file")


class AdminForm(BaseForm):
    template = "administration"
    form_type = HiddenField(default="administration")


class UploadFilesForm(BaseForm):
    template = "upload_files"
    folder = HiddenField()
    form_type = HiddenField(default="upload_files")


class ResultLogDeletionForm(BaseForm):
    action = "eNMS.administration.resultLogDeletion"
    form_type = HiddenField(default="result_log_deletion")
    deletion_types = SelectMultipleField(
        "Instances do delete",
        choices=[("run", "result"), ("changelog", "changelog")],
    )
    date_time = StringField(type="date", label="Delete Records before")


class ServerForm(BaseForm):
    action = "eNMS.base.processData"
    form_type = HiddenField(default="server")
    id = HiddenField()
    name = StringField("Name", [InputRequired()])
    description = StringField(widget=TextArea(), render_kw={"rows": 6})
    ip_address = StringField("IP address")
    weight = IntegerField("Weigth")


class CredentialForm(BaseForm):
    action = "eNMS.base.processData"
    form_type = HiddenField(default="credential")
    id = HiddenField()
    name = StringField("Name", [InputRequired()])
    role = SelectField(
        "Role",
        choices=(
            ("read-write", "Read Write"),
            ("read-only", "Read Only"),
        ),
    )
    subtype = SelectField(
        "Type", choices=(("password", "Username / Password"), ("key", "SSH Key"))
    )
    description = StringField(widget=TextArea(), render_kw={"rows": 6})
    device_pools = MultipleInstanceField("Devices", model="pool")
    user_pools = MultipleInstanceField("Users", model="pool")
    priority = IntegerField("Priority", default=1)
    username = StringField("Username")
    enable_password = PasswordField("'Enable' Password")
    password = PasswordField("Password")
    private_key = StringField(widget=TextArea(), render_kw={"rows": 10})


class LoginForm(BaseForm):
    form_type = HiddenField(default="login")
    authentication_method = SelectField("Authentication Method", choices=())
    name = StringField("Name", [InputRequired()])
    password = PasswordField("Password", [InputRequired()])


class ImportService(BaseForm):
    action = "eNMS.administration.importService"
    form_type = HiddenField(default="import_service")
    service = SelectField("Service", choices=())


class ChangelogForm(BaseForm):
    action = "eNMS.base.processData"
    form_type = HiddenField(default="changelog")
    id = HiddenField()
    severity = SelectField(
        "Severity",
        choices=(
            ("debug", "Debug"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("error", "Error"),
            ("critical", "Critical"),
        ),
    )
    content = StringField(widget=TextArea(), render_kw={"rows": 10})


def init_variable_forms(app):
    class RbacForm(BaseForm):
        action = "eNMS.base.processData"
        form_type = HiddenField(default="rbac")
        id = HiddenField()
        name = StringField("Name", [InputRequired()])
        email = StringField("Email")

    class UserForm(RbacForm):
        form_type = HiddenField(default="user")
        description = StringField(widget=TextArea(), render_kw={"rows": 6})
        groups = StringField("Groups")
        theme = SelectField(
            "Theme",
            choices=[
                (theme, values["name"]) for theme, values in themes["themes"].items()
            ],
        )
        authentication = SelectField(
            "Authentication",
            choices=[
                (method, values["display_name"])
                for method, values in settings["authentication"]["methods"].items()
            ],
        )
        password = PasswordField("Password")
        is_admin = BooleanField(default=False)

    class AccessForm(RbacForm):
        template = "access"
        form_type = HiddenField(default="access")
        description = StringField(widget=TextArea(), render_kw={"rows": 6})
        menu = SelectMultipleField("Menu", choices=choices(list(app.rbac["menu"])))
        pages = SelectMultipleField("Pages", choices=choices(app.rbac["pages"]))
        upper_menu = SelectMultipleField(
            "Upper Menu", choices=choices(app.rbac["upper_menu"])
        )
        get_requests = SelectMultipleField(
            "GET requests", choices=choices(app.rbac["get_requests"])
        )
        post_requests = SelectMultipleField(
            "POST requests", choices=choices(app.rbac["post_requests"])
        )
        delete_requests = SelectMultipleField(
            "DELETE requests", choices=choices(app.rbac["delete_requests"])
        )
        user_pools = MultipleInstanceField("pool")
        access_pools = MultipleInstanceField("pool")
        access_type = SelectMultipleStringField(
            "Access Type",
            choices=choices(
                ["Read", "Edit", "Run", "Schedule", "Connect", "Use as target"]
            ),
        )
        relations = ["pools", "services"]

        @classmethod
        def form_init(cls):
            cls.configure_relationships("users")

    class DatabaseMigrationsForm(BaseForm):
        template = "database_migration"
        form_type = HiddenField(default="database_migration")
        empty_database_before_import = BooleanField("Empty Database before Import")
        skip_pool_update = BooleanField(
            "Skip the Pool update after Import", default="checked"
        )
        export_private_properties = BooleanField(
            "Include private properties", default="checked"
        )
        export_choices = [(p, p) for p in app.database["import_export_models"]]
        import_export_types = SelectMultipleField(
            "Instances to migrate", choices=export_choices
        )

    class DatabaseDeletionForm(BaseForm):
        action = "eNMS.administration.databaseDeletion"
        form_type = HiddenField(default="database_deletion")
        deletion_choices = [(p, p) for p in app.database["import_export_models"]]
        deletion_types = SelectMultipleField(
            "Instances to delete", choices=deletion_choices
        )
