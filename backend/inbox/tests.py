from django.urls import include, path, reverse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase
from authors.models import Author
from posts.models import Post
from .models import Inbox
from django.core.exceptions import ValidationError


class InboxTests(APITestCase, URLPatternsTestCase):

    test_author1_data = {"displayName":"Lara Croft",
                        "github":"http://github.com/laracroft",
                        "profileImage":"https://i.imgur.com/k7XVwpB.jpeg"}
    
    test_author2_data = {"displayName":"Spongebob Squarepants",
                        "github":"http://github.com/spongebro",
                        "profileImage":"https://i.imgur.com/k7XVwpB.jpeg"}
    
    test_post1_data = {"title": "test title",
        "source": "http://lastplaceigotthisfrom.com/posts/yyyyy",
        "origin":"http://whereitcamefrom.com/posts/zzzzz",
        "description":"This post discusses stuff -- brief",
        "contentType":"text/plain",
        "content":"test_content"}
    
    urlpatterns = [
        path('', include('authors.urls')),
        path('', include('inbox.urls')),
        path('', include('posts.urls')),
    ]

    def get_post_list_url(self, id):
        return reverse("post_list", args=[id])
    
    def get_post_detail_url(self,author_id,post_id):
        return reverse("post_detail", args=[author_id, post_id])

    def get_author_list_url(self):
        return reverse("author_list")
    
    def get_author_detail_url(self,id):
        return reverse("author_detail", args=[id])

    def get_inbox_list_url(self,id):
        """id is author.id """
        return reverse("inbox_list", args=[id])
    

    def post_and_authorize_an_author(self, author_data):
        """POST author will be tested, but this method prevents redundant code."""
        # post the author
        response = self.client.post(self.get_author_list_url(), author_data, format='json')
        # ensure the proper response code is returned
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id = response.data["id"]
        author = get_object_or_404(Author, id=id)
        # authorize the author
        author.isAuthorized = True
        author.save()
        return id
    
    def post_a_post(self, post_data: dict) -> tuple:
        """
        Helper method for adding a post to the db
        Returns (author_id, post_id)
        """
        author_id = self.post_and_authorize_an_author(self.test_author1_data)
        # post the post
        response = self.client.post(self.get_post_list_url(author_id), post_data, format='json')
        # ensure the proper response code is given
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post_id = response.data["id"]
        return author_id, post_id

        
    def test_get_inbox_results_for_unauthorized_author(self):
        """Test getting posts for unauthorized author"""
        # post the author (but don't validate)
        response = self.client.post(self.get_author_list_url(), self.test_author1_data, format='json')
        author_id = response.data["id"]
        # get posts from the author's inbox
        response = self.client.get(self.get_inbox_list_url(author_id), format='json')
        # ensure the proper response code is given
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_get_all_data_from_empty_inbox_for_authorized_user(self):
        """Test getting posts for an author when there are no posts in inbox"""
        author_id = self.post_and_authorize_an_author(self.test_author1_data)
        # get posts from inbox
        response = self.client.get(self.get_inbox_list_url(author_id), format='json')
        # ensure the proper response code is given
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ensure the correct data is returned
        keys_arr = ['type', 'author', 'items']
        for key in keys_arr:
            assert(key in list(response.data.keys()))
        self.assertEqual(response.data['type'],"inbox")
        self.assertEqual(response.data['author'],author_id)
        self.assertEqual(len(response.data['items']),0)

        
    def test_post_a_post_and_get_post_from_inbox(self):
        """Test GET from inbox after post is posted"""
        # create an author and get them to post a post
        author_id, post_id = self.post_a_post(self.test_post1_data)
        # get posts from inbox
        response = self.client.get(self.get_inbox_list_url(author_id), format='json')
        # ensure the proper response code is given
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        inbox_items = response.data['items']
        # ensure there is one inbox_item
        self.assertEqual(len(inbox_items), 1)
        # ensure the inbox post matches the posted post
        for key in self.test_author1_data.keys():
            if key in inbox_items[0].keys():
                self.assertEqual(inbox_items[0][key], self.test_author1_data[key])
    

    def test_send_a_follow_request_and_get_from_inbox(self):
        """Test sending a post to an author's inbox then check the inbox contents"""
        # post an author
        author1_id = self.post_and_authorize_an_author(self.test_author1_data)
        # post another author
        author2_id = self.post_and_authorize_an_author(self.test_author2_data)
        # send a follow request from author2 to author1
        url = self.get_inbox_list_url(author1_id)
        response = self.client.post(url, {"id":author2_id}, format='json')
        # ensure the proper response code is returned
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # get posts from inbox
        response = self.client.get(self.get_inbox_list_url(author1_id), format='json')
        # ensure the proper response code is returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ensure the proper author id is returned
        self.assertEqual(response.data["author"],author1_id)
        # ensure there is 1 item in items
        items = response.data["items"]
        self.assertEqual(len(items),1)





        # id = response.data["id"]
        # get the post from the author's inbox
        # response = self.client.get(self.get_inbox_list_url(author_id), self.test_post1_data, format="json")
        # # ensure the proper response is given
        # self.assertEqual(response.status_code, status.HTTP_200_OK)





    



        #response = self.client.post(self.get_post_list_url(author_id), post_data, format='json')




        # ensure the proper response code is given
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 2)
    #     self.assertEqual(response.data["type"], "authors")
    #     self.assertEqual(type(response.data["items"]), list)
    #     self.assertEqual(len(response.data["items"]), 0)

        
    #     """Ensure {'type': 'authors', 'items': []} is returned when no authors are in db."""
        
    # def test_post_new_author(self):
    #     """Ensure an author object is properly added to the db"""
    #     # post the author
    #     response = self.client.post(self.get_author_list_url(), self.test_author1_data, format='json')
    #     # ensure the proper response code is returned
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # ensure the id for the posted author was returned
    #     assert("id" in response.data.keys())
    #     # ensure id is correct type
    #     self.assertEqual(type(response.data["id"]), str)
    #     # get all authors from db
    #     response = self.client.get(self.get_author_list_url(), format='json')
    #     # ensure the proper response code is given
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # ensure there is now one author in the db
    #     self.assertEqual(len(response.data["items"]), 1)

  
    # def test_get_posted_author_by_id(self):
    #     # post the author
    #     response = self.client.post(self.get_author_list_url(), self.test_author1_data, format='json')
    #     # ensure the proper response code is returned
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # ensure the id for the posted author was returned
    #     assert("id" in response.data.keys())
    #     id = response.data["id"]
    #     url = self.get_author_detail_url(id)
    #     # try to get the author with specified id
    #     response = self.client.get(url, format='json')
    #     # ensure the proper response code is given
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.data
    #     # ensure the data properly corresponds with self.test_author1_data
    #     for k in self.test_author1_data.keys():
    #         self.assertEqual(self.test_author1_data[k], response.data[k])
    #     # ensure "id" is in response.data is in correctly edited format
    #     correct_id = self.get_full_path_for_test(id)
    #     self.assertEqual(correct_id, response.data["id"])
    #     # ensure url is same as id
    #     self.assertEqual(response.data["url"], response.data["id"])

    #     # assert the object with id==id now exists
    #     assert((type(get_object_or_404(Author, id=id)) == Author))
    #     # get the existing object
    #     author = get_object_or_404(Author, id=id)
    #     # ensure the attributes match those of self.test_author1_data
    #     for k in self.test_author1_data.keys():
    #         self.assertEqual(self.test_author1_data[k], getattr(author,k))


    # def test_get_followers_for_author_with_no_followers(self):
    #     """Ensure {"type": "followers", "items": []} is returned for author with no followers."""
    #     # post an author and get there id
    #     author_id = self.post_author(self.test_author1_data)
    #     # get url to enable to get all of this authors followers
    #     url = self.get_follower_list_url(author_id)
    #     response = self.client.get(url, format='json')
    #     # ensure the proper response code is given
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 2)
    #     # assert proper "type" value
    #     self.assertEqual(response.data["type"], "followers")
    #     # assert followers size is 0
    #     self.assertEqual(len(response.data["items"]), 0)

    # def test_add_follower_for_author(self):
    #     """Test that an author is being properly added as follower of another author"""

    #     # ensure that Follower is initally empty
    #     self.assertEqual(len(Follower.objects.all()),0)
    #     # post an author and get there id
    #     author1_id = self.post_author(self.test_author1_data)
    #     # post another author and get there id
    #     author2_id = self.post_author(self.test_author2_data)
    #     # ensure author has no followers to start
    #     author1 = get_object_or_404(Author, id=author1_id)
    #     followers = author1.followers.all()
    #     self.assertEqual(len(followers),0)

    #     # try to PUT author2 as a follower of author1
    #     url = self.get_follower_detail_url(author1_id, author2_id)
    #     response = self.client.put(url, format='json')
    #     # ensure the proper response code is given
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # ensure author1 now has a follower
    #     followers = author1.followers.all()
    #     self.assertEqual(len(followers),1)
    #     # ensure that author2 is the follower
    #     author2 = get_object_or_404(Author, id=author2_id)
    #     self.assertEqual(followers[0], author2)
    #     # ensure that author1 is not a follower of author2
    #     followers = author2.followers.all()
    #     self.assertEqual(len(followers),0)

    #     # ensure that Follower now has an entry
    #     self.assertEqual(len(Follower.objects.all()),1)
    #     # ensure the follower object has the right data
    #     follower_obj = Follower.objects.all()[0]
    #     self.assertEqual(getattr(follower_obj, "author"), author1)
    #     self.assertEqual(getattr(follower_obj, "follower"), author2)
    #     self.assertEqual(getattr(follower_obj, "isAccepted"), False)


    # def test_set_author_as_follower_of_self(self):
    #     """Ensure that an author cannot follow themself"""
    #     # post an author and get there id
    #     author1_id = self.post_author(self.test_author1_data)
    #     # try to set author as follower of themself
    #     url = self.get_follower_detail_url(author1_id, author1_id)
    #     # Should raise validation error
    #     with self.assertRaises(ValidationError):
    #         self.client.put(url, format='json')

    # def test_delete_an_existing_follower(self):
    #     # Start by adding one author as a follower of another
    #     # post an author and get there id
    #     author1_id = self.post_author(self.test_author1_data)
    #     # post another author and get there id
    #     author2_id = self.post_author(self.test_author2_data)
    #     # ensure author has no followers to start
    #     author1 = get_object_or_404(Author, id=author1_id)
    #     followers = author1.followers.all()
    #     self.assertEqual(len(followers),0)
    #     # try to PUT author2 as a follower of author1
    #     url = self.get_follower_detail_url(author1_id, author2_id)
    #     response = self.client.put(url, format='json')
    #     # ensure the proper response code is given
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # ensure author1 now has a follower
    #     followers = author1.followers.all()
    #     self.assertEqual(len(followers),1)
    #     # assert the Follower table now has 1 entry
    #     self.assertEqual(len(Follower.objects.all()),1)
    #     # ensure that author2 is the follower
    #     author2 = get_object_or_404(Author, id=author2_id)
    #     self.assertEqual(followers[0], author2)
    #     # delete author2 as a follower of author1
    #     response = self.client.delete(url, format='json')
    #     # ensure the proper response code is given
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # ensure that author1 once again has no followers
    #     followers = author1.followers.all()
    #     self.assertEqual(len(followers),0)
    #     # ensure the Follower table is now empty
    #     self.assertEqual(len(Follower.objects.all()),0)
        