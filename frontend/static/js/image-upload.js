/**
 * Sistema de carga de imágenes para Merkatolima
 * Versión simplificada y robusta
 */

// Variables globales
let uploadedFiles = [];
const maxImages = 5;
const maxFileSize = 5 * 1024 * 1024; // 5MB

/**
 * Inicializar el sistema de carga de imágenes
 */
function initImageUpload() {
    console.log('Inicializando sistema de carga de imágenes...');
    
    // Event listeners para file input
    const fileInput = document.getElementById('imageFiles');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            handleFileSelection(e.target.files);
        });
    }
    
    // Drag and drop
    const uploadPanel = document.getElementById('upload-panel');
    if (uploadPanel) {
        const dropZone = uploadPanel.querySelector('.border.rounded');
        if (dropZone) {
            setupDragAndDrop(dropZone);
        }
    }
}

/**
 * Configurar drag and drop
 */
function setupDragAndDrop(dropZone) {
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('border-primary', 'bg-light');
    });

    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('border-primary', 'bg-light');
    });

    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('border-primary', 'bg-light');
        
        const files = e.dataTransfer.files;
        handleFileSelection(files);
    });
}

/**
 * Manejar selección de archivos
 */
function handleFileSelection(files) {
    const fileArray = Array.from(files);
    console.log(`Seleccionados ${fileArray.length} archivos`);
    
    // Validar número máximo de archivos
    if (uploadedFiles.length + fileArray.length > maxImages) {
        alert(`Solo puedes subir máximo ${maxImages} imágenes. Ya tienes ${uploadedFiles.length} imagen(es).`);
        return;
    }
    
    // Validar cada archivo - compatible con navegadores antiguos
    for (let i = 0; i < fileArray.length; i++) {
        const file = fileArray[i];
        console.log(`Validando archivo: ${file.name}, tipo: ${file.type}, tamaño: ${file.size}`);
        
        if (!validateFile(file)) {
            continue;
        }
        
        // Agregar archivo a la lista
        uploadedFiles.push(file);
        console.log(`Archivo agregado: ${file.name}`);
        
        // Crear preview
        createFilePreview(file, uploadedFiles.length - 1);
    }
    
    updateUploadedImagesDisplay();
    console.log(`Total de archivos cargados: ${uploadedFiles.length}`);
}

/**
 * Validar archivo
 */
function validateFile(file) {
    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
        alert(`El archivo "${file.name}" no es una imagen válida.`);
        return false;
    }
    
    // Validar tamaño
    if (file.size > maxFileSize) {
        alert(`El archivo "${file.name}" es muy grande. Máximo 5MB por imagen.`);
        return false;
    }
    
    // Validar extensión
    const validExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!validExtensions.includes(fileExtension)) {
        alert(`El archivo "${file.name}" no tiene una extensión válida. Usa: ${validExtensions.join(', ')}`);
        return false;
    }
    
    return true;
}

/**
 * Crear preview de archivo
 */
function createFilePreview(file, index) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewHtml = `
            <div class="col-md-3 col-sm-4 col-6 file-preview" data-index="${index}">
                <div class="position-relative">
                    <img src="${e.target.result}" alt="${file.name}" class="img-thumbnail w-100" style="height: 120px; object-fit: cover;">
                    <button type="button" class="btn btn-danger btn-sm position-absolute top-0 end-0 m-1" onclick="removeUploadedFile(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                    <div class="position-absolute bottom-0 start-0 end-0 bg-dark bg-opacity-75 text-white p-1">
                        <small class="text-truncate d-block">${file.name}</small>
                        <small>${(file.size / 1024 / 1024).toFixed(2)} MB</small>
                    </div>
                    ${index === 0 ? '<span class="position-absolute top-0 start-0 badge bg-primary m-1">Principal</span>' : ''}
                </div>
            </div>
        `;
        
        const uploadedImagesContainer = document.getElementById('uploadedImages');
        if (uploadedImagesContainer) {
            uploadedImagesContainer.insertAdjacentHTML('beforeend', previewHtml);
        }
    };
    reader.readAsDataURL(file);
}

/**
 * Actualizar display de imágenes subidas
 */
function updateUploadedImagesDisplay() {
    const uploadedImagesContainer = document.getElementById('uploadedImages');
    if (!uploadedImagesContainer) return;
    
    if (uploadedFiles.length > 0) {
        uploadedImagesContainer.style.display = 'block';
        
        // Actualizar contador
        const counterElement = uploadedImagesContainer.querySelector('.col-12 h6');
        if (counterElement) {
            counterElement.textContent = `Imágenes Seleccionadas (${uploadedFiles.length}/${maxImages}):`;
        }
    } else {
        uploadedImagesContainer.style.display = 'none';
        uploadedImagesContainer.innerHTML = '<div class="col-12"><h6 class="fw-bold">Imágenes Seleccionadas:</h6></div>';
    }
}

/**
 * Eliminar archivo subido
 */
function removeUploadedFile(index) {
    console.log(`Eliminando archivo en índice: ${index}`);
    
    // Remover del array
    uploadedFiles.splice(index, 1);
    
    // Remover preview del DOM
    const previewElement = document.querySelector(`.file-preview[data-index="${index}"]`);
    if (previewElement) {
        previewElement.remove();
    }
    
    // Actualizar índices de los elementos restantes
    const remainingPreviews = document.querySelectorAll('.file-preview');
    remainingPreviews.forEach((preview, newIndex) => {
        preview.setAttribute('data-index', newIndex);
        const removeBtn = preview.querySelector('button');
        removeBtn.setAttribute('onclick', `removeUploadedFile(${newIndex})`);
        
        // Actualizar badge de principal
        const principalBadge = preview.querySelector('.badge');
        if (principalBadge) {
            principalBadge.remove();
        }
        if (newIndex === 0) {
            const img = preview.querySelector('img');
            img.insertAdjacentHTML('afterend', '<span class="position-absolute top-0 start-0 badge bg-primary m-1">Principal</span>');
        }
    });
    
    updateUploadedImagesDisplay();
    
    // Limpiar input file
    const fileInput = document.getElementById('imageFiles');
    if (fileInput) {
        fileInput.value = '';
    }
}

/**
 * Subir archivos al servidor
 */
async function uploadFiles() {
    if (uploadedFiles.length === 0) {
        console.log('No hay archivos para subir');
        return [];
    }
    
    console.log(`🔄 Subiendo ${uploadedFiles.length} archivos...`);
    console.log('Archivos a subir:', uploadedFiles.map(f => f.name));
    
    const formData = new FormData();
    uploadedFiles.forEach((file, index) => {
        console.log(`📎 Agregando archivo ${index}: ${file.name} (${file.size} bytes, ${file.type})`);
        formData.append(`image_${index}`, file);
    });
    
    // Verificar contenido del FormData
    console.log('FormData keys:', Array.from(formData.keys()));
    
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        console.log('🔐 Token CSRF:', csrfToken ? 'Presente' : 'Ausente');
        
        // Usar el puerto 8001 (Django) directamente para subir imágenes
        const uploadUrl = 'http://localhost:8001/marketplace/api/upload-images/';
        console.log('📡 Enviando petición a:', uploadUrl);
        
        const response = await fetch(uploadUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            },
            credentials: 'include' // Importante para enviar cookies de sesión
        });
        
        console.log('📥 Respuesta del servidor:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error del servidor:', errorText);
            throw new Error(`Error del servidor: ${response.status} - ${errorText.substring(0, 100)}`);
        }
        
        const result = await response.json();
        console.log('📦 Resultado completo:', result);
        
        if (result.success) {
            console.log(`✅ Subida exitosa: ${result.count} imágenes`);
            console.log('🖼️ URLs generadas:', result.image_urls);
            return result.image_urls || [];
        } else {
            throw new Error(result.error || 'Error desconocido');
        }
    } catch (error) {
        console.error('❌ Error uploading files:', error);
        alert(`Error al subir las imágenes: ${error.message}`);
        return [];
    }
}

/**
 * Obtener URLs de imágenes según el método seleccionado
 */
async function getImageUrls() {
    const activeTab = document.querySelector('#imageUploadTabs .nav-link.active');
    let imageUrls = [];
    
    console.log('🔍 getImageUrls() llamada');
    console.log('   Tab activo:', activeTab ? activeTab.id : 'ninguno');
    console.log('   Archivos cargados:', uploadedFiles.length);
    
    if (activeTab && activeTab.id === 'upload-tab') {
        // Subir archivos
        if (uploadedFiles.length > 0) {
            console.log('📤 Subiendo archivos...');
            imageUrls = await uploadFiles();
            console.log('📥 URLs recibidas de uploadFiles():', imageUrls);
        } else {
            console.log('⚠️ No hay archivos para subir');
        }
    } else {
        // Recopilar URLs de inputs
        const urlInputs = document.querySelectorAll('.image-url');
        console.log('📝 Recopilando URLs de inputs, total:', urlInputs.length);
        urlInputs.forEach((input, index) => {
            console.log(`   Input ${index}: ${input.value}`);
            if (input.value && input.value.trim()) {
                imageUrls.push(input.value.trim());
            }
        });
        console.log('📋 URLs de inputs recopiladas:', imageUrls);
    }
    
    console.log('✅ getImageUrls() retorna:', imageUrls);
    console.log('📊 Total URLs:', imageUrls.length);
    
    return imageUrls;
}

/**
 * Obtener archivos cargados (para acceso externo)
 */
function getUploadedFiles() {
    return uploadedFiles;
}

/**
 * Limpiar archivos cargados
 */
function clearUploadedFiles() {
    uploadedFiles = [];
    updateUploadedImagesDisplay();
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initImageUpload();
});