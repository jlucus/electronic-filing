import os
import logging
import traceback
import jinja2
from fastapi.encoders import jsonable_encoder
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.utils.async_utils import async_wrap
from app.core.config import SENDGRID_API_KEY
from app.models.messages import MessageTemplate

logger = logging.getLogger('fastapi')

def send_message(
    sender: str,
    recipients: list,
    subject: str,
    html_content: str
):

    message = Mail(from_email=sender,
                   to_emails=recipients,
                   subject=subject,
                   html_content=html_content)

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(message)
        logger.info(response)

        if response.status_code == 202:
            return jsonable_encoder(response)
        
    except Exception as e:
        logger.exception(traceback.format_exception)


    return False

async_send_message = async_wrap(send_message)

def render_template(data_dict: dict, template: str):

    template = jinja2.Template(template)

    html = template.render(**data_dict)

    return html


def render_template_from_db(data_dict: dict,
                            db_template: MessageTemplate):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    loader = jinja2.FileSystemLoader(current_dir+"/email_templates")
    env = jinja2.Environment(loader=loader)

    pre_template = '{% extends "layout.html" %}{% block content %}'
    post_template = '{% endblock %}'
    template = env.from_string(pre_template+db_template.template+post_template)

    html = template.render(**data_dict)

    return html


def render_template_from_disk(data_dict, template_filename):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    loader = jinja2.FileSystemLoader(current_dir+"/email_templates")
    env = jinja2.Environment(loader=loader)

    template = env.get_template(template_filename)

    html = template.render(**data_dict)


    return html
    
