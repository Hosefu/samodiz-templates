package renderer

import (
	"context"
	"encoding/json"
	"fmt"

	"render-routing/internal/models"
	"render-routing/pkg/httputil"
	"render-routing/pkg/logger"
)

// Client представляет клиент для работы с рендерерами
type Client struct {
	pdfClient      *httputil.Client
	pngClient      *httputil.Client
	pdfRendererURL string
	pngRendererURL string
	logger         logger.Logger
}

// NewClient создает новый клиент для рендереров
func NewClient(pdfRendererURL, pngRendererURL string, httpConfig httputil.ClientConfig, logger logger.Logger) *Client {
	// Создаем клиенты для каждого рендерера
	pdfConfig := httpConfig
	pdfConfig.BaseURL = "" // URL передается полностью при запросе

	pngConfig := httpConfig
	pngConfig.BaseURL = "" // URL передается полностью при запросе

	return &Client{
		pdfClient:      httputil.NewClient(pdfConfig, logger),
		pngClient:      httputil.NewClient(pngConfig, logger),
		pdfRendererURL: pdfRendererURL,
		pngRendererURL: pngRendererURL,
		logger:         logger,
	}
}

// RenderPDF отправляет запрос на рендеринг PDF
func (c *Client) RenderPDF(ctx context.Context, request *models.PdfRendererRequest) (*models.RendererResponse, error) {
	c.logger.Infof("Sending PDF rendering request to %s with %d pages", c.pdfRendererURL, len(request.Pages))

	// Передаем URL ассетов для каждой страницы, если они есть
	for i, page := range request.Pages {
		// Если baseUri не установлен и есть ассеты, настраиваем baseUri для доступа к ассетам
		if page.BaseUri == "" && len(page.Assets) > 0 {
			// URL для доступа к ассетам через storage-service
			request.Pages[i].BaseUri = "http://storage-service:8000"
		} else if page.BaseUri == "" {
			// Если ассетов нет, используем базовый путь
			request.Pages[i].BaseUri = "/tmp"
		}
		c.logger.Infof("Page %d: Set baseUri to %s, assets count: %d", i, request.Pages[i].BaseUri, len(page.Assets))
	}

	// Добавляем информацию об ассетах в settings
	for i, page := range request.Pages {
		if page.Settings == nil {
			request.Pages[i].Settings = make(map[string]string)
		}

		// Если есть Assets, добавляем их в settings для обработки в PDF-рендерере
		if len(page.Assets) > 0 {
			assetsJson, err := json.Marshal(page.Assets)
			if err == nil {
				request.Pages[i].Settings["assets"] = string(assetsJson)
				c.logger.Infof("Added %d assets to settings for page %d", len(page.Assets), i)
			} else {
				c.logger.Errorf("Failed to marshal assets: %v", err)
			}
		}
	}

	requestData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %w", err)
	}

	// Отправляем запрос к PDF рендереру
	responseData, err := c.pdfClient.Post(ctx, c.pdfRendererURL, json.RawMessage(requestData), nil)
	if err != nil {
		return nil, fmt.Errorf("error sending request to PDF renderer: %w", err)
	}

	// Разбираем ответ
	var response models.RendererResponse
	if err := json.Unmarshal(responseData, &response); err != nil {
		// Если не смогли распарсить ответ как JSON, предполагаем что это бинарные данные PDF
		response.FileContent = responseData
	}

	c.logger.Infof("PDF rendering completed, response size: %d bytes", len(response.FileContent))

	return &response, nil
}

// RenderPNG отправляет запрос на рендеринг PNG
func (c *Client) RenderPNG(ctx context.Context, request *models.RendererRequest) (*models.RendererResponse, error) {
	c.logger.Infof("Sending PNG rendering request to %s", c.pngRendererURL)

	requestData, err := request.AsJSON()
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %w", err)
	}

	// Отправляем запрос к PNG рендереру
	responseData, err := c.pngClient.Post(ctx, c.pngRendererURL, json.RawMessage(requestData), nil)
	if err != nil {
		return nil, fmt.Errorf("error sending request to PNG renderer: %w", err)
	}

	// Разбираем ответ
	var response models.RendererResponse
	if err := json.Unmarshal(responseData, &response); err != nil {
		// Если не смогли распарсить ответ как JSON, предполагаем что это бинарные данные PNG
		response.FileContent = responseData
	}

	c.logger.Infof("PNG rendering completed, response size: %d bytes", len(response.FileContent))

	return &response, nil
}
