import json

import flask_praetorian
import sqlalchemy
from flask import request, jsonify
from flask_restx import abort, Resource, Namespace

from model import Region, db, RegionSchema

# namespace declaration
api_region = Namespace("Regions", "Regions management")

# Controller detailed comments in: users.py

@api_region.route("/<region_id>")
class RegionController(Resource):
    @flask_praetorian.auth_required
    def get(self, region_id):
        region = Region.query.get_or_404(region_id)
        return RegionSchema().dump(region)

    # roles accepted (user with one of these roles)
    @flask_praetorian.roles_accepted("admin", "editor")
    def delete(self, region_id):
        region = Region.query.get_or_404(region_id)
        db.session.delete(region)
        db.session.commit()
        return f"Deleted region {region_id}", 204

    @flask_praetorian.roles_accepted("admin", "editor")
    def put(self, region_id):
        new_region = RegionSchema().load(request.json)
        if str(new_region.id) != region_id:
            abort(400, "id mismatch")
        db.session.commit()
        return RegionSchema().dump(new_region)


@api_region.route("/")
class RegionListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        return RegionSchema(many=True).dump(Region.query.all())

    @flask_praetorian.roles_accepted("admin", "editor")
    def post(self):
        region = RegionSchema().load(request.json)
        db.session.add(region)
        db.session.commit()
        return RegionSchema().dump(region), 201

# TODO: Dump query to json
@api_region.route("/points/<region_id>")
class RegionController(Resource):
    @flask_praetorian.auth_required
    def get(self, region_id):
        query = sqlalchemy.text('SELECT r.name, SUM(p.puntos) AS puntos FROM player p INNER JOIN location l ON l.id = p.location_id INNER JOIN region r ON r.id = l.region_id WHERE r.id = ' + region_id + ' GROUP BY r.name')
        result = db.session.execute(query)
        return jsonify({r['name'] : r['puntos'] for r in result})

@api_region.route("/points/")
class RegionListController(Resource):
    @flask_praetorian.auth_required
    def get(self):
        query = sqlalchemy.text('SELECT r.name, SUM(p.puntos) AS puntos FROM player p INNER JOIN location l ON l.id = p.location_id INNER JOIN region r ON r.id = l.region_id GROUP BY r.name ORDER BY SUM(p.puntos) desc')
        result = db.session.execute(query)
        return jsonify({r['name'] : r['puntos'] for r in result})

