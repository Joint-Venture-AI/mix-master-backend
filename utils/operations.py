def extract_auth_token(request) -> str | None:
    try:return request.headers.get('Authorization').split(' ')[1]
    except: return None