package renderer

import (
	"context"
	"fmt"

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
	// Получаем шаблон из storage-service
	template, err := r.storageClient.GetTemplate(ctx, request.TemplateID)
	if err != nil {
		return nil, fmt.Errorf("error getting template: %w", err)
	}

	// Проверяем наличие всех обязательных полей
	if err := r.templateProcessor.ValidateRequiredFields(template, request.Data); err != nil {
		return nil, fmt.Errorf("validation error: %w", err)
	}

	// Обрабатываем шаблон и подставляем данные
	processedPages, err := r.templateProcessor.ProcessTemplate(template, request.Data)
	if err != nil {
		return nil, fmt.Errorf("error processing template: %w", err)
	}

	// Проверяем наличие страниц
	if len(processedPages) == 0 {
		return nil, fmt.Errorf("no pages processed")
	}

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
	}

	// Создаем запрос для рендерера в зависимости от типа шаблона
	switch template.Type {
	case "pdf":
		return r.handlePdfRendering(ctx, template, htmlPages, pageUnits, pageDimensions, pageSettings, request)
	case "png":
		return r.handlePngRendering(ctx, template, htmlPages[0], pageUnits[0], pageDimensions[0], pageSettings[0], request)
	default:
		return nil, fmt.Errorf("unsupported template type: %s", template.Type)
	}
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
) (*models.RenderResponse, error) {
	// Создаем запрос для PDF рендерера с поддержкой мультистраничности
	rendererRequest := &models.PdfRendererRequest{
		Pages:           make([]models.PdfPageRequest, len(htmlPages)),
		Data:            request.Data,
		GeneratePreview: request.GeneratePreview,
	}

	// Заполняем данные для каждой страницы
	for i, html := range htmlPages {
		rendererRequest.Pages[i] = models.PdfPageRequest{
			HTML:     html,
			Width:    pageDimensions[i].Width,
			Height:   pageDimensions[i].Height,
			Units:    pageUnits[i],
			Bleeds:   pageDimensions[i].Bleeds,
			Settings: pageSettings[i],
		}
	}

	// Вызываем PDF рендерер
	r.logger.Infof("Routing to PDF renderer with %d pages", len(htmlPages))
	rendererResponse, err := r.rendererClient.RenderPDF(ctx, rendererRequest)
	if err != nil {
		return nil, fmt.Errorf("error rendering PDF: %w", err)
	}

	// Загружаем результат
	return r.handleRendererResponse(ctx, template, rendererResponse, request)
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
) (*models.RenderResponse, error) {
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
	r.logger.Infof("Routing to PNG renderer")
	rendererResponse, err := r.rendererClient.RenderPNG(ctx, rendererRequest)
	if err != nil {
		return nil, fmt.Errorf("error rendering PNG: %w", err)
	}

	// Загружаем результат
	return r.handleRendererResponse(ctx, template, rendererResponse, request)
}

// Общий метод для обработки ответа от рендереров и загрузки в хранилище
func (r *Router) handleRendererResponse(
	ctx context.Context,
	template *models.Template,
	rendererResponse *models.RendererResponse,
	request *models.RenderRequest,
) (*models.RenderResponse, error) {
	// Проверяем наличие ошибки в ответе рендерера
	if rendererResponse.Error != "" {
		return &models.RenderResponse{
			Error: rendererResponse.Error,
		}, nil
	}

	// Проверяем на пустой FileContent
	if len(rendererResponse.FileContent) == 0 {
		return nil, fmt.Errorf("renderer returned empty file content")
	}

	// Загружаем результат в storage-service
	uploadRequest := &models.StorageUploadRequest{
		TemplateID: request.TemplateID,
		Format:     template.Type,
		File:       rendererResponse.FileContent,
		FormData:   request.Data,
	}

	uploadResponse, err := r.storageClient.UploadGeneratedFile(ctx, uploadRequest)
	if err != nil {
		return nil, fmt.Errorf("error uploading generated file: %w", err)
	}

	// Формируем итоговый ответ
	response := &models.RenderResponse{
		URL:       uploadResponse.URL,
		Format:    template.Type,
		CreatedAt: uploadResponse.CreatedAt,
	}

	// Добавляем URL превью, если есть
	if rendererResponse.PreviewURL != "" {
		response.PreviewURL = rendererResponse.PreviewURL
	}

	return response, nil
}
