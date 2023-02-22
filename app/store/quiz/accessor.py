from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Answer,
    Question,
    Theme, ThemeModel, AnswerModel, QuestionModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        async with self.app.database.session.begin() as sess:
            theme = ThemeModel(title=title)
            sess.add(theme)
            await sess.commit()
            return theme.to_data()

    async def get_theme_by_title(self, title: str) -> Theme | None:
        async with self.app.database.session.begin() as sess:
            q = select(ThemeModel).where(ThemeModel.title == title)
            result = await sess.execute(q)
            theme = result.scalars().first()
            if theme:
                return theme.to_data()

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        async with self.app.database.session.begin() as sess:
            q = select(ThemeModel).where(ThemeModel.id == id_)
            result = await sess.execute(q)
            theme = result.scalars().first()
            if theme:
                return theme.to_data()

    async def list_themes(self) -> list[Theme]:
        async with self.app.database.session.begin() as sess:
            q = select(ThemeModel)
            result = await sess.execute(q)
            themes = result.scalars().all()
            return [theme.to_data() for theme in themes]

    async def create_answers(
        self, question_id: int, answers: list[Answer]
    ) -> list[Answer]:
        pass

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        async with self.app.database.session.begin() as sess:
            try:
                answers = [AnswerModel(title=answer.title, is_correct=answer.is_correct) for answer in answers]
            except AttributeError:
                answers = [AnswerModel(title=answer['title'], is_correct=answer['is_correct']) for answer in answers]
            question = QuestionModel(title=title, theme_id=theme_id, answers=answers)
            sess.add(question)
            await sess.commit()
            return question.to_data()

    async def get_question_by_title(self, title: str) -> Question | None:
        async with self.app.database.session.begin() as sess:
            q = select(QuestionModel).where(QuestionModel.title == title).options(selectinload(QuestionModel.answers))
            result = await sess.execute(q)
            question = result.scalars().first()
            if question:
                return question.to_data()

    async def list_questions(self, theme_id: int | None = None) -> list[Question]:
        async with self.app.database.session.begin() as sess:
            if theme_id:
                q = select(QuestionModel).where(QuestionModel.theme_id == theme_id)
            else:
                q = select(QuestionModel)
            result = await sess.execute(q.options(selectinload(QuestionModel.answers)))
            questions = result.scalars().all()
            for _ in questions:
                return [question.to_data() for question in questions]
