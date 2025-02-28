"""Gmail tool utils."""
from __future__ import annotations

from typing import Dict
import logging
import os
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import Resource
    from googleapiclient.discovery import build as build_resource

logger = logging.getLogger(__name__)


def import_google() -> Tuple[Request, Credentials]:
    """Import google libraries.

    Returns:
        Tuple[Request, Credentials]: Request and Credentials classes.
    """
    # google-auth-httplib2
    try:
        from google.auth.transport.requests import Request  # noqa: F401
        from google.oauth2.credentials import Credentials  # noqa: F401
    except ImportError:
        raise ImportError(
            "You need to install google-auth-httplib2 to use this toolkit. "
            "Try running pip install --upgrade google-auth-httplib2"
        )
    return Request, Credentials

def import_googleapiclient_resource_builder() -> build_resource:
    """Import googleapiclient.discovery.build function.

    Returns:
        build_resource: googleapiclient.discovery.build function.
    """
    try:
        from googleapiclient.discovery import build
    except ImportError:
        raise ValueError(
            "You need to install googleapiclient to use this toolkit. "
            "Try running pip install --upgrade google-api-python-client"
        )
    return build


DEFAULT_SCOPES = ["https://mail.google.com/"]


def get_gmail_credentials(
    info: Optional[Dict[str, str]] = None,
    scopes: Optional[List[str]] = None,
) -> Credentials:
    """Get credentials."""
    # From https://developers.google.com/gmail/api/quickstart/python
    Credentials = import_google()
    scopes = scopes or DEFAULT_SCOPES
    
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    return Credentials.from_authorized_user_info(info, scopes)

def build_resource_service(
    credentials: Optional[Credentials] = None,
    service_name: str = "gmail",
    service_version: str = "v1",
) -> Resource:
    """Build a Gmail service."""
    credentials = credentials or get_gmail_credentials()
    builder = import_googleapiclient_resource_builder()
    return builder(service_name, service_version, credentials=credentials)


def clean_email_body(body: str) -> str:
    """Clean email body."""
    try:
        from bs4 import BeautifulSoup

        try:
            soup = BeautifulSoup(str(body), "html.parser")
            body = soup.get_text()
            return str(body)
        except Exception as e:
            logger.error(e)
            return str(body)
    except ImportError:
        logger.warning("BeautifulSoup not installed. Skipping cleaning.")
        return str(body)
