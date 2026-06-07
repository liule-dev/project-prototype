


class StudentPermission:
    def has_permission(self,request,view):
        if request.user.is_authenticated and request.user.role=='student':
            return True
        return False
class ManagePermission:
    def has_permission(self,request,view):
        if request.user.is_authenticated and request.user.role=='admin':
            return True
        return False
class TeacherPermission:
    def has_permission(self,request,view):
        if request.user.is_authenticated and request.user.role=='teacher':
            return True
        return False