package storage

import (
	"context"
	"encoding/json"
	"fmt"
	"strconv"

	"github.com/Hosefu/render-routing/internal/models"
	"github.com/Hosefu/render-routing/pkg/httputil"
	"github.com/Hosefu/render-routing/pkg/logger"
)

// Client представляет клиент для работы с API storage-service
type Client struct {
	httpClient *httputil.Client
	logger     logger.Logger
}

// NewClient создает новый клиент для storage-service
func NewClient(httpClient *httputil.Client, logger logger.Logger) *Client {
	return &Client{
		httpClient: httpClient,
		logger:     logger,
	}
}

// GetTemplate получает шаблон по ID
func (c *Client) GetTemplate(ctx context.Context, templateID int) (*models.Template, error) {
	path := fmt.Sprintf("/templates/%d/", templateID)

	c.logger.Debugf("Getting template with ID %d", templateID)

	data, err := c.httpClient.Get(ctx, path, nil)
	if err != nil {
		return nil, fmt.Errorf("error getting template: %w", err)
	}

	var template models.Template
	if err := json.Unmarshal(data, &template); err != nil {
		return nil, fmt.Errorf("error unmarshaling template: %w", err)
	}

	c.logger.Debugf("Successfully got template %s (ID: %d)", template.Name, template.ID)

	return &template, nil
}

// UploadGeneratedFile загружает сгенерированный файл
func (c *Client) UploadGeneratedFile(ctx context.Context, request *models.StorageUploadRequest) (*models.StorageUploadResponse, error) {
	path := "/upload-template/"

	// Подготовка multipart-формы
	files := map[string][]byte{
		"file": request.File,
	}

	formData := map[string]string{
		"template_id": strconv.Itoa(request.TemplateID),
		"format":      request.Format,
	}

	// Конвертируем данные формы в JSON
	if request.FormData != nil {
		formDataJson, err := json.Marshal(request.FormData)
		if err != nil {
			return nil, fmt.Errorf("error marshaling form data: %w", err)
		}
		formData["form_data"] = string(formDataJson)
	}

	c.logger.Debugf("Uploading generated %s file for template ID %d",
		request.Format, request.TemplateID)

	// Отправляем multipart запрос
	data, err := c.httpClient.PostMultipart(ctx, path, formData, files, nil)
	if err != nil {
		return nil, fmt.Errorf("error uploading file: %w", err)
	}

	// Разбираем ответ
	var response models.StorageUploadResponse
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, fmt.Errorf("error unmarshaling upload response: %w", err)
	}

	c.logger.Debugf("File successfully uploaded. URL: %s", response.URL)

	return &response, nil
}
