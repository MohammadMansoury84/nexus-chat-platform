from uuid import UUID

from src.entities.Group import Group


class GroupRepository:
    def __init__(self) -> None:
        self._groups: list[Group] = []

    def add(self, group: Group) -> Group:
        self._groups.append(group)
        return group

    def get_by_id(self, group_id: UUID) -> Group | None:

        for group in self._groups:
            if group.id == group_id:
                return group

        return None

    def list_all(self) -> list[Group]:
        return self._groups

    def remove_group(self, group: Group) -> bool:
        if group in self._groups:
            self._groups.remove(group)
            return True
        return False
