from app.user.models import User

class RolePermissionMixin:
    allowed_roles: list[str] = []

    async def _has_role(self, user_id):
        if not user_id:
            return False

        return await User.filter(
            id=user_id,
            role__in=self.allowed_roles,
        ).exists()