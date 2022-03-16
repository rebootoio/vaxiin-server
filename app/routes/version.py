from http import HTTPStatus
from flask_restplus import Resource, Namespace

from version import VERSION

ns = Namespace('Version', description='Get server version')


@ns.route('/')
class Version(Resource):

    @ns.doc('get server version')
    @ns.response(HTTPStatus.OK, 'Success')
    def get(self):
        return {"version": VERSION}, HTTPStatus.OK
