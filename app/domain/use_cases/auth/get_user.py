from app.domain.repositories import (
    AuthRepository,
    CompanyRepository,
    MenuRepository,
    RolePermissionRepository,
)

ALL_PERMISSIONS = ["CREATE", "READ", "UPDATE", "DELETE", "EXPORT"]


class GetUserUseCase:
    def __init__(
        self,
        auth_repo: AuthRepository,
        menu_repo: MenuRepository,
        company_repo: CompanyRepository,
        role_permission_repo: RolePermissionRepository,
    ) -> None:
        self.auth_repo = auth_repo
        self.menu_repo = menu_repo
        self.company_repo = company_repo
        self.role_permission_repo = role_permission_repo

    def execute(self, user_id: int) -> dict:
        user = self.auth_repo.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        role_entities = self.role_permission_repo.get_roles_for_user(user_id)
        role_ids = [r.id for r in role_entities]
        roles = [{"id": r.id, "name": r.name} for r in role_entities]

        companies = self.company_repo.list_for_user(user_id)

        all_menus = self.menu_repo.get_all()

        if user.is_admin:
            menu_perm_map: dict[int, list[str]] = {m.id: ALL_PERMISSIONS for m in all_menus}
        else:
            menu_perms = self.menu_repo.get_menus_with_permissions_for_role_ids(role_ids)
            menu_perm_map = {}
            for item in menu_perms:
                menu_perm_map[item["menu_id"]] = item["permissions"]

        menus = self._build_tree(all_menus, menu_perm_map)

        return {
            "user": user,
            "profile": user.profile,
            "roles": roles,
            "companies": companies,
            "menus": menus,
        }

    def _build_tree(self, all_menus, menu_perm_map: dict[int, list[str]]) -> list[dict]:
        children_map: dict[int | None, list] = {}
        for m in all_menus:
            children_map.setdefault(m.parent_id, []).append(m)

        root_menus = children_map.get(None, [])
        result = []
        for menu in sorted(root_menus, key=lambda x: x.order_index):
            node = self._build_node(menu, children_map, menu_perm_map)
            if node:
                result.append(node)
        return result

    def _build_node(self, menu, children_map, menu_perm_map: dict[int, list[str]]) -> dict:
        children = children_map.get(menu.id, [])
        child_nodes = []
        for child in sorted(children, key=lambda x: x.order_index):
            node = self._build_node(child, children_map, menu_perm_map)
            if node:
                child_nodes.append(node)

        permissions = menu_perm_map.get(menu.id, [])
        if not permissions and not child_nodes:
                return None

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
            "permissions": permissions,
        }
