class UpdateEmailPolicyUseCase:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    async def execute(self, userid: int, emailpolicy: str):
        if emailpolicy not in ("appendonly", "allowdelete"):
            raise ValueError("invalid emailpolicy")
        return await self.user_repo.set_emailpolicy(userid=userid, emailpolicy=emailpolicy)
