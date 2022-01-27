import flask_praetorian
from flask import request
from flask_restx import abort, Resource, Namespace

from model import Player, db, PlayerSchema

# namespace declaration
api_player = Namespace("Players", "Player management")

# Controller detailed comments in: users.py


@api_player.route("/<player_id>")
class PlayerController(Resource):
    @flask_praetorian.auth_required
    def get(self, player_id):
        player = Player.query.get_or_404(player_id)
        return PlayerSchema().dump(player)

    @flask_praetorian.roles_accepted("admin", "editor")
    def delete(self, player_id):
        player = Player.query.get_or_404(player_id)
        db.session.delete(player)
        db.session.commit()
        return f"Deleted player {player_id}", 204

    @flask_praetorian.roles_accepted("admin", "editor")
    def put(self, player_id):
        new_player = PlayerSchema().load(request.json)
        if str(new_player.id) != player_id:
            abort(400, "id mismatch")
        db.session.commit()
        return PlayerSchema().dump(new_player)


@api_player.route("/")
class PlayerListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return PlayerSchema(many=True).dump(Player.query.all())

    @flask_praetorian.roles_accepted("admin", "editor")
    def post(self):
        player = PlayerSchema().load(request.json)
        db.session.add(player)
        db.session.commit()
        return PlayerSchema().dump(player), 201
