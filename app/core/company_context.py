from app.core.context import get_empresa_id, set_empresa_id, clear_empresa_id


class CompanyContext:
    @staticmethod
    def get_empresa_id() -> int | None:
        return get_empresa_id()

    @staticmethod
    def set_empresa_id(empresa_id: int | None):
        set_empresa_id(empresa_id)

    @staticmethod
    def clear():
        clear_empresa_id()

    @staticmethod
    def get_empresa_id_or_default(user_empresa_id: int | None) -> int | None:
        header_id = get_empresa_id()
        if header_id is not None:
            return header_id
        return user_empresa_id
