from rest_framework import exceptions, generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from bugs import serializers
from bugs.models import Bug, Comment


class BugList(generics.ListCreateAPIView):
    serializer_class = serializers.BugSerializer

    def get_queryset(self):
        bug_status = self.request.query_params.get('status')
        if bug_status:
            if bug_status not in [Bug.Status.RESOLVED, Bug.Status.UNRESOLVED]:
                raise exceptions.ValidationError('Invalid value for status parameter.')
            return Bug.objects.filter(status=bug_status)
        return Bug.objects.all()


class BugDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bug.objects.all()
    serializer_class = serializers.BugDetailSerializer
    http_method_names = ['get', 'patch', 'delete']


class BugAssign(generics.UpdateAPIView):
    queryset = Bug.objects.all()
    serializer_class = serializers.BugAssignSerializer
    http_method_names = ['patch']


class BugResolve(generics.UpdateAPIView):
    queryset = Bug.objects.all()
    serializer_class = serializers.ResolveBugSerializer
    http_method_names = ['patch']


class CommentCreate(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    def create(self, request, *args, **kwargs):
        bug = get_object_or_404(Bug, pk=kwargs.get('pk'))

        data = request.data.copy()
        data['bug'] = bug.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CommentRetrieveDelete(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
