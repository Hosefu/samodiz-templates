package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/Hosefu/render-routing/internal/api"
	"github.com/Hosefu/render-routing/internal/config"
	"github.com/Hosefu/render-routing/internal/renderer"
	"github.com/Hosefu/render-routing/internal/storage"
	"github.com/Hosefu/render-routing/pkg/httputil"
	"github.com/Hosefu/render-routing/pkg/logger"
)

func main() {
	// Загружаем конфигурацию
	var cfg *config.Config
	configPath := os.Getenv("CONFIG_PATH")
	if configPath != "" {
		var err error
		cfg, err = config.LoadConfig(configPath)
		if err != nil {
			fmt.Printf("Error loading config: %v\n", err)
			os.Exit(1)
		}
	} else {
		cfg = config.LoadConfigFromEnv()
	}

	// Инициализируем логгер
	log := logger.New(cfg.LoggerConfig.Level, cfg.LoggerConfig.Format)
	log.Info("Starting render-routing")

	// Настраиваем HTTP-клиент для storage-service
	storageHttpConfig := httputil.ClientConfig{
		BaseURL:         cfg.StorageAPI.BaseURL,
		APIKey:          cfg.StorageAPI.APIKey,
		Timeout:         cfg.HTTPClient.Timeout,
		MaxIdleConns:    cfg.HTTPClient.MaxIdleConns,
		IdleConnTimeout: cfg.HTTPClient.IdleConnTimeout,
	}
	storageHttpClient := httputil.NewClient(storageHttpConfig, log)
	storageClient := storage.NewClient(storageHttpClient, log)

	// Настраиваем клиент для рендереров
	rendererClient := renderer.NewClient(
		cfg.Renderers.PDFRenderer,
		cfg.Renderers.PNGRenderer,
		httputil.ClientConfig{
			Timeout:         cfg.HTTPClient.Timeout,
			MaxIdleConns:    cfg.HTTPClient.MaxIdleConns,
			IdleConnTimeout: cfg.HTTPClient.IdleConnTimeout,
		},
		log,
	)

	// Создаем процессор шаблонов
	templateProcessor := renderer.NewTemplateProcessor(log)

	// Создаем маршрутизатор рендереров
	rendererRouter := renderer.NewRouter(
		storageClient,
		rendererClient,
		templateProcessor,
		log,
	)

	// Создаем HTTP-обработчик
	handler := api.NewHandler(rendererRouter, log)

	// Настраиваем HTTP-сервер
	router := api.SetupRouter(handler)
	server := &http.Server{
		Addr:         ":" + cfg.Server.Port,
		Handler:      router,
		ReadTimeout:  cfg.Server.ReadTimeout,
		WriteTimeout: cfg.Server.WriteTimeout,
	}

	// Запускаем HTTP-сервер в отдельной горутине
	go func() {
		log.Infof("Server listening on port %s", cfg.Server.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Error starting server: %v", err)
		}
	}()

	// Настраиваем обработку сигналов для корректного завершения
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Info("Shutting down server...")

	// Корректно останавливаем сервер
	ctx, cancel := context.WithTimeout(context.Background(), cfg.Server.ShutdownTimeout)
	defer cancel()
	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Info("Server exited properly")
}
