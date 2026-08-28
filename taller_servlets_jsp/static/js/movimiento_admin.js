(function($) {
    $(document).ready(function() {
        console.log('✓ Script de movimientos cargado (Versión 3.0 - Limpieza Total)');
        
        var tipoMovimientoField = $('#id_tipo_movimiento');
        var usuarioOrigenField = $('#id_usuario_origen');
        
        if (!tipoMovimientoField.length) {
            console.error('❌ Campo tipo_movimiento no encontrado');
            return;
        }
        
        function actualizarCamposRequeridos() {
            var tipoMovimiento = tipoMovimientoField.val();
            
            $('#tabla-elementos-origen').remove();
            $('#tabla-elementos-destino').remove();
            
            if (tipoMovimiento === 'Devolucion' || tipoMovimiento === 'Reasignacion') {
                var label = usuarioOrigenField.closest('.form-row').find('label');
                if (!label.hasClass('required')) {
                    label.addClass('required');
                    if (!label.find('.asterisk').length) {
                        label.append(' <span class="asteriskField">*</span>');
                    }
                }
            } else {
                var label = usuarioOrigenField.closest('.form-row').find('label');
                label.removeClass('required');
                label.find('.asteriskField').remove();
            }
        }
        
        tipoMovimientoField.change(actualizarCamposRequeridos);
        actualizarCamposRequeridos();

        // Función para mostrar mensajes visuales
        function mostrarMensaje(mensaje, tipo) {
            $('.custom-message').remove();
            var bgColors = { 'success': '#d4edda', 'warning': '#fff3cd', 'error': '#f8d7da', 'info': '#d1ecf1' };
            var borderColors = { 'success': '#28a745', 'warning': '#ffc107', 'error': '#dc3545', 'info': '#17a2b8' };
            
            var messageBox = $(
                '<div class="custom-message" style="' +
                'margin: 15px 0; padding: 12px 20px; ' +
                'background-color: ' + bgColors[tipo] + '; ' +
                'border-left: 4px solid ' + borderColors[tipo] + '; ' +
                'border-radius: 4px; font-weight: bold;">' +
                mensaje + '</div>'
            );
            
            $('fieldset').first().before(messageBox);
            if (tipo !== 'info') {
                setTimeout(function() { messageBox.fadeOut(function() { $(this).remove(); }); }, 5000);
            }
        }

        // =========================================================================
        // FUNCIÓN MAESTRA: Agrega elementos sin contaminar la plantilla de Django
        // =========================================================================
        function agregarElementosSecuencialmente(elementos, index) {
            if (index >= elementos.length) {
                mostrarMensaje('✓ Se cargaron ' + elementos.length + ' elementos al formulario', 'success');
                return;
            }

            var elemento = elementos[index];
            var addButton = $('.add-row a');

            if (addButton.length) {
                // 1. Clic nativo: Dejamos que Django cree la fila perfectamente limpia
                addButton[0].click();

                setTimeout(function() {
                    // 2. EL SECRETO: Seleccionamos la última fila visible, IGNORANDO la plantilla (.empty-form)
                    var $ultimaFila = $('.inline-related.tabular tbody tr').not('.empty-form').last();
                    
                    var $selectElemento = $ultimaFila.find('select[id$="-elemento"]');
                    var $inputCantidad = $ultimaFila.find('input[id$="-cantidad"]');

                    if ($selectElemento.length) {
                        $selectElemento.val(elemento.id);
                        // Disparamos el evento de cambio por si Django usa selectores nativos
                        $selectElemento.trigger('change'); 
                    }

                    if ($inputCantidad.length && !$inputCantidad.val()) {
                        $inputCantidad.val(1);
                    }

                    // 3. Llamamos al siguiente elemento en la fila
                    agregarElementosSecuencialmente(elementos, index + 1);
                }, 150); // 150ms es el tiempo ideal para que Django asigne los IDs sin congelarse
            }
        }

        // Funciones originales de AJAX para traer los datos (conectadas a nuestra función maestra)
        function mostrarTablaElementos(data, tipo, usuarioNombre) { /* ... Tu código de tabla visual ... */ }
        
        function cargarElementosUsuario(usuarioId, tipo, usuarioNombre) {
            var url = '/inventario/api/elementos-usuario/' + usuarioId + '/';
            $.ajax({
                url: url, method: 'GET', dataType: 'json',
                success: function(data) {
                    if (tipo === 'origen') {
                        // mostrarTablaElementos(data, 'origen', usuarioNombre); <- Descomenta si usas la tabla visual
                        if (data.elementos && data.elementos.length > 0) {
                            mostrarMensaje('⏳ Cargando ' + data.elementos.length + ' elementos...', 'info');
                            agregarElementosSecuencialmente(data.elementos, 0);
                        }
                    } else if (tipo === 'destino') {
                        // mostrarTablaElementos(data, 'destino', usuarioNombre); <- Descomenta si usas la tabla visual
                    }
                },
                error: function() { mostrarMensaje('❌ Error al cargar los elementos.', 'error'); }
            });
        }

        $('#id_usuario_origen').change(function() {
            var usuarioId = $(this).val();
            var tipoMovimiento = $('#id_tipo_movimiento').val();
            if (usuarioId && (tipoMovimiento === 'Devolucion' || tipoMovimiento === 'Reasignacion' || tipoMovimiento === 'Traslado')) {
                var usuarioNombre = $(this).find('option:selected').text();
                cargarElementosUsuario(usuarioId, 'origen', usuarioNombre);
            }
        });
    });
})(django.jQuery);