from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Elementos - CRUD completo
    path('elementos/', views.elementos_lista, name='elementos_lista'),
    path('elementos/crear/', views.elemento_crear, name='elemento_crear'),
    path('elementos/<str:elemento_id>/', views.elemento_detalle, name='elemento_detalle'),
    path('elementos/<str:elemento_id>/editar/', views.elemento_editar, name='elemento_editar'),
    # path('elementos/<str:elemento_id>/eliminar/', views.elemento_eliminar, name='elemento_eliminar'),
    
    # Movimientos
    path('movimientos/', views.movimientos_lista, name='movimientos_lista'),
    path('movimientos/crear/', views.movimiento_crear, name='movimiento_crear'),
    path('movimientos/<int:movimiento_id>/', views.movimiento_detalle, name='movimiento_detalle'),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),

    # API para obtener elementos asignados a un usuario
    path(
        'api/elementos-usuario/<int:usuario_id>/',
        views.obtener_elementos_usuario,
        name='obtener_elementos_usuario',        
    ),

    # API para obtener nombres de elementos por categoría
    path(
        'api/nombres-elementos/<int:categoria_id>/',
        views.obtener_nombres_elementos,
        name='obtener_nombres_elementos'
    ),

    path('api/elementos-asignados/',
         views.obtener_elementos_asignados,
         name='obtener_elementos_asignados'
    ),

    path('api/usuarios-bodega/',
        views.api_usuarios_bodega,
        name='api_usuarios_bodega'),

    path('api/usuarios-activos/',
         views.api_usuarios_activos,
         name='api_usuarios_activos'),

    path('api/usuarios-por-rol/<str:rol>/',
         views.api_usuarios_por_rol,
         name='api_usuarios_por_rol'),

    path('api/usuarios-excepto-rol/<str:rol>/',
         views.api_usuarios_excepto_rol,
         name='api_usuarios_excepto_rol'),     

    path('api/elementos-bodega/<int:usuario_id>/',
         views.api_elementos_bodega, 
         name='api_elementos_bodega'),

     path('api/elementos-mantenimiento/<int:usuario_id>/',
          views.api_elementos_para_mantenimiento,
          name='api_elementos_mantenimiento'), 

     path('usuarios-elementos/',
          views.usuarios_con_elementos,
          name='usuarios_con_elementos'),

     path('reportes/usuarios/',
          views.reporte_por_usuario,
          name='reporte_usuarios'),

     path('reportes/bodega/',
          views.reporte_por_bodega,
          name='reporte_bodega'),

     path('reportes/categoria/',
          views.reporte_por_categoria,
          name='reporte_categoria'),

     path('movimientos/<int:movimiento_id>/acta/',
          views.descargar_acta,
          name='descargar_acta'),

     path('movimientos/<int:movimiento_id>/acta/preview/',
          views.preview_acta,
          name='preview_acta'),  

     path('movimientos/<int:movimiento_id>/firmar/<str:tipo_firma>/',
         views.firmar_acta,
         name='firmar_acta'),

     path('mis-documentos/',
          views.mis_documentos,
          name='mis_documentos'),

     path('mis-elementos-asignados/',
          views.mis_elementos_asignados,
          name='mis_elementos_asignados'),

     path('api/elemento-detalle/<str:elemento_id>/',
          views.api_detalle_elemento,
          name='api_elemento_detalle'),           

     path('reportes/garantias/',
          views.reporte_garantias,
          name='reporte_garantias'),

     path('movimientos/editar/<int:movimiento_id>/',
          views.movimiento_editar,
          name='movimiento_editar'),

     path('movimientos/anular/<int:movimiento_id>/',
          views.movimiento_anular,
          name='movimiento_anular'),          
     # path('reportes/bodega/<int:bodega_id>/',
     #      views.reporte_bodega_detalle,
     #      name='reporte_bodega_detalle'),                  
]
