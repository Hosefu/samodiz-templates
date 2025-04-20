package httputil

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"time"

	"render-routing/pkg/logger"
)

// Client представляет HTTP клиент с расширенной функциональностью
type Client struct {
	httpClient *http.Client
	baseURL    string
	apiKey     string
	logger     logger.Logger
}

// ClientConfig содержит конфигурацию HTTP клиента
type ClientConfig struct {
	BaseURL         string
	APIKey          string
	Timeout         time.Duration
	MaxIdleConns    int
	IdleConnTimeout time.Duration
}

// NewClient создает новый HTTP клиент с заданной конфигурацией
func NewClient(cfg ClientConfig, log logger.Logger) *Client {
	transport := &http.Transport{
		MaxIdleConns:    cfg.MaxIdleConns,
		IdleConnTimeout: cfg.IdleConnTimeout,
	}

	httpClient := &http.Client{
		Timeout:   cfg.Timeout,
		Transport: transport,
	}

	return &Client{
		httpClient: httpClient,
		baseURL:    cfg.BaseURL,
		apiKey:     cfg.APIKey,
		logger:     log,
	}
}

// Get выполняет HTTP GET запрос
func (c *Client) Get(ctx context.Context, path string, headers map[string]string) ([]byte, error) {
	url := fmt.Sprintf("%s%s", c.baseURL, path)

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}

	// Добавляем заголовки
	c.addHeaders(req, headers)

	// Если задан API ключ, добавляем его
	if c.apiKey != "" {
		req.Header.Set("X-API-Key", c.apiKey)
	}

	c.logger.Debugf("Sending GET request to %s", url)
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	// Проверяем статус ответа
	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("server returned error: %d %s. Body: %s",
			resp.StatusCode, resp.Status, string(body))
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	return body, nil
}

// Post выполняет HTTP POST запрос с JSON телом
func (c *Client) Post(ctx context.Context, path string, body interface{}, headers map[string]string) ([]byte, error) {
	url := fmt.Sprintf("%s%s", c.baseURL, path)

	jsonBody, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request body: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}

	// Устанавливаем Content-Type для JSON
	req.Header.Set("Content-Type", "application/json")

	// Добавляем заголовки
	c.addHeaders(req, headers)

	// Если задан API ключ, добавляем его
	if c.apiKey != "" {
		req.Header.Set("X-API-Key", c.apiKey)
	}

	c.logger.Debugf("Sending POST request to %s", url)
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	// Проверяем статус ответа
	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("server returned error: %d %s. Body: %s",
			resp.StatusCode, resp.Status, string(body))
	}

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	return respBody, nil
}

// PostMultipart выполняет HTTP POST запрос с мультипарт данными
func (c *Client) PostMultipart(ctx context.Context, path string, formData map[string]string,
	files map[string][]byte, headers map[string]string) ([]byte, error) {
	url := fmt.Sprintf("%s%s", c.baseURL, path)

	// Создаем буфер для мультипарт-формы
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	// Добавляем текстовые поля
	for key, value := range formData {
		if err := writer.WriteField(key, value); err != nil {
			return nil, fmt.Errorf("error writing form field: %w", err)
		}
	}

	// Добавляем файлы
	for fieldName, fileContent := range files {
		part, err := writer.CreateFormFile(fieldName, "file.bin")
		if err != nil {
			return nil, fmt.Errorf("error creating form file: %w", err)
		}
		if _, err := part.Write(fileContent); err != nil {
			return nil, fmt.Errorf("error writing file content: %w", err)
		}
	}

	// Закрываем писателя для финализации формы
	if err := writer.Close(); err != nil {
		return nil, fmt.Errorf("error closing multipart writer: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, body)
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}

	// Устанавливаем Content-Type для мультипарт формы
	req.Header.Set("Content-Type", writer.FormDataContentType())

	// Добавляем заголовки
	c.addHeaders(req, headers)

	// Если задан API ключ, добавляем его
	if c.apiKey != "" {
		req.Header.Set("X-API-Key", c.apiKey)
	}

	c.logger.Debugf("Sending multipart POST request to %s", url)
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	// Проверяем статус ответа
	if resp.StatusCode >= 400 {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("server returned error: %d %s. Body: %s",
			resp.StatusCode, resp.Status, string(respBody))
	}

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	return respBody, nil
}

// addHeaders добавляет заголовки к запросу
func (c *Client) addHeaders(req *http.Request, headers map[string]string) {
	for key, value := range headers {
		req.Header.Set(key, value)
	}
}
