#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import string
import os.path
import tornado.web
import tornado.template

from settings import *
from libs.utils import *
from libs.models import *
from libs.handler import *

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            ("/", HomeHandler),
            ("/admin", AdminHandler),
            ("/login", LoginHandler),
            ("/logout", LogoutHandler),
            ("/tags", TagHandler),
            ("/articles", ArticleHandler),
            ("/page/([\d]+)", PageHandler),
            ("/admin/edit/new/page", NewPageHandler),
            ("/admin/edit/new/article", NewArticleHandler),
            ("/admin/edit/article/([\d]+)", EditArticleHandler),
            ("/admin/edit/delete/article/([\d]+)", DelArticleHandler),
        ]
        settings = dict(
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            autoescape=None,
            blog_name = blog_name,
            blog_url = blog_url,
            cookie_secret = cookie_secret,
            login_url = "/login",
            debug = DeBug
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class HomeHandler(BaseHandler):
    def get(self):
        self.render("home.html",
            title = blog_name,
            articlesList = get_articles(1),
            page = 1,
            count = get_article_count(),
            )

class PageHandler(BaseHandler):
    def get(self, page):
        self.render("home.html",
            title = blog_name,
            articlesList = get_articles(int(page)),
            page = int(page),
            count = get_article_count(),
            )

class ArticleHandler(BaseHandler):
    def get(self):
        pass

class TagHandler(BaseHandler):
    def get(self):
        pass

class LoginHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            if verify_token(self.get_current_user(), self.get_secure_cookie("token")):
                self.redirect("/admin")
                return
            else:
                self.render("login.html",
                    title = blog_name,
                    )
        else:
            self.render("login.html",
                title = blog_name,
                )

    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        if login_username == username:
            if verify_user(username, to_md5(password)):
                token = make_token(username)
                update_token(username, token)
                self.set_secure_cookie("token", token)
                self.set_secure_cookie("username", username)
                self.redirect("/admin")
                return
            else:
                self.redirect("/login")
        else:
            self.redirect("/login")

class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect("/")
        self.clear_cookie("username")
        self.clear_cookie("token")
        self.redirect("/")

class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("admin.html",
            title = blog_name + " | Admin",
            blog_author = blog_author,
            articlesList = get_all_articles(),
            )

class NewPageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pass

class NewArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("editor.html",
            title = blog_name + " | New",
            new = True,
            )

    def post(self):
        title = self.get_argument("title", None)
        content = self.get_argument("content", None)
        creat_article(title = title, content = content)
        self.redirect("/")

class EditArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, article_id):
        self.render("editor.html",
            title = blog_name + " | Edit",
            new = False,
            article = get_article(article_id),
            )
    
    def post(self, article_id):
        title = self.get_argument("title", None)
        content = self.get_argument("content", None)
        if update_article(int(article_id), title = title, content = content):
            self.redirect("/")

class DelArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, article_id):
        if delete_article(article_id):
            self.redirect("/")
