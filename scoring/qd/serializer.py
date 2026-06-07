from rest_framework import serializers

from management.models import User, Class, Specialty, ClassName, Grade


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'specialty10']

class ClassNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassName
        fields = ['id', 'class_name']

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'grade10']

class ClassSerializer(serializers.ModelSerializer):
    class1 = ClassNameSerializer()
    grade1 = GradeSerializer()
    specialty1 = SpecialtySerializer()
    class Meta:
        model = Class
        fields = ['id','class1','grade1','specialty1']


class UserSerializer(serializers.ModelSerializer):
    class1 = ClassSerializer()
    class Meta:
        model = User
        fields = ['class1','id', 'username', 'email','phone','role']

