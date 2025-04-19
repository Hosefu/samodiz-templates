package renderer

import (
	"context"
	"fmt"

	"github.com/Hosefu/render-routing/internal/models"
	"github.com/Hosefu/render-routing/internal/storage"
	"github.com/Hosefu/render-routing/pkg/logger"
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

	// Получаем первую страницу (в будущем можно обрабатывать каждую страницу отдельно)
	if len(processedPages) == 0 {
		return nil, fmt.Errorf("no pages processed")
	}

	firstPage := template.Pages[0]
	html := processedPages[0]

	// Подготавливаем запрос к рендереру
	rendererRequest := &models.RendererRequest{
		HTML:            html,
		Data:            request.Data,
		Width:           firstPage.Width,
		Height:          firstPage.Height,
		Units:           firstPage.Units,
		Bleeds:          firstPage.Bleeds,
		GeneratePreview: request.GeneratePreview,
		Settings:        firstPage.GetSettingsMap(),
	}

	// Определяем тип шаблона и маршрутизируем к соответствующему рендереру
	var rendererResponse *models.RendererResponse

	switch template.Type {
	case "pdf":
		r.logger.Infof("Routing to PDF renderer")
		rendererResponse, err = r.rendererClient.RenderPDF(ctx, rendererRequest)
	case "png":
		r.logger.Infof("Routing to PNG renderer")
		rendererResponse, err = r.rendererClient.RenderPNG(ctx, rendererRequest)
	default:
		return nil, fmt.Errorf("unsupported template type: %s", template.Type)
	}

	if err != nil {
		return nil, fmt.Errorf("error rendering: %w", err)
	}

	// Проверяем наличие ошибки в ответе рендерера
	if rendererResponse.Error != "" {
		return &models.RenderResponse{
			Error: rendererResponse.Error,
		}, nil
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
