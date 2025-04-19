package api

import (
	"net/http"

	"github.com/Hosefu/render-routing/internal/models"
	"github.com/Hosefu/render-routing/internal/renderer"
	"github.com/Hosefu/render-routing/pkg/logger"
	"github.com/gin-gonic/gin"
)

// Handler содержит обработчики HTTP-запросов
type Handler struct {
	rendererRouter *renderer.Router
	logger         logger.Logger
}

// NewHandler создает новый обработчик HTTP-запросов
func NewHandler(rendererRouter *renderer.Router, logger logger.Logger) *Handler {
	return &Handler{
		rendererRouter: rendererRouter,
		logger:         logger,
	}
}

// RenderDocument обрабатывает запрос на рендеринг документа
func (h *Handler) RenderDocument(c *gin.Context) {
	var request models.RenderRequest

	// Разбираем запрос
	if err := c.ShouldBindJSON(&request); err != nil {
		h.logger.Errorf("Error binding request JSON: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}

	// Валидируем запрос
	if err := request.Validate(); err != nil {
		h.logger.Errorf("Request validation error: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Логируем запрос
	h.logger.Infof("Received request to render document with template ID %d", request.TemplateID)

	// Маршрутизируем запрос к соответствующему рендереру
	response, err := h.rendererRouter.RouteRenderRequest(c.Request.Context(), &request)
	if err != nil {
		h.logger.Errorf("Error routing render request: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Если в ответе есть ошибка, возвращаем её
	if response.Error != "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": response.Error})
		return
	}

	// Возвращаем успешный ответ
	h.logger.Infof("Document rendered successfully, URL: %s", response.URL)
	c.JSON(http.StatusOK, response)
}

// HealthCheck отвечает на запросы проверки работоспособности
func (h *Handler) HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"service": "render-routing",
	})
}

// NotFound обрабатывает запросы к несуществующим маршрутам
func (h *Handler) NotFound(c *gin.Context) {
	c.JSON(http.StatusNotFound, gin.H{
		"error": "Route not found",
	})
}
