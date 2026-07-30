/**
 * Merktolima Chatbot - Asistente Virtual Inteligente
 * Ayuda con preguntas frecuentes, compras, ventas y publicaciones
 */

class MerktolimaChatbot {
    constructor() {
        this.isOpen = false;
        this.conversationHistory = [];
        this.currentStep = null;
        this.userData = {};
        this.init();
    }

    init() {
        this.createChatbotHTML();
        this.bindEvents();
        this.loadWelcomeMessage();
    }

    createChatbotHTML() {
        const chatbotHTML = `
            <!-- Botón flotante del chatbot -->
            <div id="chatbot-toggle" class="chatbot-toggle">
                <i class="fas fa-comments"></i>
                <span class="chatbot-badge">¡Hola!</span>
            </div>

            <!-- Ventana del chatbot -->
            <div id="chatbot-window" class="chatbot-window">
                <div class="chatbot-header">
                    <div class="chatbot-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="chatbot-info">
                        <h4>MerkaBot</h4>
                        <span>Asistente Virtual de Merktolima</span>
                    </div>
                    <button id="chatbot-close" class="chatbot-close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div id="chatbot-messages" class="chatbot-messages">
                    <!-- Los mensajes se cargarán aquí -->
                </div>
                
                <div class="chatbot-quick-actions">
                    <button class="quick-action-btn" data-action="help">
                        <i class="fas fa-question-circle"></i> Ayuda
                    </button>
                    <button class="quick-action-btn" data-action="sell">
                        <i class="fas fa-store"></i> Vender
                    </button>
                    <button class="quick-action-btn" data-action="buy">
                        <i class="fas fa-shopping-cart"></i> Comprar
                    </button>
                </div>
                
                <div class="chatbot-input-area">
                    <input type="text" id="chatbot-input" placeholder="Escribe tu pregunta..." maxlength="500">
                    <button id="chatbot-send">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    bindEvents() {
        // Toggle chatbot
        document.getElementById('chatbot-toggle').addEventListener('click', () => {
            this.toggleChatbot();
        });

        // Cerrar chatbot
        document.getElementById('chatbot-close').addEventListener('click', () => {
            this.closeChatbot();
        });

        // Enviar mensaje
        document.getElementById('chatbot-send').addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter para enviar
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Acciones rápidas
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    toggleChatbot() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        if (this.isOpen) {
            this.closeChatbot();
        } else {
            window.classList.add('open');
            toggle.classList.add('hidden');
            this.isOpen = true;
            
            // Remover badge de notificación
            const badge = toggle.querySelector('.chatbot-badge');
            if (badge) {
                badge.remove();
            }
        }
    }

    closeChatbot() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        window.classList.remove('open');
        toggle.classList.remove('hidden');
        this.isOpen = false;
    }

    loadWelcomeMessage() {
        const welcomeMessage = {
            type: 'bot',
            text: '¡Hola! 👋 Soy MerkaBot, tu asistente virtual de Merktolima. Estoy aquí para ayudarte con:',
            options: [
                { text: '🛒 Comprar productos', action: 'buy_guide' },
                { text: '🏪 Vender productos', action: 'sell_guide' },
                { text: '📝 Publicar productos', action: 'publish_guide' },
                { text: '❓ Preguntas frecuentes', action: 'faq' },
                { text: '🆘 Soporte técnico', action: 'support' }
            ]
        };
        
        this.addMessage(welcomeMessage);
    }

    sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Agregar mensaje del usuario
        this.addMessage({
            type: 'user',
            text: message
        });
        
        // Limpiar input
        input.value = '';
        
        // Procesar respuesta
        this.processMessage(message);
    }

    addMessage(message) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageElement = document.createElement('div');
        messageElement.className = `chatbot-message ${message.type}`;
        
        let messageHTML = `
            <div class="message-content">
                ${message.text}
            </div>
        `;
        
        // Agregar opciones si existen
        if (message.options) {
            messageHTML += '<div class="message-options">';
            message.options.forEach(option => {
                messageHTML += `
                    <button class="option-btn" data-action="${option.action}">
                        ${option.text}
                    </button>
                `;
            });
            messageHTML += '</div>';
        }
        
        messageElement.innerHTML = messageHTML;
        messagesContainer.appendChild(messageElement);
        
        // Bind eventos a las opciones
        messageElement.querySelectorAll('.option-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleAction(action);
            });
        });
        
        // Scroll al final
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Guardar en historial
        this.conversationHistory.push(message);
    }

    processMessage(message) {
        const lowerMessage = message.toLowerCase();
        
        // Mostrar typing indicator
        this.showTyping();
        
        setTimeout(() => {
            this.hideTyping();
            
            // Análisis de intención
            if (this.containsKeywords(lowerMessage, ['comprar', 'compra', 'producto', 'buscar'])) {
                this.handleBuyingIntent(message);
            } else if (this.containsKeywords(lowerMessage, ['vender', 'venta', 'publicar', 'anuncio'])) {
                this.handleSellingIntent(message);
            } else if (this.containsKeywords(lowerMessage, ['precio', 'costo', 'cuanto', 'pagar'])) {
                this.handlePricingQuestions();
            } else if (this.containsKeywords(lowerMessage, ['envio', 'entrega', 'shipping'])) {
                this.handleShippingQuestions();
            } else if (this.containsKeywords(lowerMessage, ['pago', 'tarjeta', 'efectivo', 'transferencia'])) {
                this.handlePaymentQuestions();
            } else if (this.containsKeywords(lowerMessage, ['cuenta', 'registro', 'perfil', 'usuario'])) {
                this.handleAccountQuestions();
            } else if (this.containsKeywords(lowerMessage, ['problema', 'error', 'ayuda', 'soporte'])) {
                this.handleSupportQuestions();
            } else {
                this.handleGeneralResponse(message);
            }
        }, 1000);
    }

    containsKeywords(text, keywords) {
        return keywords.some(keyword => text.includes(keyword));
    }

    handleBuyingIntent(message) {
        this.addMessage({
            type: 'bot',
            text: '¡Perfecto! Te ayudo a comprar en Merktolima. ¿Qué te interesa?',
            options: [
                { text: '🔍 Buscar productos específicos', action: 'search_products' },
                { text: '📱 Ver categorías populares', action: 'show_categories' },
                { text: '🛒 Cómo agregar al carrito', action: 'cart_help' },
                { text: '💳 Proceso de pago', action: 'payment_process' }
            ]
        });
    }

    handleSellingIntent(message) {
        this.addMessage({
            type: 'bot',
            text: '¡Excelente! Te guío para vender en Merktolima. ¿En qué necesitas ayuda?',
            options: [
                { text: '📝 Crear mi primera publicación', action: 'create_listing' },
                { text: '📊 Panel de vendedor', action: 'seller_dashboard' },
                { text: '💰 Comisiones y tarifas', action: 'fees_info' },
                { text: '📦 Gestión de inventario', action: 'inventory_help' }
            ]
        });
    }

    handleQuickAction(action) {
        switch (action) {
            case 'help':
                this.showFAQ();
                break;
            case 'sell':
                this.handleAction('sell_guide');
                break;
            case 'buy':
                this.handleAction('buy_guide');
                break;
        }
    }

    handleAction(action) {
        switch (action) {
            case 'buy_guide':
                this.showBuyingGuide();
                break;
            case 'sell_guide':
                this.showSellingGuide();
                break;
            case 'publish_guide':
                this.showPublishGuide();
                break;
            case 'faq':
                this.showFAQ();
                break;
            case 'support':
                this.showSupport();
                break;
            case 'search_products':
                this.guideProductSearch();
                break;
            case 'show_categories':
                this.showCategories();
                break;
            case 'cart_help':
                this.showCartHelp();
                break;
            case 'payment_process':
                this.showPaymentProcess();
                break;
            case 'create_listing':
                this.guideCreateListing();
                break;
            case 'seller_dashboard':
                this.showSellerDashboard();
                break;
            case 'fees_info':
                this.showFeesInfo();
                break;
            case 'inventory_help':
                this.showInventoryHelp();
                break;
            case 'redirect_search':
                this.redirectToSearch();
                break;
            case 'redirect_cart':
                this.redirectToCart();
                break;
            case 'redirect_seller':
                this.redirectToSellerDashboard();
                break;
            case 'redirect_create_product':
                this.redirectToCreateProduct();
                break;
            case 'payment_faq':
                this.showPaymentFAQ();
                break;
            case 'shipping_faq':
                this.showShippingFAQ();
                break;
            case 'security_faq':
                this.showSecurityFAQ();
                break;
            case 'fees_faq':
                this.showFeesFAQ();
                break;
            case 'account_faq':
                this.showAccountFAQ();
                break;
            case 'create_account':
                window.location.href = '/registro/';
                break;
            case 'login_help':
                window.location.href = '/login/';
                break;
            case 'update_profile':
                window.location.href = '/perfil/';
                break;
        }
    }

    showBuyingGuide() {
        this.addMessage({
            type: 'bot',
            text: '🛒 **Guía para Comprar en Merktolima:**\n\n1. **Busca productos** usando la barra de búsqueda\n2. **Filtra por categoría** y precio\n3. **Revisa detalles** del producto y vendedor\n4. **Agrega al carrito** la cantidad deseada\n5. **Procede al checkout** y completa tu compra\n\n¿Te ayudo con algún paso específico?',
            options: [
                { text: '🔍 Buscar productos ahora', action: 'redirect_search' },
                { text: '🛒 Ver mi carrito', action: 'redirect_cart' },
                { text: '❓ Más preguntas', action: 'faq' }
            ]
        });
    }

    showSellingGuide() {
        this.addMessage({
            type: 'bot',
            text: '🏪 **Guía para Vender en Merktolima:**\n\n1. **Crea tu cuenta** de vendedor\n2. **Accede al panel** de vendedor\n3. **Publica productos** con fotos y descripción\n4. **Gestiona inventario** y precios\n5. **Procesa pedidos** de clientes\n\n¿Quieres que te ayude a empezar?',
            options: [
                { text: '📝 Crear primera publicación', action: 'guide_first_listing' },
                { text: '📊 Ir al panel de vendedor', action: 'redirect_seller' },
                { text: '💰 Ver comisiones', action: 'fees_info' }
            ]
        });
    }

    showPublishGuide() {
        this.addMessage({
            type: 'bot',
            text: '📝 **Cómo Publicar un Producto:**\n\n1. **Título atractivo** (máx. 60 caracteres)\n2. **Descripción detallada** con características\n3. **Fotos de calidad** (mínimo 3)\n4. **Precio competitivo** en pesos colombianos\n5. **Categoría correcta** para mejor visibilidad\n6. **Stock disponible** actualizado\n\n¿Empezamos con tu publicación?',
            options: [
                { text: '✅ Sí, crear publicación', action: 'redirect_create_product' },
                { text: '💡 Consejos para fotos', action: 'photo_tips' },
                { text: '💰 Ayuda con precios', action: 'pricing_tips' }
            ]
        });
    }

    showFAQ() {
        this.addMessage({
            type: 'bot',
            text: '❓ **Preguntas Frecuentes:**\n\nSelecciona el tema que te interesa:',
            options: [
                { text: '💳 Métodos de pago', action: 'payment_faq' },
                { text: '📦 Envíos y entregas', action: 'shipping_faq' },
                { text: '🔒 Seguridad', action: 'security_faq' },
                { text: '💰 Comisiones', action: 'fees_faq' },
                { text: '👤 Cuenta y perfil', action: 'account_faq' },
                { text: '🆘 Reportar problema', action: 'report_issue' }
            ]
        });
    }

    showSupport() {
        this.addMessage({
            type: 'bot',
            text: '🆘 **Soporte Técnico:**\n\nEstoy aquí para ayudarte. También puedes:\n\n📧 **Email:** soporte@merktolima.com\n📞 **Teléfono:** +57 1 234-5678\n💬 **WhatsApp:** +57 300 123-4567\n\n**Horarios:** Lunes a Viernes 8:00 AM - 6:00 PM\n\n¿Cuál es tu problema específico?',
            options: [
                { text: '🔐 Problemas de acceso', action: 'login_issues' },
                { text: '💳 Problemas de pago', action: 'payment_issues' },
                { text: '📦 Problemas de envío', action: 'shipping_issues' },
                { text: '🛒 Problemas con pedidos', action: 'order_issues' }
            ]
        });
    }

    guideProductSearch() {
        this.addMessage({
            type: 'bot',
            text: '🔍 **Te ayudo a buscar productos:**\n\n¿Qué estás buscando? Puedes decirme:\n- Nombre del producto\n- Categoría\n- Rango de precio\n\nEjemplo: "Busco un celular Samsung entre $500.000 y $1.000.000"',
            options: [
                { text: '📱 Electrónicos', action: 'search_electronics' },
                { text: '👕 Ropa y accesorios', action: 'search_fashion' },
                { text: '🏠 Hogar y jardín', action: 'search_home' },
                { text: '🔍 Búsqueda personalizada', action: 'custom_search' }
            ]
        });
    }

    showTyping() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingElement = document.createElement('div');
        typingElement.className = 'chatbot-message bot typing';
        typingElement.id = 'typing-indicator';
        typingElement.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }

    handleGeneralResponse(message) {
        const responses = [
            "Interesante pregunta. ¿Podrías ser más específico sobre lo que necesitas?",
            "Te entiendo. ¿Te gustaría que te ayude con compras, ventas o tienes alguna pregunta específica?",
            "¡Perfecto! Estoy aquí para ayudarte. ¿Qué necesitas hacer en Merktolima?",
            "No estoy seguro de entender completamente. ¿Podrías reformular tu pregunta?"
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        
        this.addMessage({
            type: 'bot',
            text: randomResponse,
            options: [
                { text: '🛒 Ayuda para comprar', action: 'buy_guide' },
                { text: '🏪 Ayuda para vender', action: 'sell_guide' },
                { text: '❓ Ver preguntas frecuentes', action: 'faq' },
                { text: '🆘 Contactar soporte', action: 'support' }
            ]
        });
    }

    // Métodos de redirección
    redirectToSearch() {
        window.location.href = '/productos/';
    }

    redirectToCart() {
        window.location.href = '/carrito/';
    }

    redirectToSellerDashboard() {
        window.location.href = '/vendedor/';
    }

    redirectToCreateProduct() {
        window.location.href = '/vendedor/producto/nuevo/';
    }

    // Métodos adicionales para manejar preguntas específicas
    handlePricingQuestions() {
        this.addMessage({
            type: 'bot',
            text: '💰 **Información sobre Precios:**\n\n• Los precios están en pesos colombianos (COP)\n• Incluyen IVA cuando aplique\n• Puedes filtrar por rango de precio\n• Ofertas especiales marcadas con descuentos\n• Envío gratis en compras superiores a $150.000\n\n¿Necesitas ayuda con algo específico?',
            options: [
                { text: '🔍 Buscar por precio', action: 'price_filter' },
                { text: '🚚 Info sobre envíos', action: 'shipping_info' },
                { text: '💳 Métodos de pago', action: 'payment_methods' }
            ]
        });
    }

    handleShippingQuestions() {
        this.addMessage({
            type: 'bot',
            text: '📦 **Información de Envíos:**\n\n• **Envío gratis** en compras +$150.000\n• **Entrega rápida** 1-3 días hábiles\n• **Cobertura nacional** en Colombia\n• **Seguimiento** en tiempo real\n• **Empaque seguro** garantizado\n\n¿Dónde quieres recibir tu pedido?',
            options: [
                { text: '🏠 Envío a domicilio', action: 'home_delivery' },
                { text: '🏪 Punto de recogida', action: 'pickup_point' },
                { text: '📍 Verificar cobertura', action: 'check_coverage' }
            ]
        });
    }

    handlePaymentQuestions() {
        this.addMessage({
            type: 'bot',
            text: '💳 **Métodos de Pago Disponibles:**\n\n• **Tarjetas de crédito** (Visa, MasterCard)\n• **Tarjetas débito** bancarias\n• **PSE** transferencias bancarias\n• **Efectivo** contra entrega\n• **Nequi, Daviplata** billeteras digitales\n\n**Pago 100% seguro** con encriptación SSL',
            options: [
                { text: '🔒 Seguridad de pagos', action: 'payment_security' },
                { text: '💰 Pago contra entrega', action: 'cash_delivery' },
                { text: '📱 Billeteras digitales', action: 'digital_wallets' }
            ]
        });
    }

    handleAccountQuestions() {
        this.addMessage({
            type: 'bot',
            text: '👤 **Gestión de Cuenta:**\n\n¿En qué puedo ayudarte con tu cuenta?',
            options: [
                { text: '📝 Crear cuenta nueva', action: 'create_account' },
                { text: '🔐 Problemas de acceso', action: 'login_help' },
                { text: '✏️ Actualizar perfil', action: 'update_profile' },
                { text: '🔄 Cambiar contraseña', action: 'change_password' }
            ]
        });
    }

    handleSupportQuestions() {
        this.addMessage({
            type: 'bot',
            text: '🆘 **Soporte Técnico:**\n\nDescribe tu problema y te ayudo a solucionarlo:',
            options: [
                { text: '🔐 No puedo iniciar sesión', action: 'login_issues' },
                { text: '💳 Error en el pago', action: 'payment_error' },
                { text: '📦 Problema con pedido', action: 'order_problem' },
                { text: '🔄 Página no carga', action: 'loading_issues' }
            ]
        });
    }
}

// FAQ Methods Extension
MerktolimaChatbot.prototype.showPaymentFAQ = function() {
    this.addMessage({
        type: 'bot',
        text: '💳 **FAQ - Métodos de Pago:**\n\n**¿Qué tarjetas aceptan?**\nVisa, MasterCard, American Express y tarjetas débito.\n\n**¿Es seguro pagar online?**\nSí, usamos encriptación SSL de 256 bits.\n\n**¿Puedo pagar contra entrega?**\nSí, disponible en ciudades principales.\n\n**¿Aceptan PSE?**\nSí, transferencias bancarias PSE disponibles.',
        options: [
            { text: '🔒 Más sobre seguridad', action: 'security_faq' },
            { text: '💰 Pago contra entrega', action: 'cash_delivery_info' },
            { text: '🆘 Contactar soporte', action: 'support' }
        ]
    });
};

MerktolimaChatbot.prototype.showShippingFAQ = function() {
    this.addMessage({
        type: 'bot',
        text: '📦 **FAQ - Envíos:**\n\n**¿Cuánto demora el envío?**\n1-3 días hábiles en ciudades principales.\n\n**¿Hay envío gratis?**\nSí, en compras superiores a $150.000.\n\n**¿Envían a todo Colombia?**\nSí, cobertura nacional disponible.\n\n**¿Puedo rastrear mi pedido?**\nSí, recibes código de seguimiento.',
        options: [
            { text: '📍 Verificar cobertura', action: 'check_coverage' },
            { text: '🚚 Calcular envío', action: 'shipping_calculator' },
            { text: '📦 Rastrear pedido', action: 'track_order' }
        ]
    });
};

MerktolimaChatbot.prototype.showSecurityFAQ = function() {
    this.addMessage({
        type: 'bot',
        text: '🔒 **FAQ - Seguridad:**\n\n**¿Es seguro comprar aquí?**\nSí, certificado SSL y protección de datos.\n\n**¿Cómo protegen mi información?**\nEncriptación de extremo a extremo.\n\n**¿Qué hago si hay fraude?**\nContacta soporte inmediatamente.\n\n**¿Verifican a los vendedores?**\nSí, proceso de verificación obligatorio.',
        options: [
            { text: '🛡️ Política de privacidad', action: 'privacy_policy' },
            { text: '⚠️ Reportar problema', action: 'report_issue' },
            { text: '📞 Contactar soporte', action: 'support' }
        ]
    });
};

MerktolimaChatbot.prototype.showFeesFAQ = function() {
    this.addMessage({
        type: 'bot',
        text: '💰 **FAQ - Comisiones:**\n\n**¿Cuánto cobran por vender?**\n5% de comisión por venta exitosa.\n\n**¿Hay costos de publicación?**\nNo, publicar productos es gratis.\n\n**¿Cuándo recibo mi dinero?**\n7 días después de entrega confirmada.\n\n**¿Hay tarifas adicionales?**\nSolo comisión de venta, sin costos ocultos.',
        options: [
            { text: '🏪 Empezar a vender', action: 'redirect_seller' },
            { text: '📊 Ver panel vendedor', action: 'seller_dashboard' },
            { text: '💡 Consejos para vender', action: 'selling_tips' }
        ]
    });
};

MerktolimaChatbot.prototype.showAccountFAQ = function() {
    this.addMessage({
        type: 'bot',
        text: '👤 **FAQ - Cuenta:**\n\n**¿Cómo creo una cuenta?**\nClick en "Registrarse" y completa el formulario.\n\n**¿Olvidé mi contraseña?**\nUsa "Recuperar contraseña" en login.\n\n**¿Puedo cambiar mi email?**\nSí, desde tu perfil de usuario.\n\n**¿Cómo elimino mi cuenta?**\nContacta soporte para asistencia.',
        options: [
            { text: '📝 Crear cuenta', action: 'create_account' },
            { text: '🔐 Iniciar sesión', action: 'login_help' },
            { text: '✏️ Editar perfil', action: 'update_profile' }
        ]
    });
};

// Inicializar chatbot cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    new MerktolimaChatbot();
});