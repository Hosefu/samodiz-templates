package api

import (
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

// SetupRouter настраивает маршруты для HTTP-сервера
func SetupRouter(handler *Handler) *gin.Engine {
	// Настраиваем режим работы Gin
	gin.SetMode(gin.ReleaseMode)

	// Создаем новый роутер
	router := gin.New()

	// Настраиваем CORS
	corsConfig := cors.DefaultConfig()
	corsConfig.AllowAllOrigins = true
	corsConfig.AllowMethods = []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
	corsConfig.AllowHeaders = []string{"Origin", "Content-Type", "Accept", "Authorization", "X-API-Key"}
	router.Use(cors.New(corsConfig))

	// Middleware для логирования запросов
	router.Use(gin.Logger())

	// Middleware для восстановления после паники
	router.Use(gin.Recovery())

	// Основные маршруты API
	api := router.Group("/api")
	{
		// Маршруты для рендеринга
		render := api.Group("/render")
		{
			render.POST("/generate", handler.RenderDocument)
		}

		// Маршрут для проверки работоспособности
		api.GET("/health", handler.HealthCheck)
	}

	// Обработчик для несуществующих маршрутов
	router.NoRoute(handler.NotFound)

	return router
}
