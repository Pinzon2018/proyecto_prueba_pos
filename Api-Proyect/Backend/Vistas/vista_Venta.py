from flask_restful import Resource
from ..Modelos import db, Venta, VentaSchema, Producto, Detalle_Venta, Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request

Venta_schema = VentaSchema(many=True)
venta_individual_schema = VentaSchema()

class VistaVenta(Resource):
    @jwt_required()
    def get(self):
        ventas = Venta.query.all()
        return Venta_schema.dump(ventas), 200 

    @jwt_required()
    def post(self):
        detalle_Venta = request.json.get('detalle_Venta', [])
        total = 0

        usuario_id = get_jwt_identity()
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404

        nueva_venta = Venta(FK_Id_Usuario=usuario.Id_Usuario)
        db.session.add(nueva_venta)
        db.session.flush() 

        for item in detalle_Venta:
            producto = Producto.query.get(item['FK_Id_Producto'])
            cantidad = int(item['Cantidad'])

            if producto and producto.Unidades_Totales_Prod is not None and producto.Unidades_Totales_Prod >= cantidad:
                subtotal = float(producto.Precio_Neto_Unidad_Prod) * cantidad
                total += subtotal
                producto.Unidades_Totales_Prod -= cantidad
                detalle = Detalle_Venta(
                    FK_Id_Venta=nueva_venta.Id_Venta,
                    FK_Id_Producto=producto.Id_Producto,
                    Cantidad=cantidad,
                    precio_unitario=producto.Precio_Neto_Unidad_Prod
                )
                db.session.add(detalle)
            else:
                return {'error': f"Sin stock para {producto.Nombre_Prod if producto else 'producto desconocido'}"}, 400

        nueva_venta.Total_Venta = total
        db.session.commit()
        return venta_individual_schema.dump(nueva_venta), 201
    
    @jwt_required()
    def delete(self, Id_Venta):
        current_user = get_jwt_identity()
        venta = Venta.query.get_or_404(Id_Venta) 
        db.session.delete(venta) 
        db.session.commit() 
        return 'Se elimino la venta exitosamente!.',204 
