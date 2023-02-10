from abc import ABC

from rest_framework import serializers

from bugs.models import Bug, Comment


class StatusValidator:
    @staticmethod
    def validate_status(value):
        if value not in [Bug.Status.RESOLVED, Bug.Status.UNRESOLVED]:
            raise serializers.ValidationError('Invalid value for status parameter.')
        return value


class BugSerializer(serializers.ModelSerializer, StatusValidator):
    class Meta:
        model = Bug
        fields = ('title', 'description', 'status', 'assignee_id')
        extra_kwargs = {
            'status': {'required': False},
            'assignee_id': {'required': False},
        }


class BugDetailSerializer(serializers.ModelSerializer, StatusValidator):
    class Meta:
        model = Bug
        fields = ('title', 'description', 'status', 'assignee_id')
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'status': {'required': False},
            'assignee_id': {'required': False},
        }


class ResolveBugSerializer(serializers.ModelSerializer, StatusValidator):
    class Meta:
        model = Bug
        fields = ('status',)


class BugAssignSerializer(serializers.ModelSerializer, StatusValidator):
    class Meta:
        model = Bug
        fields = ('assignee_id',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('title', 'body', 'bug')
        extra_kwargs = {
            'bug': {'required': False},
        }
