"""Tests for notes app"""

from datetime import date, datetime, timedelta
from time import sleep

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Note


def create_test_user(username="test_user", password="password"):
    """Creates a test user"""
    return User.objects.create_user(username=username, password=password)


def create_test_note(
    title="Test note",
    note_type="To do",
    deadline=date.today().strftime("%Y-%m-%d"),
    weight="Normal",
    is_complete=False,
    user=None,
):
    """Creates a test note with user and optional category and reminder"""
    return Note.objects.create(
        title=title,
        desc="Test text",
        user=(user or create_test_user()),
        type=note_type,
        isComplete=is_complete,
        deadline=deadline,
        weight=weight,
    )


class NoteModelTest(TestCase):
    """Tests NoteModel"""

    def test_note_model_save_and_retrieve_data(self):
        """Tests that NoteModel save and retrieve data"""
        note = create_test_note()

        all_notes = Note.objects.all()
        self.assertEqual(len(all_notes), 1)

        self.assertEqual(note.type, "To do")
        self.assertEqual(note.title, "Test note")
        self.assertEqual(note.desc, "Test text")
        self.assertEqual(note.isComplete, False)
        self.assertEqual(note.weight, "Normal")
        self.assertEqual(note.deadline, date.today().strftime("%Y-%m-%d"))


class NoteCreateViewTestCase(TestCase):
    """Tests NoteCreateView"""

    def test_redirect_if_user_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        resp = self.client.get("/notes/note-create/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_user_logged_in_with_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        create_test_user()
        self.client.login(username="test_user1", password="12345")
        resp = self.client.get("/notes/note-create/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_create_new_entry_when_user_logged_in(self):
        """Test that authorized user can see Note Create page"""
        create_test_user()
        self.client.login(username="test_user", password="password")
        response = self.client.get("/notes/note-create/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/templates/notes/note_create_form.html")

    def test_create_view_save_data(self):
        """
        Test that the new entry is created and saved to the database
        when user is logged in when NoteCreateView is used
        """
        create_test_user()
        self.client.login(username="test_user", password="password")
        new_note = {
            "title": "New title",
            "desc": "Test text",
            "type": "Note",
            "isComplete": False,
            "deadline": "2023-12-14",
            "weight": "Normal",
        }
        self.client.post("/notes/note-create/", data=new_note)

        notes = Note.objects.all()
        note = Note.objects.get(title='New title')
        self.assertEqual(len(notes), 1)
        self.assertEqual(note.user.username, "test_user")
        self.assertEqual(note.title, "New title")
        self.assertEqual(note.desc, "Test text")
        self.assertEqual(note.type, "Note")
        self.assertEqual(note.isComplete, False)
        self.assertEqual(note.deadline, date(2023, 12, 14))
        self.assertEqual(note.weight, "Normal")

    def test_redirect_after_creation_note(self):
        """
        Test that the user will be redirected to the previous page after creating a new entry
        """
        create_test_user()
        self.client.login(username="test_user", password="password")
        new_note = {
            "title": "New title",
            "desc": "Test text",
            "type": "Note",
            "isComplete": False,
            "deadline": "2023-12-14",
            "weight": "Normal",
        }
        resp = self.client.post("/notes/note-create/?next=/notes/main/", data=new_note)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/main/"))

        resp = self.client.post(
            "/notes/note-create/?next=/notes/notes/2023-12-14/", data=new_note
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/notes/2023-12-14/"))

        resp = self.client.post("/notes/note-create/?next=/notes/", data=new_note)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/"))

        resp = self.client.post("/notes/note-create/", data=new_note)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.url.startswith(
                f'/notes/notes/2023-12-14/'
            )
        )


class NoteUpdateViewTestCase(TestCase):
    """Test NoteUpdateView"""

    def test_redirect_if_user_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        resp = self.client.get(f"/notes/note-update/{create_test_note().id}/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_user_logged_in_with_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        self.client.login(username="test_user1", password="12345")
        resp = self.client.get(f"/notes/note-update/{create_test_note().id}/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_update_entry_when_user_logged_in(self):
        """Test that authorized user can see Note Update page"""
        note = create_test_note()
        self.client.login(username="test_user", password="password")
        response = self.client.get(f"/notes/note-update/{note.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/templates/notes/note_update_form.html")

    def test_update_view_set_correct_entry(self):
        """
        Test that the changes made to note are saved
        when user is logged in and edit NoteUpdateView is used
        """

        note = create_test_note()
        self.client.login(username="test_user", password="password")
        new_data = {
            "title": "New title",
            "desc": "Test text",
            "type": "Note",
            "isComplete": True,
            "deadline": date.today().strftime("%Y-%m-%d"),
            "weight": "Normal",
        }
        self.client.post(f"/notes/note-update/{note.id}/", data=new_data)

        note = Note.objects.get(id=note.id)

        self.assertEqual(note.user.username, "test_user")
        self.assertEqual(note.title, "New title")
        self.assertEqual(note.desc, "Test text")
        self.assertEqual(note.type, "Note")
        self.assertEqual(note.isComplete, True)
        self.assertEqual(note.deadline, date.today())
        self.assertEqual(note.weight, "Normal")

    def test_redirect_after_creation_note(self):
        """
        Test that the user will be redirected to the previous page after updating the entry
        """
        note = create_test_note()
        self.client.login(username="test_user", password="password")
        new_data = {
            "title": "New title",
            "desc": "Test text",
            "type": "Note",
            "isComplete": True,
            "deadline": date.today().strftime("%Y-%m-%d"),
            "weight": "Normal",
        }
        resp = self.client.post(
            f"/notes/note-update/{note.id}/?next=/notes/main/", data=new_data
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/main/"))

        resp = self.client.post(
            f"/notes/note-update/{note.id}/?next=/notes/notes/2023-12-14/",
            data=new_data,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/notes/2023-12-14/"))

        resp = self.client.post(
            f"/notes/note-update/{note.id}/?next=/notes/", data=new_data
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/"))

        resp = self.client.post(f"/notes/note-update/{note.id}/", data=new_data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.url.startswith(
                f'/notes/notes/{datetime.today().strftime("%Y-%m-%d")}/'
            )
        )


class DeleteNoteViewTestCase(TestCase):
    """Test DeleteView"""

    def test_redirect_if_user_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        resp = self.client.get("/notes/note-delete/1/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_user_logged_in_with_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        create_test_user()
        self.client.login(username="test_user1", password="12345")
        resp = self.client.get("/notes/note-delete/1/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_delete_entry_when_user_logged_in(self):
        """Test that authorized user can see Delete page"""
        note = create_test_note()
        self.client.login(username="test_user", password="password")
        resp = self.client.get(f"/notes/note-delete/{note.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "notes/note_confirm_delete.html")

    def test_delete_view_delete_correct_entry(self):
        """
        Test that DeleteNoteView deletes note correct entry
        """
        note = create_test_note()
        self.client.login(username="test_user", password="password")
        self.client.post(f"/notes/note-delete/{note.id}/")
        self.assertFalse(Note.objects.filter(pk=note.id).exists())

    def test_redirect_after_delete_entry(self):
        """
        Test that the user will be redirected to the previous page after removing an entry
        """
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        note = create_test_note(user=test_user)
        resp = self.client.post(f"/notes/note-delete/{note.id}/?next=/notes/main/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/main/"))

        note = create_test_note(user=test_user)
        resp = self.client.post(
            f"/notes/note-delete/{note.id}/?next=/notes/notes/2023-12-14/"
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/notes/2023-12-14/"))

        note = create_test_note(user=test_user)
        resp = self.client.post(f"/notes/note-delete/{note.id}/?next=/notes/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/notes/"))

        note = create_test_note(user=test_user)
        resp = self.client.post(f"/notes/note-delete/{note.id}/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.url.startswith(
                f'/notes/notes/{datetime.today().strftime("%Y-%m-%d")}/'
            )
        )


class GetDayTestCase(TestCase):
    """Test redirect user to page with entries on target day"""

    def test_redirect_if_user_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        resp = self.client.post(
            "/notes/day/", data={"deadline": datetime.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_user_logged_in_with_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        create_test_user()
        self.client.login(username="test_user1", password="12345")
        resp = self.client.post(
            "/notes/day/", data={"deadline": datetime.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_get_entry_by_day_when_user_logged_in(self):
        """Test that authorized user can get entries by day"""
        create_test_user()
        self.client.login(username="test_user", password="password")
        resp = self.client.post(
            "/notes/day/", data={"deadline": datetime.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.url.startswith(
                f'/notes/notes/{datetime.today().strftime("%Y-%m-%d")}/'
            )
        )

    def test_get_entry_by_day_when_user_logged_in_without_date(self):
        """
        Test that user will be redirected to page with entries by today day
        if date not define in request
        """
        create_test_user()
        self.client.login(username="test_user", password="password")
        resp = self.client.post("/notes/day/", data={})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            resp.url.startswith(
                f'/notes/notes/{datetime.today().strftime("%Y-%m-%d")}/'
            )
        )


class NoteDetailsViewTestCase(TestCase):
    """Tests NoteDetailView"""

    def test_redirect_if_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        note = create_test_note()
        resp = self.client.get(f"/notes/note/{note.id}/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        test_user = create_test_user()
        note = create_test_note(user=test_user)
        self.client.login(username="test_user1", password="12345")
        resp = self.client.get(f"/notes/note/{note.id}/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_note_details_when_user_logged_in(self):
        """Test that authorized user can see Note Details page"""
        test_user = create_test_user()
        note = create_test_note(user=test_user)
        self.client.login(username="test_user", password="password")
        response = self.client.get(f"/notes/note/{note.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note.html")

    def test_note_detail_view_show_correct_data(self):
        """Tests that NoteDetailView show entries with correct data"""
        note = create_test_note()
        self.client.login(username="test_user", password="password")
        response = self.client.get(f"/notes/note/{note.id}/")
        self.assertEqual(response.status_code, 200)

        html = response.content.decode("utf8")
        self.assertIn(note.title, html)
        self.assertIn(note.desc, html)
        self.assertIn(note.weight, html)

    def test_go_back_button_redirect_url(self):
        """
        Test that the user will be redirected to the previous page after click on 'Go Back'
        """
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        note = create_test_note(user=test_user)

        resp = self.client.get(f"/notes/note/{note.id}/?next=/notes/main/")
        self.assertEqual(resp.context_data["back_to_url"], "/notes/main/")

        resp = self.client.get(f"/notes/note/{note.id}/?next=/notes/notes/2023-12-14/")
        self.assertEqual(resp.context_data["back_to_url"], "/notes/notes/2023-12-14/")

        resp = self.client.get(f"/notes/note/{note.id}/?next=/notes/")
        self.assertEqual(resp.context_data["back_to_url"], "/notes/")


class NotesListViewTestCase(TestCase):
    """Tests NoteListView"""

    def test_redirect_if_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        resp = self.client.get("/notes/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        create_test_user()
        self.client.login(username="test_user1", password="12345")
        resp = self.client.get("/notes/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_get_note_list_when_user_logged_in(self):
        """Test that not authorized user can see Journal page"""
        create_test_user()
        self.client.login(username="test_user", password="password")
        resp = self.client.get("/notes/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "notes/note_list.html")

    def test_note_list_displays_only_notes(self):
        """Tests that NoteListView show entries with type 'Note' only"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(note_type="Note", title="Note Title", user=test_user)
        create_test_note(note_type="To do", title="To do Title", user=test_user)
        create_test_note(note_type="Event", title="Event Title", user=test_user)
        resp = self.client.get("/notes/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertIn("Note Title", html)
        self.assertNotIn("To do Title", html)
        self.assertNotIn("Event Title", html)

    def test_note_list_displays_only_user_notes(self):
        """Tests that NoteListView show user's entries only"""
        test_user_1 = create_test_user()
        test_user_2 = create_test_user(username="test_user_2", password="password_2")
        self.client.login(username="test_user", password="password")
        create_test_note(note_type="Note", title="User 1 Title", user=test_user_1)
        create_test_note(
            note_type="Note", title="User 1 Another Title", user=test_user_1
        )
        self.client.logout()

        self.client.login(username="test_user_2", password="password_2")
        create_test_note(note_type="Note", title="User 2 Title", user=test_user_2)
        resp = self.client.get("/notes/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("User 1 Title", html)
        self.assertNotIn("User 1 Another Title", html)
        self.assertIn("User 2 Title", html)

    def test_notes_page_sort_entries_by_date_correctly(self):
        """Test that entries ordered by creation date correctly"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(note_type="Note", title="Note Title", user=test_user)
        sleep(0.5)
        create_test_note(note_type="Note", title="To do Title", user=test_user)
        sleep(0.5)
        create_test_note(note_type="Note", title="Event Title", user=test_user)
        resp = self.client.get("/notes/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertTrue(html.find("Note Title") > (html.find("To do Title")))
        self.assertTrue(html.find("To do Title") > (html.find("Event Title")))

        # resp = self.client.get("/notes/?sort=-create_at")
        # self.assertEqual(resp.status_code, 200)
        #
        # html = resp.content.decode("utf8")
        # self.assertTrue(html.find("Note Title") < (html.find("To do Title")))
        # self.assertTrue(html.find("To do Title") < (html.find("Event Title")))

    def test_notes_list_search_by_title_show_correct_entries(self):
        """Test that search by title returns correct data"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(note_type="Note", title="Note Title", user=test_user)
        create_test_note(note_type="Note", title="Another Title", user=test_user)
        create_test_note(note_type="Note", title="Third Title", user=test_user)
        resp = self.client.get("/notes/?search-area=o")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertIn("Note Title", html)
        self.assertIn("Another Title", html)
        self.assertNotIn("Third Title", html)


class TasksDayListViewTestCase(TestCase):
    """Tests TasksDayListView"""

    def test_redirect_if_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        resp = self.client.get("/notes/notes/2023-12-14/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        create_test_user()
        self.client.login(username="test_user1", password="12345")
        resp = self.client.get("/notes/notes/2023-12-14/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_get_notes_by_day_when_user_logged_in(self):
        """Test that authorized user can see page with entries by target day"""
        create_test_user()
        self.client.login(username="test_user", password="password")
        resp = self.client.get("/notes/notes/2023-12-14/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "notes/templates/notes/tasks_day_list.html")

    def test_tasks_day_list_no_displays_notes(self):
        """Tests that TasksDayList don't show entries with type 'Note'"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="Note", title="Note Title", deadline="2023-12-14", user=test_user
        )
        create_test_note(
            note_type="To do",
            title="To do Title",
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            deadline="2023-12-14",
            user=test_user,
        )
        resp = self.client.get("/notes/notes/2023-12-14/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("Note Title", html)
        self.assertIn("To do Title", html)
        self.assertIn("Event Title", html)

    def test_tasks_day_list_displays_only_user_notes(self):
        """Tests that TasksDayList show user's entries only"""
        test_user_1 = create_test_user()
        test_user_2 = create_test_user(username="test_user_2", password="password_2")
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="User 1 Title",
            deadline="2023-12-14",
            user=test_user_1,
        )
        self.client.logout()

        self.client.login(username="test_user_2", password="password_2")
        create_test_note(
            note_type="Note",
            title="User 2 Another Title",
            deadline="2023-12-14",
            user=test_user_2,
        )
        create_test_note(
            note_type="Event",
            title="User 2 Title",
            deadline="2023-12-14",
            user=test_user_2,
        )
        resp = self.client.get("/notes/notes/2023-12-14/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("User 1 Title", html)
        self.assertNotIn("User 2 Another Title", html)  # this View do not display notes
        self.assertIn("User 2 Title", html)

    def test_tasks_day_list_displays_tasks_by_target_day_only(self):
        """Tests that TasksDayList show entries by target day only"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="To do 1 Title",
            deadline="2023-11-11",
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do 2 Title",
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            deadline="2023-12-14",
            user=test_user,
        )
        resp = self.client.get("/notes/notes/2023-12-14/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("To do 1 Title", html)
        self.assertIn("To do 2 Title", html)  # this View do not display notes
        self.assertIn("Event Title", html)

    def test_tasks_day_list_sort_entries_correctly(self):
        """
        Tests that TasksDayList order entries by status and weight correctly
        Completed task must be shown in bottom, tasks with weight 'High' must be shown on top
        """
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="Note Title",
            weight="High",
            is_complete=True,
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do Title",
            weight="Low",
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            weight="High",
            deadline="2023-12-14",
            user=test_user,
        )
        resp = self.client.get("/notes/notes/2023-12-14/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertTrue(html.find("Event Title") < (html.find("To do Title")))
        self.assertTrue(html.find("To do Title") < (html.find("Note Title")))

    def test_tasks_day_list_search_by_title_show_correct_entries(self):
        """Test that search by title returns correct data"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do", title="Note Title", deadline="2023-12-14", user=test_user
        )
        create_test_note(
            note_type="Event",
            title="Another Title",
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="Third Title",
            deadline="2023-12-14",
            user=test_user,
        )
        resp = self.client.get("/notes/notes/2023-12-14/?search-area=o")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertIn("Note Title", html)
        self.assertIn("Another Title", html)
        self.assertNotIn("Third Title", html)


class TasksAllListViewTestCase(TestCase):
    """Tests TasksAllListView"""

    def test_redirect_if_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        resp = self.client.get("/notes/all/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        create_test_user()
        self.client.login(username="test_user1", password="12345")
        resp = self.client.get("/notes/all/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_get_all_entries_when_user_logged_in(self):
        """Test that authorized user can see page with all entries (excluding Notes)"""
        create_test_user()
        self.client.login(username="test_user", password="password")
        resp = self.client.get("/notes/all/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "notes/templates/notes/tasks_day_list.html")

    def test_tasks_list_no_displays_notes(self):
        """Tests that TasksAllList don't show entries with type 'Note'"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="Note", title="Note Title", deadline="2022-12-14", user=test_user
        )
        create_test_note(
            note_type="To do",
            title="To do Title",
            deadline="2023-10-10",
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            deadline="2018-12-18",
            user=test_user,
        )
        resp = self.client.get("/notes/all/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("Note Title", html)
        self.assertIn("To do Title", html)
        self.assertIn("Event Title", html)

    def test_tasks_list_displays_only_user_notes(self):
        """Tests that TasksAllList show user's entries only"""
        test_user_1 = create_test_user()
        test_user_2 = create_test_user(username="test_user_2", password="password_2")
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="User 1 Title",
            deadline="2023-11-14",
            user=test_user_1,
        )
        self.client.logout()

        self.client.login(username="test_user_2", password="password_2")
        create_test_note(
            note_type="Note",
            title="User 2 Another Title",
            deadline="2022-10-14",
            user=test_user_2,
        )
        create_test_note(
            note_type="Event",
            title="User 2 Title",
            deadline="2023-05-10",
            user=test_user_2,
        )
        resp = self.client.get("/notes/all/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("User 1 Title", html)
        self.assertNotIn("User 2 Another Title", html)  # this View do not display notes
        self.assertIn("User 2 Title", html)

    def test_tasks_list_displays_all_tasks(self):
        """Tests that TasksAllList show all entries (excluding Notes)"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="To do 1 Title",
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do 2 Title",
            deadline="2023-12-10",
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            deadline="2022-12-12",
            user=test_user,
        )
        resp = self.client.get("/notes/all/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertIn("To do 1 Title", html)
        self.assertIn("To do 2 Title", html)  # this View do not display notes
        self.assertIn("Event Title", html)

    def test_tasks_list_sort_entries_correctly(self):
        """
        Tests that TasksAllList order entries by status and weight correctly
        Completed task must be shown in bottom, tasks with weight 'High' must be shown on top
        """
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="To do 1 Title",
            weight="High",
            is_complete=True,
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do 2 Title",
            weight="High",
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do Title",
            weight="Low",
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            weight="High",
            deadline="2022-12-14",
            user=test_user,
        )
        resp = self.client.get("/notes/notes/2023-12-14/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertTrue(html.find("Event Title") < (html.find("To do 2 Title")))
        self.assertTrue(html.find("To do 2 Title") < (html.find("To do Title")))
        self.assertTrue(html.find("To do Title") < (html.find("To do 1 Title")))

    def test_tasks_list_search_by_title_show_correct_entries(self):
        """Test that search by title returns correct data"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do", title="Note Title", deadline="2023-10-10", user=test_user
        )
        create_test_note(
            note_type="Event",
            title="Another Title",
            deadline="2023-12-14",
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="Third Title",
            deadline="2022-11-11",
            user=test_user,
        )
        resp = self.client.get("/notes/all/?search-area=o")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertIn("Note Title", html)
        self.assertIn("Another Title", html)
        self.assertNotIn("Third Title", html)


class MainViewTestCase(TestCase):
    """Tests MainView"""

    def test_redirect_if_not_logged_in(self):
        """Test that not authorized user will be redirected to login page"""
        resp = self.client.get("/notes/main/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        """Test that not authorized user will be redirected to login page"""
        create_test_user()
        self.client.login(username="test_user1", password="12345")
        resp = self.client.get("/notes/main/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/auth/login/"))

    def test_get_notes_by_day_when_user_logged_in(self):
        """Test that authorized user can see main page"""
        create_test_user()
        self.client.login(username="test_user", password="password")
        resp = self.client.get("/notes/main/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "notes/templates/notes/main.html")

    def test_main_view_no_displays_notes(self):
        """Tests that MainView don't show entries with type 'Note'"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="Note",
            title="Note Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        resp = self.client.get("/notes/main/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("Note Title", html)
        self.assertIn("To do Title", html)
        self.assertIn("Event Title", html)

    def test_main_view_no_displays_completed_entries(self):
        """Tests that MainView don't show entries with status isComplete = True"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="To do 1 Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do 2 Title",
            is_complete=True,
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        resp = self.client.get("/notes/main/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("To do 2 Title", html)
        self.assertIn("To do 1 Title", html)
        self.assertIn("Event Title", html)

    def test_main_view_displays_only_user_notes(self):
        """Tests that MainView show user's entries only"""
        test_user_1 = create_test_user()
        test_user_2 = create_test_user(username="test_user_2", password="password_2")
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="User 1 Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user_1,
        )
        self.client.logout()

        self.client.login(username="test_user_2", password="password_2")
        create_test_note(
            note_type="Note",
            title="User 2 Another Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user_2,
        )
        create_test_note(
            note_type="Event",
            title="User 2 Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user_2,
        )
        resp = self.client.get("/notes/main/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("User 1 Title", html)
        self.assertNotIn("User 2 Another Title", html)  # this View do not display notes
        self.assertIn("User 2 Title", html)

    def test_main_view_displays_tasks_by_target_week_only(self):
        """Tests that MainView show entries by target week only"""
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="To do 1 Title",
            deadline=(datetime.today() + timedelta(days=-7)).strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do 2 Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event 1 Title",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event 2 Title",
            deadline=(datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
            user=test_user,
        )
        resp = self.client.get("/notes/main/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertNotIn("To do 1 Title", html)
        self.assertNotIn("Event 2 Title", html)
        self.assertIn("Event 1 Title", html)
        self.assertIn("To do 2 Title", html)  # this View do not display notes

    def test_main_view_sort_entries_correctly(self):
        """
        Tests that MainView order entries by weight correctly.
        Tasks with weight 'High' must be shown on top
        """
        test_user = create_test_user()
        self.client.login(username="test_user", password="password")
        create_test_note(
            note_type="To do",
            title="Note Title",
            weight="High",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="To do",
            title="To do Title",
            weight="Normal",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        create_test_note(
            note_type="Event",
            title="Event Title",
            weight="High",
            deadline=datetime.today().strftime("%Y-%m-%d"),
            user=test_user,
        )
        resp = self.client.get("/notes/main/")
        self.assertEqual(resp.status_code, 200)

        html = resp.content.decode("utf8")
        self.assertTrue(html.find("Note Title") < (html.find("Event Title")))
        self.assertTrue(html.find("Event Title") < (html.find("To do Title")))
