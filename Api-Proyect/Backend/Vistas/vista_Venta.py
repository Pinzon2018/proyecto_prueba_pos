from decimal import Decimal
from flask_restful import Resource
from ..Modelos import db, Venta, VentaSchema, Producto, Detalle_Venta, Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request

venta_individual_schema = VentaSchema()
Venta_schema = VentaSchema(many=True)

class VistaVenta(Resource):
    @jwt_required()
    def get(self):
        ventas = Venta.query.all()
        return Venta_schema.dump(ventas), 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        detalle_Venta = data.get('detalle_Venta', [])
        total = Decimal("0.00")

        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404

        nueva_venta = Venta(FK_Id_Usuario=usuario.Id_Usuario)
        db.session.add(nueva_venta)
        db.session.flush()

        for item in detalle_Venta:
            producto = Producto.query.get(item.get('FK_Id_Producto'))
            try:
                cantidad = int(item.get('Cantidad', 0))
            except (ValueError, TypeError):
                return {'error': 'Cantidad inválida'}, 400

            if not producto:
                return {'error': 'Producto no encontrado'}, 404

            if producto.Unidades_Totales_Prod is None or producto.Unidades_Totales_Prod < cantidad:
                return {'error': f"Sin stock para {producto.Nombre_Prod}"}, 400

            if producto.Precio_Neto_Unidad_Prod is None:
                return {'error': f"Producto {producto.Nombre_Prod} no tiene precio asignado"}, 400

            subtotal = producto.Precio_Neto_Unidad_Prod * cantidad
            total += subtotal
            producto.Unidades_Totales_Prod -= cantidad

            detalle = Detalle_Venta(
                FK_Id_Venta=nueva_venta.Id_Venta,
                FK_Id_Producto=producto.Id_Producto,
                Cantidad=cantidad,
                precio_unitario=producto.Precio_Neto_Unidad_Prod
            )
            db.session.add(detalle)

        nueva_venta.Total_Venta = total
        db.session.commit()

        venta_con_detalles = Venta.query.options(
            db.joinedload(Venta.usuario),
            db.joinedload(Venta.detalle_Venta).joinedload(Detalle_Venta.producto)
        ).get(nueva_venta.Id_Venta)

        return venta_individual_schema.dump(venta_con_detalles), 201

    @jwt_required()
    def delete(self, Id_Venta):
        current_user = get_jwt_identity()
        venta = Venta.query.get_or_404(Id_Venta)
        db.session.delete(venta)
        db.session.commit()
        return 'Se eliminó la venta exitosamente!.', 204