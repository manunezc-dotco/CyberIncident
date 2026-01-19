// Funciones generales para CyberIncident

// Inicializar tooltips de Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Función para confirmar eliminaciones
function confirmarAccion(mensaje) {
    return confirm(mensaje || '¿Está seguro de realizar esta acción?');
}

// Función para cargar estadísticas
function cargarEstadisticas() {
    fetch('/api/estadisticas')
        .then(response => response.json())
        .then(data => {
            // Actualizar elementos con estadísticas si existen
            if (document.getElementById('totalIncidentes')) {
                document.getElementById('totalIncidentes').textContent = data.total;
            }
            if (document.getElementById('incidentesAbiertos')) {
                document.getElementById('incidentesAbiertos').textContent = data.abiertos;
            }
            if (document.getElementById('incidentesCriticos')) {
                document.getElementById('incidentesCriticos').textContent = data.criticos;
            }
        })
        .catch(error => console.error('Error cargando estadísticas:', error));
}

// Cargar estadísticas al iniciar si estamos en la página principal
if (window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', cargarEstadisticas);
}

// Función para previsualizar imágenes
function previsualizarImagen(input, previewId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById(previewId).src = e.target.result;
            document.getElementById(previewId).style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Función para validar tamaño de archivo
function validarTamanoArchivo(input, maxSizeMB) {
    if (input.files && input.files[0]) {
        var fileSize = input.files[0].size / 1024 / 1024; // Tamaño en MB
        if (fileSize > maxSizeMB) {
            alert(`El archivo es demasiado grande. Tamaño máximo: ${maxSizeMB}MB`);
            input.value = '';
            return false;
        }
    }
    return true;
}

// Función para formatear fecha
function formatearFecha(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Exportar funciones al scope global
window.CyberIncident = {
    confirmarAccion,
    cargarEstadisticas,
    previsualizarImagen,
    validarTamanoArchivo,
    formatearFecha
};