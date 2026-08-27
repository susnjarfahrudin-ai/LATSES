class KnowledgeMigration:
    def migrate(self, old_version: str, new_version: str) -> dict[str, str]:
        if not old_version.strip() or not new_version.strip():
            raise ValueError("Migration requires source and target versions")
        return {"from": old_version, "to": new_version, "status": "MIGRATED"}
