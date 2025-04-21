package renderer

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"render-routing/internal/models"
	"render-routing/internal/storage"
	"render-routing/pkg/logger"
)

// Router маршрутизирует запросы к соответствующим рендерерам
type Router struct {
	storageClient     *storage.Client
	rendererClient    *Client
	templateProcessor *TemplateProcessor
	logger            logger.Logger
}

// NewRouter создает новый маршрутизатор рендереров
func NewRouter(
	storageClient *storage.Client,
	rendererClient *Client,
	templateProcessor *TemplateProcessor,
	logger logger.Logger,
) *Router {
	return &Router{
		storageClient:     storageClient,
		rendererClient:    rendererClient,
		templateProcessor: templateProcessor,
		logger:            logger,
	}
}

// RouteRenderRequest обрабатывает запрос и маршрутизирует его к соответствующему рендереру
func (r *Router) RouteRenderRequest(ctx context.Context, request *models.RenderRequest) (*models.RenderResponse, error) {
	// Start a timer for performance tracking
	startTime := time.Now()

	r.logger.Infof("--- RENDER REQUEST START ---")
	r.logger.Infof("Processing render request for template ID: %d", request.TemplateID)

	// Log the form data (up to 10 fields for privacy/brevity)
	if len(request.Data) > 0 {
		r.logger.Infof("Request contains %d form data fields", len(request.Data))
		count := 0
		for key, value := range request.Data {
			if count < 10 {
				// Truncate long values for logging
				displayValue := value
				if len(displayValue) > 50 {
					displayValue = displayValue[:47] + "..."
				}
				r.logger.Debugf("Form data: %s = %s", key, displayValue)
				count++
			} else {
				r.logger.Debugf("(and %d more fields)", len(request.Data)-10)
				break
			}
		}
	} else {
		r.logger.Warnf("Request contains no form data")
	}

	// Получаем шаблон из storage-service
	template, err := r.storageClient.GetTemplate(ctx, request.TemplateID)
	if err != nil {
		r.logger.Errorf("Error fetching template ID %d: %v", request.TemplateID, err)
		return nil, fmt.Errorf("error getting template: %w", err)
	}

	r.logger.Infof("Template loaded: %s (ID: %d), Type: %s, Pages: %d",
		template.Name, template.ID, template.Type, len(template.Pages))

	// Проверяем наличие всех обязательных полей
	if err := r.templateProcessor.ValidateRequiredFields(template, request.Data); err != nil {
		r.logger.Errorf("Validation error: %v", err)
		return nil, fmt.Errorf("validation error: %w", err)
	}
	r.logger.Infof("All required fields validated successfully")

	// Обрабатываем шаблон и подставляем данные
	processedPages, err := r.templateProcessor.ProcessTemplate(template, request.Data)
	if err != nil {
		r.logger.Errorf("Error processing template: %v", err)
		return nil, fmt.Errorf("error processing template: %w", err)
	}

	// Log processed HTML preview for debugging
	for i, html := range processedPages {
		htmlPreview := html
		if len(htmlPreview) > 200 {
			htmlPreview = htmlPreview[:200] + "..."
		}
		r.logger.Debugf("Processed page %d HTML preview: %s", i+1, htmlPreview)
	}

	// Проверяем наличие страниц
	if len(processedPages) == 0 {
		r.logger.Errorf("No pages processed")
		return nil, fmt.Errorf("no pages processed")
	}
	r.logger.Infof("Template processed successfully, %d pages generated", len(processedPages))

	// Подготавливаем массив HTML страниц
	htmlPages := processedPages
	pageSettings := make([]map[string]string, len(template.Pages))
	pageUnits := make([]string, len(template.Pages))
	pageDimensions := make([]struct {
		Width  int
		Height int
		Bleeds int
	}, len(template.Pages))

	// Заполняем массивы данными страниц
	for i, page := range template.Pages {
		pageSettings[i] = page.GetSettingsMap()
		pageUnits[i] = page.Units
		pageDimensions[i] = struct {
			Width  int
			Height int
			Bleeds int
		}{
			Width:  page.Width,
			Height: page.Height,
			Bleeds: page.Bleeds,
		}

		r.logger.Debugf("Page %d settings: %v", i+1, pageSettings[i])
		r.logger.Debugf("Page %d dimensions: %dx%d %s, Bleeds: %d",
			i+1, page.Width, page.Height, page.Units, page.Bleeds)
	}

	// Определяем тип рендерера в зависимости от типа шаблона
	var rendererResponse *models.RendererResponse
	var uploadFormat string

	// Added type detection logging
	r.logger.Infof("Detecting template type to select renderer...")
	r.logger.Infof("Template type is: %s", template.Type)

	switch strings.ToLower(template.Type) {
	case "pdf":
		r.logger.Infof("Routing to PDF renderer")
		rendererResponse, err = r.handlePdfRendering(ctx, template, htmlPages, pageUnits, pageDimensions, pageSettings, request)
		uploadFormat = "pdf"
	case "png":
		r.logger.Infof("Routing to PNG renderer")
		rendererResponse, err = r.handlePngRendering(ctx, template, htmlPages[0], pageUnits[0], pageDimensions[0], pageSettings[0], request)
		uploadFormat = "png"
	default:
		r.logger.Errorf("Unsupported template type: %s", template.Type)
		return nil, fmt.Errorf("unsupported template type: %s", template.Type)
	}

	if err != nil {
		r.logger.Errorf("Error from renderer: %v", err)
		return nil, fmt.Errorf("renderer error: %w", err)
	}

	// Check if renderer returned an error in the response
	if rendererResponse.Error != "" {
		r.logger.Errorf("Renderer returned error: %s", rendererResponse.Error)
		return &models.RenderResponse{
			Error: rendererResponse.Error,
		}, nil
	}

	// Check if renderer returned file content
	if len(rendererResponse.FileContent) == 0 {
		r.logger.Errorf("Renderer returned empty file content")
		return nil, fmt.Errorf("renderer returned empty file content")
	}

	// Additional validation for suspiciously small files
	if len(rendererResponse.FileContent) < 100 {
		r.logger.Warnf("Renderer returned suspiciously small file: %d bytes", len(rendererResponse.FileContent))

		// Log first bytes for debugging
		if len(rendererResponse.FileContent) > 0 {
			maxBytes := len(rendererResponse.FileContent)
			if maxBytes > 32 {
				maxBytes = 32
			}

			hexBytes := ""
			for i := 0; i < maxBytes; i++ {
				hexBytes += fmt.Sprintf("%02x ", rendererResponse.FileContent[i])
			}

			r.logger.Warnf("First %d bytes: %s", maxBytes, hexBytes)
		}
	} else {
		r.logger.Infof("Renderer returned file of %d bytes", len(rendererResponse.FileContent))
	}

	// Загружаем результат в storage-service
	uploadRequest := &models.StorageUploadRequest{
		TemplateID: request.TemplateID,
		Format:     uploadFormat,
		File:       rendererResponse.FileContent,
		FormData:   request.Data,
	}

	r.logger.Infof("Uploading generated %s to storage service", uploadFormat)
	uploadResponse, err := r.storageClient.UploadGeneratedFile(ctx, uploadRequest)
	if err != nil {
		r.logger.Errorf("Error uploading file to storage: %v", err)
		return nil, fmt.Errorf("error uploading generated file: %w", err)
	}

	// Формируем итоговый ответ
	response := &models.RenderResponse{
		URL:       uploadResponse.URL,
		Format:    uploadFormat,
		CreatedAt: uploadResponse.CreatedAt,
	}

	// Добавляем URL превью, если есть
	if rendererResponse.PreviewURL != "" {
		response.PreviewURL = rendererResponse.PreviewURL
		r.logger.Infof("Preview URL included in response: %s", response.PreviewURL)
	}

	elapsedTime := time.Since(startTime)
	r.logger.Infof("Render request completed in %v, file URL: %s", elapsedTime, response.URL)
	r.logger.Infof("--- RENDER REQUEST END ---")

	return response, nil
}

// Метод для PDF рендеринга (поддерживает многостраничные документы)
func (r *Router) handlePdfRendering(
	ctx context.Context,
	template *models.Template,
	htmlPages []string,
	pageUnits []string,
	pageDimensions []struct {
		Width  int
		Height int
		Bleeds int
	},
	pageSettings []map[string]string,
	request *models.RenderRequest,
) (*models.RendererResponse, error) {
	r.logger.Infof("--- PDF RENDERING HANDLER START ---")
	r.logger.Infof("Preparing PDF rendering request with %d pages", len(htmlPages))

	// Создаем запрос для PDF рендерера с поддержкой мультистраничности
	rendererRequest := &models.PdfRendererRequest{
		TemplateId:      request.TemplateID,
		Pages:           make([]models.PdfPageRequest, len(htmlPages)),
		Data:            request.Data,
		GeneratePreview: request.GeneratePreview,
	}

	// Заполняем данные для каждой страницы
	for i, html := range htmlPages {
		// Basic validation - don't send empty HTML
		if len(strings.TrimSpace(html)) == 0 {
			r.logger.Errorf("Page %d has empty HTML after processing", i+1)
			return nil, fmt.Errorf("page %d has empty HTML after processing", i+1)
		}

		// Add debug logging
		r.logger.Debugf("Page %d HTML length: %d bytes", i+1, len(html))

		rendererRequest.Pages[i] = models.PdfPageRequest{
			HTML:     html,
			Width:    pageDimensions[i].Width,
			Height:   pageDimensions[i].Height,
			Units:    pageUnits[i],
			Bleeds:   pageDimensions[i].Bleeds,
			Settings: pageSettings[i],
		}

		// Collect assets for this page
		var assets []models.AssetInfo
		for _, asset := range template.Pages[i].Assets {
			assets = append(assets, models.AssetInfo{File: asset.File})
			r.logger.Debugf("Added asset to page %d: %s", i+1, asset.File)
		}
		rendererRequest.Pages[i].Assets = assets

		r.logger.Infof("Page %d configuration: %dx%d %s, Bleeds: %d, Assets: %d",
			i+1,
			rendererRequest.Pages[i].Width,
			rendererRequest.Pages[i].Height,
			rendererRequest.Pages[i].Units,
			rendererRequest.Pages[i].Bleeds,
			len(rendererRequest.Pages[i].Assets))
	}

	// Log full request as JSON
	requestJSON, _ := json.MarshalIndent(rendererRequest, "", "  ")
	if len(requestJSON) > 1000 {
		r.logger.Debugf("PDF renderer request (truncated): %s...", string(requestJSON)[:1000])
	} else {
		r.logger.Debugf("PDF renderer request: %s", string(requestJSON))
	}

	// Вызываем PDF рендерер
	r.logger.Infof("Sending request to PDF renderer")
	rendererResponse, err := r.rendererClient.RenderPDF(ctx, rendererRequest)
	if err != nil {
		r.logger.Errorf("Error from PDF renderer: %v", err)
		return nil, fmt.Errorf("error rendering PDF: %w", err)
	}

	// Check response
	if rendererResponse.Error != "" {
		r.logger.Errorf("PDF renderer returned error: %s", rendererResponse.Error)
		return rendererResponse, nil
	}

	// Check file content
	if len(rendererResponse.FileContent) == 0 {
		r.logger.Errorf("PDF renderer returned empty file content")
		return nil, fmt.Errorf("PDF renderer returned empty file content")
	}

	r.logger.Infof("PDF renderer returned %d bytes of file content", len(rendererResponse.FileContent))
	if rendererResponse.PreviewURL != "" {
		r.logger.Infof("PDF preview URL: %s", rendererResponse.PreviewURL)
	}

	r.logger.Infof("--- PDF RENDERING HANDLER END ---")
	return rendererResponse, nil
}

// Метод для PNG рендеринга (одностраничные)
func (r *Router) handlePngRendering(
	ctx context.Context,
	template *models.Template,
	html string,
	units string,
	dimensions struct {
		Width  int
		Height int
		Bleeds int
	},
	settings map[string]string,
	request *models.RenderRequest,
) (*models.RendererResponse, error) {
	r.logger.Infof("--- PNG RENDERING HANDLER START ---")

	// Basic validation - don't send empty HTML
	if len(strings.TrimSpace(html)) == 0 {
		r.logger.Errorf("PNG page has empty HTML after processing")
		return nil, fmt.Errorf("PNG page has empty HTML after processing")
	}

	r.logger.Infof("Preparing PNG rendering request")
	r.logger.Infof("PNG dimensions: %dx%d %s", dimensions.Width, dimensions.Height, units)
	r.logger.Debugf("PNG HTML length: %d bytes", len(html))

	// Создаем запрос для PNG рендерера (только одна страница)
	rendererRequest := &models.RendererRequest{
		HTML:     html,
		Data:     request.Data,
		Width:    dimensions.Width,
		Height:   dimensions.Height,
		Units:    units,
		Settings: settings,
	}

	// Вызываем PNG рендерер
	r.logger.Infof("Sending request to PNG renderer")
	rendererResponse, err := r.rendererClient.RenderPNG(ctx, rendererRequest)
	if err != nil {
		r.logger.Errorf("Error from PNG renderer: %v", err)
		return nil, fmt.Errorf("error rendering PNG: %w", err)
	}

	// Check response
	if rendererResponse.Error != "" {
		r.logger.Errorf("PNG renderer returned error: %s", rendererResponse.Error)
		return rendererResponse, nil
	}

	// Check file content
	if len(rendererResponse.FileContent) == 0 {
		r.logger.Errorf("PNG renderer returned empty file content")
		return nil, fmt.Errorf("PNG renderer returned empty file content")
	}

	r.logger.Infof("PNG renderer returned %d bytes of file content", len(rendererResponse.FileContent))
	r.logger.Infof("--- PNG RENDERING HANDLER END ---")

	return rendererResponse, nil
}
