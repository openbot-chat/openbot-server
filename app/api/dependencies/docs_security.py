import os
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


basicSecurity = HTTPBasic()


def basic_http_credentials(
    credentials: HTTPBasicCredentials = Depends(basicSecurity),
) -> str:
    correct_username = secrets.compare_digest(
        credentials.username, os.getenv('DOCS_USERNAME', 'master')
    )
    correct_password = secrets.compare_digest(
        credentials.password, os.getenv('DOCS_PASSWORD', 'bbbbcccc')
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username