package renderer

import (
	"fmt"
	"strings"

	"github.com/Hosefu/render-routing/internal/models"
	"github.com/Hosefu/render-routing/pkg/logger"
)

// TemplateProcessor обрабатывает шаблоны и подставляет данные
type TemplateProcessor struct {
	logger logger.Logger
}

// NewTemplateProcessor создает новый обработчик шаблонов
func NewTemplateProcessor(logger logger.Logger) *TemplateProcessor {
	return &TemplateProcessor{
		logger: logger,
	}
}

// ProcessTemplate подставляет данные в шаблон
func (p *TemplateProcessor) ProcessTemplate(template *models.Template, data map[string]string) ([]string, error) {
	if !template.IsValid() {
		return nil, fmt.Errorf("invalid template: no pages found")
	}

	p.logger.Debugf("Processing template %s (ID: %d) with %d pages",
		template.Name, template.ID, len(template.Pages))

	// Результат - массив обработанных HTML-страниц
	processedPages := make([]string, 0, len(template.Pages))

	// Обрабатываем каждую страницу
	for i, page := range template.Pages {
		p.logger.Debugf("Processing page %d: %s", i+1, page.Name)

		// Берём исходный HTML
		html := page.HTML

		// Для каждого поля делаем замену {{FieldName}} -> value
		for _, field := range page.Fields {
			placeholder := fmt.Sprintf("{{%s}}", field.Name)
			value, exists := data[field.Name]

			if !exists {
				// Если значение не предоставлено, проверяем, обязательно ли поле
				if field.Required {
					return nil, fmt.Errorf("required field %s not provided", field.Name)
				}
				value = "" // Пустая строка для необязательных полей
			}

			// Замена placeholder на значение
			html = strings.ReplaceAll(html, placeholder, value)
			p.logger.Debugf("  ↳ Replaced %s with value of length %d", placeholder, len(value))
		}

		// Ищем неподставленные плейсхолдеры
		if index := strings.Index(html, "{{"); index != -1 {
			end := strings.Index(html[index:], "}}") + index + 2
			if end > index+2 {
				placeholder := html[index:end]
				p.logger.Warnf("Unreplaced placeholder found: %s", placeholder)
			}
		}

		processedPages = append(processedPages, html)
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
