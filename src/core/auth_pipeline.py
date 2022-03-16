def save_user(backend, user, response, *args, **kwargs) -> None:
    if user and not user.is_staff:
        user.is_staff = True
        user.save()
