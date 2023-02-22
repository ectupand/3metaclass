from hashlib import sha256

from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session
from sqlalchemy import select

from app.admin.models import AdminModel
from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = self.request['data']
        admin = await self.store.admins.get_by_email(email=data['email'])
        if admin:
            if admin.password == sha256(self.data['password'].encode()).hexdigest():
                session = await new_session(request=self.request)
                session['admin'] = AdminSchema().dump(admin)
                return json_response(AdminSchema().dump(admin))
        raise HTTPForbidden


class AdminCurrentView(View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
