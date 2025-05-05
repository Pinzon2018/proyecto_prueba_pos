from marshmallow import fields, post_dump
from flask_sqlalchemy import SQLAlchemy
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric
import pytz
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class Rol(db.Model):
    Id_Rol = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(180))      
    usuarios= db.relationship("Usuario", back_populates="rol_rl")

class Proveedor(db.Model): 
    Id_Proveedor = db.Column(db.Integer, primary_key=True)
    Nombre_Prov = db.Column(db.String(180))
    Telefono_Prov = db.Column(db.String(15))  
    Direccion_Prov = db.Column(db.String(50))
    producto= db.relationship("Producto", back_populates="proveedor")
    fecha_Registro_Prod= db.relationship("Fecha_Registro_Prod", back_populates="proveedor")

class Usuario(db.Model):    
    Id_Usuario = db.Column(db.Integer, primary_key=True)
    Nombre_Usu = db.Column(db.String(250))
    Contraseña_hash = db.Column(db.String(255))
    Cedula_Usu = db.Column(db.String(20))
    Email_Usu = db.Column(db.String(250))
    Telefono_Usu = db.Column(db.String(15))
    Fecha_Contrato_Inicio = db.Column(db.Date)
    rol = db.Column(db.Integer, db.ForeignKey('rol.Id_Rol'))
    rol_rl = db.relationship("Rol", back_populates="usuarios")
    venta_Usuario = db.relationship("Venta", back_populates="usuario")
    @property
    def contraseña(self):
        raise AttributeError("La contraseña no es un atributo legible")
    
    @contraseña.setter
    def contraseña(self, password):
        self.Contraseña_hash = generate_password_hash(password)
        
    def verificar_contraseña(self, password):
        return check_password_hash(self.Contraseña_hash, password)

class Categoria(db.Model):   
    Id_Categoria = db.Column(db.Integer, primary_key=True)
    Nombre_Cat = db.Column(db.String(80))
    Descripcion_Cat = db.Column(db.String(150))
    subcategorias = db.relationship("Subcategoria", back_populates="categoria_rl")

class Subcategoria(db.Model):
    Id_Subcategoria = db.Column(db.Integer, primary_key=True)
    Nombre_Subcategoria = db.Column(db.String(250))
    Descripcion_Subcategoria = db.Column(db.String(250))
    categoria = db.Column(db.Integer, db.ForeignKey('categoria.Id_Categoria'))
    categoria_rl = db.relationship("Categoria", back_populates="subcategorias")
    productos = db.relationship("Producto", back_populates="subcategoria")


class Producto(db.Model):  
    Id_Producto = db.Column(db.Integer, primary_key=True, nullable=False)
    Nombre_Prod = db.Column(db.String(100))
    Medida_Prod = db.Column(db.Integer)
    Unidad_Medida_Prod = db.Column(db.String(80))
    Precio_Bruto_Prod = db.Column(Numeric(10, 2))
    Iva_Prod = db.Column(Numeric(5, 2))
    Porcentaje_Ganancia = db.Column(Numeric(5, 2))
    Unidades_Totales_Prod = db.Column(db.Integer)
    Estado_Prod = db.Column(db.String(50))
    Marca_Prod = db.Column(db.String(60))
    Precio_Neto_Unidad_Prod = db.Column(Numeric(10, 2))
    FK_Id_Proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.Id_Proveedor"))
    FK_Id_Subcategoria = db.Column(db.Integer, db.ForeignKey("subcategoria.Id_Subcategoria"))
    proveedor = db.relationship("Proveedor", back_populates="producto")
    subcategoria = db.relationship("Subcategoria", back_populates="productos")
    fecha_Registro_Prod= db.relationship("Fecha_Registro_Prod", back_populates="producto")
    detalle_Venta= db.relationship("Detalle_Venta", back_populates = "producto")

colombia_tz = pytz.timezone('America/Bogota')

class Venta(db.Model):
    Id_Venta = db.Column(db.Integer, primary_key=True)
    Fecha_Venta = db.Column(db.DateTime, default=lambda: datetime.now(colombia_tz))
    Total_Venta = db.Column(db.Numeric(10,2))
    Forma_Pago_Fact = db.Column(db.String(50))
    FK_Id_Usuario = db.Column(db.Integer, db.ForeignKey("usuario.Id_Usuario"))
    usuario = db.relationship("Usuario", back_populates="venta_Usuario")
    detalle_Venta= db.relationship("Detalle_Venta", back_populates = "venta")

class Factura(db.Model):
    Id_Factura = db.Column(db.Integer, primary_key=True)
    Fecha_Generacion_Fact = db.Column(db.DateTime)
    Impuestos_Fact= db.Column(db.Float)
    detalle_Venta= db.relationship("Detalle_Venta", back_populates = "factura")

class Detalle_Venta(db.Model):
    Id_Detalle_Venta = db. Column(db.Integer, primary_key=True)
    Cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Numeric(10,2), nullable=False)
    FK_Id_Venta = db.Column(db.Integer, db.ForeignKey("venta.Id_Venta"))
    FK_Id_Producto = db.Column(db.Integer, db.ForeignKey("producto.Id_Producto"))
    FK_Id_Factura = db.Column(db.Integer, db.ForeignKey("factura.Id_Factura"))
    
    factura= db.relationship("Factura", back_populates = "detalle_Venta")
    producto= db.relationship("Producto", back_populates = "detalle_Venta")
    venta= db.relationship("Venta", back_populates = "detalle_Venta")


class Fecha_Registro_Prod(db.Model):
    Id_Fecha_Registro = db.Column(db.Integer, primary_key=True, nullable=False)
    Fecha_Registro = db.Column(db.Date)
    Cantidad = db.Column(db.Integer)
    FK_Id_Proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.Id_Proveedor"))
    FK_Id_Producto = db.Column(db.Integer, db.ForeignKey("producto.Id_Producto"))
    producto = db.relationship("Producto", back_populates="fecha_Registro_Prod")
    proveedor= db.relationship("Proveedor", back_populates="fecha_Registro_Prod")


    
#serializacion 

class EnumADiccionario(fields.Field): #maneja campos personalizados
    def _serialize(self, value, attr, obj, **kwargs): #metodo -valor, -atributo, -objeto, -argumentos
        if value is None:  #evita serializar un valor nulo
            return None
        return{"llave": value.name, "valor": value.value}
            


class RolSchema(SQLAlchemyAutoSchema):  #1
    
    class Meta:
        model = Rol
        include_relationships = True
        load_instance = True


class UsuarioSchema(SQLAlchemyAutoSchema):   #2
    
    rol_rl = fields.Nested(RolSchema)

    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

class VentaSchema(SQLAlchemyAutoSchema):  #9
    usuario = fields.Nested(UsuarioSchema)
    detalle_Venta = fields.Nested(UsuarioSchema)

    class Meta:
        model = Venta
        include_relationships = True
        load_instance = True

    @post_dump
    def convert_decimal_to_float(self, data, **kwargs):
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)
        return data
    
    Total_Venta_Formateado = fields.Method("get_total_formateado")

    def get_total_formateado(self, obj):
        return "${:,.0f}".format(obj.Total_Venta).replace(",", ".")


class ProveedorSchema(SQLAlchemyAutoSchema): #3
    
    class Meta:
        model = Proveedor
        include_relationships = True
        load_instance = True


class CategoriaSchema(SQLAlchemyAutoSchema): #6
    
    class Meta:
        model = Categoria
        include_relationships = True
        load_instance = True

class SubcategoriaSchema(SQLAlchemyAutoSchema):  #7
    
    categoria_rl = fields.Nested(CategoriaSchema)

    class Meta:
        model = Subcategoria
        include_relationships = True
        load_instance = True

class ProductoSchema(SQLAlchemyAutoSchema):  #8
    proveedor = fields.Nested(ProveedorSchema)
    subcategoria = fields.Nested(SubcategoriaSchema)

    class Meta:
        model = Producto
        include_relationships = True
        load_instance = True

    @post_dump
    def convertir_y_formatear(self, data, **kwargs):
        for campo in ['Precio_Bruto_Prod', 'Precio_Neto_Unidad_Prod', 'Iva_Prod', 'Porcentaje_Ganancia']:
            if campo in data and isinstance(data[campo], Decimal):
                data[campo] = float(data[campo])
        for campo in ['Precio_Bruto_Prod', 'Precio_Neto_Unidad_Prod']:
            if campo in data and isinstance(data[campo], (float, int)):
                data[campo] = f"${data[campo]:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return data

class Fecha_Registro_Prod (SQLAlchemyAutoSchema): #4
    
    Proveedor = fields.Nested(ProveedorSchema)
    Producto = fields.Nested(ProductoSchema)
    
    class Meta:
        model = Fecha_Registro_Prod
        include_relationships = True
        load_instance = True



class FacturaSchema(SQLAlchemyAutoSchema): #10

    class Meta:
        model = Factura
        include_relationships = True
        load_instance = True


class Detalle_VentaSchema(SQLAlchemyAutoSchema):  #11
    Venta = fields.Nested(VentaSchema)
    Producto = fields.Nested(ProductoSchema)
    Factura = fields.Nested(FacturaSchema)

    class Meta:
        model = Detalle_Venta
        include_relationships = True
        load_instance = True

    @post_dump
    def convert_decimal_to_float(self, data, **kwargs):
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)
        return data