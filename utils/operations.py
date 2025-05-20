def extract_auth_token(request) -> str | None:
    try:
        token = request.headers.get('Authorization').split(' ')[1] 
        return token
    except: return None