"""
Tests should make sure that the API is working as expected. Details:
- Create a bug. A bug should have a title, a body, and a status (resolved/unresolved).
- Edit a bug.
- Delete a bug.
- View all bugs.
- View a specific bug.
- Add a comment to a bug. A comment should have a title, and a body.
- Delete a comment from a bug.
- Mark a bug as "resolved".
- Mark a bug as "unresolved".
- View all bugs marked as "resolved".
- Assign the bug to a user. A user is identified by its ID.
"""
from rest_framework import status
from rest_framework.test import APITestCase

from bugs.models import Bug, Comment


class BugListTestCase(APITestCase):
    @staticmethod
    def create_n_bugs(n):
        for i in range(n):
            Bug.objects.create(
                title=f'Test bug {i}',
                description=f'Test description {i}',
                status=Bug.Status.UNRESOLVED,
            )

    def test_create_bug(self):
        data = {
            'title': 'Test bug',
            'description': 'Test description',
            'status': Bug.Status.UNRESOLVED,
            'assignee_id': '1',
        }
        response = self.client.post('/bugs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bug.objects.count(), 1)
        self.assertEqual(Bug.objects.get().title, 'Test bug')

    def test_create_bug_invalid_status(self):
        data = {
            'title': 'Test bug',
            'description': 'Test description',
            'status': 'invalid',
            'assignee_id': '1',
        }
        response = self.client.post('/bugs/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_bugs(self):
        self.create_n_bugs(3)

        response = self.client.get('/bugs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_bugs_with_resolved_status(self):
        self.create_n_bugs(3)
        Bug.objects.create(
            title='Resolved bug',
            description='Resolved description',
            status=Bug.Status.RESOLVED,
        )

        response = self.client.get('/bugs/?status=resolved')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Resolved bug')
        self.assertEqual(response.data[0]['status'], Bug.Status.RESOLVED)

    def test_list_bugs_with_unresolved_status(self):
        self.create_n_bugs(3)
        Bug.objects.create(
            title='Resolved bug',
            description='Resolved description',
            status=Bug.Status.RESOLVED,
        )

        response = self.client.get('/bugs/?status=unresolved')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['title'], 'Test bug 0')
        self.assertEqual(response.data[1]['status'], Bug.Status.UNRESOLVED)
        self.assertEqual(response.data[1]['title'], 'Test bug 1')
        self.assertEqual(response.data[2]['status'], Bug.Status.UNRESOLVED)
        self.assertEqual(response.data[2]['title'], 'Test bug 2')
        self.assertEqual(response.data[0]['status'], Bug.Status.UNRESOLVED)

    def test_list_bugs_with_invalid_status(self):
        response = self.client.get('/bugs/?status=invalid')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BugDetailTestCase(APITestCase):
    def test_get_bug(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )

        response = self.client.get(f'/bugs/{bug.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test bug')
        self.assertEqual(response.data['description'], 'Test description')
        self.assertEqual(response.data['status'], Bug.Status.UNRESOLVED)

    def test_get_bug_not_found(self):
        response = self.client.get('/bugs/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_bug(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )

        response = self.client.delete(f'/bugs/{bug.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Bug.objects.count(), 0)

    def test_delete_bug_not_found(self):
        response = self.client.delete('/bugs/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_bug(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )

        data = {
            'title': 'Test bug edited',
            'description': 'Test description edited',
            'status': Bug.Status.RESOLVED,
        }
        response = self.client.patch(f'/bugs/{bug.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test bug edited')
        self.assertEqual(response.data['description'], 'Test description edited')
        self.assertEqual(response.data['status'], Bug.Status.RESOLVED)

    def test_partial_update_bug(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )

        data = {
            'title': 'Test bug edited',
        }
        response = self.client.patch(f'/bugs/{bug.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test bug edited')
        self.assertEqual(response.data['description'], 'Test description')
        self.assertEqual(response.data['status'], Bug.Status.UNRESOLVED)

    def test_update_bug_invalid_status(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )

        data = {
            'title': 'Test bug edited',
            'description': 'Test description edited',
            'status': 'invalid',
        }
        response = self.client.patch(f'/bugs/{bug.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_bug_not_found(self):
        data = {
            'title': 'Test bug edited',
            'description': 'Test description edited',
            'status': Bug.Status.RESOLVED,
        }
        response = self.client.patch('/bugs/1/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BugAssignTestCase(APITestCase):
    def test_assign_bug(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )
        assignee_id = '123'
        data = {
            'assignee_id': assignee_id,
        }

        response = self.client.patch(f'/bugs/{bug.id}/assign/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['assignee_id'], assignee_id)

    def test_assign_to_not_found_bug(self):
        assignee_id = '123'
        data = {
            'assignee_id': assignee_id,
        }

        response = self.client.patch(f'/bugs/1/assign/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BugResolveTestCase(APITestCase):
    def test_resolve_bug(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )
        data = {
            'status': Bug.Status.RESOLVED,
        }

        response = self.client.patch(f'/bugs/{bug.id}/resolve/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], Bug.Status.RESOLVED)

    def test_resolve_not_found_bug(self):
        response = self.client.patch(f'/bugs/1/resolve/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentCreateTestCase(APITestCase):
    def test_create_comment(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )
        data = {
            'title': 'Test comment',
            'body': 'Test body',
        }

        response = self.client.post(f'/bugs/{bug.id}/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test comment')
        self.assertEqual(response.data['body'], 'Test body')
        self.assertEqual(response.data['bug'], bug.id)

    def test_create_comment_invalid_bug(self):
        data = {
            'title': 'Test comment',
            'body': 'Test body',
        }

        response = self.client.post('/bugs/1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentRetrieveDeleteTestCase(APITestCase):
    def test_retrieve_comment(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )
        comment = Comment.objects.create(
            title='Test comment',
            body='Test body',
            bug=bug,
        )

        response = self.client.get(f'/bugs/{bug.id}/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test comment')
        self.assertEqual(response.data['body'], 'Test body')
        self.assertEqual(response.data['bug'], bug.id)

    def test_retrieve_comment_not_found(self):
        response = self.client.get('/bugs/1/comments/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_comment(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )
        comment = Comment.objects.create(
            title='Test comment',
            body='Test body',
            bug=bug,
        )

        response = self.client.delete(f'/bugs/{bug.id}/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_not_found(self):
        response = self.client.delete('/bugs/1/comments/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_comment_invalid_bug(self):
        bug = Bug.objects.create(
            title='Test bug',
            description='Test description',
            status=Bug.Status.UNRESOLVED,
        )
        comment = Comment.objects.create(
            title='Test comment',
            body='Test body',
            bug=bug,
        )

        response = self.client.delete(f'/bugs/123/comments/{comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
