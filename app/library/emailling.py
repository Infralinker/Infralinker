from flask_mail import Message, Mail
from flask_login import current_user
from .. import db
import datetime
from ..models import ChangeLog
from threading import Thread
from flask import Flask

app = Flask(__name__)

mail = Mail(app)

def run_async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper

@run_async
def send_async_email(msg):
   with app.app_context():
      mail.send(msg)

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=to,
        html=template,
        sender= "notifications@infralinker.app"
    )
    # mail.send(msg)
    send_async_email(msg)

##################################
## CHANGE LOG FUNCTION ###########
##################################
def change_log(table_type, action_type, id_asset, description_asset):
    """
    THIS FONCTION IS FOR TRACING ALL MODIFICATION IN APPLICATIONS
    """
    changelog=ChangeLog(
        change_date = datetime.datetime.now(),
        user_id = current_user.id,
        change_type = table_type,
        id_type = id_asset,
        name_type = description_asset,
        action = action_type
    )
    db.session.add(changelog)
    db.session.commit()

######################################################
### Get Cloud provider COLOR by datacenter type#######
######################################################
def get_cloud_provider_details(datacenter_type):
    cloud_providers = {
        "AWS": ("Amazon Web Services", "#FF9900"),
        "AZURE": ("Microsoft Azure", "#0089D6"),
        "GCP": ("Google Cloud Platform", "#4285F4"),
        "ALIBABA": ("Alibaba Cloud", "#FF6F61"),
        "ORACLE": ("Oracle Cloud", "#F80000"),
        "IBM": ("IBM Cloud", "#006699"),
        "TENCENT": ("Tencent Cloud", "#0D8EFF"),
        "OVH": ("OVH Cloud", "#123F6D"),
        "DIGITALOCEAN": ("DigitalOcean Cloud", "#0080FF"),
        "LINODE": ("Linode Cloud", "#00A95C"),
        "ON-PREMISE": ("ON-PREMISE", "#616161")
    }
    complet_name, color = cloud_providers.get(datacenter_type, ("OTHER Cloud", "#262626"))
    return complet_name, color