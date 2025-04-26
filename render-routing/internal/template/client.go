package template

import (
	"context"
	"encoding/json"
	"fmt"
	"render-routing/pkg/httputil"
	"render-routing/pkg/logger"
)

// Client представляет клиент для работы с сервисом шаблонизации
type Client struct {
	httpClient  *httputil.Client
	templateURL string
	logger      logger.Logger
}

// NewClient создает новый клиент для сервиса шаблонизации
func NewClient(templateURL string, httpConfig httputil.ClientConfig, logger logger.Logger) *Client {
	// Создаем клиент для сервиса шаблонизации
	templateConfig := httpConfig
	templateConfig.BaseURL = "" // URL передается полностью при запросе

	return &Client{
		httpClient:  httputil.NewClient(templateConfig, logger),
		templateURL: templateURL,
		logger:      logger,
	}
}

// RenderRequest представляет запрос к сервису шаблонизации
type RenderRequest struct {
	TemplateHTML string            `json:"template_html"`
	Data         map[string]string `json:"data"`
	TemplateID   int               `json:"template_id,omitempty"`
	PageIndex    int               `json:"page_index,omitempty"`
}

// RenderResponse представляет ответ от сервиса шаблонизации
type RenderResponse struct {
	HTML   string `json:"html"`
	Status string `json:"status"`
	Error  string `json:"error,omitempty"`
}

// RenderTemplate отправляет запрос на обработку шаблона
func (c *Client) RenderTemplate(ctx context.Context, request *RenderRequest) (string, error) {
	c.logger.Infof("Sending template rendering request to %s", c.templateURL)
	c.logger.Debugf("Template size: %d bytes, Data fields: %d, Template ID: %d, Page index: %d",
		len(request.TemplateHTML), len(request.Data), request.TemplateID, request.PageIndex)

	// Сериализуем запрос в JSON
	requestData, err := json.Marshal(request)
	if err != nil {
		c.logger.Errorf("Failed to marshal template render request: %v", err)
		return "", fmt.Errorf("error marshaling request: %w", err)
	}

	c.logger.Infof("Sending request to template service (%d bytes)", len(requestData))

	// Отправляем запрос к сервису шаблонизации
	responseData, err := c.httpClient.Post(ctx, c.templateURL, json.RawMessage(requestData), nil)
	if err != nil {
		c.logger.Errorf("Error sending request to template service: %v", err)
		return "", fmt.Errorf("error sending request to template service: %w", err)
	}

	c.logger.Infof("Received response from template service: %d bytes", len(responseData))

	// Разбираем ответ
	var response RenderResponse
	if err := json.Unmarshal(responseData, &response); err != nil {
		c.logger.Errorf("Failed to parse template service response: %v", err)
		return "", fmt.Errorf("invalid response from template service: %w", err)
	}

	// Проверяем наличие ошибки в ответе
	if response.Error != "" {
		c.logger.Errorf("Template service returned error: %s", response.Error)
		return "", fmt.Errorf("template service error: %s", response.Error)
	}

	// Проверяем статус ответа
	if response.Status != "success" {
		c.logger.Errorf("Template service returned non-success status: %s", response.Status)
		return "", fmt.Errorf("template service returned status: %s", response.Status)
	}

	// Проверяем наличие HTML в ответе
	if response.HTML == "" {
		c.logger.Errorf("Template service returned empty HTML")
		return "", fmt.Errorf("template service returned empty HTML")
	}

	c.logger.Infof("Template rendered successfully, HTML size: %d bytes", len(response.HTML))

	return response.HTML, nil
}
