import flask_praetorian
from flask import Flask, render_template, jsonify, request, \
                  redirect, url_for, send_from_directory, session, \
                  abort

from sqlalchemy import desc, select


from flask_restx import abort, Resource, Namespace

import app
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
        datos = request.json

        # TODO: Imagen player y team
        #datos["imagen"].save(app.root_path + "/imagenes/" + datos["imagen"].filename)

        #datos["imagen"] = app.root_path + "/imagenes/" + datos["imagen"].filename
        player = PlayerSchema().load(datos)
        db.session.add(player)
        db.session.commit()
        return PlayerSchema().dump(player), 201

@api_player.route("/points/<player_id>")
class PlayerController(Resource):
    @flask_praetorian.auth_required
    def get(self, player_id):
        player = Player.query.get_or_404(player_id)
        return player.puntos

    @flask_praetorian.auth_required
    def post(self, player_id):
        datos = request.json
        player = Player.query.get_or_404(player_id)
        player.puntos += datos["clicks"]
        db.session.commit()
        return 201

@api_player.route("/points/")
class PlayerListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        result = session.execute(select(puntos))
        return result.scalars
        #return PlayerSchema(many=True).dump(Player.query.order_by(desc(Player.puntos)).all())
