class ReleaseStatus:
    Public = "public"
    Private = "private"
    Hidden = "hidden"
    All = "all"

    @staticmethod
    def Check(rs):
        if rs in ["public", "private", "hidden", "all"]:
            return True
        return False
