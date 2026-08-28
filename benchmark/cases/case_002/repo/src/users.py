USERS={1:{"id":1,"name":"Ada"},2:{"id":2,"name":"Grace"}}
def get_user_name(user_id: int) -> str | None:
    user=USERS.get(user_id)
    return user["name"]
