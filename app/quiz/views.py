from aiohttp.web_exceptions import HTTPUnauthorized, HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp_apispec import querystring_schema, request_schema, response_schema
from aiohttp_session import get_session
from sqlalchemy import select

from app.quiz.models import ThemeModel
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


async def is_authorized(request):
    if await get_session(request=request):
        return
    raise HTTPUnauthorized


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        await is_authorized(self.request)

        title = self.data['title']
        if await self.store.quizzes.get_theme_by_title(title):
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema)
    async def get(self):
        await is_authorized(self.request)

        themes = await self.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(theme) for theme in themes]
        return json_response(data={"themes": raw_themes})


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        await is_authorized(self.request)

        data = self.request['data']
        await self.question_validation(data)
        question = await self.store.quizzes.create_question(
            title=data['title'],
            theme_id=data['theme_id'],
            answers=data['answers']
        )
        return json_response(data=QuestionSchema().dump(question))

    async def question_validation(self, data):
        if not await self.store.quizzes.get_theme_by_id(data['theme_id']):
            raise HTTPNotFound
        if await self.store.quizzes.get_question_by_title(data['title']):
            raise HTTPConflict
        if sum([answer['is_correct'] for answer in data['answers']]) != 1:
            raise HTTPBadRequest
        if len(data['answers']) < 2:
            raise HTTPBadRequest


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        await is_authorized(self.request)

        try:
            theme_id = int(self.request.query['theme_id'])
        except:
            theme_id = False
        if theme_id:
            questions = await self.store.quizzes.list_questions_by_theme(theme_id=theme_id)
            raw_questions = [QuestionSchema().dump(question) for question in questions]
            return json_response(data={"questions": raw_questions})

        questions = await self.store.quizzes.list_questions()
        try:
            raw_questions = [QuestionSchema().dump(question) for question in questions]
        except TypeError:
            return json_response(data={"questions": []})
        return json_response(data={"questions": raw_questions})
