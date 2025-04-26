package renderer

import (
	"context"
	"fmt"

	"render-routing/internal/models"
	"render-routing/internal/template"
	"render-routing/pkg/logger"
)

// TemplateProcessor обрабатывает шаблоны и подставляет данные
type TemplateProcessor struct {
	logger         logger.Logger
	templateClient *template.Client
}

// NewTemplateProcessor создает новый обработчик шаблонов
func NewTemplateProcessor(templateClient *template.Client, logger logger.Logger) *TemplateProcessor {
	return &TemplateProcessor{
		logger:         logger,
		templateClient: templateClient,
	}
}

// ProcessTemplate подставляет данные в шаблон
func (p *TemplateProcessor) ProcessTemplate(ctx context.Context, tmpl *models.Template, data map[string]string) ([]string, error) {
	if !tmpl.IsValid() {
		return nil, fmt.Errorf("invalid template: no pages found")
	}

	p.logger.Infof("Processing template %s (ID: %d) with %d pages",
		tmpl.Name, tmpl.ID, len(tmpl.Pages))

	// Результат - массив обработанных HTML-страниц
	processedPages := make([]string, 0, len(tmpl.Pages))

	// Обрабатываем каждую страницу
	for i, page := range tmpl.Pages {
		p.logger.Debugf("Processing page %d: %s", i+1, page.Name)

		// Создаем запрос к сервису шаблонизации
		request := &template.RenderRequest{
			TemplateHTML: page.HTML,
			Data:         data,
			TemplateID:   tmpl.ID,
			PageIndex:    i,
		}

		// Отправляем запрос к сервису шаблонизации
		renderedHTML, err := p.templateClient.RenderTemplate(ctx, request)
		if err != nil {
			p.logger.Errorf("Error processing template page %d: %v", i+1, err)
			return nil, fmt.Errorf("error processing template page %d: %w", i+1, err)
		}

		// Добавляем обработанную страницу в результат
		processedPages = append(processedPages, renderedHTML)
		p.logger.Debugf("Page %d processed successfully (%d bytes)", i+1, len(renderedHTML))
	}

	p.logger.Infof("Template processing completed: %d pages processed", len(processedPages))

	return processedPages, nil
}

// ValidateRequiredFields проверяет наличие всех обязательных полей
func (p *TemplateProcessor) ValidateRequiredFields(template *models.Template, data map[string]string) error {
	for _, page := range template.Pages {
		for _, field := range page.Fields {
			if field.Required {
				if _, exists := data[field.Name]; !exists {
					return fmt.Errorf("required field %s not provided", field.Name)
				}
			}
		}
	}
	return nil
}
