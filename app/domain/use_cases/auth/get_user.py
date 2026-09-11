from app.domain.repositories import (
    MenuRepository,
    ProfileRepository,
    UserRepository,
    UserRoleRepository,
)

ALL_PERMISSIONS = ["CREATE", "READ", "UPDATE", "DELETE", "EXPORT"]


class GetUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        profile_repo: ProfileRepository,
        user_role_repo: UserRoleRepository,
        menu_repo: MenuRepository,
    ) -> None:
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.user_role_repo = user_role_repo
        self.menu_repo = menu_repo

    def execute(self, user_id: int) -> dict:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        profile = self.profile_repo.get_by_user_id(user_id)
        user_roles = self.user_role_repo.get_by_user_id(user_id)
        roles = [ur for ur in user_roles]

        all_menus = self.menu_repo.get_all()

        if user.is_admin:
            menu_perm_map: dict[int, list[str]] = {m.id: ALL_PERMISSIONS for m in all_menus}
        else:
            role_ids = [ur.role_id for ur in user_roles]
            menu_perms = self.menu_repo.get_menus_with_permissions_for_role_ids(role_ids)
            menu_perm_map = {}
            for item in menu_perms:
                menu_perm_map[item["menu_id"]] = item["permissions"]

        menus = self._build_tree(all_menus, menu_perm_map)

        return {
            "user": user,
            "profile": profile,
            "roles": roles,
            "menus": menus,
        }

    def _build_tree(self, all_menus, menu_perm_map: dict[int, list[str]]) -> list[dict]:
        children_map: dict[int | None, list] = {}
        for m in all_menus:
            parent_id = m.parent_id
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(m)

        root_menus = children_map.get(None, [])
        result = []
        for menu in sorted(root_menus, key=lambda x: x.order_index):
            node = self._build_node(menu, children_map, menu_perm_map)
            result.append(node)
        return result

    def _build_node(self, menu, children_map, menu_perm_map: dict[int, list[str]]) -> dict:
        children = children_map.get(menu.id, [])
        child_nodes = []
        for child in sorted(children, key=lambda x: x.order_index):
            child_nodes.append(self._build_node(child, children_map, menu_perm_map))

        return {
            "id": menu.id,
            "parent_id": menu.parent_id,
            "name": menu.name,
            "code": menu.code,
            "icon": menu.icon,
            "route": menu.route,
            "order_index": menu.order_index,
            "badge": menu.badge,
            "status": menu.status,
            "children": child_nodes,
            "permissions": menu_perm_map.get(menu.id, []),
        }
